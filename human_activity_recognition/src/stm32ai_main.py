# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import subprocess
import sys
import traceback
from omegaconf import OmegaConf
from hydra.core.hydra_config import HydraConfig
import hydra
from hydra import initialize_config_dir
import tensorflow as tf
from omegaconf import DictConfig
import mlflow
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common'))
sys.path.append(os.path.join(os.path.dirname(__file__), './preprocessing'))
sys.path.append(os.path.join(os.path.dirname(__file__), './training'))
sys.path.append(os.path.join(os.path.dirname(__file__), './utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), './evaluation'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../deployment'))
sys.path.append(os.path.join(os.path.dirname(__file__), './benchmarking'))

from preprocess import preprocess
from utils import set_gpu_memory_limit, get_random_seed, mlflow_ini
from visualizer import display_figures
from parse_config import get_config
from train import train
from evaluate import evaluate
from deploy import deploy
from benchmark import benchmark
from typing import Optional
from common_benchmark import cloud_connect


def chain_tb(cfg: DictConfig = None, train_ds: tf.data.Dataset = None,
             valid_ds: tf.data.Dataset = None, test_ds: tf.data.Dataset = None) -> None:
    """
    Runs the chain_tb pipeline, perform training and then benchmarking.

    Args:
        cfg (DictConfig): Configuration dictionary. Defaults to None.
        train_ds (tf.data.Dataset): Training dataset. Defaults to None.
        valid_ds (tf.data.Dataset): Validation dataset. Defaults to None.
        test_ds (tf.data.Dataset): Test dataset. Defaults to None.

    Returns:
        None
    """

    # Connect to STM32Cube.AI Developer Cloud
    credentials = None
    if cfg.tools.stm32ai.on_cloud:
        _, _, credentials = cloud_connect(stm32ai_version=cfg.tools.stm32ai.version)

    if test_ds:
        trained_model_path = train(cfg=cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds)
    else:
        trained_model_path = train(cfg=cfg, train_ds=train_ds, valid_ds=valid_ds)
    print('[INFO] : Training complete.')
    benchmark(cfg=cfg, model_path_to_benchmark=trained_model_path, credentials=credentials)
    print('[INFO] : benchmarking complete.')
    display_figures(cfg)
    

def process_mode(mode: str = None,
                 configs: DictConfig = None,
                 train_ds: tf.data.Dataset = None,
                 valid_ds: tf.data.Dataset = None,
                 test_ds: tf.data.Dataset = None,
                 float_model_path: Optional[str] = None) -> None:
    """
    Process the selected mode of operation.

    Args:
        mode (str): The selected mode of operation. Must be one of 'benchmarking', 'deployment',
                    'evaluation', 'training', or 'chain_tb'.
        configs (DictConfig): The configuration object.
        train_ds (tf.data.Dataset): The training dataset. Required if mode is 'train'.
        valid_ds (tf.data.Dataset): The validation dataset. 
                                    Required if mode is 'train' or 'evaluate'.
        test_ds (tf.data.Dataset): The test dataset.
                                   Required if mode is 'evaluate'.
        float_model_path(str, optional): Model path . Defaults to None
    Returns:
        None
    Raises:
        ValueError: If an invalid operation_mode is selected or if required datasets are missing.
    """

    # Check the selected mode and perform the corresponding operation
    if mode == 'benchmarking':
        benchmark(cfg=configs)
        print('[INFO] : Benchmark complete.')
    elif mode == 'deployment':
        deploy(cfg=configs)
        print('[INFO] : Deployment complete.')
    elif mode == 'evaluation':
        if test_ds:
            evaluate(cfg=configs, eval_ds=test_ds)
        else:
            evaluate(cfg=configs, eval_ds=valid_ds, name_ds="validation_set")
        display_figures(configs)
        print('[INFO] : Evaluation complete.')
    elif mode == 'training':
        if test_ds:
            train(cfg=configs, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds)
        else:
            train(cfg=configs, train_ds=train_ds, valid_ds=valid_ds)
        display_figures(configs)
        print('[INFO] : Training complete.')
    elif mode == 'chain_tb':
        chain_tb(cfg=configs,
                 train_ds=train_ds,
                 valid_ds=valid_ds,
                 test_ds=test_ds)
        print('[INFO] : chain_tb complete.')
    # Raise an error if an invalid mode is selected
    else:
        raise ValueError(f"Invalid mode: {mode}")

    if mode in ['benchmarking', 'chain_tb']:
        mlflow.log_param("model_path", configs.general.model_path)
        mlflow.log_param("stm32ai_version", configs.tools.stm32ai.version)
        mlflow.log_param("target", configs.benchmarking.board)


@hydra.main(version_base=None, config_path="", config_name="user_config")
def main(cfg: DictConfig) -> None:
    """
    Main entry point of the script.

    Args:
        cfg: Configuration dictionary.

    Returns:
        None
    """

    # Parse the configuration file
    cfg = get_config(cfg)
    cfg.output_dir = HydraConfig.get().run.dir
    mlflow_ini(cfg)
    
    # Seed global seed for random generators
    seed = get_random_seed(cfg)
    if seed is not None:
        tf.keras.utils.set_random_seed(seed)
    
    # Configure the GPU
    if cfg.general and cfg.general.gpu_memory_limit:
        set_gpu_memory_limit(cfg.general.gpu_memory_limit)
    # Extract the mode from the command-line arguments
    mode = cfg.operation_mode
    valid_modes = ['training', 'evaluation', 'chain_tb']
    if mode in valid_modes:
        # Perform further processing based on the selected mode
        preprocess_output = preprocess(cfg=cfg)
        train_ds, valid_ds, test_ds = preprocess_output
        # Process the selected mode
        process_mode(mode=mode,
                     configs=cfg,
                     train_ds=train_ds,
                     valid_ds=valid_ds,
                     test_ds=test_ds)
    else:
        # Process the selected mode
        process_mode(mode=mode, configs=cfg)

    # mlflow.end_run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=str, default='', help='Path to folder containing configuration file')
    parser.add_argument('--config-name', type=str, default='user_config', help='name of the configuration file')
    # add arguments to the parser
    parser.add_argument('params', nargs='*',
                        help='List of parameters to over-ride in config.yaml')
    args = parser.parse_args()

    # Call the main function
    main()

    # log the config_path and config_name parameters
    mlflow.log_param('config_path', args.config_path)
    mlflow.log_param('config_name', args.config_name)
    mlflow.end_run()
