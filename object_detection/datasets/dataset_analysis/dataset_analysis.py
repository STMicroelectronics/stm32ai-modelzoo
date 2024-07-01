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
from pathlib import Path
import hydra
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import OmegaConf
from omegaconf import DictConfig
from glob import glob
from tqdm import tqdm
from collections import Counter
from statistics import mean
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf


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


def parse_label_file(txt_file_path : str=None) -> list:
    """
    Provides detections in a list from input text file

    Args:
        txt_file_path (str) : Path of the detection file to analyze

    Returns:
        List : list of detected labels
    """
    labels = []
    if os.path.isfile(txt_file_path):
        with open(txt_file_path, "r") as f:
            data = f.readlines()   
        for line in data:
            if line.rstrip() != "":
                fields = line.split()
                labels.append([float(x) for x in fields])
    return labels


def compute_labels_stats(dataset_path : str=None, 
                         dataset_name : str=None, 
                         histogram_dir: str=None) -> None:
    """
    Provides statistics on the dataset labels

    Args:
        dataset_path (str) : Path of the dataset to analyze
        dataset_name (str) : Name of the dataset used
        histogram_dir (str): location of the histograms storage

    Returns:
        None
    """
    print("\nCalculating groundtruth labels statistics:")
    print("-----------------------------------------")
    print("Dataset root:", dataset_path)

    jpg_file_paths = glob(os.path.join(dataset_path, "*.jpg"))
    if len(jpg_file_paths) == 0:
        raise ValueError(f"Could not find any .jpg file in dataset root directory")

    num_jpg_files = len(jpg_file_paths)
    num_txt_files = 0
    num_empty_txt = 0

    label_sizes = []
    for jpg_path in tqdm(jpg_file_paths):
        txt_path = os.path.join(Path(jpg_path).parent, Path(jpg_path).stem + ".txt")
        if os.path.isfile(txt_path):
            num_txt_files += 1
            labels = parse_label_file(txt_path)
            if not labels:
                num_empty_txt += 1
                label_sizes.append(0)
            else:
                label_sizes.append(len(labels))
#            label_sizes.append(len(labels))

    print("Image files: ", num_jpg_files)
    print("Labels files:", num_txt_files)
    print("Empty labels files:", num_empty_txt)
    print("Labels per image:  min = {}, max = {}, mean = {:.2f}".
                format(min(label_sizes), max(label_sizes), mean(label_sizes)))

    plt.figure(figsize=(8, 8))
    plt.hist(label_sizes, bins=max(label_sizes))
    plot_title = "Number of labels per image"
    if dataset_name:
        plot_title += " in dataset " + dataset_name
    plt.title(plot_title)
    if histogram_dir:
        if not os.path.isdir(histogram_dir):
            os.makedirs(histogram_dir, exist_ok=True)
        plt.savefig(os.path.join(histogram_dir, "labels_stats_" + dataset_name + ".png"))
    plt.show()
    plt.close()


def compute_class_stats(dataset_path : str=None, 
                        dataset_name : str=None, 
                        histogram_dir: str=None) -> None:
    """
    Provides statistics on the dataset classes

    Args:
        dataset_path (str) : Path of the dataset to analyze
        dataset_name (str) : Name of the dataset used
        histogram_dir (str): location of the histograms storage

    Returns:
        None
    """
    print("\nCalculating groundtruth class statistics:")
    print("----------------------------------------")
    print("Dataset root:", dataset_path)
    
    jpg_file_paths = glob(os.path.join(dataset_path, "*.jpg"))
    if len(jpg_file_paths) == 0:
        raise ValueError(f"Could not find any .jpg file in dataset root directory")

    classes = []
    for jpg_path in tqdm(jpg_file_paths):
        txt_path = os.path.join(Path(jpg_path).parent, Path(jpg_path).stem + ".txt")
        if not os.path.isfile(txt_path):
            continue
        labels = parse_label_file(txt_path)
        # Skip .txt files with no objects
        if len(labels) == 0:
            continue
        for i in range(len(labels)):
            id = int(labels[i][0])
            classes.append(id)
            
    classes_dict = Counter(classes)

    class_ids = list(classes_dict.keys())
    class_ids.sort()
    num_classes = max(class_ids) + 1

    print("Number of classes:", num_classes)
    print("Occurences:")
    class_occurences = []
    for id in range(num_classes):
        n = classes_dict[id] if id in classes_dict else 0
        class_occurences.append(n)
        print(f"Class {id}: {n}")

    plt.figure(figsize=(8, 8))
    plot_title = "Class occurences"
    if dataset_name:
        plot_title += " in dataset " + dataset_name
    plt.title(plot_title)
    plt.xticks(class_ids)
    plt.bar(class_ids, class_occurences, width=0.4)
    if histogram_dir:
        if not os.path.isdir(histogram_dir):
            os.makedirs(histogram_dir, exist_ok=True)
        plt.savefig(os.path.join(histogram_dir, "classes_stats_" + dataset_name + ".png"))
    plt.show()
    plt.close()

    
