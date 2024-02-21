# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import GaussianNoise
from data_augmentation_layers_audio import SpecAugment, VolumeAugment 

def get_data_augmentation(cfg, db_scale: bool = False):
    '''
    Parses the data augmentation section of the config file, and returns 
    a list containing the appropriate data augmentation layers.
    
    Inputs
    ------
    cfg : Configuration dictionary
    db_scale : bool, set to True if spectrogram patches are in dBfs scale

    Outputs
    -------
    augmentation_layers : List[tf.keras.Layer] : list of data augmentation layers
    '''
    
    augmentation_layers = []
    # Nested ifs to handle case where user omits certain portions of the data augmentation
    # section of the yaml file
    # This isn't ideal
    if cfg.GaussianNoise:
        if cfg.GaussianNoise.enable:
            augmentation_layers.append(GaussianNoise(stddev=cfg.GaussianNoise.scale))
    if cfg.VolumeAugment:
        if cfg.VolumeAugment.enable:
            augmentation_layers.append(VolumeAugment(cfg.VolumeAugment.min_scale,
                                                    cfg.VolumeAugment.max_scale,
                                                    db_scale=db_scale))
    if cfg.SpecAug:
        if cfg.SpecAug.enable:
            augmentation_layers.append(SpecAugment(freq_mask_param=cfg.SpecAug.freq_mask_param,
                                                time_mask_param=cfg.SpecAug.time_mask_param,
                                                n_freq_mask=cfg.SpecAug.n_freq_mask,
                                                n_time_mask=cfg.SpecAug.n_time_mask,
                                                mask_value=cfg.SpecAug.mask_value))
        
    return augmentation_layers