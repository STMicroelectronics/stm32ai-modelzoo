# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import string
import pickle
import scipy.io
import numpy as np
import tensorflow as tf
from typing import Tuple, List


def load_cifar_batch(fpath, label_key="labels") -> Tuple:
    """
    Internal utility for parsing CIFAR data.

    Args:
        fpath (str): File path of the CIFAR data batch.
        label_key (str, optional): Key name for the labels in the CIFAR data. Defaults to "labels".

    Returns:
        data (numpy.ndarray): CIFAR data.
        labels (numpy.ndarray): Labels corresponding to the CIFAR data.
    """
    with open(fpath, "rb") as f:
        d = pickle.load(f, encoding="bytes")

        # Decode utf8 keys
        d_decoded = {}
        for k, v in d.items():
            d_decoded[k.decode("utf8")] = v
        d = d_decoded

    data = d["data"]
    labels = d[label_key]

    # Reshape the data array
    data = data.reshape(data.shape[0], 3, 32, 32)

    return data, labels


def load_cifar_10(training_path: str, num_classes: int = None, input_size: list = None,
                  interpolation: str = None, aspect_ratio: str = None,
                  batch_size: int = None, seed: int = None, to_cache: bool = False) -> Tuple:
    """
    Loads the CIFAR-10 dataset and returns two TensorFlow datasets for training and validation.

    Args:
        training_path (str): The path to the CIFAR-10 training data.
        num_classes (int, optional): The number of classes in the dataset. Must be 10. Defaults to None.
        input_size (list, optional): The size of the input images. Defaults to None.
        interpolation (str, optional): The interpolation method to use when resizing images. Defaults to None.
        aspect_ratio (bool, optional): Whether to crop images to maintain the aspect ratio. Defaults to None.
        batch_size (int, optional): The batch size for the datasets. Defaults to None.
        to_cache (bool, optional): Whether to cache the datasets in memory. Defaults to False.

    Returns:
        tuple: A tuple of two TensorFlow datasets for training and validation.
    """
    # When calling this function using the config file data, some of the arguments
    # may be used but equal to None (happens when an attribute is missing in the
    # config file or has no value). For this reason, all the arguments in the
    # definition of the function defaults to None and we set default values here
    # in case the function is called in another context with missing arguments.

    # Set default values for optional arguments
    interpolation = interpolation if interpolation else "bilinear"
    aspect_ratio = aspect_ratio if aspect_ratio else "fit"
    batch_size = batch_size if batch_size else 32

    input_size = list(input_size)

    if num_classes != 10:
        raise ValueError('Number of classes must be 10.' f"Received: number of classes={num_classes}.")

    num_train_samples = 50000

    x_train = np.empty((num_train_samples, 3, 32, 32), dtype="uint8")
    y_train = np.empty((num_train_samples,), dtype="uint8")

    for i in range(1, 6):
        fpath = os.path.join(training_path, "data_batch_" + str(i))
        (
            x_train[(i - 1) * 10000: i * 10000, :, :, :],
            y_train[(i - 1) * 10000: i * 10000],
        ) = load_cifar_batch(fpath)

    fpath = os.path.join(training_path, "test_batch")
    x_test, y_test = load_cifar_batch(fpath)

    y_train = np.reshape(y_train, (len(y_train),))
    y_test = np.reshape(y_test, (len(y_test),))

    x_train = x_train.transpose(0, 2, 3, 1)
    x_test = x_test.transpose(0, 2, 3, 1)

    x_test = x_test.astype(np.uint8)
    y_test = y_test.astype(np.uint8)
    print("Found {} files belonging to {} classes.".format(len(x_train) + len(x_test), num_classes))
    print("Using {} files for training.".format(len(x_train)))
    print("Using {} files for validation.".format(len(x_test)))

    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(len(x_train), reshuffle_each_iteration=True, seed=seed).batch(batch_size)

    valid_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    valid_ds = valid_ds.batch(batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        valid_ds = valid_ds.cache()

    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    if input_size != [32, 32]:
        crop_to_aspect_ratio = False if aspect_ratio == "fit" else True
        train_ds = train_ds.map(
            lambda x, y: (tf.keras.layers.Resizing(
                input_size[0], input_size[1],
                interpolation=interpolation,
                crop_to_aspect_ratio=crop_to_aspect_ratio
            )(x), y))

        valid_ds = valid_ds.map(
            lambda x, y: (tf.keras.layers.Resizing(
                input_size[0], input_size[1],
                interpolation=interpolation,
                crop_to_aspect_ratio=crop_to_aspect_ratio
            )(x), y))

    return train_ds, valid_ds


def load_cifar_100(training_path: str, num_classes: int = None, input_size: list = None,
                   interpolation: str = None, aspect_ratio: str = None,
                   batch_size: int = None, seed: int = None, to_cache: bool = False) -> tuple:
    """
    Loads the CIFAR-100 dataset and returns two TensorFlow datasets for training and validation.

    Args:
        training_path (str): The path to the CIFAR-100 training data.
        num_classes (int, optional): The number of classes in the dataset. Must be 20 or 100. Defaults to None.
        input_size (list, optional): The size of the input images. Defaults to None.
        interpolation (str, optional): The interpolation method to use when resizing images. Defaults to None.
        aspect_ratio (bool, optional): Whether to crop images to maintain the aspect ratio. Defaults to None.
        batch_size (int, optional): The batch size for the datasets. Defaults to None.
        to_cache (bool, optional): Whether to cache the datasets in memory. Defaults to False.

    Returns:
        tuple: A tuple of two TensorFlow datasets for training and validation.
    """
    # When calling this function using the config file data, some of the arguments
    # may be used but equal to None (happens when an attribute is missing in the
    # config file or has no value). For this reason, all the arguments in the
    # definition of the function defaults to None and we set default values here
    # in case the function is called in another context with missing arguments.

    interpolation = interpolation if interpolation else "bilinear"
    aspect_ratio = aspect_ratio if aspect_ratio else "fit"
    batch_size = batch_size if batch_size else 32

    input_size = list(input_size)

    # Labeled over 100 fine-grained classes that are grouped into 20 coarse-grained classes
    if num_classes == 20:
        label_mode = "coarse"
    elif num_classes == 100:
        label_mode = "fine"
    else:
        raise ValueError(
            '`label_mode` must be one of `"fine"` for 100 classes , `"coarse"` for 20 classes. '
            f"Received: number of classes={num_classes}.")

    fpath = os.path.join(training_path, "train")
    x_train, y_train = load_cifar_batch(fpath, label_key=label_mode + "_labels")

    fpath = os.path.join(training_path, "test")
    x_test, y_test = load_cifar_batch(fpath, label_key=label_mode + "_labels")

    y_train = np.reshape(y_train, (len(y_train),)).astype(np.uint8)
    y_test = np.reshape(y_test, (len(y_test),)).astype(np.uint8)

    x_train = x_train.transpose(0, 2, 3, 1).astype(np.uint8)
    x_test = x_test.transpose(0, 2, 3, 1).astype(np.uint8)

    print("Found {} files belonging to {} classes.".format(len(x_train) + len(x_test), num_classes))
    print("Using {} files for training.".format(len(x_train)))
    print("Using {} files for validation.".format(len(x_test)))

    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(len(x_train), reshuffle_each_iteration=True, seed=seed).batch(batch_size)

    valid_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    valid_ds = valid_ds.batch(batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        valid_ds = valid_ds.cache()

    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    if input_size != [32, 32]:
        crop_to_aspect_ratio = False if aspect_ratio == "fit" else True
        train_ds = train_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            input_size[0], input_size[1],
            interpolation=interpolation,
            crop_to_aspect_ratio=crop_to_aspect_ratio
        )(x), y))

        valid_ds = valid_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            input_size[0], input_size[1],
            interpolation=interpolation,
            crop_to_aspect_ratio=crop_to_aspect_ratio
        )(x), y))

    return train_ds, valid_ds


