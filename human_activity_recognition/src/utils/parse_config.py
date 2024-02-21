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
from utils import check_attributes
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
            raise OSError("\nCould not find an environment variable named "
                          f"`{var_name}`\n""Please check your configuration file.")
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
        if isinstance(v, dict):
            postprocess_config_dict(v)
        elif isinstance(v, str):
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
        message = "\nPlease check the top-level of your configuration file."
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
    '''
    parses the dictionary containing entire configuration file

    args:
        cfg: (DictConfig) configuration dictionary containing entire configuration file
        mode_group: (DictConfig) configuration about a given mode
    '''
    # cfg: dictionary containing the entire configuration file

    mode_choices = ["training", "evaluation", "deployment", "benchmarking", "chain_tb"]

    # Check that operation_mode is present and has a value
    message = "\nPlease check the top-level of your configuration file."
    if "operation_mode" not in cfg:
        raise ValueError("\nMissing `operation_mode` attribute\n"
                         "Supported modes: {mode_choices}{message}")
    if cfg.operation_mode is None:
        raise ValueError("\nExpecting a value for `operation_mode` attribute\n"
                         f"Supported modes: {mode_choices}{message}")

    # Check that the value of operation_mode is valid
    mode = cfg.operation_mode
    if mode not in mode_choices:
        raise ValueError(f"\nUnknown value for `operation_mode` attribute. Received {mode}\n"
                         f"Supported modes: {mode_choices}{message}")

    # Attributes usable at the top level
    legal = ["general", "operation_mode", "dataset", "preprocessing", "training",
             "prediction", "tools", "benchmarking", "deployment", "mlflow"]

    required = ["mlflow"]
    if mode not in mode_groups.training:
        # We need the 'general' section to provide model_path.
        required += ["general",]
    if mode not in ( "benchmarking", "deployment"):
        required += ["dataset",]
    if mode in mode_groups.training:
        required += ["training", "preprocessing"]
    if mode in mode_groups.benchmarking:
        required += ["benchmarking", "tools"]
    if mode in mode_groups.deployment:
        required += ["deployment", "tools"]

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="top_level")


def parse_general_section(cfg: DictConfig, mode: str = None, mode_groups=None) -> None:
    '''
    parses the general section of configuration file.
    args:
        cfg (DictConfig): configuration dictionary
        mode (str): operation mode
        mode_groups(str): operation mode group
    '''

    legal = ["project_name", "model_path", "logs_dir", "saved_models_dir", "deterministic_ops",
             "display_figures", "global_seed", "gpu_memory_limit"]

    # Usage of the model_path attribute in training modes
    # is checked when parsing the 'training' section.
    required = ["model_path"] if not mode_groups.training else []
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="general")

    # Set default values of missing optional attributes
    if not cfg.project_name:
        cfg.project_name = "human_activity_recognition"
    if not cfg.logs_dir:
        cfg.logs_dir = "logs"
    if not cfg.saved_models_dir:
        cfg.saved_models_dir = "saved_models"
    cfg.deterministic_ops = cfg.deterministic_ops if cfg.deterministic_ops is not None else False
    cfg.display_figures = cfg.display_figures if cfg.display_figures is not None else True
    if not cfg.global_seed:
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
    elif mode in ("evaluation"):
        if not ml_path or file_extension not in (".h5"):
            raise ValueError(m1 + "\'.h5\'" + m2)
    elif mode in ("benchmarking"):
        if not ml_path or file_extension not in (".h5", ".tflite", ".onnx"):
            raise ValueError(m1 + "\'.h5\', \'.tflite\' or \'.onnx\'" + m2)
    elif mode in ("deployment"):
        if not ml_path or file_extension not in (".h5"):
            raise ValueError(m1 +  "\'.h5\'"  + m2)

    # If model_path is set, check that the model file exists.
    if ml_path and not os.path.isfile(ml_path):
        raise FileNotFoundError(f"\nUnable to find file {ml_path}\n"
                                "Please check the \'general.model_path\'"
                                "attribute in your configuration file.")


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


