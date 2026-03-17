# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import random
import matplotlib.patches as patches
import numpy as np
import tensorflow as tf


def bbox_center_to_corners_coords(
                boxes: tf.Tensor, 
                image_size: tuple = None,
                normalize: bool = None,
                clip_boxes: bool = False) -> tf.Tensor:

    """
    Converts coordinates of bounding boxes in (x, y, w, h) system
    to coordinates in (x1, y1, x2, y2) system. (x1, y1) and (x2, y2)
    are pairs of diagonally opposite corners.
    Input coordinates must be normalized (lying in the interval
    [0, 1]). Output coordinates can be normalized or absolute.
    
    Arguments:
        boxes:
            Bounding boxes in (x, y, w, h) coordinates system with
            normalized values.
            Shape: [batch_size, 4]
        image_size:
            A tuple specifying the size of the image: (width, height).
            Required only when `normalize` is False.
        normalize:
            A boolean. If True, the output coordinates are normalized.
            If False, they are absolute.
        clip_boxes:
            A boolean. If True, the output coordinates of the bounding
            boxes are clipped to fit the image. If False, they are
            left as is. Defaults to False.

    Output coordinates:
        Bounding boxes in (x1, y1, x2, y2) coordinates system, with 
        normalized or absolute values.
        Shape:[batch_size, 4]
    """
        
    x = boxes[..., 0]
    y = boxes[..., 1]
    w = boxes[..., 2]
    h = boxes[..., 3]
    
    x1 = x - w/2
    y1 = y - h/2
    x2 = x + w/2
    y2 = y + h/2

    if normalize:
        if clip_boxes:
            x1 = tf.clip_by_value(x1, 0, 1)
            y1 = tf.clip_by_value(y1, 0, 1)
            x2 = tf.clip_by_value(x2, 0, 1)
            y2 = tf.clip_by_value(y2, 0, 1)
    else:
        image_size = tf.cast(image_size, tf.float32)
        width = image_size[0]
        height = image_size[1]
        x1 = tf.round(x1 * width)
        y1 = tf.round(y1 * height)
        x2 = tf.round(x2 * width)
        y2 = tf.round(y2 * height)

        if clip_boxes:
            x1 = tf.clip_by_value(x1, 0, width - 1)
            y1 = tf.clip_by_value(y1, 0, height - 1)
            x2 = tf.clip_by_value(x2, 0, width - 1)
            y2 = tf.clip_by_value(y2, 0, height - 1)
   
    return tf.stack([x1, y1, x2, y2], axis=-1)


def bbox_corners_to_center_coords(
                boxes: tf.Tensor,
                image_size: tuple = None,
                abs_corners: bool = None,
                clip_boxes: bool = False) -> tf.Tensor:
    """
    Converts coordinates of bounding boxes in (x1, y1, x2, y2) system
    to coordinates in (x, y, w, h) system. (x1, y1) and (x2, y2)
    are pairs of diagonally opposite corners.
    Input coordinates must be normalized (lying in the interval
    [0, 1]). Output coordinates can be normalized or absolute.
    
    Arguments:
        boxes:
            Bounding boxes in (x, y, w, h) coordinates system with
            normalized values.
            Shape: [batch_size, 4]
        image_size:
            A tuple specifying the size of the image: (width, height).
            Required only when `normalize` is False.
        normalize:
            A boolean. If True, the output coordinates are normalized.
            If False, they are absolute.
        clip_boxes:
            A boolean. If True, the output coordinates of the bounding
            boxes are clipped to fit the image. If False, they are
            left as is. Defaults to False.

    Output coordinates:
        Bounding boxes in (x1, y1, x2, y2) coordinates system, with 
        normalized or absolute values.
        Shape:[batch_size, 4]
    """

    x1 = boxes[..., 0]
    y1 = boxes[..., 1]
    x2 = boxes[..., 2]
    y2 = boxes[..., 3]

    # If the input corners coordinates are absolute, normalize them.
    if abs_corners:
        image_size = tf.cast(image_size, tf.float32)
        width = image_size[0]
        height = image_size[1]
        x1 /= width
        y1 /= height
        x2 /= width
        y2 /= height

    w = x2 - x1
    h = y2 - y1
    x = x1 + w / 2
    y = y1 + h / 2

    if clip_boxes:
        x = tf.clip_by_value(x, 0, 1)
        y = tf.clip_by_value(y, 0, 1)
        w = tf.clip_by_value(w, 0, 1)
        h = tf.clip_by_value(h, 0, 1)
        
    return tf.stack([x, y, w, h], axis=-1)


