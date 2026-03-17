# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import math
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, initializers, models
from tensorflow.keras.layers import Input


def _activation_by_name(inputs, activation="relu", name=None):
    if activation is None:
        return inputs

    layer_name = name and activation and name + activation
    return layers.Activation(activation=activation, name=layer_name)(inputs)

def _batchnorm_with_activation(inputs, activation=None, name=None):
    nn = layers.BatchNormalization(name=name and name + "bn")(inputs)
    if activation:
        nn = _activation_by_name(nn, activation=activation, name=name)
    return nn


def _depthwise_conv2d_no_bias(inputs, kernel_size, strides=1, padding="valid", name=None):
    """Typical DepthwiseConv2D with `use_bias` default as `False` and fixed padding
    """
    kernel_size = kernel_size if isinstance(kernel_size, (list, tuple)) else (kernel_size, kernel_size)
    if isinstance(padding, str):
        padding = padding.lower()
    return layers.DepthwiseConv2D(
        kernel_size,
        strides=strides,
        padding="valid" if padding == "valid" else "same",
        use_bias=False,
        name=name and name + "dw_conv")(inputs)

def _conv2d_no_bias(inputs, filters, kernel_size=1, strides=1, padding="valid", groups=1, name=None):
    kernel_size = kernel_size if isinstance(kernel_size, (list, tuple)) else (kernel_size, kernel_size)
    if isinstance(padding, str):
        padding = padding.lower()

    groups = max(1, groups)
    return layers.Conv2D(
        filters,
        kernel_size,
        strides=strides,
        padding="valid" if padding == "valid" else "same",
        use_bias=False,
        groups=groups,
        name=name and name + "conv")(inputs)

def _conv_dw_pw_block(inputs, filters, kernel_size=1, strides=1, use_depthwise_conv=False, activation="swish", name=""):
    nn = inputs
    if use_depthwise_conv:
        nn = _depthwise_conv2d_no_bias(nn, kernel_size, strides, padding="same", name=name)
        nn = _batchnorm_with_activation(nn, activation=activation, name=name + "dw_")
        kernel_size, strides = 1, 1
    nn = _conv2d_no_bias(nn, filters, kernel_size, strides, padding="same", name=name)
    nn = _batchnorm_with_activation(nn, activation=activation, name=name)
    return nn

def _focus_stem(inputs, filters, kernel_size=3, strides=1, padding="valid", activation="swish", name=""):
    nn = _conv_dw_pw_block(inputs, 12, kernel_size=3, strides=2, activation=activation, name="st_")
    nn = _conv_dw_pw_block(nn, filters, kernel_size=kernel_size, strides=strides, activation=activation, name=name)
    return nn

