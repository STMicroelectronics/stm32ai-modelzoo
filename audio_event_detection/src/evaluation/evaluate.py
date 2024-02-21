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
import warnings
import sklearn
import hydra
import mlflow
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig, OmegaConf
import numpy as np
import numpy.random as rnd
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import tqdm
from typing import Optional, Tuple
from sklearn.metrics import accuracy_score
from pathlib import Path
sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../utils/models'))
sys.path.append(os.path.abspath('../../common'))
sys.path.append(os.path.abspath('../preprocessing'))
sys.path.append(os.path.abspath('../training'))
from preprocess import preprocess_input
from visualizer import compute_confusion_matrix, plot_confusion_matrix
from visualizer import compute_multilabel_confusion_matrices, plot_multilabel_confusion_matrices
from utils import get_loss, log_to_file


def _majority_vote(preds: tf.Tensor, 
                   multi_label: bool = False,
                   return_proba: bool = False):
    '''
    Concatenates several one-hot prediction labels into one, according to majority vote
    Inputs
    ------
    preds : np.ndarray or tf.tensor, shape (n_preds, n_classes).
        Array of one-hot prediction vectors to concatenate 
    multi_label : bool, set to True if prediction vectors are multi_label
    return_proba : bool, if True return probabilities instead of onehot predictions

    Outputs
    -------
    onehot_vote : One-hot encoded aggregated predictions. Only returned if return_proba is False
    aggregated_preds : Averaged predictions. Only returned if return_proba is True.
    '''

    if not multi_label:
        # If we only have one label per sample, pick the one with the most votes
        try:
            preds = preds.numpy()
        except:
            pass
        n_classes = preds.shape[1]

        if return_proba:
            aggregated_preds = np.mean(preds, axis=0)
            return aggregated_preds
        
        aggregated_preds = np.sum(preds, axis=0)
        
        # Fancy version of argmax w/ random selection in case of tie
        vote = rnd.choice(np.flatnonzero(aggregated_preds == aggregated_preds.max()))
        onehot_vote = np.zeros(n_classes)
        onehot_vote[vote] = 1
        return onehot_vote

    else:
        # Else, return the label vector where classes predicted over half the time remain
        try:
            preds = preds.numpy()
        except:
            pass
        n_classes = preds.shape[1]
        aggregated_preds = np.mean(preds, axis=0)
        if return_proba:
            return aggregated_preds
        onehot_vote = (aggregated_preds >= 0.5).astype(np.int32)
        return onehot_vote


def _aggregate_predictions(preds, clip_labels, multi_label=False, is_truth=False,
                           return_proba=False):
    '''
    Aggregate predictions from patch level to clip level.
    Pass is_truth=True if aggregating true labels to skip some computation
    Inputs
    ------
    preds : tf.Tensor or np.ndarray shape (n_preds, n_classes).
        Array of one-hot prediction vectors to concatenate
    clip_labels : np.ndarray, shape (n_preds). A vector indicating which clip each patch belongs to
    multi_label : bool, set to True if preds are multi-label
    is_truth : bool, set to True if preds are true labels. Skips some computation.
    return_proba : bool, if True returns probabilities instead of one-hot labels.

    Outputs
    -------
    aggregated_preds : np.ndarray, shape (n_clips) Aggregated predictions, one prediction per clip.
    '''
    n_clips = np.max(clip_labels)
    aggregated_preds = np.empty((n_clips, preds.shape[1]))
    if not is_truth:
        for i in range(n_clips):
            patches_to_aggregate = preds[np.where(clip_labels == i)[0]]
            vote = _majority_vote(preds=patches_to_aggregate,
                                  multi_label=multi_label,
                                  return_proba=return_proba)
            aggregated_preds[i] = vote
    else:
        for i in range(n_clips):
            if len(np.where(clip_labels == i)[0]) > 0:
                aggregated_preds[i] = preds[np.where(clip_labels == i)[0][0]]
            else:
                raise ValueError(
                    "One clip had no patches. \ Check your silence removal and feature extraction settings."
                    )
    return aggregated_preds

def compute_accuracy_score(y_true, y_pred, is_multilabel=False):
    """Wrapper function around sklearn.metrics.accuracy_score"""
    if not is_multilabel:
        y_true = np.argmax(y_true, axis=1)
        y_pred = np.argmax(y_pred, axis=1)

        return accuracy_score(y_true, y_pred)
    else:
        raise NotImplementedError("Not implemented yet for multi_label=True")


