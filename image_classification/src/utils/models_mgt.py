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
from onnx import ModelProto
import onnxruntime

sys.path.append(os.path.join(os.path.dirname(__file__), '../models'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../data_augmentation'))

from utils import check_attributes
from data_augmentation_layer import DataAugmentationLayer
from mobilenetv1 import get_mobilenetv1
from mobilenetv2 import get_mobilenetv2
from fdmobilenet import get_fdmobilenet
from resnetv1 import get_resnetv1
from squeezenetv10 import get_squeezenetv10
from squeezenetv11 import get_squeezenetv11
from stmnist import get_stmnist
from st_efficientnet_lc_v1 import get_st_efficientnet_lc_v1
from st_fdmobilenet_v1 import get_st_fdmobilenet_v1
from st_resnet_8_hybrid import get_st_resnet_8_hybrid_v1, get_st_resnet_8_hybrid_v2
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
        raise ValueError("\nSupported values for `{}` attribute are {}. "
                         "Received {}.{}".format(name, values, attribute_value, message))


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
                             "model path {}".format(source_model_path))
        source_model = tf.keras.models.load_model(source_model_path, compile=False)

    message = "\nUnable to transfer to model `{}` ".format(target_model_name)
    message += "the weights from model {}\n".format(source_model_path)
    message += "Models are incompatible (backbones are different)."
    if len(source_model.layers) < end_layer_index + 1:
        raise ValueError(message)
    for i in range(end_layer_index + 1):
        weights = source_model.layers[i].get_weights()
        try:
            target_model.layers[i].set_weights(weights)
        except:
            raise ValueError(message)


def check_mobilenet(cfg: DictConfig = None, section: str =None, message: str = None):
    """
    Utility function that checks the attributes and pretrained weights
    of MobileNet-V1 and MobileNet-V2 models.
    """
    check_attributes(cfg, expected=["name", "version", "alpha", "input_shape"],
                          optional=["pretrained_weights", "pretrained_model_path"],
                          section=section)
    if cfg.pretrained_weights and cfg.pretrained_model_path:
        raise ValueError("\nThe `pretrained_weights` and `pretrained_model_path` attributes "
                         "are mutually exclusive.{}".format(message))
    if cfg.pretrained_weights:
        if cfg.pretrained_weights == "None":
            cfg.pretrained_weights = None
        check_attribute_value(cfg.pretrained_weights, values=[None, "imagenet"], name="pretrained_weights", message=message)


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
        'mobilenet': ['v1', 'v2'],
        'fdmobilenet': None,
        'resnet': ['v1'],
        'squeezenet': ['v10', 'v11'],
        'stmnist': None,
        'st_efficientnet_lc': ['v1'],
        'st_fdmobilenet': ['v1'],
        'st_resnet_8_hybrid': ['v1', 'v2'],
        'custom': None
    }

    message = "\nPlease check the 'training.model' section of your configuration file."

    # Check if the specified model is supported
    model_name = cfg.name
    model_version = cfg.version
    check_model_support(model_name, version=model_version, supported_models=supported_models, message=message)

    # If the model is MobileNet V1
    if model_name == "mobilenet" and model_version == "v1":
        check_mobilenet(cfg, section=section, message=message)
        model = get_mobilenetv1(
                        input_shape=cfg.input_shape,
                        alpha=cfg.alpha,
                        dropout=dropout,
                        pretrained_weights=cfg.pretrained_weights,
                        num_classes=num_classes)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=84,
                        target_model_name="mobilenet_v1")
 
    # If the model is MobileNet V2
    if model_name == "mobilenet" and model_version == "v2":
        check_mobilenet(cfg, section=section, message=message)
        model = get_mobilenetv2(input_shape=cfg.input_shape,
                        alpha=cfg.alpha,
                        dropout=dropout,
                        pretrained_weights=cfg.pretrained_weights,
                        num_classes=num_classes)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=152,
                        target_model_name="mobilenet_v2")
            
    # If the model is FD-MobileNet
    if model_name == "fdmobilenet":
        check_attributes(cfg, expected=["name", "alpha", "input_shape"],
                         optional=["pretrained_model_path"], section=section)
        check_attribute_value(cfg.alpha, values=[0.25, 0.50, 0.75, 1.0], name="alpha", message=message)
        if (cfg.input_shape[0] % 32 > 0) or (cfg.input_shape[1] % 32 > 0):
            raise ValueError("Expecting image width and height to be multiples of 32. "
                             "Received image shape {}".format(cfg.input_shape, message))
        model = get_fdmobilenet(
                        input_shape=cfg.input_shape,
                        alpha=cfg.alpha,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=46,
                        target_model_name="fdmobilenet")

    # If the model is ResNet V1
    if model_name == "resnet" and model_version == "v1":
        check_attributes(cfg, expected=["name", "version", "depth", "input_shape"],
                         optional=["pretrained_model_path"], section=section)
        check_attribute_value(cfg.depth, values=[8, 20, 32], name="depth", message=message)
        model = get_resnetv1(
                        input_shape=cfg.input_shape,
                        depth=cfg.depth,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=24,
                        target_model_name="resnet_v1")

    # If the model is SqueezeNet V1.0
    if model_name == "squeezenet" and model_version == "v10":
        check_attributes(cfg, expected=["name", "version", "input_shape"],
                         optional=["pretrained_model_path"], section=section)
        model = get_squeezenetv10(input_shape=cfg.input_shape, num_classes=num_classes, dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=39,
                        target_model_name="squeezenet_v10")

    # If the model is SqueezeNet V1.1
    if model_name == "squeezenet" and model_version == "v11":
        check_attributes(cfg, expected=["name", "version", "input_shape"],
                         optional=["pretrained_model_path"], section=section)
        model = get_squeezenetv11(input_shape=cfg.input_shape, num_classes=num_classes, dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=58,
                        target_model_name="squeezenet_v11")

    # If the model is ST-MNIST
    if model_name == "stmnist":
        check_attributes(cfg, expected=["name", "input_shape"], section=section)
        model = get_stmnist(input_shape=cfg.input_shape, num_classes=num_classes, dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=14,
                        target_model_name="stmnist")
    
    # If the model is st_efficientnet_lc v1
    if model_name == "st_efficientnet_lc" and model_version == "v1":
        check_attributes(cfg, expected=["name", "version", "input_shape"],
                         optional=["pretrained_model_path"], section=section)                         
        
        if cfg.input_shape[0] != cfg.input_shape[1]:
            raise ValueError("Expecting image width and height to be the same. "
                             "Received image shape {}".format(cfg.input_shape, message))
        if (cfg.input_shape[0] % 32 > 0) or (cfg.input_shape[1] % 32 > 0):
            raise ValueError("Expecting image width and height to be multiples of 32. "
                             "Received image shape {}".format(cfg.input_shape, message))
        model = get_st_efficientnet_lc_v1(
                        input_shape=cfg.input_shape,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=276,
                        target_model_name="st_efficientnet_lc_v1")
    
    # If the model is st_fdmobilenet_v1
    if model_name == "st_fdmobilenet" and model_version == "v1":
        check_attributes(cfg, expected=["name", "version", "input_shape"],
                         optional=["pretrained_model_path"], section=section)                         

        if (cfg.input_shape[0] % 32 > 0) or (cfg.input_shape[1] % 32 > 0):
                raise ValueError('input_shape should be multiple of 32 in both dimensions')
        model = get_st_fdmobilenet_v1(
                        input_shape=cfg.input_shape,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=46,
                        target_model_name="st_fdmobilenet_v1")

    # If the model is st_resnet_8_hybrid_v1
    if model_name == "st_resnet_8_hybrid" and model_version == "v1":
        check_attributes(cfg, expected=["name", "version", "input_shape"],
                         optional=["pretrained_model_path"], section=section)
        if (cfg.input_shape[0] % 32 > 0) or (cfg.input_shape[1] % 32 > 0):
                raise ValueError('input_shape should be multiple of 32 in both dimensions')
        model = get_st_resnet_8_hybrid_v1(
                        input_shape=cfg.input_shape,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=87,
                        target_model_name="st_resnet_8_hybrid_v1")

    # If the model is st_resnet_8_hybrid_v2
    if model_name == "st_resnet_8_hybrid" and model_version == "v2":
        check_attributes(cfg, expected=["name", "version", "input_shape"],
                         optional=["pretrained_model_path"], section=section)
        if (cfg.input_shape[0] % 32 > 0) or (cfg.input_shape[1] % 32 > 0):
                raise ValueError('input_shape should be multiple of 32 in both dimensions')
        model = get_st_resnet_8_hybrid_v2(
                        input_shape=cfg.input_shape,
                        num_classes=num_classes,
                        dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=87,
                        target_model_name="st_resnet_8_hybrid_v2")

    # If the model is a custom model
    if model_name == "custom":
        check_attributes(cfg, expected=["name", "input_shape"],
                         optional=["pretrained_model_path"],
                         section=section)
        model = get_custom_model(input_shape=cfg.input_shape, num_classes=num_classes, dropout=dropout)
        if cfg.pretrained_model_path:
            transfer_pretrained_weights(
                        model,
                        source_model_path=cfg.pretrained_model_path,
                        end_layer_index=10,
                        target_model_name="custom")

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
                        custom_objects={
                            'DataAugmentationLayer': DataAugmentationLayer
                        })
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
