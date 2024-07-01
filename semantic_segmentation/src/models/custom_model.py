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
    Creates a custom segmentation model

    Args:
        num_classes (int): Number of classes in the segmentation task.
        input_shape (Tuple[int, int, int]): Shape of the input image.
        dropout (Optional[float]): Dropout rate to be applied to the model.

    Returns:
        keras.Model: Custom segmentation model.
    """
    # Define the input layer
    inputs = tf.keras.Input(shape=input_shape)

    # Define the feature extraction layers, plays the role of a backbone. This is only given as example.
    x = layers.Conv2D(16, (3, 3), strides=(2, 2), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(32, (3, 3), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(64, (3, 3), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(256, (3, 3), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    # insert a couple of layers playing the role of an Head. This is only given as example.
    x = layers.Conv2D(256, 1, strides=(1, 1), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    # to finish, add the segmentation layers
    x = layers.Dropout(rate=dropout)(x)
    # Add a segmentation layer with the number of classes
    x = layers.Conv2D(num_classes, 1, strides=1, kernel_initializer='he_normal')(x)
    # Up sample the features to the original size of the input, stride of feature extractor being 16 in this example.
    x = layers.UpSampling2D(size=(16, 16), interpolation='nearest')(x)

    # Construct the final model
    model = tf.keras.Model(inputs=inputs, outputs=x, name="custom_model")
    return model
