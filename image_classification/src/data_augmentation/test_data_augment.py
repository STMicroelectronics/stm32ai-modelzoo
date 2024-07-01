# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from pathlib import Path
import argparse
import yaml
from yaml.loader import SafeLoader
from omegaconf import OmegaConf
from munch import DefaultMunch
import tensorflow as tf
import matplotlib.pyplot as plt
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../preprocessing'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../models'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../common/utils'))

from models_utils import get_model_name_and_its_input_shape
from models_mgt import IC_CUSTOM_OBJECTS
from parse_config import get_config
from data_loader import get_ds
from random_utils import remap_pixel_values_range
from data_augmentation import data_augmentation


def update_path(path: str):
    """
    Paths in the configuration file are set to run stm32ai_main.py
    in the src/ directory. But test_data_augment.py is run in 
    src/data_augmentation, so we need to update the paths.
    """
    if not os.path.isabs(path):
        return os.path.join(Path(".."), Path(path))
    else:
        return path


def view_images(images: List, images_aug: List, pixels_range=(0, 1)):
    """
    This function displays the original and augmented images side by side.

    Args:
        images (Tuple): original images.
        images_aug (Tuple): corresponding augmented images.
        pixels_range (Tuple): range of pixel values of the images.
    
    Returns:
        None
    """
    images = remap_pixel_values_range(images, pixels_range, (0, 1))
    images_aug = remap_pixel_values_range(images_aug, pixels_range, (0, 1))

    for i in range(len(images)):        
        f = plt.figure()
        f.add_subplot(1, 2, 1)
        plt.imshow(images[i], cmap='gray')
        plt.title("original")
        f.add_subplot(1, 2, 2)
        plt.imshow(images_aug[i], cmap='gray')
        plt.title("augmented")
        plt.show(block=True)
        plt.close()
        

def test_data_augmentation(config_file_path: str, num_images: int = 8, seed_arg: str = None) -> None:
    """
    This function parses the configuration file. Then, it samples a batch of images
    from the training set, applies the data augmentation functions to them, and 
    displays the original images and corresponding augmented images side-by-side.

    Arguments:
        config_file_path (str): path to the configuration file
        num_images (int): number of images to augment and display. Defaults to 8.
        seed_args (int): seed passed in argument, optional.

    Returns:
        None
    """

    # Load the configuration file
    config = OmegaConf.load(config_file_path)

    # Check the operation_mode attribute. We must be in a mode that 
    # includes a training to get the configuration file correctly.
    message = "\nPlease check your configuration file."
    if "operation_mode" not in config or config.operation_mode not in ("training", "chain_tbqeb", "chain_tqe"):
        raise ValueError("\nExpecting `operation_mode` attribute set to either 'training', "
                         f"'chain_tbqeb' or 'chain_tqe'{message}")

    if "data_augmentation" not in config or not config.data_augmentation:
        raise ValueError(f"\nMissing a `data_augmentation` section{message}")

    if "general" in config and "model_path" in config.general:
        config.general.model_path = update_path(config.general.model_path)

    # Git rid of validation_path and test_path.
    # If they are set, the datasets would be checked and loaded.
    if "dataset" in config:
        cds = config.dataset
        if "training_path" in cds:
            cds.training_path = update_path(cds.training_path)
        cds.validation_path = None
        cds.test_path = None

    # Parse the configuration file
    cfg = get_config(config)

    # Get the model input shape
    if cfg.training.model:
        input_shape = cfg.training.model.input_shape
    else:
        _, input_shape = get_model_name_and_its_input_shape(cfg.general.model_path, custom_objects=IC_CUSTOM_OBJECTS)

    if seed_arg:
        # Use the seed passed in argument
        seed = None if seed_arg in ("None", "none") else int(seed_arg)
    else:
        # Use the seed from the configuration file
        seed = 123 if not cfg.dataset.seed else int(cfg.dataset.seed)

    # Create a data loader and get a batch of images
    cpp = cfg.preprocessing
    data_loader = get_ds(
            cfg.dataset.training_path,
            class_names=cfg.dataset.class_names,
            image_size=input_shape[0:2],
            interpolation=cpp.resizing.interpolation,
            aspect_ratio=cpp.resizing.aspect_ratio,
            color_mode=cpp.color_mode,
            batch_size=num_images,
            seed=seed,
            shuffle=True)
    images, _ = iter(data_loader).next()

    # Rescale the images
    scale = cpp.rescaling.scale
    offset = cpp.rescaling.offset
    images = scale * tf.cast(images, tf.float32) + offset

    # Apply the data augmentation functions and view before/after images side-by-side
    pixels_range = offset, 255*scale + offset
    images_aug = data_augmentation(images, config=cfg.data_augmentation.config, pixels_range=pixels_range)
    view_images(images, images_aug, pixels_range=pixels_range)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, default="user_config.yaml",
                        help="Path to the YAML configuration file from the directory above. Default: user_config.yaml")
    parser.add_argument("--num_images", type=int, default=8,
                        help="Number of images to sample and augment. Default: 8")
    parser.add_argument("--seed", type=str, default="",
                        help="Seed to use to sample the images from the dataset. " +
                              "If not set, the seed from the 'dataset' section of the configuration file is used.")
    
    args = parser.parse_args()

    test_data_augmentation(update_path(args.config_file), num_images=args.num_images, seed_arg=args.seed)


if __name__ == '__main__':
    main()

