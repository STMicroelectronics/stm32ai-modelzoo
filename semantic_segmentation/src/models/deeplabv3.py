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
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models, backend


def aspp(x, out_filters, aspp_size):
    """
    Atrous Spatial Pyramid Pooling (ASPP) module for semantic segmentation.

    This module applies parallel atrous convolutions with different dilation rates,
    and a global average pooling to capture multi-scale context.

    Parameters:
    - x (tf.Tensor): The input tensor.
    - out_filters (int): The number of filters to use in the convolutions.
    - aspp_size (tuple): The target size for upsampling the image pooling features.

    Returns:
    - tf.Tensor: The output tensor after applying ASPP.

    Note:
    The number of filters in the `img_pool` Reshape layer must match the `out_filters` parameter.
    """

    # Start with a 1x1 convolution
    x1 = layers.Conv2D(out_filters, (1, 1), padding='same', kernel_initializer='he_normal')(x)
    x1 = layers.BatchNormalization()(x1)
    x1 = layers.Activation('relu')(x1)

    # Apply three 3x3 convolutions with different dilation rates for multi-scale feature extraction
    x2 = layers.Conv2D(out_filters, (3, 3), padding='same', dilation_rate=(6, 6), kernel_initializer='he_normal')(x)
    x2 = layers.BatchNormalization()(x2)
    x2 = layers.Activation('relu')(x2)

    x3 = layers.Conv2D(out_filters, (3, 3), padding='same', dilation_rate=(12, 12), kernel_initializer='he_normal')(x)
    x3 = layers.BatchNormalization()(x3)
    x3 = layers.Activation('relu')(x3)

    x4 = layers.Conv2D(out_filters, (3, 3), padding='same', dilation_rate=(18, 18), kernel_initializer='he_normal')(x)
    x4 = layers.BatchNormalization()(x4)
    x4 = layers.Activation('relu')(x4)

    # Apply global average pooling and upsample to match the feature map size
    img_pool = layers.GlobalAveragePooling2D()(x)
    img_pool = layers.Reshape((1, 1, 288))(img_pool)  
    img_pool = layers.Conv2D(out_filters, (1, 1), padding='same', kernel_initializer='he_normal')(img_pool)
    img_pool = layers.BatchNormalization()(img_pool)
    img_pool = layers.Activation('relu')(img_pool)
    img_pool = layers.UpSampling2D(size=aspp_size, interpolation='bilinear')(img_pool)

    # Concatenate the atrous and image pooling features
    x = layers.Concatenate()([x1, x2, x3, x4, img_pool])

    # Apply another 1x1 convolution and batch normalization to refine the features
    x = layers.Conv2D(out_filters, (1, 1), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    return x

def get_deeplab_v3(input_shape: list = None, backbone: str = None, version: str = None, alpha: float = None,
                   dropout: float = None, pretrained_weights: str = None, num_classes: int = None,
                   output_stride: int = 16) -> tf.keras.Model:
    """
    Constructs a DeepLabV3 model with a specified backbone.

    Parameters:
    - input_shape (list): The shape of the input data as a list, e.g., [224, 224, 3].
    - backbone (str): The backbone network to use, e.g., 'mobilenet'.
    - version (str): The version of the backbone, e.g., 'v2' for MobileNetV2.
    - alpha (float): The width multiplier for the MobileNetV2 (controls the width of the network).
    - dropout (float): The dropout rate to use after the ASPP (Atrous Spatial Pyramid Pooling) layer.
    - pretrained_weights (str): The path to the pre-trained weights file, or 'imagenet' for ImageNet weights.
    - num_classes (int): The number of classes for the output layer.
    - output_stride (int): The output stride for the network. Default is 16, but other values like 8 can be used for denser feature extraction.

    Returns:
    - tf.keras.Model: A Keras model instance of DeepLabV3 with the specified configuration.

    Note:
    This function assumes the existence of an `aspp` function and the necessary Keras imports.
    """

    # Define the input layer with the given input shape
    inputs = layers.Input(shape=input_shape)

    # Load the MobileNetV2 model with pre-trained weights on ImageNet
    # Set include_top to False to exclude the top classification layer
    if backbone == "mobilenet" and version == "v2":
        base_model = MobileNetV2(input_shape=input_shape, alpha=alpha, include_top=False, weights=pretrained_weights,
                                 input_tensor=inputs)
        # Extract the output from an intermediate layer to begin the ASPP
        x = base_model.get_layer('block_13_expand_relu').output

        # Set all layers in the base model to be trainable
        for layer in base_model.layers:
            layer.trainable = True

    # Get the shape of the current feature map for the ASPP pooling size
    _, h, w, _ = backend.int_shape(x)
    aspp_size = (h, w)

    # Apply ASPP with the given feature map size and a fixed number of filters (256)
    x = aspp(x, 256, aspp_size)

    # Apply dropout with the given rate
    x = layers.Dropout(dropout)(x)

    # Add a convolutional layer with `num_classes` filters for classification
    x = layers.Conv2D(num_classes, 1, strides=1, kernel_initializer='he_normal')(x)

    # Upsample the feature map to the original size of the input
    x = layers.UpSampling2D(size=(output_stride, output_stride), interpolation='bilinear')(x)

    # Create the model with inputs and outputs
    model = models.Model(inputs, x)

    return model