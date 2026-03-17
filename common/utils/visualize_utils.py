# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from hydra.core.hydra_config import HydraConfig
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.metrics import confusion_matrix
from PIL import Image
from typing import Dict


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
    df_val = pd.DataFrame(
        {'run': 'validation', 'step': epochs_range, 'epoch_accuracy': val_acc, 'epoch_loss': val_loss})
    df_train = pd.DataFrame({'run': 'train', 'step': epochs_range, 'epoch_accuracy': acc, 'epoch_loss': loss})

    # Concatenate the dataframes
    frames = [df_val, df_train]
    df = pd.concat(frames)
    df = df.reset_index()

    # Plot the training curves
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    sns.lineplot(data=df, x="step", y="epoch_accuracy", hue="run").set_title("accuracy")
    plt.grid()
    plt.subplot(1, 2, 2)
    sns.lineplot(data=df, x="step", y="epoch_loss", hue="run").set_title("loss")
    plt.grid()
    plt.savefig(os.path.join(output_dir, 'Training_curves.png'))
    

def plot_confusion_matrix(cm: np.ndarray = None,
                          class_names: list = None,
                          title: str = "f",
                          model_name: str = "f",
                          output_dir: str = None) -> None:
    """
    Plots a confusion matrix using seaborn and saves it as an image.

    Args:
        cm (numpy.ndarray): The confusion matrix to plot.
        class_names (list): A list of class names.title : str,  Pre-pended to model test accuracy in the figure title
        model_name (str): The name of the model.
        output_dir (str): The directory where to save the image.

    Returns:
        None
    """
    plt.figure(figsize=(14, 14))
    confusion_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    axis_labels = list(class_names)
    if len(class_names) > 20:
        sns.set(font_scale=0.5)
        plt.xticks(rotation=45, ha='right')
    sns.heatmap(confusion_normalized, xticklabels=axis_labels, yticklabels=axis_labels, cmap='Blues',
                annot=True, fmt='.2f', square=True)
    plt.title(title, fontsize=10)
    plt.tight_layout(pad=3)
    plt.ylabel("True Label", fontsize=10)
    plt.xlabel("Predicted Label", fontsize=10)
    plt.savefig(os.path.join(output_dir, f"{model_name}.png"))

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

def compute_confusion_matrix2(y_true, y_pred):
    '''Computes a confusion matrix for multiclass monolabel classification
       Takes one-hot encoded labels and predictions as input.
       Inputs
       ------
       y_true : np.ndarray, (n_samples, n_classes) True labels. Must be one-hot encoded labels
       y_pred : np.ndarray, (n_samples, n_classes) Predicted labels. Must be one-hot encoded labels.
       
       Outputs
       -------
       matrix : ndarray, (n_classes, n_classes) : Confusion matrix'''
    # Convert one-hot vectors to integer
    y_pred = np.argmax(y_pred, axis=1)
    y_true = np.argmax(y_true, axis=1)

    matrix = confusion_matrix(y_true, y_pred)

    return matrix

def compute_multilabel_confusion_matrices():
    """
    Compute confusion matrices for multilabel inference.
    Outputs 1 2x2 matrix per class.
    """
    print("this feature is not available yet!")
    pass

def plot_multilabel_confusion_matrices():
    """Plots confusion matrices for multilabel inference.
    Plots 1 2x2 matrix per class."""
    print("this feature is not available yet!")
    pass

