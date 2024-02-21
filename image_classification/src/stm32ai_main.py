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
import warnings

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import tensorflow as tf
from omegaconf import DictConfig
import mlflow
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common'))
sys.path.append(os.path.join(os.path.dirname(__file__), './data_augmentation'))
sys.path.append(os.path.join(os.path.dirname(__file__), './preprocessing'))
sys.path.append(os.path.join(os.path.dirname(__file__), './training'))
sys.path.append(os.path.join(os.path.dirname(__file__), './utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), './evaluation'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../deployment'))
sys.path.append(os.path.join(os.path.dirname(__file__), './quantization'))
sys.path.append(os.path.join(os.path.dirname(__file__), './prediction'))
sys.path.append(os.path.join(os.path.dirname(__file__), './benchmarking'))

from preprocess import preprocess
from utils import set_gpu_memory_limit, mlflow_ini
from visualizer import display_figures
from parse_config import get_config
from train import train
from evaluate import evaluate
from deploy import deploy
from quantize import quantize
from predict import predict
from benchmark import benchmark
from typing import Optional
from common_benchmark import cloud_connect


def chain_qd(cfg: DictConfig = None, float_model_path: str = None, train_ds: tf.data.Dataset = None,
             quantization_ds: tf.data.Dataset = None) -> None:
    """
    Runs the chain_qd pipeline, including quantization,  and deployment

    Args:
        cfg (DictConfig): Configuration dictionary. Defaults to None.
        float_model_path (str): float model path to evaluate and quantize. Defaults to None.
        train_ds (tf.data.Dataset): Training dataset. Defaults to None.
        quantization_ds:(tf.data.Dataset): quantization dataset. Defaults to None

    Returns:
        None
    """

    # Connect to STM32Cube.AI Developer Cloud
    credentials = None
    if cfg.tools.stm32ai.on_cloud:
        _, _, credentials = cloud_connect(stm32ai_version=cfg.tools.stm32ai.version)

    if quantization_ds:
        print('[INFO] : Using the quantization dataset to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=quantization_ds,
                                        float_model_path=float_model_path)
    elif train_ds:
        print('[INFO] : Quantization dataset is not provided! Using the training set to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=train_ds,
                                        float_model_path=float_model_path)
    else:
        print('[INFO] : Neither quantization dataset nor training set are provided! Using fake data to quantize the model. '
              'The model performances will not be accurate.')
        quantized_model_path = quantize(cfg=cfg, fake=True)
    print('[INFO] : Quantization complete.')

    deploy(cfg=cfg, model_path_to_deploy=quantized_model_path, credentials=credentials)
    print('[INFO] : Deployment complete.')


def chain_eqeb(cfg: DictConfig = None, float_model_path: str = None, train_ds: tf.data.Dataset = None,
               valid_ds: tf.data.Dataset = None,
               quantization_ds: tf.data.Dataset = None, test_ds: tf.data.Dataset = None) -> None:
    """
    Runs the chain_eqeb pipeline, including evaluation of the float model,  quantization , evaluation of
    the quantized model and benchmarking

    Args:
        cfg (DictConfig): Configuration dictionary. Defaults to None.
        float_model_path (str): float model path to evaluate and quantize. Defaults to None.
        train_ds (tf.data.Dataset): Training dataset. Defaults to None.
        valid_ds (tf.data.Dataset): Validation dataset. Defaults to None.
        test_ds (tf.data.Dataset): Test dataset. Defaults to None.
        quantization_ds:(tf.data.Dataset): quantization dataset. Defaults to None

    Returns:
        None
    """

    # Connect to STM32Cube.AI Developer Cloud
    credentials = None
    if cfg.tools.stm32ai.on_cloud:
        _, _, credentials = cloud_connect(stm32ai_version=cfg.tools.stm32ai.version)

    if test_ds:
        evaluate(cfg=cfg, eval_ds=test_ds, model_path_to_evaluate=float_model_path, name_ds="test set")
    else:
        evaluate(cfg=cfg, eval_ds=valid_ds, model_path_to_evaluate=float_model_path, name_ds="validation set")
    print('[INFO] : Evaluation complete.')
    display_figures(cfg)
    if quantization_ds:
        print('[INFO] : Using the quantization dataset to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=quantization_ds,
                                        float_model_path=float_model_path)
    else:
        print('[INFO] : Quantization dataset is not provided! Using the training set to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=train_ds,
                                        float_model_path=float_model_path)
    print('[INFO] : Quantization complete.')
    if test_ds:
        evaluate(cfg=cfg, eval_ds=test_ds, model_path_to_evaluate=quantized_model_path, name_ds="test set")
    else:
        evaluate(cfg=cfg, eval_ds=valid_ds, model_path_to_evaluate=quantized_model_path, name_ds="validation set")
    print('[INFO] : Evaluation complete.')
    display_figures(cfg)
    benchmark(cfg=cfg, model_path_to_benchmark=quantized_model_path, credentials=credentials)
    print('[INFO] : Benchmarking complete.')


