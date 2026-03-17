# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import math
import collections
import torch
import itertools
from typing import List
import numpy as np
import tensorflow as tf
from pathlib import Path
from object_detection.tf.src.models import model_family


SSDBoxSizes = collections.namedtuple('SSDBoxSizes', ['min', 'max'])

SSDSpec = collections.namedtuple('SSDSpec', ['feature_map_size', 'shrinkage', 'box_sizes', 'aspect_ratios'])


def convert_locations_to_boxes(locations, priors):
    """
    Convert regressional location results of SSD into boxes in the form of (center_x, center_y, h, w).
    Args:
        locations (batch_size, num_priors, 4): the regression output of SSD.
        priors (num_priors, 4) or (batch_size/1, num_priors, 4): prior boxes.
        center_variance: a float used to change the scale of center.
        size_variance: a float used to change of scale of size.
    Returns:
        boxes: [[center_x, center_y, h, w]]. All the values are relative to the image size.
    """
    center_variance = 0.1
    size_variance = 0.2
    # Ensure priors shape matches locations
    if priors.ndim + 1 == locations.ndim:
        priors = np.expand_dims(priors, axis=0)
    center = locations[..., :2] * center_variance * priors[..., 2:] + priors[..., :2]
    size = np.exp(locations[..., 2:] * size_variance) * priors[..., 2:]
    return np.concatenate([center, size], axis=locations.ndim - 1)

def generate_ssd_priors(image_size, clamp=True) -> torch.Tensor:
    specs = [
            SSDSpec(19, 16, SSDBoxSizes(60, 105), [2, 3]),
            SSDSpec(10, 32, SSDBoxSizes(105, 150), [2, 3]),
            SSDSpec(5, 64, SSDBoxSizes(150, 195), [2, 3]),
            SSDSpec(3, 100, SSDBoxSizes(195, 240), [2, 3]),
            SSDSpec(2, 150, SSDBoxSizes(240, 285), [2, 3]),
            SSDSpec(1, 300, SSDBoxSizes(285, 330), [2, 3]),
        ]
    priors = []
    for spec in specs:
        scale = image_size / spec.shrinkage
        for j, i in itertools.product(range(spec.feature_map_size), repeat=2):
            x_center = (i + 0.5) / scale
            y_center = (j + 0.5) / scale

            # small sized square box
            size = spec.box_sizes.min
            h = w = size / image_size
            priors.append([
                x_center,
                y_center,
                w,
                h
            ])

            # big sized square box
            size = math.sqrt(spec.box_sizes.max * spec.box_sizes.min)
            h = w = size / image_size
            priors.append([
                x_center,
                y_center,
                w,
                h
            ])

            # change h/w ratio of the small sized box
            size = spec.box_sizes.min
            h = w = size / image_size
            for ratio in spec.aspect_ratios:
                ratio = math.sqrt(ratio)
                priors.append([
                    x_center,
                    y_center,
                    w * ratio,
                    h / ratio
                ])
                priors.append([
                    x_center,
                    y_center,
                    w / ratio,
                    h * ratio
                ])

    priors = torch.tensor(priors)
    if clamp:
        torch.clamp(priors, 0.0, 1.0, out=priors)
    return priors

