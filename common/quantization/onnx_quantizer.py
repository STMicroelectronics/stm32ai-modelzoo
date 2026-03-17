# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from datetime import datetime
import glob
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
import logging
import numpy as np
import onnx
import onnxruntime
from onnx import version_converter, checker
from onnxruntime import quantization
from onnxruntime.quantization import (CalibrationDataReader, CalibrationMethod,
                                      QuantFormat, QuantType, quantize_static)
import os
from typing import List

from .quant_utils import get_weights_activations_quant_type, get_calibration_method


def _update_opset(input_model, target_opset, export_dir):
    """
    updates the opset of an onnx model
    inputs:
        input_model: path of the input model.
        target_opset: the target opset model is to be updated to.
    """
    # ir_version in function of opset
    ir_version_dict = {21: 10,
                       20: 9,
                       19: 9,
                       18: 8,
                       17: 8,
                       16: 8,
                       15: 8
                       }

    if not str(input_model).endswith('.onnx'):
        raise TypeError("Error! The model file must be of onnx format!")
    model = onnx.load(input_model)
    # Check the current opset version
    current_opset = model.opset_import[0].version
    if current_opset >= target_opset:
        print(f"[INFO] : The model is already using opset {current_opset} >= {target_opset}")
        return input_model

    # Modify the opset version in the model
    converted_model = version_converter.convert_version(model, target_opset)

    # Potentially change ir_version
    print(f"[INFO] : Model current IR version: {converted_model.ir_version}")
    if target_opset >= 15 and converted_model.ir_version != ir_version_dict[target_opset]:
        converted_model.ir_version = ir_version_dict[target_opset]
        print(f"[INFO] : Update model IR version to {converted_model.ir_version} for compatibility with target opset "
              f"{target_opset}")

    # check if the obtained model is valid
    try:
        checker.check_model(converted_model)
    except checker.ValidationError as e:
        print(f"[ERROR] : The model is invalid. {e}")

    opset_model = f'{export_dir}/{os.path.basename(input_model)}'[:-5] + f'_opset{target_opset}.onnx'
    onnx.save(converted_model, opset_model)

    # Load the modified model using ONNX Runtime Check if the model is valid
    session = onnxruntime.InferenceSession(opset_model)
    try:
        session.get_inputs()
    except Exception as e:
        print(f"[ERROR] : An error occurred while loading the modified model: {e}")
        return

    # Replace the original model file with the modified model
    print(f"[INFO] : The model has been converted to opset {target_opset}, IR {converted_model.ir_version} and saved "
          f"at the same location.")
    return opset_model

def _preprocess_random_images(height: int, width: int, channel: int, size_limit=10):
    """
    Loads a batch of images and preprocess them
    parameter height: image height in pixels
    parameter width: image width in pixels
    parameter size_limit: number of images to load. Default is 100
    return: list of matrices characterizing multiple images
    """
    unconcatenated_batch_data = []
    for i in range(size_limit):
        random_vals = np.random.uniform(0, 1, channel*height*width).astype('float32')
        random_image = random_vals.reshape(1, channel, height, width)
        unconcatenated_batch_data.append(random_image)
        batch_data = np.concatenate(np.expand_dims(unconcatenated_batch_data, axis=0), axis=0)
    print(f'[INFO] : random dataset with {size_limit} random images is prepared!')
    return batch_data

class ImageDataReader(CalibrationDataReader):
    '''
    ImageDataReader for the calibration during onnx quantization.
    The initiation takes as input:
        quantization_samples: an np array containing the calibration samples dataset
        model_path: path of the model to be quantized
    '''
    def __init__(self,
                 quantization_samples,
                 model_path: str):
        # Use inference session to get input shape
        session = onnxruntime.InferenceSession(model_path, None)
        (_, channel, height, width) = session.get_inputs()[0].shape

        # Convert image to input data
        if quantization_samples is not None:
            self.nhwc_data_list = np.expand_dims(quantization_samples, axis=1)
        else:
            self.nhwc_data_list = _preprocess_random_images(height,
                                                           width,
                                                           channel)

        self.input_name = session.get_inputs()[0].name
        self.datasize = len(self.nhwc_data_list)

        self.enum_data = None  # Enumerator for calibration data

    def get_next(self):
        if self.enum_data is None:
            # Create an iterator that generates input dictionaries
            # with input name and corresponding data
            self.enum_data = iter(
                [{self.input_name: nhwc_data} for nhwc_data in self.nhwc_data_list]
            )
        
        return next(self.enum_data, None)  # Return next item from enumerator

    def rewind(self):
        self.enum_data = None  # Reset the enumeration of calibration dataclass ImageDataReader