def chain_qb(cfg: DictConfig = None, float_model_path: str = None, train_ds: tf.data.Dataset = None,
             quantization_ds: tf.data.Dataset = None) -> None:
    """
    Runs the chain_qb pipeline, including quantization and benchmarking.

    Args:
        cfg (DictConfig): Configuration dictionary. Defaults to None.
        float_model_path (str): float_model_path to quantize. Defaults to None.
        train_ds (tf.data.Dataset): Training dataset. Defaults to None.
        quantization_ds:(tf.data.Dataset): quantization dataset. Defaults to None

    Returns:
        None
    """

    # Connect to STM32Cube.AI Developer Cloud
    credentials = None
    if cfg.tools.stm32ai.on_cloud:
        _, _, credentials = cloud_connect(stm32ai_version=cfg.tools.stm32ai.version)

    if quantization_ds:
        print('[INFO] : Using the quantization dataset to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=quantization_ds,
                                        float_model_path=float_model_path)
    elif train_ds:
        print('[INFO] : Quantization dataset is not provided! Using the training set to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=train_ds,
                                        float_model_path=float_model_path)
    else:
        print('[INFO] : Neither quantization dataset nor training set are provided! Using fake data to quantize the model. '
              'The model performances will not be accurate.')
        quantized_model_path = quantize(cfg=cfg, fake=True)
    print('[INFO] : Quantization complete.')

    benchmark(cfg=cfg, model_path_to_benchmark=quantized_model_path, credentials=credentials)
    print('[INFO] : Benchmarking complete.')


def chain_eqe(cfg: DictConfig = None, float_model_path: str = None, train_ds: tf.data.Dataset = None,
              valid_ds: tf.data.Dataset = None,
              quantization_ds: tf.data.Dataset = None, test_ds: tf.data.Dataset = None) -> None:
    """
    Runs the chain_eqe pipeline, including evaluation of a float model,  quantization and evaluation of
    the quantized model

    Args:
        cfg (DictConfig): Configuration dictionary. Defaults to None.
        float_model_path (str): float model path to evaluate and quantize. Defaults to None.
        train_ds (tf.data.Dataset): Training dataset. Defaults to None.
        valid_ds (tf.data.Dataset): Validation dataset. Defaults to None.
        test_ds (tf.data.Dataset): Test dataset. Defaults to None.
        quantization_ds:(tf.data.Dataset): quantization dataset. Defaults to None

    Returns:
        None
    """
    if test_ds:
        evaluate(cfg=cfg, eval_ds=test_ds, model_path_to_evaluate=float_model_path, name_ds="test set")
    else:
        evaluate(cfg=cfg, eval_ds=valid_ds, model_path_to_evaluate=float_model_path, name_ds="validation set")
    print('[INFO] : Evaluation complete.')
    display_figures(cfg)
    if quantization_ds:
        print('[INFO] : Using the quantization dataset to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=quantization_ds,
                                        float_model_path=float_model_path)
    else:
        print('[INFO] : Quantization dataset is not provided! Using the training set to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=train_ds,
                                        float_model_path=float_model_path)
    print('[INFO] : Quantization complete.')
    if test_ds:
        evaluate(cfg=cfg, eval_ds=test_ds, model_path_to_evaluate=quantized_model_path, name_ds="test set")
    else:
        evaluate(cfg=cfg, eval_ds=valid_ds, model_path_to_evaluate=quantized_model_path, name_ds="validation set")
    print('[INFO] : Evaluation complete.')
    display_figures(cfg)


