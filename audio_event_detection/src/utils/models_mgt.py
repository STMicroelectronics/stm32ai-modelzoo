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
import re
from typing import Tuple, Dict, Optional, List
import tensorflow as tf
from onnx import ModelProto
import onnxruntime
from pathlib import Path
from tensorflow.keras.models import Model
from tensorflow.data import Dataset
from omegaconf import OmegaConf, DictConfig, open_dict

sys.path.append(os.path.join(os.path.dirname(__file__), '../models/yamnet'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../models/miniresnet'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../models/miniresnetv2'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../models'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../data_augmentation'))
from utils import check_attributes
from data_augmentation_layers_audio import SpecAugment, VolumeAugment
import custom_model
import yamnet
import miniresnet
import miniresnetv2


def check_attribute_value(attribute_value: str, values: List[str] = None,
                          name: str = None, message: str = None) -> None: #OK
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


def check_model_support(model_name: str, version: Optional[str] = None,
                        supported_models: Dict = None,
                        message: Optional[str] = None) -> None: #OK
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


def transfer_pretrained_weights(target_model, source_model_path=None,
                                end_layer_index=None, target_model_name=None) -> None:
    # NOTE : Unused in AED for now.
    # When it's ready to use, call it after loading model in get_model.
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


def get_model(cfg: DictConfig = None, num_classes: int = None, dropout: float = None,
              fine_tune: bool = None, use_garbage_class: bool = None,
              multi_label: bool = None, pretrained_weights: bool = None,
              kernel_regularizer=None, activity_regularizer=None,
              patch_length: int = None, n_mels: int = None,
              section: str = None) -> tf.keras.Model: # OK
    """
    Returns a Keras model object based on the specified configuration and parameters.

    Args:
        cfg (DictConfig): A dictionary containing the configuration for the model.
        num_classes (int): The number of classes for the model.
        dropout (float): The dropout rate for the model.
        fine_tune : bool, if True and pretrained_weights is True, all model weights are unfrozen.
            If pretrained_weights is False, does nothing.
        use_garbage_class: bool, if True an additional neuron is added to the classification head
            of the model to accomodate for the "garbage" class.
        multi_label : bool, set to True if output is multi-label. 
            If True, activation function is a sigmoïd,
            if False it is a softmax instead.
        pretrained_weights : bool, if True use ST-provided pretrained weights
            NOTE : Will be changed to str to allow for loading of user-provided pretrained weights
        kernel_regularizer : tf.keras.Regularizer, kernel regularizer applied to the classification head.
            NOTE : Currently not parametrable by the user.
        activity_regularizer : tf.keras.Regularizer, activity regularizer applied to the classification head.
            NOTE : Currently not parametrable by the user.
        patch_length : int, length of input patches. Only used for sanity check.
        n_mels : int, n° of mels in input patches. Only used for sanity check.
        section (str): The section of the model to be used.

    Returns:
        tf.keras.Model: A Keras model object based on the specified configuration and parameters.
    """

    # Define the supported models and their versions
    supported_models = {
        'yamnet': None,
        'miniresnet': ['v1', 'v2'],
        'custom': None
    }

    message = "\nPlease check the 'training.model' section of your configuration file."

    # Check if the specified model is supported
    model_name = cfg.name
    model_version = cfg.version
    check_model_support(model_name, version=model_version, supported_models=supported_models, message=message)

    # Check if specified model allows using pretrained weights

    models_with_pretrained_weights = ['yamnet', 'miniresnet']
    if model_name not in models_with_pretrained_weights and pretrained_weights:
        raise ValueError(f"No pretrained weights are available for model {model_name}")
    # If the model is yamnet
    if model_name == "yamnet":
        check_attributes(cfg, expected=["name", "embedding_size", "input_shape", "pretrained_weights"], section=section)
        model = yamnet.get_model(n_classes=num_classes,
                embedding_size=cfg.embedding_size,
                fine_tune=fine_tune,
                use_garbage_class=use_garbage_class,
                dropout=dropout,
                multi_label=multi_label,
                kernel_regularizer=kernel_regularizer,
                activity_regularizer=activity_regularizer,
                patch_length=patch_length,
                n_mels=n_mels,
                pretrained_weights=pretrained_weights
                )

    # If the model is MiniResNet
    elif model_name == "miniresnet" and model_version == "v1":
        check_attributes(cfg, expected=["name", "version", "n_stacks", "input_shape",
                                        "pooling", "pretrained_weights"], section=section)
        model = miniresnet.get_model(input_shape=cfg.input_shape,
                n_stacks=cfg.n_stacks,
                n_classes=num_classes,
                pooling=cfg.pooling,
                use_garbage_class=use_garbage_class,
                multi_label=multi_label,
                dropout=dropout,
                pretrained_weights=pretrained_weights,
                fine_tune=fine_tune,
                kernel_regularizer=kernel_regularizer,
                activity_regularizer=activity_regularizer)

    # If the model is MiniResNetv2
    elif model_name == "miniresnet" and model_version == "v2":
        check_attributes(cfg, expected=["name", "version", "n_stacks", "input_shape",
                                            "pooling", "pretrained_weights"], section=section)
        model = miniresnetv2.get_model(input_shape=cfg.input_shape,
                n_stacks=cfg.n_stacks,
                n_classes=num_classes,
                pooling=cfg.pooling,
                use_garbage_class=use_garbage_class,
                multi_label=multi_label,
                dropout=dropout,
                pretrained_weights=pretrained_weights,
                fine_tune=fine_tune,
                kernel_regularizer=kernel_regularizer,
                activity_regularizer=activity_regularizer)

    # If the model is a custom model
    elif model_name == "custom":
        model = custom_model.get_model(input_shape=cfg.input_shape, num_classes=num_classes, dropout=dropout)

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
                            'SpecAugment': SpecAugment,
                            'VolumeAugment': VolumeAugment,
                        })
        input_shape = tuple(model.input.shape[1:])

    elif file_extension == ".tflite":
        #try:
            # Load the tflite model
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        # Get the input details
        input_details = interpreter.get_input_details()
        input_shape = input_details[0]['shape']
        input_shape = tuple(input_shape)[-3:]
        # except Exception as e:
        #     raise RuntimeError("\nUnable to extract input shape from .tflite model file\n"
        #                        f"Received path {model_path}"
        #                        f"Recieved exception {e}")

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

