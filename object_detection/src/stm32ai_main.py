# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import sys
from hydra.core.hydra_config import HydraConfig
import hydra
import warnings

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
from omegaconf import DictConfig
import mlflow
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/benchmarking'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/deployment'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/quantization'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/optimization'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/evaluation'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/training'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../deployment'))
sys.path.append(os.path.join(os.path.dirname(__file__), './data_augmentation'))
sys.path.append(os.path.join(os.path.dirname(__file__), './preprocessing'))
sys.path.append(os.path.join(os.path.dirname(__file__), './postprocessing'))
sys.path.append(os.path.join(os.path.dirname(__file__), './training'))
sys.path.append(os.path.join(os.path.dirname(__file__), './utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), './evaluation'))
sys.path.append(os.path.join(os.path.dirname(__file__), './quantization'))
sys.path.append(os.path.join(os.path.dirname(__file__), './prediction'))
sys.path.append(os.path.join(os.path.dirname(__file__), './models'))

if sys.platform.startswith('linux'):
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/optimization/linux'))
elif sys.platform.startswith('win'):
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../common/optimization/windows'))

from logs_utils import mlflow_ini
from gpu_utils import set_gpu_memory_limit
from cfg_utils import get_random_seed
from preprocess import preprocess
from parse_config import get_config
from train import train
from evaluate import evaluate
from deploy import deploy, deploy_mpu
from quantize import quantize
from predict import predict
from typing import Dict, Generator, Optional
from common_benchmark import benchmark, cloud_connect
from logs_utils import log_to_file

from tiny_yolo_v2_preprocess import tiny_yolo_v2_preprocess
from tiny_yolo_v2_train import train_tiny_yolo_v2
from tiny_yolo_v2_evaluate import evaluate_tiny_yolo_v2


def process_mode(cfg: DictConfig = None,
                 train_ds: Dict = None, valid_ds: Dict = None, test_ds: Dict = None,
                 quantization_ds: Dict = None,
                 train_gen: Generator = None, valid_gen: Generator = None, quant_gen: Generator = None):
    """
    Process the selected operation mode.
    Args:
        cfg (DictConfig): entire configuration file dictionary.
        train_ds (Dict): training dataset.
        valid_ds (Dict): validation dataset.
        test_ds (Dict): test dataset.
        quantization_ds (Dict): quantization dataset.
        train_gen (Generator): training generator, required for operation modes that include a training.
        valid_gen (Generator): validation generator, required for operation modes that include a validation / evaluation.
        quant_gen (Generator): quantization generator, required for operation modes that include a quantization
    Returns:
        None
    """

    quant_data = quant_gen

    if cfg.general.model_type == "tiny_yolo_v2" or cfg.general.model_type == "st_yolo_lc_v1":
        train_glob = train_tiny_yolo_v2
        evaluate_glob = evaluate_tiny_yolo_v2
    else:
        train_glob = train
        evaluate_glob = evaluate

    mode = cfg.operation_mode
    # logging the operation_mode in the output_dir/stm32ai_main.log file
    log_to_file(cfg.output_dir, f'operation_mode: {mode}')
    if mode == 'training':
        train_glob(cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds, train_gen=train_gen, valid_gen=valid_gen)

    elif mode == 'evaluation':
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds)

    elif mode == 'quantization':
        quantize(cfg, quant_data=quant_data)

    elif mode == 'benchmarking':
        benchmark(cfg)

    elif mode == 'deployment':
        if cfg.hardware_type == "MPU":
            deploy_mpu(cfg=cfg)
        else:
            deploy(cfg)

    elif mode == 'chain_tqe':
        trained_model = train_glob(cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds, train_gen=train_gen, valid_gen=valid_gen)
        quantized_model_path = quantize(cfg, model_path=trained_model, quant_data=quant_data)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        print("[INFO] : chain_tqe complete")

    elif mode == 'chain_tqeb':
        # Connect to STM32Cube.AI Developer Cloud
        credentials = None
        if cfg.tools.stm32ai.on_cloud:
            _, _, credentials = cloud_connect(stm32ai_version=cfg.tools.stm32ai.version)
        trained_model = train_glob(cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds, train_gen=train_gen, valid_gen=valid_gen)
        quantized_model_path = quantize(cfg, model_path=trained_model, quant_data=quant_data)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        benchmark(cfg, model_path_to_benchmark=quantized_model_path, credentials=credentials)
        print("[INFO] : chain_tqeb complete")

    elif mode == 'chain_eqe':
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds)
        quantized_model_path = quantize(cfg, quant_data=quant_data)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        print("[INFO] : chain_eqe complete")

    elif mode == 'chain_eqeb':
        credentials = None
        if cfg.tools.stm32ai.on_cloud:
            _, _, credentials = cloud_connect(stm32ai_version=cfg.tools.stm32ai.version)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds)
        quantized_model_path = quantize(cfg, quant_data=quant_data)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        benchmark(cfg, model_path_to_benchmark=quantized_model_path, credentials=credentials)
        print("[INFO] : chain_eqeb complete")

    elif mode == 'chain_qb':
        credentials = None
        if cfg.tools.stm32ai.on_cloud:
            _, _, credentials = cloud_connect(stm32ai_version=cfg.tools.stm32ai.version)
        quantized_model_path = quantize(cfg, quant_data=quant_data)
        benchmark(cfg, model_path_to_benchmark=quantized_model_path, credentials=credentials)
        print("[INFO] : chain_qb complete")

    elif mode == 'chain_qd':
        quantized_model_path = quantize(cfg, quant_data=quant_data)
        if cfg.hardware_type == "MPU":
            deploy_mpu(cfg, model_path_to_deploy=quantized_model_path)
        else:
            deploy(cfg, model_path_to_deploy=quantized_model_path)
        print("[INFO] : chain_qd complete")

    elif mode == 'prediction':
        predict(cfg)
    else:
        raise RuntimeError(f"Internal error: invalid operation mode: {mode}")

    if mode in ['benchmarking', 'chain_tbqeb', 'chain_qb', 'chain_eqeb']:
        mlflow.log_param("model_path", cfg.general.model_path)
        mlflow.log_param("stm32ai_version", cfg.tools.stm32ai.version)
        mlflow.log_param("target", cfg.benchmarking.board)

    # logging the completion of the chain
    log_to_file(cfg.output_dir, f'operation finished: {mode}')