def evaluate_tflite_quantized_model(quantized_model_path: str = None, eval_ds: tf.data.Dataset = None,
                                    batch_size: int = None, class_names: list = None,
                                    output_dir: str = None, clip_labels: np.ndarray = None,
                                    multi_label: bool = None, name_ds: Optional[str] = 'test_set'):
    """
    Evaluates the accuracy of a quantized TensorFlow Lite model using tflite.interpreter and plots the confusion matrix.

    Args:
        quantized_model_path (str): The file path to the quantized TensorFlow Lite model.
        eval_ds (tf.data.Dataset): The test dataset to evaluate the model on.
        batch_size : int, batch size of eval_ds
        class_names (list): A list of class names for the confusion matrix.
        output_dir (str): The directory where to save the image.
        clip_labels : np.ndarray or None : Clip labels associated to the test dataset.
        multi_label : bool, set to True if eval_ds is a multi-label dataset.
        name_ds (str): The name of the chosen eval_ds to be mentioned in the prints and figures.
    Returns:
        patch_level_accuracy : float, patch-level accuracy of the provided model on eval_ds
        clip-level accuracy : float, clip-level accuracy of the provided model on eval_ds
    """
        
    tf.print(f'[INFO] : Evaluating the quantized model using {name_ds}...')
    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)

    input_details = interpreter_quant.get_input_details()[0]
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]
    input_index_quant = input_details["index"]
    # Get shape of a batch
    batch_shape = input_details["shape"]
    batch_shape[0] = batch_size
    interpreter_quant.resize_tensor_input(input_index_quant, batch_shape)

    tf.print(f"[INFO] Quantization input details : {input_details['quantization']}")
    tf.print(f"[INFO] Dtype input details : {input_details['dtype']}")

    interpreter_quant.allocate_tensors()
    batch_preds = []
    batch_labels = []
    for patches, labels in tqdm.tqdm(eval_ds, total=len(eval_ds)):
        # If the last batch does not have enough patches, resize tensor input one last time
        if len(patches) != batch_size:
            batch_shape[0] = len(patches)
            interpreter_quant.resize_tensor_input(input_index_quant, batch_shape)
            interpreter_quant.allocate_tensors()
        patches_processed = preprocess_input(patches, input_details)
        interpreter_quant.set_tensor(input_index_quant, patches_processed)
        interpreter_quant.invoke()
        test_pred_score = interpreter_quant.get_tensor(output_index_quant)
        batch_preds.append(test_pred_score)
        batch_labels.append(labels.numpy())

    patch_labels = np.concatenate(batch_labels, axis=0)
    preds = np.concatenate(batch_preds, axis=0)
    # Compute patch-level accuracy
    patch_level_accuracy = compute_accuracy_score(patch_labels,
                                                  preds,
                                                  is_multilabel=multi_label)

    # Compute clip-level accuracy
    # Aggregate clip-level labels
    aggregated_labels = _aggregate_predictions(preds=patch_labels,
                                               clip_labels=clip_labels,
                                               multi_label=multi_label,
                                               is_truth=True)
    aggregated_preds = _aggregate_predictions(preds=preds,
                                              clip_labels=clip_labels,
                                              multi_label=multi_label,
                                              is_truth=False)
    clip_level_accuracy = compute_accuracy_score(aggregated_labels,
                                                 aggregated_preds,
                                                 is_multilabel=multi_label)
    # Print metrics & log in MLFlow

    print(f"[INFO] : Patch-level Accuracy of quantized model = {round(patch_level_accuracy * 100, 2)}%")
    print(f"[INFO] : Clip-level Accuracy of quantized model = {round(clip_level_accuracy * 100, 2)}%")

    mlflow.log_metric(f"quant_patch_acc_{name_ds}", round(patch_level_accuracy * 100, 2))
    mlflow.log_metric(f"quant_clip_acc_{name_ds}", round(clip_level_accuracy * 100, 2))

    log_to_file(output_dir,  "\n" + "Quantized model :")
    log_to_file(output_dir, f"Patch-level accuracy of quantized model : {round(patch_level_accuracy * 100, 2)} %")
    log_to_file(output_dir, f"Clip-level accuracy of quantized model : {round(clip_level_accuracy * 100, 2)} %")
    # Compute and plot the confusion matrices

    if multi_label:     
        raise NotImplementedError("Multi-label inference not implemented yet")
        # patch_level_cms = compute_multilabel_confusion_matrices()
        # clip_level_cms = compute_multilabel_confusion_matrices()
        # plot_multilabel_confusion_matrices(patch_level_cms)
        # plot_multilabel_confusion_matrices(clip_level_cms)
    else:
        patch_level_cm = compute_confusion_matrix(patch_labels, preds)
        clip_level_cm = compute_confusion_matrix(aggregated_labels, aggregated_preds)

        patch_level_title = f"Quantized model patch-level confusion matrix \n \
                             On dataset : {name_ds} \n \
                             Quantized model patch-level accuracy : {patch_level_accuracy}"
        clip_level_title = f"Quantized model clip-level confusion matrix \n \
                             On dataset : {name_ds} \n \
                             Quantized model clip-level accuracy : {clip_level_accuracy}"
        plot_confusion_matrix(matrix=patch_level_cm,
                              class_names=class_names,
                              title=patch_level_title,
                              model_name=f"quant_model_patch_confusion_matrix_{name_ds}",
                              output_dir=output_dir)
        
        plot_confusion_matrix(matrix=clip_level_cm,
                              class_names=class_names,
                              title=clip_level_title,
                              model_name=f"quant_model_clip_confusion_matrix_{name_ds}",
                              output_dir=output_dir)

    return patch_level_accuracy, clip_level_accuracy


