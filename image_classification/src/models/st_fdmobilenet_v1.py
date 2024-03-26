# /*---------------------------------------------------------------------------------------------
#  * Copyright 2015 The TensorFlow Authors. 
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from typing import Tuple, Optional
import tensorflow as tf
from tensorflow.keras import layers


def conv_block(inputs: tf.Tensor, filters: int, alpha: float, kernel: Tuple[int, int] = (3, 3),
                strides: Tuple[int, int] = (1, 1)) -> tf.Tensor:
    """
    Adds a convolutional block to the model.

    Args:
        inputs (tf.Tensor): The input tensor.
        filters (int): The number of filters in the convolutional layer.
        alpha (float): The width multiplier for the MobileNet architecture.
        kernel (Tuple[int, int]): The size of the convolutional kernel. Defaults to (3, 3).
        strides (Tuple[int, int]): The stride of the convolution. Defaults to (1, 1).

    Returns:
        tf.Tensor: The output tensor after applying a convolutional block.
    """

    # Calculate number of filters
    filters = int(filters * alpha)

    # Apply convolutional block
    x = layers.Conv2D(filters, kernel, padding='same', use_bias=False, strides=strides, name='conv1')(inputs)
    x = layers.BatchNormalization(name='conv1_bn')(x)
    return layers.Activation('relu', name='conv1_relu')(x)


def depthwise_conv_block(inputs: tf.Tensor, pointwise_conv_filters: int, alpha: float, depth_multiplier: int = 1,
                         strides: Tuple[int, int] = (1, 1), block_id: int = 1) -> tf.Tensor:
    """
    Adds a depthwise convolutional block to the model.

    Args:
        inputs (tf.Tensor): The input tensor.
        pointwise_conv_filters (int): The number of filters in the pointwise convolutional layer.
        alpha (float): The width multiplier for the MobileNet architecture.
        depth_multiplier (int): The depth multiplier for the depthwise convolutional layer. Defaults to 1.
        strides (Tuple[int, int]): The stride of the convolution. Defaults to (1, 1).
        block_id (int): The ID of the block.

    Returns:
        tf.Tensor: The output tensor after applying a depthwise convolutional block.
    """

    # Calculate number of filters
    pointwise_conv_filters = int(pointwise_conv_filters * alpha)

    # Apply depthwise convolutional block
    x = layers.DepthwiseConv2D((3, 3), padding='same', depth_multiplier=depth_multiplier, strides=strides,
                               use_bias=True,
                               name='conv_dw_%d' % block_id)(inputs)
    x = layers.Conv2D(pointwise_conv_filters, (1, 1), padding='same', use_bias=False, strides=(1, 1),
                      name='conv_pw_%d' % block_id)(x)
    x = layers.BatchNormalization(name='conv_pw_%d_bn' % block_id)(x)
    return layers.Activation('relu', name='conv_pw_%d_relu' % block_id)(x)

                        
def create_st_fdmobilenet_v1(input_shape: list[int] = [224, 224, 3], alpha: list[float] = [1.0],
                                    depth_multiplier: int = 1, dropout: float = 1e-3,
                                    input_tensor: Optional[tf.Tensor] = None, classes: int = 101) -> tf.keras.Model:

    img_input = input_tensor

    x = conv_block(img_input, 32, alpha[0], strides=(2, 2))
    x = depthwise_conv_block(x, 64, alpha[1], depth_multiplier, strides=(2, 2), block_id=1)

    x = depthwise_conv_block(x, 128, alpha[2], depth_multiplier, strides=(2, 2), block_id=2)
    x = depthwise_conv_block(x, 128, alpha[3], depth_multiplier, block_id=3)

    x = depthwise_conv_block(x, 256, alpha[4], depth_multiplier, strides=(2, 2), block_id=4)
    x = depthwise_conv_block(x, 256, alpha[5], depth_multiplier, block_id=5)

    x = depthwise_conv_block(x, 512, alpha[6], depth_multiplier, strides=(2, 2), block_id=6)

    # block of 4
    x = depthwise_conv_block(x, 512, alpha[7], depth_multiplier, block_id=7)
    x = depthwise_conv_block(x, 512, alpha[8], depth_multiplier, block_id=8)
    x = depthwise_conv_block(x, 512, alpha[9], depth_multiplier, block_id=9)
    x = depthwise_conv_block(x, 512, alpha[10], depth_multiplier, block_id=10)

    x = depthwise_conv_block(x, 1024, alpha[11], depth_multiplier, block_id=11)

    shape = (1, 1, int(1024 * alpha[11]))
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Reshape(shape, name='reshape_1')(x)
    x = layers.Dropout(dropout, name='dropout')(x)
    x = layers.Conv2D(classes, (1, 1), padding='same', name='conv_preds')(x)
    x = layers.Activation('softmax', name='act_softmax')(x)
    x = layers.Reshape((classes,), name='reshape_2')(x)

    model = tf.keras.Model(img_input, x, name='st_fdmobilenet_v1')

    return model


def get_st_fdmobilenet_v1(input_shape: Tuple[int, int, int] = None, num_classes: int = None,
                          dropout: float = None) -> tf.keras.Model:
    """
    Creates a Keras model for fine-grained classification from scratch.

    Args:
        input_shape (Tuple[int, int, int]): The shape of the input tensor.
        num_classes (int): The number of classes for the classification task.
        alpha (float): The width multiplier for the MobileNet architecture.
        dropout (float): The dropout rate.

    Returns:
        tf.keras.Model: A Keras model for fine-grained classification.
    """

    inputs = tf.keras.Input(shape=input_shape)
    alpha_list = [0.5, 0.75, 0.625, 0.5, 0.375, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25]

    # Create model
    model = create_st_fdmobilenet_v1(input_shape=input_shape, alpha=alpha_list, depth_multiplier=1,
                                     dropout=dropout, input_tensor=inputs, classes=num_classes)
    return model