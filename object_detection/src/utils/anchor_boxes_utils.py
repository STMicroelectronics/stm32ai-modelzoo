# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np
import tensorflow.keras.backend as K


def get_sizes_ratios(input_shape: tuple = None) -> tuple:
    """
    Returns a tuple of sizes and ratios based on the input_shape.

    Args:
        input_shape (tuple): The input shape of the model in the format (height, width, channels).

    Returns:
        tuple: A tuple of sizes and ratios in the format (sizes, ratios).

    Raises:
        None

    """
    # Define sizes and ratios based on the input_shape
    if input_shape[0] == 192:
        sizes = [[0.26, 0.33], [0.42, 0.49], [0.58, 0.66], [0.74, 0.82], [0.9, 0.98]]
        ratios = [[1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3],
                  [1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3],
                  [1.0, 2.0, 0.5, 1.0 / 3]]
    elif input_shape[0] == 224:
        sizes = [[0.1, 0.16], [0.26, 0.33], [0.42, 0.49], [0.58, 0.66], [0.74, 0.82], [0.9, 0.98]]
        ratios = [[1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3],
                  [1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3],
                  [1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3]]
    else:
        sizes = [[0.1, 0.16], [0.26, 0.33], [0.42, 0.49], [0.58, 0.66], [0.74, 0.82], [0.9, 0.98]]
        ratios = [[1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3],
                  [1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3],
                  [1.0, 2.0, 0.5, 1.0 / 3], [1.0, 2.0, 0.5, 1.0 / 3]]
    # Return the sizes and ratios as a tuple
    return sizes, ratios

def get_sizes_ratios_ssd_v2(input_shape: tuple = None) -> tuple:

    def sizes_creation(target_max_res,base_sizes,t_min_s,res_range,slope):

        # target_max_res : must be in the res_range
        # base_sizes=[[0.26,0.33], [0.42,0.49], [0.58,0.66], [0.74,0.82], [0.9,0.98]]
        # t_min_s = [0.026,0.033]
        # slope = 2
        # res_range = [24,32,52]

        ab_x = affine_search([base_sizes[0][0],t_min_s[0]],res_range,slope) # [a,b,c]
        ab_y = affine_search([base_sizes[0][1],t_min_s[1]],res_range,slope) # [a,b,c]

        arr_res = np.array([1/(target_max_res**slope),1])

        target_max_s = np.array(base_sizes[-1])
        target_min_s = np.stack([ab_x,ab_y]) @ arr_res
        target_len   = len(base_sizes)

        target_sizes = np.linspace(target_min_s,target_max_s,target_len)

        return target_sizes
    
    def affine_search(s,r,slope):

        r = np.array(r)

        R = np.stack([1/(r**slope),np.ones_like(r)],axis=1)

        # knowing that -> R@x = s then : x = R^-1 @ s

        return np.linalg.inv(R) @ s

    fmap_sizes_dict = {'192':[24,12,6,3,2],
                       '224':[28,14,7,4,2],
                       '256':[32,16,8,4,2],
                       '288':[36,18,9,5,3],
                       '320':[40,20,10,5,3],
                       '352':[44,22,11,6,3],
                       '384':[48,24,12,6,3],
                       '416':[52,26,13,7,4]}

    base_sizes = [[0.26,0.33],
                  [0.42,0.49],
                  [0.58,0.66],
                  [0.74,0.82],
                  [0.9,0.98]]

    min_sizes_max_res = [0.06,0.09]

    max_fmap_res = fmap_sizes_dict[str(input_shape[0])][0]

    res_range    = [fmap_sizes_dict['192'][0],fmap_sizes_dict['416'][0]]

    sizes  = sizes_creation(max_fmap_res, base_sizes, min_sizes_max_res, res_range, slope = 5)

    ratios = [[1.0, 2.0, 0.5, 1.0 / 3]]*len(sizes)
    
    # Return the sizes and ratios as a tuple
    return sizes, ratios


