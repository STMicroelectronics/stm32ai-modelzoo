# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
import numpy as np

from object_detection.tf.src.utils import calculate_box_wise_iou


def _calculate_iou_matrix(anchor_boxes: tf.Tensor, gt_boxes: tf.Tensor) -> tf.Tensor:
    """
    Takes as inputs a set of anchor boxes and a set of groundtruth boxes,
    and calculates the IOU of each anchor box with each groundtruth box.

    Box coordinates must be (x1, y1, x2, y2) coordinates, with normalized
    or absolute values. (x1, y1) and (x2, y2) are pairs of diagonally
    opposite corners.
 
    Arguments:
        anchor_boxes:
            Anchor boxes.
            A tf.Tensor with shape [batch_size, num_anchors, 4]
        gt_boxes:
            Groundtruth boxes.
            A tf.Tensor with shape [batch_size, num_labels, 4]
    
    Returns:
        The IOU matrix.
        A tf.Tensor with shape [batch_size, num_anchors, num_labels]
    """
    
    batch_size = tf.shape(gt_boxes)[0]
    num_anchor_boxes = tf.shape(anchor_boxes)[1]
    num_gt_boxes = tf.shape(gt_boxes)[1]

    # Tile the anchors and boxes to have all anchor/GT pairs
    num_tiles =  batch_size * num_anchor_boxes * num_gt_boxes
    anchor_boxes_t = tf.tile(anchor_boxes, [1, 1, num_gt_boxes])
    anchor_boxes_t = tf.reshape(anchor_boxes_t, [num_tiles,  4])
    gt_boxes_t = tf.tile(gt_boxes, [1, num_anchor_boxes, 1])
    gt_boxes_t = tf.reshape(gt_boxes_t, [num_tiles,  4])

    box_wise_iou = calculate_box_wise_iou(anchor_boxes_t, gt_boxes_t)

    # Reshape the box wise IOUs to get an IOU matrix
    iou_matrix = tf.reshape(box_wise_iou, [batch_size, num_anchor_boxes, num_gt_boxes])

    return iou_matrix


