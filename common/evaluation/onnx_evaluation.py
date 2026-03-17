# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import numpy as np
import os
import tensorflow as tf
import onnx
import mlflow
import tqdm
from common.utils import log_to_file


def predict_onnx(sess: onnx.ModelProto, data: np.ndarray) -> np.ndarray:
    """
    Runs inference on an ONNX model per image.

    Args:
        sess (onnx.ModelProto): The ONNX model.
        data (np.ndarray): The input data for the model.

    Returns:
        np.ndarray: The model's predictions.
    """
    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name
    # Process each image individually
    predictions = []
    for i in range(data.shape[0]):
        single_data = data[i:i + 1]  # Set batch size to 1
        single_predictions = sess.run([label_name], {input_name: single_data.astype(np.float32)})[0]
        predictions.append(single_predictions)

    # Concatenate all predictions
    onx_pred = np.concatenate(predictions, axis=0)
    return onx_pred

def predict_onnx_batch(sess: onnx.ModelProto, data: tf.data.Dataset, nchw = True) -> np.ndarray:
    """
    Runs inference on an ONNX model per batch.

    Args:
        sess (onnx.ModelProto): The ONNX model.
        data (tf.data.Dataset): The input data for the model.
        nchw (boolean) channel first (True) or last (False)

    Returns:
        np.ndarray: The model's predictions.
    """
    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name
    # Process each image individually
    predictions = []
    batch_labels = []

    for images, labels in tqdm.tqdm(data):
        batch_data = tf.cast(images, dtype=tf.float32).numpy()
        # Convert image to input data format
        if nchw and batch_data is not None:
            if batch_data.ndim == 4:
                # If last dim is smaller than height/width, assume NHWC -> convert to NCHW
                if batch_data.shape[-1] < batch_data.shape[-2]:
                    batch_data = np.transpose(batch_data, (0, 3, 1, 2))
                # else assume already NCHW, do nothing

            elif batch_data.ndim == 3:
                # If last dim is smaller than height, assume HWC -> CHW
                if batch_data.shape[-1] < batch_data.shape[-2]:
                    batch_data = np.transpose(batch_data, (2, 0, 1))
                # else assume already CHW, do nothing

            else:
                raise ValueError("The input array must have either 3 or 4 dimensions.")
        batch_labels.append(labels)
        batch_predictions = sess.run([label_name], {input_name: batch_data})[0]
        predictions.append(batch_predictions)

    batch_labels = np.concatenate(batch_labels, axis=0)
    # Concatenate all predictions
    onx_pred = np.concatenate(predictions, axis=0)

    return onx_pred, batch_labels


def count_onnx_parameters(output_dir: str = None,
                          model_path: str = None):
    # Load the ONNX model
    model = onnx.load(model_path)

    model_type = 'quantized' if model_is_quantized(model_path) else 'float'
    # Initialize the total parameter count
    total_params = 0
    
    # Iterate through the model's initializers
    for initializer in model.graph.initializer:
        # Get the shape of the initializer
        shape = initializer.dims
        # Calculate the number of parameters
        num_params = np.prod(shape)
        # Add to the total parameter count
        total_params += num_params
    
    mlflow.log_metric(f"{model_type}_nb_params", total_params)
    log_to_file(output_dir, f"Nb params of {model_type} model : {total_params}")
    print(f"[INFO] : Nb params of {model_type} model : {total_params}")


def model_is_quantized(onnx_model_path:str) -> bool:
    """
    Check if an ONNX model is quantized.

    This function iterates through all the initializers (weights) in the provided
    ONNX model to determine if any of the weights are stored as quantized data types.
    The presence of quantized data types (UINT8, INT8, INT32) among the weights
    indicates that the model is quantized. If only floating-point data types (FLOAT,
    DOUBLE) are found, the model is considered not quantized. If a non-standard data
    type is encountered, it prints a message for further investigation.

    Args:
    - onnx_model_path (str): The ONNX model path.

    Returns:
    - bool: True if the model is quantized, False otherwise.
    """
    if not os.path.isfile(onnx_model_path):
        raise FileNotFoundError('File does not exist!\nCheck the input onnx model path!')
    onnx_model = onnx.ModelProto()
    with open(onnx_model_path, mode='rb') as f:
        content = f.read()
        onnx_model.ParseFromString(content)
    quantized_data_types = {onnx.TensorProto.UINT8, onnx.TensorProto.INT8}
    for initializer in onnx_model.graph.initializer:
        if initializer.data_type in quantized_data_types:
            return True  # Model is quantized
    return False  # No integer initializers found, model is not quantized