def corners2centroids(bbox: tuple) -> list:
    """
    Convert bounding box coordinates from format
    (xmin, ymin, xmax, ymax)
    to format (xc, yc, width, height)

    Parameters:
    bbox (tuple): A tuple containing the coordinates of the bounding box in the format (xmin, ymin, xmax, ymax)

    Returns:
    list: A list containing the coordinates of the bounding box in the format (xc, yc, width, height)
    """
    bbox_cen = []
    xc = bbox[0] + (bbox[2] - bbox[0]) / 2
    yc = bbox[1] + (bbox[3] - bbox[1]) / 2
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    bbox_cen.append(xc)
    bbox_cen.append(yc)
    bbox_cen.append(width)
    bbox_cen.append(height)

    return bbox_cen


def centroids2corners(bbox_cen: list) -> list:
    """
    Convert bounding box coordinates from format (xc, yc, width, height) to format (xmin, ymin, xmax, ymax)

    Parameters:
    bbox_cen (list): A list containing the coordinates of the bounding box in the format (xc, yc, width, height)

    Returns:
    list: A list containing the coordinates of the bounding box in the format (xmin, ymin, xmax, ymax)
    """
    bbox = []

    xmin = bbox_cen[0] - bbox_cen[2] / 2
    ymin = bbox_cen[1] - bbox_cen[3] / 2
    xmax = bbox_cen[0] + bbox_cen[2] / 2
    ymax = bbox_cen[1] + bbox_cen[3] / 2

    bbox.append(xmin)
    bbox.append(ymin)
    bbox.append(xmax)
    bbox.append(ymax)

    return bbox


def centroids2topleft(bbox_cen: list) -> list:
    """
    Convert bounding box coordinates from format (xc, yc, width, height) to format (xmin, ymin, width, height)

    Parameters:
    bbox_cen (list): A list containing the coordinates of the bounding box in the format (xc, yc, width, height)

    Returns:
    list: A list containing the coordinates of the bounding box in the format (xmin, ymin, width, height)
    """
    bbox = []

    xmin = bbox_cen[0] - bbox_cen[2] / 2
    ymin = bbox_cen[1] - bbox_cen[3] / 2

    bbox.append(xmin)
    bbox.append(ymin)
    bbox.append(bbox_cen[2])
    bbox.append(bbox_cen[3])

    return bbox


def check_box(box: list, src_w: int, src_h: int) -> tuple:
    """
    Check box coordinates

    Parameters:
    box (list): A list containing the coordinates of the bounding box in the format (xmin, ymin, xmax, ymax)
    src_w (int): The width of the source image
    src_h (int): The height of the source image

    Returns:
    tuple: A tuple containing a boolean value indicating if the box is valid and a list containing the corrected coordinates of the bounding box in the format (xmin, ymin, xmax, ymax)
    """
    valid = True

    xmin = box[0]
    ymin = box[1]
    xmax = box[2]
    ymax = box[3]

    if xmin < 0:
        xmin = 0
    if xmax >= src_w:
        xmax = src_w - 1
    if ymin < 0:
        ymin = 0
    if ymax >= src_h:
        ymax = src_h - 1
    if (xmin > xmax) or (ymin > ymax):
        xmin = 0
        ymin = 0
        xmax = 0
        ymax = 0
        valid = False
    return valid, [xmin, ymin, xmax, ymax]


def interval_overlap(interval_a, interval_b):
    """
    Find overlap between two intervals
    Arguments:
        interval_a: [x1, x2]
        interval_b: [x3, x4]
    Returns:
        overlapped distance
    """
    x1, x2 = interval_a
    x3, x4 = interval_b
    if x3 < x1:
        if x4 < x1:
            return 0
        else:
            return min(x2, x4) - x1
    else:
        if x2 < x3:
            return 0
        else:
            return min(x2, x4) - x3