def evaluate_h5_model(model_path: str = None, eval_ds: tf.data.Dataset = None,
                      class_names: list = None, clip_labels: np.ndarray = None,
                      output_dir: str = None, name_ds: Optional[str] = 'test_set',
                      multi_label: bool = None):
    """
    Evaluates a trained Keras model saved in .h5 format on the provided dataset.

    Args:
        model_path (str): The file path to the .h5 model.
        eval_ds (tf.data.Dataset): Dataset to evaluate the model on.
        class_names (list): A list of class names for the confusion matrix.
        clip_labels : np.ndarray or None : Clip labels associated to the test dataset.
            If None, clip-level accuracy & confusion matrix are not computed.
        output_dir (str): The directory where to save the image.
        name_ds (str): The name of the chosen eval_ds to be mentioned in the prints and figures.
        multi_label : bool, set to True if eval_ds is a multi-label dataset.

    Returns:
        patch_level_accuracy : float, patch-level accuracy of the provided model on eval_ds
        clip-level accuracy : float or None, clip-level accuracy of the provided model on eval_ds
            Is None if clip_labels is None.
    """
    # Load the .h5 model
    model = tf.keras.models.load_model(model_path)
    loss = get_loss(multi_label=multi_label)
    model.compile(loss=loss, metrics=['accuracy'])

    # Evaluate the model on the test data
    tf.print(f'[INFO] : Evaluating the float model using {name_ds}...')
    preds = model.predict(eval_ds)

    # Compute loss
    patch_labels = np.concatenate([y for X, y in eval_ds])
    loss_value = loss(patch_labels, preds)

    # Convert preds to numpy
    # Not entirely sure it's needed
    try:
        preds = preds.numpy()
    except:
        pass

    # Compute patch-level accuracy
    patch_level_accuracy = compute_accuracy_score(patch_labels,
                                                  preds,
                                                  is_multilabel=multi_label)

    # Compute clip-level accuracy
    # Aggregate clip-level labels
    if clip_labels is not None:
        aggregated_labels = _aggregate_predictions(preds=patch_labels,
                                                clip_labels=clip_labels,
                                                multi_label=multi_label,
                                                is_truth=True)
        aggregated_preds = _aggregate_predictions(preds=preds,
                                                clip_labels=clip_labels,
                                                multi_label=multi_label,
                                                is_truth=False)
        clip_level_accuracy = compute_accuracy_score(aggregated_labels,
                                                    aggregated_preds,
                                                    is_multilabel=multi_label)
    # Print metrics & log in MLFlow

    print(f"[INFO] : Patch-level Accuracy of float model = {round(patch_level_accuracy * 100, 2)}%")

    if clip_labels is not None:
        print(f"[INFO] : Clip-level Accuracy of float model = {round(clip_level_accuracy * 100, 2)}%")
    print(f"[INFO] : Loss of float model = {loss_value}")

    mlflow.log_metric(f"float_patch_acc_{name_ds}", round(patch_level_accuracy * 100, 2))
    if clip_labels is not None:
        mlflow.log_metric(f"float_clip_acc_{name_ds}", round(clip_level_accuracy * 100, 2))
    mlflow.log_metric(f"float_loss_{name_ds}", loss_value)

    log_to_file(output_dir, "\n" + "Float model :")
    log_to_file(output_dir, f"Patch-level accuracy of float model : {round(patch_level_accuracy * 100, 2)} %")
    if clip_labels is not None:
        log_to_file(output_dir, f"Clip-level accuracy of float model : {round(clip_level_accuracy * 100, 2)} %")
    log_to_file(output_dir, f"Loss of float model : {loss_value} ")

    # Compute and plot the confusion matrices

    if multi_label:     
        raise NotImplementedError("Multi-label inference not implemented yet")
        # patch_level_cms = compute_multilabel_confusion_matrices()
        # clip_level_cms = compute_multilabel_confusion_matrices()
        # plot_multilabel_confusion_matrices(patch_level_cms)
        # plot_multilabel_confusion_matrices(clip_level_cms)
    else:
        patch_level_cm = compute_confusion_matrix(patch_labels, preds)

        patch_level_title = f"Float model patch-level confusion matrix \n \
                             On dataset : {name_ds} \n \
                             Float model patch-level accuracy : { patch_level_accuracy}"
        if clip_labels is not None:
            clip_level_cm = compute_confusion_matrix(aggregated_labels, aggregated_preds)
            clip_level_title = f"Float model clip-level confusion matrix \n \
                                On dataset : {name_ds} \n \
                                Float model clip-level accuracy : {clip_level_accuracy}"
        plot_confusion_matrix(matrix=patch_level_cm,
                              class_names=class_names,
                              title=patch_level_title,
                              model_name=f"float_model_patch_confusion_matrix_{name_ds}",
                              output_dir=output_dir)
        if clip_labels is not None:
            plot_confusion_matrix(matrix=clip_level_cm,
                                  class_names=class_names,
                                  title=clip_level_title,
                                  model_name=f"float_model_clip_confusion_matrix_{name_ds}",
                                  output_dir=output_dir)
    if clip_labels is not None:
        return patch_level_accuracy, clip_level_accuracy
    else:
        return patch_level_accuracy, None


