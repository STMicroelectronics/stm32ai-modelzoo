# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from pathlib import Path
import warnings
import sklearn
import mlflow
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
import numpy as np

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import tqdm
from typing import Optional

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../../common'))
sys.path.append(os.path.abspath('../preprocessing'))
from preprocess import apply_rescaling, postprocess_output, preprocess_input
from visualizer import confusion_matrix, plot_confusion_matrix
from utils import log_to_file


def evaluate_tflite_quantized_model(quantized_model_path: str = None, eval_ds: tf.data.Dataset = None,
                                    class_names: list = None, output_dir: str = None,
                                    name_ds: Optional[str] = 'test_set') -> float:
    """
    Evaluates the accuracy of a quantized TensorFlow Lite model using tflite.interpreter and plots the confusion matrix.

    Args:
        quantized_model_path (str): The file path to the quantized TensorFlow Lite model.
        eval_ds (tf.data.Dataset): The test dataset to evaluate the model on.
        class_names (list): A list of class names for the confusion matrix.
        output_dir (str): The directory where to save the image.
        name_ds (str): The name of the chosen eval_ds to be mentioned in the prints and figures.
    Returns:
        float: The accuracy of the quantized model.
    """
    tf.print(f'[INFO] : Evaluating the quantized model using {name_ds}...')
    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    interpreter_quant.allocate_tensors()
    input_details = interpreter_quant.get_input_details()[0]
    input_index_quant = input_details["index"]
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]
    output_details = interpreter_quant.get_output_details()[0]
    test_pred = []
    test_labels = []
    for images, labels in tqdm.tqdm(eval_ds, total=len(eval_ds)):
        for image, label in zip(images, labels):
            image_processed = preprocess_input(image, input_details)
            interpreter_quant.set_tensor(input_index_quant, image_processed)
            interpreter_quant.invoke()
            test_pred_score = interpreter_quant.get_tensor(output_index_quant)
            predicted_label = postprocess_output(test_pred_score, output_details)
            test_pred.append(predicted_label)
            test_labels.append(label.numpy())

    labels = np.array(test_labels)
    logits = np.concatenate(test_pred, axis=0)
    logits = np.squeeze(logits)
    cm = sklearn.metrics.confusion_matrix(labels, logits)
    accuracy = round((np.sum(labels == logits) * 100) / len(test_labels), 2)
    print("[INFO] : Accuracy of quantized model = {} %".format(accuracy))
    log_to_file(output_dir,  "\n" + "Quantized model :")
    log_to_file(output_dir, f"Accuracy of quantized model : {accuracy} %")
    mlflow.log_metric(f"int_acc_{name_ds}", accuracy)
    plot_confusion_matrix(cm, class_names=class_names, model_name=f"quantized_model_confusion_matrix_{name_ds}",
                          test_accuracy=str(accuracy), output_dir=output_dir)
    return accuracy


def evaluate_h5_model(model_path: str = None, eval_ds: tf.data.Dataset = None, class_names: list = None,
                      output_dir: str = None, name_ds: Optional[str] = 'test_set') -> float:
    """
    Evaluates a trained Keras model saved in .h5 format on the provided test data.

    Args:
        model_path (str): The file path to the .h5 model.
        eval_ds (tf.data.Dataset): The test data to evaluate the model on.
        class_names (list): A list of class names for the confusion matrix.
        output_dir (str): The directory where to save the image.
        name_ds (str): The name of the chosen eval_ds to be mentioned in the prints and figures.
    Returns:
        float: The accuracy of the model on the test data.
    """

    # Load the .h5 model
    model = tf.keras.models.load_model(model_path)
    if len(class_names) > 2:
        model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
    else:
        model.compile(loss=tf.keras.losses.BinaryCrossentropy(), metrics=['accuracy'])
    # Evaluate the model on the test data
    tf.print(f'[INFO] : Evaluating the float model using {name_ds}...')
    loss, accuracy = model.evaluate(eval_ds)
    confusion_matrix(test_set=eval_ds, model=model, class_names=class_names, output_dir=output_dir, name_ds=name_ds)
    print(f"[INFO] : Accuracy of float model = {round(accuracy * 100, 2)}%")
    print(f"[INFO] : Loss of float model = {loss}")
    mlflow.log_metric(f"float_acc_{name_ds}", round(accuracy * 100, 2))
    mlflow.log_metric(f"float_loss_{name_ds}", loss)
    log_to_file(output_dir, "\n" + "Float model :")
    log_to_file(output_dir, f"Accuracy of float model : {round(accuracy * 100, 2)} %")
    log_to_file(output_dir, f"Loss of float model : {round(loss,2)} ")
    return accuracy


def evaluate(cfg: DictConfig = None, eval_ds: tf.data.Dataset = None,
             model_path_to_evaluate: Optional[str] = None, name_ds: Optional[str] = 'test_set') -> None:
    """
    Evaluates and benchmarks a TensorFlow Lite or Keras model, and generates a Config header file if specified.

    Args:
        cfg (config): The configuration file.
        eval_ds (tf.data.Dataset): The validation dataset.
        model_path_to_evaluate (str, optional): Model path to evaluate
        name_ds (str): The name of the chosen test_data to be mentioned in the prints and figures.

    Returns:
        None
    """
    output_dir = HydraConfig.get().runtime.output_dir
    class_names = cfg.dataset.class_names
    # Pre-process test dataset
    eval_ds = apply_rescaling(dataset=eval_ds, scale=cfg.preprocessing.rescaling.scale,
                              offset=cfg.preprocessing.rescaling.offset)
    
    model_path = model_path_to_evaluate if model_path_to_evaluate else cfg.general.model_path

    try:
        # Check if the model is a TensorFlow Lite model
        file_extension = Path(model_path).suffix
        if file_extension == '.h5':
            # Evaluate Keras model
            evaluate_h5_model(model_path=model_path, eval_ds=eval_ds,
                              class_names=class_names, output_dir=output_dir, name_ds=name_ds)
        elif file_extension == '.tflite':
            # Evaluate quantized TensorFlow Lite model
            evaluate_tflite_quantized_model(quantized_model_path=model_path,
                                            eval_ds=eval_ds, class_names=class_names,
                                            output_dir=output_dir, name_ds=name_ds)
    except Exception:
        raise ValueError(f"Model accuracy evaluation failed\nReceived model path: {model_path}")
