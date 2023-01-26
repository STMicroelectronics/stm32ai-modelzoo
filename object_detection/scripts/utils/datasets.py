# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
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


def parse_data(trainset):
    annotation_lines = []
    path = trainset+'/'
    for file in os.listdir(path):
        if file.endswith(".txt"):
            new_path = path+file
            annotation_lines.append(new_path)
    return annotation_lines


def boxes_to_corners(boxes, image):
    height, width, _ = image.shape
    abs_boxes = []
    for box in boxes:
        x_min = box[1]*width-box[3]*width/2
        y_min = box[2]*height-box[4]*height/2
        x_max = x_min+box[3]*width
        y_max = y_min+box[4]*height
        abs_boxes.append([int(box[0]+1), int(x_min), int(y_min), int(x_max), int(y_max)])
    return abs_boxes


def load_data(annotations):
    list_of_list = []
    images = []
    image_labels = []

    for rank, annotation in enumerate(tqdm.tqdm(annotations)):
        images_path = os.path.splitext(annotation)[0]+'.jpg'
        img = cv2.imread(images_path)
        if len(img.shape) != 3:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        txt_file_size = os.path.getsize(annotation)
        if txt_file_size != 0:
            ground_truths = pd.read_csv(annotation, sep=" ", header=None)
            ground_truths.columns = ["class_id", "x", "y", "w", "h"]
            labelz = ground_truths.values.tolist()
            labelz = boxes_to_corners(labelz, img)
        else:
            labelz = []
        images.append(images_path)
        list_of_list.append(labelz)

    image_labels = [np.array(xi) for xi in list_of_list]
    image_labels = np.array(image_labels)
    num_samples = len(images)

    return images, image_labels, num_samples


def convert_to_iaa(gt_labels_list):
    '''
    Convert to imgaug BoundingBox format to use imgaug for data augmentation
    Arguments:
        gt_labels_list: a list of ground truth bounding boxes in the format of [[class_id, xmin, ymin, xmax, ymax], ...]
    Returns:
        gt_labels_list_iaa: a list of imgaug BoundingBoxes [BoundingBox(xmin, ymin, xmax, ymax, class_id), ...]
    '''
    gt_labels_list_iaa = []
    for i in range(gt_labels_list.shape[0]):
        bbs = []
        for j in range(gt_labels_list[i].shape[0]):
            bb = BoundingBox(x1=gt_labels_list[i][j, 1],
                             y1=gt_labels_list[i][j, 2],
                             x2=gt_labels_list[i][j, 3],
                             y2=gt_labels_list[i][j, 4],
                             label=gt_labels_list[i][j, 0])
            bbs.append(bb)
        gt_labels_list_iaa.append(bbs)
    return gt_labels_list_iaa