def bbox_normalized_to_abs_coords(
                boxes: tf.Tensor,
                image_size: tuple = None,
                clip_boxes: bool = False):
    """
    Converts coordinate values of bounding boxes in (x1, y1, x2, y2)
    system from normalized to absolute. (x1, y1) and (x2, y2)
    are pairs of diagonally opposite corners.
    
    Arguments:
        boxes:
            Bounding boxes in (x1, y1, x2, y2) coordinates system
            with normalized values.
            Shape: [batch_size, 4]
        image_size:
            A tuple specifying the size of the image: (width, height).
        clip_boxes:
            A boolean. If True, the output coordinates of the bounding
            boxes are clipped to fit the image. If False, they are
            left as is. Defaults to False.

    Output coordinates:
        Bounding boxes in (x1, y1, x2, y2) coordinates system with 
        absolute values.
        Shape:[batch_size, 4]
    """
    
    x1 = boxes[..., 0]
    y1 = boxes[..., 1]
    x2 = boxes[..., 2]
    y2 = boxes[..., 3]
    
    image_size = tf.cast(image_size, tf.float32)
    width = image_size[0]
    height = image_size[1]

    x1 = tf.round(x1 * width)
    y1 = tf.round(y1 * height)
    x2 = tf.round(x2 * width)
    y2 = tf.round(y2 * height)
    
    if clip_boxes:
        x1 = tf.clip_by_value(x1, 0, width - 1)
        y1 = tf.clip_by_value(y1, 0, height - 1)
        x2 = tf.clip_by_value(x2, 0, width - 1)
        y2 = tf.clip_by_value(y2, 0, height - 1)

    return tf.stack([x1, y1, x2, y2], axis=-1)
        
    
def bbox_abs_to_normalized_coords(
                boxes: tf.Tensor,
                image_size: tuple = None,
                clip_boxes: bool = False) -> tf.Tensor:

    """
    Converts coordinate values of bounding boxes in (x1, y1, x2, y2)
    system from absolute to normalized. (x1, y1) and (x2, y2)
    are pairs of diagonally opposite corners.
    
    Arguments:
        boxes:
            Bounding boxes in (x1, y1, x2, y2) coordinates system
            with absolute values.
            Shape: [batch_size, 4]
        image_size:
            A tuple specifying the size of the image: (width, height).
        clip_boxes:
            A boolean. If True, the output coordinates of the bounding
            boxes are clipped to fit the image. If False, they are
            left as is. Defaults to False.

    Output coordinates:
        Bounding boxes in (x1, y1, x2, y2) coordinates system with 
        normalized values.
        Shape:[batch_size, 4]
    """
    
    x1 = boxes[..., 0]
    y1 = boxes[..., 1]
    x2 = boxes[..., 2]
    y2 = boxes[..., 3]
    
    image_size = tf.cast(image_size, tf.float32)
    width = image_size[0]
    height = image_size[1]
    x1 /= width
    y1 /= height
    x2 /= width
    y2 /= height

    if clip_boxes:
        x1 = tf.clip_by_value(x1, 0, 1)
        y1 = tf.clip_by_value(y1, 0, 1)
        x2 = tf.clip_by_value(x2, 0, 1)
        y2 = tf.clip_by_value(y2, 0, 1)

    return tf.stack([x1, y1, x2, y2], axis=-1)
    

