# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
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
from datasets import load_ESC_10, load_custom_esc_like_multiclass
from quantization import TFLite_PTQ_quantizer
from utils import get_config, mlflow_ini, setup_seed
from visualize import _compute_confusion_matrix, _plot_confusion_matrix
from evaluation import _aggregate_predictions, compute_accuracy_score


def evaluate_model(cfg, c_header=False, c_code=False):

    """
    Quantize, evaluate and benchmark model.
    Generate Config header file.
    """

    if (cfg.model.model_path.split(".")[-1] == 'tflite'):
        # Convert a tflite model using STM32Cube.AI
        quantized_model_path = cfg.model.model_path

        # Benchmark/Generating C model
        stm32ai_benchmark(cfg, quantized_model_path, c_code)

        # Evaluate the quantized model
        if cfg.quantization.evaluate:

            # Adding batch_size to load dataset
            second_conf = OmegaConf.create({"train_parameters": {"batch_size": 64}})
            OmegaConf.set_struct(cfg, False)
            cfg = OmegaConf.merge(cfg, second_conf)
            OmegaConf.set_struct(cfg, True)

            #get datasets
            if cfg.dataset.name.lower()=="esc10":
                train_ds, valid_ds, test_ds, clip_labels = load_ESC_10(cfg)
            elif cfg.dataset.name.lower()=="custom" and not cfg.model.multi_label:
                train_ds, valid_ds, test_ds, clip_labels = load_custom_esc_like_multiclass(cfg)
            elif cfg.dataset.name.lower()=="custom" and cfg.model.multi_label:
                raise NotImplementedError("Multilabel support not implemented yet !")
            else:
                raise NotImplementedError("Please choose a valid dataset ('esc10' or 'custom')")

            X_test, y_test = test_ds[0], test_ds[1]
            q_patch_level_acc, q_clip_level_acc = evaluate_TFlite_quantized_model(quantized_model_path, X_test, y_test, clip_labels, cfg)
            mlflow.log_metric("int_patch_test_acc", q_patch_level_acc)
            mlflow.log_metric("int_clip_test_acc", q_clip_level_acc)

    else:
        # Load the model
        model = tf.keras.models.load_model(cfg.model.model_path)
        # Estimate the model footprints, quantize and convert the float model using STM32Cube.AI
        if cfg.dataset.csv_path is None and cfg.dataset.validation_path is None and cfg.dataset.test_path is None:
            TFLite_PTQ_quantizer(cfg, model, train_ds=None, fake=True)
            quantized_model_path = os.path.join(HydraConfig.get().runtime.output_dir,
                                                "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))

            # Benchmark/Generating C model
            stm32ai_benchmark(cfg, quantized_model_path, c_code)

        else:
            # Adding batch_size to load dataset
            second_conf = OmegaConf.create({"train_parameters": {"batch_size": 64}})
            OmegaConf.set_struct(cfg, False)
            cfg = OmegaConf.merge(cfg, second_conf)
            OmegaConf.set_struct(cfg, True)

            # Get datasets
            if cfg.dataset.name.lower()=="esc10":
                train_ds, valid_ds, test_ds, clip_labels = load_ESC_10(cfg)
            elif cfg.dataset.name.lower()=="custom" and not cfg.model.multi_label:
                train_ds, valid_ds, test_ds, clip_labels = load_custom_esc_like_multiclass(cfg)
            elif cfg.dataset.name.lower()=="custom" and cfg.model.multi_label:
                raise NotImplementedError("Multilabel support not implemented yet !")
            else:
                raise NotImplementedError("Please choose a valid dataset ('esc10' or 'custom')")

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
               
                # Generate the confusion matrix for the float model
                X_test, y_test = test_ds[0], test_ds[1]

                test_preds = model.predict(X_test)
                aggregated_preds = _aggregate_predictions(preds=test_preds,
                                                            clip_labels=clip_labels,
                                                            is_multilabel=cfg.model.multi_label,
                                                            is_truth=False)
                aggregated_truth = _aggregate_predictions(preds=y_test,
                                                            clip_labels=clip_labels,
                                                            is_multilabel=cfg.model.multi_label,
                                                            is_truth=True)

                # generate the confusion matrix for the float model
                patch_level_accuracy = compute_accuracy_score(y_test, test_preds,
                                                                is_multilabel=cfg.model.multi_label)

                print("[INFO] : Patch-level accuracy on test set : {}".format(patch_level_accuracy))

                clip_level_accuracy = compute_accuracy_score(aggregated_truth, aggregated_preds,
                                                                is_multilabel=cfg.model.multi_label)

                print("[INFO] : Clip-level accuracy on test set : {}".format(clip_level_accuracy))

                patch_level_confusion_matrix = _compute_confusion_matrix(y_test, test_preds,
                                                                         is_multilabel=cfg.model.multi_label)
                clip_level_confusion_matrix = _compute_confusion_matrix(aggregated_truth, aggregated_preds,
                                                                        is_multilabel=cfg.model.multi_label)

                _plot_confusion_matrix(patch_level_confusion_matrix,
                                        class_names=cfg.dataset.class_names,
                                        title="Float model Patch-level CM",
                                        test_accuracy=patch_level_accuracy)

                _plot_confusion_matrix(clip_level_confusion_matrix,
                                        class_names=cfg.dataset.class_names,
                                        title="Float model Clip-level CM",
                                        test_accuracy=clip_level_accuracy)

                # Evaluate the quantized model on test set
                if cfg.quantization.quantizer == "TFlite_converter":
                    q_patch_level_acc, q_clip_level_acc = evaluate_TFlite_quantized_model(quantized_model_path,
                                                            X_test, y_test, clip_labels, cfg)
                    mlflow.log_metric("int_patch_test_acc", q_patch_level_acc)
                    mlflow.log_metric("int_clip_test_acc", q_clip_level_acc)
                else:
                    raise TypeError("Quantizer not supported yet!")

    if c_header:
        print("[INFO] C header file generation not implemented in v1 of the model zoo for AED")
        # Generate Config.h for C embedded application
        # gen_h_user_file(cfg, quantized_model_path)


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
