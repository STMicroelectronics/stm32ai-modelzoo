# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from tensorflow import keras
from tensorflow.keras import layers
from preprocessing_pkg import RandomSaturation, RandomHue, RandomBrightness, RandomShear


def get_data_augmentation(cfg):
    """ Define Sequential data-augmentation layers model. """

    augment = False
    for key, value in cfg.data_augmentation.items():
        if value:
            augment = True
    augmentation_layers = []
    if cfg.data_augmentation.RandomFlip:
        augmentation_layers.append(layers.RandomFlip(cfg.data_augmentation.RandomFlip))
    if cfg.data_augmentation.RandomTranslation:
        height_factor, width_factor = cfg.data_augmentation.RandomTranslation
        augmentation_layers.append(
            layers.RandomTranslation(height_factor, width_factor, interpolation='nearest', fill_mode='nearest'))
    if cfg.data_augmentation.RandomRotation:
        augmentation_layers.append(
            layers.RandomRotation(factor=cfg.data_augmentation.RandomRotation, interpolation='nearest',
                                  fill_mode='nearest'))

    data_augmentation = keras.Sequential(augmentation_layers)
    data_augmentation._name = "Data_augmentation"

    return data_augmentation, augment


def preprocessing(cfg):
    """ Define Sequential preprocessing layers model. """

    preprocessing_layers = []
    if cfg.pre_processing.rescaling:
        preprocessing_layers.append(
            layers.Rescaling(1. / cfg.pre_processing.rescaling.scale, offset=cfg.pre_processing.rescaling.offset))

    preprocessing_layers = keras.Sequential(preprocessing_layers)
    preprocessing_layers._name = "Preprocessing"
    return preprocessing_layers
