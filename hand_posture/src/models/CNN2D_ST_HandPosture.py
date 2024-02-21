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
from tensorflow.keras import layers, models


def get_ST_CNN2D_model(num_classes: int = None, input_shape: Tuple[int, int, int] = None,
                     dropout: Optional[float] = 0) -> tf.keras.Model:

    input_shape = (input_shape[0], input_shape[1], input_shape[2])
    inputs = tf.keras.Input(shape=input_shape)

    # ---------------------------------------------------------------------------------------
    x = layers.Conv2D(8, (3, 3))(inputs)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2))(x)
    x = layers.Dropout(dropout)(x)

    x = layers.Flatten()(x)

    x = layers.Dense(32, activation='relu')(x)

    if num_classes > 2:
        outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)
    else:
        outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="CNN2D_ST_HandPosture")
    # ---------------------------------------------------------------------------------------

    return model
