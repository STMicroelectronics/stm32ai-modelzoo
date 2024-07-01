# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import os
import sys
import warnings
import shutil

from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from typing import Optional

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from models_utils import get_model_name_and_its_input_shape, get_model_name
from common_deploy import stm32ai_deploy, stm32ai_deploy_mpu
from common_benchmark import cloud_connect
from stm32ai_dc import Stm32Ai, CloudBackend, CliParameters, ModelNotFoundError
from gen_h_file import gen_h_user_file

anchors_str = "\t\t<link>\n\t\t\t<name>Application/STM32H747I-DISCO/Src/CM7/anchors.c</name>\n\t\t\t<type>1</type>\n\t\t\t<locationURI>PARENT-3-PROJECT_LOC/STM32H747I-DISCO/Src/CM7/anchors.c</locationURI>\n\t\t</link>\n"
network_str = "\t\t<link>\n\t\t\t<name>Application/Network/network.c</name>\n\t\t\t<type>1</type>\n\t\t\t<locationURI>PARENT-3-PROJECT_LOC/Network/Src/network.c</locationURI>\n\t\t</link>\n"

def add_anchors_to_project(output_dir, c_project_path):
    # Copy anchors.h
    shutil.copyfile(os.path.join(output_dir, os.path.join("C_header", "anchors.h")), c_project_path + '/Application/STM32H747I-DISCO/Inc/CM7/anchors.h')

def remove_anchors_from_project(c_project_path):
    # Remove anchors.h
    if os.path.exists(c_project_path + '/Application/STM32H747I-DISCO/Inc/CM7/anchors.h'):
        os.remove(c_project_path + '/Application/STM32H747I-DISCO/Inc/CM7/anchors.h')

def deploy(cfg: DictConfig = None, model_path_to_deploy: Optional[str] = None) -> None:
    """
    Deploy the AI model to a target device.

    Args:
        cfg (DictConfig): The configuration dictionary. Defaults to None.
        model_path_to_deploy (str, optional): Model path to deploy. Defaults to None

    Returns:
        None
    """
    # Build and flash Getting Started
    board = cfg.deployment.hardware_setup.board
    stlink_serial_number = cfg.deployment.hardware_setup.stlink_serial_number
    c_project_path = cfg.deployment.c_project_path
    output_dir = HydraConfig.get().runtime.output_dir
    stm32ai_output = output_dir + "/generated"
    stm32ai_version = cfg.tools.stm32ai.version
    optimization = cfg.tools.stm32ai.optimization
    path_to_stm32ai = cfg.tools.stm32ai.path_to_stm32ai
    path_to_cube_ide = cfg.tools.path_to_cubeIDE
    verbosity = cfg.deployment.verbosity
    stm32ai_ide = cfg.deployment.IDE
    stm32ai_serie = cfg.deployment.hardware_setup.serie

    # Get model name for STM32Cube.AI STATS
    if model_path_to_deploy:
        model_path = model_path_to_deploy
    else:
        model_path = cfg.general.model_path
    model_name, input_shape = get_model_name_and_its_input_shape(model_path=model_path)
    # Get model name
    get_model_name_output = get_model_name(model_type=str(model_name),
                                           input_shape=str(input_shape[0]),
                                           project_name=cfg.general.project_name)

    # Generate ai_model_config.h for C embedded application
    print("[INFO] : Generating C header file for Getting Started...")
    tpp, quantized_model_path = gen_h_user_file(config=cfg, quantized_model_path=model_path)

    if tpp:
        model_path = quantized_model_path

    # Anchors gestion
    if os.path.isfile(os.path.join(output_dir, os.path.join("C_header", "anchors.h"))):
        add_anchors_to_project(output_dir, c_project_path)
    else:
        remove_anchors_from_project(c_project_path)

    # gen_h_user_file(config=cfg, quantized_model_path=model_path, board=board)
    if stm32ai_serie.upper() == "STM32H7" and stm32ai_ide.lower() == "gcc":
        if board == "STM32H747I-DISCO":
            stmaic_conf_filename = "stmaic_STM32H747I-DISCO.conf"
        else:
            raise TypeError("The hardware selected in cfg.deployment.stm32ai.target is not supported yet!")

        # Run the deployment
        stm32ai_deploy(target=board, stlink_serial_number=stlink_serial_number, stm32ai_version=stm32ai_version, c_project_path=c_project_path,
                       output_dir=output_dir,
                       stm32ai_output=stm32ai_output, optimization=optimization, path_to_stm32ai=path_to_stm32ai,
                       path_to_cube_ide=path_to_cube_ide, stmaic_conf_filename=stmaic_conf_filename,
                       verbosity=verbosity,
                       debug=False, model_path=model_path, get_model_name_output=get_model_name_output,
                       stm32ai_ide=stm32ai_ide, stm32ai_serie=stm32ai_serie, on_cloud=cfg.tools.stm32ai.on_cloud,
                       check_large_model=True, cfg=cfg)

    else:
        raise TypeError("Options for cfg.deployment.hardware_setup.serie and cfg.deployment.IDE not supported yet!")


