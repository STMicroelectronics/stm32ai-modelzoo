#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
from typing import Dict, List
from munch import DefaultMunch
from omegaconf import DictConfig
from pathlib import Path
import re


aspect_ratio_dict = {"fit": "ASPECT_RATIO_FIT", 
                     "crop": "ASPECT_RATIO_CROP", 
                     "padding": "ASPECT_RATIO_PADDING"}


def check_attributes(cfg: Dict, 
                     expected: List[str] = None, 
                     optional: List[str] = [], 
                     section: str = None) -> None:
    '''
    Checks that all the expected attributes are present in the configuration dictionary and that
    there are no unknown attributes. Optional attributes may also be present.
    args:
        cfg (dict): The configuration dictionary.
        expected (list): A list of expected (required) attributes.
        optional (list, optional): A list of optional attributes. Defaults to [].
        section (str, optional): The name of the config file section to check. Defaults to None.
    raises:
        ValueError: If an unknown or unsupported attribute is found or if a required attribute is missing.
    '''
    if section is not None:
        message = "\nPlease check the '{}' section of your configuration file.".format(section)
    else:
        message = "\nPlease check your configuration file."

    if cfg is not None:
        if type(cfg) != DefaultMunch:
            raise ValueError("Expecting an attribute. Received {}{}".format(cfg, message))
        # Check that each attribute name is legal.
        for attr in cfg.keys():
            if (not attr in expected) and (not attr in optional):
                raise ValueError("\nUnknown or unsupported attribute. Received `{}`{}".format(attr, message))
        # Get the list of used attributes
        used = list(cfg.keys())
    else:
        used = []

    # Check that all the mandatory attributes are present.
    for attr in expected:
        if attr not in used:
            raise ValueError("\nMissing `{}` attribute{}".format(attr, message))
        if cfg[attr] is None:
            raise ValueError("\nMissing a value for attribute `{}`{}".format(attr, message))
        

def collect_callback_args(name, 
                          args=None, 
                          message=None) -> str:
    if args:
        if type(args) != DefaultMunch:
            raise ValueError(f"\nInvalid syntax for `{name}` callback arguments{message}")
        text = "("
        for k, v in args.items():
            if type(v) == str and v[:7] != "lambda ":
                text += f'{k}=r"{v}", '
            else:
                text += f'{k}={v}, '
        text = text[:-2] + ")"
    else:
        text = "()"
    return text


def get_random_seed(cfg: DictConfig = None):
    '''
    Returns a random seed based on the configuration file.
    args:
        cfg (DictConfig): The configuration object.
    returns:
        int or None: The random seed. If no seed is set in the configuration file, returns 0.
    '''
    if "global_seed" in cfg.general:
        seed = cfg.general["global_seed"]
        if seed == "None":
            seed = None
        else:
            seed = int(seed)
    else:
        seed = 0
    return seed


def replace_none_string(dico: dict) -> dict:
    '''
    Replaces None strings in the values of a dictionary with the Python None value.
       Other values are unchanged.
    args:
        dico (dict): any dictionary.
    '''
    for k, v in dico.items():
        if v == "None":
            dico[k] = None
    return dico


def expand_env_vars(string: str) -> str:
    '''
    Expands environment variables in a string if any. The syntax for variables
    is ${variable_name}. An error is thrown if a variable is found in the string
    but is not set.
    args:
        string (str): The string to expand environment variables in.
    returns:
        string (str): The original string with expanded variables.
    '''
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
    '''
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
    args:
        config (DictConfig): dictionary containing the entire configuration file.
    '''
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


def check_config_attributes(cfg: DictConfig, 
                            specs: Dict = None, 
                            section: str = None) -> None:
    '''
    This function checks that the attributes used in a given section
    of the configuration file comply with specified requirements.
    args:
        cfg (DictConfig): dictionary containing the configuration file section to check
        specs (Dict): dictionary specifying the requirements for attribute usage in the section
        section (str): name of the section
    '''
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


