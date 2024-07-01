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
from cfg_utils import postprocess_config_dict, check_attributes, check_config_attributes, parse_tools_section, \
                      parse_benchmarking_section, parse_mlflow_section, parse_top_level, parse_general_section, \
                      parse_training_section, parse_deployment_section, parse_prediction_section, check_hardware_type
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
import tensorflow as tf
from typing import Dict, List
from handposture_dictionnary import hand_posture_dict


def check_dataset_paths_and_contents(cfg, mode: str = None, mode_groups: DictConfig = None) -> None:

    dataset_paths = {}
    # Datasets used in a training
    if mode in mode_groups.training:
        dataset_paths["training_path"] = cfg.training_path
        if cfg.validation_path:
            dataset_paths["validation_path"] = cfg.validation_path
        if cfg.test_path:
            dataset_paths["test_path"] = cfg.test_path

    # Datasets used in an evaluation
    if mode in mode_groups.evaluation:
        if cfg.test_path:
            dataset_paths["test_path"] = cfg.test_path
        elif cfg.validation_path:
            dataset_paths["validation_path"] = cfg.validation_path
        else:
            dataset_paths["training_path"] = cfg.training_path

    # Check the datasets
    for name in ["training_path", "validation_path", "test_path"]: # "quantization_path"
        if name in dataset_paths:
            path = dataset_paths[name]
            if not os.path.isdir(path):
                raise FileNotFoundError(f"\nUnable to find the root directory of the {name[:-5]} set\n"
                                        f"Received path: {path}\n"
                                        "Please check the 'dataset' section of your configuration file.")
            # if cfg.check_image_files:
            #     print(f"[INFO] : Checking {path} dataset")
            # check_dataset_integrity(path, check_image_files=cfg.check_image_files)
        else:
            # Set to None the paths to datasets that are not needed,
            # otherwise the data loaders would them.
            cfg[name] = None


def parse_dataset_section(cfg: DictConfig, mode: str = None, mode_groups: DictConfig = None) -> None:
    # cfg: dictionary containing the 'dataset' section of the configuration file

    legal = ["name", "class_names", "training_path", "validation_path", "validation_split", "test_path",
             "seed"] #"quantization_path", "quantization_split", "check_image_files",

    required = []
    one_or_more = []
    if mode in mode_groups.training:
        required += ["training_path",]
    elif mode in mode_groups.evaluation:
        one_or_more += ["training_path", "test_path"]
    elif mode in mode_groups.deployment or mode == "prediction":
        required += ["class_names",]

    check_config_attributes(cfg, specs={"legal": legal, "all": required, "one_or_more": one_or_more},
                            section="dataset")

    # Set default values of missing optional attributes
    if not cfg.name:
        cfg.name = "<unnamed>"
    if not cfg.validation_split:
        cfg.validation_split = 0.2
    # cfg.check_image_files = cfg.check_image_files if cfg.check_image_files is not None else False
    # cfg.seed = cfg.seed if cfg.seed else 123

    # Sort the class names if they were provided
    if cfg.class_names:
        newdict = {key: hand_posture_dict[key] for key in cfg.class_names}
        newdict = dict(sorted(newdict.items(), key=lambda item: item[1]))
        cfg.class_names = list(newdict)

    # Check the value of validation_split if it is set
    if cfg.validation_split:
        split = cfg.validation_split
        if split <= 0.0 or split >= 1.0:
            raise ValueError(f"\nThe value of `validation_split` should be > 0 and < 1. Received {split}\n"
                                "Please check the 'dataset' section of your configuration file.")

    # Check the value of quantization_split if it is set
    # if cfg.quantization_split:
    #     split = cfg.quantization_split
    #     if split <= 0.0 or split >= 1.0:
    #         raise ValueError(f"\nThe value of `quantization_split` should be > 0 and < 1. Received {split}\n"
    #                          "Please check the 'dataset' section of your configuration file.")
        
    # if cfg.name not in ("emnist", "cifar10", "cifar100"):
    check_dataset_paths_and_contents(cfg, mode=mode, mode_groups=mode_groups)


def parse_preprocessing_section(cfg: DictConfig) -> None:
    # cfg: 'preprocessing' section of the configuration file

    legal = ["Max_distance", "Min_distance", "Background_distance"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="preprocessing")

    # legal = ["scale", "offset"]
    # check_config_attributes(cfg.rescaling, specs={"legal": legal, "all": legal}, section="preprocessing.rescaling")
    #
    # legal = ["interpolation", "aspect_ratio"]
    # check_config_attributes(cfg.resizing, specs={"legal": legal, "all": ["aspect_ratio"]}, section="preprocessing.resizing")

    # We could check the "Max_distance", "Min_distance", "Background_distance" values...
    Max_distance = cfg.Max_distance
    if Max_distance < 0 or Max_distance > 4000:
        raise ValueError(f"\nUnknown or unsupported value for `Max_distance` attribute. Received {Max_distance}\n"
                         f"Supported values are from 0 to 4000.\n"
                         "Please check the 'preprocessing.Max_distance' section of your configuration file.")
    Min_distance = cfg.Min_distance
    if Min_distance < 0 or Min_distance > Max_distance:
        raise ValueError(f"\nUnknown or unsupported value for `Min_distance` attribute. Received {Min_distance}\n"
                         f"Supported values are from 0 to Max_distance.\n"
                         "Please check the 'preprocessing.Min_distance' section of your configuration file.")
    Background_distance = cfg.Background_distance
    if Background_distance == 0 or Background_distance > 4000:
        raise ValueError(f"\nUnknown or unsupported value for `Background_distance` attribute. Received {Background_distance}\n"
                         f"Supported values are from 1 to 4000.\n"
                         "Please check the 'preprocessing.Background_distance' section of your configuration file.")




