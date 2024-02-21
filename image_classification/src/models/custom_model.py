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
                     dropout: Optional[float] = None) -> tf.keras.Model:
    """
    Creates a custom image classification model with the given number of classes and input shape.

    Args:
        num_classes (int): Number of classes in the classification task.
        input_shape (Tuple[int, int, int]): Shape of the input image.
        dropout (Optional[float]): Dropout rate to be applied to the model.

    Returns:
        keras.Model: Custom image classification model.
    """
    # Define the input layer
    inputs = tf.keras.Input(shape=input_shape)

    # Define the feature extraction layers
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

    # Define the classification layers
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    if dropout:
        x = tf.keras.layers.Dropout(dropout)(x)
    if num_classes > 2:
        outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    else:
        outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

    # Define and return the model
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="custom_model")
    return model
