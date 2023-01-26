# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import tensorflow as tf
import tensorflow.keras.layers as layers


def build_gmp(cfg):
    # function to build the CNN model

    num_classes = len(cfg.dataset.class_names)
    input_shape = (
        cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])

    # Input block
    inputs = layers.Input(shape=input_shape)

    # First block
    x = layers.BatchNormalization()(inputs)
    x = layers.Conv2D(16, kernel_size=(5, 1), strides=(1, 1),
                      kernel_initializer='glorot_uniform')(x)

    # Second block
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(16, kernel_size=(5, 1), strides=(1, 1),
                      kernel_initializer='glorot_uniform')(x)

    # maxpooling
    x = layers.GlobalMaxPooling2D()(x)

    # front
    if cfg.tf_train_parameters.dropout:
        x = layers.Dropout(cfg.tf_train_parameters.dropout)(x)
    x = layers.Dense(num_classes)(x)
    outputs = layers.Activation('softmax')(x)

    model = tf.keras.Model(inputs=inputs, outputs=[outputs], name="GMP_model")

    return model
