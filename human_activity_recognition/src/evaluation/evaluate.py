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
sys.path.append(os.path.abspath('../utils/models'))
sys.path.append(os.path.abspath('../../common'))
from visualizer import confusion_matrix, plot_confusion_matrix


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
    if len(class_names) > 2:
        # model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
        model.compile(loss=tf.keras.losses.CategoricalCrossentropy(), metrics=['accuracy'])

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