def _bipartite_matching(
                iou_matrix: tf.Tensor,
                gt_labels: tf.Tensor,
                num_anchors: int = None,
                num_labels: int = None) -> tuple:
            
    """
    Matches each groundtruth (GT) box with an anchor box using
    bipartite matching.
    
    Each GT box is matched with one anchor and the same anchor
    box can match only one GT box.
    
    The matches output of the function is a tf.Tensor with shape
    [batch_size, num_anchors, 5]. It is initialized with 0's.
    When an anchor is matched with a GT label, the anchor position
    in the matches tensor is set to the GT label.
    
    The algorithm is as follows:
        for i in range(num_labels):
            - Look for the anchor/GT pair that has the highest IOU
              across the entire IOU matrix
            - Match (associate) the anchor and the GT
            - Set to 0 all the IOUs of the matched anchor and GT
              so that they can no longer be involved in a match.
    
    Arguments:
        iou_matrix:
            Matrix of IOU values between anchor boxes and GT boxes.
            A tf.Tensor with shape [batch_size, num_anchors, num_labels]
        gt_labels:
            Groundtruth labels.
            A tf.Tensor with shape [batch_size, num_labels, 5]
        num_anchors:
            An integer, the number of anchor boxes.
        num_labels:
            An integer, the number of groundtruth labels.
            
    Returns:
        gt_anchor_matches:
            The GT/anchor matches
            A tf.Tensor with shape [batch_size, num_anchors, 5]
        iou_matrix:
            The updated IOU matrix with 0's at the locations of already
            matched anchors to avoid that they match again.
            A tf.Tensor with shape [batch_size, num_anchors, num_labels]
    """
    
    batch_size = tf.shape(iou_matrix)[0]

    # Append a dummy anchor to the IOU matrix
    zeros = tf.zeros([batch_size, 1, num_labels], dtype=tf.float32)
    iou_matrix = tf.concat([iou_matrix, zeros], axis=1)

    gt_anchor_matches = tf.zeros([batch_size, num_anchors + 1, 5], dtype=tf.float32)

    already_matched_gt = tf.zeros([batch_size, num_labels], dtype=tf.int32)

    x = tf.repeat(tf.range(batch_size), num_labels)
    batch_range = tf.reshape(x, [batch_size, num_labels])

    x = tf.range(batch_size * num_labels) % num_labels
    labels_range = tf.reshape(x, [batch_size, num_labels])

    for _ in range(num_labels):

        # For each GT, get the index of the anchor that has the maximum 
        # IOU value across all anchors. Then, get the IOU value.
        best_anchors = tf.math.argmax(iou_matrix, axis=1, output_type=tf.int32)
        ind = tf.stack([batch_range, best_anchors, labels_range], axis=-1)
        best_iou = tf.gather_nd(iou_matrix, ind)

        # Find the index the GT that has the largest IOU value
        # across still unmatched GT's. Then get the IOU value.
        best_iou = tf.where(already_matched_gt == 1, -1., best_iou)
        gt_match = tf.math.argmax(best_iou, axis=-1, output_type=tf.int32)
        ind = tf.stack([tf.range(batch_size), gt_match], axis=-1)
        iou_match = tf.gather_nd(best_iou, ind)

        # Get the index of the anchor that matches the best GT
        ind = tf.stack([tf.range(batch_size), gt_match], axis=-1)
        anchor_match = tf.gather_nd(best_anchors, ind)
        anchor_match = tf.where(iou_match > 0, anchor_match, num_anchors)

        # Fetch the matched GT and add it to the matches
        match_ind = tf.stack([tf.range(batch_size), gt_match], axis=-1)
        labels = tf.gather_nd(gt_labels, match_ind)
        match_ind = tf.stack([tf.range(batch_size), anchor_match], axis=-1)
        gt_anchor_matches = tf.tensor_scatter_nd_update(gt_anchor_matches, match_ind, labels)

        # Set all the IOUs of the matched anchor to 0
        # so that they can't match again 
        update = tf.zeros([batch_size, num_labels], dtype=tf.float32)
        iou_matrix = tf.tensor_scatter_nd_update(iou_matrix, match_ind, update)
        
        # Add the matched GT to the already matched GT's
        ind = tf.stack([tf.range(batch_size), gt_match], axis=-1)
        update = tf.ones([batch_size], dtype=tf.int32)
        already_matched_gt = tf.tensor_scatter_nd_update(already_matched_gt, ind, update)

    return gt_anchor_matches[:, :-1], iou_matrix[:, :-1, :]


def _positive_iou_matching(
                iou_matrix: tf.Tensor,
                gt_labels: tf.Tensor,
                matches: tf.Tensor,
                num_anchors: int = None,
                num_labels: int = None,
                pos_iou_threshold: float = None) -> tuple:                 

    """
    Matches the groundtruth (GT) boxes and anchor boxes that have
    an IOU value greater or equal to the positive IOU threshold.
    
    A GT box can match several anchors and an anchor can match
    only one GT box.

    Arguments:
        iou_matrix:
            Matrix of IOU values between anchor boxes and GT boxes.
            A tf.Tensor with shape [batch_size, num_anchors, num_labels]
        gt_labels:
            Groundtruth labels.
            A tf.Tensor with shape [batch_size, num_labels, 5]
        matches:
            The GT/anchor matches already made by bipartite matching.
            A tf.Tensor with shape [batch_size, num_anchors, 5]
        num_anchors:
            An integer, the number of anchor boxes.
        num_labels:
            An integer, the number of groundtruth labels.
        pos_iou_threshold:
            A float, the IOU threshold used to a associate
            an anchor box and a GT box.
            
    Returns:
        matches:
            The GT/anchor matches.
            A tf.Tensor with shape [batch_size, num_anchors, 5]
        iou_matrix:
            The updated IOU matrix with 0's at the locations of already
            matched anchors to avoid that they match again.
            A tf.Tensor with shape [batch_size, num_anchors, num_labels]
    """

    batch_size = tf.shape(iou_matrix)[0]

    # Append a dummy label to labels
    padding = tf.zeros([batch_size, 1, 5], dtype=tf.float32)
    gt_labels = tf.concat([gt_labels, padding], axis=1)

    # For each GT, get the index of the anchor that has the maximum 
    # IOU value across all anchors. Then, get the IOU value.
    gt_indices = tf.math.argmax(iou_matrix, axis=-1, output_type=tf.int32)
    max_iou = tf.math.reduce_max(iou_matrix, axis=-1)
    gt_indices = tf.where(max_iou >= pos_iou_threshold, gt_indices, num_labels)

    # Fetch the labels
    x = tf.repeat(tf.range(batch_size), num_anchors)
    batch_range = tf.reshape(x, [batch_size, num_anchors])
    ind = tf.stack([batch_range, gt_indices], axis=-1)
    labels = tf.gather_nd(gt_labels, ind)
    matches += labels

    # Get the indices of the matches that were updated
    indices = tf.where(gt_indices < num_labels)
    num_updates = tf.shape(indices)[0]

    updates = tf.zeros([num_updates, num_labels], dtype=tf.float32)
    iou_matrix = tf.tensor_scatter_nd_update(iou_matrix, indices, updates)
 
    return matches, iou_matrix


