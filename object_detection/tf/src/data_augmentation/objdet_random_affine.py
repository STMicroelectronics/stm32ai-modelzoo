
# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

"""
References:
----------
Some of the code in this package is from or was inspired by:

    Keras Image Preprocessing Layers
    The Tensorflow Authors
    Copyright (c) 2019

Link to the source code:
    https://github.com/keras-team/keras/blob/v2.12.0/keras/layers/preprocessing/image_preprocessing.py#L394-L495

"""

import math
import tensorflow as tf

from common.data_augmentation import \
            check_fill_and_interpolation, transform_images, check_dataaug_argument, \
            get_flip_matrix, get_translation_matrix, get_rotation_matrix, \
            get_shear_matrix, get_zoom_matrix
from .objdet_random_utils import objdet_apply_change_rate


def _transform_boxes(boxes, transforms, image_width, image_height, scale=1.):
    """
    This function applies affine transformations to a batch of boxes.
    The transformation matrices are independent from each other
    and are generally different from one batch item to another.
    
    Arguments:
        boxes:
            Boxes the matrices are applied to
            Shape:[batch_size, num_boxes, 4]
        transforms:
            Matrices coefficients to apply to the boxes
            Shape:[batch_size, 8]

    Returns:
        Transformed boxes
        Shape:[batch_size, num_boxes, 4]
    """
    
    image_width = tf.cast(image_width, tf.float32)
    image_height = tf.cast(image_height, tf.float32)
    
    boxes_shape = tf.shape(boxes)
    batch_size = boxes_shape[0]
    num_boxes = boxes_shape[1]
    
    # Create a mask to keep track of padding boxes
    coords_sum = tf.math.reduce_sum(boxes, axis=-1)
    padding_mask = tf.where(coords_sum > 0, 1., 0.)
    padding_mask = tf.repeat(padding_mask, 4)
    padding_mask = tf.reshape(padding_mask, [batch_size, num_boxes, 4])
        
    # Create and invert the matrices (inversion is necessary
    # to align with the TF function that transforms the images)
    transforms = tf.concat([
            transforms,
            tf.ones([batch_size, 1], dtype=tf.float32)],
            axis=-1)
    matrices = tf.reshape(transforms, [batch_size, 3, 3])
    matrices = tf.linalg.inv(matrices)
    
    # The same transform has to be applied to all the boxes
    # of a batch item, so we replicate the matrices.
    matrices = tf.expand_dims(matrices, axis=1)    
    matrices = tf.tile(matrices, [1, num_boxes, 1, 1])

    x1 = boxes[..., 0]
    y1 = boxes[..., 1]
    x2 = boxes[..., 2]
    y2 = boxes[..., 3]

    # Reduce the size of the boxes before transforming them
    if scale < 1:
        dx = scale * (x2 - x1)
        dy = scale * (y2 - y1)
        boxes = tf.stack([x1 + dx, y1 + dx, x2 - dx, y2 - dy], axis=-1)

    # Stack box corner vectors to create 4x4 matrices
    # Then multiply by transformation matrices to get
    # the transformed corner vectors.
    corners = tf.concat([
            tf.stack([x1, x2, x2, x1], axis=-1),
            tf.stack([y1, y1, y2, y2], axis=-1),
            tf.ones([batch_size, num_boxes, 4], dtype=tf.float32)],
            axis=-1)
    corners = tf.reshape(corners, [batch_size, num_boxes, 3, 4])
    
    trd_corners = tf.linalg.matmul(matrices, corners)

    # Project transformed corner vectors onto x and y axis
    tx1 = tf.math.reduce_min(trd_corners[..., 0, :], axis=-1)
    tx2 = tf.math.reduce_max(trd_corners[..., 0, :], axis=-1)
    ty1 = tf.math.reduce_min(trd_corners[..., 1, :], axis=-1)
    ty2 = tf.math.reduce_max(trd_corners[..., 1, :], axis=-1)

    # Clip transformed coordinates
    tx1 = tf.math.maximum(tx1, 0)
    tx1 = tf.math.minimum(tx1, image_width)
    
    tx2 = tf.math.maximum(tx2, 0)
    tx2 = tf.math.minimum(tx2, image_width)
    
    ty1 = tf.math.maximum(ty1, 0)
    ty1 = tf.math.minimum(ty1, image_height)
    
    ty2 = tf.math.maximum(ty2, 0)
    ty2 = tf.math.minimum(ty2, image_height)
    
    trd_boxes = tf.stack([tx1, ty1, tx2, ty2], axis=-1)

    # Get rid of boxes that don't make sense
    valid_boxes = tf.math.logical_and(tx2 > tx1, ty2 > ty1)
    valid_boxes = tf.cast(valid_boxes, tf.float32)
    trd_boxes *= tf.expand_dims(valid_boxes, axis=-1)

    # Set to 0 the coordinates of padding boxes as transforms
    # may have resulted in some non-zeros coordinates.
    trd_boxes *= padding_mask
    
    return trd_boxes


