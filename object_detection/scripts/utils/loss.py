# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
import tensorflow.keras.backend as K


def focal_loss(y_true, y_pred, alpha=0.25, gamma=2):
    '''
    Calculate the focal loss

    Arguments:
        y_true: ground truth targets, tensor of shape of (?, #boxes, 1+n_classes)
        y_pred: predicted logits, tensor of shape of (?, #boxes, 1+n_classes)
        alpha:
        gamma:

    Returns:
        focal_loss: focal loss, tensor of shape (?, #boxes)
    '''

    y_pred /= K.sum(y_pred, axis=-1, keepdims=True)

    epsilon = K.epsilon()
    y_pred = K.clip(y_pred, epsilon, 1. - epsilon)

    cross_entropy = -y_true * K.log(y_pred)

    loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy

    return K.sum(loss, axis=-1)


def smooth_L1_loss(y_true, y_pred, sigma=0.5):
    '''
    Compute smooth L1 loss.

    Arguments:
        y_true: ground truth bounding boxes, tensor of shape (?, #boxes, 4)
        y_pred: predicted bounding boxes, tensor of shape (?, #boxes, 4)
        sigma: smooth weight, a scalar number

    Returns:
        l1_loss: smoothed L1 loss, tensor of shape (?, #boxes)
    '''
    absolute_loss = tf.abs(y_true - y_pred)
    square_loss = 0.5 * (sigma * (y_true - y_pred))**2
    l1_loss = tf.where(tf.less(absolute_loss, 1.0 / sigma**2),
                       square_loss, absolute_loss - 0.5 / sigma**2)
    return tf.reduce_sum(l1_loss, axis=-1)


def ssd_focal_loss(alpha_loc_class=1.0, alpha_fl=1.0,
                   gamma_fl=0.25, sigma_l1=0.5):

    def _loss(y_true, y_pred, alpha_loc_class=alpha_loc_class,
              alpha_fl=alpha_fl, gamma_fl=gamma_fl, sigma_l1=sigma_l1):
        alpha_loc_class = tf.constant(alpha_loc_class)
        batch_size = tf.shape(y_pred)[0]
        n_boxes = tf.shape(y_pred)[1]

        classification_loss = tf.cast(focal_loss(
            y_true[:, :, :-8], y_pred[:, :, :-8], alpha=alpha_fl, gamma=gamma_fl), dtype=tf.float32)
        localization_loss = tf.cast(smooth_L1_loss(
            y_true[:, :, -8:-4], y_pred[:, :, -8:-4], sigma=sigma_l1), dtype=tf.float32)

        class_loss = tf.reduce_sum(classification_loss, axis=-1)

        positives = tf.cast(tf.reduce_max(
            y_true[:, :, 1:-8], axis=-1), dtype=tf.float32)

        n_positive = tf.reduce_sum(positives)
        loc_loss = tf.reduce_sum(localization_loss * positives, axis=-1)

        total_loss = (class_loss + alpha_loc_class * loc_loss) / \
            tf.maximum(1.0, n_positive)

        total_loss = total_loss * tf.cast(batch_size, dtype=tf.float32)

        return total_loss

    return _loss
