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

SEED = 0
tf.random.set_seed(SEED)


def build_ign(cfg):
    # function to build the CNN model

    num_classes = len(cfg.dataset.class_names)
    input_shape = (
        cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])

    # Input block
    inputs = layers.Input(shape=input_shape)

    # First block
    x = layers.Conv2D(24, kernel_size=(16, 1), strides=(1, 1))(inputs)
    x = layers.Activation(activation='relu')(x)

    # max-pooling
    x = layers.MaxPooling2D(pool_size=(3, 1))(x)

    # flatten layer to apply fully connected block
    x = layers.Flatten()(x)

    # first fully connected layer
    x = layers.Dense(12)(x)
    if cfg.tf_train_parameters.dropout:
        x = layers.Dropout(cfg.tf_train_parameters.dropout)(x)

    # last fully connected layer
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    # outputs = layers.Activation( 'softmax' )( x )

    model = tf.keras.Model(inputs=inputs, outputs=[outputs], name="IGN_model")

    return model
