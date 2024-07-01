# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os

import numpy as np
import tensorflow as tf
from omegaconf import DictConfig
from typing import Tuple


def preprocess_mask(mask_path: str = None, input_size: list = None, aspect_ratio: str = None,
                    interpolation_method: str = None) -> tf.Tensor:
    """
        Loads the mask file and pre-process it according to configuration parameters

        Args:
            mask_path (str): path to the mask of the candidate image
            input_size (list): image resolution in pixels [height, width]
            aspect_ratio (str): "fit" or "crop"
            interpolation_method (str): resizing interpolation method but so far hard-coded to 'nearest' at call

        Returns:
            A tensor containing the pre-processed mask

    """
    # Read the mask file
    mask = tf.io.read_file(mask_path)
    mask = tf.image.decode_png(mask, channels=1)

    if aspect_ratio == "fit":
        mask = tf.image.resize(mask, input_size, method=interpolation_method, preserve_aspect_ratio=False)
    else:
        mask = tf.image.resize_with_crop_or_pad(mask, input_size[0], input_size[1])

    mask = tf.cast(mask, tf.uint8)
    mask = tf.where(mask == 255, tf.zeros_like(mask), mask)

    return mask


def get_image(image_path: str = None, images_nb_channels: int = None, aspect_ratio: str = None,
              interpolation: str = None, scale: float = None, offset: int = None, input_size: list = None) -> tf.Tensor:
    """
    Loads an image from a file path. Resize it with appropriate interpolation method. Scale it according to
    config parameters.

    Args:
        image_path (str): path to candidate image
        images_nb_channels (int): 1 if greyscale, 3 if RGB
        aspect_ratio (str): "fit" or "crop"
        interpolation (str): resizing interpolation method
        scale (float): rescaling pixels value
        offset (int): offset value on pixels
        input_size (list): image resolution in pixels [height, width]

    Returns:
        A tensor containing the pixels, appropriately resized and scaled

    """
    # load image
    img = tf.io.read_file(image_path)
    img = tf.image.decode_jpeg(img, channels=images_nb_channels)

    height = input_size[0]
    width = input_size[1]

    if aspect_ratio == "fit":
        img = tf.image.resize(img, [height, width], method=interpolation, preserve_aspect_ratio=False)
    else:
        img = tf.image.resize_with_crop_or_pad(img, height, width)

    # Rescale the image
    img_processed = scale * tf.cast(img, tf.float32) + offset

    return img_processed


def load_image_and_mask_pascal_voc(image_path: str = None, mask_path: str = None, images_nb_channels: int = None,
                                   aspect_ratio: str = None, interpolation: str = None, scale: float = None,
                                   offset: int = None, input_size: list = None) -> tuple:
    """
        Loads an image and a mask from a file path. Preprocess them according to config file parameters

        Args:
            image_path (str): path to candidate image
            mask_path (str): path to corresponding mask
            images_nb_channels (int): 1 if greyscale, 3 if RGB
            aspect_ratio (str): "fit' or "crop"
            interpolation (str): resizing interpolation method
            scale (float): rescaling pixels value
            offset (int): offset value on pixels
            input_size (list): image resolution in pixels [height, width]

        Returns:
            A tuple of tensor containing the image pixels and the mask, appropriately resized and scaled

        """
    input_image = get_image(image_path, images_nb_channels, aspect_ratio, interpolation, scale, offset, input_size)
    input_mask = preprocess_mask(mask_path, input_size, aspect_ratio, interpolation_method='nearest')
    
    return input_image, input_mask


def get_path_dataset(images_dir: str = None, masks_dir: str = None, ids_file_path: str = None, seed: int = None,
                     shuffle: bool = True) -> tf.data.Dataset:
    """
    Creates a tf.data.Dataset from a dataset root directory path.

    Args:
        images_dir (str): path to image directory for dataset construction
        masks_dir (str): path to mask directory for dataset construction
        ids_file_path: (str): file path. The file contains a list of image to be considered for dataset creation.
        seed (int): seed when performing shuffle.
        shuffle (bool): Shuffle or not the dataset.

    Returns:
        dataset(tf.data.Dataset) -> dataset with a tuple (path, label) of each sample. 
    """

    with open(ids_file_path, 'r') as file:
        ids = file.read().splitlines()

    image_paths = [os.path.join(images_dir, img_id + ".jpg") for img_id in ids]
    mask_paths = [os.path.join(masks_dir, img_id + ".png") for img_id in ids]  # Adjust the extension if necessary

    # Filter out non-existing files
    existing_image_paths = []
    existing_mask_paths = []
    for img_path, msk_path in zip(image_paths, mask_paths):
        if os.path.exists(img_path) and os.path.exists(msk_path):
            existing_image_paths.append(img_path)
            existing_mask_paths.append(msk_path)
        else:
            print(f"Warning: Skipping {img_path} because the image or mask does not exist.")

    data_list = [existing_image_paths, existing_mask_paths]

    if shuffle:
        rng = np.random.RandomState(seed)
        perm = rng.permutation(len(data_list[0]))
        data_list = [np.take(data_list[0], perm, axis=0), np.take(data_list[1], perm, axis=0)]

    return data_list


