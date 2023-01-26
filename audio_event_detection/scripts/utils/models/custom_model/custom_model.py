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

def get_model(cfg):

    """" Custom model example : replace the current layers with your own topology """
    num_classes = len(cfg.dataset.class_names)
    input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1])
    if cfg.model.expand_last_dim:
        input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1], 1)
    inputs = tf.keras.Input(shape=input_shape)

    # Here you can define your own model feature extraction layers
    # ---------------------------------------------------------------------------------------
    x = layers.Conv2D(16, (3, 3), strides=(1, 1), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(32, (3, 3), strides=(1, 1), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(64, (3, 3), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    # ---------------------------------------------------------------------------------------

    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    if cfg.model.dropout:
        x = tf.keras.layers.Dropout(cfg.model.dropout)(x)
        
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="custom_model")
    return model