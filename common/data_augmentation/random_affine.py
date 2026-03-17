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
from common.data_augmentation import check_dataaug_argument, apply_change_rate
from common.data_augmentation import \
        check_fill_and_interpolation, transform_images, \
        get_flip_matrix, get_translation_matrix, get_rotation_matrix, \
        get_shear_matrix, get_zoom_matrix


#------------------------- Random flip -------------------------

def random_flip(images, mode=None, change_rate=0.5):
    """
    This function randomly flips input images horizontally, vertically, or both.
    
    Setting `change_rate` to 0.5 usually gives good results (don't set
    it to 1.0, otherwise all the images will be flipped).
    
    Args:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels]. 
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
        The flipped images.
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
    flipped_images = transform_images(images, matrix)

    return apply_change_rate(images, flipped_images, change_rate)


#--------------------------------- Random translation ---------------------

def random_translation(
            images,
            width_factor=None,
            height_factor=None,
            fill_mode='reflect',
            interpolation='bilinear',
            fill_value=0.0,
            change_rate=1.0):
    """"
    This function randomly translates input images.

    Args:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels]. 
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
        The translated images.
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

    image_shape = tf.shape(images)
    batch_size = image_shape[0]
    width = tf.cast(image_shape[1], tf.float32)
    height = tf.cast(image_shape[2], tf.float32)

    translation_width = tf.random.uniform(
            [batch_size, 1], minval=width_lower, maxval=width_upper, dtype=tf.float32)
    
    translation_height = tf.random.uniform(
            [batch_size, 1], minval=height_lower, maxval=height_upper, dtype=tf.float32)

    translations = tf.cast(
            tf.concat([translation_width * width, translation_height * height], axis=1),
            dtype=tf.float32)
    
    translation_matrix = get_translation_matrix(translations)
    translated_images = transform_images(
            images,
            translation_matrix,
            interpolation=interpolation,
            fill_mode=fill_mode,
            fill_value=fill_value)

    return apply_change_rate(images, translated_images, change_rate)


#------------------ Random rotation ----------------

def random_rotation(
            images,
            factor=None,
            fill_mode='reflect',
            interpolation='bilinear',
            fill_value=0.0,
            change_rate=1.0):
    """
    This function randomly rotates input images clock-wise and counter clock-wise.

    Args:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels]. 
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
        The rotated images.
    """

    check_dataaug_argument(factor, "factor", function_name="random_rotation", data_type=float)
    if not isinstance(factor, (tuple, list)):
        factor = (-factor, factor)
        
    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name="random_rotation")

    image_shape = tf.shape(images)
    batch_size = image_shape[0]
    width = tf.cast(image_shape[1], tf.float32)
    height = tf.cast(image_shape[2], tf.float32)
    
    min_angle = factor[0] * 2. * math.pi
    max_angle = factor[1] * 2. * math.pi
    
    angles = tf.random.uniform([batch_size], minval=min_angle, maxval=max_angle)
    
    rotation_matrix = get_rotation_matrix(angles, width, height)
    
    rotated_images = transform_images(
                        images,
                        rotation_matrix,
                        fill_mode=fill_mode,
                        fill_value=fill_value,
                        interpolation=interpolation)

    return apply_change_rate(images, rotated_images, change_rate)


#------------------ Random shear ----------------

