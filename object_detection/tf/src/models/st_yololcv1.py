# /*---------------------------------------------------------------------------------------------
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


def get_st_yololcv1(input_shape, num_anchors, num_classes, **model_kwargs):
    """
    Builds a st_yololcv1 model architecture.

    Args:
    - inputs: a tensor representing the input to the model
    - num_anchors: an integer representing the number of anchors used in the model
    - num_classes: an integer representing the number of classes to be predicted by the model

    Returns:
    - a keras Model object representing the st_yololcv1 model architecture
    """
    len_anchor = 5 + num_classes
    len_detection_vector = len_anchor * num_anchors

    inputs = tf.keras.Input(shape=(input_shape))

    x = layers.Conv2D(16, (3, 3), strides=(2, 2), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(32, (3, 3), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(64, (3, 3), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(128, (3, 3), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.DepthwiseConv2D(kernel_size=(3, 3), strides=1, use_bias=False, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(256, (1, 1), strides=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.DepthwiseConv2D(kernel_size=(3, 3), strides=1, use_bias=False, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(256, (1, 1), strides=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(1, 1), padding='same')(x)

    x = layers.DepthwiseConv2D(kernel_size=(3, 3), strides=1, use_bias=False, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(128, (1, 1), strides=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.DepthwiseConv2D(kernel_size=(3, 3), strides=1, use_bias=False, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(256, (1, 1), strides=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(len_detection_vector, (1, 1), strides=1, padding='same', use_bias=False)(x)
    outputs = layers.BatchNormalization()(x)

    return keras.Model(inputs=inputs, outputs=outputs, name="st_yololcv1")
    