def get_train_val_ds(images_path: str = None, images_masks: str = None, files_path: str = None, cfg: DictConfig = None,
                     image_size: tuple[int] = None, batch_size: int = None, seed: int = None, shuffle: bool = True,
                     to_cache: bool = False) -> Tuple[tf.data.Dataset, tf.data.Dataset]:
    """
    Loads the images under a given dataset root directory and returns training 
    and validation tf.Data.datasets.

    Args:
        images_path (str): path to image directory for dataset construction
        images_masks (str): path to mask directory for dataset construction
        files_path: (str): file path. The file contains a list of image to be considered for dataset creation.
        cfg: (dict): config dictionary
        image_size (tuple[int]): Size of the input images to resize them to.
        batch_size (int): Batch size to use for training and validation.
        seed (int): Seed to use for shuffling the data.
        shuffle (bool): Whether or not to shuffle the data.
        to_cache (bool): Whether or not to cache the datasets.

    Returns:
        Tuple[tf.data.Dataset, tf.data.Dataset]: Training and validation datasets.
    """
    color_mode = cfg.preprocessing.color_mode
    color_mode = color_mode if color_mode else "rgb"
    channels = 1 if color_mode == "grayscale" else 3

    validation_split = cfg.dataset.validation_split
    interpolation = cfg.preprocessing.resizing.interpolation
    aspect_ratio = cfg.preprocessing.resizing.aspect_ratio
    scale = cfg.preprocessing.rescaling.scale
    offset = cfg.preprocessing.rescaling.offset

    datalist = get_path_dataset(images_dir=images_path, masks_dir=images_masks, ids_file_path=files_path, seed=seed,
                                shuffle=shuffle)

    dataset = tf.data.Dataset.from_tensor_slices((datalist[0], datalist[1]))

    train_size = int(len(dataset)*(1-validation_split))
    train_ds = dataset.take(train_size)
    val_ds = dataset.skip(train_size)

    if shuffle:
        train_ds = train_ds.shuffle(len(train_ds), reshuffle_each_iteration=True, seed=seed)
    
    if cfg.dataset.name == "pascal_voc":
        # Map the paths to the actual loaded and preprocessed images and masks
        mapping_params = (channels, aspect_ratio, interpolation, scale, offset, image_size)
        train_ds = train_ds.map(lambda img, msk: load_image_and_mask_pascal_voc(img, msk, *mapping_params),
                                num_parallel_calls=tf.data.AUTOTUNE)
        val_ds = val_ds.map(lambda img, msk: load_image_and_mask_pascal_voc(img, msk, *mapping_params),
                            num_parallel_calls=tf.data.AUTOTUNE)
    else:
        raise ValueError("Other dataset than Pascal VOC are not supported yet for segmentation!")
    
    train_ds = train_ds.batch(batch_size)
    val_ds = val_ds.batch(batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        val_ds = val_ds.cache()
    
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds


def get_ds(images_path: str = None, images_masks: str = None, files_path: str = None, cfg: DictConfig = None,
           image_size: tuple[int] = None, batch_size: int = None, seed: int = None, shuffle: bool = True,
           to_cache: bool = False) -> tf.data.Dataset:
    """
    Loads the images from the given dataset root directory and returns a tf.data.Dataset.

    Args:
        images_path (str): path to image directory for dataset construction
        images_masks (str): path to mask directory for dataset construction
        files_path: (str): file path. The file contains a list of image to be considered for dataset creation.
        cfg: (dict): config dictionary
        image_size (tuple[int]): Size of the input images to resize them to.
        batch_size (int): Batch size to use for the dataset.
        seed (int): Seed to use for shuffling the data.
        shuffle (bool): Whether or not to shuffle the data.
        to_cache (bool): Whether or not to cache the dataset.

    Returns:
        tf.data.Dataset: Dataset containing the images.
    """
    color_mode = cfg.preprocessing.color_mode
    color_mode = color_mode if color_mode else "rgb"
    channels = 1 if color_mode == "grayscale" else 3
    interpolation = cfg.preprocessing.resizing.interpolation
    aspect_ratio = cfg.preprocessing.resizing.aspect_ratio
    scale = cfg.preprocessing.rescaling.scale
    offset = cfg.preprocessing.rescaling.offset

    datalist = get_path_dataset(images_dir=images_path, masks_dir=images_masks, ids_file_path=files_path, seed=seed,
                                shuffle=shuffle)

    dataset = tf.data.Dataset.from_tensor_slices((datalist[0], datalist[1]))
    
    if shuffle:
        dataset = dataset.shuffle(len(dataset), reshuffle_each_iteration=True, seed=seed)

    if cfg.dataset.name == "pascal_voc":
        # Map the paths to the actual loaded and preprocessed images and masks
        mapping_params = (channels, aspect_ratio, interpolation, scale, offset, image_size)
        dataset = dataset.map(lambda img, msk: load_image_and_mask_pascal_voc(img, msk, *mapping_params),
                              num_parallel_calls=tf.data.AUTOTUNE)
    else:
        raise ValueError("Other dataset than Pascal VOC are not supported yet for segmentation!")

    dataset = dataset.batch(batch_size)

    if to_cache:
        dataset = dataset.cache()
    
    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)

    return dataset


