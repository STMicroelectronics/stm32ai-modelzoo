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
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
import tensorflow as tf
import pandas as pd
from typing import Dict, List

def _replace_none_string(dico: dict) -> dict:
    """Replaces None strings in the values of a dictionary with the Python None value.
       Other values are unchanged.
    """
    for k, v in dico.items():
        if v == "None":
            dico[k] = None
    return dico

def expand_env_vars(string: str) -> str:
    """
    Expands environment variables in a string if any. The syntax for variables
    is ${variable_name}. An error is thrown if a variable is found in the string
    but is not set.

    Args:
        string (str): The string to expand environment variables in.

    Returns:
        string (str): The original string with expanded variables.
    """
    for match in re.findall('\$\{\w+\}', string):
        var_name = match[2:-1]
        # Get the variable value, throw an error if it is not set.
        var_value = os.environ.get(var_name)
        if var_value is None:
            raise OSError("\nCould not find an environment variable named `{}`\n"
                          "Please check your configuration file.".format(var_name))
        match = "\\" + match
        string = re.sub(match, var_value, string, count=1)
    return string


def postprocess_config_dict(config: DictConfig) -> None:
    """
    The YAML loader outputs some attribute values as strings although they
    are different Python types. This function walks the config dictionary 
    tree and restores some of these types, including booleans, integers,
    floats and tuples.
    For example:
    - "True" is converted to boolean True
    - "1./255" is converted to a float (equal to 0.00392156)
    - "(128, 128, 3)" is converted to a tuple.
    The function also replaces environment variables that appear in strings
    with their values.

    Arguments:
        config (DictConfig): dictionary containing the entire configuration file.

    Returns:
        None
    """

    for k in config.keys():
        v = config[k]
        if type(v) == dict:
            postprocess_config_dict(v)
        elif type(v) == str:
            # Expand environment variables if any
            v_exp = expand_env_vars(v)
            if v_exp != v:
                config[k] = v_exp
                v = v_exp
            if v[:7] == "lambda ":
                # The value is a lambda function. Remove the \n characters
                # and multiple blanks that get inserted by the YAML loader
                # if the function is written on several lines.
                v = re.sub("\n", "", v)
                config[k] = re.sub(" +", " ", v)
            else:
                try:
                    v_eval = eval(v)
                except:
                    v_eval = v
                if isinstance(v_eval, (bool, int, float, tuple)):
                    config[k] = v_eval


def check_config_attributes(cfg: DictConfig, specs: Dict = None, section: str = None) -> None:
    """
    This function checks that the attributes used in a given section
    of the configuration file comply with specified requirements.

    Arguments:
        cfg (DictConfig): dictionary containing the configuration file section to check
        specs (Dict): dictionary specifying the requirements for attribute usage in the section
        section (str): name of the section

    Returns:
        None
    """

    specs = DefaultMunch.fromDict(specs)
    if section == "top_level":
        message = f"\nPlease check the top-level of your configuration file."
    else:
        message = f"\nPlease check the '{section}' section of your configuration file."

    if specs.legal:
        # Check that all the used attribute names are known
        for attr in cfg.keys():
            if attr not in specs.legal:
                raise ValueError(f"\nUnknown attribute `{attr}`{message}")

    if specs.all:
        # Check that all the specified attributes are present and have a value
        for attr in specs.all:
            if attr not in cfg:
                if section == "top_level":
                    raise ValueError(f"\nMissing `{attr}` section{message}")
                else:
                    raise ValueError(f"\nMissing `{attr}` attribute{message}")
            if cfg[attr] is None:
                if section == "top_level":
                    raise ValueError(f"\nMissing body of `{attr}` section{message}")
                else:
                    raise ValueError(f"\nExpecting a value for `{attr}` attribute{message}")

    if specs.one_or_more:
        # Check that at least one of the specified attributes is present and has a value
        count = 0
        for attr in specs.one_or_more:
            if attr in cfg and cfg[attr] is not None:
                count += 1
        if count == 0:
            raise ValueError(f"\nMissing one or more attributes from {specs.one_or_more}{message}")


