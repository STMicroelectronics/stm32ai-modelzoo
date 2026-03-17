# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np
import tensorflow as tf
from object_detection.tf.src.postprocessing import yolo_head


def get_detector_mask(boxes, anchors, image_size, network_stride):
    """
    This function generates a detector mask that indicates where
    GT boxes should appear in the network output. Adjusted boxes
    are also generated. This data is used to calculate the loss.
    
    WARNING: In its current implementation, this function 
    does not support multiple strides and their associated 
    sets of anchors. Only one set is supported.
    
    Inputs:
        boxes
            GT boxes and classes in (x, y, w, h, class) format
            with x, y, w and h in [0, 1]
            Shape: [batch_size, num_gt, 5]
        anchors
            List of the anchors
            Shape: [num_anchors, 2]
        image_width, image_height
            Image dimensions
    
    Outputs:
        detector_mask
            Set to 1 at indices in the network output where a GT box
            intersects with one or several anchors. Set to 0 otherwise.
            Shape:
                [batch_size, conv_height, conv_width, num_anchors, 1]
                 conv_height and conv_width are the numbers of 
                 columns and rows of the Yolo image grid.
        matching_true_boxes
            Adjusted GT box for comparison with predicted parameters 
            at training time. Used only where the detector mask
            is set to 1. Box format is (x, y, w, h, class).
            Shape:
                [batch_size, conv_height, conv_width, num_anchors, 5]
    
    The indices [i, j, k] of GT boxes in the network output are determined
    as follows:
    - i and j are calculated based on (x, y) coordinates of boxes.
    - The IOUs of each box with all the anchors are calculated. If one or 
      several IOUs are positive, k is the index in the input list of anchors
      that has the largest IOU with the box.
      If all IOUs are equal to 0, either the box does not intersect with
      any anchor or it is a dummy box used for padding (all 4 coordinates
      set to 0). In this case the mask is set to 0
    """

    num_anchors = tf.shape(anchors)[0]
    batch_size = tf.shape(boxes)[0]
    num_boxes = tf.shape(boxes)[1]

    conv_width = image_size[0] // network_stride
    conv_height = image_size[1] // network_stride
    
    box_classes = boxes[..., 4]
        
    # Scale boxes to convolutional feature spatial dimensions
    boxes = boxes[..., :4] * tf.convert_to_tensor(
                [conv_width, conv_height, conv_width, conv_height], dtype=tf.float32)    
    
    i = tf.math.floor(boxes[..., 1])
    i = tf.cast(i, tf.int32)
    j = tf.math.floor(boxes[..., 0])
    j = tf.cast(j, tf.int32)

    # Replicate boxes and anchors in such a way that all the IOUs
    # can be calculated at once in an element wise kind of way
    tiled_boxes = tf.repeat(boxes[..., 2:4], [num_anchors], axis=1)    
    tiled_boxes = tf.reshape(tiled_boxes, [batch_size, num_boxes, num_anchors, 2]) 
    
    tiled_anchors = tf.tile(anchors, [batch_size * num_boxes, 1])
    tiled_anchors = tf.reshape(tiled_anchors, [batch_size, num_boxes, num_anchors, 2])    

    tiled_boxes_max = tiled_boxes / 2
    tiled_boxes_min = -tiled_boxes_max

    tiled_anchors_max = tiled_anchors / 2.
    tiled_anchors_min = -tiled_anchors_max
    
    intersect_max = tf.minimum(tiled_boxes_max, tiled_anchors_max)
    intersect_min = tf.maximum(tiled_boxes_min, tiled_anchors_min)
    intersect_wh = tf.maximum(intersect_max - intersect_min, 0.)
    intersect_area = tf.math.reduce_prod(intersect_wh, axis=-1)
    
    tiled_boxes_area = tf.math.reduce_prod(tiled_boxes, axis=-1)
    tiled_anchors_area = tf.math.reduce_prod(tiled_anchors, axis=-1)

    # Calculate the IOUs between boxes and anchors
    iou = intersect_area / (tiled_boxes_area + tiled_anchors_area - intersect_area)
    best_iou = tf.math.reduce_max(iou, axis=-1)

    # Find the anchors that have the largest IOUs
    k = tf.math.argmax(iou, axis=-1)
    k = tf.cast(k, tf.int32)
    
    x = tf.reshape(k, [batch_size * num_boxes, 1])    
    best_anchors = tf.gather_nd(anchors, x)
    best_anchors = tf.reshape(best_anchors, [batch_size, num_boxes, 2])
    
    # Add the batch item index n to have the [n, i, j, k] indices of boxes
    # in the detector_mask and matching_true_boxes output tensors
    n = tf.range(batch_size, dtype=tf.int32)
    n = tf.repeat(n, num_boxes, axis=0)
    n = tf.reshape(n, [batch_size, num_boxes])

    detector_indices = tf.stack([n, i, j, k], axis=-1)

    # Find the boxes that have a positive IOU with anchors
    # Get the indices of these boxes in the detector_mask
    # and matching_true_boxes output tensors
    positive_iou = tf.math.greater(best_iou, 0)
    positive_iou = tf.reshape(positive_iou, [batch_size, num_boxes])
    setting_indices = tf.gather_nd(detector_indices, tf.where(positive_iou))

    # Create and set the detector mask
    detector_mask = tf.zeros(
            [batch_size, conv_height, conv_width, num_anchors], dtype=tf.float32)
    num_settings = tf.shape(setting_indices)[0]
    settings = tf.ones([num_settings], dtype=tf.float32)
    detector_mask = tf.tensor_scatter_nd_update(detector_mask, setting_indices, settings)
    detector_mask = tf.expand_dims(detector_mask, axis=-1)

    # Calculate the adjusted boxes. Filter the adjusted boxes
    # of boxes that have a zero IOU with anchors.
    i = tf.cast(i, tf.float32)
    j = tf.cast(j, tf.float32)
    adjusted_boxes = tf.stack([
                boxes[..., 0] - j,
                boxes[..., 1] - i,
                tf.math.log(boxes[..., 2] / best_anchors[..., 0]),
                tf.math.log(boxes[..., 3] / best_anchors[..., 1]),
                box_classes],
                axis=-1)
    adjusted_boxes = tf.gather_nd(adjusted_boxes, tf.where(positive_iou))
        
    # Create and set the matching_true_boxes output tensor
    matching_true_boxes = tf.zeros(
            [batch_size, conv_height, conv_width, num_anchors, 5], dtype=tf.float32)
    matching_true_boxes = tf.tensor_scatter_nd_update(matching_true_boxes, setting_indices, adjusted_boxes)    

    return detector_mask, matching_true_boxes


