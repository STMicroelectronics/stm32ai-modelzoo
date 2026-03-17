# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from onnxruntime.quantization import QuantType, CalibrationMethod
import keras
import onnx
from onnx import numpy_helper
import os
import numpy as np
from omegaconf import DictConfig
import tensorflow

dict_types = {"Int16": QuantType.QInt16,
              "UInt16": QuantType.QUInt16,
              "Int8": QuantType.QInt8,
              "UInt8": QuantType.QUInt8,
              "Int4": QuantType.QInt4,
              "UInt4": QuantType.QUInt4
              }


def get_weights_activations_quant_type(cfg: DictConfig):
    """
        Converts bit_width type string in onnx type
        Inputs:
                cfg: dict of input parameters
        Returns:
                weight, activation type
    """

    # get Onnx type for weights and activations: Int4, Int8, Int16
    if cfg.quantization.onnx_quant_parameters:
        if cfg.quantization.onnx_quant_parameters.weightType:
            weight_type = dict_types[cfg.quantization.onnx_quant_parameters.weightType]
        else: weight_type = QuantType.QInt8
        if cfg.quantization.onnx_quant_parameters.activType:
            activation_type = dict_types[cfg.quantization.onnx_quant_parameters.activType]
        else: activation_type = QuantType.QInt8
    else:
        weight_type = QuantType.QInt8
        activation_type = QuantType.QInt8

    return weight_type, activation_type


def get_calibration_method(cfg: DictConfig):
    """
        Converts calibration method from string in onnx class type
        Inputs:
                cfg: dict of input parameters
        Returns:
                calibration_method
    """

    if cfg.quantization.onnx_quant_parameters:
        calibration_param = cfg.quantization.onnx_quant_parameters.calibrate_method
    else: calibration_param = None

    if calibration_param is None:
        calibration_method = CalibrationMethod.MinMax
    elif calibration_param == "MinMax":
        calibration_method = CalibrationMethod.MinMax
    elif calibration_param == "Entropy":
        calibration_method = CalibrationMethod.Entropy
    else:
        raise ValueError(f"Unsupported calibration method: {calibration_param}. Review your config yaml file at section"
                         f"quantization_parameters. Only MinMax or Entropy are supported so far.")

    return calibration_method


def update_bit_width(tensor_type: str = None, order: int = None, direction: str = None):
    """
        update the bit width order times, increasing or decreasing
        Inputs:
                tensor_type(str): Int4, UInt4, Int8, UInt8, Int16, or UInt16
                order (int): number of times we update the type in the specified way, must be 1 or 2
                direction (str): 'up' increase the bit width, 'down': decrease the bit_width

        Returns:
                updated_type (str): Int4, UInt4, Int8, UInt8, Int16, or UInt16
    """

    if tensor_type == 'Int4':
        if direction == 'down':
            return dict_types[tensor_type]
        else:
            if order == 1:
                return dict_types['Int8']
            if order >= 2:
                return dict_types['Int16']
    elif tensor_type == 'UInt4':
        if direction == 'down':
            return dict_types[tensor_type]
        else:
            if order == 1:
                return dict_types['UInt8']
            if order >= 2:
                return dict_types['UInt16']

    elif tensor_type == 'Int8':
        if direction == 'down':
            if order >= 1:
                return dict_types['Int4']
        else:
            if order >= 1:
                return dict_types['Int16']
    elif tensor_type == 'UInt8':
        if direction == 'down':
            if order >= 1:
                return dict_types['UInt4']
        else:
            if order >= 1:
                return dict_types['UInt16']

    elif tensor_type == 'Int16':
        if direction == 'down':
            if order == 1:
                return dict_types['Int8']
            if order >= 2:
                return dict_types['Int4']
        else:
            return dict_types[tensor_type]
    elif tensor_type == 'UInt16':
        if direction == 'down':
            if order == 1:
                return dict_types['UInt8']
            if order >= 2:
                return dict_types['UInt4']
        else:
            return dict_types[tensor_type]
    else:
        raise ValueError(f"Unsupported 'update_bit_width' function parameters. Check tensor_type = {tensor_type}, "
                         f"order = {order} and direction = {direction}")