def load_emnist_by_class(training_path: str,
                         num_classes: int = None,
                         input_size: list[int] = None,
                         interpolation: str = None,
                         aspect_ratio: str = None,
                         batch_size: int = None,
                         seed: int = None,
                         to_cache: bool = False) -> Tuple[tf.data.Dataset, tf.data.Dataset]:
    """
    Loads the EMNIST dataset by class and returns training and validation datasets.

    Args:
        training_path (str): Path to the EMNIST dataset file.
        num_classes (int): Number of classes to use from the dataset.
        input_size (list[int]): Size of the input images to resize them to.
        interpolation (str): Interpolation method to use when resizing the images.
        aspect_ratio (bool): Whether or not to crop the images to the specified aspect ratio.
        batch_size (int): Batch size to use for training and validation.
        to_cache (bool): Whether or not to cache the datasets.

    Returns:
        Tuple[tf.data.Dataset, tf.data.Dataset]: Training and validation datasets.
    """
    # When calling this function using the config file data, some of the arguments
    # may be used but equal to None (happens when an attribute is missing in the
    # config file or has no value). For this reason, all the arguments in the
    # definition of the function defaults to None and we set default values here
    # in case the function is called in another context with missing arguments.

    interpolation = interpolation if interpolation else "bilinear"
    aspect_ratio = aspect_ratio if aspect_ratio else "fit"
    batch_size = batch_size if batch_size else 32

    input_size = list(input_size)

    first_matlab_file = list(filter(lambda x : x[-4:]==".mat",os.listdir(training_path)))[0]

    training_path = os.path.join(training_path,first_matlab_file)

    emnist = scipy.io.loadmat(training_path)
    x_train = emnist["dataset"][0][0][0][0][0][0]
    y_train = emnist["dataset"][0][0][0][0][0][1]
    x_test = emnist["dataset"][0][0][1][0][0][0]
    y_test = emnist["dataset"][0][0][1][0][0][1]

    x_train = x_train.astype(np.float32)
    x_test = x_test.astype(np.float32)

    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1, order='F')
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1, order='F')
    y_train = y_train.reshape(y_train.shape[0])
    y_test = y_test.reshape(y_test.shape[0])

    remove_item = []
    for i in range(y_train.shape[0]):
        if y_train[i] > 35:
            remove_item.append(i)

    x_train = np.delete(x_train, remove_item, 0)
    y_train = np.delete(y_train, remove_item, 0)

    remove_item = []
    for i in range(y_test.shape[0]):
        if y_test[i] > 35:
            remove_item.append(i)

    x_test = np.delete(x_test, remove_item, 0)
    y_test = np.delete(y_test, remove_item, 0)

    x_test = x_test.astype(np.uint8)
    y_test = y_test.astype(np.uint8)
    print("Found {} files belonging to {} classes.".format(len(x_train) + len(x_test), num_classes))
    print("Using {} files for training.".format(len(x_train)))
    print("Using {} files for validation.".format(len(x_test)))

    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(len(x_train), reshuffle_each_iteration=True, seed=seed).batch(batch_size)

    valid_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    valid_ds = valid_ds.batch(batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        valid_ds = valid_ds.cache()

    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    if input_size != [28, 28]:
        crop_to_aspect_ratio = False if aspect_ratio == "fit" else True
        train_ds = train_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            input_size[0], input_size[1],
            interpolation=interpolation,
            crop_to_aspect_ratio=crop_to_aspect_ratio
        )(x), y))
        valid_ds = valid_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            input_size[0], input_size[1],
            interpolation=interpolation,
            crop_to_aspect_ratio=crop_to_aspect_ratio
        )(x), y))

    return train_ds, valid_ds


