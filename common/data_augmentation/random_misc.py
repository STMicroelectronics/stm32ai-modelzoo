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
The random_blur function in this package was inspired by 
the mean_filter2d function from the following package:

    Tensorflow Add-ons Package
    The TensorFlow Authors
    Copyright (c) 2019

Link to the source code:
    https://github.com/tensorflow/addons/blob/v0.20.0/tensorflow_addons/image/filters.py#L62-L122
"""

import tensorflow as tf
from common.data_augmentation import check_dataaug_argument, remap_pixel_values_range, apply_change_rate


def random_blur(images, filter_size=None, padding="reflect",
                constant_values=0, pixels_range=(0.0, 1.0),
                change_rate=1.0):

    """
    This function randomly blurs input images using a mean filter 2D.
    The filter is square with sizes that are sampled from a specified
    range. The larger the filter size, the more pronounced the blur
    effect is.

    The same filter is used for all the images of a batch. By default,
    change_rate is set to 0.5, meaning that half of the input images
    will be blurred on average. The other half of the images will 
    remain unchanged.
    
    Arguments:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        filter_size:
            A tuple of 2 integers greater than or equal to 1, specifies
            the range of values the filter sizes are sampled from (one
            per image). The width and height of the filter are both equal to 
            `filter_size`. The larger the filter size, the more pronounced
            the blur effect is. If the filter size is equal to 1, the image
            is unchanged.    
        padding:
            A string one of "reflect", "constant", or "symmetric". The type
            of padding algorithm to use.
        constant_values:
            A float or integer, the pad value to use in "constant" padding mode.
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.
            
    Returns:
        The blurred images. The data type and range of pixel values 
        are the same as in the input images.

    Usage example:
        filter_size = (1, 4)
    """

    check_dataaug_argument(filter_size, "filter_size", function_name="random_blur", data_type=int, tuples=1)
   
    if isinstance(filter_size, (tuple, list)):
        if filter_size[0] < 1 or filter_size[1] < 1:
            raise ValueError("Argument `filter_size` of function `random_blur`: expecting a tuple "
                             "of 2 integers greater than or equal to 1. Received {}".format(filter_size))
        if padding not in {"reflect", "constant", "symmetric"}:
            raise ValueError('Argument `padding` of function `random_blur`: supported '
                             'values are "reflect", "constant" and "symmetric". '
                             'Received {}'.format(padding))
    else:
        filter_size = (filter_size, filter_size)
    
    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)
    
    # Sample a filter size
    random_filter_size = tf.random.uniform([], minval=filter_size[0], maxval=filter_size[1] + 1, dtype=tf.int32)

    # We use a square filter.
    fr_width = random_filter_size
    fr_height = random_filter_size

    # Pad the images
    pad_top = (fr_height - 1) // 2
    pad_bottom = fr_height - 1 - pad_top
    pad_left = (fr_width - 1) // 2
    pad_right = fr_width - 1 - pad_left
    paddings = [[0, 0], [pad_top, pad_bottom], [pad_left, pad_right], [0, 0]]
    padded_images = tf.pad(images, paddings, mode=padding.upper(), constant_values=constant_values)

    # Create the kernel
    channels = tf.shape(padded_images)[-1]    
    fr_shape = tf.stack([fr_width, fr_height, channels, 1])
    kernel = tf.ones(fr_shape, dtype=images.dtype)

    # Apply the filter to the input images
    output = tf.nn.depthwise_conv2d(padded_images, kernel, strides=(1, 1, 1, 1), padding="VALID")
    area = tf.cast(fr_width * fr_height, dtype=tf.float32)
    images_aug = output / area

    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_gaussian_noise(images, stddev=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function adds gaussian noise to input images. The standard 
    deviations of the gaussian distribution are sampled from a specified
    range. The mean of the distribution is equal to 0.

    The same standard deviation is used for all the images of a batch.
    By default, change_rate is set to 0.5, meaning that noise will be
    added to half of the input images on average. The other half of 
    the images will remain unchanged.
   
    Arguments:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        stddev:
            A tuple of 2 floats greater than or equal to 0.0, specifies
            the range of values the standard deviations of the gaussian
            distribution are sampled from (one per image). The larger 
            the standard deviation, the larger the amount of noise added
            to the input image is. If the standard deviation is equal 
            to 0.0, the image is unchanged.
        pixels_range:
            A tuple of 2 integers or floats, specifies the range 
            of pixel values in the input images and output images.
            Any range is supported. It generally is either
            [0, 255], [0, 1] or [-1, 1].
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.
            
    Returns:
        The images with gaussian noise added. The data type and range
        of pixel values are the same as in the input images.

    Usage example:
        stddev = (0.02, 0.1)
    """
    
    check_dataaug_argument(stddev, "stddev", function_name="random_gaussian_noise", data_type=float, tuples=2)
    if stddev[0] < 0 or stddev[1] < 0:
        raise ValueError("\nArgument `stddev` of function `random_gaussian_noise`: expecting float "
                         "values greater than or equal to 0.0. Received {}".format(stddev))

    dims = tf.shape(images)
    batch_size = dims[0]
    width = dims[1]
    height = dims[2]
    channels = dims[3]

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    # Sample an std value, generate gaussian noise and add it to the images
    random_stddev = tf.random.uniform([1], minval=stddev[0], maxval=stddev[1], dtype=tf.float32)
    noise = tf.random.normal([batch_size, width, height, channels], mean=0.0, stddev=random_stddev)
    images_aug = images + noise

    # Clip the images with noise added
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)

    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)
    

