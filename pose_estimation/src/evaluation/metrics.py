# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2024 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from typing import Optional


def oks_matrix(kpt0:tf.Tensor, kpt1:tf.Tensor, area:tf.Tensor, stddev:tf.Tensor, eps:Optional[float] = 1e-7):
    '''
    Calculate OKS (object keypoint similarities) matrix

    Args
        kpt0   (tf.Tensor): shape (batch, N, nb_kpts, 3) FLOAT32 representing ground truth keypoints.
        kpt1   (tf.Tensor): shape (batch, M, nb_kpts, 3) FLOAT32 representing predicted keypoints.
        area   (tf.Tensor): shape (batch, N) FLOAT32 representing areas of the poses of the gt kpts.
        stddev (tf.Tensor): shape (nb_kpts, ) FLOAT32 representing the normalized keypoints standard deviation
        eps     Optional[float]: shape (1,)   FLOAT32 value used to avoid division by zero

    Returns:
        oks    (tf.Tensor): shape (batch, N, M) representing the object keypoint similarities.
    '''

    area *= 0.53 # `0.53` is from https://github.com/jin-s13/xtcocoapi/blob/master/xtcocotools/cocoeval.py#L384

    X_2  = tf.square(kpt0[:, :, None, :, 0] - kpt1[:, None, :, :, 0]) # (batch,N,M,nb_kpts) distances between all keypoints on the x axis
    Y_2  = tf.square(kpt0[:, :, None, :, 1] - kpt1[:, None, :, :, 1]) # (batch,N,M,nb_kpts) distances between all keypoints on the y axis

    mask = kpt0[..., 2] # (batch,N,nb_kpts) visible keypoints

    distances_2 = X_2 + Y_2  # (batch,N,M,nb_kpts) distances between all keypoints

    z = -distances_2 / (tf.square(2*stddev[None, None, None, :]) * (area[:, :, None, None] + eps) * 2) # (batch,N,M,nb_kpts)

    oks = tf.math.reduce_sum(tf.math.exp(z) * mask[:, :, None, :], axis=-1) / (tf.math.reduce_sum(mask, axis=-1)[:, :, None] + eps) # (batch,N,M) OKS formula https://cocodataset.org/#keypoints-eval

    return oks

def pose_area_calculation(tensor:tf.Tensor):
    '''
    Calculate the area of a pose

    Args
        tensor (tf.Tensor): shape (batch, N, 2) FLOAT32 bounding box [w h] values
    
    Returns:
        area   (tf.Tensor): shape (batch, N) FLOAT32 W*H area of the poses
    '''

    area = tensor[...,0] * tensor[...,1] # w * h

    return area

