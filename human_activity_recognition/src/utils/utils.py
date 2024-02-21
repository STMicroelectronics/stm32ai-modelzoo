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

import os
from pathlib import Path
import mlflow
from tabulate import tabulate
from typing import Dict, List
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import tensorflow as tf
from keras.utils.layer_utils import count_params


def set_gpu_memory_limit(gigabytes):
    """
     Sets the upper memory limit for the first GPU to the specified number of gigabytes.

     Args:
         gigabytes (int): The number of gigabytes to set as the upper memory limit.

     Raises:
         RuntimeError: If virtual devices have not been set before GPUs are initialized.

     Returns:
         None
     """
    # GPU memory usage configuration
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.set_logical_device_configuration(
                gpus[0],
                [tf.config.LogicalDeviceConfiguration(memory_limit=1024 * gigabytes)])
            logical_gpus = tf.config.list_logical_devices('GPU')
            print(f"{len(gpus)} physical GPUs, {len(logical_gpus)} logical GPUs")
            print(f"[INFO] : Setting upper memory limit to {gigabytes} GBytes on gpu[0]")
        except:
            raise RuntimeError("\nVirtual devices must be set before GPUs have been initialized.")


def get_random_seed(cfg: DictConfig = None):
    """
    Returns a random seed based on the configuration file.

    Args:
        cfg (DictConfig): The configuration object.

    Returns:
        int or None: The random seed. If no seed is set in the configuration file, returns 0.
    """

    if "global_seed" in cfg.general:
        seed = cfg.general.global_seed
        if seed == "None":
            seed = None
        else:
            seed = int(seed)
    else:
        seed = 0
    return seed


def check_training_determinism(model: tf.keras.Model, sample_ds: tf.data.Dataset):
    """
    Check if there are operations that can rise exceptions during training.

    Args:
        model (tf.keras.Model): A keras model.
    
    Returns:
        valid_training (bool): True if the training raise no exception.
    """
    valid_training = True
    x_sample, y_sample = next(iter(sample_ds))

    try:
        with tf.GradientTape() as g:
            y = model(x_sample, training=True)
            loss = model.loss(y_sample, y)
        _ = g.gradient(loss, model.trainable_variables)
        
    except Exception as error:
        print(f"[WARN] {error}")
        valid_training = False

    return valid_training


def check_attributes(cfg: Dict, expected: List[str] = None, optional: List[str] = [], section: str = None) -> None:
    """
    Checks that all the expected attributes are present in the configuration dictionary and that
    there are no unknown attributes. Optional attributes may also be present.

    Args:
        cfg (dict): The configuration dictionary.
        expected (list): A list of expected (required) attributes.
        optional (list, optional): A list of optional attributes. Defaults to [].
        section (str, optional): The name of the config file section to check. Defaults to None.

    Raises:
        ValueError: If an unknown or unsupported attribute is found or if a required attribute is missing.

    Returns:
        None
    """

    if section is not None:
        message = "\nPlease check the '{}' section of your configuration file.".format(section)
    else:
        message = "\nPlease check your configuration file."

    if cfg is not None:
        if not isinstance(cfg, DefaultMunch):
            raise ValueError(f"Expecting an attribute. Received {cfg}{message}")
        # Check that each attribute name is legal.
        for attr in cfg.keys():
            if (attr not in expected) and (attr not in optional):
                raise ValueError(f"\nUnknown or unsupported attribute. Received `{attr}`{message}")
        # Get the list of used attributes
        used = list(cfg.keys())
    else:
        used = []

    # Check that all the mandatory attributes are present.
    for attr in expected:
        if attr not in used:
            raise ValueError(f"\nMissing `{attr}` attribute{message}")
        if cfg[attr] is None:
            raise ValueError(f"\nMissing a value for attribute `{attr}`{message}")
        

def model_summary(model):
    """
    This function displays a model summary. It is similar to a Keras
    model summary with the additional information:
    - Indices of layers
    - Trainable/non-trainable status of layers
    - Total number of layers
    - Number of trainable layers
    - Number of non-trainable layers
    """
    # Create the summary table
    num_layers = len(model.layers)
    trainable_layers = 0
    table = []
    for i, layer in enumerate(model.layers):
        layer_type = layer.__class__.__name__
        is_trainable = True if layer.trainable else False
        num_params = layer.count_params()
        if layer.trainable:
            trainable_layers += 1
        table.append([i, is_trainable, layer.name, layer_type, num_params, layer.output_shape[1:]])

    # Display the table
    print(108 * '=')
    print("  Model:", model.name)
    print(108 * '=')
    print(tabulate(table, headers=["Layer index", "Trainable", "Name", "Type", "Params#", "Output shape"]))
    print(108 * '-')
    print("Total params:", model.count_params())
    print("Trainable params: ", count_params(model.trainable_weights))
    print("Non-trainable params: ", count_params(model.non_trainable_weights))
    print(108 * '-')
    print("Total layers:", num_layers)
    print("Trainable layers:", trainable_layers)
    print("Non-trainable layers:", num_layers - trainable_layers)
    print(108 * '=')


def mlflow_ini(cfg: DictConfig = None) -> None:
    """
    Initializes MLflow tracking with the given configuration.

    Args:
        cfg (dict): A dictionary containing the configuration parameters for MLflow tracking.

    Returns:
        None
    """
    mlflow.set_tracking_uri(cfg.mlflow.uri)
    experiment_name = cfg.general.project_name
    mlflow.set_experiment(experiment_name)
    run_name = HydraConfig.get().runtime.output_dir.split(os.sep)[-1]
    mlflow.set_tag("mlflow.runName", run_name)
    params = {"operation_mode": cfg.operation_mode}
    mlflow.log_params(params)
    mlflow.tensorflow.autolog(log_models=False)
