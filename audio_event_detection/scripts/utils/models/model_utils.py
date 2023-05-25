# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from tensorflow import keras
import tensorflow as tf


def add_head(n_classes, backbone, add_flatten=True, trainable_backbone=True, activation=None,
             kernel_regularizer=None, bias_regularizer=None, activity_regularizer=None, functional=True,
             dropout=0):

    if functional:
        if not trainable_backbone:
            for layer in backbone.layers:   
                layer.trainable = False
        x = backbone.output
        if add_flatten:
            x = tf.keras.layers.Flatten()(x)
        if dropout:
            x = tf.keras.layers.Dropout(dropout)(x)
        if activation is None:
            out = tf.keras.layers.Dense(units=n_classes,
                        kernel_regularizer=kernel_regularizer,
                        bias_regularizer=bias_regularizer,
                        activity_regularizer=activity_regularizer, name='new_head')(x)
        else:
            out = tf.keras.layers.Dense(units=n_classes, activation=activation,
                            kernel_regularizer=kernel_regularizer,
                            bias_regularizer=bias_regularizer,
                            activity_regularizer=activity_regularizer, name='new_head')(x)
        func_model = tf.keras.models.Model(inputs=backbone.input, outputs=out)
        return func_model
        
    else:

        if not trainable_backbone:
            for layer in backbone.layers:   
                layer.trainable = False
        seq_model = tf.keras.models.Sequential()
        seq_model.add(backbone)
        if add_flatten:
            seq_model.add(tf.keras.layers.Flatten())
        if dropout:
            seq_model.add(tf.keras.layers.Dropout(dropout))
        if activation is None:
            seq_model.add(tf.keras.layers.Dense(units=n_classes,
                        kernel_regularizer=kernel_regularizer,
                        bias_regularizer=bias_regularizer,
                        activity_regularizer=activity_regularizer))
        else:
            seq_model.add(tf.keras.layers.Dense(units=n_classes, activation=activation,
                            kernel_regularizer=kernel_regularizer,
                            bias_regularizer=bias_regularizer,
                            activity_regularizer=activity_regularizer))

        return seq_model