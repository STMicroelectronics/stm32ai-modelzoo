# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np
import tensorflow as tf
import numpy.random as rnd
from sklearn.metrics import accuracy_score

def _majority_vote(preds, is_multilabel=False):
    '''Concatenates several prediction labels into one, according to majority vote'''

    if not is_multilabel:
        # If we only have one label per sample, pick the one with the most votes
        try:
            preds = preds.numpy()
        except:
            pass
        n_classes = preds.shape[1]
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
        onehot_vote = (aggregated_preds >= 0.5).astype(np.int32)
        return onehot_vote


def _aggregate_predictions(preds, clip_labels, is_multilabel=False, is_truth=False):
    '''Aggregate predictions from patch level to clip level.
       Pass is_truth=True if aggregating true labels to skip some computation'''
    n_clips = np.max(clip_labels)
    aggregated_preds = np.empty((n_clips, preds.shape[1]))
    if not is_truth:
        for i in range(n_clips):
            patches_to_aggregate = preds[np.where(clip_labels == i)[0]]
            vote = _majority_vote(preds=patches_to_aggregate, is_multilabel=is_multilabel)
            aggregated_preds[i] = vote
    else:
        for i in range(n_clips):
            if len(np.where(clip_labels == i)[0]) > 0:
                aggregated_preds[i] = preds[np.where(clip_labels == i)[0][0]]
            else:
                raise ValueError(
                    "One clip had no patches. Check your silence removal and feature extraction settings."
                    )
    return aggregated_preds

def compute_accuracy_score(y_true, y_pred, is_multilabel=False):
    if not is_multilabel:
        y_true = np.argmax(y_true, axis=1)
        y_pred = np.argmax(y_pred, axis=1)

        return accuracy_score(y_true, y_pred)
    else:
        raise NotImplementedError("TODO : implement accuracy calculation for multilabel case")
