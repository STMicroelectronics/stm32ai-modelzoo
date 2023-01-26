# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import itertools
import os

import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.metrics
from hydra.core.hydra_config import HydraConfig


def plot_confusion_matrix(cm, class_names, model_name='f', test_accuracy='-'):
    '''
    Returns a matplotlib figure containing the plotted confusion matrix.

    Args:
    cm (array, shape = [n, n]): a confusion matrix of integer classes
    class_names (array, shape = [n]): String names of the integer classes
    '''
    # Compute the labels from the normalized confusion matrix.
    labels = np.around(cm.astype('float') / cm.sum(axis=1)[:, np.newaxis], decimals=2)
    plt.figure(figsize=(6, 6))
    plt.imshow(labels, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(f'Model_accuracy : {test_accuracy}')
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)
    # Use white text if squares are dark; otherwise black.
    threshold = labels.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        color = 'white' if labels[i, j] > threshold else 'black'
        plt.text(j, i, labels[i, j], horizontalalignment='center', color=color)

    plt.tight_layout(pad=3)
    plt.ylabel('True label', fontsize=12)
    plt.xlabel('Predicted label', fontsize=12)
    plt.savefig(os.path.join(HydraConfig.get().runtime.output_dir, f'{model_name}.png'), dpi=1200)
    plt.show()


def training_confusion_matrix(testset, model, class_names, model_name='f', test_accuracy='-'):

    # Use the model to predict the values from the validation dataset.
    test_pred = []
    test_labels = []
    list_data = list(testset)
    for data in list_data:
        test_pred_score = model.predict_on_batch(data[0])
        test_pred.append(np.argmax(test_pred_score, axis=1))
        test_labels.append(np.argmax(data[1], axis=1))
    labels = np.concatenate(test_labels, axis=0)
    logits = np.concatenate(test_pred, axis=0)
    test_accuracy = round((np.sum(labels == logits) * 100) / len(labels), 2)
    print('[INFO] : Test Accuracy = {} %'.format(test_accuracy))
    mlflow.log_metric('float_test_acc', test_accuracy)
    # Calculate the confusion matrix.
    cm = sklearn.metrics.confusion_matrix(labels, logits)
    # Log the confusion matrix as an image summary.
    plot_confusion_matrix(cm, class_names=class_names, model_name='float_model_confusion_matrix', test_accuracy=test_accuracy)
