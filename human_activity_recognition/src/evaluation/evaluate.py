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

from models_utils import compute_confusion_matrix
from visualize_utils import plot_confusion_matrix
from models_mgt import get_loss
from logs_utils import log_to_file


def evaluate_h5_model(model_path: str = None,
                      eval_ds: tf.data.Dataset = None,
                      class_names: list = None,
                      output_dir: str = None,
                      name_ds: Optional[str] = 'test_set') -> float:
    """
    Evaluates a trained Keras model saved in .h5 format on the provided test data.

    Args:
        model_path (str): The file path to the .h5 model.
        eval_ds (tf.data.Dataset): The test data to evaluate the model on.
        class_names (list): A list of class names for the confusion matrix.
        output_dir (str): The directory where to save the confusion matrix image.
        name_ds (str): The name of the chosen eval_ds to be mentioned in the prints and figures.
    Returns:
        float: The accuracy of the model on the test data.
    """

    # Load the .h5 model
    model = tf.keras.models.load_model(model_path)
    loss = get_loss(len(class_names))
    model.compile(loss=loss, metrics=['accuracy'])

    # Evaluate the model on the test data
    tf.print(f'[INFO] : Evaluating the float model using {name_ds}...')
    loss, accuracy = model.evaluate(eval_ds)

    # Calculate the confusion matrix.
    cm, test_accuracy = compute_confusion_matrix(test_set=eval_ds, model=model)
    ##########################################
    # Log the confusion matrix as an image summary.
    model_name = f"float_model_confusion_matrix_{name_ds}"
    plot_confusion_matrix(cm=cm, class_names=class_names, model_name=model_name,
                          title=f'{model_name}\naccuracy: {test_accuracy}', output_dir=output_dir)
    print(f"[INFO] : Accuracy of float model = {test_accuracy}%")
    print(f"[INFO] : Loss of float model = {loss}")
    mlflow.log_metric(f"float_acc_{name_ds}", test_accuracy)
    mlflow.log_metric(f"float_loss_{name_ds}", loss)
    log_to_file(output_dir, f"Float model {name_ds}:")
    log_to_file(output_dir, f"Accuracy of float model : {test_accuracy} %")
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
    
    model_path = model_path_to_evaluate if model_path_to_evaluate else cfg.general.model_path

    try:
        # Check if the model is a TensorFlow Lite model
        file_extension = Path(model_path).suffix
        if file_extension == '.h5':
            # Evaluate Keras model
            evaluate_h5_model(model_path=model_path, eval_ds=eval_ds,
                              class_names=class_names, output_dir=output_dir, name_ds=name_ds)
    except Exception:
        raise ValueError("Model accuracy evaluation failed because of wrong model type!\n",
                         f"Received model path: {model_path}")
