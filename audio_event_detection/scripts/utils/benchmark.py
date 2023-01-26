# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import getpass
import json
import os
import pathlib
import sys

import mlflow
import numpy as np
import sklearn.metrics
import tensorflow as tf
import tqdm
from hydra.core.hydra_config import HydraConfig
from visualize import _compute_confusion_matrix, _plot_confusion_matrix
from evaluation import _aggregate_predictions, compute_accuracy_score


def evaluate_TFlite_quantized_model(quantized_model_path, X_test, y_test, clip_labels, cfg):

    """ Evaluate accuracy of the quantized model using tflite.interpreter and plot confusion matrix. """

    tf.print('[INFO] Evaluating the quantized model ...')
    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    
    
    input_details = interpreter_quant.get_input_details()[0]
    tf.print("[INFO] Quantization input details : {}".format(input_details["quantization"]))
    tf.print("[INFO] Dtype input details : {}".format(input_details["dtype"]))
    input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]
    interpreter_quant.resize_tensor_input(input_index_quant, list(X_test.shape))
    interpreter_quant.allocate_tensors()
    X_processed = (X_test / input_details['quantization'][0]) + input_details['quantization'][1]
    X_processed = np.clip(np.round(X_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
    X_processed = X_processed.astype(input_details['dtype'])

    interpreter_quant.set_tensor(input_index_quant, X_processed)
    interpreter_quant.invoke()
    preds = interpreter_quant.get_tensor(output_index_quant)
    
    # Aggregate predictions

    aggregated_preds = _aggregate_predictions(preds=preds,
                                                clip_labels=clip_labels,
                                                is_multilabel=cfg.model.multi_label,
                                                is_truth=False)

    aggregated_truth = _aggregate_predictions(preds=y_test,
                                                clip_labels=clip_labels,
                                                is_multilabel=cfg.model.multi_label,
                                                is_truth=True)
    # generate the confusion matrix for the float model
    patch_level_accuracy = compute_accuracy_score(y_test, preds,
                                                    is_multilabel=cfg.model.multi_label)
    print("[INFO] : Quantized model patch-level accuracy on test set : {}".format(patch_level_accuracy))
    clip_level_accuracy = compute_accuracy_score(aggregated_truth, aggregated_preds,
                                                    is_multilabel=cfg.model.multi_label)
    print("[INFO] : Quantized model clip-level accuracy on test set : {}".format(clip_level_accuracy))

    patch_level_confusion_matrix = _compute_confusion_matrix(y_test, preds,
                                                                is_multilabel=cfg.model.multi_label)
    clip_level_confusion_matrix = _compute_confusion_matrix(aggregated_truth, aggregated_preds,
                                                            is_multilabel=cfg.model.multi_label)

    _plot_confusion_matrix(patch_level_confusion_matrix,
                            class_names=cfg.dataset.class_names,
                            title="Quantized model Patch-level CM",
                            test_accuracy=patch_level_accuracy)

    _plot_confusion_matrix(clip_level_confusion_matrix,
                            class_names=cfg.dataset.class_names,
                            title="Quantized model Clip-level CM",
                            test_accuracy=clip_level_accuracy)

    return patch_level_accuracy, clip_level_accuracy