#------------------------- Random flip -------------------------

def objdet_random_flip(images, labels, mode=None, change_rate=0.5):
    """
    This function randomly flips input images and the bounding boxes
    in the associated groundtruth labels.

    Setting `change_rate` to 0.5 usually gives good results (don't set
    it to 1.0, otherwise all the images will be flipped).
    
    Arguments:
        images:
            Input RGB or grayscale images
            Shape: [batch_size, width, height, channels]
        labels:
            Groundtruth labels associated to the images in 
            (class, x1, y1, x2, y2) format. Bounding box coordinates
            must be absolute, opposite corners coordinates.
            Shape: [batch_size, num_labels, 5] 
        mode:
            A string representing the flip axis. Either "horizontal",
            "vertical" or "horizontal_and_vertical".
        change_rate:
            A float in the interval [0, 1] representing the number of 
            changed images versus the total number of input images average
            ratio. For example, if `change_rate` is set to 0.25, 25% of
            the input images will get changed on average (75% won't get
            changed). If it is set to 0.0, no images are changed. If it is
            set to 1.0, all the images are changed.

    Returns:
        The flipped images and groundtruth labels with flipped bounding boxes.
    """

    if mode not in ("horizontal", "vertical", "horizontal_and_vertical"):
        raise ValueError(
            "Argument `mode` of function `random_flip`: supported values are 'horizontal', "
            "'vertical' and 'horizontal_and_vertical'. Received {}".format(mode))

    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    image_width = images_shape[1]
    image_height = images_shape[2]
    
    matrix = get_flip_matrix(batch_size, image_width, image_height, mode)

    boxes = labels[..., 1:]
    flipped_images = transform_images(images, matrix)
    flipped_boxes = _transform_boxes(boxes, matrix, image_width, image_height)

    # Apply the change rate to images and labels
    images_aug, boxes_aug = objdet_apply_change_rate(
            images, boxes, flipped_images, flipped_boxes, change_rate=change_rate)
    classes = tf.expand_dims(labels[..., 0], axis=-1)
    labels_aug = tf.concat([classes, boxes_aug], axis=-1)

    return images_aug, labels_aug


#------------------------- Random translation -------------------------

