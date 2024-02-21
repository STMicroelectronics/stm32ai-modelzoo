#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import os
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.metrics
import tensorflow as tf
from tensorflow.keras.models import Model
from PIL import Image


def plot_confusion_matrix(cm: np.ndarray = None, class_names: list = None, model_name: str = "f",
                          test_accuracy: float or str = "-",
                          output_dir: str = None) -> None:
    """
    Plots a confusion matrix using seaborn and saves it as an image.

    Args:
        cm (numpy.ndarray): The confusion matrix to plot.
        class_names (list): A list of class names.
        model_name (str): The name of the model.
        test_accuracy (float or str): The test accuracy, or "-" if not available.
        output_dir (str): The directory where to save the image.

    Returns:
        None
    """
    confusion_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    axis_labels = list(class_names)
    plt.figure(figsize=(12, 12))
    if len(class_names) > 20:
        sns.set(font_scale=0.5)
    sns.heatmap(confusion_normalized, xticklabels=axis_labels, yticklabels=axis_labels, cmap='Blues', annot=True,
                fmt='.2f', square=True)
    plt.title(f"{model_name} \nAccuracy: {test_accuracy}", fontsize=10)
    plt.tight_layout(pad=3)
    plt.ylabel("True Label", fontsize=10)
    plt.xlabel("Predicted Label", fontsize=10)
    plt.savefig(os.path.join(output_dir, f"{model_name}.png"))



def confusion_matrix(test_set: tf.data.Dataset = None, model: Model = None, class_names: List[str] = None,
                        output_dir: str = None, name_ds: Optional[str] = 'test_set') -> None:
    """
    Computes the confusion matrix and logs it as an image summary.

    Args:
        test_set (tf.data.Dataset): The test dataset to evaluate the model on.
        model (tf.keras.models.Model): The trained model to evaluate.
        class_names (List[str]): A list of class names.
        output_dir (str): The directory where to save the image.
        name_ds (str): The name of the chosen test_data to be mentioned in the prints and figures.
    Returns:
        None
    """
    test_pred = []
    test_labels = []
    for data in test_set:
        test_pred_score = model.predict_on_batch(data[0])
        if test_pred_score.shape[1] > 1:
            # Multi-label classification
            test_pred.append(np.argmax(test_pred_score, axis=1))
            test_labels.append(data[1])
        else:
            # Binary classification
            test_pred_score = np.where(test_pred_score < 0.5, 0, 1)
            test_pred.append(np.squeeze(test_pred_score))
            test_labels.append(data[1])

    labels = np.concatenate(test_labels, axis=0)
    labels = np.argmax(labels, axis=1)
    logits = np.concatenate(test_pred, axis=0)
    test_accuracy = round((np.sum(labels == logits) * 100) / len(labels), 2)

    # Calculate the confusion matrix.
    print(labels.shape, logits.shape)
    cm = sklearn.metrics.confusion_matrix(labels, logits)

    # Log the confusion matrix as an image summary.
    plot_confusion_matrix(cm=cm, class_names=class_names, model_name=f"float_model_confusion_matrix_{name_ds}",
                          test_accuracy=test_accuracy, output_dir=output_dir)


def vis_training_curves(history=None, output_dir: str = None) -> None:
    """
    Visualizes the training curves of the model.

    Args:
        history: The history object returned by the model.fit() method.
        output_dir (Optional[str]): The output directory to save the training curves plot.

    Returns:
        None
    """
    # Extract the accuracy and loss values for training and validation data
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs_range = range(len(acc))

    # Create dataframes for the training and validation data
    df_val = pd.DataFrame({'run': 'validation', 'step': epochs_range, 'epoch_accuracy': val_acc, 'epoch_loss': val_loss})
    df_train = pd.DataFrame({'run': 'train', 'step': epochs_range, 'epoch_accuracy': acc, 'epoch_loss': loss})

    # Concatenate the dataframes
    frames = [df_val, df_train]
    df = pd.concat(frames)
    df = df.reset_index()

    # Plot the training curves
    plt.figure(figsize=(16, 6))
    plt.suptitle('Training curves', fontsize=16)
    plt.subplot(1, 2, 1)
    sns.lineplot(data=df, x="step", y="epoch_accuracy", hue="run").set_title("accuracy")
    plt.grid()
    plt.subplot(1, 2, 2)
    sns.lineplot(data=df, x="step", y="epoch_loss", hue="run").set_title("loss")
    plt.grid()
    plt.savefig(os.path.join(output_dir, 'Training_curves.png'))


def display_figures(cfg: Dict = None):
    """
    Displays all the figures created during the execution of current run stored in output_dir.
    """
    if cfg.general.display_figures:
        # Get a list of all the PNG files in it and display it
        png_files = [f for f in os.listdir(cfg.output_dir) if f.endswith('.png')]
        for png_file in png_files:
            img = Image.open(os.path.join(cfg.output_dir, png_file))
            img.show()
