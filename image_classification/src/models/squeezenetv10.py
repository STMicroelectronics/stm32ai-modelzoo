# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import tensorflow.keras as keras
from tensorflow.keras import layers
from typing import Tuple

def fire_module(x: layers.Input, squeeze: int, expand: int, fire_id: str) -> layers.Concatenate:
    """
    Fire module for the SqueezeNet model.
    Implements expand layer, which has a mix of 1x1 and 3x3 filters,
    by using two conv layers concatenated in the channel dimension.

    Args:
        x: Input tensor.
        squeeze: Number of filters in the squeeze layer.
        expand: Number of filters in the expand layer.
        fire_id: Unique identifier for the fire module.

    Returns:
        A concatenated tensor.
    """
    x = layers.Convolution2D(squeeze, (1, 1), activation='relu', name=f"{fire_id}_squeeze")(x)
    x = layers.BatchNormalization(name=f"{fire_id}_squeeze_bn")(x)

    left = layers.Convolution2D(expand, (1, 1), padding='same', activation='relu', name=f"{fire_id}_expand_1x1")(x)
    right = layers.Convolution2D(expand, (3, 3), padding='same', activation='relu', name=f"{fire_id}_expand_3x3")(x)
    x = layers.concatenate([left, right], axis=3, name=f"{fire_id}_expand_merge")

    return x


def get_squeezenetv10(input_shape: Tuple[int, int, int] = None, num_classes: int = None,
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
    input_image = keras.Input(shape=input_shape)

    # First convolutional layer
    x = layers.Convolution2D(96, (7, 7), strides=(2, 2), name='conv1')(input_image)
    x = layers.Activation('relu', name='relu_conv1')(x)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool1')(x)

    # Fire modules
    x = fire_module(x, squeeze=16, expand=64, fire_id='fire2')
    x = fire_module(x, squeeze=16, expand=64, fire_id='fire3')
    x = fire_module(x, squeeze=32, expand=128, fire_id='fire4')
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool4')(x)

    x = fire_module(x, squeeze=32, expand=128, fire_id='fire5')
    x = fire_module(x, squeeze=48, expand=192, fire_id='fire6')
    x = fire_module(x, squeeze=48, expand=192, fire_id='fire7')
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool8')(x)

    x = fire_module(x, squeeze=64, expand=256, fire_id='fire9')

    # Dropout layer
    if dropout:
        x = layers.Dropout(dropout, name='dropout')(x)

    # Final convolutional layer
    x = layers.Convolution2D(num_classes, (1, 1), name='conv10')(x)
    x = layers.Activation('relu', name='relu_conv10')(x)
    x = layers.BatchNormalization(name='bn')(x)

    # Global average pooling layer
    x = layers.GlobalAveragePooling2D(name='average_pool10')(x)

    # Softmax activation layer
    output = layers.Activation('softmax', name='softmax')(x)

    # Create the model
    model = keras.Model(input_image, output, name="SqueezeNet_v1.0")

    return model

