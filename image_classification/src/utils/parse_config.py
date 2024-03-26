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
from utils import check_attributes, aspect_ratio_dict
from data_loader import check_dataset_integrity, get_class_names
from typing import Dict, List



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
    legal = ["general", "operation_mode", "dataset", "preprocessing", "data_augmentation",
             "custom_data_augmentation", "training", "quantization", "prediction", "tools",
             "benchmarking", "deployment", "mlflow", "hydra"]

    required = ["mlflow"]
    if mode not in mode_groups.training:
        # We need the 'general' section to provide model_path.
        required += ["general",]
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
             "display_figures", "global_seed", "gpu_memory_limit"]

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
    if not cfg.global_seed or cfg.global_seed=='None':
        cfg.global_seed = 123

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
    
    # Paths used in a quantization
    if mode in mode_groups.quantization:
        if cfg.quantization_path:
            dataset_paths["quantization_path"] = cfg.quantization_path
        elif cfg.test_path:
            dataset_paths["test_path"] = cfg.test_path
        elif cfg.training_path:
            dataset_paths["training_path"] = cfg.training_path

    # Check the datasets
    for name in ["training_path", "validation_path", "test_path", "quantization_path"]:
        if name in dataset_paths:
            path = dataset_paths[name]
            if not os.path.isdir(path):
                raise FileNotFoundError(f"\nUnable to find the root directory of the {name[:-5]} set\n"
                                        f"Received path: {path}\n"
                                        "Please check the 'dataset' section of your configuration file.")
            if cfg.check_image_files:
                print(f"[INFO] Checking {path} dataset")
            check_dataset_integrity(path, check_image_files=cfg.check_image_files)
        else:
            # Set to None the paths to datasets that are not needed,
            # otherwise the data loaders would them.
            cfg[name] = None


def parse_dataset_section(cfg: DictConfig, mode: str = None, mode_groups: DictConfig = None) -> None:
    # cfg: dictionary containing the 'dataset' section of the configuration file

    legal = ["name", "class_names", "training_path", "validation_path", "validation_split", "test_path",
             "quantization_path", "quantization_split", "check_image_files", "seed"]

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
    cfg.check_image_files = cfg.check_image_files if cfg.check_image_files is not None else False
    cfg.seed = cfg.seed if cfg.seed else 123

    # Sort the class names if they were provided
    if cfg.class_names:
        cfg.class_names = sorted(cfg.class_names)
    elif cfg.name in ("cifar10", "cifar100", "emnist"):
        cfg.class_names = get_class_names(cfg.name)

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
        
    if cfg.name not in ("emnist", "cifar10", "cifar100"):
        check_dataset_paths_and_contents(cfg, mode=mode, mode_groups=mode_groups)


def parse_preprocessing_section(cfg: DictConfig,
                                mode: str = None) -> None:
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
    if cfg.resizing.aspect_ratio == "fit":
        required = ["interpolation", "aspect_ratio"]
    else:
        required = ["aspect_ratio"]

    check_config_attributes(cfg.resizing, specs={"legal": legal, "all":required}, section="preprocessing.resizing")

    # Check the of aspect ratio value
    aspect_ratio = cfg.resizing.aspect_ratio
    if aspect_ratio not in aspect_ratio_dict:
        raise ValueError(f"\nUnknown or unsupported value for `aspect_ratio` attribute. Received {aspect_ratio}\n"
                         f"Supported values: {list(aspect_ratio_dict.keys())}.\n"
                         "Please check the 'preprocessing.resizing' section of your configuration file.")

    if aspect_ratio == "fit":
        # Check resizing interpolation value
        check_config_attributes(cfg.resizing, specs={"all": ["interpolation"]}, section="preprocessing.resizing")
        interpolation_methods = ["bilinear", "nearest", "area", "lanczos3", "lanczos5", "bicubic", "gaussian", "mitchellcubic"]
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


def parse_training_section(cfg: DictConfig, mode: str = None, model_path_used: bool = None) -> None:
    # cfg: 'training' section of the configuration file
    # model_path: general.model_path attribute

    legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
             "callbacks", "resume_training_from", "trained_model_path"]
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

    legal = ["test_images_path"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="prediction")

    # Check that the directory that contains the images exist
    if not os.path.isdir(cfg.test_images_path):
        raise FileNotFoundError("\nUnable to find the directory containing the images to predict\n"
                                f"Received path: {cfg.test_images_path}\nPlease check the "
                                "'prediction.test_images_path' attribute in your configuration file.")


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

    legal = ["c_project_path", "IDE", "verbosity", "hardware_setup"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="deployment")
 
    legal = ["serie", "board", "input", "output"]
    check_config_attributes(cfg.hardware_setup, specs={"legal": legal, "all": legal},
                            section="deployment.hardware_setup")


def parse_mlflow_section(cfg: DictConfig) -> None:
    # cfg: 'mlflow' section of the configuration file

    legal = ["uri"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="mlflow")


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

    if not cfg.dataset:
        cfg.dataset = DefaultMunch.fromDict({})
    parse_dataset_section(cfg.dataset, mode=cfg.operation_mode, mode_groups=mode_groups)

    parse_preprocessing_section(cfg.preprocessing, mode=cfg.operation_mode)

    if cfg.operation_mode in mode_groups.training:
        if cfg.data_augmentation or cfg.custom_data_augmentation:
            parse_data_augmentation_section(cfg, config_dict)
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

    cds = cfg.dataset
    if not cds.class_names and cfg.operation_mode not in ("quantization", "benchmarking", "chain_qb"):
        # Infer the class names from a dataset
        for path in [cds.training_path, cds.validation_path, cds.test_path, cds.quantization_path]:
            if path:
                cds.class_names = get_class_names(dataset_root_dir=path)
                print("[INFO] : Found {} classes in dataset {}".format(len(cds.class_names), path))
                break
        # This should not happen. Just in case.
        if not cds.class_names:
            raise ValueError("\nMissing `class_names` attribute\nPlease check the 'dataset' section of your configuration file.")

    return cfg