def calculate_box_wise_iou(
                box1: tf.Tensor,
                box2: tf.Tensor,
                abs_coords: bool = None) -> tf.Tensor:
    """
    Calculates the IOUs of two sets of bounding boxes in an 
    element-wise fashion (box to box). The coordinates of
    bounding boxes must be in the (x1, y1, x2, y2) system, with
    normalized or absolute values. (x1, y1) and (x2, y2) are
    pairs of diagonally opposite corners.

    Arguments:
        box1:
            First set of bounding boxes with coordinates in
            (x1, y1, x2, y2) system. 
            Shape: [num_boxes, 4]
        box2:
            Second set of bounding boxes with coordinates in
            (x1, y1, x2, y2) system. 
            Shape: [num_boxes, 4]
        abs_coords:
            Boolean. If True, coordinate values are absolute.
            If False, they are normalized.

    Returns:
        A tf.Tensor with shape [num_boxes], the box-to-box IOU values.
    """

    box1_x1 = box1[:, 0]
    box1_y1 = box1[:, 1]
    box1_x2 = box1[:, 2]
    box1_y2 = box1[:, 3]

    box2_x1 = box2[:, 0]
    box2_y1 = box2[:, 1]
    box2_x2 = box2[:, 2]
    box2_y2 = box2[:, 3]
    
    # Calculate the coordinates of diagonally opposite
    # corners of the intersection of box1 and box2
    inter_x1 = tf.math.maximum(box1_x1, box2_x1)
    inter_y1 = tf.math.maximum(box1_y1, box2_y1)
    inter_x2 = tf.math.minimum(box1_x2, box2_x2)
    inter_y2 = tf.math.minimum(box1_y2, box2_y2)
    
    if abs_coords:
        inter_x = inter_x2 - inter_x1 + 1
        inter_y = inter_y2 - inter_y1 + 1
    else:
        inter_x = inter_x2 - inter_x1
        inter_y = inter_y2 - inter_y1

    inter_area = tf.math.maximum(inter_x, 0.) * tf.math.maximum(inter_y, 0.)

    if abs_coords:
        box1_area = (box1_x2 - box1_x1 + 1) * (box1_y2 - box1_y1 + 1)
        box2_area = (box2_x2 - box2_x1 + 1) * (box2_y2 - box2_y1 + 1)
    else:
        box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
        box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)
    
    union_area = box1_area + box2_area - inter_area

    iou = tf.where(union_area > 0, inter_area / union_area, 0.)

    return iou


def plot_bounding_boxes(ax, boxes, classes=None, scores=None, class_names=None, colors=None):
    
    # The function may be called with tensors.
    # Make sure we have numpy arguments.
    boxes = np.array(boxes, dtype=np.float32)
    if classes is not None:
        classes = np.array(classes, dtype=np.int32)
    if scores is not None:
        scores = np.array(scores, dtype=np.float32)

    # Sample the box and text colors if they are not provided
    num_boxes = np.shape(boxes)[0]
    if colors is None:
        colors = []
        for i in range(num_boxes):
            colors.append(random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'w']))
    
    for i in range(num_boxes):
        # Skip padding boxes
        if np.sum(boxes[i]) == 0:
            continue
            
        # Draw the box
        x1, y1, x2, y2 = boxes[i]
        rec = patches.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                linewidth=2, edgecolor=colors[i], facecolor='none')
        ax.add_patch(rec)
                
        ## Add the class name and score to the box
        if (classes is not None) or (scores is not None):
            class_txt = ''
            if classes is not None:
                class_txt = class_names[classes[i]]
                if scores is not None:
                   class_txt += ': '
            score_txt = ''
            if scores is not None:
                score_txt = "{:.4f}".format(scores[i])
            legend = class_txt + score_txt
            
            ax.text(x1 + 2, y1 - 3,
                    legend,
                    color='black', fontsize = 6, weight='bold',
                    bbox = dict(facecolor=colors[i], color=colors[i], alpha=0.75))

