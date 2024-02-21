# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
import tensorflow.keras.backend as K


def focal_loss(y_true: tf.Tensor, y_pred: tf.Tensor, alpha: float = 0.25, gamma: float = 2) -> tf.Tensor:
    """
    Calculate the focal loss

    Args:
        y_true: Ground truth targets, tensor of shape of (?, #boxes, 1+n_classes)
        y_pred: Predicted logits, tensor of shape of (?, #boxes, 1+n_classes)
        alpha: Focal loss weight for positive samples, a scalar number
        gamma: Focal loss focusing parameter, a scalar number

    Returns:
        focal_loss: Focal loss, tensor of shape (?, #boxes)
    """

    # Normalize the predicted logits
    y_pred /= K.sum(y_pred, axis=-1, keepdims=True)

    # Clip the predicted logits to avoid numerical instability
    epsilon = K.epsilon()
    y_pred = K.clip(y_pred, epsilon, 1. - epsilon)

    # Compute the cross-entropy loss
    cross_entropy = -y_true * K.log(y_pred)

    # Compute the focal loss
    loss = alpha * K.pow(1 - y_pred, gamma) * cross_entropy

    # Sum the focal loss across all boxes
    return K.sum(loss, axis=-1)


def smooth_l1_loss(y_true: tf.Tensor, y_pred: tf.Tensor, sigma: float = 0.5) -> tf.Tensor:
    """
    Compute smooth L1 loss.

    Arguments:
        y_true: ground truth bounding boxes, tensor of shape (?, #boxes, 4)
        y_pred: predicted bounding boxes, tensor of shape (?, #boxes, 4)
        sigma: smooth weight, a scalar number

    Returns:
        l1_loss: smoothed L1 loss, tensor of shape (?, #boxes)
    """

    # Compute absolute difference between ground truth and predicted bounding boxes
    absolute_loss = tf.abs(y_true - y_pred)

    # Compute square loss
    square_loss = 0.5 * (sigma * (y_true - y_pred)) ** 2

    # Compute L1 loss using smooth L1 function
    l1_loss = tf.where(tf.less(absolute_loss, 1.0 / sigma ** 2),
                       square_loss, absolute_loss - 0.5 / sigma ** 2)

    # Sum the L1 loss across all boxes
    return tf.reduce_sum(l1_loss, axis=-1)


def ssd_focal_loss(alpha_loc_class: float = 1.0, alpha_fl: float = 1.0,
                   gamma_fl: float = 0.25, sigma_l1: float = 0.5) -> tf.Tensor:
    """
    Computes the SSD Focal Loss for object detection, which is a combination of Focal Loss and Smooth L1 Loss.

    Args:
        alpha_loc_class (float): Weighting factor for the localization loss.
        alpha_fl (float): Weighting factor for the focal loss.
        gamma_fl (float): Focusing parameter for the focal loss.
        sigma_l1 (float): Smoothing parameter for the smooth L1 loss.

    Returns:
        A tensor representing the total loss.

    """

    def _loss(y_true: tf.Tensor, y_pred: tf.Tensor, alpha_loc_class: float = alpha_loc_class,
              alpha_fl: float = alpha_fl, gamma_fl: float = gamma_fl, sigma_l1: float = sigma_l1) -> tf.Tensor:
        """
        Computes the SSD Focal Loss for a single batch of predictions.

        Args:
            y_true (tf.Tensor): The true labels for the batch.
            y_pred (tf.Tensor): The predicted labels for the batch.
            alpha_loc_class (float): Weighting factor for the localization loss.
            alpha_fl (float): Weighting factor for the focal loss.
            gamma_fl (float): Focusing parameter for the focal loss.
            sigma_l1 (float): Smoothing parameter for the smooth L1 loss.

        Returns:
            A tensor representing the total loss for the batch.

        """

        # Convert alpha_loc_class to a TensorFlow constant
        alpha_loc_class = tf.constant(alpha_loc_class)

        # Get the batch size and number of boxes from the shape of y_pred
        batch_size = tf.shape(y_pred)[0]
        n_boxes = tf.shape(y_pred)[1]

        # Compute the focal loss for the classification task
        classification_loss = tf.cast(focal_loss(
            y_true[:, :, :-8], y_pred[:, :, :-8], alpha=alpha_fl, gamma=gamma_fl), dtype=tf.float32)

        # Compute the smooth L1 loss for the localization task
        localization_loss = tf.cast(smooth_l1_loss(
            y_true[:, :, -8:-4], y_pred[:, :, -8:-4], sigma=sigma_l1), dtype=tf.float32)

        # Compute the class loss as the sum of the focal loss over all classes
        class_loss = tf.reduce_sum(classification_loss, axis=-1)

        # Compute the positives tensor as the maximum value of y_true over all classes except the background class
        positives = tf.cast(tf.reduce_max(
            y_true[:, :, 1:-8], axis=-1), dtype=tf.float32)

        # Compute the number of positive examples in the batch
        n_positive = tf.reduce_sum(positives)

        # Compute the localization loss as the sum of the smooth L1 loss over all positive examples
        loc_loss = tf.reduce_sum(localization_loss * positives, axis=-1)

        # Compute the total loss as a weighted sum of the class loss and localization loss
        total_loss = (class_loss + alpha_loc_class * loc_loss) / \
                     tf.maximum(1.0, n_positive)

        # Scale the total loss by the batch size
        total_loss = total_loss * tf.cast(batch_size, dtype=tf.float32)

        return total_loss

    return _loss
