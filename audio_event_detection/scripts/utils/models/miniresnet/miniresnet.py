# /*---------------------------------------------------------------------------------------------
#  * Copyright 2015 The TensorFlow Authors.
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from pathlib import Path
from ..model_utils import add_head
from keras import layers
from keras.applications import resnet


'''Code shamelessly adapted from tensorflow's ResNet implementation'''

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

def MiniResNet(n_stacks=1,
    include_top=False,
    weights=None,
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=10,
    classifier_activation='softmax'):
    """Instantiates a miniature ResNet architecture.
        Adapted from tf.keras implementation source
        """

    def custom_stack(x, filters, blocks, stride1=2, name=None):
        # TODO : actually customize
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
        include_top,
        weights,
        input_tensor,
        input_shape,
        pooling,
        classes,
        classifier_activation=classifier_activation)





def get_scratch_model(cfg):
    input_shape=(cfg.model.input_shape[0], cfg.model.input_shape[1], 1)
    n_classes = len(cfg.dataset.class_names)
    if cfg.dataset.use_other_class:
        n_classes += 1
    n_stacks = cfg.model.model_type.n_stacks
    pooling=cfg.model.model_type.pooling
    if cfg.model.multi_label:
        activation = 'sigmoïd'
    else:
        activation = 'softmax'

    backbone = MiniResNet(n_stacks=n_stacks,
                          input_shape=input_shape,
                          classes=n_classes,
                          pooling=pooling,
                          classifier_activation=None)
    miniresnet = add_head(backbone=backbone,
                          n_classes=n_classes,
                          trainable_backbone=True,
                          add_flatten=False,
                          functional=True,
                          activation=activation,
                          dropout=cfg.model.dropout)
    return miniresnet

def get_pretrained_model(cfg):
    # Load model
    miniresnet = tf.keras.models.load_model(Path(Path(__file__).parent.resolve(),
     'miniresnet_{}_stacks_backbone.h5'.format(cfg.model.model_type.n_stacks)))

    # Add head
    n_classes = len(cfg.dataset.class_names)
    if cfg.dataset.use_other_class:
        n_classes += 1
    if cfg.model.multi_label:
        activation = 'sigmoïd'
    else:
        activation ='softmax'

    miniresnet = add_head(backbone=miniresnet,
                         n_classes=n_classes,
                         trainable_backbone=cfg.model.fine_tune,
                         add_flatten=False,
                         functional=True,
                         activation=activation,
                         dropout=cfg.model.dropout)

    return miniresnet