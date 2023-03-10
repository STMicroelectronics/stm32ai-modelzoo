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
import mlflow
import numpy as np
import seaborn as sns
import sklearn.metrics
from hydra.core.hydra_config import HydraConfig


def plot_confusion_matrix(cm, class_names, model_name="f", test_accuracy="-"):
    """ Returns a matplotlib figure containing the plotted confusion matrix. """

    confusion_normalized = [element / sum(row) for element, row in zip([row for row in cm], cm)]
    axis_labels = list(class_names)
    plt.figure(figsize=(12, 12))
    if len(class_names) > 20:
        sns.set(font_scale=0.5)
    sns.heatmap(confusion_normalized, xticklabels=axis_labels, yticklabels=axis_labels, cmap='Blues', annot=True,
                fmt='.2f', square=True)
    plt.title("Model_accuracy : {}".format(test_accuracy), fontsize=10)
    plt.tight_layout(pad=3)
    plt.ylabel("True label", fontsize=10)
    plt.xlabel("Predicted label", fontsize=10)
    plt.savefig(os.path.join(HydraConfig.get().runtime.output_dir, '{}.png'.format(model_name)))
    plt.show()


def training_confusion_matrix(testset, model, class_names, test_accuracy="-"):
    # Use the model to predict the values from the validation dataset.
    test_pred = []
    test_labels = []
    list_data = list(testset)
    for data in list_data:
        test_pred_score = model.predict_on_batch(data[0])
        if test_pred_score.shape[1] > 1:
            # Multi-lables classification
            test_pred.append(np.argmax(test_pred_score, axis=1))
            test_labels.append(np.argmax(data[1], axis=1))
        else:
            # Binary classification
            test_pred_score = np.where(test_pred_score < 0.5, 0, 1)
            test_pred.append(np.squeeze(test_pred_score))
            #test_labels.append(data[1])
            test_labels.append(np.squeeze(data[1]))

    labels = np.concatenate(test_labels, axis=0)
    logits = np.concatenate(test_pred, axis=0)
    test_accuracy = round((np.sum(labels == logits) * 100) / len(labels), 2)
    print("[INFO] : Test Accuracy = {} %".format(test_accuracy))
    mlflow.log_metric("float_test_acc", test_accuracy)
    # Calculate the confusion matrix.
    cm = sklearn.metrics.confusion_matrix(labels, logits)
    # Log the confusion matrix as an image summary.
    plot_confusion_matrix(cm, class_names=class_names, model_name="float_model_confusion_matrix",
                          test_accuracy=test_accuracy)
