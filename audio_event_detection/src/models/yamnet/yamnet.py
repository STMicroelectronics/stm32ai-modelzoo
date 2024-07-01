# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
import tensorflow as tf
from pathlib import Path
from keras import layers
from keras import regularizers

from model_utils import add_head


def _check_parameters(embedding_size: int,
                      patch_length: int,
                      n_mels: int):
    '''Internal sanity check for Yamnet parameters.
       Checks embedding size, and input shape.'''
    
    assert int(embedding_size) in [256, 512, 1024], \
    "embedding_size parameter must be one of 256, 512, 1024 \n" \
    ", current value is {}".format(embedding_size)

    assert int(patch_length) == 96, \
    "patch_length parameter must be 96 for Yamnet models \n" \
    ", current value is {}".format(patch_length)

    assert int(n_mels) == 64, \
    "n_mels parameter must be 64 for Yamnet models \n" \
    ", current value is {}".format(n_mels)

def get_transfer_learning_model(n_classes: int = None,
                                embedding_size: int = None,
                                fine_tune: bool = False,
                                use_garbage_class: bool = False,
                                dropout: float = 0.,
                                multi_label: bool = False,
                                kernel_regularizer = None,
                                activity_regularizer = None):
    '''
    Loads a Yamnet backbone, adds a classification head, and returns a Yamnet model.
    Inputs
    ------
    n_classes : int, number of neurons of the classification head
    embedding_size : int. Must be either 256, 512 or 1024. Size of the Yamnet output embeddings
        which are fed to the classification head.
    fine_tune : bool, if True all the weights in the model are trainable. 
        If False, only the classification head is trainable
    use_garbage_class : bool, if True an additional neuron is added to the classification head
        to accomodate for the "garbage" class.
    dropout : float, dropout probability applied to the classification head.
    multi_label : bool, set to True if output is multi-label. If True, activation function is a sigmoïd,
        if False it is a softmax instead.
    kernel_regularizer : tf.keras.Regularizer, kernel regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.
    activity_regularizer : tf.keras.Regularizer, activity regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.

    Outputs
    -------
    yamnet : tf.keras.Model, Yamnet model with the appropriate classification head.
    '''
    # Load appropriate backbone
    yamnet_backbone = tf.keras.models.load_model(Path(Path(__file__).parent.resolve(),
                        'yamnet_{}_f32.h5'.format(str(embedding_size))))
    
    # Add a permutation layer to rotate the input patches
    # This is because the backbone expects (96, 64, 1) input
    # But the model zoo outputs patches in the (n_mels, n_frames) format
    # Which here is (64, 96, 1)
    inp = layers.Input(shape=(64, 96, 1))
    x = layers.Permute((2, 1, 3))(inp)
    out = yamnet_backbone(x)
    permuted_backbone = tf.keras.models.Model(inputs=inp, outputs=out)

    # Add classification head
    if use_garbage_class:
        n_classes += 1
        
    if multi_label:
        activation = 'sigmoïd'
    else:
        activation ='softmax'

    yamnet = add_head(backbone=permuted_backbone,
                      n_classes=n_classes,
                      trainable_backbone=fine_tune,
                      add_flatten=False,
                      functional=True,
                      activation=activation,
                      kernel_regularizer=kernel_regularizer,
                      activity_regularizer=activity_regularizer,
                      dropout=dropout)
                         
    return yamnet

def get_model(n_classes: int = None,
              embedding_size: int = None,
              fine_tune: bool = False,
              use_garbage_class: bool = False,
              dropout: float = 0.,
              multi_label: bool = False,
              kernel_regularizer = None,
              activity_regularizer = None,
              patch_length: int = None,
              n_mels : int = None,
              pretrained_weights : bool = None):
    ''' Loads a Yamnet model and performs basic sanity checks on input parameters.
    Inputs
    ------
    n_classes : int, number of neurons of the classification head
    embedding_size : int. Must be either 256, 512 or 1024. Size of the Yamnet output embeddings
        which are fed to the classification head.
    fine_tune : bool, if True all the weights in the model are trainable. 
        If False, only the classification head is trainable
    use_garbage_class : bool, if True an additional neuron is added to the classification head
        to accomodate for the "garbage" class.
    dropout : float, dropout probability applied to the classification head.
    multi_label : bool, set to True if output is multi-label. If True, activation function is a sigmoïd,
        if False it is a softmax instead.
    kernel_regularizer : tf.keras.Regularizer, kernel regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.
    activity_regularizer : tf.keras.Regularizer, activity regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.
    patch_length : int, length of input patches. Only used for sanity check.
    n_mels : int, n° of mels in input patches. Only used for sanity check.
    pretrained_weights : bool, must be True. Raises an appropriate error if False.

    Outputs
    -------
    yamnet : tf.keras.Model, Yamnet model with the appropriate classification head.
    '''

    _check_parameters(embedding_size, patch_length, n_mels)

    if pretrained_weights:
        yamnet = get_transfer_learning_model(n_classes=n_classes,
                                             embedding_size=embedding_size,
                                             fine_tune=fine_tune,
                                             use_garbage_class=use_garbage_class,
                                             dropout=dropout,
                                             multi_label=multi_label,
                                             kernel_regularizer=kernel_regularizer,
                                             activity_regularizer=activity_regularizer
                                             )
    else:
        raise RuntimeError("Yamnet is only available with pretrained weights. \n \
                           Please set the pretrained_weights arguments to True in \
                           the configuration file.")

    return yamnet