def evaluate(cfg: DictConfig = None, eval_ds: tf.data.Dataset = None,
             clip_labels: np.ndarray = None, multi_label: bool = None, 
             model_path_to_evaluate: Optional[str] = None, 
             batch_size: int = None, name_ds: Optional[str] = 'test_set') -> None:
    """
    Evaluates and benchmarks a TensorFlow Lite or Keras model, and generates a Config header file if specified.

    Args:
        cfg (config): The configuration file.
        eval_ds (tf.data.Dataset): The dataset on which to evaluate.
        clip_labels : np.ndarray, Clip labels associated with eval_ds
        multi_label : bool, set to True if dataset is multi_label
        batch_size : int, batch size for evaluation of the quantized model.
        model_path_to_evaluate (str, optional): Model path to evaluate
        name_ds (str): The name of the chosen test_data to be mentioned in the prints and figures.

    Returns:
        None
    """
    output_dir = HydraConfig.get().runtime.output_dir
    class_names = cfg.dataset.class_names
    # Pre-process test dataset
    if model_path_to_evaluate:
        model_path = model_path_to_evaluate
    else:
        model_path = cfg.general.model_path
    try:
        file_extension = Path(model_path).suffix
        if file_extension == '.tflite':
            # Evaluate quantized TensorFlow Lite model
            evaluate_tflite_quantized_model(quantized_model_path=model_path,
                                            eval_ds=eval_ds,
                                            batch_size=batch_size,
                                            class_names=class_names,
                                            output_dir=output_dir,
                                            clip_labels=clip_labels,
                                            multi_label=multi_label,
                                            name_ds=name_ds)

        # Check if the model is a Keras model
        elif file_extension == '.h5':
            # Evaluate Keras model
            evaluate_h5_model(model_path=model_path,
                              eval_ds=eval_ds,
                              class_names=class_names,
                              clip_labels=clip_labels,
                              output_dir=output_dir,
                              name_ds=name_ds,
                              multi_label=multi_label)

    except Exception as e:
        raise ValueError(f"Model evaluation failed\n Received model path: {model_path}. Exception was {e}")
