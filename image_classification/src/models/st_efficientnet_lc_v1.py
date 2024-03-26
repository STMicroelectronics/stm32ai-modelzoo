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
from typing import List, Tuple
import math
from tensorflow.keras.models import Model

repeats = [1, 2, 2, 3, 3, 4, 1]


def round_expansion(expansion_factor: int, repeats: List[int]) -> List[int] :
    exp_ratio = []
    flag = 1
    for r in repeats:
        if (r != 0) and flag:
            exp_ratio.append(1)
            flag = 0
        else:
            exp_ratio.append(expansion_factor)

    return exp_ratio


def num_blocks(repeats: List[int]) -> List[int]:
    blocks = []
    for r in repeats:
        if (r != 0):
            blocks.append(1)
        else:
            blocks.append(0)
    return blocks


def round_filters(filters: int, width_coefficient: float, depth_divisor: int = 8, min_filters: int = None) -> int:
    """Round number of filters based on depth multiplier."""
    if not width_coefficient:
        return filters
    filters *= width_coefficient
    min_filters = min_filters or depth_divisor
    new_filters = max(int(filters + depth_divisor / 2) // depth_divisor * depth_divisor, min_filters)
    # Make sure that round down does not go down by more than 10%.
    if new_filters < 0.9 * filters:
        new_filters += depth_divisor
    return int(new_filters)


def round_repeats(repeats: List[int], depth_coefficient: float, depth_trunc: str) -> List[int]:
    """ Per-stage depth scaling
    Scales the block repeats in each stage. This depth scaling impl maintains
    compatibility with the EfficientNet scaling method, while allowing sensible
    scaling for other models that may have multiple block arg definitions in each stage.
    """

    # We scale the total repeat count for each stage, there may be multiple
    # block arg defs per stage so we need to sum.
    num_repeat = sum(repeats)
    if depth_trunc == 'round':
        # Truncating to int by rounding allows stages with few repeats to remain
        # proportionally smaller for longer. This is a good choice when stage definitions
        # include single repeat stages that we'd prefer to keep that way as long as possible
        num_repeat_scaled = round(num_repeat * depth_coefficient)
    else:
        # The default for EfficientNet truncates repeats to int via 'ceil'.
        # Any multiplier > 1.0 will result in an increased depth for every stage.
        num_repeat_scaled = int(math.ceil(num_repeat * depth_coefficient))
    # Proportionally distribute repeat count scaling to each block definition in the stage.
    # Allocation is done in reverse as it results in the first block being less likely to be scaled.
    # The first block makes less sense to repeat in most of the arch definitions.
    repeats_scaled = []
    for r in repeats[::-1]:
        if depth_trunc == 'round':
            rs = round((r / num_repeat * num_repeat_scaled))
        else:
            rs = max(1, round((r / num_repeat * num_repeat_scaled)))
        repeats_scaled.append(rs)
        num_repeat -= r
        num_repeat_scaled -= rs
    repeats_scaled = repeats_scaled[::-1]
    return repeats_scaled


def swish(x):
    return x * tf.nn.sigmoid(x)
    

def mb_conv_block(inputs: tf.Tensor, in_channels: int, out_channels: int, num_repeat: int, stride: int, expansion_factor: int, se_ratio: float, k: int, drop_rate: float, 
                  prev_block_num: int, activation) -> tf.Tensor:

    x = inputs
    input_filters = in_channels
	
    for i in range(num_repeat):
        # Expansion phase: making the layer wide wide as mentioned in Inverted residual block
        input_tensor = x
        if i == 0:
            # The first block needs to take care of stride and filter size increase.
            stride = stride
        else:
            stride = 1

        expanded_filters = input_filters * expansion_factor
        if expansion_factor != 1:
            x = layers.Conv2D(filters=expanded_filters, kernel_size=(1, 1), strides=1, padding='same')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Activation(activation)(x)

        x = layers.DepthwiseConv2D(kernel_size=(k, k), strides=stride, padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation(activation)(x)

        # Squeeze and excitation phase: extracting global features with global average pooling and squeeze numbers of channels using se_ratio
        squeezed_filters = max (1, int(input_filters * se_ratio))
        se_tensor = layers.GlobalAveragePooling2D()(x)
        se_tensor = layers.Reshape((1, 1, expanded_filters))(se_tensor)
        se_tensor = layers.Conv2D(filters=squeezed_filters , kernel_size=(1, 1), padding='same')(se_tensor)
        se_tensor = layers.Activation(activation, name='act_{}'.format(i+prev_block_num))(se_tensor)
        se_tensor = layers.Conv2D(filters=expanded_filters , kernel_size=(1, 1), padding='same')(se_tensor)
		
        # Clip to have better quant at input of sigmoid
        se_tensor = layers.Lambda(lambda x: tf.clip_by_value(x, clip_value_min=-4.0, clip_value_max=4.0))(se_tensor)
        se_tensor = layers.Activation('sigmoid', name='act2_{}'.format(i+prev_block_num))(se_tensor)
        x = layers.multiply([x, se_tensor])
        
        # Output phase:
        x = layers.Conv2D(filters=out_channels, kernel_size=(1, 1), strides=1, padding='same')(x)
        x = layers.BatchNormalization()(x)

        if stride == 1 and input_filters == out_channels:
            num_blocks_total = 16
            dropout_rate = drop_rate * float(prev_block_num + i) / num_blocks_total
            if dropout_rate and (dropout_rate > 0):
                x = layers.Dropout(dropout_rate, noise_shape=(None, 1, 1, 1))(x)
            x = layers.add([x, input_tensor])
            
        input_filters = out_channels

    return x


def EfficientNet(width_coefficient_list: float = 1.0,
                depth_coefficient: float = 1.0,
                input_resolution: int = 224,
                expansion_factor: int = 6,
                se_ratio: float = 0.25,
                input_channels: int = 3,
                dropout_rate: float = 0.2,
                drop_connect_rate: float = 0.2,
                depth_trunc: str = 'ceil',
                activation: str = 'relu',
                include_top=True,
                pooling: str = None,
                classes: int = 101) -> tf.keras.Model:

    # Determine proper input shape
    input = layers.Input(shape=(input_resolution, input_resolution, input_channels))

    # Activation
    if activation == 'swish':
        activation = swish()
    if activation == 'relu6':
        activation = tf.nn.relu6

    # Build stem
    x = layers.Conv2D(filters=round_filters(32, width_coefficient_list[0]), kernel_size=(3, 3), strides=(2, 2), padding='same')(input)
    x = layers.BatchNormalization()(x)
    x = layers.Activation(activation, name='stem_activation')(x)

    # Build blocks
    repeats_scaled = round_repeats(repeats, depth_coefficient, depth_trunc)
    exp_ratio = round_expansion(expansion_factor, repeats_scaled)
    
    block1 = mb_conv_block(inputs=x, in_channels=round_filters(32, width_coefficient_list[0]), out_channels=round_filters(16, width_coefficient_list[1]), 
                           num_repeat=repeats_scaled[0],stride=1, expansion_factor=exp_ratio[0], se_ratio=se_ratio, k=3, drop_rate=drop_connect_rate, 
                           prev_block_num=0, activation=activation)

    block2 = mb_conv_block(inputs=block1, in_channels=round_filters(16, width_coefficient_list[1]), out_channels=round_filters(24, width_coefficient_list[2]), 
                           num_repeat=repeats_scaled[1],stride=2, expansion_factor=exp_ratio[1], se_ratio=se_ratio, k=3, drop_rate=drop_connect_rate, 
                           prev_block_num=sum(repeats_scaled[0:1]), activation=activation)
    
    block3 = mb_conv_block(inputs=block2, in_channels=round_filters(24, width_coefficient_list[2]), out_channels=round_filters(40, width_coefficient_list[3]), 
                           num_repeat=repeats_scaled[2],stride=2, expansion_factor=exp_ratio[2], se_ratio=se_ratio, k=5, drop_rate=drop_connect_rate, 
                           prev_block_num=sum(repeats_scaled[0:2]), activation=activation)
    
    block4 = mb_conv_block(inputs=block3, in_channels=round_filters(40, width_coefficient_list[3]), out_channels=round_filters(80, width_coefficient_list[4]), 
                           num_repeat=repeats_scaled[3], stride=2, expansion_factor=exp_ratio[3], se_ratio=se_ratio, k=3, drop_rate=drop_connect_rate, 
                           prev_block_num=sum(repeats_scaled[0:3]), activation=activation)
    
    block5 = mb_conv_block(inputs=block4, in_channels=round_filters(80, width_coefficient_list[4]), out_channels=round_filters(112, width_coefficient_list[5]), 
                           num_repeat=repeats_scaled[4], stride=1, expansion_factor=exp_ratio[4], se_ratio=se_ratio, k=5, drop_rate=drop_connect_rate, 
                           prev_block_num=sum(repeats_scaled[0:4]), activation=activation)
    
    block6 = mb_conv_block(inputs=block5, in_channels=round_filters(112, width_coefficient_list[5]), out_channels=round_filters(192, width_coefficient_list[6]),
                            num_repeat=repeats_scaled[5], stride=2, expansion_factor=exp_ratio[5], se_ratio=se_ratio, k=5, drop_rate=drop_connect_rate, 
                            prev_block_num=sum(repeats_scaled[0:5]), activation=activation)
    
    block7 = mb_conv_block(inputs=block6, in_channels=round_filters(192, width_coefficient_list[6]), out_channels=round_filters(320, width_coefficient_list[7]),
                            num_repeat=repeats_scaled[6],stride=1, expansion_factor=exp_ratio[6], se_ratio=se_ratio, k=3, drop_rate=drop_connect_rate, 
                            prev_block_num=sum(repeats_scaled[0:6]), activation=activation)

    # Build top
    x = layers.Conv2D(filters=round_filters(1280, width_coefficient_list[8]), kernel_size=(1, 1), padding='same', name='top_conv')(block7)
    x = layers.BatchNormalization()(x)
    x = layers.Activation(activation, name='top_activation')(x)
	
    if include_top:
        x = layers.GlobalAveragePooling2D(name='avg_pool')(x)
        if dropout_rate and dropout_rate > 0:
            x = layers.Dropout(dropout_rate, name='top_dropout')(x)
        x = layers.Dense(classes, activation='softmax', name='output_probs')(x)
    else:
        if pooling == 'avg':
            x = layers.GlobalAveragePooling2D()(x)
        elif pooling == 'max':
            x = layers.GlobalMaxPooling2D()(x)

    # Create model.
    model = Model(input, x, name="EfficientNet-STCustom")

    return model


def get_st_efficientnet_lc_v1(input_shape: Tuple[int, int, int] = None, num_classes: int = None, dropout: float = None) -> tf.keras.Model:
    """
    Creates a Keras model for fine-grained classification from scratch.

    Args:
        input_shape (Tuple[int, int, int]): The shape of the input tensor.
        num_classes (int): The number of classes for the classification task.
        dropout (float): The dropout rate.

    Returns:
        tf.keras.Model: A Keras model for fine-grained classification.
    """

    activation = 'relu6'
    d = 1.
    w = [0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45]
    e = 3
    model = EfficientNet(width_coefficient_list=w, depth_coefficient=d, input_resolution=input_shape[0], expansion_factor=e, depth_trunc='ceil', activation=activation, 
							input_channels=input_shape[2], dropout_rate=dropout, include_top=True, classes=num_classes)
    
    return model
