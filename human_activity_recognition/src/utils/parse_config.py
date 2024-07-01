#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
from pathlib import Path
import re
from hydra.core.hydra_config import HydraConfig
from cfg_utils import postprocess_config_dict, check_config_attributes, parse_tools_section, parse_benchmarking_section, \
                      parse_mlflow_section, parse_top_level, parse_general_section, parse_training_section, \
                      parse_deployment_section, check_hardware_type
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
import tensorflow as tf
from typing import Dict, List


def parse_dataset_section(cfg: DictConfig, mode: str = None, mode_groups: DictConfig = None) -> None:
    '''
    parses the dataset section from the configuration dictionary
    args:
        cfg (DictConfig): configuraiton dictionary
        mode (str): operation mode
        mode_groups (DictConfig): configuration dictionary
    '''

    legal = ["name", "class_names", "training_path", "validation_path",
             "validation_split", "test_path", "test_split", "seed"]

    required = []
    one_or_more = []
    if mode in mode_groups.training:
        required += ["training_path",]
    elif mode in mode_groups.evaluation:
        one_or_more += ["training_path", "test_path"]

    check_config_attributes(cfg, specs={"legal": legal,
                            "all": required, "one_or_more": one_or_more},
                            section="dataset")

    # Set default values of missing optional attributes
    if not cfg.name:
        cfg.name = "<unnamed>"
    if not cfg.validation_split:
        cfg.validation_split = 0.2
    if not cfg.test_split:
        cfg.validation_split = 0.25
    cfg.seed = cfg.seed if cfg.seed else 123

    # validate the class names
    if cfg.class_names and cfg.class_names != '':
        if cfg.name.lower() == "wisdm":
            if not(cfg.class_names == ["Jogging", "Stationary", "Stairs", "Walking"]):
                raise ValueError(f"\nThe value of `class_names` for `wisdm` should be {['Jogging', 'Stationary', 'Stairs', 'Walking']}\n"
                                "Please check the 'dataset.class_names' section of your configuration file.")
        elif cfg.name.lower() == "mobility_v1":    
            if not(cfg.class_names == ["Stationary", "Walking", "Jogging", "Biking"]):
                raise ValueError(f"\nThe value of `class_names` for `mobility_v1` should be {['Stationary', 'Walking', 'Jogging', 'Biking']}\n"
                                "Please check the 'dataset.class_names' section of your configuration file.")
    # # Sort the class names if they were provided
    # if cfg.class_names:
    #     cfg.class_names = sorted(cfg.class_names)

    # Check the value of validation_split if it is set
    if cfg.validation_split:
        split = cfg.validation_split
        if split <= 0.0 or split >= 1.0:
            raise ValueError(f"\nThe value of `validation_split` should be > 0 and < 1. Received {split}\n"
                                "Please check the 'dataset' section of your configuration file.")

    dataset_paths = []
    # Datasets used in a training
    if mode in mode_groups.training:
        dataset_paths += [(cfg.training_path, "training"),]
        if cfg.validation_path:
            dataset_paths += [(cfg.validation_path, "validation"),]
        if cfg.test_path:
            dataset_paths += [(cfg.test_path, "test"),]

    # Datasets used in an evaluation
    if mode in mode_groups.evaluation:
        if cfg.test_path:
            dataset_paths += [(cfg.test_path, "test"),]
        elif cfg.validation_path:
            dataset_paths += [(cfg.validation_path, "validation"),]
        else:
            dataset_paths += [(cfg.training_path, "training"),]

    # Check that the dataset root directories exist
    for path, name in dataset_paths:
        message = f"\nPlease check the 'dataset.{name}_path' attribute in your configuration file."
        if path and not os.path.isfile(path):
            raise FileNotFoundError(f"\nUnable to find the root directory of the {name} set\n"
                                    f"Received path: {path}{message}")


def parse_preprocessing_section(cfg: DictConfig) -> None:
    '''
    parses the preprocessing section of the configuration dictionary
    args:
        cfg (DictConfig): configuration dictionary containing the preprocessing info
    '''

    legal = ["gravity_rot_sup", "normalization"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="preprocessing")


def check_dataset_contents(cfg: DictConfig) -> None:
    '''
    checks if the dataset paths are provided and are correct
    args:
        cfg (DictConfig): 'dataset' section of the configuration file
    '''
    if cfg.name.lower() == 'wisdm':
        if not cfg.training_path and os.path.isfile(cfg.training_path):
            raise ValueError("training_path is not provided.\n"
                             "Please check the cfg.dataset section")
    if cfg.name.lower() == 'mobility_v1':
        if not (cfg.training_path and cfg.test_path and
               os.path.isfile(cfg.training_path) and os.path.isfile(cfg.test_path)):
            raise ValueError("valid values for training_path or test_path are missing.\n"
                             "Please check the cfg.dataset section")