def bbox_iou(box1, box2):
    """
    Find IoU between two boxes
    Arguments:
        box1 = [xmin, ymin, xmax, ymax]
        box2 = [xmin, ymin, xmax, ymax]
    Returns:
        iou similarity
    """
    intersect_w = interval_overlap([box1[0], box1[2]], [box2[0], box2[2]])
    intersect_h = interval_overlap([box1[1], box1[3]], [box2[1], box2[3]])
    intersect = intersect_w * intersect_h
    w1, h1 = box1[2] - box1[0], box1[3] - box1[1]
    w2, h2 = box2[2] - box2[0], box2[3] - box2[1]
    union = w1 * h1 + w2 * h2 - intersect
    return float(intersect) / union


def iou_matrix(boxes1, boxes2):
    """
    Compute IoU similarity matrix between set of m boxes1 and n boxes2
    Arguments:
        boxes1: [m, 4], 4 elements of  [xmin, ymin, xmax, ymax]
        boxes2: [n, 4], 4 elements of  [xmin, ymin, xmax, ymax]
    Returns:
        matrix of mxn iou metrics
    """
    m = len(boxes1)
    n = len(boxes2)
    iou_matrix = np.zeros((m, n), dtype=float)
    for i in range(m):
        for j in range(n):
            iou_matrix[i, j] = bbox_iou(boxes1[i], boxes2[j])

    return iou_matrix


def gen_anchors(fmap, img_width, img_height, sizes,
                ratios, clip=True, normalize=True):
    """
    Generate anchor boxes for a feature map
    sizes = [s1, s2, ..., sm], ratios = [r1, r2, ..., rn], n_anchors = n + m - 1, only consider [s1, r1], [s1, r2], ..., [s1, rn], [s2, r1], ..., [sm, r1]
    Arguments:
        fmap: feature map
        img_width: image width
        img_height: image height
        sizes: [s1, s2, ..., sm]
        ratios: [r1, r2, ..., rn]
        clip: clip to image boundary
        normalize: normalize to image sizes
    Returns:
        list of anchor boxes
    """
    _, fmap_height, fmap_width, _ = fmap.shape
    fmap_height = int(fmap_height)
    fmap_width = int(fmap_width)

    res_img = min(img_width, img_height)
    n_anchors = len(sizes) + len(ratios) - 1

    # compute the box widths and heights for all anchor boxes
    wh_list = []
    for ratio in ratios:
        box_w = res_img * sizes[0] * np.sqrt(ratio)
        box_h = res_img * sizes[0] / np.sqrt(ratio)
        wh_list.append((box_w, box_h))

    for i in range(len(sizes)):
        if i == 0:
            continue
        box_w = res_img * sizes[i] * np.sqrt(ratios[0])
        box_h = res_img * sizes[i] / np.sqrt(ratios[0])
        wh_list.append((box_w, box_h))

    wh_list = np.asarray(wh_list)

    step_height = img_height / fmap_height
    step_width = img_width / fmap_width

    offset_height = 0.5
    offset_width = 0.5

    # compute the grid of anchor box center points
    cy = np.linspace(
        offset_height * step_height,
        (offset_height + fmap_height - 1) * step_height,
        fmap_height)
    cx = np.linspace(
        offset_width * step_width,
        (offset_width + fmap_width - 1) * step_width,
        fmap_width)
    cx_grid, cy_grid = np.meshgrid(cx, cy)
    cx_grid = np.expand_dims(cx_grid, -1)
    cy_grid = np.expand_dims(cy_grid, -1)

    # anchors: (fmap_height, fmap_width, n_anchors, 4), 4 elements including
    # (cx, cy, w, h)
    anchors = np.zeros((fmap_height, fmap_width, n_anchors, 4))

    anchors[:, :, :, 0] = np.tile(cx_grid, (1, 1, n_anchors))  # set cx
    anchors[:, :, :, 1] = np.tile(cy_grid, (1, 1, n_anchors))  # set cy
    anchors[:, :, :, 2] = wh_list[:, 0]  # set w
    anchors[:, :, :, 3] = wh_list[:, 1]  # set h

    # convert (cx, cy, w, h) to (xmin, ymin, xmax, ymax)
    anchors1 = np.copy(anchors).astype(np.float)
    anchors1[:, :, :, 0] = anchors[:, :, :, 0] - \
                           anchors[:, :, :, 2] / 2.0  # set xmin
    anchors1[:, :, :, 1] = anchors[:, :, :, 1] - \
                           anchors[:, :, :, 3] / 2.0  # set ymin
    anchors1[:, :, :, 2] = anchors[:, :, :, 0] + \
                           anchors[:, :, :, 2] / 2.0  # set xmax
    anchors1[:, :, :, 3] = anchors[:, :, :, 1] + \
                           anchors[:, :, :, 3] / 2.0  # set ymax

    # clip the coordinates to lie within the image boundaries
    if clip:
        x_coords = anchors1[:, :, :, [0, 2]]
        x_coords[x_coords >= img_width] = img_width - 1
        x_coords[x_coords < 0] = 0
        anchors1[:, :, :, [0, 2]] = x_coords

        y_coords = anchors1[:, :, :, [1, 3]]
        y_coords[y_coords >= img_height] = img_height - 1
        y_coords[y_coords < 0] = 0
        anchors1[:, :, :, [1, 3]] = y_coords

    if normalize:
        anchors1[:, :, :, [0, 2]] /= img_width
        anchors1[:, :, :, [1, 3]] /= img_height

    # expand for batch size dimension
    #anchors1 = np.expand_dims(anchors1, axis=0)
    #anchors1 = K.tile(K.constant(anchors1, dtype='float32'),
    #                  (K.shape(fmap)[0], 1, 1, 1, 1))

    return anchors1