def matching_predictions(tensor:tf.Tensor, thres:tf.Tensor):
    '''
    Matching of the predictions with the ground truths

    Args
        tensor   (tf.Tensor): shape (batch, N, M) FLOAT32 representing the object keypoint similarities.
        thres    (tf.Tensor): shape (thres, )     FLOAT32 thresholds for the OKS
    
    Returns:
        matching (tf.Tensor): shape (batch, M, thres) FLOAT32 0 and 1's representing the matching of the preds with a gt for every thresholds.
    '''

    batch,N,M = tf.shape(tensor)

    rtensor   = tf.reshape(tensor,[-1,N*M])                # (batch, N*M)
    
    # sorting this tensor from the best score to the worst per batch
    stensor   = tf.argsort(rtensor)[:,::-1]                # (batch, N*M)  INT32

    # creation of tensors used in the tensor_scatter_nd_update function
    z         = tf.zeros(tf.shape(stensor),tf.int32)       # (batch, N*M)  INT32

    range_t   = tf.tile(tf.range(batch)[:,None],[1,N*M])   # (batch, N*M)  INT32
    range_t   = tf.reshape(range_t,-1)                     # (batch*N*M)   INT32

    fstensor  = tf.reshape(stensor,-1)                     # (batch*N*M)   INT32
    fstensor  = tf.stack([range_t,fstensor],-1)            # (batch*N*M,2) INT32

    updates   = tf.range(batch*N*M)                        # (batch*N*M)   INT32

    # this function act as the inverse function of argsort applied on the sorted tensor
    stensor   = tf.tensor_scatter_nd_update(tensor=z,
                                            indices=fstensor,
                                            updates=updates) # (batch, N*M) INT32
    stensor -= tf.range(batch)[:,None]*N*M

    nm = tf.cast(N*M,tf.float32)

    # invert the order of the sort to have at 0 the best value of oks
    stensor = (nm-1.) - tf.cast(stensor,tf.float32)          # (batch, N, M) FLOAT32
    rstensor  = tf.reshape(stensor,[-1,N,M])                 # (batch, N, M) FLOAT32

    # find the argmax of this tensor and create masks
    arstensor = tf.argmax(rstensor,axis=1)                   # (batch, M)    INT64
    oarst     = tf.one_hot(arstensor,N,axis=1)               # (batch, N, M) FLOAT32


    # -1's are not selected
    rstensor = rstensor*oarst - (1-oarst)                  # (batch, N, M) FLOAT32

    eqzz = tf.reduce_sum(oarst,axis=-1)                    # (batch, N,)   FLOAT32
    eqzz = tf.cast(eqzz!=0,tf.float32)                     # (batch, N,)   FLOAT32
    
    brstensor = tf.argmax(rstensor,axis=-1)                # (batch, N)    INT64
    obrst     = tf.one_hot(brstensor,M,axis=-1)            # (batch, N, M) FLOAT32
    obrst    *= eqzz[:,:,None]                             # (batch, N, M) FLOAT32

    matching  = obrst                                      # (batch, N, M) FLOAT32

    oks_v     = tf.reduce_max(tensor * matching,axis=1)    # (batch, M)    FLOAT32

    t_matching = oks_v > thres[:,None,None]                # (thres, batch, M) BOOL
    t_matching = tf.cast(t_matching,tf.float32)            # (thres, batch, M) FLOAT32
    t_matching = tf.transpose(t_matching,[1,2,0])          # (batch, M, thres) FLOAT32

    return t_matching

def single_pose_oks(y_true:tf.Tensor, y_pred:tf.Tensor):
    '''
    Compute the OKS (object keypoint similarities) metric for single pose estimation

    Args
        y_true  (tf.Tensor): shape (batch, 1, 5+nb_kpts*3) FLOAT32 representing ground truth keypoints.
        y_pred  (tf.Tensor): shape (batch, 1, nb_kpts*3) FLOAT32 representing predicted keypoints.
    
    Returns:
        spe_oks (tf.Tensor): shape (batch,) representing the object keypoint similarities.
    '''

    sh = tf.shape(y_pred)

    nb_kpts = sh[2]//3

    area = pose_area_calculation(y_true[:,:,3:5]) # (batch, 1)

    if nb_kpts == 17:
        stddev = tf.constant([0.026,0.025,0.025,0.035,0.035,0.079,0.079,0.072,0.072,0.062,0.062,0.107,0.107,0.087,0.087,0.089,0.089],tf.float32)
    elif nb_kpts == 13:
        stddev = tf.constant([0.035,0.079,0.079,0.072,0.072,0.062,0.062,0.107,0.107,0.087,0.087,0.089,0.089],tf.float32)
    else:
        print("ERROR : evaluation with ",nb_kpts," keypoints not supported, try using a dataset with 17 or 13 keypoints")

    gt   = y_true[:,:,5:]                             # shape (batch, 1, nb_kpts*3)
    gt   = tf.reshape(gt,    [sh[0],sh[1],nb_kpts,3]) # shape (batch, 1, nb_kpts, 3)
    pred = tf.reshape(y_pred,[sh[0],sh[1],nb_kpts,3]) # shape (batch, 1, nb_kpts, 3)

    oks_m = oks_matrix(gt,pred,area,stddev)

    return oks_m[:,0,0] # shape (batch,)