def decode_ssd_torch_predictions(predictions_r, cfg):
    ssd_t_post_proc_chpos = 'chfirst' # channel first
    if cfg.operation_mode != 'prediction':
        out_chpos = cfg.evaluation.output_chpos
        target = cfg.evaluation.target
    else:
        out_chpos = cfg.prediction.output_chpos
        target = cfg.prediction.target
    
    if out_chpos != ssd_t_post_proc_chpos and target != 'host':
        predictions = []
        for pred in predictions_r:
            # Convert from channel last to channel first
            if len(pred.shape) == 3:
                pred = tf.transpose(pred, perm=[0, 2, 1]).numpy()
                predictions.append(pred)
            elif len(pred.shape) == 4:
                pred = tf.transpose(pred, perm=[0, 3, 1, 2]).numpy()
                predictions.append(pred)
    else:
        predictions = predictions_r

    locations = predictions[1] #(32, 3000, 4)
    confidences = predictions[0] #(32, 3000, 21)
    #===============================================================
    confidences = torch.tensor(confidences)
    # Apply softmax to get class probabilities
    scores = torch.softmax(confidences, dim=2).numpy()
    scores = scores[..., 1:]  # Remove background class
    #===============================================================
    anchors = generate_ssd_priors(cfg.model.input_shape[-1]).numpy()
    # boxes: (N, B, 4) [center_x, center_y, h, w]
    boxes = convert_locations_to_boxes(locations, anchors)

    x = boxes[..., 0]
    y = boxes[..., 1]
    w = boxes[..., 2]
    h = boxes[..., 3]
    boxes = tf.stack([x - w/2, y - h/2, x + w/2, y + h/2], axis=-1)
    boxes = tf.clip_by_value(boxes, 0, 1)
    
    return boxes, scores

def decode_ssd_predictions(predictions: tuple, clip_boxes: bool = True) -> tuple:
    """
    An SSD model outputs anchor boxes and offsets. This function
    applies the offsets to the anchor boxes to obtain the coordinates
    of the bounding boxes predicted by the model.
    
    Arguments:
        predictions:
            The SSD model output, a tuple of 3 elements:
                1. Scores of predicted boxes.
                   A tf.Tensor with shape [batch_size, num_anchors, num_classes]
                2. Offsets.
                   A tf.Tensor with shape [batch_size, num_anchors, 4]
                3. Anchor boxes.
                   A tf.Tensor with shape [batch_size, num_anchors, 4]
        clip_boxes:
            A boolean. If True, the coordinates of the output bounding boxes
            are clipped to fit the image. If False, they are left as is. 
            Defaults to True.

    Returns:
        scores:
            The scores of the predicted bounding boxes in each class.
            A tf.Tensor with shape [batch_size, num_anchors, num_classes]
        boxes:
            The predicted bounding boxes in the (x1, y1, x2, y2) coordinates
            system. (x1, y1) and (x2, y2) are pairs of diagonally opposite 
            corners. The coordinates values are normalized.
            A tf.Tensor with shape [batch_size, num_anchors, 4]
    """

    scores = predictions[0]
    raw_boxes = predictions[1]
    anchor_boxes = predictions[2]
    
    # Apply anchor offsets to the detection boxes
    x1 = raw_boxes[..., 0] * (anchor_boxes[..., 2] - anchor_boxes[..., 0]) + anchor_boxes[..., 0]
    x2 = raw_boxes[..., 2] * (anchor_boxes[..., 2] - anchor_boxes[..., 0]) + anchor_boxes[..., 2]
    y1 = raw_boxes[..., 1] * (anchor_boxes[..., 3] - anchor_boxes[..., 1]) + anchor_boxes[..., 1]
    y2 = raw_boxes[..., 3] * (anchor_boxes[..., 3] - anchor_boxes[..., 1]) + anchor_boxes[..., 3]

    boxes = tf.stack([x1, y1, x2, y2], axis=-1)
    if clip_boxes:
        boxes = tf.clip_by_value(boxes, 0, 1)
       
    # Get rid of the background class
    scores = scores[..., 1:]
    
    return boxes, scores

    
def yolo_head(feats, anchors, num_classes):
    """
    Convert final layer features to bounding box parameters.

    Parameters
    ----------
    feats : tensor
        Final convolutional layer features.
    anchors : array-like
        Anchor box widths and heights.
    num_classes : int
        Number of target classes.

    Returns
    -------
    box_xy : tensor
        x, y box predictions adjusted by spatial location in conv layer.
    box_wh : tensor
        w, h box predictions adjusted by anchors and conv spatial resolution.
    box_conf : tensor
        Probability estimate for whether each box contains any object.
    box_class_pred : tensor
        Probability distribution estimate for each box over class labels.
    """

    num_anchors = tf.shape(anchors)[0]
    anchors = tf.reshape(anchors, [1, 1, 1, num_anchors, 2])

    # Get the dimensions of the grid of cells
    conv_dims = tf.shape(feats)[1:3]
    
    # Generate the grid cell indices
    # Note: YOLO iterates over height index before width index.
    i = tf.where(tf.ones([conv_dims[1], conv_dims[0]], dtype=tf.bool))
    conv_index = tf.stack([i[:, 1], i[:, 0]], axis=-1)
    
    # The coordinates box_xy of the centers of prediction boxes
    # are relative to the top-left corner of the grid cells.
