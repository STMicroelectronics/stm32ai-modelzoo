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
import numpy as np
import requests
from hydra.core.hydra_config import HydraConfig


aspect_ratio_dict = {"fit": "ASPECT_RATIO_FIT",
                     "crop": "ASPECT_RATIO_CROP",
                     "padding": "ASPECT_RATIO_PADDING",
                     "full_screen": "ASPECT_RATIO_FULLSCREEN"}
                     
color_mode_n6_dict = {"rgb": "COLOR_RGB",
                      "bgr": "COLOR_BGR"}
                      


def download_file(url:str, local_path:str):
    """
    Downloads a file from the given URL and saves it to the specified local path.
    args:
        url (str): URL of the file to download
        local_path(str): Local path where the file should be saved
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True, timeout=20) # timeout of 20 seconds

        # Check if the request was successful
        response.raise_for_status()

        # Open the local file in write-binary mode
        with open(local_path, 'wb') as file:
            # Iterate over the response content in chunks
            for chunk in response.iter_content(chunk_size=8192):
                # Write each chunk to the local file
                file.write(chunk)

        print(f"[INFO] : Pretrained model file downloaded successfully and saved as :\n\t{local_path}")

    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] : HTTP error occurred :\n\t{http_err}")
    except Exception as err:
        print(f"[ERROR] : An error occurred while downloading the pretrained model \n\t: {err}")


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
    for match in re.findall(r'\$\{\w+\}', string):
        var_name = match[2:-1]
        # Get the variable value, throw an error if it is not set.
        var_value = os.environ.get(var_name)
        if var_value is None:
            raise OSError("\nCould not find an environment variable named `{}`\n"
                          "Please check your configuration file.".format(var_name))
        match = "\\" + match
        string = re.sub(match, var_value, string, count=1)
    return string


def postprocess_config_dict(config: DictConfig, replace_none_string=False) -> None:
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
            postprocess_config_dict(v, replace_none_string=replace_none_string)
        elif type(v) == str:
            if replace_none_string and v.lower() == "none":
                config[k] = None
                continue
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


def check_model_file_extension(ml_path, mode, mode_groups, field_name):
    """
    Validates the file extension and existence of a model file path according to the current operation mode.

    Args:
        ml_path (str): Path to the model file to check.
        mode (str): The current operation mode (e.g., 'training', 'quantization', etc.).
        mode_groups (Any): An object with attributes for each mode group, each being a list of mode names.
        field_name (str): The name of the config field being checked (for error messages).

    Raises:
        ValueError: If the file extension is not allowed for the current mode, or if the path is not provided.
        FileNotFoundError: If the file does not exist at the given path.
    """
    m1 = f"\nExpecting `{field_name}` attribute to be set to a path to "
    m2 = "\nPlease check the 'model' section of your configuration file."
    if not ml_path:
        raise ValueError(m1 + "a valid file path" + m2)
    file_extension = Path(ml_path).suffix.lower()
    if mode in mode_groups.training:
        allowed = [".h5", ".keras"]
        if file_extension not in allowed:
            raise ValueError(m1 + ", ".join(allowed) + m2)
    elif mode in mode_groups.quantization:
        allowed = [".h5", ".keras", ".onnx"]
        if file_extension not in allowed:
            raise ValueError(m1 + ", ".join(allowed) + m2)
    elif mode in ("evaluation", "prediction"):
        allowed = [".h5", ".keras", ".tflite", ".onnx"]
        if file_extension not in allowed:
            raise ValueError(m1 + ", ".join(allowed) + m2)
    elif mode in ("benchmarking", "deployment"):
        allowed = [".h5", ".keras", ".tflite", ".onnx"]
        if file_extension not in allowed:
            raise ValueError(m1 + ", ".join(allowed) + m2)
    if not os.path.isfile(ml_path):
        raise FileNotFoundError(
            f"\nUnable to find file {ml_path}\nPlease check the '{field_name}' attribute in your configuration file"
        )
        

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
#    if cfg is not None:
    required = []
    if hardware_type == "MCU" and not operation_mode == "evaluation" and not operation_mode == "prediction":
        required += ["path_to_cubeIDE",]
    
    if cfg.stedgeai:
        legal = ["stedgeai", "path_to_cubeIDE"]
        check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="tools")

        # stedgeai usage
        legal = ["optimization", "on_cloud", "path_to_stedgeai"]
        check_config_attributes(cfg.stedgeai, 
                                specs={"legal": legal, "all": []}, section="tools.stedgeai")
        if not cfg.stedgeai.on_cloud:
            if not os.path.isfile(cfg.stedgeai.path_to_stedgeai):
                print(cfg.stedgeai.path_to_stedgeai)
                raise ValueError("Path for `stedgeai.exe` does not exist.\n"
                                "Please check the cfg.tools.stedgeai section!")
        
        # Patch to support stedgeai with legacy naming stm32ai : reconstruct stm32ai dictionnary
        # from stedgeai one
        cfg["stm32ai"] = cfg.stedgeai
        cfg.stm32ai["optimization"] = cfg.stedgeai.optimization if cfg.stedgeai.optimization else "balanced"
        cfg.stm32ai["on_cloud"] = cfg.stedgeai.on_cloud # if cfg.stedgeai.on_cloud else True
        cfg.stm32ai["path_to_stm32ai"] = cfg.stedgeai.path_to_stedgeai if cfg.stedgeai.path_to_stedgeai else None
        cfg.stm32ai["version"] = Path(cfg.stedgeai.path_to_stedgeai).parts[-4]
        cfg.stedgeai["version"] = Path(cfg.stedgeai.path_to_stedgeai).parts[-4]
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
    required = [x for x in legal if x not in ["export_dir", "granularity", "optimize", "target_opset", "operating_mode",
                                              "onnx_quant_parameters", "op_types_to_quantize", "onnx_extra_options",
                                              "iterative_quant_parameters"]]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="quantization")

    # Set default values of missing optional arguments
    if not cfg.export_dir:
        cfg.export_dir = "quantized_models"
    if not cfg.granularity:
        cfg.granularity = "per_channel"
    cfg.optimize = cfg.optimize if cfg.optimize is not None else False
    cfg.target_opset = cfg.target_opset if cfg.target_opset is not None else 17
    cfg.operating_mode = cfg.operating_mode if cfg.operating_mode else 'default'

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
                         "Supported target_opset parameters: 'int' up to latest onnx_opset\n"
                         "Please check the 'quantization.target_opset' attribute in your configuration file.")
    # Check the quantizer type
    if cfg.quantization_type.lower() not in ["ptq"]:
        raise ValueError(f"\nUnknown or unsupported quantization type. Received `{cfg.quantization_type}`\n"
                         "Supported type: PTQ\n"
                         "Please check the 'quantization.quantization_type' attribute in your configuration file.")


def parse_evaluation_section(cfg: DictConfig, 
                             legal: List) -> None:
    '''
    parses the dictionary containing entire configuration file
    args:
        cfg (DictConfig): 'evaluation' section of the configuration file
        legal (List): UC specific usable attributes
    '''
    required = []
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="evaluation")

    # Set default values of missing optional arguments
    if not cfg.gen_npy_input:
        cfg.gen_npy_input = False
    if not cfg.gen_npy_output:
        cfg.gen_npy_output = False
    if not cfg.profile:
        cfg.profile = "profile_O3"
    if not cfg.input_type:
        cfg.input_type = "uint8"
    if not cfg.output_type:
        cfg.output_type = "int8"
    if not cfg.input_chpos:
        cfg.input_chpos = "chlast"
    if not cfg.output_chpos:
        cfg.output_chpos = "chlast"
    if not cfg.target:
        cfg.target = "host"


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
                         f"Supported modes: {mode_choices}{message}")
    if cfg.operation_mode is None:
        raise ValueError("\nExpecting a value for `operation_mode` attribute\n"
                         f"Supported modes: {mode_choices}{message}")
    # [KH]: to be added when all use cases have model section]
    # # Check that the model section is present and has a value
    # if "model" not in cfg:
    #     raise ValueError("\nMissing `model` section at the top level of your configuration file.\n"
    #                      f"Please check your configuration file.{message}")
    # if cfg.model is None:
    #     raise ValueError("\nExpecting a value for `model` section at the top level of your configuration file.\n"
    #                      f"Please check your configuration file.{message}")

    # Check that the value of operation_mode is valid 
    mode = cfg.operation_mode
    if mode not in mode_choices:
        raise ValueError(f"\nUnknown value for `operation_mode` attribute. Received {mode}\n"
                         f"Supported modes: {mode_choices}{message}")

    # Attributes usable at the top level
    required = ["mlflow"]    # [KH]: should include model later] #, "model"]
#    if mode not in mode_groups.training:
#        # We need the 'general' section to provide model_path.
#        required += ["general",]
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
#    if mode == "prediction":
#        required += ["prediction",]
    if mode in mode_groups.benchmarking:
        required += ["benchmarking", "tools"]
    if mode in mode_groups.deployment:
        required += ["deployment", "tools"]
    if mode in mode_groups.compression:
        required += ["compression", "training"]     # Needed as fine tuning is part of the compression feature

    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="top_level")


def parse_general_section(cfg: DictConfig, 
                          mode: str = None, 
                          mode_groups: str = None,
                          legal: List = None,
                          required: List = None,
                          output_dir: str = '') -> None:
    '''
    parses the general section of configuration file.
    args:
        cfg (DictConfig): configuration dictionary
        mode (str): operation mode
        mode_groups (str): operation mode group
        legal (List): UC specific usable attributes
        required (List): UC specific required attributes
        output_dir (str): output directory for the current run
    '''
#    # Usage of the model_path attribute in training modes
#    # is checked when parsing the 'training' section.
#    required.append("model_path") if not mode_groups.training else []
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
        


def parse_random_periodic_resizing(cfg, output_stride):

    message = "Please check the 'random_periodic_resizing' section of your configuration file."
    if "period" not in cfg:  
        raise ValueError(f"\nMissing `period` argument\n{message}")
    if "image_sizes" not in cfg:  
        raise ValueError(f"\nMissing `image_sizes` argument\n{message}")
                         
    # Image sizes can be given using tuples, arrays or a mix
    # of tuples and arrays. We convert all sizes to tuples.
    sizes_str = '['
    for size in cfg.image_sizes:
        if isinstance(size, (list, tuple)):
            sizes_str += '('
            for x in size:
                sizes_str += str(x) + ','
            sizes_str = sizes_str[:-1] + '),'
        else:
            sizes_str += str(size) + ','
    sizes_str = sizes_str[:-1] + ']'

    sizes_message = "\nInvalid syntax for `image_sizes` argument\n"   
    try:
        x = eval(sizes_str)
        random_sizes = np.array(x, dtype=np.int32)
    except:
        raise ValueError(sizes_message + message)
    
    if np.shape(random_sizes)[1] != 2:
        raise ValueError(sizes_message + message)

    # Check that the image sizes are compatible with the network stride.
    for size in random_sizes:
        if np.shape(output_stride)==():
            output_strides = [output_stride]
        else:
            output_strides = output_stride
        for os in output_strides:
            if (size[0] % os != 0) or (size[1] % os != 0):
                raise ValueError(
                    f"Image sizes must be multiples of the network stride.\n"
                    f"Network stride: {os}\n"
                    f"Invalid image size: {size}\n"
                    f"{message}")

    return random_sizes.tolist()
    

def parse_compression_section(cfg: DictConfig, 
                               legal: List) -> None:
    '''
    parses the dictionary containing entire configuration file
    args:
        cfg (DictConfig): 'compression' section of the configuration file
        legal (List): UC specific usable attributes
    '''
    required = [x for x in legal if x not in ["factor", "strong_optimization"]]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="compression")

    # Set default values of missing optional arguments
    cfg.factor = cfg.factor if cfg.factor else 0.5
    cfg.strong_optimization = cfg.strong_optimization if cfg.strong_optimization else False

    # Check the compression factor type
    if not isinstance(cfg.factor, float):
        raise ValueError(f"\nUnknown or unsupported factor value. Received `{cfg.factor}`\n"
                         "Supported factor parameters: 'float'\n"
                         "Please check the 'compression.factor' attribute in your configuration file.")

    # Check optimization
    if cfg.strong_optimization not in [True, False]:
        raise ValueError(f"\nUnknown or unsupported strong_optimization value. Received `{cfg.strong_optimization}`\n"
                         "Supported optimize parameters: 'True', or 'False'\n"
                         "Please check the 'compression.strong_optimization' attribute in your configuration file.")


def parse_training_section(cfg: DictConfig, 
                           legal: List = None) -> None:
    '''
    parses the training section of configuration file.
    args:
        cfg (DictConfig): 'training' section of the configuration file
        model_path_used (bool): a flag to tell if the 'model.model_path' parameter is provided
        model_type_used (bool): a flag to tell if the 'model.model_type' parameter is provided
        legal (List): usable attributes
    '''
    required = ["batch_size", "epochs", "optimizer"]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="training")

    # The optimizer may be written on one line. For example: "optimizer: Adam"
    # In this case, we got a string instead of a dictionary.
    if type(cfg.optimizer) == str:
        cfg.optimizer = DefaultMunch.fromDict({cfg.optimizer: None})

def parse_model_section(cfg: DictConfig, mode: str, mode_groups, legal: list, required: list = None) -> None:
    """
    Checks and parses the root-level 'model' section of the config file.

    Args:
        cfg (DictConfig): The model configuration parameters.
        mode (str): The current operation mode.
        mode_groups: The mode groups object.
        legal (list): List of legal model attributes for this use case.
        required (list, optional): List of required model attributes. If None, no required fields are enforced.

    Returns:
        None
    """
    req = [] if required is None else list(required)
    if cfg.model_name:
        req.append("input_shape")
    # Mutually exclusive model sources
    model_sources = ["model_name", "model_path"]
    set_sources = [name for name in model_sources if getattr(cfg, name, None)]
    if len(set_sources) == 0:
        raise ValueError(
            "\nExpecting one of the following model source attributes to be set: "
            f"{', '.join(model_sources)}\nPlease check your configuration file." )


    check_config_attributes(cfg, specs={"legal": legal, "all": req}, section="model")

    if cfg.model_path and cfg.model_path[:4].lower() == "http":
        print('[INFO] : A URL found for model.model_path variable!')
        url = cfg.model_path
        output_dir = HydraConfig.get().runtime.output_dir
        model_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(cfg.model_path))[0])
        os.makedirs(model_dir, exist_ok=True)
        local_path = os.path.join(model_dir, url.split('/')[-1])
        download_file(url, local_path)
        cfg.model_path = local_path

    # Check model_path
    if cfg.model_path:
        file_extension = Path(cfg.model_path).suffix.lower()
        if file_extension in [".h5", ".keras", ".tflite"]:
            cfg.framework = "tf"
            check_model_file_extension(cfg.model_path, mode, mode_groups, "model_path")
        elif file_extension in [".pt", ".pth"]:
            cfg.framework = "torch"
        elif file_extension in [".onnx"] and not cfg.framework:
            cfg.framework = "tf"
            check_model_file_extension(cfg.model_path, mode, mode_groups, "model_path")
    else:
        # Get end of model name to set the framework to be used"
        if cfg.model_name[-3:]=='_pt':
            cfg.framework = "torch"
        else:
            cfg.framework = "tf"
                
    if cfg.framework == "tf":
        if len(set_sources) > 1:
            raise ValueError(
                "\nThe following model source attributes are mutually exclusive and more than one is set: "
                f"{', '.join(set_sources)}\nPlease check your configuration file.")

        
def parse_prediction_section(cfg: DictConfig) -> None:
    '''
    parses the prediction section of configuration file.
    args:
        cfg (DictConfig): 'prediction' section of the configuration file
    '''
    legal = ["seed","target", "reid_distance_metric",
             "profile", "input_type", "output_type", "input_chpos", "output_chpos"]
    required = []
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="prediction")

    # Set default values of missing optional arguments
    if not cfg.profile:
        cfg.profile = "profile_O3"
    if not cfg.input_type:
        cfg.input_type = "uint8"
    if not cfg.output_type:
        cfg.output_type = "int8"
    if not cfg.input_chpos:
        cfg.input_chpos = "chlast"
    if not cfg.output_chpos:
        cfg.output_chpos = "chlast"
    if not cfg.target:
        cfg.target = "host"

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
    required = [x for x in legal]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="deployment")
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


def get_class_names_from_file(cfg: DictConfig) -> List[str]:
    if cfg.classes_file_path :
        with open(cfg.classes_file_path, 'r') as file:
            class_names = [line.strip() for line in file]
    return class_names

from omegaconf import DictConfig, OmegaConf

def flatten_config(cfg, preserve_keys=("class_map",)):
    # Ensure cfg is a plain dict first
    if isinstance(cfg, DictConfig):
        cfg = OmegaConf.to_container(cfg, resolve=False)
    elif "DefaultMunch" in str(type(cfg)):
        cfg = cfg.toDict()
    else:
        cfg = dict(cfg)

    preserve_keys = set(preserve_keys)
    flat_config = {}

    def _flatten(d):
        for k, v in d.items():
            if isinstance(v, dict):
                if k in preserve_keys:
                    flat_config[k] = v
                else:
                    _flatten(v)
            else:
                flat_config[k] = v 

    _flatten(cfg)
    return flat_config