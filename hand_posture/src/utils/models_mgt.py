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

from cfg_utils import check_attributes
from models_utils import check_model_support
from CNN2D_ST_HandPosture import get_ST_CNN2D_model
from custom_model import get_custom_model


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
    check_model_support(model_name, 
                        version=model_version, 
                        supported_models=supported_models, 
                        message=message)

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


def get_loss(num_classes: int) -> tf.keras.losses:
    """
    Returns the appropriate loss function based on the number of classes in the dataset.

    Args:
        num_classes (int): The number of classes in the dataset.

    Returns:
        tf.keras.losses: The appropriate loss function based on the number of classes in the dataset.
    """
    if num_classes > 2:
        # loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)
    return loss