def multi_pose_oks_mAP(y_true:tf.Tensor, y_pred:tf.Tensor):
    '''
    Compute the OKS mAP (object keypoint similarities - mean Average Precision) metric for multi pose estimation

    Args
        y_true  (tf.Tensor): shape (batch, N, 5+nb_kpts*3) FLOAT32 representing ground truth keypoints.
        y_pred  (tf.Tensor): shape (batch, M, 5+nb_kpts*3) FLOAT32 representing predicted keypoints.
    
    Returns:
        tp      (tf.Tensor): shape (batch*M,thresh) FLOAT32 0's and 1's representing the true positives
        conf    (tf.Tensor): shape (batch*M,)       FLOAT32 box confidences of the detections
        nb_gt   (tf.Tensor): shape (1,)             FLOAT32 number ground truths
        maskpad (tf.Tensor): shape (batch*M,)       FLOAT32 mask for the padding of predictions
    '''
    
    sh = tf.shape(y_pred[:,:,5:])

    nb_kpts = sh[2]//3

    area = pose_area_calculation(y_true[:,:,3:5]) # shape : (batch, N) FLOAT32 calculate area for the pose
    gtT  = tf.reduce_sum(y_true[:,:,5:],-1)       # shape : (batch, M) FLOAT32 sum of all prediction values for each prediction
    preT = tf.reduce_sum(y_pred,-1)               # shape : (batch, M) FLOAT32 sum of all prediction values for each prediction
    maskpad = tf.cast(preT>0,tf.float32)          # shape : (batch, M) FLOAT32 see if a prediction if truly a prediction or just a padding
    maskpad = tf.reshape(maskpad,[-1])            # shape : (batch*M,) FLOAT32

    stddev = tf.constant([0.026,0.025,0.025,0.035,0.035,0.079,0.079,0.072,0.072,0.062,0.062,0.107,0.107,0.087,0.087,0.089,0.089],tf.float32)
    thres  = tf.constant([0.5 , 0.55, 0.6 , 0.65, 0.7 , 0.75, 0.8 , 0.85, 0.9, 0.95],tf.float32)

    gt   = y_true[:,:,5:]                        # shape (batch, N, nb_kpts*3)
    pred = y_pred[:,:,5:]                        # shape (batch, M, nb_kpts*3)
    gt   = tf.reshape(gt,  [sh[0],-1,nb_kpts,3]) # shape (batch, N, nb_kpts, 3)
    pred = tf.reshape(pred,[sh[0],-1,nb_kpts,3]) # shape (batch, M, nb_kpts, 3)

    conf = y_pred[:,:,4]                         # shape (batch, M)
    conf = tf.reshape(conf,[-1])                 # shape (batch*M,)

    oks_m = oks_matrix(gt,pred,area,stddev) # (batch, N, M)

    mtp = matching_predictions(oks_m,thres) # (batch, M, thres)

    tp  = tf.reshape(mtp,[sh[0]*sh[1],-1])  # (batch*M, thres)

    nb_gt   = tf.math.count_nonzero(gtT)  # (batch, ) INT64
    nb_gt   = tf.reduce_sum(nb_gt)        # (1, )     INT64
    nb_gt   = tf.cast(nb_gt,  tf.float32) # (1, )     FLOAT32

    return tp, conf, nb_gt, maskpad # (batch*M,thresh), (batch*M,), (1,), (batch*M,)

