# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from typing import Tuple, Dict
import numpy as np
from hydra.core.hydra_config import HydraConfig
from anchor_boxes_utils import bbox_iou
from object_det_metrics.lib.BoundingBox import BoundingBox
from object_det_metrics.lib.BoundingBoxes import BoundingBoxes
from object_det_metrics.lib.Evaluator import Evaluator
from object_det_metrics.lib.utils import BBFormat, BBType, CoordinatesType
from typing import List, Union


def decode_predictions(predictions: np.ndarray, normalize: bool = True, org_img_height: int = None,
                       org_img_width: int = None) -> np.ndarray:
    """
    Retrieve object bounding box coordinates from predicted offsets and anchor box coordinates.

    Args:
        predictions (np.ndarray): The output of an SSD-based human detection model, a tensor of [None, #boxes, 1+n_classes+4+4].
        normalize (bool): Whether the coordinates are normalized or not.
        org_img_height (int): The original image height, used if normalize=True.
        org_img_width (int): The original image width, used if normalize=True.

    Returns:
        predictions_decoded_raw (np.ndarray): The object bounding boxes and categories, a tensor of [None, #boxes, 1+n_classes+4].
    """
    predictions_decoded_raw = np.copy(predictions[:, :, :-4])

    # Unnormalize the offsets with the height and width of anchor boxes
    predictions_decoded_raw[:, :, [-4, -2]] *= np.expand_dims(predictions[:, :, -2] - predictions[:, :, -4], axis=-1)
    predictions_decoded_raw[:, :, [-3, -1]] *= np.expand_dims(predictions[:, :, -1] - predictions[:, :, -3], axis=-1)
    predictions_decoded_raw[:, :, -4:] += predictions[:, :, -4:]

    if normalize:
        predictions_decoded_raw[:, :, [-4, -2]] *= org_img_width
        predictions_decoded_raw[:, :, [-3, -1]] *= org_img_height

    return predictions_decoded_raw


def non_max_suppression(preds_decoded, nms_thresh=0.45, confidence_thresh=0.5):
    """
    Non-maximum suppression, removing overlapped bounding boxes based on IoU metric and keeping bounding boxes with the highest score
    Arguments:
        preds_decoded: return of decode_predictions function, a tensor of [None, #boxes, 1+n_classes+4]
        nms_thresh: IoU threshold to remove overlapped bounding boxes, a float between 0 and 1
        confidence_thresh: minimum score to keep bounding boxes, a float between 0 and 1
    Returns:
        final_preds: detection results after non-maximum suppression
    """
    n_boxes, batch_size, n_classes_bg = preds_decoded.shape[1:]

    final_preds = {}

    for b_item in preds_decoded:  # loop for each batch item
        for c in range(1, n_classes_bg):  # loop for each object category
            single_class = b_item[:,
                           [c, -4, -3, -2, -1]]  # retrieve predictions [score, xmin, ymin, xmax, ymax] for category c
            threshold_met = single_class[
                single_class[:, 0] > confidence_thresh]  # filter predictions with minimum confidence score threshold
            if threshold_met.shape[0] > 0:
                # sort confidence score in descending order
                sorted_indices = np.argsort(-threshold_met[:, 0])
                for i, index_i in enumerate(sorted_indices):  # loop for bounding boxes in order of highest score
                    if threshold_met[index_i, 0] == 0:  # verify if this box was processed
                        continue
                    box_i = threshold_met[index_i, 1:]  # get [xmin, ymin, xmax, ymax] of box_i
                    for index_j in sorted_indices[i + 1:]:  # loop for remaining bounding boxes
                        box_j = threshold_met[index_j, 1:]  # get [xmin, ymin, xmax, ymax] of box_j
                        iou = calculate_iou(box_i, box_j)
                        if iou > nms_thresh:
                            threshold_met[index_j, 0] = 0  # mark box_j as processed
                selected_boxes = threshold_met[threshold_met[:, 0] > 0]  # keep only boxes with non-zero score
                final_preds[(b_item, c)] = selected_boxes

    return final_preds