def get_class_names(dataset_name: str) -> List:
    '''
    returns the a list of class names in the dataset
    args:
        dataset_name (str): name of the dataset
    returns:
        list[str]: list of the class names
    '''
    # Look for a dataset that can be used to find the class names
    if dataset_name.lower() == 'wisdm':
        return ["Jogging", "Stationary", "Stairs", "Walking"]
    else:
        return ["Stationary", "Walking", "Jogging", "Biking"]

def get_config(config_data: DictConfig) -> DefaultMunch:
    """
    Converts the configuration data, performs some checks and reformats
    some sections so that they are easier to use later on.

    Args:
        config_data (DictConfig): dictionary containing the entire configuration file.

    Returns:
        DefaultMunch: The configuration object.
    """

    config_dict = OmegaConf.to_container(config_data)

    # Restore booleans, numerical expressions and tuples
    # Expand environment variables
    postprocess_config_dict(config_dict)

    # Top level section parsing
    cfg = DefaultMunch.fromDict(config_dict)
    mode_groups = DefaultMunch.fromDict({
        "training": ["training", "chain_tb"],
        "evaluation": ["evaluation"],
        "benchmarking": ["benchmarking", "chain_tb"],
        "deployment": ["deployment"],
        "quantization": []
    })
    mode_choices = ["training", "evaluation", "deployment", "benchmarking", "chain_tb"]
    legal = ["general", "operation_mode", "dataset", "preprocessing", "training",
             "prediction", "tools", "benchmarking", "deployment", "mlflow"]
    parse_top_level(cfg, 
                    mode_groups=mode_groups,
                    mode_choices=mode_choices,
                    legal=legal)
    print(f"[INFO] : Running `{cfg.operation_mode}` operation mode")

    # General section parsing
    if not cfg.general:
        cfg.general = DefaultMunch.fromDict({"project_name": "human_activity_recognition"})
    legal = ["project_name", "model_path", "logs_dir", "saved_models_dir", "deterministic_ops",
            "display_figures", "global_seed", "gpu_memory_limit", "num_threads_tflite"]
    required = []
    parse_general_section(cfg.general, 
                          mode=cfg.operation_mode, 
                          mode_groups=mode_groups,
                          legal=legal,
                          required=required)

    # Select hardware_type from yaml information
    check_hardware_type(cfg,
                        mode_groups)

    # Dataset section parsing
    if not cfg.dataset:
        cfg.dataset = DefaultMunch.fromDict({})
    parse_dataset_section(cfg.dataset, 
                          mode=cfg.operation_mode, 
                          mode_groups=mode_groups)
    
    # Preprocessing section parsing
    if not cfg.operation_mode in mode_groups.benchmarking:
        parse_preprocessing_section(cfg.preprocessing)

    # Training section parsing
    if cfg.operation_mode in mode_groups.training:
        model_path_used = bool(cfg.general.model_path)
        model_type_used = bool(cfg.general.model_type)
        legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
                 "callbacks", "resume_training_from", "trained_model_path"]
        parse_training_section(cfg.training, 
                               model_path_used=model_path_used, 
                               model_type_used=model_type_used,
                               legal=legal)

    # Tools section parsing
    if cfg.operation_mode in (mode_groups.benchmarking + mode_groups.deployment):
        parse_tools_section(cfg.tools, 
                            cfg.operation_mode,
                            cfg.hardware_type)

    # Benchmarking section parsing
    if cfg.operation_mode in mode_groups.benchmarking:
        parse_benchmarking_section(cfg.benchmarking)
        if cfg.hardware_type == "MPU" :
            if not (cfg.tools.stm32ai.on_cloud):
                print("Target selected for benchmark :", cfg.benchmarking.board)
                print("Offline benchmarking for MPU is not yet available please use online benchmarking")
                exit(1)

    # Deployment section parsing
    if cfg.operation_mode in mode_groups.deployment:
        legal = ["c_project_path", "IDE", "verbosity", "hardware_setup"]
        legal_hw = ["serie", "board", "stlink_serial_number"]
        parse_deployment_section(cfg.deployment,
                                 legal=legal,
                                 legal_hw=legal_hw)

    # MLFlow section parsing
    parse_mlflow_section(cfg.mlflow)

    # Check that the provided datast is from one of the supported datasets, raise error otherwise
    cds = cfg.dataset
    if cfg.operation_mode in ['benchmarking', 'deployment']:
        pass
    elif(cds.name.lower() in ['wisdm', 'mobility_v1']):
        check_dataset_contents(cds)
        cds.class_names = get_class_names(cds.name)
    else:
        raise ValueError("\nOnly \'wisdm\' and \'mobility_v1\' datasets are supproted." 
                         "Please update your configuration file.")

    return cfg
