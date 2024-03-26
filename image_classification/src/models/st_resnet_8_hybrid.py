# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from typing import Tuple, Optional, List
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import larq as lq
from larq import utils
import numpy as np

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../common'))
from common_quantizers import STCustomDoReFa


def st_binary_cell(x: tf.Tensor, num_filters: int = None) -> tf.Tensor:
    """
        Implements a proprietary cell of layers mostly quantized in binary for weights and activations.

        Args:
            x (tf.Tensor): input tensor of the cell
            num_filters (int): number of channels of the input tensor 'x'. Will also be the cell output tensor number of channel

        Returns:
            A graph of layers with quantizer integrated, ready for quantization aware training.
    """

    kwargs_conv2d = dict(kernel_initializer='glorot_normal',
                         padding='same',
                         pad_values=1.0,
                         input_quantizer="ste_sign",
                         kernel_quantizer="ste_sign",
                         kernel_constraint="weight_clip",
                         use_bias=False)

    kwargs_depthwise = dict(kernel_initializer='glorot_normal',
                            padding='same',
                            pad_values=1.0,
                            input_quantizer="ste_sign",
                            depthwise_quantizer="ste_sign",
                            depthwise_constraint="weight_clip",
                            use_bias=False)

    kwargs_bn_before_binary = dict(momentum=0.9, center=True, scale=False)
    kwargs_bn_standard = dict(momentum=0.99, center=True, scale=True)

    x1 = x

    x = lq.layers.QuantDepthwiseConv2D(kernel_size=(3, 3), strides=(1, 1), **kwargs_depthwise)(x)
    x = layers.BatchNormalization(**kwargs_bn_before_binary)(x)

    x = layers.Concatenate(axis=-1)([x1, x])

    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(1, 1), strides=(1, 1), **kwargs_conv2d)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = layers.Add()([x, x1])

    return x


