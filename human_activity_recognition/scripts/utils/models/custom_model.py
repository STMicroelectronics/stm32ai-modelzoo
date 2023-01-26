# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from tensorflow import keras
from tensorflow.keras import layers

# custom model example : replace the current layers with your own topology


def get_model(cfg):

    num_classes = len(cfg.dataset.class_names)
    input_shape = (
        cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
    inputs = keras.Input(shape=input_shape)

    # you can start defining your own model layers here
    # ---------------------------------------------------------------------------------------
    x = layers.Conv2D(16, (5, 1), strides=(
        1, 1), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(32, (5, 1), strides=(
        1, 1), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(64, (5, 1), strides=(
        1, 1), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    # ---------------------------------------------------------------------------------------

    x = keras.layers.GlobalAveragePooling2D()(x)
    if cfg.tf_train_parameters.dropout:
        x = keras.layers.Dropout(cfg.tf_train_parameters.dropout)(x)

    outputs = keras.layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="custom_model")
    return model
