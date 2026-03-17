# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf

from common.data_augmentation import check_dataaug_argument
from .objdet_random_utils import objdet_apply_change_rate
from object_detection.tf.src.utils import bbox_corners_to_center_coords, bbox_center_to_corners_coords, bbox_normalized_to_abs_coords


def _check_objdet_random_crop_arguments(crop_center_x, crop_center_y, crop_width, crop_height, interpolation):

    def check_value_range(arg_value, arg_name):
        if isinstance(arg_value, (tuple, list)):
            if arg_value[0] <= 0 or arg_value[0] >= 1 or arg_value[1] <= 0 or arg_value[1] >= 1:
                raise ValueError(f"\nArgument `{arg_name}` of function `objdet_random_crop`: expecting "
                                 f"float values greater than 0 and less than 1. Received {arg_value}")
        else:
            if arg_value <= 0 or arg_value >= 1:
                raise ValueError(f"\nArgument `{arg_name}` of function `objdet_random_crop`: expecting "
                                 f"float values greater than 0 and less than 1. Received {arg_value}")
    
    check_dataaug_argument(crop_center_x, "crop_center_x", function_name="objdet_random_crop", data_type=float, tuples=2)
    check_value_range(crop_center_x, "crop_center_x")
    
    check_dataaug_argument(crop_center_y, "crop_center_y", function_name="objdet_random_crop", data_type=float, tuples=2)
    check_value_range(crop_center_y, "crop_center_y")

    check_dataaug_argument(crop_width, "crop_width", function_name="objdet_random_crop", data_type=float, tuples=1)
    check_value_range(crop_width, "crop_width")
        
    check_dataaug_argument(crop_height, "crop_height", function_name="objdet_random_crop", data_type=float, tuples=1)
    check_value_range(crop_height, "crop_height")
    
    if interpolation not in ("bilinear", "nearest"):
        raise ValueError("\nArgument `interpolation` of function `objdet_random_crop`: expecting "
                         f"either 'bilinear' or 'nearest'. Received {interpolation}")

