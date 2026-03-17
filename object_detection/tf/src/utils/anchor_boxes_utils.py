# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import numpy as np


def get_sizes_ratios_ssd_v1(input_shape: tuple = None) -> tuple:
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

    def _sizes_creation(target_max_res,base_sizes,t_min_s,res_range,slope):

        # target_max_res : must be in the res_range
        # base_sizes=[[0.26,0.33], [0.42,0.49], [0.58,0.66], [0.74,0.82], [0.9,0.98]]
        # t_min_s = [0.026,0.033]
        # slope = 2
        # res_range = [24,32,52]

        ab_x = _affine_search([base_sizes[0][0],t_min_s[0]],res_range,slope) # [a,b,c]
        ab_y = _affine_search([base_sizes[0][1],t_min_s[1]],res_range,slope) # [a,b,c]

        arr_res = np.array([1/(target_max_res**slope),1])

        target_max_s = np.array(base_sizes[-1])
        target_min_s = np.stack([ab_x,ab_y]) @ arr_res
        target_len   = len(base_sizes)

        target_sizes = np.linspace(target_min_s,target_max_s,target_len)

        return target_sizes
    
    def _affine_search(s,r,slope):

        r = np.array(r)

        R = np.stack([1/(r**slope),np.ones_like(r)],axis=1)

        # knowing that -> R@x = s then : x = R^-1 @ s

        return np.linalg.inv(R) @ s
    
    fmap_sizes_dict = {'192': [24, 12, 6, 3,2],
                       '224': [28, 14, 7, 4,2],
                       '256': [32, 16, 8, 4,2],
                       '288': [36, 18, 9, 5,3],
                       '320': [40, 20, 10, 5,3],
                       '352': [44, 22, 11, 6,3],
                       '384': [48, 24, 12, 6,3],
                       '416': [52, 26, 13, 7,4]}

    # Check that the model input shape is supported
    if str(input_shape[0]) not in fmap_sizes_dict or str(input_shape[1]) not in fmap_sizes_dict:
        supported_shapes = [(int(k), int(k), 3) for k in fmap_sizes_dict.keys()]        
        raise ValueError(f"\nInput shape ({input_shape[1]}, {input_shape[0]}, 3) "
                         "is not supported for `ssd_mobilenet_v2_fpnlite` models.\n"
                         f"Supported shapes: {supported_shapes}\n"
                         "Please check the 'training.model' section of your configuration file.")
        
    base_sizes = [[0.26, 0.33],
                  [0.42, 0.49],
                  [0.58, 0.66],
                  [0.74, 0.82],
                  [0.90, 0.98]]

    min_sizes_max_res = [0.06, 0.09]

    max_fmap_res = fmap_sizes_dict[str(input_shape[0])][0]
    
    res_range = [fmap_sizes_dict['192'][0],fmap_sizes_dict['416'][0]]
    
    sizes  = _sizes_creation(max_fmap_res, base_sizes, min_sizes_max_res, res_range, slope = 5)

    ratios = [[1.0, 2.0, 0.5, 1.0 / 3]]*len(sizes)

    # Return the sizes and ratios as a tuple
    return sizes, ratios


def get_fmap_sizes(model_type, input_shape):
    
    fmap_sizes_dict = {
            'st_ssd_mobilenet_v1': {
                    '192': [24, 12, 6, 3, 1],
                    '224': [32, 16, 8, 4, 2, 1],
                    '256': [32, 16, 8, 4, 2, 1]
            },
            'ssd_mobilenet_v2_fpnlite': {
                    '192': [24, 12, 6, 3, 2],
                    '224': [28, 14, 7, 4, 2],
                    '256': [32, 16, 8, 4, 2],
                    '288': [36, 18, 9, 5, 3],
                    '320': [40, 20, 10, 5, 3],
                    '352': [44, 22, 11, 6, 3],
                    '384': [48, 24, 12, 6, 3],
                    '416': [52, 26, 13, 7, 4]
            }
    }
  
    fmap_widths  = np.array(fmap_sizes_dict[model_type][str(input_shape[0])])
    fmap_heights = np.array(fmap_sizes_dict[model_type][str(input_shape[1])])

    fmap_sizes = None
    if model_type == 'st_ssd_mobilenet_v1':
        fmap_sizes = np.stack([fmap_widths, fmap_heights],axis=-1)
    elif model_type == 'ssd_mobilenet_v2_fpnlite':
        fmap_sizes = np.stack([fmap_widths, fmap_heights],axis=-1)
    
    return fmap_sizes


def gen_anchors(fmap, img_width, img_height, sizes, ratios, normalize=True, clip=False):
    """
    Generate anchor boxes for a feature map
    sizes = [s1, s2, ..., sm], ratios = [r1, r2, ..., rn], n_anchors = n + m - 1, only consider [s1, r1], [s1, r2], ..., [s1, rn], [s2, r1], ..., [sm, r1]
    Arguments:
        fmap: feature map
        img_width: image width
        img_height: image height
        sizes: [s1, s2, ..., sm]
        ratios: [r1, r2, ..., rn]
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
    anchors1 = np.copy(anchors).astype(np.float32)
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


def _gen_anchors_fmap(fmap_size, img_width, img_height,
                     sizes, ratios, normalize=True, clip=False):
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
    anchors1 = np.copy(anchors).astype(np.float32)
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


def get_anchor_boxes(fmap_sizes,
                     image_size,
                     sizes=None,
                     ratios=None,
                     normalize=True,
                     clip_boxes=False):

    anchor_boxes = []
    for i in range(len(fmap_sizes)):
        bboxes_fmap = _gen_anchors_fmap(
            fmap_sizes[i],
            image_size[0],
            image_size[1],
            sizes[i],
            ratios[i],
            normalize=normalize,
            clip=clip_boxes)
        
        dims = bboxes_fmap.shape
        anchor_boxes += np.reshape(bboxes_fmap, (dims[0] * dims[1] * dims[2], 4)).tolist()

    return np.array(anchor_boxes, dtype=np.float32)
