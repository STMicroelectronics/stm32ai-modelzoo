# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2016 Refikcanmalli
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from tensorflow import keras
from tensorflow.keras import layers
from typing import Tuple


def fire_module(x: keras.layers.Layer, fire_id: int, squeeze: int = 16, expand: int = 64) -> keras.layers.Layer:
    """
    Fire module for the SqueezeNet model.
    Implements expand layer, which has a mix of 1x1 and 3x3 filters,
    by using two conv layers concatenated in the channel dimension.

    Args:
    - x: input tensor.
    - fire_id: integer, the id of the fire module.
    - squeeze: integer, the number of filters in the squeeze layer.
    - expand: integer, the number of filters in the expand layer.

    Returns:
    - keras.layers.Layer object, the output tensor.

    """
    # Define some constants
    sq1x1 = "squeeze1x1"
    exp1x1 = "expand1x1"
    exp3x3 = "expand3x3"
    relu = "relu_"

    # Define the id of the fire module
    s_id = 'fire' + str(fire_id) + '/'

    # Get the channel axis
    if keras.backend.image_data_format() == 'channels_first':
        channel_axis = 1
    else:
        channel_axis = 3

    # Squeeze layer
    x = layers.Convolution2D(squeeze, (1, 1), padding='valid', name=s_id + sq1x1)(x)
    x = layers.Activation('relu', name=s_id + relu + sq1x1)(x)

    # Expand layer
    left = layers.Convolution2D(expand, (1, 1), padding='valid', name=s_id + exp1x1)(x)
    left = layers.Activation('relu', name=s_id + relu + exp1x1)(left)

    right = layers.Convolution2D(expand, (3, 3), padding='same', name=s_id + exp3x3)(x)
    right = layers.Activation('relu', name=s_id + relu + exp3x3)(right)

    x = layers.concatenate([left, right], axis=channel_axis, name=s_id + 'concat')

    return x


def get_squeezenetv11(num_classes: int = None, input_shape: Tuple[int, int, int] = None,
                      dropout: float = None) -> keras.Model:
    """
    Returns a SqueezeNet model with the specified number of output classes.

    Args:
    - num_classes: integer, the number of output classes.
    - input_shape: tuple of integers, the shape of the input tensor (height, width, channels).
    - dropout: float between 0 and 1, the dropout rate to apply.

    Returns:
    - keras.Model object, the SqueezeNet model.

    """
    # Define the input tensor
    input_image = layers.Input(input_shape)

    # First convolutional layer
    x = layers.Convolution2D(64, (3, 3), strides=(2, 2), padding='valid', name='conv1')(input_image)
    x = layers.Activation('relu', name='relu_conv1')(x)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool1')(x)

    # Fire modules
    x = fire_module(x, fire_id=2, squeeze=16, expand=64)
    x = fire_module(x, fire_id=3, squeeze=16, expand=64)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool3')(x)

    x = fire_module(x, fire_id=4, squeeze=32, expand=128)
    x = fire_module(x, fire_id=5, squeeze=32, expand=128)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool5')(x)

    x = fire_module(x, fire_id=6, squeeze=48, expand=192)
    x = fire_module(x, fire_id=7, squeeze=48, expand=192)
    x = fire_module(x, fire_id=8, squeeze=64, expand=256)
    x = fire_module(x, fire_id=9, squeeze=64, expand=256)

    # Dropout layer
    if dropout:
        x = layers.Dropout(dropout, name='drop9')(x)

    # Final convolutional layer
    x = layers.Convolution2D(num_classes, (1, 1), padding='valid', name='conv10')(x)
    x = layers.Activation('relu', name='relu_conv10')(x)

    # Global average pooling layer
    x = layers.GlobalAveragePooling2D()(x)

    # Softmax activation layer
    output = layers.Activation('softmax', name='loss')(x)

    # Create the model
    model = keras.Model(input_image, output, name='SqueezeNet_v1.1')

    return model