def parse_tools_section(cfg: DictConfig, 
                        operation_mode: str,
                        hardware_type: str ="MCU") -> None:
    '''
    parses the 'tools' section of the configuration file
    args:
        cfg (DictConfig): 'tools' section of configuration file
        operation_mode (str): service or operation mode used
        hardware_type (str): type of hardware targetted
    '''
    required = []
    if hardware_type == "MCU":
        required += ["path_to_cubeIDE",]
    legal = ["stm32ai", "stedgeai", "path_to_cubeIDE"]
    one_or_more = ["stm32ai", "stedgeai"]
    check_config_attributes(cfg, specs={"legal": legal, "all": required, "one_or_more": one_or_more}, section="tools")

    if cfg.stm32ai:
        # Legacy stm32ai usage
        legal = ["version", "optimization", "on_cloud", "path_to_stm32ai"]
        check_config_attributes(cfg.stm32ai, 
                                specs={"legal": legal, "all": legal}, section="tools.stm32ai")
        if not cfg.stm32ai.on_cloud:
            if not os.path.isfile(cfg.stm32ai.path_to_stm32ai):
                raise ValueError("Path for `stm32ai.exe` does not exist.\n"
                                "Please check the cfg.tools.stm32ai section!")
    else:
        # stedgeai usage
        legal = ["version", "optimization", "on_cloud", "path_to_stedgeai"]
        check_config_attributes(cfg.stedgeai, 
                                specs={"legal": legal, "all": legal}, section="tools.stedgeai")
        if not cfg.stedgeai.on_cloud:
            if not os.path.isfile(cfg.stedgeai.path_to_stedgeai):
                raise ValueError("Path for `stedgeai.exe` does not exist.\n"
                                "Please check the cfg.tools.stedgeai section!")
        # Patch to support stedgeai with legacy naming stm32ai : reconstruct stm32ai dictionnary
        # from stedgeai one
        cfg["stm32ai"] = cfg.stedgeai
        cfg.stm32ai["version"] = cfg.stedgeai.version
        cfg.stm32ai["optimization"] = cfg.stedgeai.optimization
        cfg.stm32ai["on_cloud"] = cfg.stedgeai.on_cloud
        cfg.stm32ai["path_to_stm32ai"] = cfg.stedgeai.path_to_stedgeai
    
    # Path to cubeIDE only needed for MCU in deployment service
    if hardware_type == "MCU":
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


def parse_quantization_section(cfg: DictConfig, 
                               legal: List) -> None:
    '''
    parses the dictionary containing entire configuration file
    args:
        cfg (DictConfig): 'quantization' section of the configuration file
        legal (List): UC specific usable attributes
    '''
    required = [x for x in legal if x not in ["export_dir", "granularity", "optimize", "target_opset"]]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="quantization")

    # Set default values of missing optional arguments
    if not cfg.export_dir:
        cfg.export_dir = "quantized_models"
    if not cfg.granularity:
        cfg.granularity = "per_channel"
    cfg.optimize = cfg.optimize if cfg.optimize is not None else False
    cfg.target_opset = cfg.target_opset if cfg.target_opset is not None else 17

    # Check the quantizer name
    if cfg.quantizer.lower() not in ["tflite_converter", "onnx_quantizer"]:
        raise ValueError(f"\nUnknown or unsupported quantizer. Received `{cfg.quantizer}`\n"
                         "Supported quantizers are : TFlite_converter or Onnx_quantizer\n"
                         "Please check the 'quantization.quantizer' attribute in your configuration file.")

    # Check the granularity value
    if cfg.granularity not in ['per_channel', 'per_tensor']:
        raise ValueError(f"\nUnknown or unsupported granularity value. Received `{cfg.granularity}`\n"
                         "Supported granularity: 'per_channel, or 'per_tensor'\n"
                         "Please check the 'quantization.granularity' attribute in your configuration file.")
    # Check optimization
    if cfg.optimize not in [True, False]:
        raise ValueError(f"\nUnknown or unsupported optimize value. Received `{cfg.optimize}`\n"
                         "Supported optimize parameters: 'True', or 'False'\n"
                         "Please check the 'quantization.optimize' attribute in your configuration file.")

    if not isinstance(cfg.target_opset, int):
        raise ValueError(f"\nUnknown or unsupported target_opset value. Received `{cfg.optimize}`\n"
                         "Supported target_opset parameters: 'int' upto latest onnx_opset\n"
                         "Please check the 'quantization.target_opset' attribute in your configuration file.")
    # Check the quantizer type
    if cfg.quantization_type.lower() not in ["ptq"]:
        raise ValueError(f"\nUnknown or unsupported quantization type. Received `{cfg.quantization_type}`\n"
                         "Supported type: PTQ\n"
                         "Please check the 'quantization.quantization_type' attribute in your configuration file.")


def parse_top_level(cfg: DictConfig, 
                    mode_groups: DictConfig = None,
                    mode_choices: List = None, 
                    legal: List = None) -> None:
    '''
    parses the dictionary containing entire configuration file
    args:
        cfg (DictConfig): configuration dictionary containing entire configuration file
        mode_groups (DictConfig): configuration about a given mode
        mode_choices (List): currently supported modes
        legal (List): UC specific usable attributes
    '''
    # Check that operation_mode is present and has a value
    message = "\nPlease check the top-level of your configuration file."
    if "operation_mode" not in cfg:
        raise ValueError("\nMissing `operation_mode` attribute\n"
                         "Supported modes: {mode_choices}{message}")
    if cfg.operation_mode is None:
        raise ValueError("\nExpecting a value for `operation_mode` attribute\n"
                         "Supported modes: {mode_choices}{message}")

    # Check that the value of operation_mode is valid
    mode = cfg.operation_mode
    if mode not in mode_choices:
        raise ValueError(f"\nUnknown value for `operation_mode` attribute. Received {mode}\n"
                         f"Supported modes: {mode_choices}{message}")

    # Attributes usable at the top level
    required = ["mlflow"]
    if mode not in mode_groups.training:
        # We need the 'general' section to provide model_path.
        required += ["general",]
    if mode != "benchmarking":
        # Need the preprocessing & feature extraction sections (when available)
        required += ["preprocessing"]
        if "feature_extraction" in legal:
            required += ["feature_extraction"]
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