def check_dataset_integrity(dataset_root_dir: str, check_image_files: bool = False) -> None:
    """
    This function checks that a dataset has the following directory structure:
        dataset_root_dir:
            class_a:
                a_image_1.jpg
                a_image_2.jpg
            class_b:
                b_image_1.jpg
                b_image_2.jpg
    If the `check_images` argument is set to True, an attempt is made to load each 
    image file. If a file fails the test, it is reported together with the list of
    supported image formats.

    Args:
        dataset_root_dir (str): the root directory of the dataset.
        check_images (bool): if set to True, an attempt is made to load each image file.

    Returns:
        None

    Errors:
        - The root directory of the dataset provided in argument cannot be found.
        - A class directory contains a subdirectory (should be files only).
        - An image file cannot be loaded.
    """

    message = ["The directory structure should be:",
               "    dataset_root:",
               "       class_a:",
               "          a_image_1.jpg",
               "          a_image_2.jpg",
               "       class_b:",
               "          b_image_1.jpg",
               "          b_image_2.jpg"]
    message = ('\n').join(message)

    class_dir_paths = []
    for x in os.listdir(dataset_root_dir):
        path = os.path.join(dataset_root_dir, x)
        if os.path.isdir(path):
            class_dir_paths.append(path)

    if not class_dir_paths:
        raise ValueError("\nExpecting subdirectories under dataset root "
                         f"directory {dataset_root_dir}\n{message}")
    
    image_paths = []
    for class_dir in class_dir_paths:
        for x in os.listdir(class_dir):
            path = os.path.join(class_dir, x)
            if os.path.isdir(path):
                raise ValueError("\nClass directories should only contain image files.\n"
                                 f"Found subdirectory {path}\n{message}")
            image_paths.append(path)

    # Try to load each image file if it was requested
    if check_image_files:
        for im_path in image_paths:
            try:
                data = tf.io.read_file(im_path)
            except:
                raise ValueError(f"\nUnable to read file {im_path}\nThe file may be corrupt.")
            try:
                tf.image.decode_image(data, channels=3)
            except:
                raise ValueError(f"\nUnable to read image file {im_path}\n"
                                 "Supported image file formats are JPEG, PNG, GIF and BMP.")


