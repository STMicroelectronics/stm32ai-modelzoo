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
from tensorflow import keras
from tensorflow.keras import layers


def depthwise_conv_block(inputs, filters, alpha, depth_multiplier=1, strides=(1, 1), block_id=1):
    """    Adds a depthwise convolution block.
        A depthwise convolution block consists of a depthwise conv,
        batch normalization, relu6, pointwise convolution,
        batch normalization and relu6 activation.
    """

    pointwise_conv_filters = int(filters * alpha)

    if strides == (1, 1):
        x = inputs
    else:
        x = layers.ZeroPadding2D(((0, 1), (0, 1)))(inputs)
    x = layers.DepthwiseConv2D(kernel_size=(3, 3), padding="same" if strides == (1, 1) else "valid",
                               depth_multiplier=depth_multiplier, strides=strides, use_bias=False,
                               name="conv_dw_%d" % block_id, )(x)
    x = layers.BatchNormalization(name="conv_dw_%d_bn" % block_id)(x)
    x = layers.ReLU(6.0, name="conv_dw_%d_relu" % block_id)(x)

    x = layers.Conv2D(pointwise_conv_filters, kernel_size=(1, 1), padding="same", use_bias=False, strides=(1, 1),
                      name="conv_pw_%d" % block_id)(x)
    x = layers.BatchNormalization(name="conv_pw_%d_bn" % block_id)(x)
    x = layers.ReLU(6.0, name="conv_pw_%d_relu" % block_id)(x)

    return x


def get_scratch_model(cfg):
    alpha = cfg.model.model_type.alpha
    num_classes = len(cfg.dataset.class_names)
    input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
    inputs = keras.Input(shape=input_shape)

    first_block_filters = int(32 * alpha)
    x = layers.Conv2D(first_block_filters, kernel_size=3, strides=(2, 2), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU(6.)(x)

    x = depthwise_conv_block(x, filters=64, alpha=alpha, strides=(1, 1), block_id=1)

    x = depthwise_conv_block(x, filters=128, alpha=alpha, strides=(2, 2), block_id=2)
    x = depthwise_conv_block(x, filters=128, alpha=alpha, strides=(1, 1), block_id=3)

    x = depthwise_conv_block(x, filters=256, alpha=alpha, strides=(2, 2), block_id=4)
    x = depthwise_conv_block(x, filters=256, alpha=alpha, strides=(1, 1), block_id=5)

    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(2, 2), block_id=6)

    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=7)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=8)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=9)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=10)
    x = depthwise_conv_block(x, filters=512, alpha=alpha, strides=(1, 1), block_id=11)

    x = depthwise_conv_block(x, filters=1024, alpha=alpha, strides=(2, 2), block_id=12)
    x = depthwise_conv_block(x, filters=1024, alpha=alpha, strides=(1, 1), block_id=13)

    x = keras.layers.GlobalAveragePooling2D()(x)
    if cfg.model.dropout:
        x = keras.layers.Dropout(cfg.model.dropout)(x)
    if num_classes > 2:
        outputs = keras.layers.Dense(num_classes, activation="softmax")(x)
    else:
        outputs = keras.layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs=inputs, outputs=outputs, name="mobilenet_v1_alpha_{}".format(alpha))

    return model


def get_transfer_learning_model(cfg):
    random_model = get_scratch_model(cfg)
    if cfg.model.input_shape[0] in [224, 192, 160, 128]:
        input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
        backbone = tf.keras.applications.MobileNet(input_shape, input_tensor=random_model.inputs[0],
                                                   alpha=cfg.model.model_type.alpha, include_top=False,
                                                   weights='imagenet')
    else:
        backbone = tf.keras.applications.MobileNet(input_tensor=random_model.inputs[0],
                                                   alpha=cfg.model.model_type.alpha,
                                                   include_top=False, weights='imagenet')
    for i, layer in enumerate(backbone.layers):
        random_model.layers[i].set_weights(layer.get_weights())
        random_model.layers[i].trainable = False
    return random_model


def unfreeze_model(model):
    for layer in model.layers:
        layer.trainable = True

    return model
