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
Some of the functions included in this package are equivalent Tensorflow 
implementations of functions from:

    The Pillow (PIL) ImagesOps Module
    https://pillow.readthedocs.io/en/stable/reference/ImageOps.html

    Copyright (c) 1997-2011 by Secret Labs AB
    Copyright (c) 1995-2011 by Fredrik Lundh
    Copyright (c) 2010-2023 by Jeffrey A. Clark (Alex) and contributors

The ImagesOps functions are sharpness, posterize, invert, solarize, 
equalize and autocontrast.
"""

import tensorflow as tf
from common.data_augmentation import grayscale_not_supported, check_dataaug_argument, remap_pixel_values_range, apply_change_rate


def random_contrast(images, factor=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly changes the contrast of input images.
    
    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels].
        factor:
            A float or a tuple of 2 floats, specifies the range of values 
            contrast factors are sampled from. If a scalar value v
            is used, it is equivalent to the tuple (-v, v).
            The contrast of an input image is:
            - decreased if the contrast factor is less than 0.
            - increased if the contrast factor is greater than 0.
            - unchanged if the contrast factor is equal to 0.
        pixels_range:
            A tuple of 2 integers or floats, specifies the range of pixel
            values in the input images and output images. Any range is 
            supported. It generally is either [0, 255], [0, 1] or [-1, 1].
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.
            
    Returns:
        The images with adjusted contrast. The data type and range
        of pixel values are the same as in the input images.
    """

    check_dataaug_argument(factor, "factor", function_name="random_contrast", data_type=(int, float))
    if not isinstance(factor, (tuple, list)):
        factor = (1 - factor, 1 + factor)
    
    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]
    channels = images_shape[3]

    pixels_dtype = images.dtype
    
    # Generate random alpha values and replicate to channels
    alpha = tf.random.uniform([batch_size], minval=factor[0], maxval=factor[1], dtype=tf.float32)
    alpha = tf.repeat(alpha, channels)
    alpha = tf.reshape(alpha, [batch_size, 1, 1, channels])
    
    # Calculate the average of pixel values in each channel
    x = tf.reshape(images, [batch_size, width * height, channels])
    x = tf.math.reduce_mean(x, axis=1)
    channel_mean_pix = tf.reshape(x, [batch_size, 1, 1, channels])

    images_aug = alpha*(images - channel_mean_pix) + channel_mean_pix
    images_aug = tf.clip_by_value(images_aug, pixels_range[0], pixels_range[1])
    outputs = apply_change_rate(images, images_aug, change_rate)

    return tf.cast(outputs, pixels_dtype)


