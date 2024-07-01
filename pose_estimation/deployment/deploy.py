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

def deploy(cfg: DictConfig = None, model_path_to_deploy: Optional[str] = None) -> None:
    """
    Deploy the AI model to a target device.

    Args:
        cfg (DictConfig): The configuration dictionary. Defaults to None.
        model_path_to_deploy (str, optional): Model path to deploy. Defaults to None

    Returns:
        None
    """

    #TO BE DONE

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