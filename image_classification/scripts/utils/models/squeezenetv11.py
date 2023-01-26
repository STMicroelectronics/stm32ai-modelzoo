# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2016 Refikcanmalli
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from tensorflow import keras
from tensorflow.keras import layers
from keras import backend as k

sq1x1 = "squeeze1x1"
exp1x1 = "expand1x1"
exp3x3 = "expand3x3"
relu = "relu_"


def fire_module(x, fire_id, squeeze=16, expand=64):
    """
        Fire module for the SqueezeNet model.
        Implements expand layer, which has a mix of 1x1 and 3x3 filters,
        by using two conv layers concatenated in the channel dimension.
        Returns a callable function
    """
    s_id = 'fire' + str(fire_id) + '/'

    if k.image_data_format() == 'channels_first':
        channel_axis = 1
    else:
        channel_axis = 3

    x = layers.Convolution2D(
        squeeze, (1, 1), padding='valid', name=s_id + sq1x1)(x)
    x = layers.Activation('relu', name=s_id + relu + sq1x1)(x)

    left = layers.Convolution2D(
        expand, (1, 1), padding='valid', name=s_id + exp1x1)(x)
    left = layers.Activation('relu', name=s_id + relu + exp1x1)(left)

    right = layers.Convolution2D(
        expand, (3, 3), padding='same', name=s_id + exp3x3)(x)
    right = layers.Activation('relu', name=s_id + relu + exp3x3)(right)

    x = layers.concatenate(
        [left, right], axis=channel_axis, name=s_id + 'concat')
    return x


def get_scratch_model(cfg):
    input_shape = (
        cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
    classes = len(cfg.dataset.class_names)
    input_image = layers.Input(input_shape)

    x = layers.Convolution2D(64, (3, 3), strides=(
        2, 2), padding='valid', name='conv1')(input_image)
    x = layers.Activation('relu', name='relu_conv1')(x)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool1')(x)

    x = fire_module(x, fire_id=2, squeeze=16, expand=64)
    x = fire_module(x, fire_id=3, squeeze=16, expand=64)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool3')(x)

    x = fire_module(x, fire_id=4, squeeze=32, expand=128)
    x = fire_module(x, fire_id=5, squeeze=32, expand=128)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool5')(x)

    x = fire_module(x, fire_id=6, squeeze=48, expand=192)
    x = fire_module(x, fire_id=7, squeeze=48, expand=192)
    x = fire_module(x, fire_id=8, squeeze=64, expand=256)
    x = fire_module(x, fire_id=9, squeeze=64, expand=256)
    x = layers.Dropout(cfg.model.dropout, name='drop9')(x)

    x = layers.Convolution2D(
        classes, (1, 1), padding='valid', name='conv10')(x)
    x = layers.Activation('relu', name='relu_conv10')(x)
    x = layers.GlobalAveragePooling2D()(x)
    output = layers.Activation('softmax', name='loss')(x)

    model = keras.Model(input_image, output, name='SqueezeNet_v1.1')
    return model
