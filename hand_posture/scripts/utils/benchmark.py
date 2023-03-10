# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np
import sklearn.metrics
import tensorflow as tf
import tqdm

from visualize import *


def evaluate_TFlite_quantized_model(quantized_model_path, test_dataset, cfg):
    """ Evaluate accuracy of the quantized model using tflite.interpreter and plot confusion matrix. """

    tf.print('[INFO] Evaluating the quantized model ...')
    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    interpreter_quant.allocate_tensors()
    input_details = interpreter_quant.get_input_details()[0]
    input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]
    test_pred = []
    test_labels = []
    for images, labels in tqdm.tqdm(test_dataset, total=len(list(test_dataset))):
        count = 0
        for image in images:
            if input_details['dtype'] in [np.uint8, np.int8]:
                image_processed = (image / input_details['quantization'][0]) + input_details['quantization'][1]
                image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min,
                                          np.iinfo(input_details['dtype']).max)
            else:
                image_processed = image
            image_processed = tf.cast(image_processed, dtype=input_details['dtype'])
            image_processed = tf.expand_dims(image_processed, 0)
            interpreter_quant.set_tensor(input_index_quant, image_processed)
            interpreter_quant.invoke()
            test_pred_score = interpreter_quant.get_tensor(output_index_quant)
            if test_pred_score.shape[1] > 1:
                # Multi-lables classification
                test_pred.append(np.argmax(test_pred_score, axis=1))
                test_labels.append(labels[count].numpy())
            else:
                # Binary classification
                test_pred_score = np.where(test_pred_score < 0.5, 0, 1)
                test_pred.append(test_pred_score)
                test_labels.append(labels[count].numpy())
            count = count + 1
    labels = np.array(test_labels)
    logits = np.concatenate(test_pred, axis=0)
    logits = np.squeeze(logits)
    cm = sklearn.metrics.confusion_matrix(labels, logits)
    accuracy = round((np.sum(labels == logits) * 100) / len(test_labels), 2)
    print("[INFO] : Quantized model Accuracy = {} %".format(accuracy))
    plot_confusion_matrix(cm, class_names=cfg.dataset.class_names, model_name="quantized_model_confusion_matrix",
                          test_accuracy=str(accuracy))
    return accuracy
