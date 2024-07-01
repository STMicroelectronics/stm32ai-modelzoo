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

from models_utils import transfer_pretrained_weights, check_attribute_value, check_model_support
from cfg_utils import check_attributes
from data_augmentation_layer import DataAugmentationLayer
from mobilenetv1 import get_mobilenetv1
from mobilenetv2 import get_mobilenetv2
from fdmobilenet import get_fdmobilenet
from resnetv1 import get_resnetv1
from squeezenetv11 import get_squeezenetv11
from stmnist import get_stmnist
from st_efficientnet_lc_v1 import get_st_efficientnet_lc_v1
from st_fdmobilenet_v1 import get_st_fdmobilenet_v1
from st_resnet_8_hybrid import get_st_resnet_8_hybrid_v1, get_st_resnet_8_hybrid_v2
from custom_model import get_custom_model


IC_CUSTOM_OBJECTS={'DataAugmentationLayer': DataAugmentationLayer}


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
        'squeezenet': ['v11'],
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


def get_loss(num_classes: int) -> tf.keras.losses:
    """
    Returns the appropriate loss function based on the number of classes in the dataset.

    Args:
        num_classes (int): The number of classes in the dataset.

    Returns:
        tf.keras.losses: The appropriate loss function based on the number of classes in the dataset.
    """
    # We use the sparse version of the categorical crossentropy because
    # this is what we use to load the dataset.
    if num_classes > 2:
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)

    return loss
