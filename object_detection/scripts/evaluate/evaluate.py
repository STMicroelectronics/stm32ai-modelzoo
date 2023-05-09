# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import logging
import os
import random
import ssl
import sys
import warnings

import hydra
import mlflow
import numpy as np
import tensorflow as tf
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig, OmegaConf
from tensorflow import keras
from tensorflow.keras.utils import get_custom_objects

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../utils/models'))
sys.path.append(os.path.abspath('../../../common'))

import load_models
from anchor_boxes_utils import gen_anchors, get_sizes_ratios
from common_benchmark import (Cloud_benchmark, analyze_footprints,
                              benchmark_model, get_credentials, stm32ai_benchmark)
from callbacks import *
from datasets import *
from datasets import generate, load_data, parse_data
from header_file_generator import *
from loss import ssd_focal_loss
from metrics_utils import calculate_float_map, calculate_quantized_map, relu6
from quantization import *
from utils import get_config, mlflow_ini, setup_seed

logger = tf.get_logger()
logger.setLevel(logging.ERROR)

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
ssl._create_default_https_context = ssl._create_unverified_context

def evaluate_model(cfg, c_header=False, c_code=False):

    if (os.path.splitext(cfg.model.model_path)[-1] == '.tflite'):
        quantized_model_path = cfg.model.model_path
        # Benchmark/Generating C model
        stm32ai_benchmark(cfg, quantized_model_path, c_code)
        # Evaluate the quantized model
        if cfg.quantization.evaluate:
            if (cfg.dataset.validation_path is not None) or (cfg.dataset.validation_path is not None):
                tf.print('[INFO] Evaluating the quantized model ...')
                mAP = calculate_quantized_map(cfg, quantized_model_path)
                mlflow.log_metric("int_model_mAP", mAP)
            else:
                tf.print('[INFO] Please provide a dataset for evaluation ...')
        if c_header:
            # Generate Config.h for C embedded application
            gen_h_user_file(cfg, quantized_model_path)
    else:
        # get loss
        loss = ssd_focal_loss()
        keras_model = tf.keras.models.load_model(cfg.model.model_path,custom_objects={'gen_anchors': gen_anchors, 'relu6': relu6, '_loss': loss})
        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            tf.print("[INFO] : Quantizing the model ... This might take few minutes ...")
            if cfg.dataset.training_path is None:
                TFLite_PTQ_quantizer(cfg, keras_model, fake=True)
                quantized_model_path = os.path.join(HydraConfig.get().runtime.output_dir, "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))
                stm32ai_benchmark(cfg, quantized_model_path, c_code)
                tf.print("[INFO] A Training set was not provided, the model can't be properly quantized for evaluation. Please provide a training dataset")
            else:
                TFLite_PTQ_quantizer(cfg, keras_model, fake=False)
                quantized_model_path = os.path.join(HydraConfig.get().runtime.output_dir, "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))
                stm32ai_benchmark(cfg, quantized_model_path, c_code)
                if cfg.quantization.evaluate:
                    if (cfg.dataset.validation_path is not None) or (cfg.dataset.validation_path is not None):
                        tf.print('[INFO] Evaluating the quantized model ...')
                        mAP = calculate_quantized_map(cfg, quantized_model_path)
                        mlflow.log_metric("int_model_mAP", mAP)
                    else:
                        tf.print('[INFO] Please provide a dataset for evaluation ...')
        else:
            raise TypeError("Quantizer and quantization type not supported yet!")
        if c_header:
            # Generate Config.h for C embedded application
            gen_h_user_file(cfg, quantized_model_path)


@hydra.main(version_base=None, config_path="", config_name="user_config")
def main(cfg: DictConfig) -> None:
    # Initilize configuration & mlflow
    configs = get_config(cfg)
    mlflow_ini(configs)

    # Set all seeds
    setup_seed(42)

    # Evaluate model performance / footprints
    evaluate_model(cfg)

    # Record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()


if __name__ == "__main__":
    main()