def get_path_dataset(path : str,
                     class_names : list[str],
                     seed : int,
                     shuffle : bool = True) -> tf.data.Dataset:
    """
    Creates a tf.data.Dataset from a dataset root directory path.
    The dataset has the following directory structure (checked in parse_config.py):
        dataset_root_dir:
            class_a:
                a_image_1.jpg
                a_image_2.jpg
            class_b:
                b_image_1.jpg
                b_image_2.jpg

    Args:
        path (str): Path of the dataset folder.
        class_names (list(str)): List of the classes names.
        seed (int): seed when performing shuffle.
        shuffle (bool): Shuffle the dataset.

    Returns:
        dataset(tf.data.Dataset) -> dataset with a tuple (path, label) of each sample. 
    """

    data_list = []
    labels = os.listdir(path)

    for label in class_names:
        assert label in labels, f"[ERROR] label {label} not found in {path}"

    for idx, label in enumerate(sorted(class_names)):
        imgs = os.listdir(os.path.join(path, label))
        data_list.extend(sorted([(os.path.join(path,label,img), idx) for img in imgs]))

    if shuffle:
        rng = np.random.RandomState(seed)
        rng.shuffle(data_list)
    
    imgs, labels = zip(*data_list)
    dataset = tf.data.Dataset.from_tensor_slices((list(imgs), list(labels)))

    return dataset


def preprocess_function(data_x : tf.Tensor,
                        data_y : tf.Tensor,
                        image_size: tuple[int],
                        interpolation: str,
                        aspect_ratio: str,
                        color_mode: str,
                        label_mode: str,
                        num_classes: int) -> tuple[tf.Tensor, tf.Tensor]:
    """
    Load images from path and apply necessary transformations.
    """
    width, height = image_size
    channels = 1 if color_mode == "grayscale" else 3

    image = tf.io.read_file(data_x)
    image = tf.image.decode_image(image, channels=channels, expand_animations=False)
    if aspect_ratio == "fit":
        image = tf.image.resize(image, [height, width], method=interpolation, preserve_aspect_ratio=False)
    else:
        image = tf.image.resize_with_crop_or_pad(image, height, width)

    if label_mode == "categorical":
        data_y = tf.keras.utils.to_categorical(data_y, num_classes)
        
    return image, data_y