def parse_top_level(cfg: DictConfig, mode_groups: DictConfig = None) -> None:
    # cfg: dictionary containing the entire configuration file

    mode_choices = ["training", "evaluation", "prediction", "deployment", 
                    "quantization", "benchmarking", "chain_tbqeb", "chain_tqe",
                    "chain_eqe", "chain_qb", "chain_eqeb", "chain_qd"]
    
    # Check that operation_mode is present and has a value
    message = "\nPlease check the top-level of your configuration file."
    if "operation_mode" not in cfg:
        raise ValueError(f"\nMissing `operation_mode` attribute\nSupported modes: {mode_choices}{message}")
    if cfg.operation_mode is None:
        raise ValueError("\nExpecting a value for `operation_mode` attribute\n"
                         f"Supported modes: {mode_choices}{message}")
    
    # Check that the value of operation_mode is valid
    mode = cfg.operation_mode
    if mode not in mode_choices:
        raise ValueError(f"\nUnknown value for `operation_mode` attribute. Received {mode}\n"
                         f"Supported modes: {mode_choices}{message}")

    # Attributes usable at the top level
    legal = ["general", "operation_mode", "dataset", "preprocessing", "feature_extraction", 
             "data_augmentation", "custom_data_augmentation", "training",
             "quantization", "prediction", "tools", "dataset_specific",
             "benchmarking", "deployment", "mlflow", "hydra"]

    required = ["mlflow"]
    if mode not in mode_groups.training:
        # We need the 'general' section to provide model_path.
        required += ["general",]
    if mode != "benchmarking":
        # Need the preprocessing & feature extraction sections
        required += ["preprocessing", "feature_extraction"]
    if mode not in ("prediction", "quantization", "benchmarking", "deployment", "chain_qb", "chain_qd"):
        required += ["dataset",]
    if mode in mode_groups.training:
        required += ["training",]
    if mode in mode_groups.quantization:
        required += ["quantization",]
    if mode == "prediction":
        required += ["prediction",]
    if mode in mode_groups.benchmarking:
        required += ["benchmarking", "tools"]
    if mode in mode_groups.deployment:
        required += ["deployment", "tools"]

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="top_level")


def parse_general_section(cfg: DictConfig, mode: str = None, mode_groups=None) -> None:
    # cfg: dictionary containing the 'general' section of the configuration file

    legal = ["project_name", "model_path", "logs_dir", "saved_models_dir", "deterministic_ops", 
             "display_figures", "global_seed", "gpu_memory_limit", "batch_size"]

    # Usage of the model_path attribute in training modes 
    # is checked when parsing the 'training' section.
    required = ["model_path"] if not mode_groups.training else []
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="general")

    # Set default values of missing optional attributes
    if not cfg.project_name:
        cfg.project_name = "<unnamed>"
    if not cfg.logs_dir:
        cfg.logs_dir = "logs"
    if not cfg.saved_models_dir:
        cfg.saved_models_dir = "saved_models"
    cfg.deterministic_ops = cfg.deterministic_ops if cfg.deterministic_ops is not None else False
    cfg.display_figures = cfg.display_figures if cfg.display_figures is not None else True
    if not cfg.global_seed:
        cfg.global_seed = 133

    ml_path = cfg.model_path
    file_extension = Path(ml_path).suffix if ml_path else ""
    m1 = "\nExpecting `model_path` to be set to a path to a "
    m2 = f" model file when running '{mode}' operation mode\n"
    if ml_path:
        m2 += f"Received path: {ml_path}\n"
    m2 += "Please check the 'general' section of your configuration file."
    
    if mode in mode_groups.training:
        if ml_path and file_extension != ".h5":
            raise ValueError(m1 + ".h5" + m2)
    elif mode in mode_groups.quantization:
        if not ml_path or file_extension != ".h5":
            raise ValueError(m1 + ".h5" + m2)
    elif mode in ("evaluation", "prediction"):
        if not ml_path or file_extension not in (".h5", ".tflite"):
            raise ValueError(m1 + ".h5 or .tflite" + m2)
    elif mode in ("benchmarking"):
        if not ml_path or file_extension not in (".h5", ".tflite", ".onnx"):
            raise ValueError(m1 + ".h5, .tflite or .onnx" + m2)
    elif mode in ("deployment"):
        if not ml_path or file_extension != ".tflite":
            raise ValueError(m1 + ".tflite" + m2)

    # If model_path is set, check that the model file exists.
    if ml_path and not os.path.isfile(ml_path):
        raise FileNotFoundError(f"\nUnable to find file {ml_path}\nPlease check the 'general.model_path'"
                                "attribute in your configuration file.")


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
    cfg.seed = cfg.seed if cfg.seed else 133

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
    _replace_none_string(cfg)

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
 
