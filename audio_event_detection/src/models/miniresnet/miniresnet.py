# /*---------------------------------------------------------------------------------------------
#  * Copyright 2015 The TensorFlow Authors.
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
import warnings
import tensorflow as tf
from pathlib import Path
from keras import layers
from keras import regularizers
from keras.applications import resnet

from model_utils import add_head

'''NOTE : Most of this implementation is adapted from the Tensorflow implementation of ResNets.'''

def block1_custom(x, filters, kernel_size=3, stride=1, conv_shortcut=True, name=None):
  """A residual block.
  Args:
    x: input tensor.
    filters: integer, filters of the bottleneck layer.
    kernel_size: default 3, kernel size of the bottleneck layer.
    stride: default 1, stride of the first layer.
    conv_shortcut: default True, use convolution shortcut if True,
        otherwise identity shortcut.
    name: string, block label.
  Returns:
    Output tensor for the residual block.
  """
  bn_axis = 3 

  if conv_shortcut:
    shortcut = layers.Conv2D(
        filters, 1, strides=stride, name=name + '_0_conv')(x)
    shortcut = layers.BatchNormalization(
        axis=bn_axis, epsilon=1.001e-5, name=name + '_0_bn')(shortcut)
  else:
    shortcut = x

  x = layers.Conv2D(filters, 1, strides=stride, name=name + '_1_conv')(x)
  x = layers.BatchNormalization(
      axis=bn_axis, epsilon=1.001e-5, name=name + '_1_bn')(x)
  x = layers.Activation('relu', name=name + '_1_relu')(x)

  x = layers.Conv2D(
      filters, kernel_size, padding='SAME', name=name + '_2_conv')(x)
  x = layers.BatchNormalization(
      axis=bn_axis, epsilon=1.001e-5, name=name + '_2_bn')(x)
  x = layers.Activation('relu', name=name + '_2_relu')(x)

  x = layers.Add(name=name + '_add')([shortcut, x])
  x = layers.Activation('relu', name=name + '_out')(x)
  return x

def MiniResNet(n_stacks: int = 1,
               weights: str = None,
               input_shape: tuple = None,
               pooling: str = 'avg'):
    """
    Instantiates a miniature ResNet architecture model.
    Adapted from tf.keras implementation source.

    Inputs
    ------
    n_stacks : int, number of residual block stacks to include in the model.
    weights : str, path to pretrained weight files. If None, initialize with random weights.
    input_shape : tuple, input shape of the model.
    pooling : str, one of "avg", "max" or None. The type of pooling applied 
        to the output features of the model.
    
    Outputs
    -------
    resnet : tf.keras.Model : the appropriate MiniResNet model, without a classification head.
    """

    def custom_stack(x, filters, blocks, stride1=2, name=None):
        x = block1_custom(x, filters, stride=stride1, conv_shortcut=True, name=name + '_block1')
        for i in range(2, blocks+1):
            x = block1_custom(x, filters, conv_shortcut=False, name=name + '_block' + str(i))
        return x

    def stack_fn(x):
        for i in range(n_stacks):
            x = custom_stack(x, 64 * 2**(i), 2, name='conv{}'.format(2+i))
        return x

    return resnet.ResNet(
        stack_fn,
        False,
        True,
        'resnet_mini',
        include_top=False,
        weights=weights,
        input_tensor=None,
        input_shape=input_shape,
        pooling=pooling,
        classes=None,
        classifier_activation=None)

def _check_parameters(n_stacks: int = None,
                      pooling : str = None,
                      pretrained_weights: bool = None
                      ):
    if pooling is None or pooling == "None":
        warnings.warn(message="Warning : pooling is set to None \
                        instead of 'avg' or 'max'. Ignore this warning if this is deliberate.")
    if pretrained_weights: 
        assert int(n_stacks) in [1, 2, 3], "n_stacks parameter must be one of (1, 2, 3)\n" \
        ", current value is {}".format(n_stacks)


def get_scratch_model(input_shape: tuple = None,
                      n_stacks: int = None,
                      n_classes: int = None,
                      pooling: str = 'avg',
                      use_garbage_class: bool = False,
                      multi_label: bool = False,
                      dropout: float = 0.,
                      kernel_regularizer=None,
                      activity_regularizer=None):
    '''
    Creates a MiniResNet model from scratch, i.e. with randomly initialized weights.
    Inputs
    ------
    input_shape : tuple, input shape of the model. Should be in format (n_mels, patch_length)
        and not (n_mels, patch_length, 1)
    n_stacks : int, number of residual block stacks to include in the model.
    n_classes : int, number of neurons of the classification head
    pooling : str, one of "avg", "max" or None. The type of pooling applied 
    to the output features of the model.
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
    miniresnet : tf.keras.Model, MiniResNet model with the appropriate classification head.
    '''
    
    input_shape=(input_shape[0], input_shape[1], 1)
    if use_garbage_class:
        n_classes += 1

    if multi_label:
        activation = 'sigmoïd'
    else:
        activation = 'softmax'

    backbone = MiniResNet(n_stacks=n_stacks,
                          input_shape=input_shape,
                          weights=None,
                          pooling=pooling)
    
    add_flatten = pooling == None or pooling == "None"
    miniresnet = add_head(backbone=backbone,
                          n_classes=n_classes,
                          trainable_backbone=True,
                          add_flatten=add_flatten,
                          functional=True,
                          activation=activation,
                          dropout=dropout,
                          kernel_regularizer=kernel_regularizer,
                          activity_regularizer=activity_regularizer)
    return miniresnet

