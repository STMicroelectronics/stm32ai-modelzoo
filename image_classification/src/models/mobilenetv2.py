# /*---------------------------------------------------------------------------------------------
#  * Copyright 2018 The TensorFlow Authors.
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow import keras
from keras.applications import imagenet_utils
from tensorflow.keras import layers


def make_divisible(v, divisor, min_value=None):
    """Round the number of filters to be divisible by a given divisor.

    This function is used to ensure that the number of filters on the last 1x1
    convolution of a mobile architecture is divisible by 8.

    Args:
        v (int): Number of filters.
        divisor (int): Divisor to ensure the number of filters is divisible by.
        min_value (int, optional): Minimum value for the number of filters.

    Returns:
        int: Number of filters rounded to be divisible by the given divisor.

    """
    # If no minimum value is specified, use the divisor as the minimum value.
    if min_value is None:
        min_value = divisor
    # Round the number of filters to be divisible by the divisor.
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    # Make sure that rounding down does not go down by more than 10%.
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v


def inverted_res_block(inputs, expansion, stride, alpha, filters, block_id):
    """Inverted ResNet block.

    This function defines an inverted residual block for use in a mobile
    architecture. The block consists of a depthwise convolution, followed by
    a pointwise convolution, with optional expansion and skip connections.

    Args:
        inputs (tensor): Input tensor.
        expansion (int): Expansion factor for the pointwise 1x1 convolution.
        stride (int): Stride for the depthwise 3x3 convolution.
        alpha (float): Width multiplier for the number of filters.
        filters (int): Number of filters for the pointwise 1x1 convolution.
        block_id (str): Block identifier.

    Returns:
        tensor: Output tensor.

    """
    # Get the shape of the input tensor.
    shape = inputs.get_shape().as_list()
    # Get the number of channels in the input tensor.
    in_channels = shape[-1]
    # Calculate the number of filters for the pointwise 1x1 convolution.
    pointwise_conv_filters = int(filters * alpha)
    # Ensure the number of filters on the last 1x1 convolution is divisible by 8.
    pointwise_filters = make_divisible(pointwise_conv_filters, 8)
    # Set the input tensor as the starting point.
    x = inputs

    # If the block identifier is not None, perform the expansion step.
    if block_id:
        # Expand with a pointwise 1x1 convolution.
        x = layers.Conv2D(expansion * in_channels, kernel_size=1, padding='same', use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.ReLU(6.)(x)

    # Depthwise 3x3 convolution.
    if stride == 2:
        # If the stride is 2, pad the input tensor to maintain the same output size.
        x = layers.ZeroPadding2D(padding=imagenet_utils.correct_pad(x, 3))(x)
    # Perform the depthwise 3x3 convolution.
    x = layers.DepthwiseConv2D(kernel_size=3, strides=stride, use_bias=False,
                               padding='same' if stride == 1 else 'valid')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU(6.)(x)

    # Project with a pointwise 1x1 convolution.
    x = layers.Conv2D(pointwise_filters, kernel_size=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)

    # If the number of channels in the input tensor is the same as the number of filters
    # in the last 1x1 convolution and the stride is 1, add the input tensor to the output tensor.
    if in_channels == pointwise_filters and stride == 1:
        return layers.Add()([inputs, x])
    # Otherwise, return the output tensor.
    return x


def get_scratch_model(input_shape: tuple = None, alpha: float = None, num_classes: int = None, 
                      dropout: float = None) -> tf.keras.Model:
    """
    Returns a MobileNetV2-based Keras model from scratch.

    Args:
        input_shape (tuple): Shape of the input tensor. Default is None.
        num_classes (int): Number of output classes. Default is None.
        alpha (float): Width multiplier for MobileNetV2 architecture. Default is None.
        dropout (float): Dropout rate for the model. Default is None.

    Returns:
        tf.keras.Model: Keras model based on MobileNetV2 architecture.

    """

    # Define the input layer
    inputs = keras.Input(shape=input_shape)

    # Define the first block of the model
    first_block_filters = make_divisible(32 * alpha, 8)
    x = layers.Conv2D(first_block_filters, kernel_size=3, strides=(2, 2), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU(6.)(x)

    # Define the rest of the blocks in the model
    x = inverted_res_block(x, filters=16, alpha=alpha, stride=1, expansion=1, block_id=0)
    x = inverted_res_block(x, filters=24, alpha=alpha, stride=2, expansion=6, block_id=1)
    x = inverted_res_block(x, filters=24, alpha=alpha, stride=1, expansion=6, block_id=2)
    x = inverted_res_block(x, filters=32, alpha=alpha, stride=2, expansion=6, block_id=3)
    x = inverted_res_block(x, filters=32, alpha=alpha, stride=1, expansion=6, block_id=4)
    x = inverted_res_block(x, filters=32, alpha=alpha, stride=1, expansion=6, block_id=5)
    x = inverted_res_block(x, filters=64, alpha=alpha, stride=2, expansion=6, block_id=6)
    x = inverted_res_block(x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=7)
    x = inverted_res_block(x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=8)
    x = inverted_res_block(x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=9)
    x = inverted_res_block(x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=10)
    x = inverted_res_block(x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=11)
    x = inverted_res_block(x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=12)
    x = inverted_res_block(x, filters=160, alpha=alpha, stride=2, expansion=6, block_id=13)
    x = inverted_res_block(x, filters=160, alpha=alpha, stride=1, expansion=6, block_id=14)
    x = inverted_res_block(x, filters=160, alpha=alpha, stride=1, expansion=6, block_id=15)
    x = inverted_res_block(x, filters=320, alpha=alpha, stride=1, expansion=6, block_id=16)

    # Define the last block of the model
    if alpha > 1.0:
        last_block_filters = make_divisible(1280 * alpha, 8)
    else:
        last_block_filters = 1280
    x = layers.Conv2D(last_block_filters, kernel_size=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU(6.)(x)

    # Define the output layer of the model
    x = keras.layers.GlobalAveragePooling2D()(x)
    if dropout:
        x = layers.Dropout(rate=dropout, name="dropout")(x)
    if num_classes > 2:
        outputs = keras.layers.Dense(num_classes, activation="softmax")(x)
    else:
        outputs = keras.layers.Dense(1, activation="sigmoid")(x)

    # Create the Keras model
    model = keras.Model(inputs=inputs, outputs=outputs, name="mobilenet_v2_alpha_{}".format(alpha))

    return model


def get_transfer_learning_model(input_shape: tuple, alpha: float = None, num_classes: int = None,
                                dropout: float = None, weights: str = None) -> tf.keras.Model:
    """
    Returns a transfer learning model based on MobileNetV2 architecture pre-trained on ImageNet.

    Args:
        input_shape (tuple): Shape of the input tensor.
        alpha (float): Width multiplier for MobileNetV2 architecture. Default is None.
        dropout: A float representing the dropout rate of the model.
        num_classes (int): Number of output classes. Default is None.
        weights (str, optional): The pre-trained weights to use. Either "imagenet" or None. Defaults to None.

    Returns:
        tf.keras.Model: Transfer learning model based on MobileNetV2 architecture.

    Raises:
        ValueError: If input_shape is not one of [224, 192, 160, 128, 96].

    """
    # Get a random model with the specified input shape and number of classes
    random_model = get_scratch_model(input_shape=input_shape, num_classes=num_classes, alpha=alpha, dropout=dropout)

    # Check if input_shape is valid for MobileNetV2 architecture
    if input_shape[0] in [224, 192, 160, 128, 96]:
        input_shape = (input_shape[0], input_shape[1], input_shape[2])
        # Use MobileNetV2 architecture with pre-trained weights on ImageNet
        backbone = tf.keras.applications.MobileNetV2(input_shape, input_tensor=random_model.inputs[0],
                                                     alpha=alpha, weights=weights, include_top=False)
    else:
        backbone = tf.keras.applications.MobileNetV2(input_tensor=random_model.inputs[0],
                                                     alpha=alpha, weights=weights, include_top=False)

    # Transfer the weights from the pre-trained MobileNetV2 model to the random model
    for i, layer in enumerate(backbone.layers):
        random_model.layers[i].set_weights(layer.get_weights())

    return random_model


def get_mobilenetv2(input_shape: tuple, alpha: float = None, num_classes: int = None, 
                    dropout: float = None, pretrained_weights: str = "imagenet") -> tf.keras.Model:
    """
    Returns a MobileNetV2 model with a custom classifier.

    Args:
        input_shape (tuple): The shape of the input tensor.
        alpha (float, optional): The width multiplier for the MobileNetV2 backbone. Defaults to None.
        dropout (float, optional): The dropout rate for the custom classifier. Defaults to 1e-6.
        num_classes (int, optional): The number of output classes. Defaults to None.
        pretrained_weights (str, optional): The pre-trained weights to use. Either "imagenet"
        or None. Defaults to "imagenet".

    Returns:
        tf.keras.Model: The MobileNetV2 model with a custom classifier.
    """
    
    if pretrained_weights:
        model = get_transfer_learning_model(input_shape=input_shape, alpha=alpha, 
                                            num_classes=num_classes, dropout=dropout,
                                            weights=pretrained_weights)
    else:
        model = get_scratch_model(input_shape=input_shape, alpha=alpha, 
                                  num_classes=num_classes, dropout=dropout)

    return model