def define_extra_options(cfg: dict = None, list_weights_tensors=None, list_activation_tensors=None, axis_list=None,
                         bit_width_w=None, bit_width_a=None):
    """
            Set ONNX quantizer extra options according to config file
            Inputs:
                    cfg (dict): dictionary of configuration parameters
                    list_weights_tensors (str): list of weights tensor names for which we want to override quantization
                                                parameters. If None, ignored
                    list_activation_tensors (str): list of activation tensor names for which we want to override
                                                quantization parameters. If None, ignored
                    bit_width_w (QuantType): QuantType.QInt16 or QuantType.QUInt16 or QuantType.QInt8 or QuantType.QUInt8,
                                            or QuantType.QInt4 or QuantType.QUInt4 for all weights
                    bit_width_a (QuantType): QuantType.QInt16 or QuantType.QUInt16 or QuantType.QInt8 or QuantType.QUInt8,
                                            or QuantType.QInt4 or QuantType.QUInt4 for all activations
            Returns:
                    a dictionary with all extra options set
    """

    extra_options = dict()

    # when variable is not defined in cfg, extra_options dict receives None. Therefore, Onnx uses its default values
    if cfg.quantization.onnx_extra_options:
        extra_options["WeightSymmetric"] = cfg.quantization.onnx_extra_options.WeightSymmetric \
            if cfg.quantization.onnx_extra_options.WeightSymmetric is not None else True
        extra_options["ActivationSymmetric"] = cfg.quantization.onnx_extra_options.ActivationSymmetric \
            if cfg.quantization.onnx_extra_options.ActivationSymmetric is not None else False
        extra_options["CalibMovingAverage"] = cfg.quantization.onnx_extra_options.CalibMovingAverage \
            if cfg.quantization.onnx_extra_options.CalibMovingAverage is not None else False
        extra_options["QuantizeBias"] = cfg.quantization.onnx_extra_options.QuantizeBias \
            if cfg.quantization.onnx_extra_options.QuantizeBias is not None else True
        extra_options["SmoothQuant"] = cfg.quantization.onnx_extra_options.SmoothQuant \
            if cfg.quantization.onnx_extra_options.SmoothQuant is not None else False
        extra_options["SmoothQuantAlpha"] = cfg.quantization.onnx_extra_options.SmoothQuantAlpha \
            if cfg.quantization.onnx_extra_options.SmoothQuantAlpha is not None else 0.5
        extra_options["SmoothQuantFolding"] = cfg.quantization.onnx_extra_options.SmoothQuantFolding \
            if cfg.quantization.onnx_extra_options.SmoothQuantFolding is not None else True
    else:
        extra_options["WeightSymmetric"] = True
        extra_options["ActivationSymmetric"] = False
        extra_options["CalibMovingAverage"] = False
        extra_options["QuantizeBias"] = True
        extra_options["SmoothQuant"] = False
        extra_options["SmoothQuantAlpha"] = 0.5
        extra_options["SmoothQuantFolding"] = True

    extra_options["TensorQuantOverrides"] = {}

    # Code for setting a specific bit_width for some weights tensor.
    # if we want to keep per-channel quantization we need to add "axis" field for the weights
    if list_weights_tensors:
        for idx, e in enumerate(list_weights_tensors):
            extra_options["TensorQuantOverrides"][e] = [{'quant_type': bit_width_w}]
            if cfg.quantization.granularity == 'per_channel':
                extra_options["TensorQuantOverrides"][e][0]["axis"] = axis_list[idx]

    # Code for setting a specific bit_width for some activations tensors
    if list_activation_tensors:
        for e in list_activation_tensors:
            extra_options["TensorQuantOverrides"][e] = [{'quant_type': bit_width_a}]

    # case where overrides would be specified in the yaml
    # we consider quant_type is mandatory, scale and offset optional. We don't support (yet?) scale and offset
    # per channel but that would be very impractical to write the full list in the yaml. Per-tensor is ok

    if not list_weights_tensors and not list_activation_tensors:
        list_override_tensor = []
        if cfg.quantization.onnx_extra_options:
            if cfg.quantization.onnx_extra_options.weights_tensor_override:
                list_override_tensor = cfg.quantization.onnx_extra_options.weights_tensor_override
            if cfg.quantization.onnx_extra_options.activations_tensor_override:
                list_override_tensor = list_override_tensor + cfg.quantization.onnx_extra_options.activations_tensor_override

        if list_override_tensor:
            for idx, t in enumerate(list_override_tensor):
                # conversion string to type and zero point to int, and scale to np.array float32 as required by ONNX
                t[1].quant_type = dict_types[t[1].quant_type]
                if t[1].zero_point is not None: t[1].zero_point = np.array(t[1].zero_point)
                if t[1].scale is not None: t[1].scale = np.array(t[1].scale, dtype=np.float32)
                extra_options["TensorQuantOverrides"][t[0]] = [dict(t[1])]

    return extra_options


