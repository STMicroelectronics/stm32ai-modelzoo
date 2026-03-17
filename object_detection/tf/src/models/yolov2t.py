# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import sys
import numpy as np
import tensorflow as tf
from pathlib import Path#change
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Lambda


def _DarknetConv2D_BN_Leaky(filters: int, x: layers.Input) -> layers.Input:
    """
    Darknet Convolution2D followed by CustomBatchNormalization and LeakyReLU.
    
    Args:
    - filters: An integer representing the number of filters in the convolution layer.
    - x: A tensor representing the input to the layer.
    
    Returns:
    - A tensor representing the output of the layer.
    """
    x = layers.Conv2D(filters, (3, 3), strides=(1,1), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('leaky_relu')(x)
    return x


def get_yolov2t(input_shape, num_anchors: int, num_classes: int, **model_kwargs) -> keras.Model:
    """
    Builds a Tiny YOLOv2 model architecture using the _DarknetConv2D_BN_Leaky layer.

    Args:
    - inputs: a tensor representing the input to the model
    - num_anchors: an integer representing the number of anchors used in the model
    - num_classes: an integer representing the number of classes to be predicted by the model

    Returns:
    - a keras Model object representing the Tiny YOLOv2 model architecture
    
    """
    len_anchor = 5 + num_classes
    len_detection_vector = len_anchor * num_anchors

    inputs = tf.keras.Input(shape=(input_shape))
    
    x = _DarknetConv2D_BN_Leaky(16, inputs)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = _DarknetConv2D_BN_Leaky(32,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = _DarknetConv2D_BN_Leaky(64,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = _DarknetConv2D_BN_Leaky(128,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = _DarknetConv2D_BN_Leaky(256,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = _DarknetConv2D_BN_Leaky(512,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(1, 1), padding='same')(x)

    x = _DarknetConv2D_BN_Leaky(1024,x)

    x = _DarknetConv2D_BN_Leaky(512,x)

    x = layers.Conv2D(len_detection_vector, (1, 1), strides=1, padding='same', use_bias=False)(x)
        
    outputs = layers.BatchNormalization(name='predict_conv')(x)

    return Model(inputs=inputs, outputs=outputs, name="yolov2t")