def check_random_crop_arguments(crop_center_x, crop_center_y, crop_width, crop_height, interpolation):
    """
    check_random_crop_arguments assesses the validity of random parameters and potentially raises an error
    
        Args:
            crop_center_x (tuple): range for the x coordinates of the centers of the crop regions. Expects 2 floats between 0 and 1.
            crop_center_y (tuple): range for the y coordinates of the centers of the crop regions. Expects 2 floats between 0 and 1.
            crop_width (tuple): range for the widths of the crop regions. A tuple of 2 floats between 0 and 1.
            crop_height (tuple): range for the heights of the crop regions. A tuple of 2 floats between 0 and 1.
            interpolation: method to resize the cropped image. Either 'bilinear' or 'nearest'.
        Returns:

    """

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

    check_dataaug_argument(crop_width, "crop_width", function_name="objdet_random_crop", data_type=float)
    check_value_range(crop_width, "crop_width")
        
    check_dataaug_argument(crop_height, "crop_height", function_name="objdet_random_crop", data_type=float)
    check_value_range(crop_height, "crop_height")
    
    if interpolation not in ("bilinear", "nearest"):
        raise ValueError("\nArgument `interpolation` of function `objdet_random_crop`: expecting "
                         f"either 'bilinear' or 'nearest'. Received {interpolation}")

def random_crop(
            images: tf.Tensor,
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
            Shape: [batch_size, width, height, channels]
    """
    
    # Check the function arguments
    check_random_crop_arguments(crop_center_x, crop_center_y, crop_width, crop_height, interpolation)

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

    # Apply the change rate to the cropped images
    images_aug = apply_change_rate(images, cropped_images, change_rate=change_rate)

    return images_aug


def random_jpeg_quality(images, jpeg_quality=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly changes the JPEG quality of input images.

    If argument `jpeg_quality` is:
      - equal to 100, images are unchanged.
      - less than 100, JPEG quality is decreased
    
    Arguments:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        jpeg_quality:
            A tuple of 2 integers in the interval [0, 100], specifies
            the range of values the JPEG quality factors are sampled 
            from. If the JPEG quality factor is less is than 100,
            squares that are characteristic of low quality JPEG's
            appear on the output image. The lower the value of 
            the JPEG quality factor, the more degraded the output
            image is. If the JPEG quality factor is equal to 100,
            the input image is unchanged.
        pixels_range:
            A tuple of 2 integers or floats, specifies the range 
            of pixel values in the input images and output images.
            Any range is supported. It generally is either
            [0, 255], [0, 1] or [-1, 1].
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.
            
    Returns:
        The images with adjusted JPEG quality. The data type and range
        of pixel values are the same as in the input images.

    Usage example:
        jpeg_quality = (50, 100)
    """
    
    # Only tuples are accepted for the `jpeg_quality` argument.
    quality = jpeg_quality
    check_dataaug_argument(quality, "jpeg_quality", function_name="random_jpeg_quality", data_type=int, tuples=2)
    if quality[0] < 0 or quality[0] > 100 or quality[1] < 0 or quality[1] > 100:
        raise ValueError("Argument `jpeg_quality` of function `random_jpeg_quality`: expecting a tuple of "
                         "2 integers in the interval [0, 100]. Received {}".format(quality))

    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]
    channels = images_shape[3]

    # Remap pixel values to the interval [0, 1]
    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)
        
    diag = tf.ones([batch_size])
    mask = tf.linalg.diag(diag, num_rows=-1, num_cols=-1, padding_value=0)
    
    # Sample a JPEG quality for each image
    random_quality = tf.random.uniform([batch_size], quality[0], maxval=quality[1] + 1, dtype=tf.int32)
    
    images_aug = tf.zeros([batch_size, width, height, channels], tf.float32)
    for i in range(batch_size):
        # Adjust the JPEG quality
        img = tf.image.adjust_jpeg_quality(images[i], random_quality[i])

        # Replicate the lower quality image to have a row
        # of the same image of length batch_size
        img_row = tf.tile(img, [batch_size, 1, 1])
        img_row = tf.reshape(img_row, [batch_size, width, height, channels])

        # Replicate the mask to match the row of images
        mask_row = tf.repeat(mask[i], [width * height * channels])
        mask_row = tf.reshape(mask_row, [batch_size, width, height, channels])
        
        images_aug = mask_row*img_row + images_aug

    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)



def random_periodic_resizing(
                images,
                interpolation=None,
                new_image_size=None):
    """
    This function periodically resizes the input images. The size of
    the images is held constant for a specified number of batches,
    referred to as the "resizing period". Every time a period ends,
    a new size is sampled from a specified set of sizes. Then, the
    size is held constant for the next period, etc.
    
    Arguments:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        interpolation:
            A string, the interpolation method used to resize the images.
            Supported values are "bilinear", "nearest", "area", "gaussian",
            "lanczos3", "lanczos5", "bicubic" and "mitchellcubic"
            (resizing is done using the Tensorflow tf.image.resize() function).
        new_image_size:
            A tuple or list of integers, the set of sizes the image
            sizes are sampled from.

    Returns:
        The resized images.
    """


    # Resize the images
    resized_images = tf.image.resize(images, new_image_size, method=interpolation)

    return resized_images
