# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from typing import Tuple, Optional
import tensorflow as tf
from tensorflow.keras import layers


def get_custom_model(num_classes: int = None, input_shape: Tuple[int, int, int] = None,
                     dropout: Optional[float] = 0) -> tf.keras.Model:
    """
    Creates a custom ToF classification model with the given number of classes and input shape.

    Args:
        num_classes (int): Number of classes in the classification task.
        input_shape (Tuple[int, int, int]): Shape of the input image.
        dropout (Optional[float]): Dropout rate to be applied to the model.

    Returns:
        keras.Model: Custom image classification model.
    """
    # Define the input layer
    input_shape = (input_shape[0], input_shape[1], input_shape[2])
    inputs = tf.keras.Input(shape=input_shape)

    # ---------------------------------------------------------------------------------------

    # Define the feature extraction layers
    x = layers.Conv2D(16, (3, 3), strides=(1, 1), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv2D(32, (3, 3), strides=(1, 1), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Dropout(dropout)(x)

    x = layers.Flatten()(x)

    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dense(32, activation='relu')(x)

    if num_classes > 2:
        outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    else:
        outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="CNN2D_ST_HandPosture")
    # ---------------------------------------------------------------------------------------

    return model

