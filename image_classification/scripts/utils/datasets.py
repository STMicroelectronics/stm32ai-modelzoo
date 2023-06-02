# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import pickle
from re import A

import scipy.io

import numpy as np
import tensorflow as tf


def get_train_val_ds(cfg, validation_split=0.2, to_cache=False):
    """ Parse Training/validation sets from the provided dataset path. """

    print("[INFO] : {} %% of the training set will be used as validation set".format(validation_split * 100))

    train_ds = tf.keras.utils.image_dataset_from_directory(
        cfg.dataset.training_path,
        validation_split=validation_split,
        label_mode="int",
        class_names=cfg.dataset.class_names,
        seed=133,
        subset="training",
        image_size=cfg.model.input_shape[:2],
        interpolation=cfg.pre_processing.resizing,
        color_mode=("rgb" if cfg.pre_processing.color_mode == "bgr" else cfg.pre_processing.color_mode),
        crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio),
        batch_size=cfg.train_parameters.batch_size)

    train_ds = train_ds.shuffle(len(list(train_ds)), reshuffle_each_iteration=True, seed=133)
    if to_cache:
        train_ds = train_ds.cache()
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    valid_ds = tf.keras.utils.image_dataset_from_directory(
        cfg.dataset.training_path,
        validation_split=validation_split,
        label_mode="int",
        class_names=cfg.dataset.class_names,
        seed=133,
        subset="validation",
        image_size=cfg.model.input_shape[:2],
        interpolation=cfg.pre_processing.resizing,
        color_mode=("rgb" if cfg.pre_processing.color_mode == "bgr" else cfg.pre_processing.color_mode),
        crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio),
        batch_size=cfg.train_parameters.batch_size)
    if to_cache:
        valid_ds = valid_ds.cache()
    valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, valid_ds


def get_ds(datapath, cfg, shuffle=False, to_cache=False):
    """ Parse dataset from the provided path. """

    ds = tf.keras.utils.image_dataset_from_directory(
        datapath,
        label_mode="int",
        class_names=cfg.dataset.class_names,
        seed=133,
        image_size=cfg.model.input_shape[:2],
        interpolation=cfg.pre_processing.resizing,
        color_mode=("rgb" if cfg.pre_processing.color_mode == "bgr" else cfg.pre_processing.color_mode),
        crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio),
        batch_size=cfg.train_parameters.batch_size)
    if shuffle:
        ds = ds.shuffle(len(list(ds)), reshuffle_each_iteration=True, seed=133)
    if to_cache:
        ds = ds.cache()
    ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return ds


def load_batch(fpath, label_key="labels"):
    """Internal utility for parsing CIFAR data. """
    with open(fpath, "rb") as f:
        d = pickle.load(f, encoding="bytes")
        # decode utf8
        d_decoded = {}
        for k, v in d.items():
            d_decoded[k.decode("utf8")] = v
        d = d_decoded
    data = d["data"]
    labels = d[label_key]

    data = data.reshape(data.shape[0], 3, 32, 32)
    return data, labels


def load_CIFAR_10(cfg, to_cache=False):
    """ Parse CIFAR 10 data set. """

    if len(cfg.dataset.class_names) != 10:
        raise ValueError('Number of classes must be 10.' f"Received: number of classes={len(cfg.dataset.class_names)}.")

    num_train_samples = 50000

    x_train = np.empty((num_train_samples, 3, 32, 32), dtype="uint8")
    y_train = np.empty((num_train_samples,), dtype="uint8")

    for i in range(1, 6):
        fpath = os.path.join(cfg.dataset.training_path, "data_batch_" + str(i))
        (
            x_train[(i - 1) * 10000: i * 10000, :, :, :],
            y_train[(i - 1) * 10000: i * 10000],
        ) = load_batch(fpath)

    fpath = os.path.join(cfg.dataset.training_path, "test_batch")
    x_test, y_test = load_batch(fpath)

    y_train = np.reshape(y_train, (len(y_train),))
    y_test = np.reshape(y_test, (len(y_test),))

    x_train = x_train.transpose(0, 2, 3, 1)
    x_test = x_test.transpose(0, 2, 3, 1)

    x_test = x_test.astype(np.uint8)
    y_test = y_test.astype(np.uint8)
    print("Found {} files belonging to {} classes.".format(len(x_train) + len(x_test), len(cfg.dataset.class_names)))
    print("Using {} files for training.".format(len(x_train)))
    print("Using {} files for validation.".format(len(x_test)))

    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(len(x_train), reshuffle_each_iteration=True, seed=133).batch(
        cfg.train_parameters.batch_size)

    valid_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    valid_ds = valid_ds.batch(cfg.train_parameters.batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        valid_ds = valid_ds.cache()

    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    if cfg.model.input_shape[:2] != [32, 32]:
        train_ds = train_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            cfg.model.input_shape[0], cfg.model.input_shape[1], interpolation=cfg.pre_processing.resizing,
            crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio), )(x), y))
        valid_ds = valid_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            cfg.model.input_shape[0], cfg.model.input_shape[1], interpolation=cfg.pre_processing.resizing,
            crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio), )(x), y))

    return train_ds, valid_ds