def gen_anchors_fmap(fmap_size, img_width, img_height,
                     sizes, ratios, clip=True, normalize=True):
    """
    Generate anchor boxes for a given feature map size
    Arguments:
        fmap_size: feature map size
        img_width: image width
        img_height: image height
        sizes: [s1, s2, ..., sm]
        ratios: [r1, r2, ..., rn]
        clip: clip to image boundary
        normalize: normalize to image sizes
    Returns:
        list of anchor boxes
    """
    fmap_height, fmap_width = fmap_size
    fmap_height = int(fmap_height)
    fmap_width = int(fmap_width)

    res_img = min(img_width, img_height)
    n_anchors = len(sizes) + len(ratios) - 1

    # compute the box widths and heights for all anchor boxes
    wh_list = []
    for ratio in ratios:
        box_w = res_img * sizes[0] * np.sqrt(ratio)
        box_h = res_img * sizes[0] / np.sqrt(ratio)
        wh_list.append((box_w, box_h))

    for i in range(len(sizes)):
        if i == 0:
            continue
        box_w = res_img * sizes[i] * np.sqrt(ratios[0])
        box_h = res_img * sizes[i] / np.sqrt(ratios[0])
        wh_list.append((box_w, box_h))

    wh_list = np.asarray(wh_list)

    step_height = img_height / fmap_height
    step_width = img_width / fmap_width

    offset_height = 0.5
    offset_width = 0.5

    # compute the grid of anchor box center points
    cy = np.linspace(
        offset_height * step_height,
        (offset_height + fmap_height - 1) * step_height,
        fmap_height)
    cx = np.linspace(
        offset_width * step_width,
        (offset_width + fmap_width - 1) * step_width,
        fmap_width)
    cx_grid, cy_grid = np.meshgrid(cx, cy)
    cx_grid = np.expand_dims(cx_grid, -1)
    cy_grid = np.expand_dims(cy_grid, -1)

    # anchors: (fmap_height, fmap_width, n_anchors, 4), 4 elements including
    # (cx, cy, w, h)
    anchors = np.zeros((fmap_height, fmap_width, n_anchors, 4))

    anchors[:, :, :, 0] = np.tile(cx_grid, (1, 1, n_anchors))  # set cx
    anchors[:, :, :, 1] = np.tile(cy_grid, (1, 1, n_anchors))  # set cy
    anchors[:, :, :, 2] = wh_list[:, 0]  # set w
    anchors[:, :, :, 3] = wh_list[:, 1]  # set h

    # convert (cx, cy, w, h) to (xmin, ymin, xmax, ymax)
    anchors1 = np.copy(anchors).astype(np.float)
    anchors1[:, :, :, 0] = anchors[:, :, :, 0] - \
                           anchors[:, :, :, 2] / 2.0  # set xmin
    anchors1[:, :, :, 1] = anchors[:, :, :, 1] - \
                           anchors[:, :, :, 3] / 2.0  # set ymin
    anchors1[:, :, :, 2] = anchors[:, :, :, 0] + \
                           anchors[:, :, :, 2] / 2.0  # set xmax
    anchors1[:, :, :, 3] = anchors[:, :, :, 1] + \
                           anchors[:, :, :, 3] / 2.0  # set ymax

    # clip the coordinates to lie within the image boundaries
    if clip:
        x_coords = anchors1[:, :, :, [0, 2]]
        x_coords[x_coords >= img_width] = img_width - 1
        x_coords[x_coords < 0] = 0
        anchors1[:, :, :, [0, 2]] = x_coords

        y_coords = anchors1[:, :, :, [1, 3]]
        y_coords[y_coords >= img_height] = img_height - 1
        y_coords[y_coords < 0] = 0
        anchors1[:, :, :, [1, 3]] = y_coords

    if normalize:
        anchors1[:, :, :, [0, 2]] /= img_width
        anchors1[:, :, :, [1, 3]] /= img_height

    return anchors1