def _neutral_iou_matching(
                iou_matrix: tf.Tensor,
                matches: tf.Tensor,
                pos_iou_threshold: float = None,
                neg_iou_threshold: float = None) -> tf.Tensor:
    """
    If the maximum IOU value of an anchor box across all the GT's falls
    between the negative IOU threshold and the positive IOU threshold,
    it is associated to the background class.

    Arguments:
        iou_matrix:
            Matrix of IOU values between anchor boxes and GT boxes.
            A tf.Tensor with shape [batch_size, num_anchors, num_labels]
        gt_labels:
            Groundtruth labels.
            A tf.Tensor with shape [batch_size, num_labels, 5]
        matches:
            The GT/anchor matches already made by bipartite matching
            and pôsitive matching.
            A tf.Tensor with shape [batch_size, num_anchors, 5]
        num_anchors:
            An integer, the number of anchor boxes.
        num_labels:
            An integer, the number of groundtruth labels.
        pos_iou_threshold:
            A float, the positive IOU threshold.
        negative_iou_threshold:
            A float, the negative IOU threshold.
            
    Returns:
        matches:
            The GT/anchor matches.
            A tf.Tensor with shape [batch_size, num_anchors, 5]
    """
    
    # Look for neutral anchors, i.e. anchors with
    # a maximum IOU value across GT's that falls in 
    # the [neg_iou_threshold, pos_iou_threshold[ interval
    max_iou = tf.math.reduce_max(iou_matrix, axis=-1)

    cond = tf.math.logical_and(max_iou >= neg_iou_threshold, max_iou < pos_iou_threshold)
    indices = tf.cast(tf.where(cond), tf.int32)

    # Append a 0 to the indices to access the class in matches
    # (indices 1 to 4 are the box coordinates)
    num_updates = tf.shape(indices)[0]
    zeros = tf.zeros([num_updates, 1], dtype=tf.int32)
    indices = tf.concat([indices, zeros], axis=-1)

    # Set the class of the matched GT's to zero (background)
    updates = tf.zeros([num_updates], dtype=tf.float32)
    matches = tf.tensor_scatter_nd_update(matches, indices, updates)

    return matches
    

