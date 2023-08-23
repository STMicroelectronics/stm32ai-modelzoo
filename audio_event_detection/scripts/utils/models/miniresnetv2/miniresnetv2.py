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

def block2_custom(x, filters, kernel_size=3, stride=1, conv_shortcut=False, name=None):
    """A custom ResnetV2 block.
    Args:
        x: input tensor.
        filters: integer, filters of the bottleneck layer.
        kernel_size: default 3, kernel size of the bottleneck layer.
        stride: default 1, stride of the first layer.
        conv_shortcut: default False, use convolution shortcut if True,
        otherwise identity shortcut.
        name: string, block label.
    Returns:
    Output tensor for the residual block.
    """
    bn_axis =  3

    preact = layers.BatchNormalization(
        axis=bn_axis, epsilon=1.001e-5, name=name + '_preact_bn')(x)
    preact = layers.Activation('relu', name=name + '_preact_relu')(preact)
    if conv_shortcut:
        shortcut = layers.Conv2D(
        filters, 1, strides=stride, name=name + '_0_conv')(preact)
    else:
        shortcut = layers.MaxPooling2D(1, strides=stride)(x) if stride > 1 else x
    x = layers.Conv2D(
        filters, 1, strides=1, use_bias=False, name=name + '_1_conv')(preact)
    x = layers.BatchNormalization(
        axis=bn_axis, epsilon=1.001e-5, name=name + '_1_bn')(x)
    x = layers.Activation('relu', name=name + '_1_relu')(x)
    x = layers.ZeroPadding2D(padding=((1, 1), (1, 1)), name=name + '_2_pad')(x)
    x = layers.Conv2D(
        filters,
        kernel_size,
        strides=stride,
        name=name + '_2_conv')(x)
    x = layers.Add(name=name + '_out')([shortcut, x])
    return x

def MiniResNetV2(n_stacks=1,
    include_top=False,
    weights=None,
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=10,
    classifier_activation='softmax'):
    """Instantiates a miniature ResNetV2 architecture.
        Adapted from tf.keras implementation source
        """

    def custom_stack(x, filters, blocks, stride1=2, name=None):
        # TODO : actually customize
        x = block2_custom(x, filters, conv_shortcut=True, name=name + '_block1')
        for i in range(2, blocks):
            x = block2_custom(x, filters, name=name + '_block' + str(i))
        x = block2_custom(x, filters, stride=stride1, name=name + '_block' + str(blocks))
        return x

    def stack_fn(x):
        for i in range(n_stacks):
            x = custom_stack(x, 64 * 2**(i), 2, name='conv{}'.format(2+i))
        return x

    return resnet.ResNet(
        stack_fn,
        True,
        True,
        'resnet_miniv2',
        include_top,
        weights,
        input_tensor,
        input_shape,
        pooling,
        classes,
        classifier_activation=classifier_activation)


def get_scratch_model(cfg):
    # TODO : this
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

    backbone = MiniResNetV2(n_stacks=n_stacks,
                          input_shape=input_shape,
                          classes=n_classes,
                          pooling=pooling,
                          classifier_activation=None)

    miniresnetv2 = add_head(backbone=backbone,
                          n_classes=n_classes,
                          trainable_backbone=True,
                          add_flatten=False,
                          functional=True,
                          activation=activation,
                          dropout=cfg.model.dropout)
    return miniresnetv2

def get_pretrained_model(cfg):
    # Load model
    miniresnetv2 = tf.keras.models.load_model(Path(Path(__file__).parent.resolve(),
     'miniresnetv2_{}_stacks_backbone.h5'.format(cfg.model.model_type.n_stacks)))

    # Add head
    n_classes = len(cfg.dataset.class_names)
    if cfg.dataset.use_other_class:
        n_classes += 1
    if cfg.model.multi_label:
        activation = 'sigmoïd'
    else:
        activation ='softmax'

    miniresnetv2 = add_head(backbone=miniresnetv2,
                           n_classes=n_classes,
                           trainable_backbone=cfg.model.fine_tune,
                           add_flatten=False,
                           functional=True,
                           activation=activation,
                           dropout=cfg.model.dropout)

    return miniresnetv2