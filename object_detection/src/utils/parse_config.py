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
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
from cfg_utils import postprocess_config_dict, check_config_attributes, parse_tools_section, parse_benchmarking_section, \
                      parse_mlflow_section, parse_top_level, parse_general_section, parse_quantization_section, \
                      parse_training_section, parse_prediction_section, parse_deployment_section, check_hardware_type
from typing import Dict, List


def parse_postprocessing_section(cfg: DictConfig) -> None:
    # cfg: 'postprocessing' section of the configuration file

    legal = ["confidence_thresh", "NMS_thresh", "IoU_eval_thresh", "yolo_anchors", "plot_metrics",
             'max_detection_boxes']
    required = ["confidence_thresh", "NMS_thresh", "IoU_eval_thresh"]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="postprocessing")

    if not cfg.yolo_anchors:
        cfg.yolo_anchors = [0.076023, 0.258508, 0.163031, 0.413531, 0.234769, 0.702585, 0.427054, 0.715892, 0.748154, 0.857092]

    cfg.plot_metrics = cfg.plot_metrics if cfg.plot_metrics is not None else False

def get_class_names_from_file(cfg: DictConfig) -> List:
    if cfg.deployment.label_file_path :
        with open(cfg.deployment.label_file_path, 'r') as file:
            class_names = [line.strip() for line in file]
    return class_names

def parse_dataset_section(cfg: DictConfig, mode: str = None, mode_groups: DictConfig = None, hardware_type: str = None) -> None:
    # cfg: dictionary containing the 'dataset' section of the configuration file

    legal = ["name", "class_names", "training_path", "validation_path", "validation_split", "test_path",
             "quantization_path", "quantization_split", "seed"]

    required = []
    one_or_more = []
    if mode in mode_groups.training:
        required += ["training_path", ]
    elif mode in mode_groups.evaluation:
        one_or_more += ["training_path", "test_path"]
    if mode not in ("quantization", "benchmarking", "chain_qb"):
        if hardware_type == "MCU":
            required += ["class_names", ]
    check_config_attributes(cfg, specs={"legal": legal, "all": required, "one_or_more": one_or_more},
                            section="dataset")

    # Set default values of missing optional attributes
    if not cfg.name:
        cfg.name = "unnamed"
    if not cfg.validation_split:
        cfg.validation_split = 0.2
    cfg.seed = cfg.seed if cfg.seed else 123

    # Check the value of validation_split if it is set
    if cfg.validation_split:
        split = cfg.validation_split
        if split <= 0.0 or split >= 1.0:
            raise ValueError(f"\nThe value of `validation_split` should be > 0 and < 1. Received {split}\n"
                             "Please check the 'dataset' section of your configuration file.")

    # Check the value of quantization_split if it is set
    if cfg.quantization_split:
        split = cfg.quantization_split
        if split <= 0.0 or split >= 1.0:
            raise ValueError(f"\nThe value of `quantization_split` should be > 0 and < 1. Received {split}\n"
                             "Please check the 'dataset' section of your configuration file.")


def parse_preprocessing_section(cfg: DictConfig,
                                mode:str = None) -> None:
    # cfg: 'preprocessing' section of the configuration file
    legal = ["rescaling", "resizing", "color_mode"]
    if mode == 'deployment':
        # removing the obligation to have rescaling for the 'deployment' mode
        required=["resizing", "color_mode"]
        check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="preprocessing")
    else:
        required=legal
        check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="preprocessing")
        legal = ["scale", "offset"]
        check_config_attributes(cfg.rescaling, specs={"legal": legal, "all": legal}, section="preprocessing.rescaling")

    legal = ["interpolation", "aspect_ratio"]
    check_config_attributes(cfg.resizing, specs={"legal": legal, "all": legal}, section="preprocessing.resizing")
    if cfg.resizing.aspect_ratio != "fit":
        raise ValueError("The only value of aspect_ratio that is supported at this point is 'fit' "
                         "('crop' and 'padding' are not supported).")

    # Check resizing interpolation value
    interpolation_methods = ["bilinear", "nearest", "area", "lanczos3", "lanczos5", "bicubic", "gaussian",
                             "mitchellcubic"]
    if cfg.resizing.interpolation not in interpolation_methods:
        raise ValueError(f"\nUnknown value for `interpolation` attribute. Received {cfg.resizing.interpolation}\n"
                         f"Supported values: {interpolation_methods}\n"
                         "Please check the 'preprocessing.resizing' section of your configuration file.")

    # Check color mode value
    color_modes = ["grayscale", "rgb", "rgba"]
    if cfg.color_mode not in color_modes:
        raise ValueError(f"\nUnknown value for `color_mode` attribute. Received {cfg.color_mode}\n"
                         f"Supported values: {color_modes}\n"
                         "Please check the 'preprocessing' section of your configuration file.")