def _spatial_pyramid_pooling(inputs, pool_sizes=(5, 9, 13), activation="swish", name=""):
    channel_axis = -1
    input_channels = inputs.shape[channel_axis]
    nn = _conv_dw_pw_block(inputs, input_channels // 2, kernel_size=1, activation=activation, name=name + "1_")
    pp = [layers.MaxPool2D(pool_size=ii, strides=1, padding="same")(nn) for ii in pool_sizes]
    nn = layers.Concatenate(axis=channel_axis)([nn, *pp])
    nn = _conv_dw_pw_block(nn, input_channels, kernel_size=1, activation=activation, name=name + "2_")
    return nn

def _csp_block(inputs, expansion=0.5, use_shortcut=True, use_depthwise_conv=False, activation="swish", name=""):
    input_channels = inputs.shape[-1]
    nn = _conv_dw_pw_block(inputs, int(input_channels * expansion), activation=activation, name=name + "1_")
    nn = _conv_dw_pw_block(nn, input_channels, kernel_size=3, strides=1, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "2_")
    if use_shortcut:
        nn = layers.Add()([inputs, nn])
    return nn

def _csp_stack(inputs, depth, out_channels=-1, expansion=0.5, use_shortcut=True, use_depthwise_conv=False, activation="swish", name=""):
    channel_axis = -1
    out_channels = inputs.shape[channel_axis] if out_channels == -1 else out_channels
    hidden_channels = int(out_channels * expansion)
    short = _conv_dw_pw_block(inputs, hidden_channels, kernel_size=1, activation=activation, name=name + "short_")

    deep = _conv_dw_pw_block(inputs, hidden_channels, kernel_size=1, activation=activation, name=name + "deep_")
    for id in range(depth):
        block_name = name + "block{}_".format(id + 1)
        deep = _csp_block(deep, 1, use_shortcut=use_shortcut, use_depthwise_conv=use_depthwise_conv, activation=activation, name=block_name)

    out = layers.Concatenate(axis=channel_axis)([deep, short])
    out = _conv_dw_pw_block(out, out_channels, kernel_size=1, activation=activation, name=name + "output_")
    return out

def _CSPDarknet(width_mul=1, depth_mul=1, out_features=[-3, -2, -1], use_depthwise_conv=False, input_shape=(512, 512, 3), activation="swish", model_name=""):
    """
    Creates a _CSPDarknet model with specified parameters.

    Parameters:
    width_mul (float, optional): Width multiplier for the model. Default is 1.
    depth_mul (float, optional): Depth multiplier for the model. Default is 1.
    out_features (list, optional): Indices of features to output. Default is [-3, -2, -1].
    use_depthwise_conv (bool, optional): Whether to use depthwise convolution. Default is False.
    input_shape (tuple, optional): Shape of the input tensor, e.g., (height, width, channels). Default is (512, 512, 3).
    activation (str, optional): Activation function to use. Default is "swish".
    model_name (str, optional): Name of the model. Default is an empty string.

    Returns:
    Model: A _CSPDarknet model instance configured with the specified parameters.
    """
    base_channels, base_depth = int(width_mul * 64), max(round(depth_mul * 3), 1)
    inputs = tf.keras.Input((input_shape))
    nn = _focus_stem(inputs, base_channels, activation=activation, name="stem_")
    features = [nn]
    depthes = [base_depth, base_depth * 3, base_depth * 3, base_depth]
    channels = [base_channels * 2, base_channels * 4, base_channels * 8, base_channels * 16]
    use_spps = [False, False, False, True]
    use_shortcuts = [True, True, True, False]
    for id, (channel, depth, use_spp, use_shortcut) in enumerate(zip(channels, depthes, use_spps, use_shortcuts)):
        stack_name = "stack{}_".format(id + 1)
        nn = _conv_dw_pw_block(nn, channel, kernel_size=3, strides=2, use_depthwise_conv=use_depthwise_conv, activation=activation, name=stack_name)
        if use_spp:
            nn = _spatial_pyramid_pooling(nn, activation=activation, name=stack_name + "spp_")
        nn = _csp_stack(nn, depth, use_shortcut=use_shortcut, use_depthwise_conv=use_depthwise_conv, activation=activation, name=stack_name)
        features.append(nn)

    nn = [features[ii] for ii in out_features]
    model = models.Model(inputs, nn, name=model_name)
    return model


def _upsample_merge(inputs, csp_depth, use_depthwise_conv=False, activation="swish", name=""):
    # print(f">>>> _upsample_merge inputs: {[ii.shape for ii in inputs] = }")
    channel_axis = -1
    target_channel = inputs[-1].shape[channel_axis]
    fpn_out = _conv_dw_pw_block(inputs[0], target_channel, activation=activation, name=name + "fpn_")
    inputs[0] = layers.UpSampling2D(size=(2, 2),interpolation='bilinear')(fpn_out) # The 'nearest' interpolation is not supported by XLA_GPU
    nn = layers.Concatenate(axis=channel_axis)(inputs)
    nn = _csp_stack(nn, csp_depth, target_channel, 0.5, False, use_depthwise_conv, activation=activation, name=name)
    return fpn_out, nn

def _downsample_merge(inputs, csp_depth, use_depthwise_conv=False, activation="swish", name=""):
    # print(f">>>> _downsample_merge inputs: {[ii.shape for ii in inputs] = }")
    channel_axis = -1
    inputs[0] = _conv_dw_pw_block(inputs[0], inputs[-1].shape[channel_axis], 3, 2, use_depthwise_conv, activation=activation, name=name + "down_")
    nn = layers.Concatenate(axis=channel_axis)(inputs)
    nn = _csp_stack(nn, csp_depth, nn.shape[channel_axis], 0.5, False, use_depthwise_conv, activation=activation, name=name)
    return nn

def _path_aggregation_fpn(features, depth_mul=1, use_depthwise_conv=False, activation="swish", name=""):
    """
    Creates a Path Aggregation Feature Pyramid Network (FPN) with specified parameters.

    Parameters:
    features (list): List of feature tensors from the backbone network.
    depth_mul (float, optional): Depth multiplier for the model. Default is 1.
    use_depthwise_conv (bool, optional): Whether to use depthwise convolution. Default is False.
    activation (str, optional): Activation function to use. Default is "swish".
    name (str, optional): Base name for the layers. Default is an empty string.

    Returns:
    list: List of output tensors from the Path Aggregation FPN.
    """
    csp_depth = max(round(depth_mul * 3), 1)
    p3, p4, p5 = features
    fpn_out0, f_out0 = _upsample_merge([p5, p4], csp_depth, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "c3p4_")
    fpn_out1, pan_out2 = _upsample_merge([f_out0, p3], csp_depth, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "c3p3_")
    pan_out1 = _downsample_merge([pan_out2, fpn_out1], csp_depth, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "c3n3_")
    pan_out0 = _downsample_merge([pan_out1, fpn_out0], csp_depth, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "c3n4_")
    return [pan_out2, pan_out1, pan_out0]

def _yolox_head_single(inputs, out_channels, num_classes=80, regression_len=4, num_anchors=1, use_depthwise_conv=False, use_object_scores=True, activation="swish", name=""):
    """
    Creates a single head of the _YOLOX model with specified parameters.

    Parameters:
    inputs (tensor): Input tensor from the feature pyramid network.
    out_channels (int): Number of output channels.
    num_classes (int, optional): Number of classes for detection. Default is 80.
    regression_len (int, optional): Length of the bounding box regression output. Default is 4.
    num_anchors (int, optional): Number of anchor boxes. Default is 1.
    use_depthwise_conv (bool, optional): Whether to use depthwise convolution. Default is False.
    use_object_scores (bool, optional): Whether to use object scores. Default is True.
    activation (str, optional): Activation function to use. Default is "swish".
    name (str, optional): Base name for the layers. Default is an empty string.

    Returns:
    tensor: Concatenated output tensor containing regression, object, and classification predictions.
    """
    stem = _conv_dw_pw_block(inputs, out_channels, activation=activation, name=name + "stem_")

    # cls_convs, cls_preds
    cls_nn = _conv_dw_pw_block(stem, out_channels, kernel_size=3, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "cls_1_")
    cls_nn = _conv_dw_pw_block(cls_nn, out_channels, kernel_size=3, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "cls_2_")
    cls_out = layers.Conv2D(num_classes * num_anchors, kernel_size=1, use_bias=False, name=name + "class_out")(cls_nn)

    # reg_convs, reg_preds
    reg_nn = _conv_dw_pw_block(stem, out_channels, kernel_size=3, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "reg_1_")
    reg_nn = _conv_dw_pw_block(reg_nn, out_channels, kernel_size=3, use_depthwise_conv=use_depthwise_conv, activation=activation, name=name + "reg_2_")
    reg_out = layers.Conv2D(regression_len * num_anchors, use_bias=False, kernel_size=1, name=name + "regression_out")(reg_nn)

    # obj_preds
    obj_out = layers.Conv2D(1 * num_anchors, kernel_size=1, use_bias=False, name=name + "object_out")(reg_nn)

    return layers.Concatenate(axis=-1)([reg_out,obj_out,cls_out])
    

def _yolox_head(inputs, width_mul=1.0, num_classes=80, regression_len=4, num_anchors=1, use_depthwise_conv=False, use_object_scores=True, activation="swish", name=""):
    """
    Creates the head of the _YOLOX model with specified parameters.

    Parameters:
    inputs (list): List of input tensors from the feature pyramid network.
    width_mul (float, optional): Width multiplier for the model. Default is 1.0.
    num_classes (int, optional): Number of classes for detection. Default is 80.
    regression_len (int, optional): Length of the bounding box regression output. Default is 4.
    num_anchors (int, optional): Number of anchor boxes. Default is 1.
    use_depthwise_conv (bool, optional): Whether to use depthwise convolution. Default is False.
    use_object_scores (bool, optional): Whether to use object scores. Default is True.
    activation (str, optional): Activation function to use. Default is "swish".
    name (str, optional): Base name for the layers. Default is an empty string.

    Returns:
    list: List of output tensors from the _YOLOX head.
    """
    out_channel = int(256 * width_mul)
    outputs = []
    for id, input in enumerate(inputs):
        cur_name = name + "{}_".format(id + 1)
        out = _yolox_head_single(
            input, out_channel, num_classes, regression_len, num_anchors, use_depthwise_conv, use_object_scores, activation=activation, name=cur_name
        )
        outputs.append(out)
    return outputs

def _YOLOX(
    features_pick=[-3, -2, -1],
    depth_mul=1,
    width_mul=-1,
    use_depthwise_conv=False,
    regression_len=4,  # bbox output len,
    num_anchors=1,
    use_object_scores=True,
    input_shape=(640, 640, 3),
    num_classes=1,
    activation="swish",
    model_name="st_yoloxn"):
    """
    Creates a _YOLOX model with specified parameters.

    Parameters:
    features_pick (list, optional): Indices of features to pick from the backbone. Default is [-3, -2, -1].
    depth_mul (float, optional): Depth multiplier for the model. Default is 1.
    width_mul (float, optional): Width multiplier for the model. Default is -1, which sets it to 1.
    use_depthwise_conv (bool, optional): Whether to use depthwise convolution. Default is False.
    regression_len (int, optional): Length of the bounding box regression output. Default is 4.
    num_anchors (int, optional): Number of anchor boxes. Default is 1.
    use_object_scores (bool, optional): Whether to use object scores. Default is True.
    input_shape (tuple, optional): Shape of the input tensor, e.g., (height, width, channels). Default is (640, 640, 3).
    num_classes (int, optional): Number of classes for detection. Default is 1.
    activation (str, optional): Activation function to use. Default is "swish".
    model_name (str, optional): Name of the model. Default is "yolox".

    Returns:
    Model: A _YOLOX model instance configured with the specified parameters.
    """

    width_mul = width_mul if width_mul > 0 else 1
    backbone = _CSPDarknet(width_mul, depth_mul, features_pick, use_depthwise_conv, input_shape, activation=activation, model_name="darknet")
    features = backbone.outputs

    inputs = backbone.inputs[0]

    fpn_features = _path_aggregation_fpn(features, depth_mul=depth_mul, use_depthwise_conv=use_depthwise_conv, activation=activation, name="pafpn_")
    outputs = _yolox_head(fpn_features, width_mul, num_classes, regression_len, num_anchors, use_depthwise_conv, use_object_scores, activation=activation, name="head_")
    model = models.Model(inputs, outputs, name=model_name)

    return model

def get_st_yoloxn(input_shape, num_anchors, num_classes, depth_mul=0.33, width_mul=0.25, **model_kwargs):
    """
    Creates a _YOLOX model with specified parameters.

    Parameters:
    input_shape (tuple): Shape of the input tensor, e.g., (height, width, channels).
    num_anchors (int): Number of anchor boxes.
    num_classes (int): Number of classes for detection.
    depth_mul (float, optional): Depth multiplier for the model
    width_mul (float, optional): Width multiplier for the model

    Returns:
    _YOLOX: A _YOLOX model instance configured with the specified parameters.
    """
    return _YOLOX(input_shape=input_shape,num_classes=num_classes,num_anchors=num_anchors,use_depthwise_conv=True, activation="relu6", depth_mul=depth_mul, width_mul=width_mul, model_name="st_yoloxn")
    