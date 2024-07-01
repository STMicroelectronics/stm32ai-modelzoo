# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import random
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf
import cv2
from datasets import *
from imgaug import augmenters as iaa
from typing import List, Tuple

from models_utils import get_model_name_and_its_input_shape
from data_augment import data_aug, convert_to_iaa, convert_from_iaa
from datasets import load_dataset
from anchor_boxes_utils import get_sizes_ratios, get_sizes_ratios_ssd_v2, match_gt_anchors


def load_and_preprocess_image(image_file_path: str = None,
                              image_size=None,
                              scale: float = None,
                              offset: float = None,
                              interpolation: str = None,
                              color_mode: str = None) -> np.ndarray:
    """
    Loads and preprocesses an image.

    Args:
        image_file_path: The path to the image.
        image_size: The image shape.
        scale: The scale factor for rescaling the image.
        offset: The offset for rescaling the image.
        interpolation: interpolation method for resizing the image.
        color_mode: str. Used to have number of input channels

    Returns:
        The preprocessed image as a NumPy array.
    """

    channels = 1 if color_mode == "grayscale" else 3
    data = tf.io.read_file(image_file_path)
    image = tf.io.decode_image(data, channels=channels, expand_animations=False)
    image = tf.image.resize(image, [image_size[1], image_size[0]], method=interpolation)

    image = tf.cast(image, tf.float32) * scale + offset
    
    return image.numpy()


def data_resize_3(images_list: list, gt_labels_list: list, img_height: int, img_width: int,
                  interpolation: str = 'bilinear') -> tuple:
    """
    Resize the original images along with their ground truth bounding boxes.

    Args:
        images_list: A list of original images.
        gt_labels_list: A list of ground truth bounding boxes.
        img_height: The target image height.
        img_width: The target image width.
        interpolation: The interpolation method to use for resizing ('bilinear' or 'nearest').

    Returns:
        A tuple containing the resized images and resized ground truth bounding boxes.
    """

    if interpolation == 'bilinear':
        # Define the sequence of resizing using bilinear interpolation
        seq_resize = iaa.Sequential(
            [iaa.Resize({
                "height": img_height,
                "width": img_width
            }, interpolation=1)])
    elif interpolation == 'nearest':
        # Define the sequence of resizing using nearest neighbor interpolation
        seq_resize = iaa.Sequential(
            [iaa.Resize({
                "height": img_height,
                "width": img_width
            }, interpolation=0)])
    else:
        raise ValueError("Invalid interpolation method. Supported methods are 'bilinear' and 'nearest'.")

    # Convert the ground truth bounding boxes to the required format for the sequence
    gt_labels_list_iaa = convert_to_iaa(gt_labels_list)

    # Apply the sequence to both the images and the ground truth bounding boxes
    images_list_resize, gt_labels_list_iaa_resize = seq_resize(
        images=images_list, bounding_boxes=gt_labels_list_iaa)

    # Convert the ground truth bounding boxes back to the original format
    gt_labels_list_resize = convert_from_iaa(gt_labels_list_iaa_resize)

    # Return the resized images and ground truth bounding boxes
    return images_list_resize, gt_labels_list_resize


def data_resize(images_list: list, gt_labels_list: list, img_height: int, img_width: int) -> tuple:
    """
    Resize the original images along with their ground truth bounding boxes.

    Args:
        images_list: A list of original images.
        gt_labels_list: A list of ground truth bounding boxes.
        img_height: The target image height.
        img_width: The target image width.

    Returns:
        A tuple containing the resized images and resized ground truth bounding boxes.
    """

    # Define the sequence of resizing
    seq_resize = iaa.Sequential(
        [iaa.Resize({
            "height": img_height,
            "width": img_width
        }, interpolation=1)])

    # Convert the ground truth bounding boxes to the required format for the sequence
    gt_labels_list_iaa = convert_to_iaa(gt_labels_list)

    # Apply the sequence to both the images and the ground truth bounding boxes
    images_list_resize, gt_labels_list_iaa_resize = seq_resize(
        images=images_list, bounding_boxes=gt_labels_list_iaa)

    # Convert the ground truth bounding boxes back to the original format
    gt_labels_list_resize = convert_from_iaa(gt_labels_list_iaa_resize)

    # Return the resized images and ground truth bounding boxes
    return images_list_resize, gt_labels_list_resize