def get_train_val_ds(training_path: str,
                     image_size: tuple[int] = None,
                     label_mode: str = None,
                     class_names: list[str] = None,
                     interpolation: str = None,
                     aspect_ratio: str = None,
                     color_mode: str = None,
                     validation_split: float = None,
                     batch_size: int = None,
                     seed: int = None,
                     shuffle: bool = True,
                     to_cache: bool = False) -> Tuple[tf.data.Dataset, tf.data.Dataset]:
    """
    Loads the images under a given dataset root directory and returns training 
    and validation tf.Data.datasets.
    The dataset has the following directory structure (checked in parse_config.py):
        dataset_root_dir:
            class_a:
                a_image_1.jpg
                a_image_2.jpg
            class_b:
                b_image_1.jpg
                b_image_2.jpg

    Args:
        training_path (str): Path to the directory containing the training images.
        image_size (tuple[int]): Size of the input images to resize them to.
        label_mode (str): Mode for generating the labels for the images.
        class_names (list[str]): List of class names to use for the images.
        interpolation (float): Interpolation method to use when resizing the images.
        aspect_ratio (bool): Whether or not to crop the images to the specified aspect ratio.
        color_mode (str): Color mode to use for the images.
        validation_split (float): Fraction of the data to use for validation.
        batch_size (int): Batch size to use for training and validation.
        seed (int): Seed to use for shuffling the data.
        shuffle (bool): Whether or not to shuffle the data.
        to_cache (bool): Whether or not to cache the datasets.

    Returns:
        Tuple[tf.data.Dataset, tf.data.Dataset]: Training and validation datasets.
    """
    # When calling this function using the config file data, some of the arguments
    # may be used but equal to None (happens when an attribute is missing in the
    # config file or has no value). For this reason, all the arguments in the
    # definition of the function defaults to None and we set default values here
    # in case the function is called in another context with missing arguments.

    label_mode = label_mode if label_mode else "int"
    interpolation = interpolation if interpolation else "bilinear"
    aspect_ratio = aspect_ratio if aspect_ratio else "fit"
    color_mode = color_mode if color_mode else "rgb"
    validation_split = validation_split if validation_split else 0.2
    batch_size = batch_size if batch_size else 32

    preprocess_params = (image_size, 
                         interpolation,
                         aspect_ratio,
                         color_mode,
                         label_mode,
                         len(class_names))

    dataset = get_path_dataset(training_path, class_names, seed=seed)

    train_size = int(len(dataset)*(1-validation_split))
    train_ds = dataset.take(train_size)
    val_ds = dataset.skip(train_size)

    if shuffle:
        train_ds = train_ds.shuffle(len(train_ds), reshuffle_each_iteration=True, seed=seed)
    
    train_ds = train_ds.map(lambda *data : preprocess_function(*data,*preprocess_params))
    val_ds = val_ds.map(lambda *data : preprocess_function(*data,*preprocess_params))
    
    train_ds = train_ds.batch(batch_size)
    val_ds = val_ds.batch(batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        val_ds = val_ds.cache()
    
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds


def get_ds(data_path: str = None,
           label_mode: str = None,
           class_names: list[str] = None,
           image_size: tuple[int] = None,
           interpolation: str = None,
           aspect_ratio: str = None,
           color_mode: str = None,
           batch_size: int = None,
           seed: int = None,
           shuffle: bool = True,
           to_cache: bool = False) -> tf.data.Dataset:
    """
    Loads the images from the given dataset root directory and returns a tf.data.Dataset.
    The dataset has the following directory structure (checked in parse_config.py):
        dataset_root_dir:
            class_a:
                a_image_1.jpg
                a_image_2.jpg
            class_b:
                b_image_1.jpg
                b_image_2.jpg

    Args:
        data_path (str): Path to the directory containing the images.
        label_mode (str): Mode for generating the labels for the images.
        class_names (list[str]): List of class names to use for the images.
        image_size (tuple[int]): Size of the input images to resize them to.
        interpolation (str): Interpolation method to use when resizing the images.
        aspect_ratio (bool): Whether or not to crop the images to the specified aspect ratio.
        color_mode (str): Color mode to use for the images.
        batch_size (int): Batch size to use for the dataset.
        seed (int): Seed to use for shuffling the data.
        shuffle (bool): Whether or not to shuffle the data.
        to_cache (bool): Whether or not to cache the dataset.

    Returns:
        tf.data.Dataset: Dataset containing the images.
    """
    # When calling this function using the config file data, some of the arguments
    # may be used but equal to None (happens when an attribute is missing in the
    # config file or has no value). For this reason, all the arguments in the
    # definition of the function defaults to None and we set default values here
    # in case the function is called in another context with missing arguments.

    label_mode = label_mode if label_mode else "int"
    interpolation = interpolation if interpolation else "bilinear"
    aspect_ratio = aspect_ratio if aspect_ratio else "fit"
    color_mode = color_mode if color_mode else "rgb"
    batch_size = batch_size if batch_size else 32

    preprocess_params = (image_size, 
                         interpolation,
                         aspect_ratio,
                         color_mode,
                         label_mode,
                         len(class_names))
    
    dataset = get_path_dataset(data_path, class_names, seed=seed)

    if shuffle:
        dataset = dataset.shuffle(len(dataset), reshuffle_each_iteration=True, seed=seed)
    
    dataset = dataset.map(lambda *data : preprocess_function(*data, *preprocess_params))
    dataset = dataset.batch(batch_size)

    if to_cache:
        dataset = dataset.cache()
    
    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)

    return dataset


