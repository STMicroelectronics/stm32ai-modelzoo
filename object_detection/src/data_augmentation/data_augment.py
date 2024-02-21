# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import random

import cv2
import numpy as np
import pandas as pd
import tqdm
from anchor_boxes_utils import match_gt_anchors
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from tensorflow.keras.applications.mobilenet import preprocess_input
from typing import List


def convert_to_iaa(gt_labels_list: List[List[float]]) -> List[List[BoundingBox]]:
    """
    Convert ground truth bounding boxes to imgaug BoundingBox format for data augmentation

    Args:
        gt_labels_list (List[List[float]]): a list of ground truth bounding boxes in the format of [[class_id, xmin, ymin, xmax, ymax], ...]

    Returns:
        gt_labels_list_iaa (List[List[BoundingBox]]): a list of imgaug BoundingBoxes [BoundingBox(xmin, ymin, xmax, ymax, class_id), ...]
    """
    gt_labels_list_iaa = []  # initialize empty list to hold imgaug BoundingBoxes
    for gt_labels in gt_labels_list:  # loop through each ground truth bounding box
        bbs = []  # initialize empty list to hold BoundingBoxes for each ground truth bounding box
        for label in gt_labels:  # loop through each label in the ground truth bounding box
            # create a BoundingBox object with the label's coordinates and class ID
            bb = BoundingBox(x1=label[1], y1=label[2], x2=label[3], y2=label[4], label=label[0])
            bbs.append(bb)  # add the BoundingBox to the list
        gt_labels_list_iaa.append(bbs)  # add the list of BoundingBoxes to the list of imgaug BoundingBoxes
    return gt_labels_list_iaa  # return the list of imgaug BoundingBoxes


def convert_from_iaa(gt_labels_list_iaa: list) -> np.ndarray:
    """
    Converts ground truth bounding boxes from imgaug BoundingBox format to [[class_id, xmin, ymin, xmax, ymax], ...]
    format.

    Args:
        gt_labels_list_iaa (list): A list of imgaug BoundingBoxes [BoundingBox(xmin, ymin, xmax, ymax, class_id), ...].

    Returns:
        gt_labels_list (np.ndarray): A list of ground truth bounding boxes in [[class_id, xmin, ymin, xmax, ymax], ...]
        format.
    """
    gt_labels_list = []

    # Loop through each ground truth label
    for gt_labels in gt_labels_list_iaa:
        bbs = []

        # Loop through each BoundingBox in the ground truth label
        for bb in gt_labels:
            # Create a new bounding box array and append it to the list
            xmin, ymin, xmax, ymax = bb.x1, bb.y1, bb.x2, bb.y2
            class_id = bb.label
            bbs.append([class_id, xmin, ymin, xmax, ymax])

        gt_labels_list.append(np.asarray(bbs))

    gt_labels_list = np.asarray(gt_labels_list)
    return gt_labels_list


def data_aug(cfg, images_list, gt_labels_list):
    '''
    Augment the original images along with their ground truth bounding boxes
    Arguments:
        images_list: list of original images
        gt_labels_list: list of ground truth bounding boxes
    Returns:
        images_list_aug: list of augmented images
        gt_labels_list_aug: list of augmented ground truth bounding boxes
    '''

    def sometimes(aug):
        return iaa.Sometimes(0.5, aug)

    seq_gen = iaa.Sequential([
        sometimes(iaa.Fliplr(cfg.data_augmentation.horizontal_flip)),
        sometimes(iaa.Flipud(cfg.data_augmentation.vertical_flip)),
        sometimes(iaa.CropAndPad(percent=(-0.25, 0), pad_cval=(0, 255))),
        sometimes(
            iaa.Affine(scale={
                "x": (0.5, 1.1),
                "y": (0.5, 1.1)
            },
                translate_percent={
                    "x": (-cfg.data_augmentation.translation, cfg.data_augmentation.translation),
                    "y": (-cfg.data_augmentation.translation, cfg.data_augmentation.translation)
                },
                rotate=(-cfg.data_augmentation.rotation, cfg.data_augmentation.rotation),
                shear=(-cfg.data_augmentation.shearing, cfg.data_augmentation.shearing),
                order=[0, 1],
                cval=(0, 255))),
        iaa.Multiply((0.5, 1.5)),
        iaa.GaussianBlur(sigma=(0.0, cfg.data_augmentation.gaussian_blur)),
        iaa.AdditiveGaussianNoise(scale=(0.0, 0.05 * 255)),
        iaa.LinearContrast((cfg.data_augmentation.linear_contrast[0], cfg.data_augmentation.linear_contrast[1])),
        iaa.Add((-50, 50), per_channel=0.5)
    ],
        random_order=True)

    gt_labels_list_iaa = convert_to_iaa(gt_labels_list)
    images_list_aug, gt_labels_list_iaa_aug = seq_gen(
        images=images_list, bounding_boxes=gt_labels_list_iaa)
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
            gt_labels_list_iaa_aug_1.append(
                gt_labels_iaa_aug_oni.bounding_boxes)
        gt_labels_list_aug_1 = convert_from_iaa(gt_labels_list_iaa_aug_1)
    return images_list_aug_1, gt_labels_list_aug_1