def random_brightness(images, factor=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly changes the brightness of input images.

    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels].
        factor:
            A float or a tuple of 2 floats, specifies the range of values
            brightness factors are sampled from. If a scalar value v
            is used, it is equivalent to the tuple (-v, v).
            The brightness of an input image is:
            - decreased if the brightness factor is less than 0.
            - increased if the brightness factor is greater than 0.
            - unchanged if the brightness factor is equal to 0.
        pixels_range:
            A tuple of 2 integers or floats, specifies the range of pixel
            values in the input images and output images. Any range is 
            supported. It generally is either [0, 255], [0, 1] or [-1, 1].
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.
            
    Returns:
        The images with adjusted brightness. The data type and range
        of pixel values are the same as in the input images.
    """
    check_dataaug_argument(factor, "factor", function_name="random_brightness", data_type=(int, float))
    if not isinstance(factor, (tuple, list)):
        factor = (-factor, factor)

    batch_size = tf.shape(images)[0]
    channels = tf.shape(images)[-1]

    pixels_dtype = images.dtype
    
    # Generate random beta values and replicate to channels
    beta = tf.random.uniform([batch_size], minval=factor[0], maxval=factor[1], dtype=tf.float32)
    beta = tf.repeat(beta, channels)
    beta = tf.reshape(beta, [batch_size, 1, 1, channels])

    images_aug = images + beta
    images_aug = tf.clip_by_value(images_aug, pixels_range[0], pixels_range[1])
    outputs = apply_change_rate(images, images_aug, change_rate)

    return tf.cast(outputs, pixels_dtype)


def random_gamma(images, gamma=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly changes the pixels of input images
    according to the equation:
           Out = In**gamma

    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels].
        gamma:
            A tuple of 2 floats greater than 0.0, specifies the range
            of values gamma factors are sampled from (one per image).
            For a given input image, the output image is:
            - darker if the gamma factor is less than 1.0.
            - brighter if the gamma factor is greater than 1.0.
            - unchanged if the gamma factor is equal to 1.0
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
        The images with adjusted gamma. The data type and range
        of pixel values are the same as in the input images.

    Usage example:
        gamma = (0.2, 2.0)
    """

    # Only tuple values are accepted for the `gamma` argument.
    check_dataaug_argument(gamma, "gamma", function_name="random_gamma", data_type=(int, float), tuples=2)
    if gamma[0] < 0 or gamma[1] < 0:
        raise ValueError("\nArgument `gamma` of function `random_gamma`: expecting "
                         "a tuple of 2 floats greater than or equal to 0. Received {}".format(gamma))
    
    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]
    channels = images_shape[3]
    
    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)
    
    x = tf.random.uniform([batch_size], minval=gamma[0], maxval=gamma[1], dtype=tf.float32)
    x = tf.repeat(x, width * height * channels)
    random_gamma = tf.reshape(x, [batch_size, width, height, channels])

    images_aug = tf.math.pow(images, random_gamma)
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)
    
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)
    
    
def random_hue(images, delta=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly changes the hue of input RGB images.
    Images are first converted to HSV (Hue, Saturation, Value) 
    representation, then a randomly chosen offset is added to 
    the hue channel, and the images are converted back to
    RGB representation.
    
    Args:
        images:
            Input RGB images, a tensor with shape
            [batch_size, width, height, 3].   
        delta:
            A float or a tuple of 2 floats, specifies the range 
            of values the offsets added to the hue channel are
            sampled from(one per image). If a scalar value v is 
            used, it is equivalent to the tuple (-v, v).
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
        The images with adjusted hue. The data type and range
        of pixel values are the same as in the input images.
    """

    check_dataaug_argument(delta, "delta", function_name="random_hue", data_type=(int, float))
    if not isinstance(delta, (tuple, list)):
        delta = (-delta, delta)
    grayscale_not_supported(images, function_name="random_hue")
    
    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]
    
    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    shape = [batch_size, width, height]
    x = tf.random.uniform([batch_size], minval=delta[0], maxval=delta[1], dtype=tf.float32)
    x = tf.repeat(x, width * height)
    random_delta = tf.reshape(x, shape)

    offset = tf.stack([tf.zeros(shape) + random_delta, tf.zeros(shape), tf.zeros(shape)], axis=-1)
    hsv_images = tf.image.rgb_to_hsv(images) + offset   
     
    images_aug = tf.image.hsv_to_rgb(hsv_images)
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_saturation(images, delta=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly changes the value of input RGB images.
    Images are first converted to HSV (Hue, Saturation, Value) 
    representation, then a randomly chosen offset is added to 
    the saturation channel, and the images are converted back
    to RGB representation.

    Args:
        images:
            Input RGB images, a tensor with shape
            [batch_size, width, height, 3].
        delta:
            A float or a tuple of 2 floats, specifies the range 
            of values the offsets added to the saturation channel
            are sampled from (one per image). If a scalar value v
            is used, it is equivalent to the tuple (-v, v).
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
        The images with adjusted saturation. The data type and range
        of pixel values are the same as in the input images.
    """
    
    check_dataaug_argument(delta, "delta", function_name="random_saturation", data_type=(int, float))
    if not isinstance(delta, (tuple, list)):
        delta = (-delta, delta)
    grayscale_not_supported(images, function_name="random_saturation")
    
    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]
    
    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    shape = [batch_size, width, height]
    x = tf.random.uniform([batch_size], minval=delta[0], maxval=delta[1], dtype=tf.float32)
    x = tf.repeat(x, width * height)
    random_delta = tf.reshape(x, shape)

    offset = tf.stack([tf.zeros(shape), tf.zeros(shape) + random_delta, tf.zeros(shape)], axis=-1)
    hsv_images = tf.image.rgb_to_hsv(images) + offset   
    
    images_aug = tf.image.hsv_to_rgb(hsv_images)
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_value(images, delta=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly changes the value of input RGB images.
    Images are first converted to HSV (Hue, Saturation, Value) 
    representation, then a randomly chosen offset is added to 
    the value channel, and the images are converted back to
    RGB representation.

    Args:
        images:
            Input RGB images, a tensor with shape
            [batch_size, width, height, 3].
        delta:
            A float or a tuple of 2 floats, specifies the range 
            of values the offsets added to the value channel are
            sampled from (one per image). If a scalar value v is 
            used, it is equivalent to the tuple (-v, v).
        change_rate:
            A float in the interval [0, 1], the number of changed images
            versus the total number of input images average ratio.
            For example, if `change_rate` is set to 0.25, 25% of the input
            images will get changed on average (75% won't get changed).
            If it is set to 0.0, no images are changed. If it is set
            to 1.0, all the images are changed.
            
    Returns:
        The images with adjusted value. The data type and range
        of pixel values are the same as in the input images.
    """
    
    check_dataaug_argument(delta, "delta", function_name="random_value", data_type=(int, float))
    if not isinstance(delta, (tuple, list)):
        delta = (-delta, delta)
    grayscale_not_supported(images, function_name="random_value")
    
    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    shape = [batch_size, width, height]
    x = tf.random.uniform([batch_size], minval=delta[0], maxval=delta[1], dtype=tf.float32)
    x = tf.repeat(x, width * height)
    random_delta = tf.reshape(x, shape)

    offset = tf.stack([tf.zeros(shape), tf.zeros(shape), tf.zeros(shape) + random_delta], axis=-1)
    hsv_images = tf.image.rgb_to_hsv(images) + offset   
     
    images_aug = tf.image.hsv_to_rgb(hsv_images)
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_hsv(images, 
               hue_delta=None, saturation_delta=None, value_delta=None,
               pixels_range=(0.0, 1.0),
               change_rate=1.0):
    """
    This function randomly changes the hue, saturation and value
    of input RGB images. Images are first converted to HSV (Hue,
    Saturation, Value) representation, then randomly chosen offsets
    are added to the hue, saturation and value channels. Finally,
    the images are converted back to RGB representation.

    Args:
        images:
            Input RGB images, a tensor with shape
            [batch_size, width, height, 3]. 
        hue_delta:
            A float or a tuple of 2 floats, specifies the range 
            of values the offsets added to the hue channel are sampled
            from. If a scalar value v is used, it is equivalent
            to the tuple (-v, v).
        saturation_delta:
            A float or a tuple of 2 floats, specifies the range of
            values the offsets added to the saturation channel are
            sample from (one per image). If a scalar value v is used,
            it is equivalent to the tuple (-v, v).
        value_delta:
            A float or a tuple of 2 floats, specifies the range of
            values the offsets added to the value channel are sampled
            from (one per image). If a scalar value v is used, it is 
            equivalent to the tuple (-v, v).
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
        The images with adjusted hue, saturation and value. The data type
        and range of pixel values are the same as in the input images.
    """
    
    check_dataaug_argument(hue_delta, "hue_delta", function_name="random_hsv", data_type=(int, float))
    if not isinstance(hue_delta, (tuple, list)):
        hue_delta = (-hue_delta, hue_delta)
        
    check_dataaug_argument(saturation_delta, "saturation_delta", function_name="random_hsv", data_type=(int, float))
    if not isinstance(saturation_delta, (tuple, list)):
        saturation_delta = (-saturation_delta, saturation_delta)
        
    check_dataaug_argument(value_delta, "value_delta", function_name="random_hsv", data_type=(int, float))
    if not isinstance(value_delta, (tuple, list)):
        value_delta = (-value_delta, value_delta)

    grayscale_not_supported(images, function_name="random_hsv")
    
    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    # Generate random hue offset to add to the hue channel
    shape = [batch_size, width, height]
    x = tf.random.uniform([batch_size], minval=hue_delta[0], maxval=hue_delta[1], dtype=tf.float32)
    x = tf.repeat(x, width * height)
    hue_offset = tf.reshape(x, shape)
    
    # Generate random saturation offset to add to the saturation channel
    x = tf.random.uniform([batch_size], minval=saturation_delta[0], maxval=saturation_delta[1], dtype=tf.float32)
    x = tf.repeat(x, width * height)
    saturation_offset = tf.reshape(x, shape)
    
    # Generate random value offset to add to the value channel
    x = tf.random.uniform([batch_size], minval=value_delta[0], maxval=value_delta[1], dtype=tf.float32)
    x = tf.repeat(x, width * height)
    value_offset = tf.reshape(x, shape)

    offset = tf.stack([
                tf.zeros(shape) + hue_offset,
                tf.zeros(shape) + saturation_offset,
                tf.zeros(shape) + value_offset],
                axis = - 1)

    hsv_images = tf.image.rgb_to_hsv(images) + offset
    
    images_aug = tf.image.hsv_to_rgb(hsv_images)
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_rgb_to_hsv(images, pixels_range=(0.0, 1.0), change_rate=0.25):
    """
    This function converts input RGB images to HSV (Hue, Saturation,
    Value) representation.

    Args:
        images:
            Input RGB images, a tensor with shape
            [batch_size, width, height, 3].
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
        The images converted to HSV representation. The data type and
        range of pixel values are the same as in the input images.
    """
    
    grayscale_not_supported(images, function_name="random_rgb_to_hsv")

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)
    
    images_aug = tf.image.rgb_to_hsv(images)
    images_aug = tf.clip_by_value(images_aug, 0.0, 1.0)
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)
     

def random_rgb_to_grayscale(images, pixels_range=(0.0, 1.0), change_rate=0.25):
    """
    This function converts input RGB images to grayscale. Output 
    images are RGB images with identical R, G and B channels.

    Args:
        images:
            Input RGB images, a tensor with shape
            [batch_size, width, height, 3].
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
        The images converted to grayscale. The data type and range
        of pixel values are the same as in the input images. 
    """
    
    grayscale_not_supported(images, function_name="random_rgb_to_grayscale")

    pixels_dtype = images.dtype    
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    x = 0.299*images[..., 0] + 0.587*images[..., 1] + 0.114*images[..., 2]
    x = tf.clip_by_value(x, 0.0, 1.0)
    x = tf.repeat(x, 3)
    images_aug = tf.reshape(x, tf.shape(images))

    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_sharpness(images, factor=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly increases the sharpness of input images.
    Use the random_blur() function if you want to decrease the sharpness.
    
    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        factor:
            A float or a tuple of 2 floats greater than or equal to 0,
            specifies the range of values the sharpness factors are sampled
            from (one per image). If a scalar value v is used, it is equivalent
            to the tuple (0, v).
            The larger the value of the sharpness factor, the more pronounced
            the sharpening effect is. If the sharpness factor is equal to 0.0,
            the images are unchanged.
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
        The images with adjusted sharpness. The data type and range
        of pixel values are the same as in the input images.

    Usage examples:
        factor = (0, 4)
    """

    check_dataaug_argument(factor, "factor", function_name="random_sharpness", data_type=(int, float))
    factor_arg = factor
    if not isinstance(factor, (tuple, list)):
        factor = (0.0, factor)
    if factor[0] < 0 or factor[1] < 0:
        raise ValueError("\nArgument `factor` of function `random_sharpness`: expecting a float or a tuple "
                         "of 2 floats greater than or equal to 0.0. Received {}".format(factor_arg))
    
    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]
    channels = images_shape[3]

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 255.0), dtype=tf.float32)
    
    # SMOOTH PIL Kernel
    kernel = (
        tf.constant([[1, 1, 1], [1, 5, 1], [1, 1, 1]], dtype=tf.float32, shape=[3, 3, 1, 1]) / 13.0
    )
    kernel = tf.tile(kernel, [1, 1, channels, 1])

    # Apply kernel channel-wise
    degenerate = tf.nn.depthwise_conv2d(
        images, kernel, strides=[1, 1, 1, 1], padding="VALID", dilations=[1, 1]
    )

    # For the borders of the resulting image, fill in the values of the original image.
    mask = tf.ones_like(degenerate)
    padded_mask = tf.pad(mask, [[0, 0], [1, 1], [1, 1], [0, 0]])
    padded_degenerate = tf.pad(degenerate, [[0, 0], [1, 1], [1, 1], [0, 0]])
    padded = tf.where(tf.equal(padded_mask, 1), padded_degenerate, images)

    # Blend the original images and the degenerate images
    x = tf.random.uniform([batch_size], minval=factor[0], maxval=factor[1], dtype=tf.float32)
    x = tf.repeat(x, width * height * channels)
    random_factor = tf.reshape(x, [batch_size, width, height, channels])
    
    x = images + random_factor * (images - padded)
    images_aug = tf.round(tf.clip_by_value(x, 0.0, 255.0))
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 255.0), pixels_range, dtype=pixels_dtype)