def parse_data_augmentation_section(cfg: DictConfig, config_dict: Dict) -> None:
    """
    This function checks the data augmentation section of the config file.
    The attribute that introduces the section is either `data_augmentation`
    or `custom_data_augmentation`. If it is `custom_data_augmentation`,
    the name of the data augmentation function that is provided must be
    different from `data_augmentation` as this is a reserved name.

    Arguments:
        cfg (DictConfig): The entire configuration file as a DefaultMunch dictionary.
        config_dict (Dict): The entire configuration file as a regular Python dictionary.

    Returns:
        None
    """

    if cfg.data_augmentation and cfg.custom_data_augmentation:
        raise ValueError("\nThe `data_augmentation` and `custom_data_augmentation` attributes "
                         "are mutually exclusive.\nPlease check your configuration file.")

    if cfg.data_augmentation:
        cfg.data_augmentation = DefaultMunch.fromDict({})
        # The name of the Model Zoo data augmentation function is 'data_augmentation'.
        cfg.data_augmentation.function_name = "data_augmentation"
        cfg.data_augmentation.config = config_dict['data_augmentation'].copy()

    if cfg.custom_data_augmentation:
        check_attributes(cfg.custom_data_augmentation,
                         required=["function_name"],
                         optional=["config"],
                         section="custom_data_augmentation")
        cfg.data_augmentation = DefaultMunch.fromDict({})
        if cfg.custom_data_augmentation["function_name"] == "data_augmentation":
            raise ValueError("\nThe function name `data_augmentation` is reserved.\n"
                             "Please use another name (attribute `function_name` in "
                             "the 'custom_data_augmentation' section).")
        cfg.data_augmentation.function_name = cfg.custom_data_augmentation.function_name
        if cfg.custom_data_augmentation.config:
            cfg.data_augmentation.config = config_dict['custom_data_augmentation']['config'].copy()
        del cfg.custom_data_augmentation


def infer_class_names_from_dataset(cfg: DictConfig) -> List:
    # Look for a dataset that can be used to find the class names
    if cfg.training_path:
        path = cfg.training_path
    elif cfg.validation_path:
        path = cfg.validation_path
    elif cfg.test_path:
        path = cfg.test_path
    else:
        raise ValueError("\nUnable to find the class names, no dataset is available."
                         "\nPlease provide them using the `dataset.class_names` "
                         "attribute in your configuration file.")
    # Infer the class names from the dataset
    return get_class_names(cfg.name, dataset_root_dir=path)


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
        "training": ["training"],
        "evaluation": ["evaluation"],
        "benchmarking": ["benchmarking"],
        "deployment": ["deployment"],
        "quantization": [],
    })
    mode_choices = ["training", "evaluation", "prediction", "deployment", "benchmarking",
                    # "quantization", "chain_tbqeb", "chain_tqe",
                    # "chain_eqe", "chain_qb", "chain_eqeb", "chain_qd"
                    ]
    legal = ["general", "operation_mode", "dataset", "preprocessing", "data_augmentation", 
             "custom_data_augmentation", "training", "prediction", "tools",
             "benchmarking", "deployment", "mlflow", "hydra"]
    parse_top_level(cfg, 
                    mode_groups=mode_groups, 
                    mode_choices=mode_choices,
                    legal=legal)
    print(f"[INFO] : Running `{cfg.operation_mode}` operation mode")

    # General section parsing
    if not cfg.general:
        cfg.general = DefaultMunch.fromDict({"project_name": "<unnamed>"})
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
    if cfg.operation_mode in (mode_groups.training + mode_groups.evaluation + mode_groups.deployment):
        parse_preprocessing_section(cfg.preprocessing)

    # training section parsing
    if cfg.operation_mode in mode_groups.training:
        if cfg.data_augmentation or cfg.custom_data_augmentation:
            parse_data_augmentation_section(cfg, config_dict)
        model_path_used = bool(cfg.general.model_path)
        model_type_used = bool(cfg.general.model_type)
        legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
                "callbacks", "trained_model_path"]
        parse_training_section(cfg.training, 
                               model_path_used=model_path_used,
                               model_type_used=model_type_used,
                               legal=legal)

    # Prediction section parsing
    if cfg.operation_mode == "prediction":
        parse_prediction_section(cfg.prediction)

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

    return cfg
