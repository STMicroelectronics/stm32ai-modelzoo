# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import numpy as np
import random
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

def convert_tiny_yolo_v2_to_iaa(gt_labels_list):
    '''
    Convert ground truth bounding boxes to imgaug BoundingBox format to use imgaug for data augmentation
    Arguments:                                                                   
        gt_labels_list: a list of ground truth bounding boxes in the format of abs [[(xmin, ymin, xmax, ymax, class_id), ...], ...]
    Returns:
        gt_labels_list_iaa: a list of imgaug BoundingBoxes [[BoundingBox(xmin, ymin, xmax, ymax, class_id), ...], ...]
    '''
    gt_labels_list_iaa = []
    for i in range(gt_labels_list.shape[0]):
        bbs = []
        for j in range(gt_labels_list[i].shape[0]):
            bb = BoundingBox(x1=gt_labels_list[i][j, 0],
                             y1=gt_labels_list[i][j, 1],
                             x2=gt_labels_list[i][j, 2],
                             y2=gt_labels_list[i][j, 3],
                             label=gt_labels_list[i][j, 4])
            bbs.append(bb)
        gt_labels_list_iaa.append(bbs)
    return gt_labels_list_iaa

def convert_tiny_yolo_v2_from_iaa(gt_labels_list_iaa: list) -> list:
    '''
    Convert from imgaug BoundingBox format to the normal format

    Args:
    - gt_labels_list_iaa: a list of imgaug BoundingBoxes in the format of [BoundingBox(xmin, ymin, xmax, ymax, class_id), ...]

    Returns:
    - gt_labels_list: a list of ground truth bounding boxes in the format of [[xmin, ymin, xmax, ymax, class_id], ...]
    '''
    gt_labels_list = []
    for i in range(len(gt_labels_list_iaa)):
        bbs = []
        for j in range(len(gt_labels_list_iaa[i])):
            xmin = gt_labels_list_iaa[i][j].x1
            ymin = gt_labels_list_iaa[i][j].y1
            xmax = gt_labels_list_iaa[i][j].x2
            ymax = gt_labels_list_iaa[i][j].y2
            class_id = gt_labels_list_iaa[i][j].label
            bb = np.asarray([xmin, ymin, xmax, ymax, class_id])
            bbs.append(bb)
        gt_labels_list.append(np.asarray(bbs))
    return gt_labels_list

def tiny_yolo_v2_data_aug(cfg, images_list, gt_labels_list, max_boxes =100):
    '''
    Augment the original images along with their ground truth bounding boxes
    Arguments:
        cfg: object containing configuration parameters
        images_list: list of original images
        gt_labels_list: list of ground truth bounding boxes in the format of [[(xmin, ymin, xmax, ymax, class_id), ...], ...]
        max_boxes: maximum number of bounding boxes per image
    Returns:
        images_list_aug: list of augmented images
        gt_labels_list_aug: list of augmented ground truth bounding boxes in the format of [[(xmin, ymin, xmax, ymax, class_id), ...], ...]
    '''
    data_aug_list = []
    interpolation = cfg.preprocessing.resizing.interpolation
    interpolation_id = 0
    if interpolation == 'bilinear':
        interpolation_id = 1
    elif interpolation == 'nearest':
        interpolation_id = 0
    
    if cfg.data_augmentation.horizontal_flip:
        if random.random() < 0.5:
            data_aug_list.append(iaa.Fliplr(cfg.data_augmentation.horizontal_flip))

    if cfg.data_augmentation.vertical_flip:
        if random.random() < 0.5:
            data_aug_list.append(iaa.Flipud(cfg.data_augmentation.vertical_flip))
    
    count_affine = 0

    if cfg.data_augmentation.translation:
        if random.random() < 0.5:
            count_affine = count_affine+1
            translate = {"x": (-cfg.data_augmentation.translation, cfg.data_augmentation.translation),
                        "y": (-cfg.data_augmentation.translation, cfg.data_augmentation.translation)}
        else:
            translate = None
    else:
        translate = None
    
    if cfg.data_augmentation.rotation:
        if random.random() < 0.5:
            count_affine = count_affine+1
            rotation = (-cfg.data_augmentation.rotation, cfg.data_augmentation.rotation)
        else:
            rotation = None
    else:
        rotation = None

    if cfg.data_augmentation.shearing:
        if random.random() < 0.5:
            count_affine = count_affine + 1
            shearing = (-cfg.data_augmentation.shearing, cfg.data_augmentation.shearing)
        else:
            shearing = None
    else:
        shearing = None
    
    if count_affine > 0:
        data_aug_list.append(iaa.Affine(translate_percent=translate,rotate=rotation,shear=shearing,
                                                  order=interpolation_id,backend="cv2",cval=0))
    if cfg.data_augmentation.gaussian_blur:
        if random.random() < 0.5:
            data_aug_list.append(iaa.GaussianBlur(sigma=(0.0, cfg.data_augmentation.gaussian_blur)))

    if cfg.data_augmentation.linear_contrast:
        if random.random() < 0.5:
            data_aug_list.append(iaa.LinearContrast((cfg.data_augmentation.linear_contrast[0], cfg.data_augmentation.linear_contrast[1])))

    gt_labels_list_iaa = convert_tiny_yolo_v2_to_iaa(gt_labels_list)

    if len(data_aug_list)>0:
        seq_gen = iaa.Sequential(data_aug_list,random_order=True)
        images_list_aug, gt_labels_list_iaa_aug = seq_gen(images=images_list, bounding_boxes=gt_labels_list_iaa)
    else:
        images_list_aug = images_list
        gt_labels_list_iaa_aug = gt_labels_list_iaa

    # post-processing bounding boxes
    images_list_aug_1 = []
    gt_labels_list_iaa_aug_1 = []
    for i in range(len(images_list_aug)):
        img_shape = (images_list_aug[i].shape[0], images_list_aug[i].shape[1])
        gt_labels_iaa_aug_oni = BoundingBoxesOnImage(
            bounding_boxes=gt_labels_list_iaa_aug[i], shape=img_shape)
        gt_labels_iaa_aug_oni = gt_labels_iaa_aug_oni.remove_out_of_image(
        ).clip_out_of_image()

        if len(gt_labels_iaa_aug_oni.bounding_boxes) != 0:
            images_list_aug_1.append(images_list_aug[i])
            gt_labels_list_iaa_aug_1.append(gt_labels_iaa_aug_oni.bounding_boxes)

        gt_labels_list_aug_1 = convert_tiny_yolo_v2_from_iaa(gt_labels_list_iaa_aug_1)

    fix_label_tensor =[]
    for im_box in gt_labels_list_aug_1:
        boxes = im_box
        #(xmin, ymin, xmax, ymax, cls_id)
        if len(boxes)>max_boxes:
            boxes = boxes[:max_boxes]
        # fill in box data
        box_data = np.zeros((max_boxes,5))

        if len(boxes)>0:
            box_data[:len(boxes)] = boxes

        fix_label_tensor.append(box_data)
    fix_label_tensor = np.asarray(fix_label_tensor)

    return images_list_aug_1, fix_label_tensor