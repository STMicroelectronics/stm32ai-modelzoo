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

import tf2onnx
import tflite2onnx
import tensorflow as tf
import onnx as onx
import onnxruntime as onx_rt
import numpy as np

def quantized_per_tensor(model_path):
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
    is_per_tensor_quantized = quantized_per_tensor('path/to/model.tflite')
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

def tool_version_used():
    """
    Prints the versions of the ONNX, ONNX Runtime, and TensorFlow libraries currently installed.

    This function retrieves the version numbers of the ONNX (`onnx`), ONNX Runtime (`onnxruntime`),
    and TensorFlow (`tensorflow`) libraries and prints them to the console. It's useful for
    debugging, ensuring compatibility, and reporting issues with these libraries.

    No parameters are needed, and there are no return values.
    Make sure to import the required libraries are installed and imported
    Usage:
    tool_version_used()  # Call the function to print the versions of the libraries
    """
    print('The version of libraries are: ')
    print(f'onnx: {onx.__version__}')
    print(f'onnxruntime: {onx_rt.__version__}')
    print(f'tensorflow: {tf.__version__}')


def onnx_model_converter(input_model_path: str, target_opset: int = 17):
    """
    Converts a TensorFlow model in .h5 or .tflite format to ONNX format.

    This function takes the path to a TensorFlow model and converts it to the ONNX format.
    If the model is already in ONNX format, it prints a message and does nothing.
    For .h5 models, it uses the tf2onnx converter.
    For .tflite models, it checks if the model is quantized per-tensor using the
    quantized_per_tensor function. If it is, it uses the tflite2onnx converter.
    If the model is not quantized per-tensor, it raises a TypeError.
    If the input model is neither .h5 nor .tflite, it raises a TypeError.

    Parameters:
    input_model_path (str): The file path to the input model. Supported file types are .h5 and .tflite.
    target_opset (int, optional): The ONNX opset version to use for the conversion. Default is 17.

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
    elif model_type == '.h5':
        h5_model = tf.keras.models.load_model(input_model_path)
        # Get the input tensor name
        input_name = h5_model.input.name
        onnx_file_name = ".".join(os.path.basename(input_model_path).split(".")[:-1])
        tf2onnx.convert.from_keras(h5_model,
                                   opset=target_opset,
                                   inputs_as_nchw=[input_name],
                                   output_path=f"{onnx_file_name}.onnx");
    elif model_type == '.tflite':
        if quantized_per_tensor(input_model_path):
            onnx_file_name = ".".join(os.path.basename(input_model_path).split(".")[:-1])
            tflite2onnx.convert(input_model_path, f"{onnx_file_name}.onnx");
        else:
            raise TypeError('Only tflite models quantized using per-tensor can be converted')
    else:
        raise TypeError("Provide a valid type of model, only supported types are `.h5`, and `.tflite`")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example script that accepts two arguments.')
    parser.add_argument('--model', help='The path to the input model')
    parser.add_argument('--opset', help='The target opset: default value is 17', default=17)
    args = parser.parse_args()
    tool_version_used()
    onnx_model_converter(args.model, args.opset)
