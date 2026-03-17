# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import numpy as np
import onnx
import math
import shutil
from omegaconf import DictConfig
from onnxruntime.quantization import (CalibrationDataReader, CalibrationMethod, QuantFormat, QuantType)
from onnxruntime.quantization.qdq_loss_debug import (collect_activations, compute_activation_error,
                                                     compute_weight_error, create_activation_matching,
                                                     create_weight_matching, modify_model_output_intermediate_tensors)
from onnxruntime import set_default_logger_severity

from .quant_utils import define_extra_options, update_bit_width, count_weights
from .onnx_quantizer import ImageDataReader
from common.utils import log_to_file, tf_dataset_to_np_array


def tensors_inspection(cfg, float_model_path, quantized_model_path, insp_set, threshold_weights, threshold_activation,
                       output_dir):
    """
        Uses onnx-runtime debug functions to inspect impact of quantization on model tensors.

        Args:
            float_model_path: The Onnx float model
            quantized_model_path: Onnx QdQ quantized model
            insp_set (tf.data.Dataset): A set of input samples on which we compare the 2 models quality metrics
            threshold_weights: reports the 'threshold_weights' worst SNR weight tensor
            threshold_activation: reports the 'threshold_activation' worst SNR activation tensor
            output_dir: file location for logging

        Returns:
            None
        """

    set_default_logger_severity(3)
    # weights inspection
    matched_weights = create_weight_matching(float_model_path, quantized_model_path)
    weights_error = compute_weight_error(matched_weights, err_func=_my_compute_signal_to_quantization_noise_ratio)

    list_snr_weights = []
    for k, v in weights_error.items():
        list_snr_weights.append((k, v))
    list_snr_weights = sorted(list_snr_weights, key=lambda snr: snr[1])

    # log weight list
    log_to_file(output_dir, f"\nWeights tensors SNR:")
    for tensor_snr in list_snr_weights:
        log_to_file(output_dir, f"{tensor_snr[0]}: {tensor_snr[1]:.3f}")

    # remove bias tensors from list, they will not be overrided and be kept in INT32 in any case
    w_and_bias_names = [x[0] for x in list_snr_weights]
    b_names = _get_model_bias_tensor_names(quantized_model_path)
    w_tensors_names = _prevent_bias_tensor_override(w_and_bias_names, b_names)
    selected_w_tensors_names = w_tensors_names
    if threshold_weights:
        selected_w_tensors_names = selected_w_tensors_names[0:threshold_weights]

    # get axis values for per-channel override
    axis_per_channel_list = _make_override_per_channel(model_path=float_model_path, weight_tensor_names=selected_w_tensors_names)

    # activations inspection
    aug_float_model_path = _generate_aug_model_path(float_model_path)
    modify_model_output_intermediate_tensors(float_model_path, aug_float_model_path)
    aug_qdq_model_path = _generate_aug_model_path(quantized_model_path)
    modify_model_output_intermediate_tensors(quantized_model_path, aug_qdq_model_path)

    if cfg.model.framework == "tf":
        # Convert the tf dataset to NumPy array as dataloader was based on TF framework
        data, labels = tf_dataset_to_np_array(insp_set, nchw=True)
    input_data_reader = ImageDataReader(quantization_samples=data, model_path=float_model_path)
    float_activations = collect_activations(aug_float_model_path, input_data_reader)
    input_data_reader.rewind()
    qdq_activations = collect_activations(aug_qdq_model_path, input_data_reader)

    # activation inspections
    act_matching = create_activation_matching(qdq_activations, float_activations)
    act_error = compute_activation_error(act_matching)
    list_snr_activations = []
    for k, v in act_error.items():
        list_snr_activations.append((k, v['xmodel_err']))
    list_snr_activations = sorted(list_snr_activations, key=lambda snr: snr[1])

    # log activation list
    log_to_file(output_dir, f"\nActivations tensors SNR:")
    for tensor_snr in list_snr_activations:
        log_to_file(output_dir, f"{tensor_snr[0]}: {tensor_snr[1]:.3f}")

    if threshold_activation:
        list_snr_activations = list_snr_activations[0:threshold_activation]
    selected_act_tensors_names = [x[0] for x in list_snr_activations]

    return selected_w_tensors_names, selected_act_tensors_names, axis_per_channel_list


def _my_compute_signal_to_quantization_noise_ratio(x, y) -> float:
    """
        Auxiliary function to compute SNR between 2 tensors

        Args:
            x: first tensor
            y: second tensor

        Returns:
            SNR ~ 20 * log10 ( norm(x) / norm(x - y) )
    """
    if isinstance(x, np.ndarray):
        if x.size == 1:
            xlist = [[x]]
        else:
            xlist = [x]
    elif isinstance(x, np.float32):
        xlist = [[x]]
    else:  # list
        xlist = x

    if isinstance(y, np.ndarray):
        if y.size == 1:
            ylist = [[y]]
        else:
            ylist = [y]
    elif isinstance(y, np.float32):
        ylist = [[y]]
    else:  # list
        ylist = y

    if len(xlist) != len(ylist):
        raise RuntimeError("Unequal number of tensors to compare!")

    left = np.concatenate(xlist).flatten()
    right = np.concatenate(ylist).flatten()

    epsilon = np.finfo("float").eps
    tensor_norm = max(np.linalg.norm(left), epsilon)
    diff_norm = max(np.linalg.norm(left - right), epsilon)
    res = tensor_norm / diff_norm
    return 20 * math.log10(res)