def st_resnet_8_hybrid(inputs: tf.Tensor, num_filters_global: List[int] = [32, 64, 128], num_classes: int = 10,
                       dropout: float = 0.2) -> tf.keras.Model:
    """
        Implements the st_reset_8_hybrid topology.

         Args:
            inputs (tf.Tensor): input tensor of the network
            num_filters_global (List[int]): number of channels for each of the network 3 sections
            num_classes (int): number of classes of the use-case
            dropout (float): dropout rate
        Returns:
            keras.Model: A keras model representing the st_reset_8_hybrid topology
    """

    kwargs_dense_8bits = dict(kernel_initializer='glorot_normal',
                              input_quantizer=STCustomDoReFa(k_bit=8, mode="activations"),
                              kernel_quantizer=STCustomDoReFa(k_bit=8, mode="weights"),
                              use_bias=False)

    kwargs_conv2d_8bits = dict(kernel_initializer='glorot_normal',
                               padding='same',
                               input_quantizer=STCustomDoReFa(k_bit=8, mode="activations"),
                               kernel_quantizer=STCustomDoReFa(k_bit=8, mode="weights"),
                               use_bias=False)

    kwargs_depthwise_8bits = dict(kernel_initializer='glorot_normal',
                                  padding='same',
                                  input_quantizer=STCustomDoReFa(k_bit=8, mode="activations"),
                                  depthwise_quantizer=STCustomDoReFa(k_bit=8, mode="weights"),
                                  use_bias=False)

    kwargs_bn_standard = dict(momentum=0.99, center=True, scale=True)

    num_filters = num_filters_global[0]

    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(3, 3), strides=(1, 1),
                              kernel_initializer='glorot_normal',
                              padding='same',
                              input_quantizer=lq.quantizers.DoReFa(k_bit=8, mode="activations"),
                              kernel_quantizer=STCustomDoReFa(k_bit=8, mode="weights"),
                              use_bias=False)(inputs)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)

    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = st_binary_cell(x, num_filters=num_filters)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = lq.layers.QuantDepthwiseConv2D(kernel_size=(3, 3), strides=(2, 2), depth_multiplier=1,
                                       **kwargs_depthwise_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(1, 1), strides=(1, 1), **kwargs_conv2d_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)

    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = st_binary_cell(x, num_filters=num_filters)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = lq.layers.QuantDepthwiseConv2D(kernel_size=(3, 3), strides=(1, 1), depth_multiplier=1,
                                       **kwargs_depthwise_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(1, 1), strides=(1, 1), **kwargs_conv2d_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)

    # Second stack
    num_filters = num_filters_global[1]
    x2 = x
    x = st_binary_cell(x, num_filters=num_filters_global[0])
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = lq.layers.QuantDepthwiseConv2D(kernel_size=(3, 3), strides=(2, 2), depth_multiplier=1,
                                       **kwargs_depthwise_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(1, 1), strides=(1, 1), **kwargs_conv2d_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)

    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = st_binary_cell(x, num_filters=num_filters)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = lq.layers.QuantDepthwiseConv2D(kernel_size=(3, 3), strides=(1, 1), depth_multiplier=1,
                                       **kwargs_depthwise_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(1, 1), strides=(1, 1), **kwargs_conv2d_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)

    y = lq.layers.QuantConv2D(filters=num_filters,
                              kernel_size=1,
                              strides=2,
                              **kwargs_conv2d_8bits)(x2)
    y = layers.BatchNormalization(**kwargs_bn_standard)(y)
    # # Overall residual, connect weight layer and identity paths
    y = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(y)
    x = tf.keras.layers.add([x, y])
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)

    # Third stack
    num_filters = num_filters_global[2]
    x2 = x
    x = st_binary_cell(x, num_filters=num_filters_global[1])
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = lq.layers.QuantDepthwiseConv2D(kernel_size=(3, 3), strides=(2, 2), depth_multiplier=1,
                                       **kwargs_depthwise_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(1, 1), strides=(1, 1), **kwargs_conv2d_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = st_binary_cell(x, num_filters)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = lq.layers.QuantDepthwiseConv2D(kernel_size=(3, 3), strides=(1, 1), depth_multiplier=1,
                                       **kwargs_depthwise_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = lq.layers.QuantConv2D(filters=num_filters, kernel_size=(1, 1), strides=(1, 1), **kwargs_conv2d_8bits)(x)
    x = layers.BatchNormalization(**kwargs_bn_standard)(x)
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)

    y = lq.layers.QuantConv2D(filters=num_filters,
                              kernel_size=1,
                              strides=2,
                              **kwargs_conv2d_8bits)(x2)
    y = layers.BatchNormalization(**kwargs_bn_standard)(y)
    # Overall residual, connect weight layer and identity paths
    y = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(y)
    x = tf.keras.layers.add([x, y])

    # Fourth stack.
    # While the paper uses four stacks, for cifar10 that leads to a large increase in complexity for minor benefits

    # Final classification layer.
    pool_size = int(np.amin(x.shape[1:3]))
    x = layers.Activation(STCustomDoReFa(k_bit=8, mode="activations"))(x)
    x = layers.AveragePooling2D(pool_size=pool_size)(x)
    y = layers.Flatten()(x)
    if dropout:
      y = layers.Dropout(dropout)(y)
    y = lq.layers.QuantDense(num_classes, **kwargs_dense_8bits)(y)
    y = layers.BatchNormalization(**kwargs_bn_standard)(y)
    outputs = layers.Activation('softmax')(y)

    # Instantiate model.
    model = keras.Model(inputs=inputs, outputs=outputs)
    return model


def get_st_resnet_8_hybrid_v1(input_shape: Tuple[int, int, int] = None, num_classes: int = None, dropout: Optional[float] = None) -> tf.keras.Model:
    """
    Creates a st_reset_8_hybrid_v1 classification model with the given number of classes and input shape.

    Args:
        num_classes (int): Number of classes in the classification task.
        input_shape (Tuple[int, int, int]): Shape of the input image.
        dropout (Optional[float]): Dropout rate to be applied to the model.

    Returns:
        keras.Model: Custom image classification model.
    """
    
    num_filters_global = [32, 96, 128]
    inputs = tf.keras.Input(shape=input_shape)
    model = st_resnet_8_hybrid(inputs=inputs, num_filters_global=num_filters_global, num_classes=num_classes, dropout=dropout)

    return model


def get_st_resnet_8_hybrid_v2(input_shape: Tuple[int, int, int] = None, num_classes: int = None, dropout: Optional[float] = None) -> tf.keras.Model:
    """
    Creates a st_reset_8_hybrid_v2 classification model with the given number of classes and input shape.

    Args:
        num_classes (int): Number of classes in the classification task.
        input_shape (Tuple[int, int, int]): Shape of the input image.
        dropout (Optional[float]): Dropout rate to be applied to the model.

    Returns:
        keras.Model: Custom image classification model.
    """

    num_filters_global = [32, 64, 128]
    inputs = tf.keras.Input(shape=input_shape)
    model = st_resnet_8_hybrid(inputs=inputs, num_filters_global=num_filters_global, num_classes=num_classes, dropout=dropout)

    return model
