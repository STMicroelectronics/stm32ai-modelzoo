# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import numpy as np
import os
import onnx


def predict_onnx(sess: onnx.ModelProto, data: np.ndarray) -> np.ndarray:
    """
    Runs inference on an ONNX model.

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

