# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import io
import os
import time
import math
from typing import Tuple, Dict
import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as k
import tqdm
from anchor_boxes_utils import bbox_iou
from hydra.core.hydra_config import HydraConfig
from object_det_metrics.lib.BoundingBox import BoundingBox
from object_det_metrics.lib.BoundingBoxes import BoundingBoxes
from object_det_metrics.lib.Evaluator import Evaluator
from object_det_metrics.lib.utils import BBFormat, BBType, CoordinatesType
from typing import List, Union



def check(va: str) -> float:
    """
    Checks if a value is infinite or NaN and returns 0 if it is.

    Args:
        va (str): The value to check.

    Returns:
        The value as a float, or 0 if the value is infinite or NaN.
    """
    if va in ["inf", "-inf", "NaN", "nan"] or math.isnan(float(va)):
        return 0
    else:
        return float(va)



def calculate_iou(box_i, box_j):
    """
    Calculate intersection over union (IoU) of two bounding boxes
    Arguments:
        box_i: [xmin, ymin, xmax, ymax] of box i
        box_j: [xmin, ymin, xmax, ymax] of box j
    Returns:
        iou: IoU of box i and box j
    """
    x1, y1, x2, y2 = box_i
    x3, y3, x4, y4 = box_j
    xi1, yi1 = max(x1, x3), max(y1, y3)
    xi2, yi2 = min(x2, x4), min(y2, y4)
    inter_area = max(xi2 - xi1, 0) * max(yi2 - yi1, 0)
    box_i_area = (x2 - x1) * (y2 - y1)
    box_j_area = (x4 - x3) * (y4 - y3)
    union_area = box_i_area + box_j_area - inter_area
    iou = inter_area / union_area
    return iou


def relu6(x: tf.Tensor) -> tf.Tensor:
    """
    Computes the Rectified Linear Unit 6 (ReLU6) activation function.

    Args:
        x: A tensor.

    Returns:
        A tensor with ReLU6 applied element-wise.
    """

    # Apply ReLU activation with a maximum value of 6.0
    return k.relu(x, max_value=6.0)



def calculate_map(ap_classes: List[float], ap_classes_names: List[str]) -> float:
    """
    Prints the AP for each class and calculates the mean average precision (mAP).

    Args:
        ap_classes (List[float]): List of AP values.
        ap_classes_names (List[str]): List of class names.

    Returns:
        float: Mean average precision (mAP).
    """
    # Initialize the mAP to zero
    map = 0

    # Loop through each class and print the AP
    for rank, av_p in enumerate(ap_classes):
        map += av_p * 100

    # Calculate the mAP
    map /= len(ap_classes)

    # Return the mAP
    return round(map, 2)