def objdet_random_translation(
            images, labels,
            width_factor, height_factor,
            fill_mode='reflect', interpolation='bilinear', fill_value=0.0,
            change_rate=1.0):
    """
    This function randomly translates input images and the bounding boxes
    in the associated groundtruth labels.

    Arguments:
        images:
            Input RGB or grayscale images with shape
            Shape: [batch_size, width, height, channels]
        labels:
            Groundtruth labels associated to the images in 
            (class, x1, y1, x2, y2) format. Bounding box coordinates
            must be absolute, opposite corners coordinates.
            Shape: [batch_size, num_labels, 5]
        width_factor:
            A float or a tuple of 2 floats, specifies the range of values
            the horizontal shift factors are sampled from (one per image).
            If a scalar value v is used, it is equivalent to the tuple (-v, v).
            A negative factor means shifting the image left, while a positive 
            factor means shifting the image right.
            For example, `width_factor`=(-0.2, 0.3) results in an output shifted
            left by up to 20% or shifted right by up to 30%.
        height_factor:
            A float or a tuple of 2 floats, specifies the range of values
            the vertical shift factors are sampled from (one per image).
            If a scalar value v is used, it is equivalent to the tuple (-v, v).
            A negative factor means shifting the image up, while a positive
            factor means shifting the image down.
            For example, `height_factor`=(-0.2, 0.3) results in an output shifted
            up by up to 20% or shifted down by up to 30%.
        fill_mode:
            Points outside the boundaries of the input are filled according
            to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}.
            See Tensorflow documentation at https://tensorflow.org
            for more details.
        interpolation:
            A string, the interpolation method. Supported values: 'nearest', 'bilinear'.
        change_rate:
            A float in the interval [0, 1] representing the number of 
            changed images versus the total number of input images average
            ratio. For example, if `change_rate` is set to 0.25, 25% of
            the input images will get changed on average (75% won't get
            changed). If it is set to 0.0, no images are changed. If it is
            set to 1.0, all the images are changed.

    Returns:
        The translated images and groundtruth labels with translated bounding boxes.
    """

    check_dataaug_argument(width_factor, "width_factor", function_name="random_translation", data_type=float)
    if isinstance(width_factor, (tuple, list)):
        width_lower = width_factor[0]
        width_upper = width_factor[1]
    else:
        width_lower = -width_factor
        width_upper = width_factor
        
    check_dataaug_argument(height_factor, "height_factor", function_name="random_translation", data_type=float)
    if isinstance(height_factor, (tuple, list)):
        height_lower = height_factor[0]
        height_upper = height_factor[1]
    else:
        height_lower = -height_factor
        height_upper = height_factor

    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name="random_translation")

    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    image_width = images_shape[1]
    image_height = images_shape[2]
    
    classes = labels[..., 0]
    boxes = labels[..., 1:]
    
    width_translate = tf.random.uniform(
            [batch_size, 1], minval=width_lower, maxval=width_upper, dtype=tf.float32)
    width_translate = width_translate * tf.cast(image_width, tf.float32)
    
    height_translate = tf.random.uniform(
            [batch_size, 1], minval=height_lower, maxval=height_upper, dtype=tf.float32)
    height_translate = height_translate * tf.cast(image_height, tf.float32)

    translations = tf.cast(
            tf.concat([width_translate, height_translate], axis=1),
            dtype=tf.float32)

    translation_matrix = get_translation_matrix(translations)
    
    translated_images = transform_images(
            images,
            translation_matrix,
            interpolation=interpolation,
            fill_mode=fill_mode,
            fill_value=fill_value)

    translated_boxes = _transform_boxes(
            boxes,
            translation_matrix,
            image_width,
            image_height)

    # Apply the change rate to images and labels
    images_aug, boxes_aug = objdet_apply_change_rate(
            images, boxes, translated_images, translated_boxes, change_rate=change_rate)
    classes = tf.expand_dims(labels[..., 0], axis=-1)
    labels_aug = tf.concat([classes, boxes_aug], axis=-1)

    return images_aug, labels_aug


#------------------------- Random rotation -------------------------

def objdet_random_rotation(
                images, labels, factor=None,
                fill_mode='reflect', interpolation='bilinear', fill_value=0.0,
                change_rate=1.0):
    """
    This function randomly rotates input images and the bounding boxes
    in the associated groundtruth labels.

    Arguments:
        images:
            Input RGB or grayscale images with shape
            Shape: [batch_size, width, height, channels]
        labels:
            Groundtruth labels associated to the images in 
            (class, x1, y1, x2, y2) format. Bounding box coordinates
            must be absolute, opposite corners coordinates.
            Shape: [batch_size, num_labels, 5]
        factor:
            A float or a tuple of 2 floats, specifies the range of values the
            rotation angles are sampled from (one per image). If a scalar 
            value v is used, it is equivalent to the tuple (-v, v).
            Rotation angles are in gradients (fractions of 2*pi). A positive 
            angle means rotating counter clock-wise, while a negative angle 
            means rotating clock-wise.
            For example, `factor`=(-0.2, 0.3) results in an output rotated by
            a random amount in the range [-20% * 2pi, 30% * 2pi].
        fill_mode:
            Points outside the boundaries of the input are filled according
            to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}.
            See Tensorflow documentation at https://tensorflow.org
            for more details.
        interpolation:
            A string, the interpolation method. Supported values: 'nearest', 'bilinear'.
        change_rate:
            A float in the interval [0, 1] representing the number of 
            changed images versus the total number of input images average
            ratio. For example, if `change_rate` is set to 0.25, 25% of
            the input images will get changed on average (75% won't get
            changed). If it is set to 0.0, no images are changed. If it is
            set to 1.0, all the images are changed.

    Returns:
        The rotated images and groundtruth labels with rotated bounding boxes.
    """

    check_dataaug_argument(factor, "factor", function_name="random_rotation", data_type=float)
    if not isinstance(factor, (tuple, list)):
        factor = (-factor, factor)
        
    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name="random_rotation")

    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    image_width = images_shape[1]
    image_height = images_shape[2]

    min_angle = factor[0] * 2. * math.pi
    max_angle = factor[1] * 2. * math.pi
    angles = tf.random.uniform([batch_size], minval=min_angle, maxval=max_angle)

    classes = labels[..., 0]
    boxes = labels[..., 1:]
    
    rotation_matrix = get_rotation_matrix(angles, image_width, image_height)
    
    rotated_images = transform_images(
                        images,
                        rotation_matrix,
                        fill_mode=fill_mode,
                        fill_value=fill_value,
                        interpolation=interpolation)
 
    rotated_boxes = _transform_boxes(
                        boxes,
                        rotation_matrix,
                        image_width,
                        image_height,
                        scale=0.1)

     # Apply the change rate to images and labels
    images_aug, boxes_aug = objdet_apply_change_rate(
            images, boxes, rotated_images, rotated_boxes, change_rate=change_rate)
    classes = tf.expand_dims(labels[..., 0], axis=-1)
    labels_aug = tf.concat([classes, boxes_aug], axis=-1)

    return images_aug, labels_aug