#    print("conv_dims : ",conv_dims)
#    print("conv_dims[0] : ",conv_dims[0])
#    print("conv_dims[1] : ",conv_dims[1])
#    print("num_anchors : ",num_anchors)
#    print("num_classes + 5 : ",num_classes + 5)
    feats = tf.reshape(feats, [-1, conv_dims[0], conv_dims[1], num_anchors, num_classes + 5])
    box_xy = tf.math.sigmoid(feats[..., :2])
    box_wh = tf.math.exp(feats[..., 2:4])
    box_confidence = tf.math.sigmoid(feats[..., 4:5])
    box_class_probs = tf.math.softmax(feats[..., 5:])

    conv_index = tf.reshape(conv_index, [1, conv_dims[0], conv_dims[1], 1, 2])
    conv_index = tf.cast(conv_index, tf.float32)
    conv_dims = tf.reshape(conv_dims, [1, 1, 1, 1, 2])
    conv_dims = tf.cast(conv_dims, tf.float32)

    # Adjust the coordinates of the centers of prediction 
    # boxes to grid cell locations so that they are 
    # relative to the top-left corner of the image.
    box_xy = (box_xy + conv_index) / conv_dims
    box_wh = box_wh * anchors / conv_dims

    return box_xy, box_wh, box_confidence, box_class_probs

    
def decode_yolo_predictions(predictions, num_classes, anchors, image_size):

    box_xy, box_wh, box_confidence, box_class_probs = yolo_head(predictions, anchors, num_classes)

    x = box_xy[..., 0]
    y = box_xy[..., 1]
    w = box_wh[..., 0]
    h = box_wh[..., 1]
    boxes = tf.stack([x - w/2, y - h/2, x + w/2, y + h/2], axis=-1)
    boxes = tf.clip_by_value(boxes, 0, 1)   
    
    # Flatten boxes using the shape of box_confidence which is 
    # [batch_size, yolo_grid_nrows, yolo_grid_ncols, num_anchors]
    conf_shape = tf.shape(box_confidence)
    batch_size = conf_shape[0]
    num_boxes = conf_shape[1] * conf_shape[2] * conf_shape[3]

    boxes = tf.reshape(boxes, [batch_size, num_boxes, 4])
    
    box_confidence = tf.reshape(box_confidence, [batch_size, num_boxes, 1])
    box_class_probs = tf.reshape(box_class_probs, [batch_size, num_boxes, num_classes])
    scores = box_confidence * box_class_probs
    
    return boxes, scores

def decode_yolov8n_predictions(predictions):
    x = predictions[..., 0]
    y = predictions[..., 1]
    w = predictions[..., 2]
    h = predictions[..., 3]
    boxes = tf.stack([x - w/2, y - h/2, x + w/2, y + h/2], axis=-1)
    boxes = tf.clip_by_value(boxes, 0, 1)
    scores = predictions[..., 4:]
    return boxes, scores