def random_shear(
        images,
        factor=None,
        axis='xy',
        fill_mode='reflect',
        interpolation='bilinear',
        fill_value=0.0,
        change_rate=1.0):
    """
    This function randomly shears input images.

    Args:
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

    batch_size = tf.shape(images)[0]
    min_angle = factor[0] * 2. * math.pi
    max_angle = factor[1] * 2. * math.pi
    angles = tf.random.uniform([batch_size], minval=min_angle, maxval=max_angle)

    shear_matrix = get_shear_matrix(angles, axis=axis)
    
    sheared_images = transform_images(
                        images,
                        shear_matrix,
                        fill_mode=fill_mode,
                        fill_value=fill_value,
                        interpolation=interpolation)
 
    return apply_change_rate(images, sheared_images, change_rate)


#--------------------------------- Random zoom ---------------------

def random_zoom(
        images, 
        width_factor=None,
        height_factor=None,
        fill_mode='reflect',
        interpolation='bilinear',
        fill_value=0.0,
        change_rate=1.0):
    
    """
    This function randomly zooms in/out on each axis of input images.

    If `width_factor` and `height_factor` are both set, the images are zoomed
    in or out on each axis independently, which may result in noticeable distortion.
    If you want to avoid distortion, only set `width_factor` and the mages will be
    zoomed by the same amount in both directions.
 
    Args:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels]. 
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
        The zoomed images.    
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
            
    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name="random_zoom")

    image_shape = tf.shape(images)
    batch_size = image_shape[0]
    width = tf.cast(image_shape[1], tf.float32)
    height = tf.cast(image_shape[2], tf.float32)

    zoom_width = tf.random.uniform(
            [batch_size, 1], minval=1.0 + width_lower, maxval=1.0 + width_upper, dtype=tf.float32)
        
    if height_factor is not None:
        zoom_height = tf.random.uniform(
            [batch_size, 1], minval=1.0 + height_lower, maxval=1.0 + height_upper, dtype=tf.float32)
    else:
        zoom_height = zoom_width
                
    zooms = tf.cast(tf.concat([zoom_width, zoom_height], axis=1), dtype=tf.float32)
      
    zoom_matrix = get_zoom_matrix(zooms, width, height)
    
    zoomed_images = transform_images(
                images,
                zoom_matrix,
                fill_mode=fill_mode,
                fill_value=fill_value,
                interpolation=interpolation)

    return apply_change_rate(images, zoomed_images, change_rate)



#--------------------------------- Random bounded crop ---------------------

def random_bounded_crop(
        images, 
        width_factor=None,
        height_factor=None,
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
 
    Args:
        images:
            Input RGB or grayscale images with shape
            [batch_size, width, height, channels]. 
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
        The zoomed images.    
    """

    check_dataaug_argument(width_factor, "width_factor", function_name="random_bounded_crop", data_type=float)
    if isinstance(width_factor, (tuple, list)):
        width_lower = width_factor[0]
        width_upper = width_factor[1]
    else:
        width_lower = -width_factor
        width_upper = width_factor
                
    if height_factor is not None:
        check_dataaug_argument(height_factor, "height_factor", function_name="random_bounded_crop", data_type=float)
        if isinstance(height_factor, (tuple, list)):
            height_lower = height_factor[0]
            height_upper = height_factor[1]
        else:
            height_lower = -height_factor
            height_upper = height_factor
        if abs(height_lower) > 1.0 or abs(height_upper) > 1.0:
            raise ValueError(
                "Argument `height_factor` of function `random_bounded_crop`: expecting float "
                "values in the interval [-1.0, 1.0]. Received: {}".format(height_factor))
            
    check_fill_and_interpolation(fill_mode, interpolation, fill_value, function_name="random_bounded_crop")

    image_shape = tf.shape(images)
    batch_size = image_shape[0]
    width = tf.cast(image_shape[1], tf.float32)
    height = tf.cast(image_shape[2], tf.float32)

    zoom_width = tf.random.uniform(
            [batch_size, 1], minval=1.0 + width_lower, maxval=1.0 + width_upper, dtype=tf.float32)
        
    if height_factor is not None:
        zoom_height = tf.random.uniform(
            [batch_size, 1], minval=1.0 + height_lower, maxval=1.0 + height_upper, dtype=tf.float32)
    else:
        zoom_height = zoom_width
                
    zoom_factor_w = 1-zoom_width
    zoom_factor_h = 1-zoom_height

    zoom_factor_w *= tf.cast(zoom_factor_w>=0,tf.float32)
    zoom_factor_h *= tf.cast(zoom_factor_h>=0,tf.float32)

    translation_width = tf.random.uniform(
            [batch_size, 1], minval=-1, maxval=1, dtype=tf.float32)
    
    translation_height = tf.random.uniform(
            [batch_size, 1], minval=-1, maxval=1, dtype=tf.float32)

    translation_width  *= zoom_factor_w/2
    translation_height *= zoom_factor_h/2

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

    zoomed_images = transform_images(
                translated_images,
                zoom_matrix,
                fill_mode=fill_mode,
                fill_value=fill_value,
                interpolation=interpolation)

    return apply_change_rate(images, zoomed_images, change_rate)
