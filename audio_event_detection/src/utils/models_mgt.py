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
from typing import Tuple, Dict, Optional, List
import tensorflow as tf
from onnx import ModelProto
from pathlib import Path
from omegaconf import OmegaConf, DictConfig, open_dict

from cfg_utils import check_attributes
from models_utils import check_model_support
from data_augmentation_layers_audio import SpecAugment, VolumeAugment
import custom_model
import yamnet
import miniresnet
import miniresnetv2


AED_CUSTOM_OBJECTS={'SpecAugment': SpecAugment,
                    'VolumeAugment': VolumeAugment,
                   }

def get_model(cfg: DictConfig = None, num_classes: int = None, dropout: float = None,
              fine_tune: bool = None, use_garbage_class: bool = None,
              multi_label: bool = None, pretrained_weights: bool = None,
              kernel_regularizer=None, activity_regularizer=None,
              patch_length: int = None, n_mels: int = None,
              section: str = None) -> tf.keras.Model:
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


def get_loss(multi_label:bool) -> tf.keras.losses:
    """
    Returns the appropriate loss function based on the number of classes in the dataset.

    Args:
        multi_label : bool, set to True if the dataset is multi-label.

    Returns:
       loss:  The appropriate keras loss function based on the number of classes in the dataset.
    """
    if multi_label:
        raise NotImplementedError("Multi-label classification not implemented yet, but will be in a future update.")
        # Remove the error once it's implemented
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)
        
    return loss
    