def _postprocess_anchor_matches(
                box_matches: tf.Tensor,
                anchor_boxes: tf.Tensor,
                num_anchors: int = None):
    """
    This function postprocesses GT/anchor matches to account
    for the offsets applied to anchors.
    """

    batch_size = tf.shape(anchor_boxes)[0]
    
    sum_boxes = tf.reduce_sum(box_matches, axis=-1)
    mask = tf.where(sum_boxes != 0, 1., 0.)
    x = tf.repeat(mask, 4)
    box_mask = tf.reshape(x, [batch_size, num_anchors, 4])

    x1_anchors = anchor_boxes[..., 0]
    y1_anchors = anchor_boxes[..., 1]
    x2_anchors = anchor_boxes[..., 2]
    y2_anchors = anchor_boxes[..., 3]

    x1_gt = box_matches[..., 0]
    y1_gt = box_matches[..., 1]
    x2_gt = box_matches[..., 2]
    y2_gt = box_matches[..., 3]
 
    anchor_width = x2_anchors - x1_anchors + 1e-9
    x1 = (x1_gt - x1_anchors) / anchor_width
    x2 = (x2_gt - x2_anchors) / anchor_width

    anchor_height = y2_anchors - y1_anchors + 1e-9
    y1 = (y1_gt - y1_anchors) / anchor_height
    y2 = (y2_gt - y2_anchors) / anchor_height

    box_matches_pp = tf.stack([x1, y1, x2, y2], axis=-1)
    
    # Set back to 0 the matches that were intially
    # set to 0 (meaning there was no match).
    box_matches_pp *= box_mask

    return box_matches_pp


def match_gt_anchors(anchor_boxes: tf.Tensor,
                     gt_labels : tf.Tensor,
                     num_classes: int = None,
                     num_anchors: int = None,
                     num_labels: int = None,
                     pos_iou_threshold: float = None,
                     neg_iou_threshold: float = None) -> tf.Tensor:
        
    """
    Assign groundtruth labels to anchor boxes for training.
    
    All anchors that did not match any groundtruth label are assigned
    to the background class, which is class 0.
    
    Arguments:
        anchor_boxes:
            Anchor boxes.
            A tf.Tensor with shape [batch_size, num_anchors, 4]
        gt_labels:
            Groundtruth labels.
            A tf.Tensor with shape [batch_size, num_labels, 5]
        num_classes:
            An integer, the number of classes.
        num_anchors:
            An integer, the number of anchor boxes.
        num_labels:
            An integer, the number of groundtruth labels.
        pos_iou_threshold:
            A float, the positive IOU threshold.
        negative_iou_threshold:
            A float, the negative IOU threshold.
            
    Returns:
        Classes are one-hot encoded in the output matches.
        Each match:
        [batch_size, num_anchors, num_classes, 4]

    """

    batch_size = tf.shape(gt_labels)[0]
    
    # Increment the class indices in GT labels to account 
    # for the background class. Padding boxes stay assigned
    # to class 0 as they are treated as background.
    gt_classes = gt_labels[..., 0]
    gt_boxes = gt_labels[..., 1:]
    coords_sum = tf.math.reduce_sum(gt_boxes, axis=-1)
    gt_classes = tf.where(coords_sum > 0, gt_classes + 1, 0.)
    gt_labels = tf.concat([tf.expand_dims(gt_classes, axis=-1), gt_boxes], axis=-1)

    num_anchor_boxes = tf.shape(anchor_boxes)[0]

    # Replicate the anchor boxes to have them in each batch item
    x = tf.tile(anchor_boxes, [batch_size, 1])
    anchor_boxes = tf.reshape(x, [batch_size, num_anchor_boxes, 4])
  
    iou_matrix = _calculate_iou_matrix(anchor_boxes, gt_labels[..., 1:])

    matches, iou_matrix = _bipartite_matching(
                    iou_matrix, gt_labels,
                    num_anchors=num_anchors, num_labels=num_labels)

    matches, iou_matrix = _positive_iou_matching(
                    iou_matrix, gt_labels, matches,
                    num_anchors=num_anchors, num_labels=num_labels,
                    pos_iou_threshold=pos_iou_threshold)
    
    if neg_iou_threshold < pos_iou_threshold:
        matches = _neutral_iou_matching(
                        iou_matrix, matches,
                        pos_iou_threshold=pos_iou_threshold, neg_iou_threshold=neg_iou_threshold)

    class_matches = tf.cast(matches[..., 0], tf.int32)
    class_matches = tf.one_hot(class_matches, depth=num_classes + 1, on_value=1.0, off_value=0.0, dtype=tf.float32)
    box_matches = _postprocess_anchor_matches(matches[..., 1:], anchor_boxes, num_anchors)

    output = tf.concat([class_matches, box_matches, anchor_boxes], axis=-1)

    return output
