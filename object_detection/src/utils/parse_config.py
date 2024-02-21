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
from utils import check_attributes
from typing import Dict


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

    mode_choices = ["training", "evaluation", "deployment",
                    "quantization", "benchmarking", "chain_tqeb", "chain_tqe",
                    "chain_eqe", "chain_qb", "chain_eqeb", "chain_qd", "prediction"]

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
             "training", "postprocessing", "quantization", "tools",
             "benchmarking", "deployment", "mlflow", "hydra"]

    required = ["mlflow"]
    if mode not in mode_groups.training:
        # We need the 'general' section to provide model_path.
        required += ["general", ]
    if mode not in ("quantization", "benchmarking", "deployment", "chain_qb", "chain_qd"):
        required += ["dataset", ]
    if mode in mode_groups.training:
        required += ["training", ]
    if mode in mode_groups.quantization:
        required += ["quantization", ]
    if mode in mode_groups.benchmarking:
        required += ["benchmarking", "tools"]
    if mode in mode_groups.deployment:
        required += ["deployment", "tools"]

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="top_level")


def parse_general_section(cfg: DictConfig, mode: str = None, mode_groups=None) -> None:
    # cfg: dictionary containing the 'general' section of the configuration file

    legal = ["project_name", "model_path", "logs_dir", "saved_models_dir", "deterministic_ops",
             "display_figures", "global_seed", "gpu_memory_limit", "model_type"]

    # Usage of the model_path attribute in training modes 
    # is checked when parsing the 'training' section.
    required = ["model_type"]
    required.append("model_path") if not mode_groups.training else []
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="general")

    # Set default values of missing optional attributes
    if not cfg.model_type:
        raise ValueError(f"\nPlease select a model_type in the general section.")
    if not cfg.project_name:
        cfg.project_name = "<unnamed>"
    if not cfg.logs_dir:
        cfg.logs_dir = "logs"
    if not cfg.saved_models_dir:
        cfg.saved_models_dir = "saved_models"
    cfg.deterministic_ops = cfg.deterministic_ops if cfg.deterministic_ops is not None else False
    cfg.display_figures = cfg.display_figures if cfg.display_figures is not None else True
    if not cfg.global_seed:
        cfg.global_seed = 123

    ml_path = cfg.model_path

    if mode not in mode_groups.training:
        file_extension = Path(ml_path).suffix if ml_path else ""
        m1 = "\nExpecting `model_path` to be set to a path to a "
        m2 = f" model file when running '{mode}' operation mode\n"
        if ml_path:
            m2 += f"Received path: {ml_path}\n"
        m2 += "Please check the 'general' section of your configuration file."

        if mode in mode_groups.quantization:
            if not ml_path or file_extension != ".h5":
                raise ValueError(m1 + ".h5" + m2)
        elif mode in ("evaluation"):
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

    legal = ["name", "class_names", "training_path", "validation_path", "validation_split", "test_path",
             "quantization_path", "quantization_split", "seed"]

    required = []
    one_or_more = []
    if mode in mode_groups.training:
        required += ["training_path", ]
    elif mode in mode_groups.evaluation:
        one_or_more += ["training_path", "test_path"]
    if mode not in ("quantization", "benchmarking", "chain_qb"):
        required += ["class_names", ]
    check_config_attributes(cfg, specs={"legal": legal, "all": required, "one_or_more": one_or_more},
                            section="dataset")

    # Set default values of missing optional attributes
    if not cfg.name:
        cfg.name = "<unnamed>"
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


def parse_preprocessing_section(cfg: DictConfig) -> None:
    # cfg: 'preprocessing' section of the configuration file

    legal = ["rescaling", "resizing", "color_mode"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="preprocessing")

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