def data_resize_2(images: List[np.ndarray],
                  gt_labels: np.ndarray,
                  img_height: int,
                  img_width: int,
                  interpolation: str = 'bilinear') -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Resize images and ground truth labels to img_height and img_width
    Arguments:
        images: list of images to resize
        gt_labels: ground truth bounding boxes corresponding to the images
        img_height: height to resize the images to
        img_width: width to resize the images to
        interpolation: interpolation method to use for resizing ('bilinear' or 'nearest')
    Returns:
        images_resized: list of resized images
        gt_labels_resized: resized ground truth bounding boxes
    """
    images_resized = []
    gt_labels_resized = []

    for i, image in enumerate(images):
        if interpolation == 'bilinear':
            # Resize the image using bilinear interpolation
            image_resized = cv2.resize(image, (img_width, img_height), interpolation=cv2.INTER_LINEAR)
        elif interpolation == 'nearest':
            # Resize the image using nearest neighbor interpolation
            image_resized = cv2.resize(image, (img_width, img_height), interpolation=cv2.INTER_NEAREST)
        else:
            raise ValueError("Invalid interpolation method. Supported methods are 'bilinear' and 'nearest'.")

        # Append the resized image to the list of resized images
        images_resized.append(image_resized)

        # Scale the ground truth bounding boxes based on the image size
        scale_x = img_width / image.shape[1]
        scale_y = img_height / image.shape[0]
        gt_labels_resized_i = gt_labels[i].copy()
        gt_labels_resized_i[:, 0] *= scale_x
        gt_labels_resized_i[:, 2] *= scale_x
        gt_labels_resized_i[:, 1] *= scale_y
        gt_labels_resized_i[:, 3] *= scale_y
        gt_labels_resized.append(gt_labels_resized_i)

    # Convert the list of resized images to a numpy array
    images_resized = np.asarray(images_resized)

    # Convert the list of resized ground truth bounding boxes to a numpy array
    gt_labels_resized = np.asarray(gt_labels_resized)

    return images_resized, gt_labels_resized


def preprocess_image(image: np.ndarray, target_size: int) -> np.ndarray:
    """
    Preprocesses an image for input to the model.

    Args:
        image: The image as a NumPy array.
        target_size: The target size of the image.

    Returns:
        The preprocessed image as a NumPy array.
    """
    resized_image = cv2.resize(image, (target_size, target_size), interpolation=cv2.INTER_LINEAR)
    image_data = resized_image / 255.0
    image_processed = np.expand_dims(image_data, 0)
    return image_processed


def generate(cfg: dict = None,
             images_filename_list: List[str] = None,
             gt_labels_list: List[List[Tuple[float, float, float, float, int]]] = None,
             batch_size: int = 64,
             shuffle: bool = None,
             augmentation: bool = False,
             fmap_sizes: List[Tuple[int, int]] = None,
             img_width: int = None,
             img_height: int = None,
             sizes: List[int] = None,
             ratios: List[float] = None,
             n_classes: int = None,
             clip: bool = False,
             normalize: bool = True,
             pos_iou_threshold: float = 0.5,
             neg_iou_limit: float = 0.5,
             pre_input_mobilenet: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a generator for model.fit_generator
    Arguments:
        cfg: dictionary containing configuration parameters
        images_filename_list: list of filename of original images
        gt_labels_list: list of ground truth bounding boxes corresponding to original images
        batch_size: size of generated minibatch
        shuffle: shuffle or not input dataset
        augmentation: apply or not data augmentation
        fmap_sizes: list of feature map sizes (used for generating anchor boxes)
        img_width: image width
        img_height: image height
        sizes: list of sizes of generated anchor boxes
        ratios: list of aspect ratios of generated anchor boxes
        n_classes: number of object categories
        clip: clip boxes to image size
        normalize: normalize anchor boxes to image size
        pos_iou_threshold: IoU threshold to define positive anchor boxes
        neg_iou_limit: IoU threshold to define negative anchor boxes
        pre_input_mobilenet: apply pre_processing_input of MobileNet
    Returns:
        [images_batch, truths_batch]: a minibatch of images and encoded bounding boxes for training
    """

    # Check if the resizing method is bilinear
    # assert cfg.pre_processing.resizing == "bilinear", "only bilinear is supported for resizing"

    # Check if aspect ratio is not enabled
    # global images_filename_list_sampled
    # assert cfg.pre_processing.aspect_ratio is False, "Aspect ratio == True not supported yet"

    # Check if color mode is RGB
    # assert cfg.pre_processing.color_mode == "rgb", "only rgb training is supported"

    # Get the number of samples
    num_samples = len(images_filename_list)
    # handle case when the batch size is greater or equal the dataset size
    if batch_size >= num_samples:
        exp = np.math.log(num_samples, 2)
        exp = np.math.floor(exp)
        batch_size = int(2 ** exp)

    if shuffle:
        # If shuffle is True, randomly sample the indices
        sampled_indices = random.sample(range(num_samples), num_samples)

        # Sample the images and ground truth labels based on the sampled indices
        images_filename_list_sampled = [images_filename_list[sampled_indice] for sampled_indice in sampled_indices]
        gt_labels_list_sampled = [gt_labels_list[sampled_indice] for sampled_indice in sampled_indices]

    # Initialize the offset
    offset = 0

    # Loop infinitely
    while True:
        # If offset is greater than or equal to the number of samples, reset offset to 0
        if offset >= num_samples:
            offset = 0

            if shuffle:
                # If shuffle is True, randomly sample the indices
                sampled_indices = random.sample(range(num_samples), num_samples)

                # Sample the images and ground truth labels based on the sampled indices
                images_filename_list_sampled = [images_filename_list[sampled_indice] for sampled_indice in
                                                sampled_indices]
                gt_labels_list_sampled = [gt_labels_list[sampled_indice] for sampled_indice in sampled_indices]

        # If the next batch exceeds the number of samples, skip to the next batch
        if (offset + batch_size) >= num_samples:
            offset += batch_size
            continue

        # Sample the images and ground truth labels based on the offset and batch size
        if shuffle:
            images_filename_batch = images_filename_list_sampled[offset:offset + batch_size]
            gt_labels_batch = gt_labels_list_sampled[offset:offset + batch_size]
        else:
            images_filename_batch = images_filename_list[offset:offset + batch_size]
            gt_labels_batch = gt_labels_list[offset:offset + batch_size]

        # Initialize an empty list to store the images
        images_batch = []

        # Loop through the images in the batch and preprocess them
        for filename in images_filename_batch:
            # Read the image 
            data = tf.io.read_file(filename)
            img = tf.io.decode_image(data, channels=3)
            # Append the image to the images batch
            images_batch.append(img.numpy())

        # Convert the ground truth labels to a numpy array
        gt_labels_batch = np.asarray(gt_labels_batch)

        # Resize the images and ground truth labels to img_height and img_width
        images_batch, gt_labels_batch = data_resize(images_batch, gt_labels_batch, img_height, img_width)

        # Apply data augmentation if augmentation is True
        if augmentation:
            images_batch, gt_labels_batch = data_aug(cfg, images_batch, gt_labels_batch)

        # Increment the offset by the batch size
        offset += batch_size

        # Apply pre-processing input of MobileNet if pre_input_mobilenet is True
        if pre_input_mobilenet:
            ####### THIS FUNCTION DOES NOT EXIST. #######
            images_batch_aug = preprocess_input(np.asarray(images_batch))
        else:
            # Normalize the images based on the rescaling parameters in the configuration file
            images_batch_aug = [
                np.asarray(img).astype(float) * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset
                for img in images_batch]
        images_batch_aug = np.asarray(images_batch_aug)

        # Convert the ground truth labels to a numpy array
        gt_labels_batch_aug = np.asarray(gt_labels_batch)

        # Generate anchor boxes based on the ground truth labels
        truths_batch_aug = match_gt_anchors(fmap_sizes, img_width, img_height, sizes, ratios, gt_labels_batch_aug,
                                            n_classes, clip=clip, normalize=normalize,
                                            pos_iou_threshold=pos_iou_threshold, neg_iou_limit=neg_iou_limit)

        # # Return the images batch and the encoded bounding boxes for training
        ret = []
        ret.append(images_batch_aug)
        ret.append(truths_batch_aug)
        yield ret