#------------------------- Random shear -------------------------

def objdet_random_shear(
        images,
        labels,
        factor=None,
        axis='xy',
        fill_mode='reflect',
        interpolation='bilinear',
        fill_value=0.0,
        change_rate=1.0):
    """
    This function randomly shears input images.

    Arguments:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels]. 
        factor:
            A float or a tuple of 2 floats, specifies the range of values
            the shear angles are sampled from (one per image). If a scalar 
            value v is used, it is equivalent to the tuple (-v, v). Angles 
            are in radians (fractions of 2*pi). 
            For example, factor=(-0.349, 0.785) results in an output sheared
            by a random angle in the range [-20 degrees, +45 degrees].
        axis:
            The shear axis:
                'xy': shear along both axis
                'x': shear along the x axis only
                'y': shear along the y axis only  
        fill_mode:
            Points outside the boundaries of the input are filled according
            to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}.
            See Tensorflow documentation at https://tensorflow.org
            for more details.
        interpolation:
            A string, the interpolation method. Supported values: 'nearest', 'bilinear'.
        change_rate:
            A float in the interval [0, 1] representing the number of 
            changed images versus the total number of input images average
            ratio. For example, if `change_rate` is set to 0.25, 25% of
            the input images will get changed on average (75% won't get
            changed). If it is set to 0.0, no images are changed. If it is
            set to 1.0, all the images are changed.
    Returns:
        The sheared images.
    """
    
    if axis == 'x':
        function_name = "random_shear_x"
    elif axis == 'y':
        function_name = "random_shear_y"
    else:
        function_name = "random_shear"

    check_dataaug_argument(factor, "factor", function_name=function_name, data_type=float)
    if not isinstance(factor, (tuple, list)):
        factor = (-factor, factor)
        
    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name=function_name)

    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    image_width = images_shape[1]
    image_height = images_shape[2]

    min_angle = factor[0] * 2. * math.pi
    max_angle = factor[1] * 2. * math.pi
    angles = tf.random.uniform([batch_size], minval=min_angle, maxval=max_angle)

    classes = labels[..., 0]
    boxes = labels[..., 1:]

    shear_matrix = get_shear_matrix(angles, axis=axis)
    
    sheared_images = transform_images(
                        images,
                        shear_matrix,
                        fill_mode=fill_mode,
                        fill_value=fill_value,
                        interpolation=interpolation)
 
    sheared_boxes = _transform_boxes(
                        boxes,
                        shear_matrix,
                        image_width,
                        image_height,
                        scale=0.1)
                        
     # Apply the change rate to images and labels
    images_aug, boxes_aug = objdet_apply_change_rate(
            images, boxes, sheared_images, sheared_boxes, change_rate=change_rate)
    classes = tf.expand_dims(labels[..., 0], axis=-1)
    labels_aug = tf.concat([classes, boxes_aug], axis=-1)

    return images_aug, labels_aug