def match_bipartite_greedy(weight_matrix):
    """
    Match bipartite greedy
    Arguments:
        weight_matrix: IoU matrix between anchor boxes and ground truth bounding boxes
    Returns:
        matches: matched index
    """
    weight_matrix = np.copy(weight_matrix)
    num_ground_truth_boxes = weight_matrix.shape[0]
    all_gt_indices = list(range(num_ground_truth_boxes))

    matches = np.zeros(num_ground_truth_boxes, dtype=np.int)

    for _ in range(num_ground_truth_boxes):
        anchor_indices = np.argmax(weight_matrix, axis=1)
        overlaps = weight_matrix[all_gt_indices, anchor_indices]
        ground_truth_index = np.argmax(overlaps)
        anchor_index = anchor_indices[ground_truth_index]
        matches[ground_truth_index] = anchor_index

        weight_matrix[ground_truth_index] = 0
        weight_matrix[:, anchor_index] = 0

    return matches


def match_multi(weight_matrix, threshold):
    """
    Match multi
    Arguments:
        weight_matrix: IoU matrix between anchor boxes and ground truth bounding boxes
        threshold: IoU threshold
    Returns:
        gt_indices_thresh_met, anchor_indices_thresh_met
    """
    num_anchor_boxes = weight_matrix.shape[1]
    all_anchor_indices = list(range(num_anchor_boxes))

    ground_truth_indices = np.argmax(weight_matrix, axis=0)
    overlaps = weight_matrix[ground_truth_indices, all_anchor_indices]

    anchor_indices_thresh_met = np.nonzero(overlaps >= threshold)[0]
    gt_indices_thresh_met = ground_truth_indices[anchor_indices_thresh_met]

    return gt_indices_thresh_met, anchor_indices_thresh_met