def chain_tbqeb(cfg: DictConfig = None, train_ds: tf.data.Dataset = None, valid_ds: tf.data.Dataset = None,
                quantization_ds: tf.data.Dataset = None, test_ds: tf.data.Dataset = None) -> None:
    """
    Runs the chain_tbqeb pipeline, including training,  benchmarking , quantization, evaluation and benchmarking.

    Args:
        cfg (DictConfig): Configuration dictionary. Defaults to None.
        train_ds (tf.data.Dataset): Training dataset. Defaults to None.
        valid_ds (tf.data.Dataset): Validation dataset. Defaults to None.
        test_ds (tf.data.Dataset): Test dataset. Defaults to None.
        quantization_ds:(tf.data.Dataset): quantization dataset. Defaults to None

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
    if quantization_ds:
        print('[INFO] : Using the quantization dataset to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=quantization_ds,
                                        float_model_path=trained_model_path)
    else:
        print('[INFO] : Quantization dataset is not provided! Using the training set to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=train_ds,
                                        float_model_path=trained_model_path)
    print('[INFO] : Quantization complete.')
    if test_ds:
        evaluate(cfg=cfg, eval_ds=test_ds, model_path_to_evaluate=quantized_model_path, name_ds="test set")
    else:
        evaluate(cfg=cfg, eval_ds=valid_ds, model_path_to_evaluate=quantized_model_path, name_ds="validation set")
    print('[INFO] : Evaluation complete.')
    display_figures(cfg)
    benchmark(cfg=cfg, model_path_to_benchmark=quantized_model_path, credentials=credentials)
    print('[INFO] : Benchmarking complete.')


def chain_tqe(cfg: DictConfig = None, train_ds: tf.data.Dataset = None, valid_ds: tf.data.Dataset = None,
              quantization_ds: tf.data.Dataset = None, test_ds: tf.data.Dataset = None) -> None:
    """
    Runs the chain_tqe pipeline, including training,  quantization and evaluation.

    Args:
        cfg (DictConfig): Configuration dictionary. Defaults to None.
        train_ds (tf.data.Dataset): Training dataset. Defaults to None.
        valid_ds (tf.data.Dataset): Validation dataset. Defaults to None.
        test_ds (tf.data.Dataset): Test dataset. Defaults to None.
        quantization_ds:(tf.data.Dataset): quantization dataset. Defaults to None

    Returns:
        None
    """
    if test_ds:
        trained_model_path = train(cfg=cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds)
    else:
        trained_model_path = train(cfg=cfg, train_ds=train_ds, valid_ds=valid_ds)
    print('[INFO] : Training complete.')
    if quantization_ds:
        print('[INFO] : Using the quantization dataset to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=quantization_ds,
                                        float_model_path=trained_model_path)
    else:
        print('[INFO] : Quantization dataset is not provided! Using the training set to quantize the model.')
        quantized_model_path = quantize(cfg=cfg, quantization_ds=train_ds,
                                        float_model_path=trained_model_path)
    print('[INFO] : Quantization complete.')
    if test_ds:
        evaluate(cfg=cfg, eval_ds=test_ds, model_path_to_evaluate=quantized_model_path, name_ds="test set")
    else:
        evaluate(cfg=cfg, eval_ds=valid_ds, model_path_to_evaluate=quantized_model_path, name_ds="validation set")
    print('[INFO] : Evaluation complete.')
    display_figures(cfg)


def process_mode(mode: str = None, configs: DictConfig = None, train_ds: tf.data.Dataset = None,
                 valid_ds: tf.data.Dataset = None, quantization_ds: tf.data.Dataset = None,
                 test_ds: tf.data.Dataset = None, float_model_path: Optional[str] = None,fake: Optional[bool] = False) -> None:
    """
    Process the selected mode of operation.

    Args:
        mode (str): The selected mode of operation. Must be one of 'train', 'evaluate', or 'predict'.
        configs (DictConfig): The configuration object.
        train_ds (tf.data.Dataset): The training dataset. Required if mode is 'train'.
        valid_ds (tf.data.Dataset): The validation dataset. Required if mode is 'train' or 'evaluate'.
        test_ds (tf.data.Dataset): The test dataset. Required if mode is 'evaluate' or 'predict'.
        quantization_ds(tf.data.Dataset): The quantization dataset.
        float_model_path(str, optional): Model path . Defaults to None
        fake (bool, optional): Whether to use fake data for representative dataset generation. Defaults to False.
    Returns:
        None
    Raises:
        ValueError: If an invalid mode is selected or if required datasets are missing.
    """

    # Check the selected mode and perform the corresponding operation
    if mode == 'training':
        if test_ds:
            train(cfg=configs, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds)
        else:
            train(cfg=configs, train_ds=train_ds, valid_ds=valid_ds)
        display_figures(configs)
        print('[INFO] : Training complete.')
    elif mode == 'evaluation':
        if test_ds:
            evaluate(cfg=configs, eval_ds=test_ds, name_ds="test set")
        else:
            evaluate(cfg=configs, eval_ds=valid_ds, name_ds="validation set")
        display_figures(configs)
        print('[INFO] : Evaluation complete.')
    elif mode == 'deployment':
        deploy(cfg=configs)
        print('[INFO] : Deployment complete.')
    elif mode == 'quantization':
        if quantization_ds:
            print('[INFO] : Using the quantization dataset to quantize the model.')
            quantize(cfg=configs, quantization_ds=quantization_ds, fake=False)
        elif train_ds:
            print('[INFO] : Quantization dataset is not provided! Using the training set to quantize the model.')
            quantize(cfg=configs, quantization_ds=train_ds, fake=False)
        else:
            print(
                '[INFO] : Neither quantization dataset or training set are provided! Using fake data to quantize the model. '
                'The model performances will not be accurate.')
            quantize(cfg=configs, fake=fake)
        print('[INFO] : Quantization complete.')
    elif mode == 'prediction':
        predict(cfg=configs)
        print('[INFO] : Prediction complete.')
    elif mode == 'benchmarking':
        benchmark(cfg=configs)
        print('[INFO] : Benchmark complete.')
    elif mode == 'chain_tbqeb':
        chain_tbqeb(cfg=configs, train_ds=train_ds, valid_ds=valid_ds, quantization_ds=quantization_ds,
                    test_ds=test_ds)
        print('[INFO] : chain_tbqeb complete.')
    elif mode == 'chain_tqe':
        chain_tqe(cfg=configs, train_ds=train_ds, valid_ds=valid_ds, quantization_ds=quantization_ds,
                  test_ds=test_ds)
        print('[INFO] : chain_tqe complete.')
    elif mode == 'chain_eqe':
        chain_eqe(cfg=configs, float_model_path=float_model_path, train_ds=train_ds, valid_ds=valid_ds,
                  quantization_ds=quantization_ds,
                  test_ds=test_ds)
        print('[INFO] : chain_eqe complete.')
    elif mode == 'chain_qb':
        chain_qb(cfg=configs, float_model_path=float_model_path, train_ds=train_ds,
                 quantization_ds=quantization_ds)
        print('[INFO] : chain_qb complete.')
    elif mode == 'chain_eqeb':
        chain_eqeb(cfg=configs, float_model_path=float_model_path, train_ds=train_ds, valid_ds=valid_ds,
                   quantization_ds=quantization_ds,
                   test_ds=test_ds)
        print('[INFO] : chain_eqeb complete.')
    elif mode == 'chain_qd':
        chain_qd(cfg=configs, float_model_path=float_model_path, train_ds=train_ds,
                 quantization_ds=quantization_ds)
        print('[INFO] : chain_qd complete.')
    # Raise an error if an invalid mode is selected
    else:
        raise ValueError(f"Invalid mode: {mode}")
    
    if mode in ['benchmarking', 'chain_qb', 'chain_eqeb', 'chain_tbqeb']:
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

    # Configure the GPU (the 'general' section may be missing)
    if "general" in cfg and cfg.general:
        if "gpu_memory_limit" in cfg.general and cfg.general.gpu_memory_limit:
            set_gpu_memory_limit(cfg.general.gpu_memory_limit)

    # Parse the configuration file
    cfg = get_config(cfg)

    cfg.output_dir = HydraConfig.get().run.dir
    mlflow_ini(cfg)
    # Global seed for random generators
    seed = int(cfg.general.global_seed)
    print(f'The random seed for this simulation is {seed}')
    if seed is not None:
        tf.keras.utils.set_random_seed(seed)
    # Extract the mode from the command-line arguments
    mode = cfg.operation_mode
    valid_modes = ['training', 'evaluation', 'chain_tbqeb', 'chain_tqe']
    if mode in valid_modes:
        # Perform further processing based on the selected mode
        preprocess_output = preprocess(cfg=cfg)
        train_ds, valid_ds, quantization_ds, test_ds = preprocess_output
        # Process the selected mode
        process_mode(mode=mode, configs=cfg, train_ds=train_ds, valid_ds=valid_ds, quantization_ds=quantization_ds,
                     test_ds=test_ds)
    elif mode == 'quantization':
        if cfg.dataset.training_path or cfg.dataset.quantization_path:
            # Perform further processing based on the selected mode
            preprocess_output = preprocess(cfg=cfg)
            train_ds, valid_ds, quantization_ds, test_ds = preprocess_output
            # Process the selected mode
            process_mode(mode=mode, configs=cfg, train_ds=train_ds, valid_ds=valid_ds, quantization_ds=quantization_ds,
                         test_ds=test_ds)
        else:
            process_mode(mode=mode, configs=cfg, fake=True)
    else:
        if mode in ['chain_eqe', 'chain_qb', 'chain_eqeb', 'chain_qd']:
            if cfg.dataset.training_path or cfg.dataset.quantization_path:
                preprocess_output = preprocess(cfg=cfg)
                train_ds, valid_ds, quantization_ds, test_ds = preprocess_output
            else:
                train_ds = valid_ds = quantization_ds = test_ds = None
            process_mode(mode=mode, configs=cfg, train_ds=train_ds, valid_ds=valid_ds, quantization_ds=quantization_ds,
                         test_ds=test_ds, float_model_path=cfg.general.model_path)
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
