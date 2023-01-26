# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import ssl

import numpy as np
import sklearn.metrics
import tensorflow as tf
import tqdm
from visualize import plot_confusion_matrix

ssl._create_default_https_context = ssl._create_unverified_context
os.environ['NO_SSL_VERIFY'] = '1'


def evaluate_TFlite_quantized_model(quantized_model_path, test_dataset, cfg):
    tf.print('[INFO] Evaluating the quantized model ...')
    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    interpreter_quant.allocate_tensors()
    input_details = interpreter_quant.get_input_details()[0]
    input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]
    test_pred = []
    test_labels = []
    for inputs, labels in tqdm.tqdm(test_dataset, total=len(list(test_dataset))):
        count = 0
        for input in inputs:
            if input_details['dtype'] in [np.uint8, np.int8]:
                input_processed = (input / input_details['quantization'][0]) + input_details['quantization'][1]
                input_processed = np.clip(np.round(input_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
            else:
                input_processed = input
            input_processed = tf.cast(input_processed, dtype=input_details['dtype'])
            input_processed = tf.expand_dims(input_processed, 0)
            interpreter_quant.set_tensor(input_index_quant, input_processed)
            interpreter_quant.invoke()
            test_pred_score = interpreter_quant.get_tensor(output_index_quant)
            if test_pred_score.shape[1] > 1:
                # Multi-lables classification
                # test_pred.append(np.argmax(test_pred_score, axis=1))
                test_pred.append(test_pred_score)
                test_labels.append(labels[count].numpy())
            else:
                # Binary classification
                test_pred_score = np.where(test_pred_score < 0.5, 0, 1)
                test_pred.append(test_pred_score)
                test_labels.append(labels[count].numpy())
            count = count+1
    labels = np.argmax(np.array(test_labels), axis=1)
    logits = np.argmax(np.concatenate(test_pred, axis=0), axis=1)

    cm = sklearn.metrics.confusion_matrix(labels, logits)
    accuracy = np.round(sklearn.metrics.accuracy_score(labels, logits) * 100, 2)
    print("[INFO] : Quantized model Accuracy = {} %".format(accuracy))
    plot_confusion_matrix(cm, class_names=cfg.dataset.class_names,
                          model_name="quantized_model_confusion_matrix", test_accuracy=str(accuracy))
    return accuracy


def get_model_name(cfg):

  strings = list(cfg['model']['model_type'].values())
  strings.append(str(cfg['model']['input_shape'][0]))
  strings.append(cfg['dataset']['name'])

  name = '_'.join([str(i) for i in strings])

  return name

