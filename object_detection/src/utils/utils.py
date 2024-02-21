# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import mlflow
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
from tabulate import tabulate
import tensorflow as tf
from keras.utils.layer_utils import count_params
from typing import List, Dict


aspect_ratio_dict = {"fit": "ASPECT_RATIO_FIT",
                     "crop": "ASPECT_RATIO_CROP",
                     "padding": "ASPECT_RATIO_PADDING"}


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
            print("{} physical GPUs, {} logical GPUs".format(len(gpus), len(logical_gpus)))
            print("[INFO] : Setting upper memory limit to {}GBytes on gpu[0]".format(gigabytes))
        except:
            raise RuntimeError("\nVirtual devices must be set before GPUs have been initialized.")


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

    # Check that all the attributes that were used are supported
    used = list(cfg.keys())
    for x in used:
        if x not in expected and x not in optional:
            raise ValueError("\nUnknown or unsupported attribute. Received `{}`{}".format(x, message))

    # Check that all the mandatory attributes are present
    for x in expected:
        if x not in used:
            raise ValueError("\nMissing `{}` attribute{}".format(x, message))


def mlflow_ini(cfg: DictConfig = None) -> None:
    """
    Initializes MLflow tracking with the given configuration.

    Args:
        cfg (dict): A dictionary containing the configuration parameters for MLflow tracking.

    Returns:
        None
    """
    mlflow.set_tracking_uri(cfg['mlflow']['uri'])
    experiment_name = cfg.general.project_name
    mlflow.set_experiment(experiment_name)
    run_name = HydraConfig.get().runtime.output_dir.split(os.sep)[-1]
    mlflow.set_tag("mlflow.runName", run_name)
    params = {"operation_mode": cfg.operation_mode}
    mlflow.log_params(params)
    mlflow.tensorflow.autolog(log_models=False)


def get_config(cfg):
    config_dict = OmegaConf.to_container(cfg)
    configs = DefaultMunch.fromDict(config_dict)
    return configs


def inc_gpu_mode() -> None:
    """
    Increases the GPU memory allocation incrementally as needed.

    Returns:
        None
    """
    physical_gpus = tf.config.experimental.list_physical_devices('GPU')
    if not physical_gpus:
        return

    try:
        for gpu in physical_gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(f"Error setting memory growth: {e}")


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
        if layer_type == "InputLayer":
            layer_shape = model.input.shape
        else:
            layer_shape = layer.output_shape
        is_trainable = True if layer.trainable else False
        num_params = layer.count_params()
        if layer.trainable:
            trainable_layers += 1
        table.append([i, is_trainable, layer.name, layer_type, num_params, layer_shape])

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
