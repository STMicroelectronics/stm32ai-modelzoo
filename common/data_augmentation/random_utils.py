# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf


def grayscale_not_supported(images, function_name=None):
    """
    Docstring for grayscale_not_supported. Reports an error message if grayscale images are detected 
    in the input images batch.
    
    Args: 
        images (tf.Tensor): batch of images
        function_name (str): name of the augmentation function
    """

    message = f"\nFunction `{function_name}`: grayscale images are not supported."                         
    tf.debugging.assert_equal(tf.shape(images)[-1], tf.constant(3), message)


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
    def _check_data_type(arg):
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
        _check_data_type(arg[0])
        _check_data_type(arg[1])
    else:
        _check_data_type(arg)


def remap_pixel_values_range(images, input_range, output_range, dtype=tf.float32):
    """
    This function remaps the pixel values of input images to a different range
    of values using a linear transformation.
    For example, it can be used to remap input pixels with values in the [0, 255] 
    interval with uint8 data type to output pixels in the interval [0.0, 1.0] 
    with float data type.

        Args:
            images (tf.Tensor): batch of input images
            input_range (tuple): pixels range at input
            output_range (tuple): pixels range at output
            dtype: type to cast output images

        Returns:
            (tf.Tensor): batch of remapped and casted images
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
        Args:
            images (tf.Tensor): input batch of images
            images_augmented (tf.Tensor): output augmented images
            change_rate (float): probability to apply augmentation
        Returns:
            (tf.Tensor): stacking of augmented and non augmented images 
    """
    
    if change_rate == 1.0:
        return images_augmented

    if change_rate < 0. or change_rate > 1.:
        raise ValueError("The value of `change_rate` must be in the interval [0, 1]. ",
                         "Received {}".format(change_rate))

    images_shape = tf.shape(images)
    batch_size = images_shape[0]
    width = images_shape[1]
    height = images_shape[2]
    channels = images_shape[3]
    
    probs = tf.random.uniform([batch_size], minval=0, maxval=1, dtype=tf.float32)
    change = tf.where(probs < change_rate, True, False)
    
    # Create a mask to apply to images
    mask = tf.repeat(change, width * height * channels)
    mask = tf.reshape(mask, [batch_size, width, height, channels])
    mask_not = tf.math.logical_not(mask)
    mask = tf.cast(mask, images.dtype)
    
    mask_not = tf.cast(mask_not, images.dtype)

    return mask_not * images + mask * images_augmented