def count_weights(onnx_model_path_quant, w_tensor_name: str = None):
    """
        Count weights that are in 4 bits and weights that are in 8 bits and output the ratio

        Args:
            onnx_model_path_quant: the ONNX quantized model path
            w_tensor_name (str): name of any tensor that has weights

        Returns:
            nb_weights_4bits, nb_weights_8bits, total_count_weights
        """
    nb_weights_4bits = nb_weights_8bits = total_count_weights = 0
    w_values_t_names = [w + '_quantized' for w in w_tensor_name]  # extension needed to get the weights values
    model_quant = onnx.load(onnx_model_path_quant)

    initializers = [initializer for initializer in model_quant.graph.initializer if initializer.name in w_values_t_names]

    for initializer in initializers:
        tensor_values = numpy_helper.to_array(initializer)
        n_weights = tensor_values.size
        total_count_weights += n_weights
        # since np.int4 does not exist we identify 4 bits tensors by the dynamic range having in mind that 4 bits
        # means 16 integers
        dyn_range = int(tensor_values.max()) - int(tensor_values.min())
        if dyn_range <= 15:  # 4 bits
            nb_weights_4bits += n_weights
        elif tensor_values.dtype == np.int8:
            nb_weights_8bits += n_weights
        
    return nb_weights_4bits, nb_weights_8bits, total_count_weights


def weights_based_layer_ranking(model, extension: str = None):
    """
        Count weights (not bias) per layer in a Keras or onnx model

        Args:
            model: the keras or onnx model
            extension (str): model backend, expected 'onnx' or 'keras'

        Returns:
            list of layer name and weight number after ranking
        """

    layer_params = []
    if extension == 'keras':
        for layer in model.layers:
            if hasattr(layer, "kernel"):  # Only include layers with weights
                num_params = layer.get_weights()[0].size
                layer_params.append((layer.name, num_params))
    elif extension == 'onnx':
        initializers = {init.name: init for init in model.graph.initializer}
        for node in model.graph.node:
            if node.op_type in ['Conv', 'ConvTranspose', 'Gemm', 'MatMul']:  # there are weights
                initializer = initializers[node.input[1]]
                num_params = int(np.prod(list(initializer.dims)))
                layer_params.append((initializer.name, num_params))

    # Sort by number of parameters in descending order
    layer_params_ranked = sorted(layer_params, key=lambda x: x[1], reverse=True)

    return layer_params_ranked
    

