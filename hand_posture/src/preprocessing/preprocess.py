# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from omegaconf import DictConfig
import numpy as np
import tensorflow as tf
from typing import Tuple
import sys
import os

from models_utils import get_model_name_and_its_input_shape
from data_loader import load_dataset


def preprocess(cfg: DictConfig = None) -> Tuple:
    """
    Preprocesses the data based on the provided configuration.

    Args:
        cfg (DictConfig): Configuration object containing the settings.

    Returns:
        Tuple: A tuple containing the following:
            - data_augmentation (object): Data augmentation object.
            - augment (bool): Flag indicating whether data augmentation is enabled.
            - pre_process (object): Preprocessing object.
            - train_ds (object): Training dataset.
            - valid_ds (object): Validation dataset.
    """

    # Get the model input shape
    if cfg.general.model_path:
        _, input_shape = get_model_name_and_its_input_shape(cfg.general.model_path)
    else:
        # We are running a training using the 'training' section of the config file.
        input_shape = cfg.training.model.input_shape

    Max_distance = cfg.preprocessing.Max_distance
    Min_distance = cfg.preprocessing.Min_distance
    Background_distance = cfg.preprocessing.Background_distance


    # Set a default value to 32 for the 'evaluation' mode
    # in case a 'training' section is not available
    batch_size = cfg.training.batch_size if cfg.training else 32

    train_ds, valid_ds, test_ds = load_dataset(
        dataset_name=cfg.dataset.name,
        training_path=cfg.dataset.training_path,
        validation_path=cfg.dataset.validation_path,
        test_path=cfg.dataset.test_path,
        validation_split=cfg.dataset.validation_split,
        class_names=cfg.dataset.class_names,
        Max_distance=Max_distance,
        Min_distance=Min_distance,
        Background_distance=Background_distance,
        batch_size=batch_size,
        seed=cfg.dataset.seed)
                 
    return train_ds, valid_ds, test_ds
