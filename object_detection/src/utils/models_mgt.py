#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
from pathlib import Path
import tensorflow as tf
from onnx import ModelProto
import onnxruntime
from typing import Tuple

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../evaluation'))
sys.path.append(os.path.abspath('../../../common'))
sys.path.append(os.path.abspath('../training'))
from anchor_boxes_utils import gen_anchors
from metrics_utils import relu6
from loss import ssd_focal_loss


def get_model_name_and_its_input_shape(model_path: str = None) -> Tuple:
    """
    Load a model from a given file path and return the model name and
    its input shape. Supported model formats are .h5, .tflite and .onnx.
    The basename of the model file is used as the model name. The input
    shape is extracted from the model.

    Args:
        model_path(str): A path to an .h5, .tflite or .onnx model file.

    Returns:
        Tuple: A tuple containing the loaded model name and its input shape.
               The input shape is a tuple of length 3.
    Raises:
        ValueError: If the model file extension is not '.h5' or '.tflite'.
        RuntimeError: If the input shape of the model cannot be found.
    """

    # We use the file basename as the model name.
    model_name = Path(model_path).stem

    file_extension = Path(model_path).suffix
    if file_extension == ".h5":
        # When we resume a training, the model includes the preprocessing layers
        # (augmented model). Therefore, we need to declare the custom data
        # augmentation layer as a custom object to be able to load the model.
        model = tf.keras.models.load_model(
                        model_path,
                        compile=False)
        input_shape = tuple(model.input.shape[1:])

    elif file_extension == ".tflite":
        try:
            # Load the tflite model
            interpreter = tf.lite.Interpreter(model_path=model_path)
            interpreter.allocate_tensors()
            # Get the input details
            input_details = interpreter.get_input_details()
            input_shape = input_details[0]['shape']
            input_shape = tuple(input_shape)[-3:]
        except:
            raise RuntimeError("\nUnable to extract input shape from .tflite model file\n"
                               f"Received path {model_path}")

    elif file_extension == ".onnx":
        try:
            # Load the model
            onx = ModelProto()
            with open(model_path, "rb") as f:
                content = f.read()
                onx.ParseFromString(content)
            sess = onnxruntime.InferenceSession(model_path)
            # Get the model input shape
            input_shape = sess.get_inputs()[0].shape
            input_shape = tuple(input_shape)[-3:]
        except:
            raise RuntimeError("\nUnable to extract input shape from .onnx model file\n"
                               f"Received path {model_path}")

    else:
        raise RuntimeError(f"\nUnknown/unsupported model file type.\nReceived path {model_path}")

    return model_name, input_shape