#------------------------- Random zoom -------------------------

def objdet_random_zoom(
            images, labels, width_factor=None, height_factor=None,
            fill_mode='reflect', interpolation='bilinear', fill_value=0.0,
            change_rate=1.0):
    """
    This function randomly zooms input images and the bounding boxes
    in the associated groundtruth labels.

    If `width_factor` and `height_factor` are both set, the images are zoomed
    in or out on each axis independently, which may result in noticeable distortion.
    If you want to avoid distortion, only set `width_factor` and the mages will be
    zoomed by the same amount in both directions.
 
    Arguments:
        images:
            Input RGB or grayscale images with shape
            Shape: [batch_size, width, height, channels] 
        labels:
            Groundtruth labels associated to the images in 
            (class, x1, y1, x2, y2) format. Bounding box coordinates
            must be absolute, opposite corners coordinates.
            Shape: [batch_size, num_labels, 5]
        width_factor:
            A float or a tuple of 2 floats, specifies the range of values horizontal
            zoom factors are sampled from (one per image). If a scalar value v is used,
            it is equivalent to the tuple (-v, v). Factors are fractions of the width
            of the image. A positive factor means zooming out, while a negative factor
            means zooming in.
            For example, width_factor=(0.2, 0.3) results in an output zoomed out by
            a random amount in the range [+20%, +30%]. width_factor=(-0.3, -0.2) results
            in an output zoomed in by a random amount in the range [+20%, +30%].
        height_factor:
            A float or a tuple of 2 floats, specifies the range of values vertical
            zoom factors are sampled from (one per image). If a scalar value v is used,
            it is equivalent to the tuple (-v, v). Factors are fractions of the height
            of the image. A positive value means zooming out, while a negative value
            means zooming in.
            For example, height_factor=(0.2, 0.3) results in an output zoomed out 
            between 20% to 30%. height_factor=(-0.3, -0.2) results in an output zoomed
            in between 20% to 30%.
            If `height_factor` is not set, it defaults to None. In this case, images
            images will be zoomed by the same amounts in both directions and no image
            distortion will occur.
        fill_mode:
            Points outside the boundaries of the input are filled according
            to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}.
            See Tensorflow documentation at https://tensorflow.org
            for more details.
        interpolation:
            A string, the interpolation method. Supported values: 'nearest', 'bilinear'.
        change_rate:
            A float in the interval [0, 1] representing the number of 
            changed images versus the total number of input images average
            ratio. For example, if `change_rate` is set to 0.25, 25% of
            the input images will get changed on average (75% won't get
            changed). If it is set to 0.0, no images are changed. If it is
            set to 1.0, all the images are changed.

    Returns:
        The zoomed images and groundtruth labels with zoomed bounding boxes.
    """

    check_dataaug_argument(width_factor, "width_factor", function_name="random_zoom", data_type=float)
    if isinstance(width_factor, (tuple, list)):
        width_lower = width_factor[0]
        width_upper = width_factor[1]
    else:
        width_lower = -width_factor
        width_upper = width_factor
                
    if height_factor is not None:
        check_dataaug_argument(height_factor, "height_factor", function_name="random_zoom", data_type=float)
        if isinstance(height_factor, (tuple, list)):
            height_lower = height_factor[0]
            height_upper = height_factor[1]
        else:
            height_lower = -height_factor
            height_upper = height_factor
        if abs(height_lower) > 1.0 or abs(height_upper) > 1.0:
            raise ValueError(
                "Argument `height_factor` of function `random_zoom`: expecting float "
                "values in the interval [-1.0, 1.0]. Received: {}".format(height_factor))
    else:
        height_lower = width_lower
        height_upper = width_upper
    
    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name="random_zoom")

    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    image_width = images_shape[1]
    image_height = images_shape[2]

    classes = labels[..., 0]
    boxes = labels[..., 1:]

    height_zoom = tf.random.uniform(
            [batch_size, 1], minval=1. + height_lower, maxval=1. + height_upper, dtype=tf.float32)
    width_zoom = tf.random.uniform(
            [batch_size, 1], minval=1. + width_lower, maxval=1. + width_upper, dtype=tf.float32)
            
    zooms = tf.cast(tf.concat([width_zoom, height_zoom], axis=1), dtype=tf.float32)
      
    zoom_matrix = get_zoom_matrix(zooms, image_width, image_height)
    
    zoomed_images = transform_images(
                images,
                zoom_matrix,
                fill_mode=fill_mode,
                fill_value=fill_value,
                interpolation=interpolation)

    zoomed_boxes = _transform_boxes(
                boxes,
                zoom_matrix,
                image_width,
                image_height)
    
    # Apply the change rate to images and labels
    images_aug, boxes_aug = objdet_apply_change_rate(
            images, boxes, zoomed_images, zoomed_boxes, change_rate=change_rate)
    classes = tf.expand_dims(labels[..., 0], axis=-1)
    labels_aug = tf.concat([classes, boxes_aug], axis=-1)

    return images_aug, labels_aug