def deploy_mpu(cfg: DictConfig = None, model_path_to_deploy: Optional[str] = None,
            credentials: list[str] = None) -> None:
    """
    Deploy the AI model to a MPU target device.

    Args:
        cfg (DictConfig): The configuration dictionary. Defaults to None.
        model_path_to_deploy (str, optional): Model path to deploy. Defaults to None
        credentials list[str]: User credentials used before to connect.

    Returns:
        None
    """
    # Build and flash Getting Started
    board = cfg.deployment.hardware_setup.board
    c_project_path = cfg.deployment.c_project_path
    label_file_path = cfg.deployment.label_file_path
    board_deploy_path = cfg.deployment.board_deploy_path
    verbosity = cfg.deployment.verbosity
    board_serie = cfg.deployment.hardware_setup.serie
    board_ip = cfg.deployment.hardware_setup.ip_address
    optimized_model_path = c_project_path + "Optimized_models/"

    # Get model name for STM32Cube.AI STATS
    model_path = model_path_to_deploy if model_path_to_deploy else cfg.general.model_path
    model_extension = os.path.splitext(model_path)[1]
    model_name, input_shape = get_model_name_and_its_input_shape(model_path=model_path)

    if board_serie == "STM32MP2" and (model_extension == ".tflite" or model_extension == ".onnx") and cfg.tools.stm32ai.on_cloud:
        # Connect to STM32Cube.AI Developer Cloud
        login_success, ai, _ = cloud_connect(stm32ai_version=None, credentials=credentials)
        if login_success:
            try:
                ai.upload_model(model_path)
                model = model_name + model_extension
                res = ai.generate_nbg(model)
                ai.download_model(res, optimized_model_path + res)
                model_path=os.path.join(optimized_model_path,res)
                model_name = model_name + ".nb"
                rename_model_path=os.path.join(optimized_model_path,model_name)
                os.rename(model_path, rename_model_path)
                model_path = rename_model_path
                print("[INFO] : Optimized Model Name:", model_name)
                print("[INFO] : Optimization done ! Model available at :",optimized_model_path)

            except Exception as e:
                print(f"[FAIL] : Model optimization via Cloud failed : {e}.")
                print("[INFO] : Use default model instead of optimized ...")

    if board in ["STM32MP257F-EV1","STM32MP157F-DK2","STM32MP135F-DK"]:
        # Run the deployment
        res = stm32ai_deploy_mpu(target=board, board_ip_address=board_ip, label_file=label_file_path, board_deploy=board_deploy_path, c_project_path=c_project_path,
                                    verbosity=verbosity, debug=False, model_path=model_path,cfg=cfg)
        if res == False:
            raise TypeError("Deployment on the target failed\n")
    else:
        raise TypeError("Options for cfg.deployment.hardware_setup.board and not supported !\n"
                        "Only valid options are STM32MP257F-EV1,STM32MP157F-DK2,STM32MP135F-DK \n")