# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf


def check_images_shape(images, function_name=None, allow_grayscale=True):
    """
    This function is a utility that checks that input images have
    the expected shape and number of channels.
    
    Inputs:
        images:
            A tensor. The shape must be [batch_size, width, height, channels],
            otherwise an exception is thrown.
        function_name:
            A string, the name of the function calling check_image_shape().
        allow_grayscale:
            A boolean, specifies whether grayscable images are supported.
            If set to True, the number of channels may be equal to 1 or 3.
            If set to False, it must be equal to 3 (RGB images only).
    """
    
    if len(images.shape) != 4 or (images.shape[-1] != 3 and images.shape[-1] != 1):
        raise ValueError("\nFunction `{}`: input images must have shape "
                         "[batch_size, width, height, channels]\n"
                         "with `channels` equal 3 (RGB) or 1 (grayscale). "
                         "Received shape {}".format(function_name, images.shape))

    if not allow_grayscale and images.shape[-1] == 1:
        raise ValueError("Function `{}`: Expecting RGB images, grayscale not supported".format(function_name))
    

def check_dataaug_argument(arg, arg_name, function_name=None, data_type=None, tuples=1):
    """
    This function is a utility that checks the data types of arguments
    used in data augmentation functions. Argument values may be integers,
    floats or tuples of length 2.
    
    Inputs:
        arg:
            The argument to check.
        arg_name:
            A string, the name of the argument.
        function_name:
            A string, the name of the function calling check_dataaug_argument().
        data_type:
            Specifies the expected data type for the argument. It may 
            be int, float, (int, float) or (float, int).
        tuples:
            An integer, specifies how tuples should be handled:
                0: tuples are not accepted, scalars only.
                1: both tuples and scalars are accepted.
                2. scalars are not accepted, tuples only.
            By default, both scalers and tuples are accepted.
    """
    def check_data_type(arg):
        # Check that the data type of the argument is as expected.
        arg_type = type(arg)
        if data_type == int and arg_type != int:
           raise ValueError("\nArgument `{}` of function `{}`: expecting integer values. "
                            "Received {}".format(arg_name, function_name, arg))
        if data_type == float and arg_type != float:
           raise ValueError("\nArgument `{}` of function `{}`: expecting float values. "
                            "Received {}".format(arg_name, function_name, arg))
        if data_type == (int, float) or data_type == (float, int):
            if arg_type != int and arg_type != float:
                raise ValueError("\nArgument `{}` of function `{}`: expecting float or integer values. "
                                "Received {}".format(arg_name, function_name, arg))


    if tuples not in {0, 1, 2}:
        # The function is used incorrectly.
        raise ValueError("\nArgument `{}` of function `{}`: expecting an integer "
                         "value in {0, 1, 2}".format(arg_name, function_name))
    if arg is None:
        # The argument is not set.            
        raise ValueError("\nFunction `{}`: the argument `{}` is not set. "
                         "Received None.".format(function_name, arg_name))
                         
    if not isinstance(arg, (int, float, tuple, list)):
        raise ValueError("\nArgument `{}` of function `{}`: invalid data type. "
                         "Received {}".format(arg_name, function_name, arg))
                         
    if tuples == 0:
        # Tuples are not accepted, scalars only.
        if isinstance(arg, (tuple, list)):
            raise ValueError("\nArgument `{}` of function `{}`: tuples are not supported. "
                            "Received {}".format(arg_name, function_name, arg))
    if tuples == 2:
        # Only tuples are accepted, no scalars.
        if not isinstance(arg, (tuple, list)):
            raise ValueError("\nArgument `{}` of function `{}`: expecting a tuple of length 2. "
                             "Received {}".format(arg_name, function_name, arg))
    if isinstance(arg, (tuple, list)):
        if len(arg) != 2:
            raise ValueError("\nArgument `{}` of function `{}`: the tuple should have 2 elements. "
                            "Received {}".format(arg_name, function_name, arg))
        if arg[1] <= arg[0]:
            raise ValueError("\nArgument `{}` of function `{}`: the tuple right value should be greater "
                             "than the left value. Received{}".format(arg_name, function_name, arg))  
        check_data_type(arg[0])
        check_data_type(arg[1])
    else:
        check_data_type(arg)


def remap_pixel_values_range(images, input_range, output_range, dtype=tf.float32):
    """
    This function remaps the pixel values of input images to a different range
    of values using a linear transformation.
    For example, it can be used to remap input pixels with values in the [0, 255] 
    interval with uint8 data type to output pixels in the interval [0.0, 1.0] 
    with float data type.
    """
    if input_range != output_range:
        s0, s1 = input_range
        t0, t1 = output_range
        images = tf.cast(images, tf.float32)
        images = ((t1 - t0) * images + t0*s1 - t1*s0) / (s1 - s0)
        images = tf.clip_by_value(images, t0, t1)
        
    return tf.cast(images, dtype)


def apply_change_rate(images, images_augmented, change_rate=1.0): 
    """
    This function outputs a mix of augmented images and original
    images. The argument `change_rate` is a float in the interval 
    [0.0, 1.0] representing the number of changed images versus 
    the total number of input images average ratio. For example,
    if `change_rate` is set to 0.25, 25% of the input images will
    get changed on average (75% won't get changed). If it is set
    to 0.0, no images are changed. If it is set to 1.0, all the
    images are changed.
    """
    
    if change_rate < 0. or change_rate > 1.:
        raise ValueError("The value of `change_rate` must be in the interval [0, 1]. ",
                         "Received {}".format(change_rate))

    batch_size = tf.shape(images)[0]
    width, height, channels = images.shape[1:]
    
    probs = tf.random.uniform([batch_size], minval=0, maxval=1, dtype=tf.float32)
    change = tf.where(probs < change_rate, True, False)
    
    # Create a mask to apply to images
    mask = tf.repeat(change, width * height * channels)
    mask = tf.reshape(mask, [batch_size, width, height, channels])
    mask_not = tf.math.logical_not(mask)
    mask = tf.cast(mask, images.dtype)
    
    mask_not = tf.cast(mask_not, images.dtype)

    return mask_not * images + mask * images_augmented