def objdet_random_crop(
            images: tf.Tensor,
            labels: tf.Tensor,
            crop_center_x: tuple = (0.25, 0.75),
            crop_center_y: tuple = (0.25, 0.75),
            crop_width: float = (0.6, 0.9),
            crop_height: float = (0.6, 0.9),
            interpolation: str = "bilinear",
            change_rate: float = 0.9) -> tuple:
            
    """
    This function randomly crops input images and their associated  bounding boxes.
    The output images have the same size as the input images.
    We designate the portions of the images that are left after cropping
    as 'crop regions'.
    
    Arguments:
        images:
            Input images to crop.
            Shape: [batch_size, width, height, channels]
        labels:
            Labels associated to the images. The class is first, the bounding boxes
            coordinates are (x1, y1, x2, y2) absolute coordinates.
            Shape: [batch_size, num_labels, 5]
        crop_center_x:
            Sampling range for the x coordinates of the centers of the crop regions.
            A tuple of 2 floats between 0 and 1.
        crop_center_y:
            Sampling range for the y coordinates of the centers of the crop regions.
            A tuple of 2 floats between 0 and 1.
        crop_width:
            Sampling range for the widths of the crop regions. A tuple of 2 floats
            between 0 and 1.
            A single float between 0 and 1 can also be used. In this case, the width 
            of all the crop regions will be equal to this value for all images.
        crop_height:
            Sampling range for the heights of the crop regions. A tuple of 2 floats
            between 0 and 1.
            A single float between 0 and 1 can also be used. In this case, the height 
            of all the crop regions will be equal to this value for all images.
        interpolation:
            Interpolation method to resize the cropped image.
            Either 'bilinear' or 'nearest'.
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.

    Returns:
        cropped_images:
            The cropped images.
            Shape: [batch_size, width, height, channels]
        cropped_labels:
            Labels with cropped bounding boxes.
            Shape: [batch_size, num_labels, 5]
    """
    
    # Check the function arguments
    _check_objdet_random_crop_arguments(crop_center_x, crop_center_y, crop_width, crop_height, interpolation)

    if not isinstance(crop_width, (tuple, list)):
        crop_width = (crop_width, crop_width)
    if not isinstance(crop_height, (tuple, list)):
        crop_height = (crop_height, crop_height)

    # Sample the coordinates of the center, width and height of the crop regions
    batch_size = tf.shape(images)[0]
    crop_center_x = tf.random.uniform([batch_size], crop_center_x[0], maxval=crop_center_x[1], dtype=tf.float32)
    crop_center_y = tf.random.uniform([batch_size], crop_center_y[0], maxval=crop_center_y[1], dtype=tf.float32)
    crop_width = tf.random.uniform([batch_size], crop_width[0], maxval=crop_width[1], dtype=tf.float32)
    crop_height = tf.random.uniform([batch_size], crop_height[0], maxval=crop_height[1], dtype=tf.float32)

    # Calculate and clip the (x1, y1, x2, y2) normalized
    # coordinates of the crop regions relative to the
    # upper-left corners of the images
    x1 = tf.clip_by_value(crop_center_x - crop_width/2, 0, 1)
    y1 = tf.clip_by_value(crop_center_y - crop_height/2, 0, 1)
    x2 = tf.clip_by_value(crop_center_x + crop_width/2, 0, 1)
    y2 = tf.clip_by_value(crop_center_y + crop_height/2, 0, 1)

    # Crop the input images and resize them to their initial size
    image_size = tf.shape(images)[1:3]
    crop_regions = tf.stack([y1, x1, y2, x2], axis=-1) 
    crop_region_indices = tf.range(batch_size)
    cropped_images = tf.image.crop_and_resize(images, crop_regions, crop_region_indices,
                                              crop_size=image_size, method=interpolation)

    # Convert cropping regions coordinates from normalized to absolute
    image_size = tf.cast(image_size, tf.float32)
    x1 = tf.expand_dims(x1, axis=-1) * image_size[0]
    y1 = tf.expand_dims(y1, axis=-1) * image_size[1]
    x2 = tf.expand_dims(x2, axis=-1) * image_size[0]
    y2 = tf.expand_dims(y2, axis=-1) * image_size[1]
    
    # Keep track of padding boxes in the input labels
    box_coords_sum = tf.math.reduce_sum(labels[..., 1:], axis=-1)
    input_padding = tf.math.less_equal(box_coords_sum, 0)
    
    # Keep track of boxes that fall outside of the crop regions
    box_x1 = labels[..., 1]
    box_y1 = labels[..., 2]
    box_x2 = labels[..., 3]
    box_y2 = labels[..., 4]
    cond_x = tf.math.logical_or(box_x2 <= x1, box_x1 >= x2)
    cond_y = tf.math.logical_or(box_y2 <= y1, box_y1 >= y2)
    outside_crop_regions = tf.math.logical_or(cond_x, cond_y)

    # Calculate the coordinates of the boxes relative
    # to the upper-left corners of the crop regions
    box_x1 = box_x1 - x1
    box_y1 = box_y1 - y1
    box_x2 = box_x2 - x1
    box_y2 = box_y2 - y1
    
    # Clip the coordinates of the boxes
    # to the size of the crop regions
    region_width = x2 - x1
    region_height = y2 - y1
    box_x1 = tf.math.maximum(0., box_x1)
    box_y1 = tf.math.maximum(0., box_y1)
    box_x2 = tf.math.minimum(box_x2, region_width)
    box_y2 = tf.math.minimum(box_y2, region_height)

    # Normalize the coordinates of the boxes
    # with the size of the crop regions
    box_x1 /= region_width
    box_y1 /= region_height
    box_x2 /= region_width
    box_y2 /= region_height

    # Convert the coordinates of the boxes to absolute
    # coordinates based on the size of the output images
    cropped_boxes = tf.stack([box_x1, box_y1, box_x2, box_y2], axis=-1)
    cropped_boxes = bbox_normalized_to_abs_coords(cropped_boxes, image_size, clip_boxes=True)

    # Output labels that correspond to input padding labels
    # or have boxes that fell outside of the crop regions 
    # must be made padding labels.
    padding = tf.math.logical_or(input_padding, outside_crop_regions)
    not_padding = tf.cast(tf.math.logical_not(padding), tf.float32)
    cropped_boxes *= tf.expand_dims(not_padding, axis=-1)
    cropped_labels = tf.concat([labels[..., 0:1], cropped_boxes], axis=-1)

    # Rearrange the output labels in such a way that the padding
    # labels are grouped together at the end of the labels
    indices = tf.argsort(not_padding, direction='DESCENDING', axis=1)
    cropped_labels = tf.gather(cropped_labels, indices, batch_dims=1)

    # Apply the change rate to images and labels
    images_aug, boxes_aug = objdet_apply_change_rate(
            images, labels[..., 1:], cropped_images, cropped_labels[..., 1:], change_rate=change_rate)
    labels_aug = tf.concat([cropped_labels[..., 0:1], boxes_aug], axis=-1)

    return images_aug, labels_aug
    

def objdet_random_periodic_resizing(
                images,
                gt_labels,
                interpolation=None,
                new_image_size=None):
    """
    This function periodically resizes the input images. The size of
    the images is held constant for a specified number of batches,
    referred to as the "resizing period". Every time a period ends,
    a new size is sampled from a specified set of sizes. Then, the
    size is held constant for the next period, etc.
    
    This function is intended to be used with the 'data_augmentation.py'
    package as it needs the current batch number and the size of the
    images of the previous batch.
    
    Arguments:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        period:
            An integer, the resizing period.
        image_sizes:
            A tuple or list of integers, the set of sizes the image
            sizes are sampled from.
        interpolation:
            A string, the interpolation method used to resize the images.
            Supported values are "bilinear", "nearest", "area", "gaussian",
            "lanczos3", "lanczos5", "bicubic" and "mitchellcubic"
            (resizing is done using the Tensorflow tf.image.resize() function).
        batch:
            An integer, the current batch number starting from the beginning
            of the training.
        last_image_size:
            An tuple of 2 integers, the size of the images of the previous
            batch of images.

    Returns:
        The periodally resized images.
    """

    input_image_size = tf.shape(images)[1:3]
    
    output_image_size = tf.cast(new_image_size,tf.int32)

    #Resize GT boxes
    gt_boxes = bbox_corners_to_center_coords(gt_labels[..., 1:], image_size=input_image_size, abs_corners=True)
    gt_boxes = bbox_center_to_corners_coords(gt_boxes, image_size=output_image_size, normalize=False)
    resized_gt_labels = tf.concat([gt_labels[..., 0:1], gt_boxes], axis=-1)

    # Resize the images
    resized_images = tf.image.resize(images,output_image_size)

    return resized_images, resized_gt_labels
