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
from tqdm import tqdm
from typing import Tuple, List
from handposture_dictionnary import hand_posture_dict


def get_ds(data_path: str = None,
           class_names: list[str] = None,
           validation_split: float = None,
           Max_distance: float = None,
           Min_distance: float = None,
           Background_distance: float = None,
           batch_size: int = None,
           seed: int = None,
           shuffle: bool = True,
           to_cache: bool = False):

    """
    Loads the ToF frames from the given dataset root directory and returns a tf.data.Dataset.
    The dataset has the following directory structure (checked in parse_config.py):
        dataset_root_dir:
        dataset_directory/
        ...class_a/
        ......log__class_a__xxx_1/ (***)
        .........npz/
        ............data_class_a_xxx_1.npz
        ............data_class_a_xxx_2.npz
        ......log__class_a__xxx_2/
        .........npz/
        ............data_class_a_xxy_1.npz
        ............data_class_a_xxy_2.npz
        ...class_b/
        ......log__class_b__xxx_1/
        .........npz/
        ............data_class_b_xxx_1.npz
        ............data_class_b_xxx_2.npz
        ......log__class_b__xxx_2/
        .........npz/
        ............data_class_b_xxy_1.npz
        ............data_class_b_xxy_2.npz

    Args:
        data_path (str): Path to the dataset directory.
        class_names (list[str]): List of class names to use for the images.
        validation_split (float): Split ratio valid/train, 0.2 => 80% train and 20% valid
        Max_distance (float): Maximum posture distance
        Min_distance (float): Min posture distance
        Background_distance (float): Background removal distance from the closest distance of the hand
        batch_size (int): Batch size to use for the dataset.
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

    """ Parse dataset from the provided path. """

    """Data extraction from the NPZ datalogs"""

    dict_of_glob_data_fields = {
        ".GestureGT": [".GestureGT"]
    }
    dict_of_zone_data_fields = {
        "distance_mm": ["distance_mm"],
        "signal_per_spad": ["signal_per_spad"],
        "target_status": ["target_status"],
        "valid": ["valid"]}

    gdata, gheaders, zdata, zheaders = fetch_npz_data(class_names, data_path,
                                                      dict_of_glob_data_fields,
                                                      dict_of_zone_data_fields)

    """Cleaning the Frames containing a NaN"""
    input_zdata = list(dict_of_zone_data_fields.keys())
    input_gdata = list(dict_of_glob_data_fields.keys())

    X0 = np.copy(zdata[[zheaders[zd] for zd in input_zdata], :, :])
    y0 = np.copy(gdata[[gheaders[gd] for gd in input_gdata], :])
    # print(y0.shape)

    # Delete data if nan data
    zone_nan_mask = np.isnan(X0).any(axis=(0, 1))
    glob_nan_mask = np.isnan(y0).any(axis=0)
    nan_mask = np.logical_or(zone_nan_mask, glob_nan_mask)
    X1 = X0[:, :, ~nan_mask]
    y1 = y0[:, ~nan_mask]
    if len(nan_mask[nan_mask]):
        print("Dropped {} (over {}) frames because they were containing np.nan".format(len(nan_mask[nan_mask]),
                                                                                         len(nan_mask)))
    # print(X1[:,:,1])

    """BackGround + Distance Filtering based on Yaml pre_processing values"""
    (max_fields, max_zones, max_frames) = X1.shape
    index_GestureGT = list(dict_of_glob_data_fields.keys()).index(".GestureGT")
    index_distance = list(dict_of_zone_data_fields.keys()).index("distance_mm")
    index_status = list(dict_of_zone_data_fields.keys()).index("target_status")
    index_valid = list(dict_of_zone_data_fields.keys()).index("valid")
    valid_status = [5, 9]  # Sensor params - hardcoded - no need to be modified
    default_distance = 4000
    default_signal = 0
    for i in range(max_frames):
        # for i in [1]:
        min = 4000
        for j in range(max_zones):  # Num zones
            X1[index_valid, j, i] = 0
            # Valid if Target_status is ok
            if (X1[index_status, j, i] in valid_status):
                X1[index_valid, j, i] = 1
                if X1[index_distance, j, i] < min:
                    min = X1[index_distance, j, i]
        # set Nan to the frames outside of min/max
        if (min > Max_distance or min < Min_distance):
            y1[index_GestureGT, i] = np.nan
            # print("Frame Removed = ", i, "Min = ", min)
        # remove the data beyond the nearest point
        for j in range(max_zones):  # Num zones
            if (X1[index_valid, j, i] == 1):  # If valid
                if X1[index_distance, j, i] > (min + Background_distance):
                    X1[index_valid, j, i] = 0
    # Clean Frames outside min/max - set to NaN
    zone_nan_mask = np.isnan(X1).any(axis=(0, 1))
    glob_nan_mask = np.isnan(y1).any(axis=0)
    nan_mask = np.logical_or(zone_nan_mask, glob_nan_mask)
    X1 = X1[:, :, ~nan_mask]
    y1 = y1[:, ~nan_mask]
    if len(nan_mask[nan_mask]):
        print("Dropped {} (over {}) frames because the hand is outside the Min / Max defined in user_config.yaml".
              format(len(nan_mask[nan_mask]), len(nan_mask)))

    # Set unvalid zone to default values
    # unvalid zone can be fron status flag or background removal
    np.place(X1[zheaders["distance_mm"]], X1[index_valid] == 0, default_distance)
    np.place(X1[zheaders["signal_per_spad"]], X1[index_valid] == 0, default_signal)

    '''Normalization'''
    X1_norm = np.copy(X1[[zheaders["distance_mm"], zheaders["distance_mm"]]])
    X1_norm[zheaders["distance_mm"]] = (X1[zheaders["distance_mm"]] - 295) / 196
    X1_norm[zheaders["signal_per_spad"]] = (X1[zheaders["signal_per_spad"]] - 281) / 452


    '''y values change to [0,1,2,...]'''
    newdict = {key: hand_posture_dict[key] for key in class_names}
    newdict = dict(sorted(newdict.items(), key=lambda item: item[1]))
    class_names = list(newdict)
    labeldict = {newdict[key]: index for index, key in enumerate(list(newdict))}
    for i in list(labeldict):
        y1[index_GestureGT] = np.where(y1[index_GestureGT] == i,
                                       labeldict[i], y1[index_GestureGT])

    '''Reshape'''
    X1_norm_swap = np.swapaxes(X1_norm, 0, 2)
    X1_norm_reshape = X1_norm_swap.reshape((X1_norm_swap.shape[0], 8, 8, X1_norm_swap.shape[-1]))

    # debug
    y1_swap = np.reshape(np.swapaxes(y1, 0, 1), len(X1_norm_reshape))
    y1_swap = y1_swap.astype(np.uint8)
    if (len(class_names) == 2):
        y1_swap = np.expand_dims(y1_swap, axis=1)
    else:
        y1_swap = tf.keras.utils.to_categorical(y1_swap)

    '''TensorFlow TF.data'''
    data_ds = tf.data.Dataset.from_tensor_slices((X1_norm_reshape, y1_swap))
    if shuffle:
        data_ds = data_ds.shuffle(len(X1_norm_reshape), reshuffle_each_iteration=True, seed=seed)

    ds_1_size = int((1-validation_split) * len(X1_norm_reshape))

    ds_1 = data_ds.take(ds_1_size)
    ds_2 = data_ds.skip(ds_1_size)

    ds_1 = ds_1.batch(batch_size)
    ds_2 = ds_2.batch(batch_size)

    if to_cache:
        ds_1 = ds_1.cache()
        ds_2 = ds_2.cache()

    ds_1 = ds_1.prefetch(buffer_size=tf.data.AUTOTUNE)
    ds_2 = ds_2.prefetch(buffer_size=tf.data.AUTOTUNE)

    # No Split
    if validation_split == 0:
        return ds_1
    else:
        return ds_1, ds_2


def load_dataset(dataset_name: str = None,
                 training_path: str = None,
                 validation_path: str = None,
                 test_path: str = None,
                 validation_split: float = None,
                 class_names: list[str] = None,
                 Max_distance: float = None,
                 Min_distance: float = None,
                 Background_distance: float = None,
                 batch_size: int = None,
                 seed: int = None) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
    """
    Loads the images from the given dataset root directories and returns training,
    validation, and test tf.data.Datasets.
    The datasets have the following directory structure (checked in parse_config.py):
    dataset_root_dir:
        dataset_directory/
        ...class_a/
        ......log__class_a__xxx_1/ (***)
        .........npz/
        ............data_class_a_xxx_1.npz
        ............data_class_a_xxx_2.npz
        ......log__class_a__xxx_2/
        .........npz/
        ............data_class_a_xxy_1.npz
        ............data_class_a_xxy_2.npz
        ...class_b/
        ......log__class_b__xxx_1/
        .........npz/
        ............data_class_b_xxx_1.npz
        ............data_class_b_xxx_2.npz
        ......log__class_b__xxx_2/
        .........npz/
        ............data_class_b_xxy_1.npz
        ............data_class_b_xxy_2.npz

    Args:
        dataset_name (str): Name of the dataset to load.
        training_path (str): Path to the directory containing the training images.
        validation_path (str): Path to the directory containing the validation images.
        quantization_path (str): Path to the directory containing the quantization images.
        test_path (str): Path to the directory containing the test images.
        validation_split (float): Fraction of the data to use for validation.
        class_names (list[str]): List of class names to use for the images.
        image_size (tuple[int]): resizing (width, height) of input images
        Max_distance (float): Maximum posture distance
        Min_distance (float): Min posture distance
        Background_distance (float): Background removal distance from the closest distance of the hand
        batch_size (int): Batch size to use for the datasets.
        seed (int): Seed to use for shuffling the data.

    Returns:
        Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]: Training, validation, and test datasets.
    """

    num_classes = len(class_names)
    
    if training_path and not validation_path:
        # There is no validation. We split the
        # training set in two to create one.
        print("\nTraining and Validation dataset using a validation_split = {}:".format(validation_split))
        train_ds, val_ds = get_ds(
            training_path,
            class_names=class_names,
            validation_split=validation_split,
            Max_distance=Max_distance,
            Min_distance=Min_distance,
            Background_distance=Background_distance,
            batch_size=batch_size,
            seed=seed,
            shuffle=True)
    elif training_path and validation_path:
        print("Training dataset:")
        train_ds = get_ds(
            training_path,
            class_names=class_names,
            validation_split=0,
            Max_distance=Max_distance,
            Min_distance=Min_distance,
            Background_distance=Background_distance,
            batch_size=batch_size,
            seed=seed,
            shuffle=True)

        print("Validation dataset:")
        val_ds = get_ds(
            validation_path,
            class_names=class_names,
            validation_split=0,
            Max_distance=Max_distance,
            Min_distance=Min_distance,
            Background_distance=Background_distance,
            batch_size=batch_size,
            seed=seed,
            shuffle=True)
    else:
        train_ds = None
        val_ds = None


    if test_path:
        print("Test dataset:")
        test_ds = get_ds(
            test_path,
            class_names=class_names,
            validation_split=0,
            Max_distance=Max_distance,
            Min_distance=Min_distance,
            Background_distance=Background_distance,
            batch_size=batch_size,
            seed=seed,
            shuffle=True)
    else:
        test_ds = None

    return train_ds, val_ds, test_ds #quantization_ds,

"""
    This function loads data fields in dict_of_data_fields from the .npz files listed in list_of_dirs
    In case one field is not available in one .npz file, the associated data is set to np.nan
    save_to_file option will save one npz file with all data in it in PresenceEVK format style
    """
def fetch_npz_data(class_names,path,
                   dict_of_glob_data_fields,
                   dict_of_zone_data_fields,
                   expected_nb_of_zones=64,
                   save_to_file=None):

    working_dir = os.getcwd()
    dataset_path = os.path.join(working_dir, path)
    List_of_gesture_dir = [os.path.join(dataset_path, posture) for posture in class_names if posture in os.listdir(dataset_path)]
    list_of_dirs = [os.path.join(gesture_folder_path, record, "npz") for gesture_folder_path in List_of_gesture_dir for
                    record in os.listdir(gesture_folder_path)]
    npzFiles = []
    for rootdir in list_of_dirs:
        for root, dirs, files in os.walk(rootdir):
            for f in files:
                if ".npz" in f[-4:]:
                    npzFiles.append(os.path.join(root, f))
    print('{} .npz files found'.format(len(npzFiles)))
    globdata_shape = [len(dict_of_glob_data_fields), 0]
    zonedata_shape = [len(dict_of_zone_data_fields), expected_nb_of_zones, 0]
    for i, fname in enumerate(tqdm(npzFiles, desc='Analysing data shapes')):
        dataload = np.load(fname)
        globdata_shape[-1] += dataload['glob_data'].shape[-1]
        zonedata_shape[-1] += dataload['zone_data'].shape[-1]
        if dataload['zone_data'].shape[1] != expected_nb_of_zones:
            raise Exception("Wrong number of zones found in zone_data array of file {}".format(fname))
    RAMsizeGB = (int(globdata_shape[0] * globdata_shape[1]) + \
                 int(zonedata_shape[0] * zonedata_shape[1] * zonedata_shape[2])) * \
                np.zeros(1, dtype=np.float64).nbytes / float(10 ** 9)
    print('Dataset needs {} GB RAM size ({} GB is required during loading)'.format(round(RAMsizeGB, 3),
                                                                                   round(RAMsizeGB * 2, 3)))

    print('Loading {} .npz files'.format(len(npzFiles)))
    zdata = np.empty(tuple(zonedata_shape), dtype=np.float64)
    gdata = np.empty(tuple(globdata_shape), dtype=np.float64)
    zdata[:] = np.nan
    gdata[:] = np.nan
    zheaders = {zfn: i for i, zfn in enumerate(dict_of_zone_data_fields.keys())}
    gheaders = {gfn: i for i, gfn in enumerate(dict_of_glob_data_fields.keys())}
    ind = 0
    for i, fname in enumerate(tqdm(npzFiles)):
        dataload = np.load(fname)
        length = dataload['glob_data'].shape[1]

        # Load all global data fields
        for i, (fieldname, fieldnames) in enumerate(dict_of_glob_data_fields.items()):
            header_index = find_data_field_index(list(dataload['glob_head'].astype('U')), fieldnames)
            if header_index is not None:
                gdata[i, ind:ind + length] = dataload['glob_data'][header_index, :]

        # Load all zone data fields
        for i, (fieldname, fieldnames) in enumerate(dict_of_zone_data_fields.items()):
            header_index = find_data_field_index(list(dataload['zone_head'].astype('U')), fieldnames)
            if header_index is not None:
                zdata[i, :, ind:ind + length] = dataload['zone_data'][header_index, :, :]

        ind += length

    if save_to_file is not None:
        if ".HostTimestamp" in gheaders:
            np.savez_compressed(save_to_file,
                                start_tstmp=np.min(gdata[gheaders[".HostTimestamp"]]),
                                end_tstmp=np.max(gdata[gheaders[".HostTimestamp"]]),
                                zone_data=zdata,
                                glob_data=gdata,
                                zone_head=[h for h, i in sorted(zheaders.items(), key=lambda it: it[1])],
                                glob_head=[h for h, i in sorted(gheaders.items(), key=lambda it: it[1])])
        else:
            raise Exception(
                "Could not save data to file because '.HostTimestamp' does not appear in global headers and it is a mandatory field.")

    if gdata.shape[-1] != zdata.shape[-1]:
        raise Exception("Global data and zone data do not have the same number of frames. Please check datalogs.")
    elif gdata.shape[0] != len(gheaders):
        raise Exception("Global headers do not match global data matrix shape. Please check datalogs.")
    elif zdata.shape[0] != len(zheaders):
        raise Exception("Zone headers do not match zone data matrix shape. Please check datalogs.")

    return gdata, gheaders, zdata, zheaders

def find_data_field_index(list_of_fields, list_of_accepted_names, verbose=True):
    header_index = None
    for fn in list_of_accepted_names:
        try:
            header_index = list_of_fields.index(fn)
        except ValueError:
            continue
        break
    if verbose and header_index is None:
        print("Could not find one of the accepted fields\n{}\nin list\n{}".format(list_of_accepted_names, list_of_fields))
    return header_index