def load_dataset(dataset_name: str = None,
                 training_path: str = None,
                 validation_path: str = None,
                 quantization_path: str = None,
                 test_path: str = None,
                 validation_split: float = None,
                 class_names: list[str] = None,
                 image_size: tuple[int] = None,
                 interpolation: str = None,
                 aspect_ratio: str = None,
                 color_mode: str = None,
                 batch_size: int = None,
                 seed: int = None) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
    """
    Loads the images from the given dataset root directories and returns training,
    validation, and test tf.data.Datasets.
    The datasets have the following directory structure (checked in parse_config.py):
        dataset_root_dir:
            class_a:
                a_image_1.jpg
                a_image_2.jpg
            class_b:
                b_image_1.jpg
                b_image_2.jpg

    Args:
        dataset_name (str): Name of the dataset to load.
        training_path (str): Path to the directory containing the training images.
        validation_path (str): Path to the directory containing the validation images.
        quantization_path (str): Path to the directory containing the quantization images.
        test_path (str): Path to the directory containing the test images.
        validation_split (float): Fraction of the data to use for validation.
        class_names (list[str]): List of class names to use for the images.
        image_size (tuple[int]): resizing (width, height) of input images
        interpolation (str): Interpolation method to use when resizing the images.
        aspect_ratio (bool): Whether or not to crop the images to the specified aspect ratio.
        color_mode (str): Color mode to use for the images.
        batch_size (int): Batch size to use for the datasets.
        seed (int): Seed to use for shuffling the data.

    Returns:
        Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]: Training, validation, and test datasets.
    """

    num_classes = len(class_names)
    
    if dataset_name == "cifar10":
        # Load CIFAR-10 dataset
        train_ds, val_ds = load_cifar_10(
            training_path,
            num_classes=num_classes,
            input_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            batch_size=batch_size,
            seed=seed,
            to_cache=False)
    elif dataset_name == "cifar100":
        # Load CIFAR-100 dataset
        train_ds, val_ds = load_cifar_100(
            training_path,
            num_classes=num_classes,
            input_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            batch_size=batch_size,
            seed=seed,
            to_cache=False)
    elif dataset_name == "emnist":
        # Load EMNIST-ByClass dataset
        train_ds, val_ds = load_emnist_by_class(
            training_path,
            num_classes=num_classes,
            input_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            batch_size=batch_size,
            to_cache=False)
    elif training_path and not validation_path:
        # There is no validation. We split the
        # training set in two to create one.
        train_ds, val_ds = get_train_val_ds(
            training_path,
            class_names=class_names,
            image_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            color_mode=color_mode,
            validation_split=validation_split,
            batch_size=batch_size,
            seed=seed)
    elif training_path and validation_path:
        train_ds = get_ds(
            training_path,
            class_names=class_names,
            image_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            color_mode=color_mode,
            batch_size=batch_size,
            seed=seed)

        val_ds = get_ds(
            validation_path,
            class_names=class_names,
            image_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            color_mode=color_mode,
            batch_size=batch_size,
            seed=seed)
    else:
        train_ds = None
        val_ds = None

    if quantization_path:
        quantization_ds = get_ds(
            quantization_path,
            class_names=class_names,
            image_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            color_mode=color_mode,
            batch_size=batch_size,
            seed=seed)
    else:
        quantization_ds = None

    if test_path:
        test_ds = get_ds(
            test_path,
            class_names=class_names,
            image_size=image_size,
            interpolation=interpolation,
            aspect_ratio=aspect_ratio,
            color_mode=color_mode,
            batch_size=batch_size,
            seed=seed)
    else:
        test_ds = None

    return train_ds, val_ds, quantization_ds, test_ds