def parse_training_section(cfg: DictConfig, saved_models_dir: str = None) -> None:
    # cfg: 'training' section of the configuration file

    legal = ["model", "batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
             "callbacks", "trained_model_path"]
    required = ["batch_size", "epochs", "optimizer"]

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="training")

    # # Check that there is one and only one model source
    # message = "\nPlease check the 'training' section of your configuration file."
    # count = 0
    # if cfg.model: count += 1
    # if cfg.resume_training_from: count += 1
    # if count == 0:
    #     raise ValueError(f"\nExpecting either `model` or `resume_training_from` attribute{message}")
    # if count > 1:
    #     raise ValueError(f"\nThe `model` and `resume_training_from` attributes are mutually exclusive.{message}\n")

    if cfg.model:
        required = ["input_shape"]
        check_config_attributes(cfg.model, specs={"all": required}, section="training.model")

    # if cfg.resume_training_from:
    #     path = cfg.resume_training_from
    #     if not os.path.isdir(path):
    #         raise FileNotFoundError("\nUnable to find `resume_training_from` directory\n"
    #                                 f"Received path: {path}{message}")
    #     path = os.path.join(cfg.resume_training_from, saved_models_dir)
    #     if not os.path.isdir(path):
    #         raise FileNotFoundError(f"\nUnable to find directory {path}{message}")

    # The optimizer may be written on one line. For example: "optimizer: Adam"
    # In this case, we got a string instead of a dictionary.
    if type(cfg.optimizer) == str:
        cfg.optimizer = DefaultMunch.fromDict({cfg.optimizer: None})


def parse_postprocessing_section(cfg: DictConfig) -> None:
    # cfg: 'postprocessing' section of the configuration file

    legal = ["confidence_thresh", "NMS_thresh", "IoU_eval_thresh", "yolo_anchors", "plot_metrics",
             'max_detection_boxes']
    required = ["confidence_thresh", "NMS_thresh", "IoU_eval_thresh"]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="postprocessing")

    if not cfg.yolo_anchors:
        cfg.yolo_anchors = [0.076023, 0.258508, 0.163031, 0.413531, 0.234769, 0.702585, 0.427054, 0.715892, 0.748154, 0.857092]

    cfg.plot_metrics = cfg.plot_metrics if cfg.plot_metrics is not None else False


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

    legal = ["serie", "board"]
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
        "training": ["training", "chain_tqeb", "chain_tqe"],
        "evaluation": ["evaluation", "chain_tqeb", "chain_tqe", "chain_eqe", "chain_eqeb"],
        "quantization": ["quantization", "chain_tqeb", "chain_tqe", "chain_eqe",
                         "chain_qb", "chain_eqeb", "chain_qd"],
        "benchmarking": ["benchmarking", "chain_tqeb", "chain_qb", "chain_eqeb"],
        "deployment": ["deployment", "chain_qd"],
        "prediction": ["prediction"]
    })

    parse_top_level(cfg, mode_groups=mode_groups)
    print(f"[INFO] : Running `{cfg.operation_mode}` operation mode")

    if not cfg.general:
        cfg.general = DefaultMunch.fromDict({})
    parse_general_section(cfg.general, mode=cfg.operation_mode, mode_groups=mode_groups)

    if not cfg.dataset:
        cfg.dataset = DefaultMunch.fromDict({})
    parse_dataset_section(cfg.dataset, mode=cfg.operation_mode, mode_groups=mode_groups)

    parse_preprocessing_section(cfg.preprocessing)

    if cfg.operation_mode in mode_groups.training and cfg.data_augmentation:
        parse_data_augmentation_section(cfg.data_augmentation)

    if cfg.operation_mode in mode_groups.training:
        parse_training_section(cfg.training, saved_models_dir=cfg.general.saved_models_dir)

    if cfg.operation_mode in (mode_groups.training + mode_groups.evaluation + mode_groups.quantization + mode_groups.deployment + mode_groups.prediction):
        parse_postprocessing_section(cfg.postprocessing)

    if cfg.operation_mode in mode_groups.quantization:
        parse_quantization_section(cfg.quantization)

    if cfg.operation_mode in (mode_groups.benchmarking + mode_groups.deployment):
        parse_tools_section(cfg.tools)

    if cfg.operation_mode in mode_groups.benchmarking:
        parse_benchmarking_section(cfg.benchmarking)

    if cfg.operation_mode in mode_groups.deployment:
        parse_deployment_section(cfg.deployment)

    parse_mlflow_section(cfg.mlflow)

    return cfg