def random_posterize(images, bits=None, pixels_range=(0.0, 1.0), change_rate=1.0):
    """
    This function randomly reduces the number of bits used 
    for each color channel of input images. Color contraction
    occurs when the number of bits is reduced.

    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        bits:
            A tuple of 2 integers in the interval [1, 8], specifies
            the range of values the numbers of bits used to encode
            pixels are sampled from (one per image). The lower the 
            number of bits, the more degraded the image is.
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
        The posterized images. The data type and range of pixel values
        are the same as in the input images.
    
    Usage example:
        bits = (2, 8)
    """
    
    # Only tuple values are accepted for the `bits` argument.
    check_dataaug_argument(bits, "bits", function_name="random_posterize", data_type=int, tuples=2)
    if bits[0] < 1 or bits[0] > 8 or bits[1] < 0 or bits[1] > 8:
        raise ValueError("Argument `bits` of function `random_posterize`: expecting of tuple of "
                         "2 integers in the interval [1, 8]. Received {}".format(bits))

    batch_size = tf.shape(images)[0]

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0, 255), dtype=tf.uint8)
    
    # Generate a random number of bits for each image
    shift = tf.random.uniform([batch_size, 1, 1, 1], minval=bits[0], maxval=bits[1] + 1, dtype=tf.int32)
    shift = 8 - tf.cast(shift, tf.uint8)
    
    rs = tf.bitwise.right_shift(images, shift)
    images_aug = tf.bitwise.left_shift(rs, shift)
    
    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0, 255), pixels_range, dtype=pixels_dtype)