#choices=['training' , 'evaluation', 'deployment', 'quantization', 'benchmarking',
#        '','','','','','chain_qd ']


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
        # Set upper limit on usable GPU memory
        if "gpu_memory_limit" in cfg.general and cfg.general.gpu_memory_limit:
            set_gpu_memory_limit(cfg.general.gpu_memory_limit)
            print(f"[INFO] : Setting upper limit of usable GPU memory to {int(cfg.general.gpu_memory_limit)}GBytes.")
        else:
            print("[WARNING] The usable GPU memory is unlimited.\n"
                  "Please consider setting the 'gpu_memory_limit' attribute "
                  "in the 'general' section of your configuration file.")

    # Parse the configuration file
    cfg = get_config(cfg)
    cfg.output_dir = HydraConfig.get().run.dir
    mlflow_ini(cfg)

    # Seed global seed for random generators
    seed = get_random_seed(cfg)
    print(f'[INFO] : The random seed for this simulation is {seed}')
    if seed is not None:
        tf.keras.utils.set_random_seed(seed)

    # Extract the mode from the command-line arguments
    mode = cfg.operation_mode
    if cfg.hardware_type == "MCU":
        if mode not in ["benchmarking"]:
            if cfg.general.model_type == "tiny_yolo_v2" or cfg.general.model_type == "st_yolo_lc_v1":
                train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen, quantization_gen = tiny_yolo_v2_preprocess(cfg)
            else:
                train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen, quantization_gen = preprocess(cfg)
        else:
            train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen, quantization_gen = None, None, None, None, None, None, None
    else:
        if mode not in ["benchmarking","deployment"]:
            if cfg.general.model_type == "tiny_yolo_v2" or cfg.general.model_type == "st_yolo_lc_v1":
                train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen, quantization_gen = tiny_yolo_v2_preprocess(cfg)
            else:
                train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen, quantization_gen = preprocess(cfg)
        else:
            train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen, quantization_gen = None, None, None, None, None, None, None

    process_mode(cfg,
                 train_ds=train_ds,
                 valid_ds=valid_ds,
                 test_ds=test_ds,
                 quantization_ds=quantization_ds,
                 train_gen=train_gen,
                 valid_gen=valid_gen,
                 quant_gen=quantization_gen)


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
