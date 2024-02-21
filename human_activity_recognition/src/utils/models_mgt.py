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
from typing import Tuple, Dict, Optional, List
import numpy as np
import tensorflow as tf
from omegaconf import DictConfig
from onnx import ModelProto
import onnxruntime

sys.path.append(os.path.join(os.path.dirname(__file__), '../models'))
from utils import check_attributes
from ign import get_ign
from gmp import get_gmp
from custom_model import get_custom_model


def check_attribute_value(attribute_value: str, values: List[str] = None,
                          name: str = None, message: str = None) -> None:
    """
    Check if an attribute value is valid based on a list of supported values.
    Args:
        attribute_value(str): The value of the attribute to check.
        values(List[str]): A list of supported values.
        name(str): The name of the attribute being checked.
        message(str): A message to print if the attribute is not supported.
    Raises:
        ValueError: If the attribute value is not in the list of supported values.
    """
    if attribute_value not in values:
        raise ValueError(f"\nSupported values for `{name}` attribute are {values}. "
                         f"Received {attribute_value}.{message}")


def check_model_support(model_name: str, supported_models: Dict = None,
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
        x = list(supported_models)
        raise ValueError(f"\nSupported model names are {x}. Received '{model_name}'.{message}")


def transfer_pretrained_weights(target_model: tf.keras.Model, source_model_path: str = None,
                                end_layer_index: int = None, target_model_name: str = None) -> None:
    """
    Copy the weights of a source model to a target model. Only the backbone weights
    are copied as the two models can have different classifiers.

    Args:
        target_model (tf.keras.Model): The target model.
        source_model_path (str): Path to the source model file (h5 file).
        end_layer_index (int): Index of the last backbone layer (the first layer of the model has index 0).
        target_model_name (str): The name of the target model.

    Raises:
        ValueError: The source model file cannot be found.
        ValueError: The two models are incompatible because they have different backbones.
    """
    if source_model_path:
        if not os.path.isfile(source_model_path):
            raise ValueError("Unable to find pretrained model file.\nReceived "
                             f"model path {source_model_path}")
        source_model = tf.keras.models.load_model(source_model_path, compile=False)

    message = f"\nUnable to transfer to model `{target_model_name}`"
    message += f"the weights from model {source_model_path}\n"
    message += "Models are incompatible (backbones are different)."
    if len(source_model.layers) < end_layer_index + 1:
        raise ValueError(message)
    for i in range(end_layer_index + 1):
        weights = source_model.layers[i].get_weights()
        try:
            target_model.layers[i].set_weights(weights)
        except ValueError as error:
            raise message from error


def get_keras_model(cfg: DictConfig = None,
                    num_classes: int = None,
                    dropout: float = None,
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
        'ign',
        'gmp',
        'custom'
    }

    message = "\nPlease check the 'training.model' section of your configuration file."

    # Check if the specified model is supported
    model_name = cfg.name
    check_model_support(model_name,
                        supported_models=supported_models,
                        message=message)

    # if model name is "ign"
    if model_name.lower() == "ign":
        check_attributes(cfg, expected=["name", "input_shape"],
                         optional=["pretrained_model_path", "dropout"], section=section)
        if cfg.input_shape[0] < 20:
            raise ValueError("Expecting window length to be at least 20 samples. "
                             f"Received window length {cfg.input_shape[0]}{message}")
        model = get_ign(input_shape=cfg.input_shape,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=-1,
                        target_model_name="ign")
    # if model name is "ign"
    elif model_name.lower() == "gmp":
        check_attributes(cfg, expected=["name", "input_shape"],
                         optional=["pretrained_model_path", "dropout"])
        if cfg.input_shape[0] < 20:
            raise ValueError("Expecting window length to be at least 20 samples. "
                             f"Received window length {cfg.input_shape[0]}{message}")
        model = get_gmp(input_shape=cfg.input_shape,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=-1,
                        target_model_name="gmp")

    elif model_name == "custom":
        check_attributes(cfg, expected=["name", "input_shape"],
                         optional=["pretrained_model_path", "dropout"],
                         section=section)
        model = get_custom_model(input_shape=cfg.input_shape,
                                 num_classes=num_classes,
                                 dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=-1,
                        target_model_name="custom")
    else:
        raise ValueError("Unspported model configurations used."
                         "Expected model names are `ign`, `gmp`, or `custom`.\n"
                         f"provided value is: {cfg.name}", message)

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
        model = tf.keras.models.load_model(model_path)
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
        except RuntimeError as error:
            raise RuntimeError("\nUnable to extract input shape from .tflite model file\n"
                               f"Received path {model_path}") from error

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
        except RuntimeError as error:
            raise RuntimeError("\nUnable to extract input shape from .onnx model file\n"
                               f"Received path {model_path}") from error

    else:
        raise RuntimeError(f"\nUnknown/unsupported model file type.\nExpected `.tflite`, `.h5`, or `.onnx`."
                           f"\nReceived path {model_path.split('.')[-1]}")

    return model_name, input_shape
