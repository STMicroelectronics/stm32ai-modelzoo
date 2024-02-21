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
from omegaconf import DictConfig
import re
import tensorflow as tf
from typing import Tuple, List, Optional
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
import mlflow

sys.path.append(os.path.abspath('../../common'))
sys.path.append(os.path.abspath('../utils'))
from common_benchmark import stm32ai_benchmark, get_model_name
from models_mgt import get_model_name_and_its_input_shape
from utils import log_to_file


def benchmark(cfg: DictConfig = None, model_path_to_benchmark: Optional[str] = None,
              credentials: list[str] = None) -> None:
    """
    Benchmark a model .

    Args:
        cfg (DictConfig): Configuration dictionary.
        model_path_to_benchmark (str, optional): model path to benchmark.
        credentials list[str]: User credentials used before to connect.

    Returns:
        None
    """

    model_path = model_path_to_benchmark if model_path_to_benchmark else cfg.general.model_path
    model_name, input_shape = get_model_name_and_its_input_shape(model_path=model_path)
    output_dir = HydraConfig.get().runtime.output_dir
    stm32ai_output = output_dir + "/stm32ai_files"
    stm32ai_version = cfg.tools.stm32ai.version
    optimization = cfg.tools.stm32ai.optimization
    board = cfg.benchmarking.board
    path_to_stm32ai = cfg.tools.stm32ai.path_to_stm32ai
    #log the parameters in stm32ai_main.log 
    log_to_file(cfg.output_dir, f'Stm32ai version : {stm32ai_version}')
    log_to_file(cfg.output_dir, f'Benchmarking board : {board}')
    get_model_name_output = get_model_name(model_type=str(model_name),
                                           input_shape=str(input_shape[0]),
                                           project_name=cfg.general.project_name)
    stm32ai_benchmark(footprints_on_target=board,
                      optimization=optimization,
                      stm32ai_version=stm32ai_version, model_path=model_path,
                      stm32ai_output=stm32ai_output, path_to_stm32ai=path_to_stm32ai,
                      get_model_name_output=get_model_name_output,on_cloud =cfg.tools.stm32ai.on_cloud,
                      credentials=credentials)