def yolo_loss(anchors, num_classes, pred, image_labels, detectors_mask, matching_true_boxes, image_size):
    """YOLO localization loss function.

    Parameters
    ----------
    yolo_output : tensor
        Final convolutional layer features.

    true_boxes : tensor
        Ground truth boxes tensor with shape [batch, num_true_boxes, 5]
        containing box x_center, y_center, width, height, and class.

    detectors_mask : array
        0/1 mask for detector positions where there is a matching ground truth.

    matching_true_boxes : array
        Corresponding ground truth boxes for positive detector positions.
        Already adjusted for conv height and width.

    anchors : tensor
        Anchor boxes for model.

    num_classes : int
        Number of object classes.

    Returns
    -------
    mean_loss : float
        mean localization loss across minibatch
    """

    (yolo_output, true_boxes, detectors_mask, matching_true_boxes, image_size) = \
                      pred,image_labels, detectors_mask, matching_true_boxes, image_size
                      
    num_anchors = len(anchors)
    object_scale = 5
    no_object_scale = 1
    class_scale = 1
    coordinates_scale = 1

    pred_xy, pred_wh, pred_confidence, pred_class_prob = yolo_head(yolo_output, anchors, num_classes)
              
    yolo_output_shape = tf.shape(yolo_output)
    feats = tf.reshape(yolo_output, [
        -1, yolo_output_shape[1], yolo_output_shape[2], num_anchors,
        num_classes + 5
    ])
    pred_boxes = tf.concat(
        [tf.math.sigmoid(feats[..., 0:2]), feats[..., 2:4]], axis=-1)
    
    pred_xy = tf.expand_dims(pred_xy, axis=4)
    pred_wh = tf.expand_dims(pred_wh, axis=4)
    pred_wh_half = pred_wh / 2.
    
    pred_mins = pred_xy - pred_wh_half
    pred_maxes = pred_xy + pred_wh_half
    
    true_boxes_shape = tf.shape(true_boxes)
    true_boxes = tf.reshape(true_boxes, [
        true_boxes_shape[0], 1, 1, 1, true_boxes_shape[1], true_boxes_shape[2]
    ])
    true_boxes = tf.cast(true_boxes, 'float32')
    true_xy = true_boxes[..., 0:2]
    true_wh = true_boxes[..., 2:4]
    true_wh_half = true_wh / 2.
    
    true_mins = true_xy - true_wh_half
    true_maxes = true_xy + true_wh_half
    
    intersect_mins = tf.math.maximum(pred_mins, true_mins)
    intersect_maxes = tf.math.minimum(pred_maxes, true_maxes)
    intersect_wh = tf.math.maximum(intersect_maxes - intersect_mins, 0.)
    intersect_areas = intersect_wh[..., 0] * intersect_wh[..., 1]
    
    pred_areas = pred_wh[..., 0] * pred_wh[..., 1]
    true_areas = true_wh[..., 0] * true_wh[..., 1]
    union_areas = pred_areas + true_areas - intersect_areas
    
    iou_scores = intersect_areas / union_areas
    best_ious = tf.math.reduce_max(iou_scores, axis=4)  # Best IOU scores.

    best_ious = tf.expand_dims(best_ious, axis=-1)
 
    object_detections = tf.cast(best_ious > 0.6, tf.float32)

    no_object_weights = no_object_scale * (1 - object_detections) * (1 - detectors_mask)
    no_objects_loss = no_object_weights * tf.math.square(-pred_confidence)
    objects_loss = object_scale * detectors_mask * tf.math.square(1 - pred_confidence)
    confidence_loss = objects_loss + no_objects_loss
    
    matching_classes = tf.cast(matching_true_boxes[..., 4], tf.int32)

    matching_classes = tf.one_hot(matching_classes, num_classes, on_value=1.0, off_value=0.0, axis=-1)
    
    classification_loss = (class_scale * detectors_mask *
                           tf.math.square(matching_classes - pred_class_prob))
                           
    matching_boxes = matching_true_boxes[..., 0:4]

    coordinates_loss = (coordinates_scale * detectors_mask * 
                        tf.math.square(matching_boxes - pred_boxes))
    
    confidence_loss = tf.reshape(confidence_loss, [-1])
    confidence_loss_sum = tf.math.reduce_sum(confidence_loss)

    classification_loss = tf.reshape(classification_loss, [-1])
    classification_loss_sum = tf.math.reduce_sum(classification_loss)
    
    coordinates_loss = tf.reshape(coordinates_loss, [-1])
    coordinates_loss_sum = tf.math.reduce_sum(coordinates_loss)

    confidence_loss_sum = 0.5 * confidence_loss_sum
    classification_loss_sum = 0.5 * classification_loss_sum
    coordinates_loss_sum = 0.5 * coordinates_loss_sum
    total_loss = confidence_loss_sum + classification_loss_sum + coordinates_loss_sum

    return total_loss