def get_pretrained_model(n_stacks: int = None,
                         n_classes: int = None,
                         pooling: str = None,
                         use_garbage_class: bool = False,
                         multi_label: bool = False,
                         dropout: float = 0.,
                         fine_tune: bool = False,
                         kernel_regularizer=None,
                         activity_regularizer=None):
    
    '''
    Creates a MiniResNet model from ST provided pretrained weights
    Inputs
    ------
    n_stacks : int, number of residual block stacks to include in the model.
    n_classes : int, number of neurons of the classification head. 
        Must be either 1, 2 or 3.
    pooling : str or None, if str must be "avg". Type of pooling applied to the pretrained backbone
    use_garbage_class : bool, if True an additional neuron is added to the classification head
        to accomodate for the "garbage" class.
    dropout : float, dropout probability applied to the classification head.
    fine_tune : bool, if True all the weights in the model are trainable. 
        If False, only the classification head is trainable
    multi_label : bool, set to True if output is multi-label. If True, activation function is a sigmoïd,
        if False it is a softmax instead.
    kernel_regularizer : tf.keras.Regularizer, kernel regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.
    activity_regularizer : tf.keras.Regularizer, activity regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.

    Outputs
    -------
    miniresnet : tf.keras.Model, MiniResNet model with the appropriate classification head.
    '''
    # Load model
    if pooling == "avg":
        miniresnet = tf.keras.models.load_model(Path(Path(__file__).parent.resolve(),
        'pooled_miniresnet_{}_stacks_backbone.h5'.format(n_stacks)))
        add_flatten = False
    elif pooling == None:
        miniresnet = tf.keras.models.load_model(Path(Path(__file__).parent.resolve(),
        'miniresnet_{}_stacks_backbone.h5'.format(n_stacks)))
        add_flatten = True
    else:
        raise NotImplementedError("When using a pretrained backbone for miniresnet, 'pooling' must be either None or 'avg'")

    
    # Add head
    if use_garbage_class:
        n_classes += 1
    if multi_label:
        activation = 'sigmoïd'
    else:
        activation ='softmax'

    miniresnet = add_head(backbone=miniresnet,
                          n_classes=n_classes,
                          trainable_backbone=fine_tune,
                          add_flatten=add_flatten,
                          functional=True,
                          activation=activation,
                          dropout=dropout,
                          kernel_regularizer=kernel_regularizer,
                          activity_regularizer=activity_regularizer)

    return miniresnet

def get_model(input_shape: tuple = None,
              n_stacks: int = None,
              n_classes: int = None,
              pooling: str = 'avg',
              use_garbage_class: bool = False,
              multi_label: bool = False,
              dropout: float = 0.,
              pretrained_weights: bool = None,
              fine_tune: bool = False,
              kernel_regularizer=None,
              activity_regularizer=None):
    '''
    Instantiate a MiniResNet model, and perform basic sanity check on input parameters.
    Inputs
    ------
    input_shape : tuple, input shape of the model. Should be in format (n_mels, patch_length)
        and not (n_mels, patch_length, 1). Only used if pretrained_weights is False.
    n_stacks : int, number of residual block stacks to include in the model.
            Must be either 1, 2 or 3.
    n_classes : int, number of neurons of the classification head. 
    pooling : str, one of "avg", "max" or None. The type of pooling applied 
    to the output features of the model.
    use_garbage_class : bool, if True an additional neuron is added to the classification head
        to accomodate for the "garbage" class.
    dropout : float, dropout probability applied to the classification head.
    pretrained_weights : bool, use ST-provided pretrained weights is True, and 
        create model from scratch if False.
    fine_tune : bool, if True all the weights in the model are trainable. 
        If False, only the classification head is trainable
    multi_label : bool, set to True if output is multi-label. If True, activation function is a sigmoïd,
        if False it is a softmax instead.
    kernel_regularizer : tf.keras.Regularizer, kernel regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.
    activity_regularizer : tf.keras.Regularizer, activity regularizer applied to the classification head.
        NOTE : Currently not parametrable by the user.
    '''

    _check_parameters(n_stacks=n_stacks,
                      pooling=pooling,
                      pretrained_weights=pretrained_weights)
    
    # Failsafe convert pooling None string to None type
    # This should happen earlier but just in case
    if pooling == "None":
        pooling = None
    
    if not pretrained_weights:
        miniresnet = get_scratch_model(input_shape=input_shape,
                                       n_stacks=n_stacks,
                                       n_classes=n_classes,
                                       pooling=pooling,
                                       use_garbage_class=use_garbage_class,
                                       multi_label=multi_label,
                                       dropout=dropout,
                                       kernel_regularizer=kernel_regularizer,
                                       activity_regularizer=activity_regularizer)
    else:
        miniresnet = get_pretrained_model(n_stacks=n_stacks,
                                          n_classes=n_classes,
                                          pooling=pooling,
                                          use_garbage_class=use_garbage_class,
                                          multi_label=multi_label,
                                          dropout=dropout,
                                          fine_tune=fine_tune,
                                          kernel_regularizer=kernel_regularizer,
                                          activity_regularizer=activity_regularizer)
        
    return miniresnet