def load_CIFAR_100(cfg, to_cache=False):
    """ Parse CIFAR 10 data set. """

    # labeled over 100 fine-grained classes that are grouped into 20 coarse-grained classes
    if len(cfg.dataset.class_names) == 20:
        label_mode = "coarse"
    elif len(cfg.dataset.class_names) == 100:
        label_mode = "fine"
    else:
        raise ValueError(
            '`label_mode` must be one of `"fine"` for 100 classes , `"coarse"` for 20 classes. '
            f"Received: number of classes={len(cfg.dataset.class_names)}.")

    fpath = os.path.join(cfg.dataset.training_path, "train")
    x_train, y_train = load_batch(fpath, label_key=label_mode + "_labels")

    fpath = os.path.join(cfg.dataset.training_path, "test")
    x_test, y_test = load_batch(fpath, label_key=label_mode + "_labels")

    y_train = np.reshape(y_train, (len(y_train),)).astype(np.uint8)
    y_test = np.reshape(y_test, (len(y_test),)).astype(np.uint8)

    x_train = x_train.transpose(0, 2, 3, 1).astype(np.uint8)
    x_test = x_test.transpose(0, 2, 3, 1).astype(np.uint8)

    print("Found {} files belonging to {} classes.".format(len(x_train) + len(x_test), len(cfg.dataset.class_names)))
    print("Using {} files for training.".format(len(x_train)))
    print("Using {} files for validation.".format(len(x_test)))

    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(len(x_train), reshuffle_each_iteration=True, seed=133).batch(
        cfg.train_parameters.batch_size)

    valid_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    valid_ds = valid_ds.batch(cfg.train_parameters.batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        valid_ds = valid_ds.cache()

    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    if cfg.model.input_shape[:2] != [32, 32]:
        train_ds = train_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            cfg.model.input_shape[0], cfg.model.input_shape[1], interpolation=cfg.pre_processing.resizing,
            crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio), )(x), y))
        valid_ds = valid_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            cfg.model.input_shape[0], cfg.model.input_shape[1], interpolation=cfg.pre_processing.resizing,
            crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio), )(x), y))

    return train_ds, valid_ds

def load_EMNIST_Byclass(cfg, to_cache=False):
    emnist = scipy.io.loadmat(cfg.dataset.training_path)
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
    for i in range( y_train.shape[0] ):
        if y_train[i] > 35:
            remove_item.append( i )

    x_train = np.delete(x_train,remove_item,0)
    y_train = np.delete(y_train,remove_item,0)

    remove_item = []
    for i in range( y_test.shape[0] ):
        if y_test[i] > 35:
            remove_item.append( i )

    x_test = np.delete(x_test,remove_item,0)
    y_test = np.delete(y_test,remove_item,0)

    x_test = x_test.astype(np.uint8)
    y_test = y_test.astype(np.uint8)
    print("Found {} files belonging to {} classes.".format(len(x_train) + len(x_test), len(cfg.dataset.class_names)))
    print("Using {} files for training.".format(len(x_train)))
    print("Using {} files for validation.".format(len(x_test)))

    train_ds = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    train_ds = train_ds.shuffle(len(x_train), reshuffle_each_iteration=True, seed=133).batch(
        cfg.train_parameters.batch_size)

    valid_ds = tf.data.Dataset.from_tensor_slices((x_test, y_test))
    valid_ds = valid_ds.batch(cfg.train_parameters.batch_size)

    if to_cache:
        train_ds = train_ds.cache()
        valid_ds = valid_ds.cache()

    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    valid_ds = valid_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    if cfg.model.input_shape[:2] != [28, 28]:
        train_ds = train_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            cfg.model.input_shape[0], cfg.model.input_shape[1], interpolation=cfg.pre_processing.resizing,
            crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio), )(x), y))
        valid_ds = valid_ds.map(lambda x, y: (tf.keras.layers.Resizing(
            cfg.model.input_shape[0], cfg.model.input_shape[1], interpolation=cfg.pre_processing.resizing,
            crop_to_aspect_ratio=(True if cfg.pre_processing.aspect_ratio == "crop" else cfg.pre_processing.aspect_ratio), )(x), y))

    return train_ds, valid_ds