def quantize_onnx(configs: DictConfig, model_path=None, quantization_samples=None, model: object = None, extra_options: dict = None):
    """
    Quantizes an ONNX model using onnx-runtime.

    Args:
        configs (DictConfig): Configuration dictionary containing quantization and model settings.
        quantization_samples: Calibration/representative dataset as a numpy array (optional).
        model (object, optional): Model object with a model_path attribute, or None to use configs.model.model_path.
        extra_options (dict, optional): Extra options for ONNX quantizer.

    Returns:
        onnxruntime.InferenceSession: Quantized model session with model_path attribute.
    """
#    model_path = configs.model.model_path
#    model_path = model.model_path
    granularity = configs.quantization.granularity.lower()
    target_opset = configs.quantization.target_opset
    output_dir = HydraConfig.get().runtime.output_dir
    export_dir = configs.quantization.export_dir

    export_dir = output_dir + (f'/{export_dir}' if export_dir else '')
    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)
    if granularity == 'per_tensor':
        quant_tag = f'quant_qdq_pt'
    elif granularity == 'per_channel':
        quant_tag = f'quant_qdq_pc'
    else:
        raise TypeError('Not a valid quantization_type!\n',
                        'Only supported options for quantization_type are per_channel, or per_tensor!')

    print(f'[INFO] : Quantizing model : {model_path}')

    opset_model = _update_opset(input_model=model_path, target_opset=target_opset, export_dir=output_dir)

    # set the data reader pointing to the representative dataset
    print('[INFO] : Prepare the data reader for the representative dataset...')
    dr = ImageDataReader(quantization_samples=quantization_samples, model_path=opset_model)
    print('[INFO] : the data reader is ready')

    # preprocess the model to infer shapes of each tensor
    infer_model = os.path.join(export_dir, f'{os.path.basename(opset_model)[:-5]}_infer.onnx')
    quantization.quant_pre_process(input_model_path=opset_model,
                                   output_model_path=infer_model,
                                   skip_optimization=False,
                                   skip_symbolic_shape=True)

    # settings for quantization
    weight_type, activ_type = get_weights_activations_quant_type(cfg=configs)
    calibration_method = get_calibration_method(cfg=configs)
    if configs.quantization.onnx_quant_parameters:
        op_types_to_quantize = configs.quantization.onnx_quant_parameters.op_types_to_quantize
        nodes_to_quantize = configs.quantization.onnx_quant_parameters.nodes_to_quantize
        nodes_to_exclude = configs.quantization.onnx_quant_parameters.nodes_to_exclude
    else:
        op_types_to_quantize = None
        nodes_to_quantize = None
        nodes_to_exclude = None

    # prepare quantized onnx model filename
    quant_model = os.path.join(export_dir,f'{os.path.basename(opset_model)[:-5]}_{quant_tag}.onnx')
    print(f'[INFO] : Quantizing the model {os.path.basename(model_path)}, please wait...')

    quantize_static(
        infer_model,
        quant_model,
        dr,
        op_types_to_quantize=op_types_to_quantize,
        calibrate_method=calibration_method,
        quant_format=QuantFormat.QDQ,
        per_channel= granularity == 'per_channel',
        weight_type=weight_type,
        activation_type=activ_type,
        nodes_to_quantize=nodes_to_quantize,
        nodes_to_exclude=nodes_to_exclude,
        #optimize_model=False,
        extra_options=extra_options)

    # Load the modified model using ONNX Runtime Check if the model is valid
    model = onnxruntime.InferenceSession(quant_model)
    try:
        model.get_inputs()
    except Exception as e:
        print(f"[ERROR] : An error occurred while quantizing the model: {e}")
        return
    print("Quantized model path:", quant_model)
    setattr(model, 'model_path', quant_model)
    return model