def parse_data_augmentation_section(cfg: DictConfig) -> None:
    # cfg: 'data_augmentation' section of the configuration file

    legal = ["horizontal_flip", "vertical_flip", "translation", "rotation",
             "shearing", "gaussian_blur", "linear_contrast"]
    for fn in cfg.keys():
        if fn not in legal:
            raise ValueError(f"\nUnknown or unsupported data augmentation function: {fn}\n"
                             "Please check the 'data_augmentation' section of your configuration file.")


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
        "training": ["training", "chain_tqeb", "chain_tqe"],
        "evaluation": ["evaluation", "chain_tqeb", "chain_tqe", "chain_eqe", "chain_eqeb"],
        "quantization": ["quantization", "chain_tqeb", "chain_tqe", "chain_eqe",
                         "chain_qb", "chain_eqeb", "chain_qd"],
        "benchmarking": ["benchmarking", "chain_tqeb", "chain_qb", "chain_eqeb"],
        "deployment": ["deployment", "chain_qd"],
        "prediction": ["prediction"]
    })
    mode_choices = ["training", "evaluation", "deployment",
                    "quantization", "benchmarking", "chain_tqeb", "chain_tqe",
                    "chain_eqe", "chain_qb", "chain_eqeb", "chain_qd", "prediction"]
    legal = ["general", "operation_mode", "dataset", "preprocessing", "data_augmentation",
             "training", "postprocessing", "quantization", "prediction", "tools",
             "benchmarking", "deployment", "mlflow", "hydra"]
    parse_top_level(cfg,
                    mode_groups=mode_groups,
                    mode_choices=mode_choices,
                    legal=legal)
    print(f"[INFO] : Running `{cfg.operation_mode}` operation mode")

    # General section parsing
    if not cfg.general:
        cfg.general = DefaultMunch.fromDict({})
    legal = ["project_name", "model_path", "logs_dir", "saved_models_dir", "deterministic_ops",
            "display_figures", "global_seed", "gpu_memory_limit", "model_type", "num_threads_tflite"]
    required = ["model_type"]
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
                          mode_groups=mode_groups,
                          hardware_type=cfg.hardware_type)

    # Preprocessing section parsing
    parse_preprocessing_section(cfg.preprocessing,
                                mode=cfg.operation_mode)

    # Training section parsing
    if cfg.operation_mode in mode_groups.training:
        if cfg.data_augmentation or cfg.custom_data_augmentation:
            parse_data_augmentation_section(cfg.data_augmentation)
        model_path_used = bool(cfg.general.model_path)
        model_type_used = bool(cfg.general.model_type)
        legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
                "callbacks", "trained_model_path"]
        parse_training_section(cfg.training,
                               model_path_used=model_path_used,
                               model_type_used=model_type_used,
                               legal=legal)

    # Postprocessing section parsing
    if cfg.operation_mode in (mode_groups.training + mode_groups.evaluation + mode_groups.quantization + mode_groups.deployment + mode_groups.prediction):
        if cfg.hardware_type == "MCU":
            parse_postprocessing_section(cfg.postprocessing)

    # Quantization section parsing
    if cfg.operation_mode in mode_groups.quantization:
        legal = ["quantizer", "quantization_type", "quantization_input_type",
                "quantization_output_type", "granularity", "export_dir", "optimize"]
        parse_quantization_section(cfg.quantization,
                                   legal=legal)

    # Prediction section parsing
    if cfg.operation_mode == "prediction":
        parse_prediction_section(cfg.prediction)

    # Tools section parsing
    if cfg.operation_mode in (mode_groups.benchmarking + mode_groups.deployment):
        parse_tools_section(cfg.tools,
                            cfg.operation_mode,
                            cfg.hardware_type)

    #For MPU, check if online benchmarking is activated
    if cfg.operation_mode in mode_groups.benchmarking:
        if "STM32MP" in cfg.benchmarking.board :
            if cfg.operation_mode == "benchmarking" and not(cfg.tools.stm32ai.on_cloud):
                print("Target selected for benchmark :", cfg.benchmarking.board)
                print("Offline benchmarking for MPU is not yet available please use online benchmarking")
                exit(1)

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
        if cfg.hardware_type == "MCU":
            legal = ["c_project_path", "IDE", "verbosity", "hardware_setup"]
            legal_hw = ["serie", "board", "stlink_serial_number"]
        else:
            legal = ["c_project_path", "label_file_path","board_deploy_path", "verbosity", "hardware_setup"]
            legal_hw = ["serie", "board", "ip_address"]
            if cfg.preprocessing.color_mode != "rgb":
                raise ValueError("\n Color mode used is not supported for deployment on MPU target \n Please use RGB format")
            if cfg.preprocessing.resizing.aspect_ratio != "fit":
                raise ValueError("\n Aspect ratio used is not supported for deployment on MPU target \n Please use FIT aspect ratio")
        parse_deployment_section(cfg.deployment,
                                 legal=legal,
                                 legal_hw=legal_hw)

    # MLFlow section parsing
    parse_mlflow_section(cfg.mlflow)

    # Check that all datasets have the required directory structure
    cds = cfg.dataset

    if not cds.class_names and cfg.operation_mode in ("deployment","chain_qd") and cfg.hardware_type == "MPU":
        cds.class_names = get_class_names_from_file(cfg)
        print("[INFO] : Found {} classes in label file {}".format(len(cds.class_names), cfg.deployment.label_file_path))

    return cfg
