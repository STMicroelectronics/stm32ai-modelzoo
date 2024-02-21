# /*---------------------------------------------------------------------------------------------
#  * Copyright 2015 The TensorFlow Authors.
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from typing import Tuple


def depthwise_conv_block(inputs, filters, alpha, depth_multiplier=1, strides=(1, 1), block_id=1):
    """Adds a depthwise convolution block.

    This function defines a depthwise convolution block for use in a mobile
    architecture. The block consists of a depthwise convolution, followed by
    a pointwise convolution, with batch normalization and ReLU6 activations.

    Args:
        inputs (tensor): Input tensor.
        filters (int): Number of filters for the pointwise convolution.
        alpha (float): Width multiplier for the number of filters.
        depth_multiplier (int, optional): Depth multiplier for the depthwise convolution.
        strides (tuple, optional): Strides for the depthwise convolution.
        block_id (int, optional): Block identifier.

    Returns:
        tensor: Output tensor.

    """
    # Calculate the number of filters for the pointwise convolution.
    pointwise_conv_filters = int(filters * alpha)

    if strides == (1, 1):
        x = inputs
    else:
        # If the strides are not (1, 1), pad the input tensor to maintain the same output size.
        x = layers.ZeroPadding2D(((0, 1), (0, 1)))(inputs)
    # Perform the depthwise convolution.
    x = layers.DepthwiseConv2D(kernel_size=(3, 3), padding="same" if strides == (1, 1) else "valid",
                               depth_multiplier=depth_multiplier, strides=strides, use_bias=False,
                               name="conv_dw_%d" % block_id, )(x)
    x = layers.BatchNormalization(name="conv_dw_%d_bn" % block_id)(x)
    x = layers.ReLU(6.0, name="conv_dw_%d_relu" % block_id)(x)

    # Perform the pointwise convolution.
    x = layers.Conv2D(pointwise_conv_filters, kernel_size=(1, 1), padding="same", use_bias=False, strides=(1, 1),
                      name="conv_pw_%d" % block_id)(x)
    x = layers.BatchNormalization(name="conv_pw_%d_bn" % block_id)(x)
    x = layers.ReLU(6.0, name="conv_pw_%d_relu" % block_id)(x)

    return x


def get_scratch_model(input_shape: tuple = None, alpha: float = None, num_classes: int = None, 
                      dropout: float = None) -> tf.keras.Model:
    """Get a MobileNet V1 model from scratch.

    This function defines a MobileNet V1 model from scratch using depthwise
    convolution blocks.

    Args:
        input_shape (tuple): Shape of the input tensor.
        num_classes (int): Number of output classes.
        alpha (float): Width multiplier for the number of filters.
        dropout (float, optional): Dropout rate.

    Returns:
        model: MobileNet V1 model.

    """
    # Define the input tensor.
    inputs = keras.Input(shape=input_shape)

    # First convolution block.
    first_block_filters = int(32 * alpha)
    x = layers.Conv2D(first_block_filters, kernel_size=3, strides=(2, 2), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU(6.)(x)

    # Depthwise convolution blocks.
    x = depthwise_conv_block(x, filters=64, alpha=alpha, strides=(1, 1), block_id=1)

    x = depthwise_conv_block(x, filters=128, alpha=alpha, strides=(2, 2), block_id=2)
    x = depthwise_conv_block(x, filters=128, alpha=alpha, strides=(1, 1), block_id=3)

    x = depthwise_conv_block(x, filters=256, alpha=alpha, strides=(2, 2), block_id=4)
    x = depthwise_conv_block(x, filters=256, alpha=alpha, strides=(1, 1), block_id=5)

    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(2, 2), block_id=6)

    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=7)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=8)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=9)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=10)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=11)

    x = depthwise_conv_block(x, filters=1024, alpha=alpha, strides=(2, 2), block_id=12)
    x = depthwise_conv_block(x, filters=1024, alpha=alpha, strides=(1, 1), block_id=13)

    # Global average pooling and output layer.
    x = keras.layers.GlobalAveragePooling2D()(x)
    if dropout:
        x = keras.layers.Dropout(dropout)(x)
    if num_classes > 2:
        outputs = keras.layers.Dense(num_classes, activation="softmax")(x)
    else:
        outputs = keras.layers.Dense(1, activation="sigmoid")(x)

    # Define the model.
    model = keras.Model(inputs=inputs, outputs=outputs, name="mobilenet_v1_alpha_{}".format(alpha))

    return model


def get_transfer_learning_model(input_shape: Tuple[int, int, int] = None, alpha: float = None,
                                num_classes: int = None, dropout: float = None,
                                weights: str = None) -> tf.keras.Model:
    """
    Creates a transfer learning model using the MobileNet architecture.

    Args:
        input_shape: A tuple representing the input shape of the model.
        dropout: A float representing the dropout rate of the model.
        alpha: A float representing the width multiplier of the MobileNet architecture.
        num_classes (int): Number of output classes. Default is None.
        weights (str, optional): The pre-trained weights to use. Either "imagenet" or None. Defaults to None.
    Returns:
        A Keras model object with the MobileNet architecture as the backbone and a randomly initialized head.
    """
    # Create a randomly initialized model
    random_model = get_scratch_model(input_shape=input_shape, num_classes=num_classes, alpha=alpha, dropout=dropout)

    # Check if input shape is valid for MobileNet architecture
    if input_shape[0] in [224, 192, 160, 128]:
        input_shape = (input_shape[0], input_shape[1], input_shape[2])
        # Use MobileNet architecture with specified input shape
        backbone = tf.keras.applications.MobileNet(input_shape, input_tensor=random_model.inputs[0],
                                                   alpha=alpha, weights=weights, include_top=False)
    else:
        # Use default MobileNet architecture
        backbone = tf.keras.applications.MobileNet(input_tensor=random_model.inputs[0],
                                                   alpha=alpha, weights=weights, include_top=False)

    # Copy weights from MobileNet backbone to randomly initialized model
    for i, layer in enumerate(backbone.layers):
        random_model.layers[i].set_weights(layer.get_weights())

    # Return the transfer learning model
    return random_model


def get_mobilenetv1(input_shape: tuple, alpha: float = None, 
                     num_classes: int = None, dropout: float = None,
                     pretrained_weights: str = "imagenet") -> tf.keras.Model:
    """
    Returns a MobileNetV1 model with a custom classifier.

    Args:
        input_shape (tuple): The shape of the input tensor.
        alpha (float, optional): The width multiplier for the MobileNetV1 backbone. Defaults to None.
        dropout (float, optional): The dropout rate for the MobileNetV1 backbone. Defaults to None.
        num_classes (int, optional): The number of output classes. Defaults to None.
        weights (str, optional): The pre-trained weights to use. Either "imagenet" or None.
                                 Defaults to "imagenet".

    Returns:
        tf.keras.Model: The MobileNetV1 model with a custom classifier.
    """
    
    if pretrained_weights:
        model = get_transfer_learning_model(input_shape=input_shape, alpha=alpha,
                                            num_classes=num_classes, dropout=dropout,
                                            weights=pretrained_weights)
    else:
        model = get_scratch_model(input_shape=input_shape, alpha=alpha,
                                  num_classes=num_classes, dropout=dropout)

    return model
