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
from cfg_utils import replace_none_string, postprocess_config_dict, check_config_attributes, parse_tools_section, \
                      parse_benchmarking_section, parse_mlflow_section, parse_top_level, parse_general_section, \
                      parse_training_section, parse_quantization_section, parse_prediction_section, parse_deployment_section, \
                      check_hardware_type
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
import tensorflow as tf
import pandas as pd
from typing import Dict, List


def parse_dataset_section(cfg: DictConfig, mode: str = None, mode_groups: DictConfig = None) -> None:
    # cfg: dictionary containing the 'dataset' section of the configuration file

    legal = ["name", "training_audio_path", "training_csv_path",
             "multi_label", "use_garbage_class", "expand_last_dim", "file_extension",
             "to_cache", "shuffle", "batch_size",  "class_names","validation_audio_path", "validation_csv_path",
             "validation_split", "test_audio_path", "test_csv_path",
             "quantization_audio_path", "quantization_csv_path", "quantization_split",
             "n_samples_per_garbage_class", "seed"]

    required = ["name", "multi_label", "use_garbage_class", "expand_last_dim", "file_extension",
                "to_cache", "shuffle", "class_names",
                "n_samples_per_garbage_class", "seed"]
    one_or_more = []
    if mode in mode_groups.training and cfg.name != "fsd50k":
        required += ["training_csv_path", "training_audio_path"]
    elif mode in mode_groups.evaluation and cfg.name != "fsd50k":
        one_or_more += ["training_csv_path", "test_csv_path"]
        # A second check explicitly for the audio paths
        check_config_attributes(cfg, specs={"legal":legal, "all":None,
                                           "one_or_more":["training_audio_path", "test_audio_path"]},
                                section="dataset")

    check_config_attributes(cfg, specs={"legal": legal, "all": required, "one_or_more": one_or_more},
                            section="dataset")

    # Set default values of missing optional attributes
    if not cfg.name:
        cfg.name = "<unnamed>"
    if not cfg.validation_split:
        cfg.validation_split = 0.2
    cfg.seed = cfg.seed if cfg.seed else 123

    # Sort the class names if they were provided
    if cfg.class_names:
        cfg.class_names = sorted(cfg.class_names)

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

    # Check that the training, evaluation, test and quantization sets
    # root directories exist in the attributes are set
    dataset_audio_paths = [(cfg.training_audio_path, "training audio"),
                           (cfg.validation_audio_path, "validation audio"),
                           (cfg.test_audio_path, "test audio"),
                           (cfg.quantization_audio_path, "quantization audio")]
        
    dataset_csv_paths =[(cfg.training_csv_path, "training csv file"),
                        (cfg.validation_csv_path, "validation csv file"),
                        (cfg.test_csv_path, "test csv file"),
                        (cfg.quantization_csv_path, "quantization csv file")]
    for path, name in dataset_audio_paths:
        if path and not os.path.isdir(path):
            raise FileNotFoundError(f"\nUnable to find the directory of {name}\n"
                                    f"Received path: {path}\n"
                                    "Please check the 'dataset' section of your configuration file.")
    for path, name in dataset_csv_paths:
        if path and not os.path.isfile(path):
            raise FileNotFoundError(f"\nUnable to find the {name}\n"
                                    f"Received path: {path}\n"
                                    "Please check the 'dataset' section of your configuration file.") 

def parse_dataset_specific_fsd50k_section(cfg: DictConfig) -> None:
    # cfg: 'preprocessing' section of the configuration file
    legal = ["csv_folder", "dev_audio_folder", "eval_audio_folder", "audioset_ontology_path",
             "only_keep_monolabel"]
    # All are required if this function is called
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="preprocessing")

def parse_preprocessing_section(cfg: DictConfig) -> None:
    # cfg: 'preprocessing' section of the configuration file
    legal = ["min_length", "max_length", "target_rate",
             "top_db", "frame_length", "hop_length",
             "trim_last_second", "lengthen"]
    # All are required
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="preprocessing")

def parse_feature_extraction_section(cfg: DictConfig) -> None:
    # cfg: 'feature_extraction' section of the config file
    # TODO : add more explicit error messages in case of wrong input but I expect the user
    # to be able to read a basic readme

    legal = ["patch_length", "n_mels", "overlap", "n_fft",
             "hop_length", "window_length", "window", "center",
             "pad_mode", "power", "fmin", "fmax", "norm",
             "htk", "to_db", "include_last_patch"]
    # all are required
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="feature_extraction")
    replace_none_string(cfg)

def parse_data_augmentation_section(cfg: DictConfig) -> None:
    """
    This function checks the data augmentation section of the config file.
    
    Arguments:
        cfg (DictConfig): The entire configuration file as a DefaultMunch dictionary.

    Returns:
        None
    """
    # Check top-level data augmentation attributes, then check for each valid attribute.
    legal = ["GaussianNoise", "VolumeAugment", "SpecAug"]
    check_config_attributes(cfg.data_augmentation,
                            specs={"legal": legal, "all": legal},
                            section="data_augmentation")
    legal = ["enable", "scale"]
    all = ["enable"]
    check_config_attributes(cfg.data_augmentation.GaussianNoise,
                            specs={"legal": legal, "all": all},
                            section="data_augmentation.GaussianNoise")
    
    legal = ["enable", "min_scale", "max_scale"]
    all = ["enable"]
    check_config_attributes(cfg.data_augmentation.VolumeAugment,
                            specs={"legal": legal, "all": all},
                            section="data_augmentation.VolumeAugment")
    legal = ["enable","freq_mask_param", "time_mask_param",
             "n_freq_mask", "n_time_mask", "mask_value"]
    all = ["enable"]
    check_config_attributes(cfg.data_augmentation.SpecAug,
                            specs={"legal": legal, "all": all},
                            section="data_augmentation.SpecAug")


