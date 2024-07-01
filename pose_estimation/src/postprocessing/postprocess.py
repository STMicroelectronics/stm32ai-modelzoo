# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2024 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
import numpy as np


def heatmaps_spe_postprocess(tensor:tf.Tensor):
    '''
    Post-process for the single pose estimation heatmaps use-case

    Args
        tensor    (tf.Tensor): shape (batch, res, res, keypoints) FLOAT32 heatmaps outputs of the single pose estimation models
    
    Returns:
        detection (tf.Tensor): shape (batch, 1, keypoints*3) FLOAT32 the (x,y,conf) values of all keypoints for the single person
    '''

    sh = tensor.shape # (batch, res,res,keypoints)

    predictions_flat = tf.reshape(tensor,[sh[0],sh[1]*sh[2],-1]) # flatten the prediction tensor,         shape : (batch,res*res,keypoints)
    arg_pred = tf.argmax(predictions_flat,1) # find the argmax for each keypoints in this flatten tensor, shape : (batch,keypoints)
    val_pred = tf.reduce_max(predictions_flat,1) # find the max value of this flatten tensor,             shape : (batch,keypoints)

    arg_pred_x = (tf.cast(arg_pred//sh[2],dtype=tf.float32)+0.5) / sh[1] # find the x values of keypoints in [0,1], shape : (batch,keypoints)
    arg_pred_y = (tf.cast(arg_pred%sh[2],dtype=tf.float32)+0.5) / sh[2] # find the y values of keypoints in [0,1],  shape : (batch,keypoints)

    detection = tf.stack([arg_pred_y,arg_pred_x,val_pred],1) # shape : (batch,3,keypoints)
    detection = tf.transpose(detection,[0,2,1])              # shape : (batch,keypoints,3)
    detection = tf.reshape(detection,[sh[0],-1])             # shape : (batch,keypoints*3)
    detection = detection[:,None,:]                          # shape : (batch,1,keypoints*3)

    return detection # shape : (batch,1,keypoints*3)

def spe_postprocess(tensor:tf.Tensor):
    '''
    Post-process for the single pose estimation use-case

    Args
        tensor    (tf.Tensor): shape (batch, 1, keypoints, 3) FLOAT32 the (x,y,conf) values of all keypoints but in a different format
    
    Returns:
        detection (tf.Tensor): shape (batch, 1, keypoints*3) FLOAT32 the (x,y,conf) values of all keypoints for the single person
    '''

    sh = tensor.shape

    x = tensor[:,:,:,1]
    y = tensor[:,:,:,0]
    v = tensor[:,:,:,2]

    detection = tf.stack([x,y,v],-1) # (batch, 1, keypoints, 3)

    detection = tf.reshape(detection,[sh[0],1,-1]) # (batch, 1, keypoints*3)

    return detection

def padded_nms(tensor:tf.Tensor,max_output_size:int,iou_threshold:float,score_threshold:float):
    '''
    Function used to apply NMS on each image of the batch independently

    Args
        tensor          (tf.Tensor): shape (5+keypoints*3, num_boxes) FLOAT32 outputs of the YOLO multi pose estimation models
        max_output_size (tf.Tensor): shape (1,) INT32 max number of detections per image
        iou_threshold   (tf.Tensor): shape (1,) FLOAT32 threshold for NMS iou
        score_threshold (tf.Tensor): shape (1,) FLOAT32 threshold to filter detections under a certain score
    
    Returns:
        detection       (tf.Tensor): shape (max_output_size, 5+keypoints*3) FLOAT32 bounding boxes + (x,y,conf) values for all keypoints of all detected persons
    '''

    boxes     = tensor[:4] # shape : (4,num_boxes)
    scores    = tensor[4]  # shape : (num_boxes)
    keypoints = tensor[5:] # shape : (nb_kpts*3,num_boxes)

    # the scores must be of the form [y1, x1, y2, x2] in order for the NMS to work
    # they are initially of the form [x,y,w,h]

    x1 = boxes[0] - boxes[2]/2 # shape : (num_boxes)
    y1 = boxes[1] - boxes[3]/2 # shape : (num_boxes)
    x2 = boxes[0] + boxes[2]/2 # shape : (num_boxes)
    y2 = boxes[1] + boxes[3]/2 # shape : (num_boxes)

    yxboxes = tf.stack([y1, x1, y2, x2])  # shape : (4,num_boxes)
    yxboxes = tf.transpose(yxboxes,[1,0]) # shape : (num_boxes,4)

    selected_indices = tf.image.non_max_suppression(yxboxes,scores,
                                                    max_output_size = max_output_size,
                                                    iou_threshold   = iou_threshold,
                                                    score_threshold = score_threshold)
    indices = selected_indices.shape[0]

    if indices:
        detection = tf.gather(tensor,selected_indices,axis=1) # shape : (5+nb_kpts*3,selected_indices)
        detection = tf.transpose(detection,[1,0])             # shape : (selected_indices,5+nb_kpts*3)
    else:
        detection = tf.zeros((indices,tensor.shape[0]))

    zero_padding = tf.zeros((max_output_size-indices,tensor.shape[0])) # shape : (max_output_size-selected_indices,5+nb_kpts*3)

    detection = tf.concat([detection,zero_padding],0) # shape : (max_output_size,5+nb_kpts*3)

    return detection # shape : (max_output_size, 5+nb_kpts*3)

def yolo_mpe_postprocess(tensor:tf.Tensor,max_output_size:int=20,iou_threshold:float=0.7,score_threshold:float=0.25):
    '''
    Post-process for the multi pose estimation use-case

    Args
        tensor          (tf.Tensor): shape (batch, 5+keypoints*3, num_boxes) FLOAT32 outputs of the YOLO multi pose estimation models
        max_output_size (tf.Tensor): shape (1,) INT32 max number of detections per image
        iou_threshold   (tf.Tensor): shape (1,) FLOAT32 threshold for NMS iou
        score_threshold (tf.Tensor): shape (1,) FLOAT32 threshold to filter detections under a certain score
    
    Returns:
        detections      (tf.Tensor): shape (batch, max_output_size, 5+keypoints*3) FLOAT32 values for all keypoints of all detected persons
    '''


    tensor = tf.constant(tensor,tf.float32)

    args = {'max_output_size':max_output_size,
            'iou_threshold':iou_threshold,
            'score_threshold':score_threshold}

    detections = tf.map_fn(lambda x : padded_nms(x,**args),tensor)

    return detections # shape : (batch, max_output_size, 5+keypoints*3)