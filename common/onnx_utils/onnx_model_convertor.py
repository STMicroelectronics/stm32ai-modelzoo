# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import argparse
from pathlib import Path
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from copy import deepcopy
import tf2onnx
import tensorflow as tf
import onnx
import onnxruntime as onnx_rt
import numpy as np
from .tf2onnx_lib import patch_tf2onnx
import torch
from omegaconf import DictConfig
from common.model_utils.tf_model_loader import load_model_from_path
from common.onnx_utils.ssd_onnx_export import SSDExportWrapper

def _quantized_per_tensor(model_path):
    """
    Check if a TFLite model is quantized per-tensor.

    This function loads a TFLite model from the specified path and iterates
    through its tensors to check their quantization parameters. It returns True
    if all quantized tensors use per-tensor quantization, and False if any
    tensor uses per-channel quantization or if the model is not quantized.

    Parameters:
    model_path (str): The file path to the TFLite model.

    Returns:
    bool: True if the model is quantized per-tensor, False otherwise.
    
    Usage:
    is_per_tensor_quantized = _quantized_per_tensor('path/to/model.tflite')
    print(is_per_tensor_quantized)
    """
    # Load the TFLite model
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    # Iterate through the tensors and check their quantization parameters
    for tensor_details in interpreter.get_tensor_details():
        # Skip tensors that are not quantized
        if not tensor_details['quantization_parameters']:
            continue

        # Get the scale and zero_point from the quantization parameters
        scale = tensor_details['quantization_parameters']['scales']
        zero_point = tensor_details['quantization_parameters']['zero_points']

        # Check if the scale and zero_point are per-channel
        if isinstance(scale, np.ndarray) and len(scale) > 1:
            return False  # This indicates per-channel quantization

        if isinstance(zero_point, np.ndarray) and len(zero_point) > 1:
            return False  # This indicates per-channel quantization

    # If all quantized tensors use per-tensor quantization or if there are no quantized tensors, return True
    return True

def _tool_version_used():
    """
    Prints the versions of the ONNX, ONNX Runtime, and TensorFlow libraries currently installed.

    This function retrieves the version numbers of the ONNX (`onnx`), ONNX Runtime (`onnxruntime`),
    and TensorFlow (`tensorflow`) libraries and prints them to the console. It's useful for
    debugging, ensuring compatibility, and reporting issues with these libraries.

    No parameters are needed, and there are no return values.
    Make sure to import the required libraries are installed and imported
    Usage:
    _tool_version_used()  # Call the function to print the versions of the libraries
    """
    print('The version of libraries are: ')
    print(f'onnx: {onnx.__version__}')
    print(f'onnxruntime: {onnx_rt.__version__}')
    print(f'tensorflow: {tf.__version__}')