def load_dataset(cfg: DictConfig = None,
                 image_size: tuple[int] = None) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
    """
    Loads the images from the given dataset root directories and returns training,
    validation, and test tf.data.Datasets.

    Args:
        cfg: (dict): config dictionary
        image_size (tuple[int]): resizing (width, height) of input images
    Returns:
        Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]: Training, validation, quantization
        and test datasets.
    """

    training_path = cfg.dataset.training_path
    training_masks_path = cfg.dataset.training_masks_path
    training_files_path = cfg.dataset.training_files_path
    validation_path = cfg.dataset.validation_path
    validation_masks_path = cfg.dataset.validation_masks_path
    validation_files_path = cfg.dataset.validation_files_path
    quantization_path = cfg.dataset.quantization_path
    quantization_masks_path = cfg.dataset.quantization_masks_path
    quantization_files_path = cfg.dataset.quantization_files_path
    test_path = cfg.dataset.test_path
    test_masks_path = cfg.dataset.test_masks_path
    test_files_path = cfg.dataset.test_files_path
    seed = cfg.dataset.seed

    # Set a default value to 32 for the 'evaluation' mode in case a 'training' section is not available
    batch_size = cfg.training.batch_size if cfg.training else 32

    if training_path and not validation_path:
        # There is no validation. We split the training set in two to create one.
        train_ds, val_ds = get_train_val_ds(images_path=training_path, images_masks=training_masks_path,
                                            files_path=training_files_path, cfg=cfg, image_size=image_size,
                                            batch_size=batch_size, seed=seed, shuffle=True, to_cache=False)
    elif training_path and validation_path:
        train_ds = get_ds(images_path=training_path, images_masks=training_masks_path,
                          files_path=training_files_path, cfg=cfg, image_size=image_size,
                          batch_size=batch_size, seed=seed, shuffle=True, to_cache=False)

        val_ds = get_ds(images_path=validation_path, images_masks=validation_masks_path,
                        files_path=validation_files_path, cfg=cfg, image_size=image_size,
                        batch_size=batch_size, seed=seed, shuffle=True, to_cache=False)
    elif validation_path:
        val_ds = get_ds(images_path=validation_path, images_masks=validation_masks_path,
                        files_path=validation_files_path, cfg=cfg, image_size=image_size,
                        batch_size=batch_size, seed=seed, shuffle=True, to_cache=False)
        train_ds = None
    else:
        train_ds = None
        val_ds = None

    if quantization_path:
        quantization_ds = get_ds(images_path=quantization_path, images_masks=quantization_masks_path,
                                 files_path=quantization_files_path, cfg=cfg, image_size=image_size,
                                 batch_size=1, seed=seed, shuffle=True, to_cache=False)
    elif train_ds is not None:
        # reload train_ds but with batch_size = 1, which is mandatory for tflite converter execution
        quantization_ds = get_ds(images_path=training_path, images_masks=training_masks_path,
                                 files_path=training_files_path, cfg=cfg, image_size=image_size,
                                 batch_size=1, seed=seed, shuffle=True, to_cache=False)
        if cfg.dataset.quantization_split:
            dataset_size = int(len(quantization_ds) * cfg.dataset.quantization_split)
            quantization_ds = quantization_ds.take(dataset_size)
    else:
        quantization_ds = None

    if test_path:
        test_ds = get_ds(images_path=test_path, images_masks=test_masks_path,
                         files_path=test_files_path, cfg=cfg, image_size=image_size,
                         batch_size=batch_size, seed=seed, shuffle=True, to_cache=False)
    else:
        test_ds = None

    return train_ds, val_ds, quantization_ds, test_ds
