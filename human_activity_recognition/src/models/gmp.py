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


def get_gmp(input_shape: tuple[int] = (24, 3, 1),
            num_classes: int = 4,
            dropout: float = 0.5):
    """
    Builds and returns an gmp model for human_activity_recognition.
    Args:
        input_shape (tuple): A dictionary containing the configuration for the model.
        num_classes (int): number of nodes in the output layer
        dropout (float): dropout ratio to be used for dropout layer
    Returns:
        - keras.Model object, the gmp model.
    """
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
    if dropout:
        x = layers.Dropout(dropout)(x)
    x = layers.Dense(num_classes)(x)
    outputs = layers.Activation('softmax')(x)

    model = tf.keras.Model(inputs=inputs, outputs=[outputs], name="GMP_model")

    return model
