# /*---------------------------------------------------------------------------------------------
#  * Copyright 2015 The TensorFlow Authors. 
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow.keras import layers
from typing import List, Tuple, Optional


def create_fd_mobilenet(input_shape: List[int] = [224, 224, 3], alpha: float = 1.0, depth_multiplier: int = 1,
                        dropout: float = None, input_tensor: Optional[tf.Tensor] = None,
                        classes: int = 101) -> tf.keras.Model:
    """
    Creates a MobileNet-based model for fine-grained classification.

    Args:
        input_shape (List[int]): The shape of the input tensor. Defaults to [224, 224, 3].
        alpha (float): The width multiplier for the MobileNet architecture. Must be one of 0.25, 0.50, 0.75, or 1.0.
            Defaults to 1.0.
        depth_multiplier (int): The depth multiplier for the MobileNet architecture. Defaults to 1.
        dropout (float): The dropout rate. Defaults to 1e-3.
        input_tensor (Optional[tf.Tensor]): Optional input tensor for the model. Defaults to None.
        classes (int): The number of classes for the classification task. Defaults to 101.

    Returns:
        model (tf.keras.Model): A Keras model for fine-grained classification.

    Raises:
        ValueError: If input_shape is less than 32 for either dimension or is not a multiple of 32 in both dimensions.
        ValueError: If alpha is not one of 0.25, 0.50, 0.75, or 1.0.
    """

    # Check input_shape
    if input_shape[0] < 32 or input_shape[1] < 32:
        raise ValueError('input_shape should be >= 32 for both dimensions')
    if (input_shape[0] % 32 > 0) or (input_shape[1] % 32 > 0):
        raise ValueError('input_shape should be multiple of 32 in both dimensions')

    # Check alpha
    if alpha not in [0.25, 0.50, 0.75, 1.0]:
        raise ValueError('alpha can be one of 0.25, 0.50, 0.75 or 1.0 only.')

    # Define input tensor
    img_input = input_tensor

    # Build MobileNet architecture
    x = _conv_block(img_input, 32, alpha, strides=(2, 2))
    x = depthwise_conv_block(x, 64, alpha, depth_multiplier, strides=(2, 2), block_id=1)
    x = depthwise_conv_block(x, 128, alpha, depth_multiplier, strides=(2, 2), block_id=2)
    x = depthwise_conv_block(x, 128, alpha, depth_multiplier, block_id=3)
    x = depthwise_conv_block(x, 256, alpha, depth_multiplier, strides=(2, 2), block_id=4)
    x = depthwise_conv_block(x, 256, alpha, depth_multiplier, block_id=5)
    x = depthwise_conv_block(x, 512, alpha, depth_multiplier, strides=(2, 2), block_id=6)
    x = depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=7)
    x = depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=8)
    x = depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=9)
    x = depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=10)
    x = depthwise_conv_block(x, 1024, alpha, depth_multiplier, block_id=11)

    # Add classification layers
    shape = (1, 1, int(1024 * alpha))
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Reshape(shape, name='reshape_1')(x)
    if dropout:
        x = layers.Dropout(dropout, name='dropout')(x)
    x = layers.Conv2D(classes, (1, 1), padding='same', name='conv_preds')(x)
    x = layers.Activation('softmax', name='act_softmax')(x)
    x = layers.Reshape((classes,), name='reshape_2')(x)

    # Create and return model
    model = tf.keras.Model(img_input, x, name='fd_mobilenet_%0.2f' % alpha)
    return model


def _conv_block(inputs: tf.Tensor, filters: int, alpha: float, kernel: Tuple[int, int] = (3, 3),
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


def get_fdmobilenet(input_shape: Tuple[int, int, int] = None, num_classes: int = None, alpha: float = None,
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

    # Create model using create_fd_mobilenet function
    model = create_fd_mobilenet(input_shape=input_shape, alpha=alpha, depth_multiplier=1, dropout=dropout,
                                input_tensor=inputs, classes=num_classes)
    return model
