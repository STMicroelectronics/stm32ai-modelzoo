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

from cfg_utils import check_attributes
from models_utils import transfer_pretrained_weights, check_model_support
from ign import get_ign
from gmp import get_gmp
from custom_model import get_custom_model


def get_model(cfg: DictConfig = None,
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
        'ign' : None,
        'gmp' : None,
        'custom' : None
    }

    message = "\nPlease check the 'training.model' section of your configuration file."

    # Check if the specified model is supported
    model_name = cfg.name
    model_version = cfg.version
    check_model_support(model_name,
                        version=model_version, 
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


def get_loss(num_classes: int) -> tf.keras.losses:
    """
    Returns the appropriate loss function based on the number of classes in the dataset.

    Args:
        num_classes (int): The number of classes in the dataset.

    Returns:
        tf.keras.losses: The appropriate loss function based on the
          number of classes in the dataset.
    """
    # We use the sparse version of the categorical crossentropy because
    # this is what we use to load the dataset.
    if num_classes > 2:
        # loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)

    return loss
