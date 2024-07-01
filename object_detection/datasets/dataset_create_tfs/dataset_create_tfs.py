# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2024 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import argparse
from glob import glob
from pathlib import Path
from tqdm import tqdm
import hydra
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import OmegaConf
from omegaconf import DictConfig
from collections import Counter
from statistics import mean
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
sys.path.append(os.path.join(os.path.dirname(__file__), '../dataset_analysis'))
from dataset_analysis import num_labels_above_percentage


def get_config(config: DictConfig) -> DefaultMunch:
    """
    Converts the configuration data

    Args:
        config (DictConfig): dictionary containing the entire configuration file.

    Returns:
        DefaultMunch: The configuration object.
    """
    config_dict = OmegaConf.to_container(config)
    cfg = DefaultMunch.fromDict(config_dict)
    return cfg


def parse_label_file(txt_file_path):
    labels = []
    if os.path.isfile(txt_file_path):
        with open(txt_file_path, "r") as f:
            data = f.readlines()   
        for line in data:
            if line.rstrip() != "":
                fields = line.split()
                labels.append([float(x) for x in fields])
    return labels


def add_tfs_files_to_dataset(dataset_path : str=None, 
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
    
    jpg_file_paths = glob(os.path.join(dataset_path, "*.jpg"))
    if len(jpg_file_paths) == 0:
        raise ValueError(f"Could not find any .jpg file in dataset root directory")
    if padded_labels_size <= 0:
        raise ValueError(f"Error getting maximum number of detections")

    # Delete any existing labels serialized tensor .tfs files
    for path in glob(os.path.join(dataset_path, "*.tfs")):
        os.remove(path)
    
    missing_txt = 0
    discarded = 0
    background = 0
    
    jpg_file_paths = glob(os.path.join(dataset_path, "*.jpg"))
    num_images = len(jpg_file_paths)

    for jpg_path in tqdm(jpg_file_paths):

        base_path = os.path.join(Path(jpg_path).parent, Path(jpg_path).stem)
        txt_path = base_path + ".txt"

        if not os.path.isfile(txt_path):
            missing_txt += 1
            print(f"[INFO] Skipping example, no .txt labels file for image {jpg_path}")
            continue

        labels = parse_label_file(txt_path)
        if not labels:
            background += 1
            labels = [[0.,0.,0.,0.,0.]]

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
    print("Discarded examples due to missing .txt file: {}  ({:.1f}%)"
                   .format(missing_txt, 100*missing_txt/num_images))
    remaining = num_images - missing_txt
    print("Discarded examples due to number of labels greater than padding size: {}  ({:.1f}%)"
                   .format(discarded, 100*discarded/remaining))
    remaining -= discarded
    print("Remaining examples: {}   ({:.1f}%)".format(remaining, 100*remaining/num_images))
    print("Background images: {}   ({:.1f}%)".format(background, 100*background/remaining))


@hydra.main(version_base=None, config_path="", config_name="dataset_config")
def main(configs: DictConfig) -> None:
    """
    Main entry point of the script.
 
    Args:
        cfg: Configuration dictionary.
 
    Returns:
        None
    """
    cfg = get_config(configs)
    cfg.output_dir = HydraConfig.get().run.dir
    if not "training_path" in cfg.dataset:
        print("Please make sure that you provided at least a dataset training path")
        print("Exiting the script...")
        sys.exit()
 
    # Set default values of missing optional attributes
    if not cfg.dataset.dataset_name:
        cfg.dataset.dataset_name = "<unnamed>"

    if "max_detections" in cfg.settings and (cfg.settings.max_detections != None) :
        max_detections = cfg.settings.max_detections
    else:
        # Computes the maximum number of detections in current training dataset and assign it
        max_detections = num_labels_above_percentage(dataset_path = cfg.dataset.training_path, 
                                                     target_percentage = 0.0)

    # Add tfs files to the training dataset
    add_tfs_files_to_dataset(dataset_path = cfg.dataset.training_path, 
                             padded_labels_size = max_detections)

    # Add tfs files to the validation dataset if present
    if "validation_path" in cfg.dataset and (cfg.dataset.validation_path != None) :
        add_tfs_files_to_dataset(dataset_path = cfg.dataset.validation_path, 
                                 padded_labels_size = max_detections)

    # Add tfs files to the test dataset if present
    if "test_path" in cfg.dataset and (cfg.dataset.test_path != None) :
        add_tfs_files_to_dataset(dataset_path = cfg.dataset.test_path, 
                                 padded_labels_size = max_detections)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=str, default='', help='Path to folder containing configuration file')
    parser.add_argument('--config-name', type=str, default='user_config', help='name of the configuration file')
    
    # Add arguments to the parser
    parser.add_argument('params', nargs='*',
                        help='List of parameters to over-ride in config.yaml')
    args = parser.parse_args()

    # Call the main function
    main()