def convert_from_iaa(gt_labels_list_iaa):
    '''
    Convert from imgaug BoundingBox format to the normal format
    Arguments:
        gt_labels_list_iaa: a list of imgaug BoundingBoxes [BoundingBox(xmin, ymin, xmax, ymax, class_id), ...]
    Returns:
        gt_labels_list: a list of ground truth bounding boxes in the format of [[class_id, xmin, ymin, xmax, ymax], ...]
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
            bb = np.asarray([class_id, xmin, ymin, xmax, ymax])
            bbs.append(bb)
        gt_labels_list.append(np.asarray(bbs))
    gt_labels_list = np.asarray(gt_labels_list)
    return gt_labels_list


def data_resize(images_list, gt_labels_list, img_height, img_width):
    '''
    Resize the original images along with their ground truth bounding boxes
    Arguments:
        images_list: list of original images
        gt_labels_list: list of ground truth bounding boxes
        img_height: target image height
        img_width: target image width
    Returns:
        images_list_resize: list of resized images
        gt_labels_list_resize: list of resized ground truth bounding boxes
    '''
    seq_resize = iaa.Sequential(
        [iaa.Resize({
            "height": img_height,
            "width": img_width
        }, interpolation=1)])

    gt_labels_list_iaa = convert_to_iaa(gt_labels_list)
    images_list_resize, gt_labels_list_iaa_resize = seq_resize(
        images=images_list, bounding_boxes=gt_labels_list_iaa)
    gt_labels_list_resize = convert_from_iaa(gt_labels_list_iaa_resize)
    return images_list_resize, gt_labels_list_resize


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
        sometimes(iaa.Fliplr(cfg.data_augmentation.horizantal_flip)),
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


def generate(cfg, images_filename_list,
             gt_labels_list,
             batch_size,
             shuffle,
             augmentation,
             fmap_sizes,
             img_width,
             img_height,
             sizes,
             ratios,
             n_classes,
             clip=False,
             normalize=True,
             pos_iou_threshold=0.5,
             neg_iou_limit=0.5,
             pre_input_mobilenet=False):
    '''
    Create a generator for model.fit_generator
    Arguments:
        images_filename_list: list of filename of original images
        gt_labels_list: list of ground truth bounding boxes coressponding to original images (TODO: Format ?)
        batch_size: size of generated minibatch
        shuffle: shuffle or not input dataset
        augmentation: apply or not data augmentation
        fmap_sizes: list of feature map sizes (used for generating anchor boxes)
        img_width: image width
        img_height: image height
        sizes, ratios: size and ratio of generated anchor boxes
        n_classes: number of object categories
        clip: clip boxes to image size
        normalize: normalize anchor boxes to image size
        pos_iou_threshold: IoU threshold to define positive anchor boxes
        neg_iou_limit: IoU threshold to define negative anchor boxes
        pre_input_mobilenet: apply pre_processing_input of MobileNet
    Returns:
        [images_batch, truths_batch]: a minibatch of images and encoded bounding boxes for training
    '''
    assert cfg.pre_processing.resizing == "bilinear", "only bilinear is supported for resizing"
    assert cfg.pre_processing.aspect_ratio is False, "Aspect ratio == True not supported yet"
    assert cfg.pre_processing.color_mode == "rgb", "only rgb training is supported"
    num_samples = len(images_filename_list)

    if shuffle:
        sampled_indices = random.sample(range(num_samples), num_samples)
        images_filename_list_sampled = [
            images_filename_list[sampled_indice]
            for sampled_indice in sampled_indices
        ]
        gt_labels_list_sampled = [
            gt_labels_list[sampled_indice]
            for sampled_indice in sampled_indices
        ]

    offset = 0
    while True:
        # samples
        if offset >= num_samples:
            offset = 0

            if shuffle:
                sampled_indices = random.sample(range(num_samples),
                                                num_samples)
                images_filename_list_sampled = [
                    images_filename_list[sampled_indice]
                    for sampled_indice in sampled_indices
                ]
                gt_labels_list_sampled = [
                    gt_labels_list[sampled_indice]
                    for sampled_indice in sampled_indices
                ]

        if (offset + batch_size) >= num_samples:
            offset += batch_size
            continue

        if shuffle:
            images_filename_batch = images_filename_list_sampled[
                offset:offset + batch_size]
            gt_labels_batch = gt_labels_list_sampled[offset:offset +
                                                     batch_size]
        else:
            images_filename_batch = images_filename_list[offset:offset +
                                                         batch_size]
            gt_labels_batch = gt_labels_list[offset:offset + batch_size]

        images_batch = []
        for filename in images_filename_batch:
            image = cv2.imread(filename)
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = np.asarray(image)
            images_batch.append(img)

        gt_labels_batch = np.asarray(gt_labels_batch)

        # resize to img_height and img_width
        images_batch, gt_labels_batch = data_resize(images_batch,
                                                    gt_labels_batch,
                                                    img_height, img_width)

        if augmentation:
            images_batch, gt_labels_batch = data_aug(cfg, images_batch,
                                                     gt_labels_batch)

        offset += batch_size

        if pre_input_mobilenet:
            images_batch_aug = preprocess_input(np.asarray(images_batch))
        else:
            images_batch_aug = [
                np.asarray(img).astype(float) / cfg.pre_processing.rescaling.scale + cfg.pre_processing.rescaling.offset for img in images_batch
            ]
        images_batch_aug = np.asarray(images_batch_aug)
        gt_labels_batch_aug = np.asarray(gt_labels_batch)

        truths_batch_aug = match_gt_anchors(
            fmap_sizes,
            img_width,
            img_height,
            sizes,
            ratios,
            gt_labels_batch_aug,
            n_classes,
            clip=clip,
            normalize=normalize,
            pos_iou_threshold=pos_iou_threshold,
            neg_iou_limit=neg_iou_limit)

        ret = []
        ret.append(images_batch_aug)
        ret.append(truths_batch_aug)

        yield ret
