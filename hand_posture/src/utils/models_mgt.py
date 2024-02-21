#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import sys
import os
from pathlib import Path
from typing import Tuple, Dict, Optional, List
import tensorflow as tf
from omegaconf import DictConfig

sys.path.append(os.path.join(os.path.dirname(__file__), '../models'))
from utils import check_attributes
from CNN2D_ST_HandPosture import get_ST_CNN2D_model
from custom_model import get_custom_model


def check_model_support(model_name: str, version: Optional[str] = None,
                        supported_models: Dict = None,
                        message: Optional[str] = None) -> None:
    """
    Check if a model name and version are supported based on a dictionary of supported models and versions.

    Args:
        model_name(str): The name of the model to check.
        version(str): The version of the model to check. May be set to None by the caller.
        supported_models(Dict[str, List[str]]): A dictionary of supported models and their versions.
        message(str): An error message to print.

    Raises:
        NotImplementedError: If the model name or version is not in the list of supported models or versions.
        ValueError: If the version attribute is missing or not applicable for the given model.
    """
    if model_name not in supported_models:
        x = list(supported_models.keys())
        raise ValueError("\nSupported model names are {}. Received {}.{}".format(x, model_name, message))

    model_versions = supported_models[model_name]
    if model_versions:
        # There are different versions of the model.
        if not version:
            # The version is missing.
            raise ValueError("\nMissing `version` attribute for `{}` model.{}".format(model_name, message))
        if version not in model_versions:
            # The version is not a supported version.
            raise ValueError("\nSupported versions for `{}` model are {}. "
                             "Received {}.{}".format(model_name, model_versions, version, message))
    else:
        if version:
            # A version was given but there is no version for this model.
            raise ValueError("\nThe `version` attribute is not applicable "
                             "to '{}' model.{}".format(model_name, message))



def get_model(cfg: DictConfig = None, num_classes: int = None, dropout: float = None,
              section: str = None) -> tf.keras.Model:
    """
    Returns a Keras model object based on the specified configuration and parameters.

    Args:
        cfg (DictConfig): A dictionary containing the configuration for the model.
        num_classes (int): The number of classes for the model.
        dropout (float): The dropout rate for the model.
        section (str): The section of the model to be used.

    Returns:
        tf.keras.Model: A Keras model object based on the specified configuration and parameters.
    """
    # Define the supported models and their versions
    supported_models = {
        'CNN2D_ST_HandPosture': ['v1'],
        'custom': None
    }

    message = "\nPlease check the 'training.model' section of your configuration file."

    # Check if the specified model is supported
    model_name = cfg.name
    model_version = cfg.version
    check_model_support(model_name, version=model_version, supported_models=supported_models, message=message)

    # If the model is CNN2D_ST_HandPosture
    if model_name == "CNN2D_ST_HandPosture":
        check_attributes(cfg, expected=["name", "input_shape", "version"],
                         optional=[],
                         section=section)
        if not dropout:
            dropout = 0
        model = get_ST_CNN2D_model(input_shape=cfg.input_shape, num_classes=num_classes, dropout=dropout)


    # If the model is a custom model
    if model_name == "custom":
        check_attributes(cfg, expected=["name", "input_shape"],
                         optional=[],
                         section=section)
        model = get_custom_model(input_shape=cfg.input_shape, num_classes=num_classes, dropout=dropout)

    return model


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
                        )
        input_shape = tuple(model.input.shape[1:])

    else:
        raise RuntimeError(f"\nUnknown/unsupported model file type. Only .h5 format is supported.\nReceived path {model_path}")

    return model_name, input_shape