def onnx_model_converter(input_model_path: str, target_opset: int = 17, output_dir: str = None,
                         static_input_shape=None, input_channels_last=False):
    """
    Converts a TensorFlow model in .h5 or .tflite format to ONNX format.

    This function takes the path to a TensorFlow model and converts it to the ONNX format.
    If the model is already in ONNX format, it prints a message and does nothing.
    For .h5 models, it uses the tf2onnx converter.
    For .tflite models, it checks if the model is quantized per-tensor using the
    _quantized_per_tensor function. If it is, it uses the tflite2onnx converter.
    If the model is not quantized per-tensor, it raises a TypeError.
    If the input model is neither .h5 nor .tflite, it raises a TypeError.

    Parameters:
    input_model_path (str): The file path to the input model. Supported file types are .h5 and .tflite.
    target_opset (int, optional): The ONNX opset version to use for the conversion. Default is 17.
    output_dir (str, optional) : Directory in which to output model
    static_input_shape (List[int], optional) : Static input shape to give the ONNX model. 
        For example [1, 3, 224, 224] will output a model with this input shape instead of 
        [None, 3, 224, 224] (dynamic batch axis)
    input_channels_last : if True, no input is passed to the input_as_nchw arg of
        tf2onnx.convert.from_keras. Use if you want to keep your ONNX model channels last.
    Raises:
    TypeError: If the input model is not in .h5 or .tflite format, or if the .tflite model is not
               quantized per-tensor.

    Usage:
    onnx_converter('path/to/model.h5')  # Converts an .h5 model to ONNX
    onnx_converter('path/to/model.tflite')  # Converts a per-tensor quantized or float .tflite model to ONNX
    """
    # Function implementation follows...
    model_type = Path(input_model_path).suffix
    if model_type == '.onnx':
        print('Model is already in onnx format')
    elif model_type in ['.h5','.keras']:
        h5_model = tf.keras.models.load_model(input_model_path, compile = False)
        # Get the input tensor name
        input_names = [e.name for e in h5_model.inputs]
        output_names = list(h5_model.output_names)
        
        if input_channels_last:
            inputs_as_nchw = None
        else:
            inputs_as_nchw = input_names

        patch_tf2onnx()  # TODO: Remove this once `tf2onnx` supports numpy 2.
        if static_input_shape:
            spec = (tf.TensorSpec(static_input_shape, tf.float32, name=input_names[0]),)
            tf2onnx.convert.from_keras(h5_model,
                                    opset=int(target_opset),
                                    inputs_as_nchw=inputs_as_nchw,
                                    outputs_as_nchw=output_names,
                                    input_signature=spec,
                                    output_path=output_dir)
        else:
            tf2onnx.convert.from_keras(h5_model,
                                    opset=int(target_opset),
                                    inputs_as_nchw=inputs_as_nchw,
                                    outputs_as_nchw=output_names,
                                    output_path=output_dir)
    elif model_type == '.tflite':
        import tflite2onnx
        if _quantized_per_tensor(input_model_path):
#            onnx_file_name = ".".join(os.path.basename(input_model_path).split(".")[:-1])
#            tflite2onnx.convert(input_model_path, f"{onnx_file_name}.onnx")
            tflite2onnx.convert(input_model_path, output_dir)
        else:
            raise TypeError('Only tflite models quantized using per-tensor can be converted')
    else:
        raise TypeError("Provide a valid type of model, only supported types are `.keras`, `.h5`, and `.tflite`")


def torch_model_export_static(cfg: DictConfig, 
                              model_dir: str, 
                              model: object,
                              opset_version: int = 20) -> onnx.ModelProto:
    """
    Exports a PyTorch model to ONNX format with static input shapes.

    Args:
        cfg (DictConfig): Configuration object containing model settings.
        model_dir (str): Directory where the ONNX model will be saved.
        model (object): The PyTorch model to export.
        opset_version (int): ONNX opset version to use (default is 20).

    Returns:
        onnx.ModelProto: The exported ONNX model.
    """
    # Set the model to evaluation mode
    
    if 'ssd' in cfg.model.model_name : 
        model_back = deepcopy(model)
        model=model.to("cpu")
        model.priors = model.priors.to("cpu")
        model=SSDExportWrapper(model)
    
    if 'yolod' in cfg.model.model_name : 
        model.head.decode_in_inference = False

    model.eval()

    # Create a dummy input tensor with the specified input shape from the configuration
    # Need 4d for torch
    dummy_input = torch.randn((1, *cfg.model.input_shape))

    # Define the path to save the ONNX model
    onnx_model_path = Path(model_dir, cfg.model.model_name, cfg.model.model_name+".onnx")
    onnx_model_path.parent.mkdir(exist_ok=True)

    # Export the PyTorch model to ONNX format
    torch.onnx.export(
        model,
        dummy_input,
        onnx_model_path,
        export_params=True, # Store trained parameters in the model file
        opset_version=opset_version,   # ONNX opset version to use
        do_constant_folding=True,   # Optimize constant expressions
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={      # Specify dynamic axes for batch size
            "input": {0: "batch_size"},
            "output": {0: "batch_size"}
        }
    )
    
    if 'ssd' in cfg.model.model_name : 
        model = deepcopy(model_back)
    
    # Load the exported ONNX model from the saved path
    onnx_model = load_model_from_path(cfg, onnx_model_path)
    setattr(onnx_model, 'model_path', onnx_model_path)
    
    # Update the configuration with the path to the ONNX model
    cfg.model.model_path = onnx_model_path

    # Return the loaded ONNX model
    return onnx_model
        