def generate_quant(cfg=None, images_filename_list=None, batch_size=None, img_width=None, img_height=None):
    """
    Create a generator for model.fit_generator
    Arguments:
        cfg: dictionary containing configuration parameters
        images_filename_list: list of filename of original images
        batch_size: size of generated minibatch
        img_width: image width
        img_height: image height
    Returns:
        [images_batch, truths_batch]: a minibatch of images and encoded bounding boxes for training
    """
    
    channels = 1 if cfg.preprocessing.color_mode == "grayscale" else 3
    interpolation = cfg.preprocessing.resizing.interpolation

    def parse_function(filename):

        image_string = tf.io.read_file(filename)
        image = tf.io.decode_image(image_string, channels=channels, expand_animations=False)
        image = tf.image.resize(image, [img_height, img_width], method=interpolation)
        image = tf.cast(image, tf.float32) * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset

        return image

    # Get the number of samples
    num_samples = len(images_filename_list)
    # handle case when the batch size is greater or equal the dataset size
    if batch_size >= num_samples:
        exp = np.math.log(num_samples, 2)
        exp = np.math.floor(exp)
        batch_size = int(2 ** exp)

    quant_dataset = tf.data.Dataset.from_tensor_slices(images_filename_list)
    quant_dataset = quant_dataset.map(parse_function,num_parallel_calls=tf.data.AUTOTUNE)
    quant_dataset = quant_dataset.batch(batch_size,drop_remainder=True)

    return quant_dataset


