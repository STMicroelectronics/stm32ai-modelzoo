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

import numpy as np
import tensorflow as tf
from random_utils import check_images_shape, check_dataaug_argument, remap_pixel_values_range, apply_change_rate


def random_blur(images, filter_size= None, padding="reflect",
                constant_values=0, change_rate=1.0):
    """
    This function randomly blurs input images using a mean filter 2D.
    The filter is square with sizes that are sampled from a specified
    range. The larger the filter size, the more pronounced the blur
    effect is.

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

    def blur_image(image, filter_shape, mode=None):
    
        # Pad the image
        filter_width = filter_shape[0]
        filter_height = filter_shape[1]
        pad_top = (filter_height - 1) // 2
        pad_bottom = filter_height - 1 - pad_top
        pad_left = (filter_width - 1) // 2
        pad_right = filter_width - 1 - pad_left
        paddings = [[0, 0], [pad_top, pad_bottom], [pad_left, pad_right], [0, 0]]

        image = tf.expand_dims(image, axis=0)
        image = tf.pad(image, paddings, mode=mode, constant_values=constant_values)

        # Filter of shape (filter_width, filter_height, in_channels, 1)
        # has the value of 1 for each element.
        filter_shape += (tf.shape(image)[-1], 1)
        kernel = tf.ones(filter_shape, dtype=image.dtype)

        output = tf.nn.depthwise_conv2d(image, kernel, strides=(1, 1, 1, 1), padding="VALID")
        
        area = tf.cast(filter_shape[0] * filter_shape[1], dtype=tf.float32)
        return tf.squeeze(output / area)
        
        
    check_dataaug_argument(filter_size, "filter_size", function_name="random_blur", data_type=int, tuples=2)
    if filter_size[0] < 1 or filter_size[1] < 1:
        raise ValueError("Argument `filter_size` of function `random_blur`: expecting a tuple "
                         "of 2 integers greater than or equal to 1. Received {}".format(filter_size))
    if padding not in {"reflect", "constant", "symmetric"}:
        raise ValueError('Argument `padding` of function `random_blur`: supported '
                         'values are "reflect", "constant" and "symmetric". '
                         'Received {}'.format(padding))
    
    check_images_shape(images, function_name="random_blur")

    pixels_dtype = images.dtype
    images = tf.cast(images, tf.float32)
    batch_size = tf.shape(images)[0]
    width, height, channels = images.shape[1:]
    
    diag = tf.ones([batch_size])
    mask = tf.linalg.diag(diag, num_rows=-1, num_cols=-1, padding_value=0)
    
    # Sample a filter size for each image
    random_filter_sizes = tf.random.uniform(
                [batch_size], minval=filter_size[0], maxval=filter_size[1] + 1, dtype=tf.int32)
    images_aug = tf.zeros([batch_size, width, height, channels])
    for i in range(batch_size):
        # Blur the image
        filter_shape = [random_filter_sizes[i], random_filter_sizes[i]]
        img = blur_image(images[i], filter_shape, mode=padding.upper())

        if len(img.shape) == 2:
            # This happens when using grayscale images (1 channel).
            img = tf.expand_dims(img, axis=-1)

        # Replicate the blurred image to have a row
        # of the same image of length batch_size
        img_row = tf.tile(img, [batch_size, 1, 1])
        img_row = tf.reshape(img_row, [batch_size, width, height, channels])

        # Replicate the mask to match the row of images
        mask_row = tf.repeat(mask[i], [width * height * channels])
        mask_row = tf.reshape(mask_row, [batch_size, width, height, channels])
        
        images_aug = mask_row*img_row + images_aug

    outputs = apply_change_rate(images, images_aug, change_rate)
    return tf.cast(outputs, pixels_dtype)


def random_gaussian_noise(images, stddev=None, pixels_range=(0.0, 1.0), change_rate=1.0, mode="image"):
    """
    This function adds gaussian noise to input images. The standard 
    deviations of the gaussian distribution are sampled from a specified
    range. The mean of the distribution is equal to 0.

    The function has two modes:
    - image mode: a different standard deviation is used for each image
      of the batch.
    - batch mode: the same standard deviation is used for all the images
      of the batch.
    The image mode creates more image diversity, potentially leading to
    better training results, but run times are longer than in the batch
    mode.
    
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
        mode:
            Either "image" or "batch". If set to "image", noise will be
            sampled using a different standard deviation for each image
            of the batch. If set to "batch", noise will be sampled using
            the same standard deviation for all the images of the batch.
            
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

    if mode not in {"image", "batch"}:
        raise ValueError("\nArgument `mode` of function `random_gaussian_noise`: "
                         "expecting 'image' or 'batch'. Received {}".format(mode))

    check_images_shape(images, function_name="random_gaussian_noise")
    batch_size = tf.shape(images)[0]
    width, height, channels = images.shape[1:]
    
    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    if mode == "batch":
        # Sample an std value, generate gaussian noise and add it to the images
        random_stddev = tf.random.uniform([1], minval=stddev[0], maxval=stddev[1], dtype=tf.float32)
        noise = tf.random.normal([batch_size, width, height, channels], mean=0.0, stddev=random_stddev)
        images_aug = images + noise
    else:
        diag = tf.ones([batch_size])
        mask = tf.linalg.diag(diag, num_rows=-1, num_cols=-1, padding_value=0)
        
        # Sample an std value for each image
        random_stddev = tf.random.uniform([batch_size], minval=stddev[0], maxval=stddev[1], dtype=tf.float32)
        images_aug = tf.zeros([batch_size, width, height, channels], dtype=tf.float32)
        for i in range(batch_size):
            # Add gaussian noise to the image
            noise = tf.random.normal([width, height, channels], mean=0.0, stddev=random_stddev[i])
            img = images[i] + noise

            # Replicate the noisy image to have a row of 
            # the same image of length batch_size
            img_row = tf.tile(img, [batch_size, 1, 1])
            img_row = tf.reshape(img_row, [batch_size, width, height, channels])

            # Replicate the mask to match the row of images
            mask_row = tf.repeat(mask[i], [width * height * channels])
            mask_row = tf.reshape(mask_row, [batch_size, width, height, channels])
            
            images_aug = mask_row*img_row + images_aug
            
    # Clip the images with noise added
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)

    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_jpeg_quality(images, jpeg_quality=100, pixels_range=(0.0, 1.0), change_rate=1.0):
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
        jpeg_quality = (5, 100)
    """
    
    # Only tuples are accepted for the `jpeg_quality` argument.
    quality = jpeg_quality
    check_dataaug_argument(quality, "jpeg_quality", function_name="random_jpeg_quality", data_type=int, tuples=2)
    if quality[0] < 0 or quality[0] > 100 or quality[1] < 0 or quality[1] > 100:
        raise ValueError("Argument `jpeg_quality` of function `random_jpeg_quality`: expecting a tuple of "
                         "2 integers in the interval [0, 100]. Received {}".format(quality))
    check_images_shape(images, function_name="random_jpeg_quality")
    batch_size = tf.shape(images)[0]
    width, height, channels = images.shape[1:]

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