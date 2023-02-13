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
from benchmark import evaluate_TFlite_quantized_model
from common_benchmark import stm32ai_benchmark
from datasets import WISDM
from header_file_generator import gen_h_user_file
from quantization import TFLite_PTQ_quantizer
from utils import get_config, mlflow_ini, setup_seed
from visualize import training_confusion_matrix


def load_dataset(cfg):
    if not cfg.dataset.name == 'wisdm':
        print('[ERROR] : DATASET not Supproted!')
        print('[ERROR] : Only widsm dataset is supported now, link to download : ')
        print('[Error] : link to download:')
        print('[ERROR] : https://www.cis.fordham.edu/wisdm/includes/datasets/latest/WISDM_ar_latest.tar.gz')
        raise TypeError("Provide correct path to WISDM dataset")
    # Adding batch_size to load dataset
    second_conf = OmegaConf.create({"tf_train_parameters": {"batch_size": 32}})
    OmegaConf.set_struct(cfg, False)
    cfg = OmegaConf.merge(cfg, second_conf)
    OmegaConf.set_struct(cfg, True)

    # get datasets
    data_handler = WISDM(cfg)
    train_ds, _, test_ds = data_handler.get_dataset()
    return train_ds, test_ds


def evaluate_model(cfg, c_header=False, c_code=False):

    """
    Quantize, evaluate and benchmark model.
    Generate Config header file.
    """

    if cfg.model.model_type.name.lower() == 'svc':
        model_path = cfg.model.model_path
        # Benchmark/Generating C model
        stm32ai_benchmark(cfg, model_path, c_code)

    elif (cfg.model.model_path.split(".")[-1] == 'tflite'):
        # Convert a tflite model using STM32Cube.AI
        quantized_model_path = cfg.model.model_path

        # Benchmark/Generating C model
        stm32ai_benchmark(cfg, quantized_model_path, c_code)

        # Evaluate the quantized model
        if cfg.quantization.evaluate:
            # load the dataset
            train_ds, test_ds = load_dataset(cfg)
            q_acc = evaluate_TFlite_quantized_model(quantized_model_path, test_ds, cfg)
            mlflow.log_metric("int_test_acc", q_acc)

    else:
        # Load the model
        model = tf.keras.models.load_model(cfg.model.model_path)
        # Estimate the model footprints, quantize and convert the float model using STM32Cube.AI

        if not cfg.quantization.quantize:
            # Benchmark/Generating C model
            stm32ai_benchmark(cfg, cfg.model.model_path, c_code)

        else:
            if cfg.dataset.training_path is None:
                TFLite_PTQ_quantizer(cfg, model, train_ds=None, fake=True)
                quantized_model_path = os.path.join(HydraConfig.get().runtime.output_dir,
                                                    "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))

                # Benchmark/Generating C model
                stm32ai_benchmark(cfg, quantized_model_path, c_code)

            else:

                # Check train set is provided
                if cfg.dataset.training_path is None:
                    raise TypeError("Path to Training set is empty. Please provide the training set used to train the model in order to quantize it!")

                # get the dataset
                train_ds, test_ds = load_dataset(cfg)

                print("[INFO] : Quantizing the model ... This might take few minutes ...")
                if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
                    TFLite_PTQ_quantizer(cfg, model, train_ds, fake=False)
                    quantized_model_path = os.path.join(HydraConfig.get().runtime.output_dir,
                                                        "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))
                else:
                    raise TypeError("Quantizer and quantization type not supported yet!")

                # Benchmark/Generating C model
                stm32ai_benchmark(cfg, quantized_model_path, c_code)

                # Evaluate the quantized model
                if cfg.quantization.evaluate:
                    # Evaluate the quantized model on test set

                    # Generate the confusion matrix for the float model
                    training_confusion_matrix(test_ds, model, cfg.dataset.class_names)

                    if cfg.quantization.quantizer == "TFlite_converter":
                        q_acc = evaluate_TFlite_quantized_model(quantized_model_path, test_ds, cfg)
                    else:
                        raise TypeError("Quantizer not supported yet!")
                    mlflow.log_metric("int_test_acc", q_acc)

    if c_header:
        # Generate Config.h for C embedded application
        gen_h_user_file(cfg)


@hydra.main(version_base=None, config_path="", config_name="user_config")
def main(cfg: DictConfig) -> None:
    # Initilize configuration & mlflow
    configs = get_config(cfg)
    mlflow_ini(configs)

    # Set all seeds
    setup_seed(611)

    # Evaluate model performance / footprints
    evaluate_model(cfg)

    # Record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()


if __name__ == "__main__":
    main()