def num_labels_above_cutoff(dataset_path : str=None, 
                            padded_labels_size : int=15) -> float:
    """
    Calculates the percentage of filtered images corresponding to the maximum number of detections 
    kept per image

    Args:
        dataset_path (str): Path of the dataset to analyze
        padded_labels_size (int) : The max number of detection allowed per image 

    Returns:
        float : The corresponding percentage of filtered detections
    """
    print("\nCalculating number of truncated groundtruth labels:")
    print("--------------------------------------------------")
    print("Dataset root:", dataset_path)

    if (padded_labels_size <= 0):
        print("Please make sure that you provided maximum number of detections bigger than 0")
        print("Exiting the script...")
        sys.exit()        

    jpg_file_paths = glob(os.path.join(dataset_path, "*.jpg"))
    if len(jpg_file_paths) == 0:
        raise ValueError(f"Could not find any .jpg file under dataset root {dataset_path}")

    num_examples = 0
    above_cutoff = 0
    txt_file_paths = glob(os.path.join(dataset_path, "*.txt"))
    for path in txt_file_paths:
        num_examples += 1
        labels = parse_label_file(path)
        if len(labels) > padded_labels_size:
            above_cutoff += 1

    cutoff_percentage = 100 * above_cutoff/num_examples
    print("Padded labels size:", padded_labels_size)
    print("Examples with a number of labels greater than padding size: {}/{}  ({:.2f}%)".
          format(above_cutoff, num_examples, cutoff_percentage))
    
    return (cutoff_percentage)


def num_labels_above_percentage(dataset_path : str=None, 
                                target_percentage : float=0.0) -> int:
    """
    Calculates the maximum number of detections in the input images corresponding to the max percentage 
    of the dataset to be filtered by removing images with a lot a detections

    Args:
        dataset_path (str) : Path of the dataset to analyze
        target_percentage (float) : The max percentage of the dataset to be filtered by 
                                    removing images with a lot a detections

    Returns:
        int : The corresponding maximum number of detections per image filtered.
    """
    print("\nCalculating number of truncated groundtruth labels:")
    print("--------------------------------------------------")
    print("Dataset root:", dataset_path)
    if (target_percentage < 0.0) and (target_percentage >= 100.0):
        print("Please make sure that you provided maximum percentage of images to filter between [0.0  100[")
        print("Exiting the script...")
        sys.exit()    

    jpg_file_paths = glob(os.path.join(dataset_path, "*.jpg"))
    if len(jpg_file_paths) == 0:
        raise ValueError(f"Could not find any .jpg file under dataset root {dataset_path}")

    num_examples = 0
    label_sizes = []
    txt_file_paths = glob(os.path.join(dataset_path, "*.txt"))
    for path in txt_file_paths:
        num_examples += 1
        labels = parse_label_file(path)
        if not labels:
            num_empty_txt += 1
            label_sizes.append(0)
        else:
            label_sizes.append(len(labels))

    padded_labels_size = max(label_sizes)
    above_cutoff_final = 0
    while padded_labels_size > 0:
        above_cutoff = 0
        for path in txt_file_paths:
            labels = parse_label_file(path)
            if len(labels) > padded_labels_size:
                above_cutoff += 1
        current_percentage = 100 * above_cutoff/num_examples
        if (current_percentage <= target_percentage):
            above_cutoff_final = above_cutoff
            padded_labels_size -= 1
        else:
            above_cutoff = above_cutoff_final
            break

    print("Padded labels size:", padded_labels_size+1)
    print("Examples with a number of labels greater than padding size: {}/{}  ({:.2f}%)".
          format(above_cutoff, num_examples, 100 * above_cutoff/num_examples))

    return (padded_labels_size+1)


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
    if not "dataset_path" in cfg.dataset:
        print("Please make sure that you provided a dataset path")
        print("Exiting the script...")
        sys.exit()
 
    # Set default values of missing optional attributes
    if not cfg.dataset.dataset_name:
        cfg.dataset.dataset_nameme = "<unnamed>"

    # Compute classes statistics
    compute_class_stats(dataset_path = cfg.dataset.dataset_path, 
                        dataset_name = cfg.dataset.dataset_name, 
                        histogram_dir = "histograms")

    # Compute labels statistics
    compute_labels_stats(dataset_path = cfg.dataset.dataset_path, 
                         dataset_name = cfg.dataset.dataset_name, 
                         histogram_dir = "histograms")

    # Provide statistics using max number of detections per image
    if "max_detections" in cfg.settings and (cfg.settings.max_detections != None) :
        max_detections_percentage_filtered = num_labels_above_cutoff(dataset_path = cfg.dataset.dataset_path, 
                                                padded_labels_size = cfg.settings.max_detections)

    # Provide statistics using max number of detections per image
    if "max_percentage_filtered" in cfg.settings and (cfg.settings.max_percentage_filtered != None) :
        max_detections_allowed = num_labels_above_percentage(dataset_path = cfg.dataset.dataset_path,
                                                             target_percentage = cfg.settings.max_percentage_filtered)


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