def _get_initializer_tensor(model, name: str = None):
    """
        Report weights (not bias) corresponding to tensor 'name' if exists, in an onnx model

        Args:
            model: the onnx model
            name (str): tensor name

        Returns: weight tensor values

    """
    for tensor in model.graph.initializer:
        if tensor.name == name:
            return onnx.numpy_helper.to_array(tensor)
    return None


def _onnx_node_identity_card(model, node):
    """
        Returns a list with node characteristic in order to make a ranking later-on

        Args:
            model: the onnx model
            node: node under consideration

        Returns:
            list of node characteristics
    """

    node_card_list = []
    group = 1

    if node.op_type == "Conv":
        for attr in node.attribute:
            if attr.name == "group":
                group = attr.i
                break
        weight_name = node.input[1]
        weight = _get_initializer_tensor(model, weight_name)
        # onnx 'Conv' weight expected shape: [out_channels, in_channels_per_group, kH, kW]
        out_channels, in_channels_per_group, kH, kW = weight.shape
        nparams = int(np.prod([out_channels, in_channels_per_group, kH, kW]))
        params_per_scale = int(np.prod([in_channels_per_group, kH, kW]))
        # For depthwise, we expect in_channels_per_group == 1 and group == in_channels == out_channels
        if in_channels_per_group == 1 and group == out_channels:
            layer_type = 0  # DW
        else:
            layer_type = 1  # Conv2D
        node_card_list = [node.name, layer_type, nparams, params_per_scale]
    elif node.op_type in ["Gemm", "MatMul"]:
        weight_name = node.input[1]
        weight = _get_initializer_tensor(model, weight_name)
        # There is a possibility that MatMul works with 2 tensors none of them being of type 'initializer' so with no weights
        # in this case we report an empty list
        if weight is not None:
            out_channels, in_channels = weight.shape
            nparams = out_channels * in_channels
            params_per_scale = out_channels
            node_card_list = [node.name, 2, nparams, params_per_scale]
        else:
            node_card_list = []

    return node_card_list


def _keras_layer_identity_card(layer):
    """
        Returns a list with node characteristic in order to make a ranking later-on

        Args:
            layer: layer under consideration

        Returns:
            list of layers characteristics
    """
    layer_card_list = []
    
    if hasattr(layer, "kernel"):  # Only include layers with weights
        weight = layer.get_weights()[0]
        nparams = weight.size
        if isinstance(layer, tensorflow.keras.layers.DepthwiseConv2D):
            layer_type = 0  # DW
            kH, kW, in_ch, depth_mult = weight.shape
            params_per_scale = kH * kW
        elif isinstance(layer, tensorflow.keras.layers.Conv2D):
            layer_type = 1  # Conv2D
            kH, kW, in_ch, out_ch = weight.shape
            params_per_scale = int(np.prod([kH, kW, in_ch]))
        elif isinstance(layer, tensorflow.keras.layers.Dense):
            layer_type = 2  # Dense
            in_dim, out_dim = weight.shape
            params_per_scale = out_dim

        layer_card_list = [layer.name, layer_type, nparams, params_per_scale]
    
    return layer_card_list


def composite_score_layer_ranking(model, extension: str = None):
    """
        Count weights (not bias) per layer in a Keras model

        Args:
            model: the model either onnx or keras
            extension: model backend, expected 'onnx' or 'keras'

        Returns:
            list of layer names ranked
        """

    layer_params = []

    if extension == '.keras':
        for layer in model.layers:
            layer_card_list = _keras_layer_identity_card(layer)
            if layer_card_list:
                layer_params.append(layer_card_list)
    elif extension == '.onnx':
        for node in model.graph.node:
            node_card_list = _onnx_node_identity_card(model, node)
            if node_card_list:
                layer_params.append(node_card_list)

    # Ranking of layers for mixed precision w4w8 quantization
    layer_params_ranked = sorted(layer_params, key=lambda x: (x[2], -x[3], x[0]), reverse=True)

    return layer_params_ranked