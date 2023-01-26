# /*---------------------------------------------------------------------------------------------
#  * Copyright 2018 The TensorFlow Authors. 
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow import keras
from keras.applications import imagenet_utils
from tensorflow.keras import layers


def make_divisible(v, divisor, min_value=None):
    if min_value is None:
        min_value = divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    # Make sure that round down does not go down by more than 10%.
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v


def inverted_res_block(inputs, expansion, stride, alpha, filters, block_id):
    """Inverted ResNet block."""

    shape = inputs.get_shape().as_list()
    in_channels = shape[-1]
    pointwise_conv_filters = int(filters * alpha)
    # Ensure the number of filters on the last 1x1 convolution is divisible by 8.
    pointwise_filters = make_divisible(pointwise_conv_filters, 8)
    x = inputs

    if block_id:
        # Expand with a pointwise 1x1 convolution.
        x = layers.Conv2D(expansion * in_channels, kernel_size=1, padding='same', use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.ReLU(6.)(x)

    # Depthwise 3x3 convolution.
    if stride == 2:
        x = layers.ZeroPadding2D(padding=imagenet_utils.correct_pad(x, 3))(x)
    x = layers.DepthwiseConv2D(kernel_size=3, strides=stride, use_bias=False,
                               padding='same' if stride == 1 else 'valid')(x)
    x = layers.BatchNormalization()(x)

    x = layers.ReLU(6.)(x)
    # Project with a pointwise 1x1 convolution.
    x = layers.Conv2D(pointwise_filters, kernel_size=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)

    if in_channels == pointwise_filters and stride == 1:
        return layers.Add()([inputs, x])
    return x


def get_scratch_model(cfg):
    alpha = cfg.model.model_type.alpha
    num_classes = len(cfg.dataset.class_names)
    input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
    inputs = keras.Input(shape=input_shape)

    first_block_filters = make_divisible(32 * alpha, 8)
    x = layers.Conv2D(first_block_filters, kernel_size=3, strides=(2, 2), padding='same', use_bias=False)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU(6.)(x)

    x = inverted_res_block(x, filters=16, alpha=alpha, stride=1, expansion=1, block_id=0)

    x = inverted_res_block(x, filters=24, alpha=alpha, stride=2, expansion=6, block_id=1)
    x = inverted_res_block(x, filters=24, alpha=alpha, stride=1, expansion=6, block_id=2)

    x = inverted_res_block(x, filters=32, alpha=alpha, stride=2, expansion=6, block_id=3)
    x = inverted_res_block(x, filters=32, alpha=alpha, stride=1, expansion=6, block_id=4)
    x = inverted_res_block(x, filters=32, alpha=alpha, stride=1, expansion=6, block_id=5)

    x = inverted_res_block(x, filters=64, alpha=alpha, stride=2, expansion=6, block_id=6)
    x = inverted_res_block(x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=7)
    x = inverted_res_block(x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=8)
    x = inverted_res_block(x, filters=64, alpha=alpha, stride=1, expansion=6, block_id=9)

    x = inverted_res_block(x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=10)
    x = inverted_res_block(x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=11)
    x = inverted_res_block(x, filters=96, alpha=alpha, stride=1, expansion=6, block_id=12)

    x = inverted_res_block(x, filters=160, alpha=alpha, stride=2, expansion=6, block_id=13)
    x = inverted_res_block(x, filters=160, alpha=alpha, stride=1, expansion=6, block_id=14)
    x = inverted_res_block(x, filters=160, alpha=alpha, stride=1, expansion=6, block_id=15)

    x = inverted_res_block(x, filters=320, alpha=alpha, stride=1, expansion=6, block_id=16)

    if alpha > 1.0:
        last_block_filters = make_divisible(1280 * alpha, 8)
    else:
        last_block_filters = 1280

    x = layers.Conv2D(last_block_filters, kernel_size=1, padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU(6.)(x)

    x = keras.layers.GlobalAveragePooling2D()(x)
    if cfg.model.dropout:
        x = keras.layers.Dropout(cfg.model.dropout)(x)
    if num_classes > 2:
        outputs = keras.layers.Dense(num_classes, activation="softmax")(x)
    else:
        outputs = keras.layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs=inputs, outputs=outputs, name="mobilenet_v2_alpha_{}".format(alpha))
    return model


def get_transfer_learning_model(cfg):
    random_model = get_scratch_model(cfg)
    if cfg.model.input_shape[0] in [224, 192, 160, 128, 96]:
        input_shape = (cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
        backbone = tf.keras.applications.MobileNetV2(input_shape, input_tensor=random_model.inputs[0],
                                                     alpha=cfg.model.model_type.alpha, include_top=False,
                                                     weights='imagenet')
    else:
        backbone = tf.keras.applications.MobileNetV2(input_tensor=random_model.inputs[0],
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
