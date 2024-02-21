# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow.keras import backend as K

def tiny_yolo_v2_decode(feats, anchors, num_classes, input_shape, calc_loss=False):
    """
    Decode final layer features to bounding box parameters.

    Args:
        feats (tensor): Final layer features of a YOLOv2 model.
        anchors (list of tuples): Anchor boxes for the model.
        num_classes (int): Number of object classes.
        input_shape (tuple): Tuple specifying the size of the input images.
        calc_loss (bool, default=False): If True, return loss function expected params.

    Returns:
        If calc_loss is True, returns the grid, features, box_xy, and box_wh tensors.
        Otherwise, returns the box_xy, box_wh, box_confidence, and box_class_probs tensors.
    """
    num_anchors = len(anchors)
    anchors_tensors = K.reshape(K.constant(anchors), [1, 1, 1, num_anchors, 2])
    grid_shape = K.shape(feats)[1:3]
    anchors_tensor = (anchors_tensors/K.cast(input_shape[..., ::-1], K.dtype(feats)))*K.cast(grid_shape[..., ::-1], K.dtype(feats))
    
    grid_y = K.tile(K.reshape(K.arange(0, stop=grid_shape[0]), [-1, 1, 1, 1]),[1, grid_shape[1], 1, 1])
    grid_x = K.tile(K.reshape(K.arange(0, stop=grid_shape[1]), [1, -1, 1, 1]),[grid_shape[0], 1, 1, 1])
    grid = K.concatenate([grid_x, grid_y])
    grid = K.cast(grid, K.dtype(feats))

    feats = K.reshape(feats, [-1, grid_shape[0], grid_shape[1], num_anchors, num_classes + 5])

    box_xy = (K.sigmoid(feats[..., :2]) + grid) / K.cast(grid_shape[..., ::-1], K.dtype(feats))
    box_wh = K.exp(feats[..., 2:4]) * anchors_tensor / K.cast(grid_shape[..., ::-1], K.dtype(feats))
    box_confidence = K.sigmoid(feats[..., 4:5])
    box_class_probs = K.softmax(feats[..., 5:])

    if calc_loss == True:
        return grid, feats, box_xy, box_wh
    return [box_xy, box_wh, box_confidence, box_class_probs]

def filter_boxes(my_boxes,boxes, box_confidence, box_class_probs, threshold=0.5):
    """
    Filters YOLO boxes based on object and class confidence.

    Args:
        my_boxes (tensor): containing the coordinates of the boxes in the original image dimensions.
        boxes (tensor): containing the coordinates of the boxes.
        box_confidence (tensor): containing the object confidence scores.
        box_class_probs (tensor): containing the class probabilities.
        threshold (float): threshold for box score to be considered as a detection.

    Returns:
        boxes (tensor): containing the coordinates of the filtered boxes in corners format.
        scores (tensor): containing the scores of the filtered boxes.
        classes (tensor): containing the class IDs of the filtered boxes.
        my_boxes (tensor): containing the coordinates of the filtered boxes in centoids format.
    """
    box_scores =  box_confidence*box_class_probs
    box_classes = K.argmax(box_scores, axis=-1)
    box_class_scores = K.max(box_scores, axis=-1)
    prediction_mask = box_class_scores >= threshold
    boxes = tf.boolean_mask(boxes, prediction_mask)
    my_boxes = tf.boolean_mask(my_boxes, prediction_mask)
    scores = tf.boolean_mask(box_class_scores, prediction_mask)
    classes = tf.boolean_mask(box_classes, prediction_mask)
    return boxes, scores, classes,my_boxes

def process_boxes(box_xy, box_wh):
    """
    Concatinate xw and wh arrays.

    Args:
        box_xy (tensor): containing the center coordinates of the boxes.
        box_wh (tensor): containing the width and height of the boxes.

    Returns:
        corners (tensor): containing the corner coordinates of the boxes in (xmin, ymin, xmax, ymax) format.
        centers (tensor): containing the center coordinates and width and height of the boxes in (x, y, w, h) format.
    """
    box_mins = box_xy - (box_wh / 2.)
    
    box_maxes = box_xy + (box_wh / 2.)
    corners = K.concatenate([
        box_mins[..., 1:2],  # y_min
        box_mins[..., 0:1],  # x_min
        box_maxes[..., 1:2], # y_max
        box_maxes[..., 0:1]  # x_max
        ])
    centers = K.concatenate([
        box_xy[..., 1:2],  # y
        box_xy[..., 0:1],  # x
        box_wh[..., 1:2],  # h
        box_wh[..., 0:1],  # w
        ])
    return corners, centers

def tiny_yolo_v2_nms(yolo_outputs,image_shape,max_boxes=30,score_threshold=.5,iou_threshold=.3 , classes_ids=[0]):
    """
    Applies non-max suppression to the output of Tiny YOLO v2 model.

    Args:
        yolo_outputs (list): output of the Tiny YOLO v2 model.
        image_shape (tuple): shape of the input image (height, width).
        max_boxes (int): maximum number of boxes to be selected by non-max suppression.
        score_threshold (float): threshold for box score to be considered as a detection.
        iou_threshold (float): threshold for intersection over union to be considered as a duplicate detection.
        classes_ids (list): list of class IDs to perform non-max suppression on.

    Returns:
        s_boxes (tensor): tensor of shape (num_boxes, 4) containing the coordinates of the selected boxes in corners format.
        s_scores (tensor): tensor of shape (num_boxes,) containing the scores of the selected boxes.
        s_classes (tensor): tensor of shape (num_boxes,) containing the class IDs of the selected boxes.
        s_my_boxes (tensor): tensor of shape (num_boxes, 4) containing the coordinates of the selected boxes in centroids format.
    """
    box_xy, box_wh, box_confidence, box_class_probs = yolo_outputs
    boxes,my_boxes = process_boxes(box_xy, box_wh)
    boxes, scores, classes,my_boxes= filter_boxes(my_boxes,boxes, box_confidence, box_class_probs, threshold=score_threshold)
    height = image_shape[0]
    width = image_shape[1]
    image_dims = K.stack([height, width, height, width])
    image_dims = K.reshape(image_dims, [1, 4])
    image_dims = K.cast(image_dims, dtype='float32')
    boxes = boxes * image_dims
    max_boxes_tensor = K.variable(max_boxes, dtype='int32')
    total_boxes = []
    total_scores = []
    total_classes = []
    total_my_boxes = []
    #apply nms per class
    for c in classes_ids:
        mask =tf.equal(classes, c)
        s_classes = tf.boolean_mask(classes, mask)
        s_scores = tf.boolean_mask(scores, mask)
        s_boxes = tf.boolean_mask(boxes, mask)
        s_my_boxes = tf.boolean_mask(my_boxes, mask)

        nms_index = tf.image.non_max_suppression(
            s_boxes, s_scores, max_boxes_tensor, iou_threshold=iou_threshold)
        s_boxes = K.gather(s_boxes, nms_index)
        s_scores = K.gather(s_scores, nms_index)
        s_classes = K.gather(s_classes, nms_index)
        s_my_boxes = K.gather(s_my_boxes, nms_index)

        total_boxes.append(s_boxes)
        total_scores.append(s_scores)
        total_classes.append(s_classes)
        total_my_boxes.append(s_my_boxes)
    s_boxes = K.concatenate(total_boxes, axis=0)
    s_my_boxes = K.concatenate(total_my_boxes, axis=0)
    s_scores = K.concatenate(total_scores, axis=0)
    s_classes = K.concatenate(total_classes, axis=0)
    return s_boxes, s_scores, s_classes,s_my_boxes