#--------------------------------- Random bounded crop ---------------------

def objdet_random_bounded_crop(
        images,
        labels,
        width_factor=None,
        height_factor=None,
        crop_center_x=None,
        crop_center_y=None,
        fill_mode='reflect',
        interpolation='bilinear',
        fill_value=0.0,
        change_rate=1.0):
    
    """
    This function randomly crops or dezoom on each axis of the input images.

    If `width_factor` and `height_factor` are both set, the images are zoomed
    in or out on each axis independently, which may result in noticeable distortion.
    If you want to avoid distortion, only set `width_factor` and the mages will be
    zoomed by the same amount in both directions.
 
    Arguments:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels]. 
        labels:
            Groundtruth labels associated to the images in 
            (class, x1, y1, x2, y2) format. Bounding box coordinates
            must be absolute, opposite corners coordinates.
            Shape: [batch_size, num_labels, 5]
        width_factor:
            A float or a tuple of 2 floats, specifies the range of values horizontal
            zoom factors are sampled from (one per image). If a scalar value v is used,
            it is equivalent to the tuple (-v, v). Factors are fractions of the width
            of the image. A positive factor means zooming out, while a negative factor
            means zooming in.
            For example, width_factor=(0.2, 0.3) results in an output zoomed out by
            a random amount in the range [+20%, +30%]. width_factor=(-0.3, -0.2) results
            in an output zoomed in by a random amount in the range [+20%, +30%].
        height_factor:
            A float or a tuple of 2 floats, specifies the range of values vertical
            zoom factors are sampled from (one per image). If a scalar value v is used,
            it is equivalent to the tuple (-v, v). Factors are fractions of the height
            of the image. A positive value means zooming out, while a negative value
            means zooming in.
            For example, height_factor=(0.2, 0.3) results in an output zoomed out 
            between 20% to 30%. height_factor=(-0.3, -0.2) results in an output zoomed
            in between 20% to 30%.
            If `height_factor` is not set, it defaults to None. In this case, images
            images will be zoomed by the same amounts in both directions and no image
            distortion will occur.
        fill_mode:
            Points outside the boundaries of the input are filled according
            to the given mode. One of {'constant', 'reflect', 'wrap', 'nearest'}.
            See Tensorflow documentation at https://tensorflow.org
            for more details.
        interpolation:
            A string, the interpolation method. Supported values: 'nearest', 'bilinear'.
        change_rate:
            A float in the interval [0, 1] representing the number of 
            changed images versus the total number of input images average
            ratio. For example, if `change_rate` is set to 0.25, 25% of
            the input images will get changed on average (75% won't get
            changed). If it is set to 0.0, no images are changed. If it is
            set to 1.0, all the images are changed.
    Returns:
        The zoomed images and groundtruth labels with zoomed bounding boxes.
    """

    check_dataaug_argument(width_factor, "width_factor", function_name="random_bounded_crop", data_type=float)
    if isinstance(width_factor, (tuple, list)):
        width_lower = width_factor[0]
        width_upper = width_factor[1]
    else:
        width_lower = width_factor
        width_upper = width_factor
                
    if height_factor is not None:
        check_dataaug_argument(height_factor, "height_factor", function_name="random_bounded_crop", data_type=float)
        if isinstance(height_factor, (tuple, list)):
            height_lower = height_factor[0]
            height_upper = height_factor[1]
        else:
            height_lower = height_factor
            height_upper = height_factor
        if abs(height_lower) > 1.0 or abs(height_upper) > 1.0:
            raise ValueError(
                "Argument `height_factor` of function `random_bounded_crop`: expecting float "
                "values in the interval [-1.0, 1.0]. Received: {}".format(height_factor))
        if (crop_center_x is not None) and (crop_center_y is not None):
            check_dataaug_argument(crop_center_x, "crop_center_x", function_name="random_bounded_crop", data_type=float)
            if isinstance(crop_center_x, (tuple, list)) and isinstance(crop_center_y, (tuple, list)):
                t_width_lower = 0.5 - crop_center_x[1]
                t_width_upper = 0.5 - crop_center_x[0]
                t_height_lower = 0.5 - crop_center_y[1]
                t_height_upper = 0.5 - crop_center_y[0]
            else:
                t_width_lower = - crop_center_x/2
                t_width_upper = crop_center_x/2
                t_height_lower = -crop_center_y/2
                t_height_upper = crop_center_y/2
            if abs(t_width_lower) > 1.0 or abs(t_width_upper) > 1.0 or abs(t_height_lower) > 1.0 or abs(t_height_upper) > 1.0:
                raise ValueError(
                    "Argument `crop_center_x` or `crop_center_y` of function `random_bounded_crop`: expecting float "
                    "values in the interval [-1.0, 1.0]. Received: {}, {}".format(crop_center_x,crop_center_y))
        else:
            t_width_lower = None
            t_width_upper = None
            t_height_lower = None
            t_height_upper = None
            
    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name="random_bounded_crop")

    image_shape = tf.shape(images)
    batch_size = image_shape[0]
    width = tf.cast(image_shape[1], tf.float32)
    height = tf.cast(image_shape[2], tf.float32)

    classes = labels[..., 0]
    boxes = labels[..., 1:]

    zoom_width = tf.random.uniform(
            [batch_size, 1], minval=width_lower, maxval=width_upper, dtype=tf.float32)
        
    if height_factor is not None:
        zoom_height = tf.random.uniform(
            [batch_size, 1], minval=height_lower, maxval=height_upper, dtype=tf.float32)
    else:
        zoom_height = zoom_width
                
    zoom_factor_w = 1-zoom_width
    zoom_factor_h = 1-zoom_height

    zoom_factor_w *= tf.cast(zoom_factor_w>=0,tf.float32)
    zoom_factor_h *= tf.cast(zoom_factor_h>=0,tf.float32)

    if t_width_lower is None:
        translation_width = tf.random.uniform(
                [batch_size, 1], minval=-1, maxval=1, dtype=tf.float32)
        
        translation_height = tf.random.uniform(
                [batch_size, 1], minval=-1, maxval=1, dtype=tf.float32)

        translation_width  *= zoom_factor_w/2
        translation_height *= zoom_factor_h/2
    else:
        translation_width = tf.random.uniform(
                [batch_size, 1], minval=t_width_lower, maxval=t_width_upper, dtype=tf.float32)
        
        translation_height = tf.random.uniform(
                [batch_size, 1], minval=t_height_lower, maxval=t_height_upper, dtype=tf.float32)

    zooms = tf.cast(tf.concat([zoom_width, zoom_height], axis=1), dtype=tf.float32) # shape : (batch, 2)

    translations = tf.cast(
            tf.concat([translation_width * width, translation_height * height], axis=1),
            dtype=tf.float32)

    zoom_matrix        = get_zoom_matrix(zooms, width, height)
    translation_matrix = get_translation_matrix(translations)


    translated_images = transform_images(
                images,
                translation_matrix,
                fill_mode=fill_mode,
                fill_value=fill_value,
                interpolation=interpolation)

    translated_boxes = _transform_boxes(
                boxes,
                translation_matrix,
                width,
                height)


    zoomed_images = transform_images(
                translated_images,
                zoom_matrix,
                fill_mode=fill_mode,
                fill_value=fill_value,
                interpolation=interpolation)

    zoomed_boxes = _transform_boxes(
                translated_boxes,
                zoom_matrix,
                width,
                height)
    
    # Apply the change rate to images and labels
    images_aug, boxes_aug = objdet_apply_change_rate(
            images, boxes, zoomed_images, zoomed_boxes, change_rate=change_rate)
    classes = tf.expand_dims(labels[..., 0], axis=-1)
    labels_aug = tf.concat([classes, boxes_aug], axis=-1)

    return images_aug, labels_aug