def _generate_aug_model_path(model_path: str) -> str:
    aug_model_path = (
        model_path[: -len(".onnx")] if model_path.endswith(".onnx") else model_path
    )
    return aug_model_path + ".save_tensors.onnx"


def _get_model_bias_tensor_names(model_path):
    """
        reports all bias tensor names in a network

        Args:
            model_path: an ONNX model path

        Returns:
            a list of all bias tensors names

    """
    model_aux = onnx.load(model_path)
    bias_names_list = []

    for node in model_aux.graph.node:
        if node.op_type in ["Conv", "Gemm"]:
            # So far restricted support to some layers type. Maybe other layers have bias...
            # For Gemm and Conv node.input should return [input, weights, bias] if there is a bias
            if len(node.input) > 2:
                bias_names_list.append(node.input[2])

    return bias_names_list


def _prevent_bias_tensor_override(list_w_b_tensor, list_b_tensor):
    """
        remove bias tensor name from weight and bias list

        Args:
            list_w_b_tensor: list of weights and bias tensor names
            list_b_tensor: list of bias tensor names

        Returns:
            a list of weight only tensor names

    """

    for name in list_b_tensor:
        if name in list_w_b_tensor:
            list_w_b_tensor.remove(name)

    return list_w_b_tensor


def _make_override_per_channel(model_path, weight_tensor_names):

    model = onnx.load(model_path)
    axis_list = []
    for name in weight_tensor_names:
        for node in model.graph.node:
            if name in node.input:
                if node.op_type == "Conv":
                    axis_list.append(0)
                elif node.op_type == "ConvTranspose":
                    axis_list.append(1)
                elif node.op_type == "Gemm":
                    attr_dict = {attr.name: onnx.helper.get_attribute_value(attr) for attr in node.attribute}
                    if "transB" in attr_dict:
                        if attr_dict["transB"] == 1:
                            axis_list.append(0)
                        else:
                            axis_list.append(1)  # default value
                    else:
                        axis_list.append(1)  # default value
                elif node.op_type == "MatMul":
                    axis_list.append(1)  # default value
                else:
                    axis_list.append(None)
                break

    return axis_list


def _get_node_attributes_names(node):

    list_attributes_names = []
    for a in node.attribute:
        list_attributes_names.append(a.name)

    return list_attributes_names


def onnx_tensor_names(onnx_model_path_flp, onnx_model_path_quant, layer_rank):
    """
        Find equivalent quantized ONNX weights tensors names that corresponds to Onnx layers names

        Args:
            onnx_model_path_flp: the ONNX floating point model path
            onnx_model_path_quant: the ONNX quantized model path
            layer_rank: list of tuple (layer name, scores...)

        Returns:
            w_tensor_name and axis_list (for later per-channel override)
        """ 
        
    layer_names = [layer[0] for layer in layer_rank]

    model_flp = onnx.load(onnx_model_path_flp)
    w_tensor_names_flp = []

    onnx_flp_node_identity = [{"inputs": n.input, "name": n.name, "op_type": n.op_type} for n in model_flp.graph.node]

    for name in layer_names:
        for node in onnx_flp_node_identity:
            # only consider layers having weights and layer name is in the weight tensor name or
            # layer name is in the node names for conv2d
            if node["op_type"] in ['Conv', 'ConvTranspose', 'Gemm', 'MatMul']:  # there are weights
                if name in node["inputs"][1] or name in node["name"]:
                    if node["inputs"][1] not in w_tensor_names_flp:
                        w_tensor_names_flp.append(node["inputs"][1])
                        break

    if len(layer_names) != len(w_tensor_names_flp):
        raise ValueError(f"Not able to make an exact matching between Keras and corresponding ONNX weight tensors names ")

    axis_list = _make_override_per_channel(onnx_model_path_flp, w_tensor_names_flp)

    model_quant = onnx.load(onnx_model_path_quant)
    w_tensor_names_quant = []

    onnx_quant_node_identity = [{"inputs": n.input, "name": n.name, "op_type": n.op_type} for n in model_quant.graph.node]

    for name in w_tensor_names_flp:
        for node in onnx_quant_node_identity:
            # only consider layers having weights and layer name is in the weight tensor name or
            # layer name is in the node names
            if node["op_type"] in ['Conv', 'ConvTranspose', 'Gemm', 'MatMul']:  # there are weights
                if name in node["inputs"][1] or name in node["name"]:
                    w_tensor_names_quant.append(node["inputs"][1].split('_DequantizeLinear_Output')[0])
                    break

    if len(layer_names) != len(w_tensor_names_quant):
        raise ValueError(f"Not able to make an exact matching between Keras and corresponding quantized ONNX weight "
                         f"tensors names ")

    return w_tensor_names_quant, axis_list