def ssd_generate_anchors(opts):
    """This is a trimmed down version of the C++ code; all irrelevant parts
    have been removed.
    (reference: mediapipe/calculators/tflite/ssd_anchors_calculator.cc)
    """
    layer_id = 0
    num_layers = opts['num_layers']
    strides = opts['strides']
    assert len(strides) == num_layers
    input_height = opts['input_size_height']
    input_width = opts['input_size_width']
    anchor_offset_x = opts['anchor_offset_x']
    anchor_offset_y = opts['anchor_offset_y']
    interpolated_scale_aspect_ratio = opts['interpolated_scale_aspect_ratio']
    anchors = []
    while layer_id < num_layers:
        last_same_stride_layer = layer_id
        repeats = 0
        while (last_same_stride_layer < num_layers and
               strides[last_same_stride_layer] == strides[layer_id]):
            last_same_stride_layer += 1
            repeats += 2 if interpolated_scale_aspect_ratio == 1.0 else 1
        stride = strides[layer_id]
        feature_map_height = input_height // stride
        feature_map_width = input_width // stride
        for y in range(feature_map_height):
            y_center = (y + anchor_offset_y) / feature_map_height
            for x in range(feature_map_width):
                x_center = (x + anchor_offset_x) / feature_map_width
                for _ in range(repeats):
                    anchors.append((x_center, y_center))
        layer_id = last_same_stride_layer
    return np.array(anchors, dtype=np.float32)

def remove_kpts(arr):
    if arr.shape[1] > 1:
        return arr[:, :4]
    return arr

def sort_and_combine(arrays):
    squeezed_arrays = [np.squeeze(arr, axis=0) for arr in arrays]
    sorted_arrays = sorted(squeezed_arrays, key=lambda arr: (arr.shape[0], arr.shape[1]), reverse=True)
    processed_arrays = [remove_kpts(arr) for arr in sorted_arrays]
    out_1 = np.concatenate((processed_arrays[0], processed_arrays[1]), axis=1)
    out_2 = np.concatenate((processed_arrays[2], processed_arrays[3]), axis=1)
    final_array = np.concatenate((out_1, out_2), axis=0)
    return  final_array

def _decode_boxes(raw_boxes,input_shape,anchors):
    # width == height so scale is the same across the board
    scale = input_shape
    num_points = raw_boxes.shape[-1] // 2
    # scale all values (applies to positions, width, and height alike)
    boxes = raw_boxes.reshape(-1, num_points, 2) / scale
    # adjust center coordinates and key points to anchor positions
    boxes[:, 0] += anchors
    for i in range(2, num_points):
        boxes[:, i] += anchors
    # convert x_center, y_center, w, h to xmin, ymin, xmax, ymax
    center = np.array(boxes[:, 0])
    half_size = boxes[:, 1] / 2
    boxes[:, 0] = center - half_size
    boxes[:, 1] = center + half_size
    return boxes

def sigmoid(data):
    return 1 / (1 + np.exp(-data))

def _get_sigmoid_scores(raw_scores):
    """Extracted loop from ProcessCPU (line 327) in
    mediapipe/calculators/tflite/tflite_tensors_to_detections_calculator.cc
    """
    # score limit is 100 in mediapipe and leads to overflows with IEEE 754 floats
    # # this lower limit is safe for use with the sigmoid functions and float32
    RAW_SCORE_LIMIT = 80
    # just a single class ("face"), which simplifies this a lot
    # 1) thresholding; adjusted from 100 to 80, since sigmoid of [-]100
    #    causes overflow with IEEE single precision floats (max ~10e38)
    raw_scores[raw_scores < -RAW_SCORE_LIMIT] = -RAW_SCORE_LIMIT
    raw_scores[raw_scores > RAW_SCORE_LIMIT] = RAW_SCORE_LIMIT
    # 2) apply sigmoid function on clipped confidence scores
    return sigmoid(raw_scores)

def decode_face_detect_front_predictions(predictions,image_size):
    SSD_OPTIONS_FRONT = {
    'num_layers': 4,
    'input_size_height': 128,
    'input_size_width': 128,
    'anchor_offset_x': 0.5,
    'anchor_offset_y': 0.5,
    'strides': [8, 16, 16, 16],
    'interpolated_scale_aspect_ratio': 1.0}
    anchors=ssd_generate_anchors(SSD_OPTIONS_FRONT)
    out = sort_and_combine(predictions)
    decoded_boxes = _decode_boxes(out[:,0:4],image_size[0],anchors) #xmin, ymin, xmax, ymax
    reshaped_d_boxes = decoded_boxes.reshape(-1, 4)
    decoded_scores = _get_sigmoid_scores(out[:,-1])
    reshaped_d_scores = np.expand_dims(decoded_scores, axis=1)
    boxes = np.expand_dims(reshaped_d_boxes, axis=0)
    scores = np.expand_dims(reshaped_d_scores, axis=0)
    return boxes, scores