def parse_general_section(cfg: DictConfig, 
                          mode: str = None, 
                          mode_groups: str = None,
                          legal: List = None,
                          required: List = None) -> None:
    '''
    parses the general section of configuration file.
    args:
        cfg (DictConfig): configuration dictionary
        mode (str): operation mode
        mode_groups (str): operation mode group
        legal (List): UC specific usable attributes
        required (List): UC specific required attributes
    '''
    # Usage of the model_path attribute in training modes
    # is checked when parsing the 'training' section.
    required.append("model_path") if not mode_groups.training else []
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
    if not cfg.global_seed or cfg.global_seed == 'None':
        cfg.global_seed = 123

    if not cfg.num_threads_tflite:
        cfg.num_threads_tflite = 1
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
        if not ml_path or file_extension not in [".h5", ".onnx"]:
            raise ValueError(m1 + ".h5 or .onnx" + m2)
    elif mode in ("evaluation", "prediction"):
        if not ml_path or file_extension not in (".h5", ".tflite", ".onnx"):
            raise ValueError(m1 + ".h5, .tflite or onnx" + m2)
    elif mode in ("benchmarking"):
        if not ml_path or file_extension not in (".h5", ".tflite", ".onnx"):
            raise ValueError(m1 + ".h5, .tflite or .onnx" + m2)
    elif mode in ("deployment"):
        if not ml_path or file_extension not in (".h5", ".tflite", ".onnx"):
            raise ValueError(m1 + ".h5, .tflite or .onnx" + m2)

    # If model_path is set, check that the model file exists.
    if ml_path and not os.path.isfile(ml_path):
        raise FileNotFoundError(f"\nUnable to find file {ml_path}\n"
                                "Please check the \'general.model_path\'"
                                "attribute in your configuration file.")


def parse_training_section(cfg: DictConfig, 
                           model_path_used: bool = None, 
                           model_type_used: bool = None,
                           legal: List = None) -> None:
    '''
    parses the training section of configuration file.
    args:
        cfg (DictConfig): 'training' section of the configuration file
        model_path_used (bool): a flag to tell if the 'general.model_path' parameter is provided
        model_type_used (bool): a flag to tell if the 'general.model_type' parameter is provided
        legal (List): usable attributes
    '''
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
        required = ["input_shape"]
        required.append("name") if not model_type_used else []
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


def parse_prediction_section(cfg: DictConfig) -> None:
    '''
    parses the prediction section of configuration file.
    args:
        cfg (DictConfig): 'prediction' section of the configuration file
    '''
    legal = ["test_files_path"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="prediction")

    # Check that the directory that contains the prediction tests files exist
    if not os.path.isdir(cfg.test_files_path):
        raise FileNotFoundError("\nUnable to find the directory containing the test files to predict\n"
                                f"Received path: {cfg.test_files_path}\nPlease check the "
                                "'prediction.test_files_path' attribute in your configuration file.")


def parse_deployment_section(cfg: DictConfig,
                             legal: List = None,
                             legal_hw: List = None) -> None:
    '''
    parses the training section of configuration file.
    args:
        cfg (DictConfig): 'deployment' section of the configuration file
        legal (List): usable attributes
        legal_hw (List): usable attributes for the HW setup part
    '''
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="deployment")
    required = [x for x in legal_hw if x != 'stlink_serial_number']
    check_config_attributes(cfg.hardware_setup, specs={"legal": legal_hw, "all": required},
                            section="deployment.hardware_setup")


def parse_mlflow_section(cfg: DictConfig) -> None:
    '''
    parses the mlflow section of configuration
    args:
        cfg (DictConfig): 'mlflow' section of the configuration
    '''
    legal = ["uri"]
    check_config_attributes(cfg, specs={"legal": legal, "all": legal}, section="mlflow")


def check_hardware_type(cfg: DictConfig, 
                        mode_groups: DictConfig = None) -> None:
    '''
    parses the mlflow section of configuration
    args:
        cfg (DictConfig): dictionary containing the configuration file section to check
        mode_groups (DictConfig): configuration about a given mode
    '''
    # By default MCU is selected
    cfg["hardware_type"] = "MCU"

    # Check if a MPU target is specified in the configuration
    if cfg.operation_mode in mode_groups.benchmarking:
        if cfg.benchmarking.board is not None:
            if "STM32MP" in cfg.benchmarking.board:
                cfg.hardware_type = "MPU"
    elif cfg.operation_mode in mode_groups.deployment:
        if cfg.deployment.hardware_setup.serie is not None:
            if "STM32MP" in cfg.deployment.hardware_setup.serie:
                cfg.hardware_type = "MPU"

