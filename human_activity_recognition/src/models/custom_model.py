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


def get_custom_model(input_shape: tuple[int] = (24, 3, 1),
                    num_classes: int = 4,
                    dropout: float = None):

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
    if dropout:
        x = keras.layers.Dropout(dropout)(x)

    outputs = keras.layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="custom_model")
    return model