def get_class_names(cfg: DictConfig, name: str, csv_path=None):
    '''Attemps to get class names for a dataset.
       If the dataset name is not previously known, attemps to get the class names 
       from the dataset's associated csv file. Expects that this csv file is in ESC-10 format.
    '''
    if name.lower() == "esc10":
        return ['dog', 'chainsaw', 'crackling_fire', 'helicopter', 'rain',
                'crying_baby', 'clock_tick', 'sneezing', 'rooster', 'sea_waves']
    if name.lower() == "fsd50k":
        # grab them from the vocabulary.csv
        vocab_path = os.path.join(cfg.dataset_specific.fsd50k.csv_folder, "vocabulary.csv")
        if not os.isfile(vocab_path):
            raise FileNotFoundError(f"Tried to infer class names for FSD50K dataset,\
                                     but could not find vocabulary file at {vocab_path}")
        vocab = pd.read_csv(vocab_path, header=None, names= ['id', 'name', 'mids'])
        return vocab["name"].unique().tolist()
    elif csv_path is not None:
        df = pd.read_csv(csv_path)
        return df["category"].unique().tolist()
    else:
        return None # This will raise the appropriate exception in get_config  


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
        "training": ["training", "chain_tbqeb", "chain_tqe"],
        "evaluation": ["evaluation", "chain_tbqeb", "chain_tqe", "chain_eqe", "chain_eqeb"],
        "quantization": ["quantization", "chain_tbqeb", "chain_tqe", "chain_eqe",
                         "chain_qb", "chain_eqeb", "chain_qd"],
        "benchmarking": ["benchmarking", "chain_tbqeb", "chain_qb", "chain_eqeb"],
        "deployment": ["deployment", "chain_qd"]
    })
    mode_choices = ["training", "evaluation", "prediction", "deployment", 
                "quantization", "benchmarking", "chain_tbqeb", "chain_tqe",
                "chain_eqe", "chain_qb", "chain_eqeb", "chain_qd"]
    legal = ["general", "operation_mode", "dataset", "preprocessing", "feature_extraction", 
             "data_augmentation", "custom_data_augmentation", "training",
             "quantization", "prediction", "tools", "dataset_specific",
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
             "display_figures", "global_seed", "gpu_memory_limit", "batch_size", "num_threads_tflite"]
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
    if cfg.operation_mode != "benchmarking":
        if not cfg.dataset:
            cfg.dataset = DefaultMunch.fromDict({})
        parse_dataset_section(cfg.dataset, 
                              mode=cfg.operation_mode, 
                              mode_groups=mode_groups)
        # If dataset is FSD50K, parse its dedicated section
        if cfg.dataset.name.lower() == 'fsd50k':
            parse_dataset_specific_fsd50k_section(cfg.dataset_specific.fsd50k)
        parse_preprocessing_section(cfg.preprocessing)
        parse_feature_extraction_section(cfg.feature_extraction)

    # Training section parsing
    if cfg.operation_mode in mode_groups.training:
        if cfg.data_augmentation:
            parse_data_augmentation_section(cfg)
        model_path_used = bool(cfg.general.model_path)
        model_type_used = bool(cfg.general.model_type)
        legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
            "callbacks", "resume_training_from", "trained_model_path", "fine_tune"]
        parse_training_section(cfg.training, 
                               model_path_used=model_path_used, 
                               model_type_used=model_type_used,
                               legal=legal)

    # Quantization section parsing
    if cfg.operation_mode in mode_groups.quantization:
        legal = ["quantizer", "quantization_type", "quantization_input_type",
                "quantization_output_type", "export_dir", "granularity", "target_opset", "optimize"]
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
        legal = ["c_project_path", "IDE", "verbosity", "hardware_setup", "unknown_class_threshold"]
        legal_hw = ["serie", "board", "stlink_serial_number"]
        parse_deployment_section(cfg.deployment,
                                 legal=legal,
                                 legal_hw=legal_hw)

    # MLFlow section parsing
    parse_mlflow_section(cfg.mlflow)

    # Check that all datasets have the required directory structure
    # Also check that all image files can be loaded if requested
    cds = cfg.dataset
    if cds: # All this breaks if no dataset section is present
        if not cds.class_names and cfg.operation_mode not in ("quantization", "benchmarking", "chain_qb"):
            # Infer the class names from a dataset if there is one
            for path in [cds.training_csv_path, cds.validation_csv_path, cds.test_csv_path, cds.quantization_csv_path]:
                cds.class_names = get_class_names(cfg, name=cds.name, csv_path=path)
                print(f"[INFO] : Found {len(cds.class_names)} classes in dataset {path}")
                print(f"[INFO] : Automatically inferred classes {cds.class_names}")
                break
            if not cds.class_names:
                raise ValueError("\nMissing the class names. You can provide in the 'dataset' section either:\n"
                                    " - the class names using the `class_names` attribute\n"
                                    " - a path to a dataset using the `training_path`, `validation_path`, `test_path` or `quantization_path` attribute\n" 
                                    "Please update your configuration file.")

    return cfg
