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
    '''
    Adds a classification head to a backbone. 
    This classification head consists of a dense layer and an activation function.
    
    Inputs
    ------
    n_classes : int, number of neurons in the classification head
    backbone : tf.keras.Model : Backbone upon which to add the classification head
    add_flatten : bool, if True add a Flatten layer between the backbone and the head
    trainable_backbone : bool, if True unfreeze all backbone weights.
        If False freeze all backbone weights
    activation : str, activation function of the classification head. Usually "softmax" or "sigmoid"
    kernel_regularizer : tf.keras.regularizers.Regularizer,
        kernel regularizer to add to the classification head.
    bias_regularizer : tf.keras.regularizers.Regularizer,
        bias regularizer to add to the classification head.
    activity_regularizer : tf.keras.regularizers.Regularizer,
        activity regularizer to add to the classification head.
    functional : bool, if True return a tf.keras functional (as opposed to Sequential) model.
        Recommended.
    dropout : float, if >0 adds dropout to the classification head with the specified rate.

    Outputs
    -------
    model : Model with the attached classification head
    
    '''
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