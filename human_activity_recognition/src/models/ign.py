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


def get_ign(input_shape: tuple[int] = (24, 3, 1),
            num_classes: int = 4,
            dropout: float = 0.5):
    """
    Builds and returns an ign model for human_activity_recognition.
    Args:
        input_shape (tuple): A dictionary containing the configuration for the model.
        num_classes (int): number of nodes in the output layer
        dropout (float): dropout ratio to be used for dropout layer
    Returns:
        - keras.Model object, the ign model.
    """
    # function to build the CNN model

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
    if dropout:
        x = layers.Dropout(dropout)(x)

    # last fully connected layer
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    # outputs = layers.Activation( 'softmax' )( x )

    model = tf.keras.Model(inputs=inputs, outputs=[outputs], name="ign")

    return model
