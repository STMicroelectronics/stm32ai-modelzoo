# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from keras.models import Model
from keras.regularizers import l2
from tensorflow import keras
from tensorflow.keras import layers
from typing import Tuple


def resnet_layer(inputs: layers.Input, num_filters: int = 16, kernel_size: int = 3, strides: int = 1,
                 activation: str = 'relu', batch_normalization: bool = True,
                 conv_first: bool = True) -> layers.Activation:
    """
    2D Convolution-Batch Normalization-Activation stack builder for ResNet models.

    Args:
        inputs: Input tensor from input image or previous layer.
        num_filters: Conv2D number of filters.
        kernel_size: Conv2D square kernel dimensions.
        strides: Conv2D square stride dimensions.
        activation: Activation name.
        batch_normalization: Whether to include batch normalization.
        conv_first: Conv-BN-Activation (True) or BN-Activation-Conv (False).

    Returns:
        A tensor as input to the next layer.
    """
    conv = layers.Conv2D(num_filters,
                         kernel_size=kernel_size,
                         strides=strides,
                         padding='same',
                         kernel_initializer='he_normal',
                         kernel_regularizer=l2(1e-4))

    x = inputs
    if conv_first:
        x = conv(x)
        if batch_normalization:
            x = layers.BatchNormalization()(x)
        if activation is not None:
            x = layers.Activation(activation)(x)
    else:
        if batch_normalization:
            x = layers.BatchNormalization()(x)
        if activation is not None:
            x = layers.Activation(activation)(x)
        x = conv(x)
    return x


def get_resnetv1(num_classes: int = None, input_shape: Tuple[int, int, int] = None,
                 depth: int = None, dropout: float = None) -> keras.Model:
    """
    ResNet Version 1 Model builder.

    Stacks of 2 x (3 x 3) Conv2D-BN-ReLU. Last ReLU is after the shortcut connection.
    At the beginning of each stage, the feature map size is halved (down-sampled)
    by a convolutional layer with strides=2, while the number of filters is doubled.
    Within each stage, the layers have the same number filters and the same number of filters.

    Args:
        num_classes: Number of classes in the dataset.
        input_shape: Shape of the input tensor.
        depth: Depth of the ResNet model.
        dropout: Dropout rate to be applied to the fully connected layer.

    Returns:
        A Keras model instance.
    """
    if (depth - 2) % 6 != 0:
        raise ValueError("Depth should be 6n+2.")

    # Start model definition.
    num_filters = 16
    num_res_blocks = int((depth - 2) / 6)

    inputs = keras.Input(shape=input_shape)
    x = resnet_layer(inputs=inputs)

    # Instantiate the stack of residual units
    for stack in range(3):
        for res_block in range(num_res_blocks):
            strides = 1
            if stack > 0 and res_block == 0:  # first layer but not first stack
                strides = 2  # down sample
            y = resnet_layer(inputs=x,
                             num_filters=num_filters,
                             strides=strides)
            y = resnet_layer(inputs=y,
                             num_filters=num_filters,
                             activation=None)
            if stack > 0 and res_block == 0:  # first layer but not first stack
                # linear projection residual shortcut connection to match changed dims
                x = resnet_layer(inputs=x,
                                 num_filters=num_filters,
                                 kernel_size=1,
                                 strides=strides,
                                 activation=None,
                                 batch_normalization=False)
            x = layers.add([x, y])
            x = layers.Activation('relu')(x)
        num_filters *= 2

    # Add classifier on top.
    # v1 does not use BN after last shortcut connection-ReLU
    x = layers.AveragePooling2D(pool_size=8)(x)
    x = layers.Flatten()(x)
    if dropout:
        x = layers.Dropout(dropout)(x)

    if num_classes > 2:
        outputs = keras.layers.Dense(num_classes, activation="softmax", kernel_initializer='he_normal')(x)
    else:
        outputs = layers.Dense(1, activation="sigmoid")(x)

    # Instantiate model.
    model = keras.Model(inputs=inputs, outputs=outputs, name=f"resnet_v1_depth_{depth}")
    return model