def parse_training_section(cfg: DictConfig, mode: str = None, model_path_used: bool = None) -> None:
    # cfg: 'training' section of the configuration file
    # model_path: general.model_path attribute

    legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
             "callbacks", "resume_training_from", "trained_model_path", "fine_tune"]
    required = ["batch_size", "epochs", "optimizer"]

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="training")

    # Check that there is one and only one model source
    count = 0
    if cfg.model: count += 1
    if cfg.resume_training_from: count += 1
    if model_path_used: count += 1
    if count == 0:
        raise ValueError("\nExpecting either `training.model`, `training.resume_training_from` or "
                         "`general.model_path` attribute\nPlease check your configuration file.")
    if count > 1:
        raise ValueError("\nThe `training.model`, `training.resume_training_from` and `general.model_path` "
                         "attributes are mutually exclusive.\nPlease check your configuration file.")

    if cfg.model:
        required = ["name", "input_shape"]
        check_config_attributes(cfg.model, specs={"all": required}, section="training.model")

    # If resume_training_from is set, check that the model file exists
    if cfg.resume_training_from:
        path = cfg.resume_training_from
        if Path(path).suffix != ".h5":
            raise ValueError("\nExpecting `resume_training_from` attribute to be set to a path to a .h5 model path\n"
                             f"Received path: {path}\n"
                             "Please check the 'training' section of your configuration file.")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"\nUnable to find file {path}\nPlease check the 'training.resume_training_from'"
                                    "attribute in your configuration file")

    # The optimizer may be written on one line. For example: "optimizer: Adam"
    # In this case, we got a string instead of a dictionary.
    if type(cfg.optimizer) == str:
        cfg.optimizer = DefaultMunch.fromDict({cfg.optimizer: None})


def parse_quantization_section(cfg: DictConfig) -> None:
    # cfg: 'quantization' section of the configuration file

    legal = ["quantizer", "quantization_type", "quantization_input_type",
             "quantization_output_type", "export_dir"]
    required = [x for x in legal if x != "export_dir"]

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="quantization")

    # Set default values of missing optional arguments
    if not cfg.export_dir:
        cfg.export_dir = "quantized_models"

    # Check the quantizer name
    if cfg.quantizer != "TFlite_converter":
        raise ValueError(f"\nUnknown or unsupported quantizer. Received `{cfg.quantizer}`\n"
                         "Supported quantizer: TFlite_converter\n"
                         "Please check the 'quantization.quantizer' attribute in your configuration file.")
    
    # Check the quantizer type
    if cfg.quantization_type != "PTQ":
        raise ValueError(f"\nUnknown or unsupported quantization type. Received `{cfg.quantization_type}`\n"
                         "Supported type: PTQ\n"
                         "Please check the 'quantization.quantization_type' attribute in your configuration file.")

    
def parse_prediction_section(cfg: DictConfig) -> None:
    # cfg: 'prediction' section of the configuration file

    legal = ["test_files_path"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="prediction")

    # Check that the directory that contains the audio files exist
    if not os.path.isdir(cfg.test_files_path):
        raise FileNotFoundError("\nUnable to find the directory containing the audio files to predict\n"
                                f"Received path: {cfg.test_files_path}\nPlease check the "
                                "'prediction.test_files_path' attribute in your configuration file.")


