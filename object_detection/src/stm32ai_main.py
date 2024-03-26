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
import hydra
import argparse
from omegaconf import DictConfig
from hydra.core.hydra_config import HydraConfig
import mlflow
import tensorflow as tf
from typing import Dict, Generator, Optional


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
from parse_config import get_config
from train import train
from evaluate import evaluate
from quantize import quantize
from benchmark import benchmark
from deploy import deploy

from tiny_yolo_v2_preprocess import tiny_yolo_v2_preprocess
from tiny_yolo_v2_train import train_tiny_yolo_v2
from tiny_yolo_v2_quantize import quantize_tiny_yolo_v2
from tiny_yolo_v2_evaluate import evaluate_tiny_yolo_v2
from tiny_yolo_v2_predict import predict_tiny_yolo_v2

def process_mode(cfg: DictConfig = None,
                 train_ds: Dict = None, valid_ds: Dict = None, test_ds: Dict = None,
                 quantization_ds: Dict = None,  
                 train_gen: Generator = None, valid_gen: Generator = None):
    """
    Process the selected operation mode.
    Args:
        cfg (DictConfig): entire configuration file dictionary.
        train_ds (Dict): training dataset.
        valid_ds (Dict): validation dataset.
        test_ds (Dict): test dataset.
        quantization_ds (Dict): quantization dataset.
        train_gen (Generator): training generator, required for operation modes that include a training.
        valid_gen (Generator): training generator, required for operation modes that include a training.
    Returns:
        None
    """
    if cfg.general.model_type == "tiny_yolo_v2" or cfg.general.model_type == "st_yolo_lc_v1":
        train_glob = train_tiny_yolo_v2
        quantize_glob = quantize_tiny_yolo_v2
        evaluate_glob = evaluate_tiny_yolo_v2
        predict_glob = predict_tiny_yolo_v2
    else:
        train_glob = train
        quantize_glob = quantize
        evaluate_glob = evaluate
    
    mode = cfg.operation_mode
    if mode == 'training':
        train_glob(cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds, train_gen=train_gen, valid_gen=valid_gen)
        
    elif mode == 'evaluation':
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds)

    elif mode == 'quantization':
        quantize_glob(cfg)

    elif mode == 'benchmarking':
        benchmark(cfg)

    elif mode == 'deployment':
        deploy(cfg)

    elif mode == 'chain_tqe':
        trained_model = train_glob(cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds, train_gen=train_gen, valid_gen=valid_gen)
        quantized_model_path = quantize_glob(cfg, model_path=trained_model)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        print("[INFO] chain_tqe complete")

    elif mode == 'chain_tqeb':
        trained_model = train_glob(cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds, train_gen=train_gen, valid_gen=valid_gen)
        quantized_model_path = quantize_glob(cfg, model_path=trained_model)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        benchmark(cfg, model_path=quantized_model_path)
        print("[INFO] chain_tqeb complete")

    elif mode == 'chain_eqe':
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds)
        quantized_model_path = quantize_glob(cfg)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        print("[INFO] chain_eqe complete")

    elif mode == 'chain_eqeb':
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds)
        quantized_model_path = quantize_glob(cfg)
        evaluate_glob(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=quantized_model_path)
        benchmark(cfg, model_path=quantized_model_path)
        print("[INFO] chain_eqeb complete")

    elif mode == 'chain_qb':
        quantized_model_path = quantize_glob(cfg)
        benchmark(cfg, model_path=quantized_model_path)
        print("[INFO] chain_qb complete")

    elif mode == 'chain_qd':
        quantized_model_path = quantize_glob(cfg)
        deploy(cfg, model_path_to_deploy=quantized_model_path)
        print("[INFO] chain_qd complete")

    elif mode == 'prediction':
        predict_glob(cfg)
    else:
        raise RuntimeError(f"Internal error: invalid operation mode: {mode}")

    if mode in ['benchmarking', 'chain_tbqeb', 'chain_qb', 'chain_eqeb']:
        mlflow.log_param("model_path", cfg.general.model_path)
        mlflow.log_param("stm32ai_version", cfg.tools.stm32ai.version)
        mlflow.log_param("target", cfg.benchmarking.board)


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
   
    if "general" in cfg and cfg.general:
        # Set upper limit on usable GPU memory
        if "gpu_memory_limit" in cfg.general and cfg.general.gpu_memory_limit:
            set_gpu_memory_limit(cfg.general.gpu_memory_limit)
            print(f"[INFO] Setting upper limit of usable GPU memory to {int(cfg.general.gpu_memory_limit)}GBytes.")
        else:
            print("[WARNING] The usable GPU memory is unlimited.\n"
                  "Please consider setting the 'gpu_memory_limit' attribute "
                  "in the 'general' section of your configuration file.")

        # Set global seed
        if "global_seed" in cfg.general:
            if cfg.general.global_seed == "None":
                print("[WARNING] No seed for random generators was specified.\n"
                      "Results may be more difficult to reproduce from one run to another.")
            elif cfg.general.global_seed:
                tf.keras.utils.set_random_seed(int(cfg.general.global_seed))
            else:
                # Default seed
                tf.keras.utils.set_random_seed(123)

    # Parse the configuration file
    cfg = get_config(cfg)

    # Initialize MLflow
    mlflow_ini(cfg)
    if cfg.general.model_type == "tiny_yolo_v2" or cfg.general.model_type == "st_yolo_lc_v1":
        preprocess_output = tiny_yolo_v2_preprocess(cfg)
    else: 
        preprocess_output = preprocess(cfg)

    train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen = preprocess_output

    process_mode(cfg, train_ds=train_ds, valid_ds=valid_ds, test_ds=test_ds,
                 quantization_ds=quantization_ds,
                 train_gen=train_gen, valid_gen=valid_gen)
    

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
