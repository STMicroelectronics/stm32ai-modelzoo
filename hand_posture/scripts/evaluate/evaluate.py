# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import logging
import os
import sys
import warnings

import hydra
import mlflow
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, OmegaConf

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

logger = tf.get_logger()
logger.setLevel(logging.ERROR)

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../utils/models'))
sys.path.append(os.path.abspath('../../../common'))


from common_benchmark import stm32ai_benchmark
from datasets import get_ds
from header_file_generator import gen_h_user_file
from utils import get_config, mlflow_ini, setup_seed
from visualize import training_confusion_matrix


def evaluate_model(cfg, c_header=False, c_code=False):
    """
    Quantize, evaluate and benchmark model.
    Generate Config header file.
    """

    if cfg.model.model_path.split(".")[-1] != 'h5':
        raise TypeError("Supporting only h5 model.")

    # Load the model
    model = tf.keras.models.load_model(cfg.model.model_path)

    # Estimate the model footprints, quantize and convert the float model using STM32Cube.AI

    # Adding batch_size to load dataset
    second_conf = OmegaConf.create({"train_parameters": {"batch_size": 32}})
    OmegaConf.set_struct(cfg, False)
    cfg = OmegaConf.merge(cfg, second_conf)
    OmegaConf.set_struct(cfg, True)

    # Benchmark/Generating C model
    stm32ai_benchmark(cfg, cfg.model.model_path, c_code)

    # Evaluate the float model
                # Check train set is provided

    if cfg.dataset.test_path is not None:
        test_ds = get_ds(cfg, ds_path=cfg.dataset.test_path, shuffle=True, split=1)

        # Generate the confusion matrix for the float model
        training_confusion_matrix(test_ds, model, cfg.dataset.class_names)
    else:
        print("[INFO] : Test Dataset path was not specified, the model accuracy will not be evaluate.")
    if c_header:
        # Generate Config.h for C embedded application
        gen_h_user_file(cfg, cfg.model.model_path)


@hydra.main(version_base=None, config_path="", config_name="user_config")
def main(cfg: DictConfig) -> None:
    # Initilize configuration & mlflow
    configs = get_config(cfg)
    mlflow_ini(configs)

    # Set all seeds
    setup_seed(42)

    # Evaluate model performance / footprints
    # evaluate_model(cfg, c_header=True, c_code=True)
    evaluate_model(cfg)

    # Record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()


if __name__ == "__main__":
    main()