def intersection_area(boxes1, boxes2):
    """
    Get intersection areas between two sets of boxes
    Arguments:
        boxes1, boxes2: two sets of boxes in the format [xmin, ymin, xmax, ymax]
    Returns:
        matrix of intersection areas between two sets of boxes
    """
    m = boxes1.shape[0]  # The number of boxes in `boxes1`
    n = boxes2.shape[0]  # The number of boxes in `boxes2`

    # Set the correct coordinate indices for the respective formats.
    xmin = 0
    ymin = 1
    xmax = 2
    ymax = 3

    min_xy = np.maximum(np.tile(np.expand_dims(boxes1[:, [xmin, ymin]], axis=1), reps=(
        1, n, 1)), np.tile(np.expand_dims(boxes2[:, [xmin, ymin]], axis=0), reps=(m, 1, 1)))

    max_xy = np.minimum(np.tile(np.expand_dims(boxes1[:, [xmax, ymax]], axis=1), reps=(
        1, n, 1)), np.tile(np.expand_dims(boxes2[:, [xmax, ymax]], axis=0), reps=(m, 1, 1)))

    side_lengths = np.maximum(0, max_xy - min_xy)

    return side_lengths[:, :, 0] * side_lengths[:, :, 1]


def iou(boxes1, boxes2):
    """
    Computes the intersection-over-union similarity (also known as Jaccard similarity)
    of two sets of axis-aligned 2D rectangular boxes.
    Arguments:
        boxes1, boxes2: two sets of boxes in the format [xmin, ymin, xmax, ymax]
    Returns:
        IoU matrix
    """
    if boxes1.ndim > 2:
        raise ValueError(
            "boxes1 must have rank either 1 or 2, but has rank {}.".format(
                boxes1.ndim))
    if boxes2.ndim > 2:
        raise ValueError(
            "boxes2 must have rank either 1 or 2, but has rank {}.".format(
                boxes2.ndim))

    if boxes1.ndim == 1:
        boxes1 = np.expand_dims(boxes1, axis=0)
    if boxes2.ndim == 1:
        boxes2 = np.expand_dims(boxes2, axis=0)

    if not (boxes1.shape[1] == boxes2.shape[1] == 4):
        raise ValueError(
            "All boxes must consist of 4 coordinates, but the boxes in `boxes1` and `boxes2` have {} and {} coordinates, respectively.".format(
                boxes1.shape[1],
                boxes2.shape[1]))

    intersection_areas = intersection_area(boxes1, boxes2)

    m = boxes1.shape[0]  # The number of boxes in `boxes1`
    n = boxes2.shape[0]  # The number of boxes in `boxes2`

    xmin = 0
    ymin = 1
    xmax = 2
    ymax = 3

    boxes1_areas = np.tile(np.expand_dims(
        (boxes1[:, xmax] - boxes1[:, xmin]) * (boxes1[:, ymax] - boxes1[:, ymin]), axis=1), reps=(1, n))
    boxes2_areas = np.tile(np.expand_dims(
        (boxes2[:, xmax] - boxes2[:, xmin]) * (boxes2[:, ymax] - boxes2[:, ymin]), axis=0), reps=(m, 1))

    union_areas = boxes1_areas + boxes2_areas - intersection_areas

    return intersection_areas / union_areas


