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
from tensorflow.keras import layers


def create_fd_mobilenet(input_shape=[224, 224, 3], alpha=1.0, depth_multiplier=1, dropout=1e-3, input_tensor=None,
                        classes=101):
    if input_shape[0] < 32 or input_shape[1] < 32:
        raise ValueError('input_shape should be >= 32 for both dimensions')

    if (input_shape[0] % 32 > 0) or (input_shape[1] % 32 > 0):
        raise ValueError('input_shape should be multiple of 32 in both dimensions')

    if alpha not in [0.25, 0.50, 0.75, 1.0]:
        raise ValueError('alpha can be one of 0.25, 0.50, 0.75 or 1.0 only.')

    img_input = input_tensor
    x = _conv_block(img_input, 32, alpha, strides=(2, 2))
    x = _depthwise_conv_block(x, 64, alpha, depth_multiplier, strides=(2, 2), block_id=1)

    x = _depthwise_conv_block(x, 128, alpha, depth_multiplier, strides=(2, 2), block_id=2)
    x = _depthwise_conv_block(x, 128, alpha, depth_multiplier, block_id=3)

    x = _depthwise_conv_block(x, 256, alpha, depth_multiplier, strides=(2, 2), block_id=4)
    x = _depthwise_conv_block(x, 256, alpha, depth_multiplier, block_id=5)

    x = _depthwise_conv_block(x, 512, alpha, depth_multiplier, strides=(2, 2), block_id=6)

    # block of 4
    x = _depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=7)
    x = _depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=8)
    x = _depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=9)
    x = _depthwise_conv_block(x, 512, alpha, depth_multiplier, block_id=10)

    x = _depthwise_conv_block(x, 1024, alpha, depth_multiplier, block_id=11)

    shape = (1, 1, int(1024 * alpha))
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Reshape(shape, name='reshape_1')(x)
    x = layers.Dropout(dropout, name='dropout')(x)
    x = layers.Conv2D(classes, (1, 1), padding='same', name='conv_preds')(x)
    x = layers.Activation('softmax', name='act_softmax')(x)
    x = layers.Reshape((classes,), name='reshape_2')(x)

    model = tf.keras.Model(img_input, x, name='fd_mobilenet_%0.2f' % alpha)

    return model


def _conv_block(inputs, filters, alpha, kernel=(3, 3), strides=(1, 1)):
    filters = int(filters * alpha)
    x = layers.Conv2D(filters, kernel, padding='same', use_bias=False, strides=strides, name='conv1')(inputs)
    x = layers.BatchNormalization(name='conv1_bn')(x)

    return layers.Activation('relu', name='conv1_relu')(x)


def _depthwise_conv_block(inputs, pointwise_conv_filters, alpha, depth_multiplier=1, strides=(1, 1), block_id=1):
    pointwise_conv_filters = int(pointwise_conv_filters * alpha)
    x = layers.DepthwiseConv2D((3, 3), padding='same', depth_multiplier=depth_multiplier, strides=strides,
                               use_bias=True,
                               name='conv_dw_%d' % block_id)(inputs)

    x = layers.Conv2D(pointwise_conv_filters, (1, 1), padding='same', use_bias=False, strides=(1, 1),
                      name='conv_pw_%d' % block_id)(x)

    x = layers.BatchNormalization(name='conv_pw_%d_bn' % block_id)(x)

    return layers.Activation('relu', name='conv_pw_%d_relu' % block_id)(x)


def get_scratch_model(cfg):
    alpha = cfg.model.model_type.alpha
    num_classes = len(cfg.dataset.class_names)
    input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
    inputs = tf.keras.Input(shape=input_shape)
    dropout = cfg.model.dropout

    model = create_fd_mobilenet(input_shape=input_shape, alpha=alpha, depth_multiplier=1, dropout=dropout,
                                input_tensor=inputs, classes=num_classes)
    return model