def load_and_pre_process_image(image_path: str = None, 
                               input_shape: tuple = None,
                               scale: float = None,
                               offset: float = None,
                               interpolation: str = None,
                               color_mode: str = None) -> Tuple[np.ndarray, int, int]:
    """
    Loads and preprocesses an image.

    Args:
        image_path (str): The path to the image.
        scale (float, optional): The scale factor for normalization. Defaults to 1 / 125.5.
        offset (float, optional): The offset factor for normalization. Defaults to -1.
        interpolation (int, optional): The interpolation method to use for resizing images.
        Defaults to cv2.INTER_LINEAR.
        input_shape (tuple, optional): The input shape of the model. Defaults to None.
        color_mode: (str)

    Returns:
        Tuple[np.ndarray, int, int]: The preprocessed image as a NumPy array, and the height and width of the original
        image.
    """
    width, height = input_shape[:2]
    channels = 1 if color_mode == "grayscale" else 3

    data = tf.io.read_file(image_path)
    image = tf.io.decode_image(data, channels=channels)
    image = tf.image.resize(image, [height, width], method=interpolation)
    image = image.numpy()

    image = scale * image + offset
    image_processed = np.expand_dims(image, axis=0)

    return image_processed, height, width


def preprocess(cfg: DictConfig = None) -> tuple:
    """
    Preprocesses the data based on the provided configuration.

    train_ds, valid_ds, test_ds and quantization_ds are dictionaries that include
    the images and the parsed labels.
    If there is no validation set, the training set is split in two to create one.
    The train_gen and valid_gen generators are only returned if the operation mode
    includes a training. Otherwise, only train_ds, valid_ds, test_ds and quantization_ds
    are returned.

    Args:
        cfg (DictConfig): Configuration object containing the settings.

    Returns:
        train_ds (Dict): training dataset
        valid_ds (Dict): validation dataset
        test_ds (Dict): test dataset
        quantization_ds (Dict): quantization_ dataset
        train_gen (Generator): training generator
        valid_gen (Generator): validation generator
    """

    # Load the datasets
    train_ds, valid_ds, quantization_ds, test_ds = load_dataset(
                training_path=cfg.dataset.training_path,
                validation_path=cfg.dataset.validation_path,
                quantization_path=cfg.dataset.quantization_path,
                test_path=cfg.dataset.test_path,
                validation_split=cfg.dataset.validation_split)

    fmap_sizes_dict = {'st_ssd_mobilenet_v1': {'192': [24, 12, 6, 3, 1],
                                               '224': [32, 16, 8, 4, 2, 1],
                                               '256': [32, 16, 8, 4, 2, 1]},
                       'ssd_mobilenet_v2_fpnlite': {'192': [24, 12, 6, 3, 2],
                                                    '224': [28, 14, 7, 4, 2],
                                                    '256': [32, 16, 8, 4, 2],
                                                    '288': [36, 18, 9, 5, 3],
                                                    '320': [40, 20, 10, 5, 3],
                                                    '352': [44, 22, 11, 6, 3],
                                                    '384': [48, 24, 12, 6, 3],
                                                    '416': [52, 26, 13, 7, 4]}}
    train_gen = None
    valid_gen = None
    quant_gen = None

    if cfg.general.model_path or cfg.training:

        # Get the model input shape and feature map sizes
        try:
            batch_size = cfg.training.batch_size
        except:
            batch_size = 64

        try:
            n_classes = len(cfg.dataset.class_names)
        except:
            
            if cfg.operation_mode in ['quantization' ,'benchmarking', 'chain_qb']:
                n_classes = None
            else:
                raise AttributeError("Missing the class_names variable in the dataset section!\nCheck the dataset section of your config.yaml file.")
        

        model_path = cfg.general.model_path
        if model_path:
            if model_path[-15:] == 'best_weights.h5':
                input_shape = cfg.training.model.input_shape
                #_, _, fmap_sizes = get_model(cfg=cfg, class_names=cfg.dataset.class_names)
            elif model_path[-4:]=='onnx':
                _, ish = get_model_name_and_its_input_shape(model_path)
                input_shape = [ish[1],ish[2],ish[0]] # because ONNX is channel first
            else:
                # We are resuming the training.
                #os.path.join(cfg.training.resume_training_from, cfg.general.saved_models_dir, "inference_model.h5")
                _, input_shape = get_model_name_and_its_input_shape(model_path)
        else:
            input_shape = cfg.training.model.input_shape

        img_width, img_height, _ = input_shape
        fmap_widths  = np.array(fmap_sizes_dict[cfg.general.model_type][str(input_shape[0])])
        fmap_heights = np.array(fmap_sizes_dict[cfg.general.model_type][str(input_shape[1])])

        if cfg.general.model_type == 'st_ssd_mobilenet_v1':
            fmap_sizes   = np.stack([fmap_widths,fmap_heights],axis=-1)
            sizes_h, ratios_h = get_sizes_ratios(input_shape)
        elif cfg.general.model_type == 'ssd_mobilenet_v2_fpnlite':
            fmap_sizes   = np.stack([fmap_widths,fmap_heights],axis=-1)
            sizes_h, ratios_h = get_sizes_ratios_ssd_v2(input_shape)
        else:
            print('[ERROR] : Unsupported model type, please use "st_ssd_mobilenet_v1" or "ssd_mobilenet_v2_fpnlite"')

        if train_ds:
            train_gt_labels_ds = train_ds['train_gt_labels_ds']
            train_images_filename_ds = train_ds['train_images_filename_ds']
            train_gen = generate(cfg=cfg, images_filename_list=train_images_filename_ds,
                                 gt_labels_list=train_gt_labels_ds, batch_size=batch_size, shuffle=True,
                                 augmentation=True if cfg.data_augmentation else False,
                                 fmap_sizes=fmap_sizes, img_width=img_width, img_height=img_height, sizes=sizes_h,
                                 ratios=ratios_h, n_classes=n_classes)

        if valid_ds:
            val_gt_labels_ds = valid_ds['val_gt_labels_ds']
            val_images_filename_ds = valid_ds['val_images_filename_ds']
            # Create the data generators for training and validation
            valid_gen = generate(cfg=cfg, images_filename_list=val_images_filename_ds, gt_labels_list=val_gt_labels_ds,
                                 batch_size=batch_size, shuffle=False, augmentation=False, fmap_sizes=fmap_sizes,
                                 img_width=img_width, img_height=img_height, sizes=sizes_h, ratios=ratios_h,
                                 n_classes=n_classes)

        if train_ds or quantization_ds:
            if train_ds:
                quant_images_filename_ds = train_ds['train_images_filename_ds']
            else:
                quant_images_filename_ds = quantization_ds['quantization_images_filename_ds']
            quant_gen = generate_quant(cfg=cfg, images_filename_list=quant_images_filename_ds,
                                       batch_size=batch_size, img_width=img_width, img_height=img_height)
        
    return train_ds, valid_ds, test_ds, quantization_ds, train_gen, valid_gen, quant_gen