def corners_to_center_box_coords(x_min, x_max, y_min, y_max, image_size=None, relative=None):
    """
    Converts a predicted bounding box from (class_id, x_min, y_min, x_max, y_max) format 
    to (class_id, x_center, y_center, w, h) or (class_id, x_r, y_r, w_r, h_r) format.

    Args:
        image (np.ndarray): The input image.
        box (List[Union[int, float]]): The predicted bounding box in (class_id, x_min, y_min, x_max, y_max) format.
        relative (bool): Whether to return the bounding box coordinates as relative to the image size.

    Returns:
        The predicted bounding box in (class_id, x_center, y_center, w, h) or (class_id, x_r, y_r, w_r, h_r) format.
    """
    width, height = image_size

    w = x_max - x_min
    h = y_max - y_min
    x_center = x_min + w / 2
    y_center = y_min + h / 2

    if relative:
        x_center /= width
        y_center /= height
        w /= width
        h /= height

    return x_center, y_center, w, h


def do_nms(preds_decoded, nms_thresh=0.45, confidence_thresh=0.5):
    """
    Non-maximum suppression, removing overlapped bounding boxes based on IoU metric and keeping bounding boxes with the highest score
    Arguments:
        preds_decoded: return of decode_predictions function, a tensor of [None, #boxes, 1+n_classes+4]
        nms_thresh: IoU threshold to remove overlapped bounding boxes, a float between 0 and 1
        confidence_thresh: minimum score to keep bounding boxes, a float between 0 and 1
    Returns:
        final_preds: detection results after non-maximum suppression
    """
    n_classes_bg = int(preds_decoded.shape[2]) - 4

    final_preds = dict()

    for b_item in preds_decoded:  # loop for each batch item
        for c in range(1, n_classes_bg):  # loop for each object category
            single_class = b_item[:,
                           [c, -4, -3, -2, -1]]  # retrieve predictions [score, xmin, ymin, xmax, ymax] for category c
            threshold_met = single_class[
                single_class[:, 0] > confidence_thresh]  # filter predictions with minimum confidence score threshold
            if threshold_met.shape[0] > 0:
                # sort confidence score in descending order
                sorted_indices = np.argsort([-elm[0] for elm in threshold_met])
                for i in range(len(sorted_indices)):  # loop for bounding boxes in order of highest score
                    index_i = sorted_indices[i]
                    if threshold_met[index_i, 0] == 0:  # verify if this box was processed
                        continue
                    box_i = threshold_met[index_i, -4:]  # get [xmin, ymin, xmax, ymax] of box_i
                    for j in range(i + 1, len(sorted_indices)):
                        index_j = sorted_indices[j]
                        if threshold_met[index_j, 0] == 0:  # verify if this box was processed
                            continue
                        box_j = threshold_met[index_j, -4:]  # get [xmin, ymin, xmax, ymax] of box_j
                        if bbox_iou(box_i,
                                    box_j) >= nms_thresh:  # check if two boxes are overlapped based on IoU metric
                            threshold_met[index_j, 0] = 0  # if Yes, remove bounding box with smaller confidence score
                threshold_met = threshold_met[threshold_met[:, 0] > 0]
            final_preds[c] = threshold_met  # detection results after non-maximum suppression of object category c
    
    return final_preds


def postprocess_predictions(predictions: Dict[str, List[Tuple[float, float, float, float, float]]],
                            image_size: int = None,
                            nms_thresh: float = 0.5,
                            confidence_thresh: float = 0.5) -> Dict[str, List[Tuple[float, float, float, float]]]:
    """
    Postprocesses the predictions to filter out weak and overlapping bounding boxes.

    Args:
        predictions: A dictionary of predictions for each class.
        height: The height of the original image.
        width: The width of the original image.
        nms_thresh: The IoU threshold for non-maximum suppression.
        confidence_thresh: The confidence threshold for filtering out weak predictions.

    Returns:
        A dictionary of filtered predictions for each class.
    """

    predicted_scores, predicted_boxes, predicted_anchors = predictions
    predictions = np.concatenate([predicted_scores, predicted_boxes, predicted_anchors], axis=2)

    preds_decoded = decode_predictions(predictions, normalize=True, 
                                       org_img_height=image_size[1], org_img_width=image_size[0])
    final_preds = do_nms(preds_decoded, nms_thresh=float(nms_thresh),
                         confidence_thresh=float(confidence_thresh))
    return final_preds