def decode_yolov4_predictions(predictions):
    # Lists to hold respective values while unwrapping.
    boxes = np.clip(np.squeeze(predictions[0]), 0, 1)
    scores = np.squeeze(predictions[1])
    if(len(scores.shape)==1):
        scores = np.expand_dims(scores,axis=1)
    boxes = np.expand_dims(boxes, axis=0)
    scores = np.expand_dims(scores, axis=0)
    
    return boxes, scores

_TORCH_VER = [int(x) for x in torch.__version__.split(".")[:2]]

def meshgrid(*tensors):
    import torch 
    if _TORCH_VER >= [1, 10]:
        return torch.meshgrid(*tensors, indexing="ij")
    else:
        return torch.meshgrid(*tensors)
    
def decode_outputs(predictions,cfg):
    import torch 
    
    outputs = torch.as_tensor(predictions)   
    
    img_w = cfg.model.input_shape[-1]
    img_h = cfg.model.input_shape[-2]
    strides_list=[8, 16, 32]
    
    hw = [
    (img_h // s, img_w // s)
    for s in strides_list
    ]
    
    grids = []
    strides = []
    
    for (hsize, wsize), stride in zip(hw, strides_list):
        yv, xv = meshgrid([torch.arange(hsize), torch.arange(wsize)])
        grid = torch.stack((xv, yv), 2).view(1, -1, 2)
        grids.append(grid)
        shape = grid.shape[:2]
        strides.append(torch.full((*shape, 1), stride))

    grids = torch.cat(grids, dim=1).type(torch.FloatTensor)
    strides = torch.cat(strides, dim=1).type(torch.FloatTensor)
    
    
    boxes = outputs[...,0:4]
    prob_conf = outputs[...,4:] 
    
    # ---- NO IN-PLACE OPS BELOW ----
    xy = (boxes[..., 0:2] + grids) * strides
    wh = torch.exp(boxes[..., 2:4]) * strides

    # normalize
    xy = torch.stack(
        [xy[..., 0] / img_w, xy[..., 1] / img_h],
        dim=-1
    )
    wh = torch.stack(
        [wh[..., 0] / img_w, wh[..., 1] / img_h],
        dim=-1
    )
    
    outputs = torch.cat([
        xy,
        wh,
        prob_conf, 
    ], dim=-1)

    predictions = outputs.detach().cpu().numpy()
    return predictions
    
def decode_yolod_predictions(predictions, cfg):
    
    yolo_d_post_proc_chpos = 'chfirst' # channel first
    if cfg.operation_mode != 'prediction':
        out_chpos = cfg.evaluation.output_chpos
        target = cfg.evaluation.target
    else:
        out_chpos = cfg.prediction.output_chpos
        target = cfg.prediction.target
    if out_chpos != yolo_d_post_proc_chpos and target != 'host':
        # Convert from channel last to channel first
        if len(predictions.shape) == 3:
            predictions = tf.transpose(predictions, perm=[0, 2, 1]).numpy()
        elif len(predictions.shape) == 4:
            predictions = tf.transpose(predictions, perm=[0, 3, 1, 2]).numpy()
    else:
        predictions = predictions

    predictions = decode_outputs(predictions,cfg)

    x = predictions[..., 0]
    y = predictions[..., 1]
    w = predictions[..., 2]
    h = predictions[..., 3]
    prob = predictions[..., 5:]
    objectness = predictions[..., 4]
    objectness = objectness[..., None]
    scores = prob * objectness
    boxes = tf.stack([x - w/2, y - h/2, x + w/2, y + h/2], axis=-1)
    boxes = tf.clip_by_value(boxes, 0, 1)
    
    return boxes, scores



def blind_nms(boxes_scores,max_output_size,iou_threshold,score_threshold):

    boxes = boxes_scores[...,:4] # shape (anchors,classes,4)
    scores = boxes_scores[...,4] # shape (anchors,classes,1)

    boxes = tf.reshape(boxes,[-1,4]) # shape (anchors*classes,4)
    scores = tf.reshape(scores,[-1]) # shape (anchors*classes)

    selected_indices,valid_outputs = tf.raw_ops.NonMaxSuppressionV4(boxes=boxes,
                                                                    scores=scores,
                                                                    max_output_size=max_output_size,
                                                                    iou_threshold=iou_threshold,
                                                                    score_threshold=score_threshold,
                                                                    pad_to_max_output_size=True)

    nmsed_boxes = tf.gather(boxes,selected_indices)   # shape (max_output_size,4)
    nmsed_scores = tf.gather(scores,selected_indices) # shape (max_output_size)
    valid_outputs = tf.cast(tf.range(max_output_size)<tf.cast(valid_outputs,tf.int32),tf.float32) # shape (max_output_size)

    return tf.concat(values=[nmsed_boxes,nmsed_scores[...,None],valid_outputs[...,None]],axis=-1) # shape (max_output_size,6)

def st_combined_nms(boxes_scores,max_output_size,iou_threshold,score_threshold):

    boxes_scores = tf.transpose(boxes_scores,[1,0,2]) # shape (classes,anchors,5) FLOAT32

    args = {'max_output_size':max_output_size,
            'iou_threshold':iou_threshold,
            'score_threshold':score_threshold}

    classed_value = tf.map_fn(lambda x : blind_nms(x,**args), boxes_scores) # shape (classes,max_output_size,6) FLOAT32
    classed_value = tf.reshape(classed_value,[-1,6])                        # shape (classes*max_output_size,6) FLOAT32

    classed_valid =  classed_value[:,-1]                                    # shape (classes*max_output_size)   FLOAT32
    classed_scores = classed_value[:,-2]*classed_valid                      # shape (classes*max_output_size)   FLOAT32
    classed_boxes  = classed_value[:,:-2]*classed_valid[...,None]           # shape (classes*max_output_size,4) FLOAT32

    cls_nb = tf.shape(classed_scores)[0] // max_output_size # number of classes INT32

    nmsed_scores,classed_indices = tf.raw_ops.TopKV2(input=classed_scores,k=max_output_size,sorted=True,index_type=tf.int32) # shape (max_output_size) FLOAT32, (max_output_size) INT32

    nmsed_cls = tf.cast(classed_indices//max_output_size,tf.float32) # shape (max_output_size) FLOAT32

    nmsed_boxes = tf.gather(classed_boxes,classed_indices) # shape (max_output_size,4) FLOAT32

    return tf.concat(values=[nmsed_boxes,nmsed_scores[...,None],nmsed_cls[...,None]],axis=-1) # shape (max_output_size,6)

def st_combined_non_max_suppression(boxes,scores,max_total_size,iou_threshold,score_threshold):

    boxes_scores = tf.concat(values=[boxes,scores[...,None]],axis=-1) # shape (batch,anchors,classes,5)

    args = {'max_output_size':max_total_size,
            'iou_threshold':iou_threshold,
            'score_threshold':score_threshold}

    nmsed_values = tf.map_fn(lambda x : st_combined_nms(x,**args), boxes_scores)

    nmsed_boxes, nmsed_scores, nmsed_classes = nmsed_values[...,:-2],nmsed_values[...,-2],nmsed_values[...,-1]

    return nmsed_boxes, nmsed_scores, nmsed_classes


def nms_box_filtering(
                boxes: tf.Tensor,
                scores: tf.Tensor,
                max_boxes: int = None,
                score_threshold: float = None,
                iou_threshold: float = None,
                clip_boxes: bool = True) -> tuple:
    """
    Prunes detection boxes using non-max suppression (NMS).
    
    The coordinates of the input bounding boxes must be in the
    (x1, y1, x2, y2) system with normalized values. (x1, y1)
    and (x2, y2) are pairs of diagonally opposite corners.
    The output boxes are also in the (x1, y1, x2, y2) system 
    with normalized values.
    
    The NMS is class-aware, i.e. the IOU between two boxes assigned
    to different classes is 0.
    
    If the number of boxes selected by NMS is less than the maximum
    number, padding boxes with all 4 coordinates set to 0 are
    used to reach the maximum number.
    
    Arguments:
        boxes:
            Detection boxes to prune using NMS.
            A tf.Tensor with shape [batch_size, num_boxes, 4]
        scores:
            Scores of the detection boxes in each class.
            A tf.Tensor with shape [batch_size, num_boxes, num_classes]
        max_boxes:
            An integer, the maximum number of boxes to be selected
            by NMS.
        score_threshold:
            A float, the score threshold to use to discard 
            low-confidence boxes.
        iou_threshold:
            A float, the IOU threshold used to eliminate boxes that
            have a large overlap with a selected box.
        clip_boxes:
            A boolean. If True, the output coordinates of the boxes
            selected by NMS are clipped to fit the image. If False,
            they are left as is. Defaults to True.

    Returns:
        nmsed_boxes:
            Boxes selected by NMS. 
            A tf.Tensor with shape [batch_size, max_boxes, 4]
        nmsed_scores:
            Scores of the selected boxes.
            A tf.Tensor with shape [batch_size, max_boxes]
        nmsed_classes:
            Classes assigned to the selected boxes.
            A tf.Tensor with shape [batch_size, max_boxes]
    """
    
    batch_size = tf.shape(boxes)[0]
    num_boxes = tf.shape(boxes)[1]
    num_classes = tf.shape(scores)[-1]
    
    # Convert box coordinates from (x1, y1, x2, y2) to (y1, x1, y2, x2)
    boxes = tf.stack([boxes[..., 1], boxes[..., 0], boxes[..., 3], boxes[..., 2]], axis=-1)

    # NMS is run by class, so we need to replicate the boxes num_classes times.
    boxes_t = tf.tile(boxes, [1, 1, num_classes])
    nms_input_boxes = tf.reshape(boxes_t, [batch_size, num_boxes, num_classes, 4])


    # nmsed_boxes, nmsed_scores, nmsed_classes = st_combined_non_max_suppression(
    #                                                 boxes=nms_input_boxes,
    #                                                 scores=scores,
    #                                                 max_total_size=max_boxes,
    #                                                 iou_threshold=iou_threshold,
    #                                                 score_threshold=score_threshold)


    # The valid_detections output is not returned. Invalid boxes 
    # have all 4 coordinates set to 0, so they are easy to spot.    
    nmsed_boxes, nmsed_scores, nmsed_classes, _ = \
                tf.image.combined_non_max_suppression(
                        boxes=nms_input_boxes,
                        scores=scores,  
                        max_output_size_per_class=max_boxes,
                        max_total_size=max_boxes,
                        iou_threshold=iou_threshold,
                        score_threshold=score_threshold,
                        # Pad/clip output nmsed boxes, scores and classes to max_total_size
                        pad_per_class=False,
                        # Clip coordinates of output nmsed boxes to [0, 1]
                        clip_boxes=clip_boxes)

    # Convert coordinates of NMSed boxes to (x1, y1, x2, y2)
    nmsed_boxes = tf.stack([nmsed_boxes[..., 1], nmsed_boxes[..., 0],
                            nmsed_boxes[..., 3], nmsed_boxes[..., 2]],
                            axis=-1)

    return nmsed_boxes, nmsed_scores, nmsed_classes


def get_nmsed_detections(cfg, predictions, image_size):

    num_classes = len(cfg.dataset.class_names)
    cpp = cfg.postprocessing
    
    if model_family(cfg.model.model_type) == "ssd":
        boxes, scores = decode_ssd_predictions(predictions)
    elif model_family(cfg.model.model_type) == "yolo":
        boxes, scores = decode_yolo_predictions(predictions, num_classes, cpp.yolo_anchors, image_size)

    elif model_family(cfg.model.model_type) == "st_yoloxn":
        np_anchors=[]
        anchors = cpp.yolo_anchors
        network_stride = cpp.network_stride
        predictions = sorted(predictions, key=lambda x: x.shape[1], reverse=True)
        anchors = [anchors * (image_size[0]/ns) for ns in network_stride]
        for anch in anchors:
            if isinstance(anch, np.ndarray):
                np_anchors.append(anch.astype(np.float32))
            else:
                np_anchors.append(anch.numpy().astype(np.float32)) 
        levels_boxes = []
        levels_scores = []
        for i , prediction in enumerate(predictions):
            box, score = decode_yolo_predictions(prediction, num_classes, np_anchors[i], image_size)
            levels_boxes.append(box)
            levels_scores.append(score)
        
        boxes = tf.concat(levels_boxes, axis=1)
        scores = tf.concat(levels_scores, axis=1)
    
    elif model_family(cfg.model.model_type) == "yolov8n":
        boxes, scores = decode_yolov8n_predictions(predictions)
    elif model_family(cfg.model.model_type) == "yolov4":
        boxes, scores = decode_yolov4_predictions(predictions)
    elif model_family(cfg.model.model_type) == "face_detect_front":
        boxes, scores = decode_face_detect_front_predictions(predictions,image_size)

    else:
        raise ValueError("Unsupported model type")
        
    # NMS the detections
    nmsed_boxes, nmsed_scores, nmsed_classes = nms_box_filtering(
                    boxes,
                    scores,
                    max_boxes=cpp.max_detection_boxes,
                    score_threshold=cpp.confidence_thresh,
                    iou_threshold=cpp.NMS_thresh)

    return nmsed_boxes, nmsed_scores, nmsed_classes

def get_detections(cfg, predictions, image_size):

    num_classes = len(cfg.dataset.class_names)
    cpp = cfg.postprocessing
    
#    if model_family(cfg.model.model_type) == "ssd":
#        boxes, scores = decode_ssd_predictions(predictions)
#    elif model_family(cfg.model.model_type) == "yolo":
    if model_family(cfg.model.model_type) == "yolo":
        boxes, scores = decode_yolo_predictions(predictions, num_classes, cpp.yolo_anchors, image_size)

    elif model_family(cfg.model.model_type) == "st_yoloxn":
        np_anchors=[]
        anchors = cpp.yolo_anchors
        network_stride = cpp.network_stride
        predictions = sorted(predictions, key=lambda x: x.shape[1], reverse=True)
        anchors = [anchors * (image_size[0]/ns) for ns in network_stride]
        for anch in anchors:
            if isinstance(anch, np.ndarray):
                np_anchors.append(anch.astype(np.float32))
            else:
                np_anchors.append(anch.numpy().astype(np.float32)) 
        levels_boxes = []
        levels_scores = []
        for i , prediction in enumerate(predictions):
            box, score = decode_yolo_predictions(prediction, num_classes, np_anchors[i], image_size)
            levels_boxes.append(box)
            levels_scores.append(score)
        
        boxes = tf.concat(levels_boxes, axis=1)
        scores = tf.concat(levels_scores, axis=1)
    
    elif model_family(cfg.model.model_type) == "yolov8n":
        boxes, scores = decode_yolov8n_predictions(predictions)
    elif("yolod" in str(getattr(cfg.model, "model_name", "") or "").lower()) or ("yolod" in str(getattr(cfg.model, "model_type", "") or "").lower()):
        boxes, scores = decode_yolod_predictions(predictions,cfg)
    elif("ssd" in str(getattr(cfg.model, "model_name", "") or "").lower()) or ("ssd" in str(getattr(cfg.model, "model_type", "") or "").lower()):
        boxes, scores = decode_ssd_torch_predictions(predictions,cfg)
    else:
        raise ValueError("Unsupported model type")

    return boxes, scores