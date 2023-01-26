# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from tensorflow import keras
from tensorflow.keras import layers


def fire_module(x, squeeze, expand, fire_id):
    """
        Fire module for the SqueezeNet model.
        Implements  expand layer, which has a mix of 1x1 and 3x3 filters,
        by using two conv layers concatenated in the channel dimension.
        Returns a callable function

    """

    x = layers.Convolution2D(squeeze, (1, 1), activation='relu', name=fire_id + '_squeeze')(x)
    x = layers.BatchNormalization(name=fire_id + '_squeeze_bn')(x)

    left = layers.Convolution2D(expand, (1, 1), padding='same', activation='relu', name=fire_id + 'expand_1x1')(
        x)
    right = layers.Convolution2D(expand, (3, 3), padding='same', activation='relu', name=fire_id + '_expand_3x3')(
        x)
    x = layers.concatenate([left, right], axis=3, name=fire_id + '_expand_merge')

    return x


def get_scratch_model(cfg):
    input_shape = (
        cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
    classes = len(cfg.dataset.class_names)
    input_image = keras.Input(shape=input_shape)

    x = layers.Convolution2D(96, (7, 7), strides=(2, 2), name='conv1')(input_image)
    x = layers.Activation('relu', name='relu_conv1')(x)
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool1')(x)

    x = fire_module(x, squeeze=16, expand=64, fire_id='fire2')
    x = fire_module(x, squeeze=16, expand=64, fire_id='fire3')
    x = fire_module(x, squeeze=32, expand=128, fire_id='fire4')
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool4')(x)

    x = fire_module(x, squeeze=32, expand=128, fire_id='fire5')
    x = fire_module(x, squeeze=48, expand=192, fire_id='fire6')
    x = fire_module(x, squeeze=48, expand=192, fire_id='fire7')
    x = layers.MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='pool8')(x)

    x = fire_module(x, squeeze=64, expand=256, fire_id='fire9')

    x = layers.Dropout(cfg.model.dropout, name='dropout')(x)

    x = layers.Convolution2D(classes, (1, 1), name='conv10')(x)
    x = layers.Activation('relu', name='relu_conv10')(x)
    x = layers.BatchNormalization(name='bn')(x)

    x = layers.GlobalAveragePooling2D(name='average_pool10')(x)

    output = layers.Activation('softmax', name='softmax')(x)

    model = keras.Model(input_image, output, name="SqueezeNet_v1.0")
    return model