def random_invert(images, pixels_range=(0.0, 1.0), change_rate=0.25):
    """
    This function inverts (negates) all the pixel values of input images.

    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
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
        The inverted images. The data type and range of pixel values
        are the same as in the input images.
    """
        
    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 1.0), dtype=tf.float32)

    images_aug = 1.0 - images

    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 1.0), pixels_range, dtype=pixels_dtype)


def random_solarize(images, pixels_range=(0.0, 1.0), change_rate=0.25):
    """
    This function solarizes the input images. For each image:
    - a threshold is sampled in the interval [0, 255]
    - the pixels that are above the threshold are inverted (negated).

    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
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
        The solarized images. The data type and range of pixel values
        are the same as in the input images.
    """

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0, 255), dtype=tf.int32)

    batch_size = tf.shape(images)[0]
    random_threshold = tf.random.uniform([batch_size, 1, 1, 1], minval=0, maxval=256, dtype=tf.int32)
    images_aug = tf.where(images >= random_threshold, 255 - images, images)
    
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0, 255), pixels_range, dtype=pixels_dtype)


def random_autocontrast(images, cutoff=10, pixels_range=(0.0, 1.0), change_rate=0.25):    
    """
    This function maximizes the contrast of input images.

    Cutoff percent of the lightest and darkest pixels are first
    removed from the image, then the image is remapped so that
    the darkest pixel becomes black (0), and the lightest becomes
    white (255).

    Args:
        images:
            Input RGB or grayscale images, a tensor with shape
            [batch_size, width, height, channels]. 
        cutoff:
            A positive integer greater than 0, specifies the percentage
            of pixels to remove on the low and high ends of the pixels 
            histogram. If `cutoff` is equal to 0, the images are unchanged.
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
        The images with maximized contrast. The data type and range
        of pixel values are the same as in the input images.
    """
    
    grayscale_not_supported(images, function_name="random_autocontrast")

    check_dataaug_argument(cutoff, "cutoff", function_name="random_autocontrast", data_type=int)
    if cutoff < 0 or cutoff > 100:
        raise ValueError("Argument `cutoff` of function `random_autocontrast`: expecting integer values "
                         "in the interval [0, 100]. Received {}".format(cutoff))

    pixels_dtype = images.dtype
    images = remap_pixel_values_range(images, pixels_range, (0.0, 255.0), dtype=tf.float32)

    def scale_channel(image):
        batch_size = tf.shape(image)[0]

        # Calculate the numbers of pixels to remove
        w = tf.shape(images)[1]
        h = tf.shape(images)[2]
        lower_cut = upper_cut = tf.cast((w * h * cutoff) // 100, dtype=tf.int32)

        # Cut off pixels
        img = tf.reshape(image, [batch_size, w * h])        
        img = tf.sort(img, axis=-1)
        img = img[:, lower_cut:]
        img = img[:, :-upper_cut]

        # Find the lowest and highest
        # pixel values after cutoff
        lo = tf.math.reduce_min(img, axis=-1)
        hi = tf.math.reduce_max(img, axis=-1)

        # Calculate rescaling coeffs
        lo = tf.reshape(lo, [batch_size, 1, 1])
        hi = tf.reshape(hi, [batch_size, 1, 1])
        scale = 255.0 / (hi - lo)
        offset = -lo * scale
        
        # Rescale the image
        scaled_image = tf.clip_by_value(image * scale + offset, 0.0, 255.0)
        return tf.where(hi > lo, scaled_image, image)
    
    rs = scale_channel(images[..., 0])
    gs = scale_channel(images[..., 1])
    bs = scale_channel(images[..., 2])
    images_aug = tf.stack([rs, gs, bs], axis=-1)

    # Apply change rate and remap pixel values to input images range
    outputs = apply_change_rate(images, images_aug, change_rate)
    return remap_pixel_values_range(outputs, (0.0, 255.0), pixels_range, dtype=pixels_dtype)