def parse_tools_section(cfg: DictConfig) -> None:
    # cfg: 'tools' section of the configuration file

    legal = ["stm32ai", "path_to_cubeIDE"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="tools")

    legal = ["version", "optimization", "on_cloud", "path_to_stm32ai"]
    check_config_attributes(cfg.stm32ai, specs={"legal": legal, "all": legal}, section="tools.stm32ai")


def parse_benchmarking_section(cfg: DictConfig) -> None:
    # cfg: 'benchmarking' section of the configuration file
    
    legal = ["board"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="benchmarking")


def parse_deployment_section(cfg: DictConfig) -> None:
    # cfg: 'deployment' section of the configuration file

    legal = ["c_project_path", "IDE", "verbosity", "hardware_setup", "unknown_class_threshold"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="deployment")
 
    legal = ["serie", "board"]
    check_config_attributes(cfg.hardware_setup, specs={"legal": legal, "all": legal},
                            section="deployment.hardware_setup")


def parse_mlflow_section(cfg: DictConfig) -> None:
    # cfg: 'mlflow' section of the configuration file

    legal = ["uri"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="mlflow")

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
    cfg = DefaultMunch.fromDict(config_dict)

    mode_groups = DefaultMunch.fromDict({
        "training": ["training", "chain_tbqeb", "chain_tqe"],
        "evaluation": ["evaluation", "chain_tbqeb", "chain_tqe", "chain_eqe", "chain_eqeb"],
        "quantization": ["quantization", "chain_tbqeb", "chain_tqe", "chain_eqe",
                         "chain_qb", "chain_eqeb", "chain_qd"],
        "benchmarking": ["benchmarking", "chain_tbqeb", "chain_qb", "chain_eqeb"],
        "deployment": ["deployment", "chain_qd"]
    })

    parse_top_level(cfg, mode_groups=mode_groups)
    print(f"[INFO] : Running `{cfg.operation_mode}` operation mode")

    if not cfg.general:
        cfg.general = DefaultMunch.fromDict({"project_name": "<unnamed>"})
    parse_general_section(cfg.general, mode=cfg.operation_mode, mode_groups=mode_groups)

    if cfg.operation_mode != "benchmarking":
        if not cfg.dataset:
            cfg.dataset = DefaultMunch.fromDict({})
        parse_dataset_section(cfg.dataset, mode=cfg.operation_mode, mode_groups=mode_groups)
        # If dataset is FSD50K, parse its dedicated section
        if cfg.dataset.name.lower() == 'fsd50k':
            parse_dataset_specific_fsd50k_section(cfg.dataset_specific.fsd50k)

        parse_preprocessing_section(cfg.preprocessing)
        parse_feature_extraction_section(cfg.feature_extraction)

    if cfg.operation_mode in mode_groups.training:
        if cfg.data_augmentation:
            parse_data_augmentation_section(cfg)
        model_path_used = True if cfg.general.model_path else False
        parse_training_section(cfg.training, mode=cfg.operation_mode, model_path_used=model_path_used)

    if cfg.operation_mode in mode_groups.quantization:
        parse_quantization_section(cfg.quantization)

    if cfg.operation_mode == "prediction":
        parse_prediction_section(cfg.prediction)

    if cfg.operation_mode in (mode_groups.benchmarking + mode_groups.deployment):
        parse_tools_section(cfg.tools)

    if cfg.operation_mode in mode_groups.benchmarking:
        parse_benchmarking_section(cfg.benchmarking)

    if cfg.operation_mode in mode_groups.deployment:
        parse_deployment_section(cfg.deployment)

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
                print(f"[INFO] Automatically inferred classes {cds.class_names}")
                break
            if not cds.class_names:
                raise ValueError("\nMissing the class names. You can provide in the 'dataset' section either:\n"
                                    " - the class names using the `class_names` attribute\n"
                                    " - a path to a dataset using the `training_path`, `validation_path`, `test_path` or `quantization_path` attribute\n" 
                                    "Please update your configuration file.")

    return cfg