def precision_recall(tp:tf.Tensor, conf:tf.Tensor, nb_gt:tf.Tensor, maskpad:tf.Tensor, eps:Optional[float] = 1e-7):
    '''
    Compute precision and recall for all thresholds

    Args
        tp      (tf.Tensor):     shape (batch*M,thresh) FLOAT32 0's and 1's representing the true positives
        conf    (tf.Tensor):     shape (batch*M,)       FLOAT32 box confidences of the detections
        nb_gt   (tf.Tensor):     shape (1,)             FLOAT32 number ground truths
        maskpad (tf.Tensor):     shape (batch*M,)       FLOAT32 mask for the padding of predictions
        eps     Optional[float]: shape (1,)             FLOAT32 value used to avoid division by zero
    
    Returns:
        precision (tf.Tensor): shape (thres, ) FLOAT32 precision values for all the thresholds
        recall    (tf.Tensor): shape (thres, ) FLOAT32 recall values for all the thresholds
    '''

    conf_sort = tf.argsort(conf)[::-1]      # (batch*M,) sort the confidence scores of the boxes by descending order

    ntp      = tf.gather(tp,conf_sort)      # (batch*M,thresh) reorder the axis 0 with sorted confidences

    nmaskpad = tf.gather(maskpad,conf_sort) # (batch*M,) reorder with sorted confidences

    TP = tf.cumsum(ntp)                      # (batch*M,thresh) cumulative summation on the axis 0
    FP = tf.cumsum((1-ntp)*nmaskpad[:,None]) # (batch*M,thresh) cumulative summation on the axis 0

    precision = TP / (TP + FP + eps)        # (batch*M,thresh) precision calculation
    recall    = TP / (nb_gt + eps)          # (batch*M,thresh) recall calculation

    return precision, recall

def auc(precision:tf.Tensor, recall:tf.Tensor):
    '''
    Compute the Area Under the Curve (AUC) that gives the mAP value

    Args
        precision (tf.Tensor): shape (thres, ) FLOAT32 precision values for all the thresholds
        recall    (tf.Tensor): shape (thres, ) FLOAT32 recall values for all the thresholds
    
    Returns:
        mAP (tf.Tensor): shape (1, ) FLOAT32 mean Average Precision value
    '''

    # Append sentinel values to beginning and end
    mrec = np.concatenate(([0.0], recall, [1.0]))
    mpre = np.concatenate(([1.0], precision, [0.0]))

    # Compute the precision envelope
    mpre = np.flip(np.maximum.accumulate(np.flip(mpre)))

    _,i_mrec = np.unique(mrec,return_index=True)

    mrec = mrec[i_mrec]
    mpre = mpre[i_mrec]

    # Integrate area under curve
    x  = np.linspace(0, 1, 101)  # 101-point interpolation (COCO)
    interpolation = np.interp(x, mrec, mpre)
    ap = np.trapz(interpolation, x)  # integrate
    
    return ap, mpre, mrec

def compute_ap(tp:tf.Tensor, conf:tf.Tensor, nb_gt:tf.Tensor, maskpad:tf.Tensor, plot_metrics:bool):
    '''
    Compute the AP (Average Precision) for each threshold values

    Args
        tp      (tf.Tensor): shape (batch*M,thresh) FLOAT32 0's and 1's representing the true positives
        conf    (tf.Tensor): shape (batch*M,)       FLOAT32 box confidences of the detections
        nb_gt   (tf.Tensor): shape (1,)             FLOAT32 number ground truths
        maskpad (tf.Tensor): shape (batch*M,)       FLOAT32 mask for the padding of predictions
        plot_metrics (bool): shape (1,)             BOOL    if true the precision/recall curve will be drawn
    
    Returns:
        mAPs (tf.Tensor): shape (thresh, ) FLOAT32 mean Average Precision values
    '''

    precision,recall = precision_recall(tp, conf, nb_gt, maskpad)

    sp = tf.shape(precision)

    mAPs = []

    for i in range(sp[1]):
        ac = auc(precision[:,i],recall[:,i])
        mAPs.append(ac[0])

    if plot_metrics:
        plt.plot(recall[:,0],precision[:,0])
        plt.show()

    return mAPs