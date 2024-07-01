# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from timeit import default_timer as timer
from datetime import timedelta
from typing import Tuple, List, Dict, Optional

import mlflow
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf


def set_frozen_layers(model: tf.keras.Model, frozen_layers: str = None) -> None:
    """
    This function freezes (makes non-trainable) the layers that are 
    specified by the `frozen_layers` attribute. If `frozen_layers` is `None`,
    then all layers in the model are made trainable.
    The indices are specified using the same syntax as in Python:
       2                      layer 2 (3rd layer from network input)
       (2)                    layer 2
       (4:8)                  layers 4 to 7
       (0:-1)                 layers 0 to before last
       (7:13, 16, 20:28, -1)  layers 7 to 12, 16, 20 to 27, last
    There can be any number of index slices in the attribute.
    The attribute must be between parentheses. Using square brackets
    would make it an array and it could be changed by the YAML loader.
      not be left unchanged by the

    Arguments:
        model (tf.keras.Model): the model.
        frozen_layers (str): the indices of the layers to freeze. If `None`, all layers are made trainable.

    Returns:
        None
    """
    if frozen_layers == 'None':
        # Train the whole model
        model.trainable = True
        return
    
    frozen_layers = str(frozen_layers)
    frozen_layers = frozen_layers.replace(" ", "")
    frozen_slices = frozen_layers[1:-1] if frozen_layers[0] == "(" else frozen_layers
    
    num_layers = len(model.layers)
    indices = np.arange(num_layers)
    frozen_indices = np.zeros(num_layers, dtype=bool)
    for slice_ in frozen_slices.split(','):
        try:
            i = eval("indices[" + str(slice_) + "]")
        except ValueError as val_err:
            raise ValueError("\nInvalid syntax for `frozen_layers` attribute\nLayer index slices "
                             f"should follow the Python syntax. Received {frozen_layers}\nPlease check the "
                             "'training' section of your configuration file.") from val_err
        frozen_indices[i] = True

    # Freeze layers
    model.trainable = True
    num_trainable = num_layers
    for i in range(num_layers):
        if frozen_indices[i]:
            num_trainable -= 1
            model.layers[i].trainable = False


def set_dropout_rate(model: tf.keras.Model, dropout_rate: float = None) -> None:
    """
    This function sets the dropout rate of the dropout layer if 
    the `dropout`attribute was used in the 'training' section of
    the config file.
    An error is thrown if:
    - The `dropout` attribute was used but the model does not
      include a dropout layer.
    - The model includes a dropout layer but the `dropout`attribute
      was not used to specify a rate.

    Arguments:
        model (tf.keras.Model): the model.
        dropout_rate (float): the dropout rate to set on the dropout layer.
        
    Returns:
        None
    """
    found_layer = False
    for layer in model.layers:
        layer_type = layer.__class__.__name__
        if layer_type == "Dropout":
            found_layer = True
    
    if found_layer:
        # The dropout rate must be specified.
        if not dropout_rate:
            raise ValueError("\nThe model includes a dropout layer.\nPlease use the 'training.dropout' "
                             "attribute in your configuration file to specify a dropout rate")
        for layer in model.layers:
            layer_type = layer.__class__.__name__
            if layer_type == "Dropout":
                layer.rate = dropout_rate
        print("[INFO] : Set dropout rate to", dropout_rate)
    else:
        # The dropout rate can't be applied.
        if dropout_rate:
            raise ValueError("\nUnable to set the dropout rate specified by the 'training.dropout' "
                             "attribute in the configuration file\nThe model does not include "
                             "a dropout layer.")


def get_optimizer(cfg: DictConfig) -> tf.keras.optimizers:
    """
    This function creates a Keras optimizer from the 'optimizer' section
    of the config file.
    The optimizer name, attributes and values used in the config file
    are used to create a string that is the call to the Keras optimizer
    with its arguments. Then, the string is evaluated. If the evaluation
    succeeds, the optimizer object is returned. If it fails, an error
    is thrown with a message that tells the user that the name and/or
    arguments of the optimizer are incorrect.

    Arguments:
        cfg (DictConfig): dictionary containing the 'optimizer' section of
                          the configuration file.
    Returns:
        tf.keras.optimizers: the Keras optimizer object.
    """
    message = "\nPlease check the 'training.optimizer' section of your configuration file."
    if type(cfg) != DefaultMunch:
        raise ValueError(f"\nInvalid syntax for optimizer{message}")
    optimizer_name = list(cfg.keys())[0]
    optimizer_args = cfg[optimizer_name]

    # Get the optimizer
    if not optimizer_args:
        # The optimizer has no arguments.
        optimizer_text = f"tf.keras.optimizers.{optimizer_name}()"
    else:
        if type(optimizer_args) != DefaultMunch:
            raise ValueError(f"\nInvalid syntax for `{optimizer_name}` optimizer arguments{message}")
        text = f"tf.keras.optimizers.{optimizer_name}("
        # Collect the arguments
        for k, v in optimizer_args.items():
            if type(v) == str:
                text += f'{k}=r"{v}", '
            else:
                text += f'{k}={v}, '
        optimizer_text = text[:-2] + ')'

    try:
        optimizer = eval(optimizer_text)
    except ValueError as val_err:
        raise ValueError(f"\nThe optimizer name `{optimizer_name}` is unknown or,"
                         f"the arguments are invalid, got:\n{optimizer_text}.{message}") from val_err
    return optimizer

