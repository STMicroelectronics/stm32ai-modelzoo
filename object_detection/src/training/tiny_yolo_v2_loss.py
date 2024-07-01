# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import sys
import math
import tensorflow as tf
from tensorflow.keras import backend as K
from tiny_yolo_v2_postprocess import tiny_yolo_v2_decode


def box_iou(b1, b2, expand_dims=True):
    """
    Return IOU tensor.

    Args:
        b1 (tensor): Tensor representing the first bounding box with shape (i1,...,iN, 4).
        b2 (tensor): Tensor representing the second bounding box with shape (j, 4).
        expand_dims (bool, default=True): If True, expand dimensions to apply broadcasting.
    Returns:
        iou (tensor): Tensor representing the IOU between the two bounding boxes with shape (i1,...,iN, j).
    """
    if expand_dims:
        # Expand dim to apply broadcasting.
        b1 = K.expand_dims(b1, -2)

    b1_xy = b1[..., :2]
    b1_wh = b1[..., 2:4]
    b1_wh_half = b1_wh/2.
    b1_mins = b1_xy - b1_wh_half
    b1_maxes = b1_xy + b1_wh_half

    # Expand dim to apply broadcasting.
    b2 = K.expand_dims(b2, 0)
    b2_xy = b2[..., :2]
    b2_wh = b2[..., 2:4]
    b2_wh_half = b2_wh/2.
    b2_mins = b2_xy - b2_wh_half
    b2_maxes = b2_xy + b2_wh_half

    intersect_mins = K.maximum(b1_mins, b2_mins)
    intersect_maxes = K.minimum(b1_maxes, b2_maxes)
    intersect_wh = K.maximum(intersect_maxes - intersect_mins, 0.)
    intersect_area = intersect_wh[..., 0] * intersect_wh[..., 1]
    b1_area = b1_wh[..., 0] * b1_wh[..., 1]
    b2_area = b2_wh[..., 0] * b2_wh[..., 1]
    iou = intersect_area / (b1_area + b2_area - intersect_area)

    return iou

def tiny_yolo_v2_loss(args, anchors, num_classes,network_stride):
    """
    YOLOv2 loss function.

    Args:
        args (tuple): A tuple containing the model output and ground truth.
        anchors (tensor): Anchor boxes for the model.
        num_classes (int): Number of object classes.
    Returns:
        total_loss (float): Total mean YOLOv2 loss across minibatch.
    """
    (yolo_output, y_true) = args
    num_anchors = len(anchors)
    scale_x_y = None
    yolo_output_shape = K.shape(yolo_output)
    input_shape = K.cast(yolo_output_shape[1:3] * network_stride, K.dtype(y_true))
    grid_shape = K.cast(yolo_output_shape[1:3], K.dtype(y_true))
    batch_size_f = K.cast(yolo_output_shape[0], K.dtype(yolo_output))
    object_scale = 5
    no_object_scale = 1
    class_scale = 1
    location_scale = 1

    grid, raw_pred, pred_xy, pred_wh = tiny_yolo_v2_decode(yolo_output, anchors, num_classes, input_shape, calc_loss=True)
    pred_confidence = K.sigmoid(raw_pred[..., 4:5])
    pred_class_prob = K.softmax(raw_pred[..., 5:])

    object_mask = y_true[..., 4:5]

    pred_box = K.concatenate([pred_xy, pred_wh])
    pred_box = K.expand_dims(pred_box, 4)

    raw_true_box = y_true[...,0:4]
    raw_true_box = K.expand_dims(raw_true_box, 4)

    iou_scores = box_iou(pred_box, raw_true_box, expand_dims=False)
    iou_scores = K.squeeze(iou_scores, axis=0)

    # Best IOUs for each location.
    best_ious = K.max(iou_scores, axis=4)  # Best IOU scores.
    best_ious = K.expand_dims(best_ious)

    # A detector has found an object if IOU > thresh for some true box.
    object_detections = K.cast(best_ious > 0.6, K.dtype(best_ious))

    no_object_weights = (no_object_scale * (1 - object_detections) * (1 - object_mask))
    no_objects_loss = no_object_weights * K.square(-pred_confidence)

    
    objects_loss = (object_scale * object_mask * K.square(1 - pred_confidence))
    confidence_loss = objects_loss + no_objects_loss

    matching_classes = K.cast(y_true[..., 5], 'int32')
    matching_classes = K.one_hot(matching_classes, num_classes)

    classification_loss = (class_scale * object_mask * K.square(matching_classes - pred_class_prob))

    trans_true_boxes = y_true[..., 0:4]

    trans_pred_boxes = K.concatenate((K.sigmoid(raw_pred[..., 0:2]), raw_pred[..., 2:4]), axis=-1)

    location_loss = (location_scale * object_mask *
                        K.square(trans_true_boxes - trans_pred_boxes))


    confidence_loss_sum = K.sum(confidence_loss) / batch_size_f
    location_loss_sum = K.sum(location_loss) / batch_size_f

    if num_classes == 1:
        classification_loss_sum = K.constant(0)
    else:
        classification_loss_sum = K.sum(classification_loss) / batch_size_f

    total_loss = 0.5 * (confidence_loss_sum + classification_loss_sum + location_loss_sum)

    total_loss = K.expand_dims(total_loss, axis=-1)

    return total_loss, location_loss_sum, confidence_loss_sum, classification_loss_sum