def match_gt_anchors(fmap_sizes, img_width, img_height, sizes, ratios, groundtruth_labels,
                     n_classes, clip=True, normalize=True, pos_iou_threshold=0.5, neg_iou_limit=0.3):
    """
    Assign ground truth bouding boxes labels to anchor boxes for training
    Arguments:
        fmap_sizes (list): list of feature map size, i.e. [(32, 32), (16, 16), ...]
        img_width: origin image width
        img_height: origin image height
        sizes, ratios: size and aspect ratio for generating anchor boxes
        groundtruth_labels (list): A python list of length `batch_size` that contains one 2D Numpy array
                    for each batch image. Each such array has `k` rows for the `k` ground truth bounding boxes belonging
                    to the respective image, and the data for each ground truth bounding box has the format
                    `(class_id, xmin, ymin, xmax, ymax)` (i.e. the 'corners' coordinate format), and `class_id` must be
                    an integer greater than 0 for all boxes as class ID 0 is reserved for the background class
        n_classes: number of object categories, +1 for taking into account background
        clip: clip boxes to image size
        normalize: normalize coordinate of anchor boxes
        pos_iou_threshold: IoU threshold to define as positive anchor boxes
        neg_iou_limit: IoU threshold to define as negative anchor boxes
    Returns:
        a tensor of shape [None, #boxes, n_classes + 1 + 4 + 4]
    """
    # list of anchors generated for each feature map
    bboxes_list = []
    for i in range(len(fmap_sizes)):
        bboxes_fmap = gen_anchors_fmap(
            fmap_sizes[i],
            img_width,
            img_height,
            sizes[i],
            ratios[i],
            clip,
            normalize)
        bboxes_list.append(bboxes_fmap)

    # indices in groundtruth_labels
    class_id = 0
    xmin = 1
    ymin = 2
    xmax = 3
    ymax = 4

    background_id = 0
    batch_size = len(groundtruth_labels)

    # generate template for truths
    bboxes_batch = []
    for bboxes in bboxes_list:
        # expand dimension for batch size
        bboxes = np.expand_dims(bboxes, axis=0)
        bboxes = np.tile(bboxes, (batch_size, 1, 1, 1, 1))
        bboxes = np.reshape(bboxes, (batch_size, -1, 4))
        bboxes_batch.append(bboxes)

    bbox_truths = np.concatenate(bboxes_batch, axis=1)
    cls_truths = np.zeros((batch_size, bbox_truths.shape[1], n_classes + 1))

    # shape (batch_size, #boxes, 1 + n_classes + 4 + 4)
    truths = np.concatenate((cls_truths, bbox_truths, bbox_truths), axis=2)

    # begin assigning
    truths[:, :, background_id] = 1
    n_boxes = truths.shape[1]
    class_vectors = np.eye(n_classes + 1)

    for i in range(batch_size):
        if groundtruth_labels[i].size == 0:
            continue

        labels = groundtruth_labels[i].astype(np.float)

        if normalize:
            labels[:, [ymin, ymax]] /= img_height
            labels[:, [xmin, xmax]] /= img_width

        classes_one_hot = class_vectors[labels[:, class_id].astype(np.int)]
        labels_one_hot = np.concatenate(
            [classes_one_hot, labels[:, [xmin, ymin, xmax, ymax]]], axis=-1)

        # calculate iou matrix between groundtruth boxes and anchor boxes
        # (#groundtruth_boxes, #anchor_boxes)
        similarities = iou(
            labels[:, [xmin, ymin, xmax, ymax]], truths[i, :, -8:-4])

        bipartite_matches = match_bipartite_greedy(weight_matrix=similarities)

        truths[i, bipartite_matches, :-4] = labels_one_hot

        similarities[:, bipartite_matches] = 0

        # Get all matches that satisfy the IoU threshold.
        matches = match_multi(
            weight_matrix=similarities,
            threshold=pos_iou_threshold)

        # Write the ground truth data to the matched anchor boxes.
        truths[i, matches[1], :-4] = labels_one_hot[matches[0]]

        # Set the columns of the matched anchor boxes to zero to indicate that
        # they were matched.
        similarities[:, matches[1]] = 0

        max_background_similarities = np.amax(similarities, axis=0)
        neutral_boxes = np.nonzero(
            max_background_similarities >= neg_iou_limit)[0]
        truths[i, neutral_boxes, background_id] = 0

    # (gt - anchor) for all four coordinates
    truths[:, :, [-8, -7, -6, -5]] -= truths[:, :, [-4, -3, -2, -1]]
    # (xmin(gt) - xmin(anchor)) / w(anchor), (xmax(gt) - xmax(anchor)) / w(anchor)
    truths[:, :, [-8, -6]
    ] /= np.expand_dims(truths[:, :, -2] - truths[:, :, -4], axis=-1)
    # (ymin(gt) - ymin(anchor)) / h(anchor), (ymax(gt) - ymax(anchor)) / h(anchor)
    truths[:, :, [-7, -5]
    ] /= np.expand_dims(truths[:, :, -1] - truths[:, :, -3], axis=-1)

    return truths
