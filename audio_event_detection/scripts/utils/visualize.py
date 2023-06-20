# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import normalize
import itertools
from hydra.core.hydra_config import HydraConfig
import os
import pandas as pd
import seaborn as sns
import mlflow

def vis_training_curves(history,cfg):

    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(len(acc))

    df_val = pd.DataFrame({'run': 'validation', 'step': epochs_range, 'epoch_accuracy': val_acc, 'epoch_loss': val_loss})
    df_train = pd.DataFrame({'run': 'train', 'step': epochs_range, 'epoch_accuracy': acc, 'epoch_loss': loss})

    frames = [df_val, df_train]

    df = pd.concat(frames)
    df = df.reset_index()

    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    sns.lineplot(data=df, x="step", y="epoch_accuracy",
                 hue="run").set_title("accuracy")
    plt.subplot(1, 2, 2)
    sns.lineplot(data=df, x="step", y="epoch_loss",
                 hue="run").set_title("loss")
    plt.savefig(os.path.join(HydraConfig.get().runtime.output_dir,'Training_curves.png'))
    plt.show()


def _compute_confusion_matrix(y_true, y_pred, is_multilabel=False):
    if not is_multilabel:
        # Convert one-hot vectors to integer
        y_pred = np.argmax(y_pred, axis=1)
        y_true = np.argmax(y_true, axis=1)

        matrix = confusion_matrix(y_true, y_pred)
    else:
        raise NotImplementedError("TODO : implement multilabel confusion matrices")

    return matrix

def _plot_confusion_matrix(matrix, class_names, title, model_name="f",
                           test_accuracy='-', is_multilabel=False):
    
    # Order class_names alphabetically as that is what is used by the string lookup layers
    # used to get the one hot encodings
    class_names = sorted(class_names)
    if not is_multilabel:
        plt.figure(figsize=(14, 14))
        if len(class_names) > 20:
            sns.set(font_scale=0.5)
        confusion_normalized = normalize(matrix, axis=1, norm='l1')
        # confusion_normalized = [element / sum(row) for element, row in zip([row for row in cm], cm)]
        sns.heatmap(confusion_normalized, xticklabels=class_names, yticklabels=class_names, cmap='Blues', annot=True, fmt='.2f', square=True)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel("True label", fontsize=8)
        plt.xlabel("Predicted label", fontsize=10)
        plt.title(title + "\n Model_accuracy : {}".format(test_accuracy), fontsize=12)
        plt.savefig(os.path.join(HydraConfig.get().runtime.output_dir, '{}.png'.format(title)))
        plt.show()
        
    else:
        raise NotImplementedError("TODO : Implement confusion matrices for multilabel case")
