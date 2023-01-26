# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow.keras import layers


def get_scratch_model(cfg):

    """" stmnist model for mnist type datasets """
    input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
    inputs = tf.keras.Input(shape=input_shape)
    num_filters = 16

    # block 1
    x = layers.Conv2D(num_filters,kernel_size=3,strides=2,padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    x = layers.DepthwiseConv2D(kernel_size=3,strides=1,padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    # block 2
    num_filters = 2*num_filters
    x = layers.Conv2D(num_filters,kernel_size=3,strides=1,padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    x = layers.DepthwiseConv2D(kernel_size=3,strides=2,padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    # block 3
    num_filters = 2*num_filters
    x = layers.Conv2D(num_filters,kernel_size=1,strides=1)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(len(cfg.dataset.class_names), activation="softmax")(x)

    model = tf.keras.models.Model(inputs, x, name="stmnist")
    return model