def parse_training_section(cfg: DictConfig, mode: str = None, model_path_used: bool = None) -> None:
    '''
    parses the training section of the configuraiton dictionary
    args:
        cfg (DictConfig): 'training' section of the configuration file
        mode (str): operation mode
        model_path_used (bool): a flag to tell if the 'general.model_path' parameter is provided    
    '''
    legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
             "callbacks", "resume_training_from", "trained_model_path"]
    required = ["batch_size", "epochs", "optimizer"]

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="training")

    # Check that there is one and only one model source
    count = 0
    if cfg.model:
        count += 1
    if cfg.resume_training_from:
        count += 1
    if model_path_used:
        count += 1
    if count == 0:
        raise ValueError("\nExpecting either `training.model`, `training.resume_training_from` or "
                         "`general.model_path` attribute\nPlease check your configuration file.")
    if count > 1:
        raise ValueError("\nThe `training.model`, `training.resume_training_from`"
                         " and `general.model_path` attributes are mutually exclusive."
                         "\nPlease check your configuration file.")

    if cfg.model:
        required = ["name", "input_shape"]
        check_config_attributes(cfg.model, specs={"all": required}, section="training.model")

    # If resume_training_from is set, check that the model file exists
    if cfg.resume_training_from:
        path = cfg.resume_training_from
        if Path(path).suffix != ".h5":
            raise ValueError("\nExpecting `resume_training_from` attribute to be set to a path to a"
                             f" .h5 model path\nReceived path: {path}\n"
                             "Please check the 'training' section of your configuration file.")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"\nUnable to find file {path}\n"
                                    "Please check the 'training.resume_training_from'"
                                    "attribute in your configuration file")

    # The optimizer may be written on one line. For example: "optimizer: Adam"
    # In this case, we got a string instead of a dictionary.
    if isinstance(cfg.optimizer, str):
        cfg.optimizer = DefaultMunch.fromDict({cfg.optimizer: None})



def parse_tools_section(cfg: DictConfig, operation_mode: str) -> None:
    '''
    parses the 'tools' section of the configuration file
    args:
        cfg (DictConfig): 'tools' section of configuration file
    '''

    legal = ["stm32ai", "path_to_cubeIDE"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="tools")

    legal = ["version", "optimization", "on_cloud", "path_to_stm32ai"]
    check_config_attributes(cfg.stm32ai, 
                            specs={"legal": legal, "all": legal}, section="tools.stm32ai")
    if not cfg.stm32ai.on_cloud:
        if not os.path.isfile(cfg.stm32ai.path_to_stm32ai):
            raise ValueError("Path for `stm32ai.exe` does not exist.\n"
                             "Please check the cfg.tools.stm32ai section!")
    if operation_mode == "deployment" and not os.path.isfile(cfg.path_to_cubeIDE):
        raise ValueError("Path for `path_to_cubeIDE` does not exist.\n"
                             "Please check the cfg.tools section!")


def parse_benchmarking_section(cfg: DictConfig) -> None:
    '''
    parses the 'benchmarking' section of the configuration file
    args:
        cfg (DictConfig): 'benchmarking' section of the configuration file
    '''
    legal = ["board"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="benchmarking")


def parse_deployment_section(cfg: DictConfig) -> None:
    '''
    parses the 'deployment' section of the configuration file
    args:
        cfg (DictConfig): 'deployment' section of the configuration file
    '''
    legal = ["c_project_path", "IDE", "verbosity", "hardware_setup"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="deployment")

    legal = ["serie", "board"]
    check_config_attributes(cfg.hardware_setup, specs={"legal": legal, "all": legal},
                            section="deployment.hardware_setup")


def parse_mlflow_section(cfg: DictConfig) -> None:
    '''
    parses the mlflow section of configuration
    args:
        cfg (DictConfig): 'mlflow' section of the configuration
    '''
    legal = ["uri"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="mlflow")


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
    cfg = DefaultMunch.fromDict(config_dict)

    mode_groups = DefaultMunch.fromDict({
        "training": ["training", "chain_tb"],
        "evaluation": ["evaluation"],
        "benchmarking": ["benchmarking", "chain_tb"],
        "deployment": ["deployment"]
    })

    parse_top_level(cfg, mode_groups=mode_groups)
    print(f"[INFO] : Running `{cfg.operation_mode}` operation mode")

    if not cfg.general:
        cfg.general = DefaultMunch.fromDict({"project_name": "human_activity_recognition"})
    parse_general_section(cfg.general, mode=cfg.operation_mode, mode_groups=mode_groups)

    if not cfg.dataset:
        cfg.dataset = DefaultMunch.fromDict({})
    parse_dataset_section(cfg.dataset, mode=cfg.operation_mode, mode_groups=mode_groups)
    
    if not cfg.operation_mode in mode_groups.benchmarking:
        parse_preprocessing_section(cfg.preprocessing)

    if cfg.operation_mode in mode_groups.training:
        model_path_used = bool(cfg.general.model_path)
        parse_training_section(cfg.training, mode=cfg.operation_mode,
                               model_path_used=model_path_used)

    if cfg.operation_mode in (mode_groups.benchmarking + mode_groups.deployment):
        parse_tools_section(cfg.tools, cfg.operation_mode)

    if cfg.operation_mode in mode_groups.benchmarking:
        parse_benchmarking_section(cfg.benchmarking)

    if cfg.operation_mode in mode_groups.deployment:
        parse_deployment_section(cfg.deployment)

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
