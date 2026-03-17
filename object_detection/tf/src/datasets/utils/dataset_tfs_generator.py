# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
from glob import glob
from pathlib import Path
from tqdm import tqdm
from statistics import mean
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from .dataset_analyzers import parse_label_file

def add_tfs_files_to_dataset(dataset_path : str=None,
                             exclude_unlabeled_images : bool=False,
                             padded_labels_size : int=0) -> None:
    """
    Creates .tfs files filtering images with the number of detections above the padded_labels_size value.

    Args:
        dataset_path (str): Path of the dataset to analyze
        padded_labels_size (int) : The max number of detection allowed per image

    Returns:
        None
    """
    print("\nAdding .tfs labels files to dataset:")
    print("----------------------------------")
    print("Dataset root:", dataset_path)
    print("Padded labels size:", padded_labels_size)

    jpg_file_paths = glob.glob(os.path.join(dataset_path, "*.jpg"))
    if len(jpg_file_paths) == 0:
        raise ValueError(f"Could not find any .jpg file in dataset root directory")
    if padded_labels_size <= 0:
        raise ValueError(f"Error getting maximum number of detections")

    # Delete any existing labels serialized tensor .tfs files
    for path in glob.glob(os.path.join(dataset_path, "*.tfs")):
        os.remove(path)

    discarded = 0
    background = 0

    jpg_file_paths = glob.glob(os.path.join(dataset_path, "*.jpg"))
    num_images = len(jpg_file_paths)

    for jpg_path in tqdm(jpg_file_paths):

        base_path = os.path.join(Path(jpg_path).parent, Path(jpg_path).stem)
        txt_path = base_path + ".txt"

        labels = parse_label_file(txt_path)
        if not labels:
            background += 1
            if exclude_unlabeled_images==False:
                labels = [[0.,0.,0.,0.,0.]]
            else:
                print(f"[INFO] Skipping background image {jpg_path}")
                continue

        # Discard examples with a number of labels
        # that is greater than the padding size
        if len(labels) > padded_labels_size:
            discarded += 1
            continue

        # Pad labels to the target size
        padded_labels = []
        for i in range(padded_labels_size):
            if i < len(labels):
                padded_labels.append(labels[i])
            else:
                padded_labels.append([0.,0.,0.,0.,0.])

        # Save the padded labels as TF tensor strings
        data = tf.convert_to_tensor(padded_labels, dtype=tf.float32)
        data = tf.io.serialize_tensor(data)
        tf.io.write_file(base_path + ".tfs", data)

    print("Number of image files:", num_images)
    if exclude_unlabeled_images == True:
        remaining = num_images - background
    else:
        remaining = num_images
    print("Discarded examples due to number of labels greater than padding size: {}  ({:.1f}%)".format(discarded, 100*discarded/remaining))
    remaining -= discarded
    print("Remaining examples: {}   ({:.1f}%)".format(remaining, 100*remaining/num_images))
    print("Background images: {}   ({:.1f}%)".format(background, 100*background/num_images))
