# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from models.miniresnet import miniresnet
from models.miniresnetv2 import miniresnetv2
from models.yamnet import yamnet
from models import custom_model

def check_yamnet_config(cfg):
    '''Make sure params in user config correspond to the expected params for Yamnet'''
    params_are_fine = (cfg.pre_processing.target_rate == 16000 and
                       cfg.feature_extraction.n_fft == 400 and
                       cfg.feature_extraction.window_length == 400 and
                       cfg.feature_extraction.n_mels == 64 and
                       cfg.feature_extraction.hop_length == 160 and
                       cfg.feature_extraction.fmax == 7500 and
                       cfg.feature_extraction.fmin == 125 and
                       cfg.feature_extraction.patch_length == 96 and
                       cfg.feature_extraction.overlap == 0.25)
    if not params_are_fine:
        raise ValueError(" Invalid pre-processing and/or feature extraction parameters for Yamnet. \n \
            Valid parameters are : pre_processing.target_rate = 16000 \n \
                       feature_extraction.n_fft = 400 \n \
                       feature_extraction.window_length = 400 \n \
                       feature_extraction.n_mels = 64 \n \
                       feature_extraction.hop_length = 160 \n \
                       feature_extraction.fmax = 7500 \n \
                       feature_extraction.fmin = 125 \n \
                       feature_extraction.patch_length = 96 \n \
                       feature_extraction.overlap = \n \
        ")
    else:
        print("[INFO] Pre-processing and feature extraction parameters valid for Yamnet, continuing...")

def get_model(cfg):
    if cfg.model.multi_label:
        raise NotImplementedError("Multi-label classification is not implemented yet, but will be in a future update. \n Please set model.multi_label to False.")
    if cfg.model.model_type.name.lower() == "miniresnet":
        if cfg.model.transfer_learning == True:
            return miniresnet.get_pretrained_model(cfg)
        else:
            return miniresnet.get_scratch_model(cfg)

    elif cfg.model.model_type.name.lower() == "miniresnetv2":
        if cfg.model.transfer_learning == True:
            return miniresnetv2.get_pretrained_model(cfg)
        else:
            return miniresnetv2.get_scratch_model(cfg)

    elif cfg.model.model_type.name.lower() == "yamnet":
        # Check disabled for now
        #check_yamnet_config(cfg)
        return yamnet.get_pretrained_model(cfg)

    elif cfg.model.model_type.name == "custom":
        return custom_model.get_model(cfg)

    else:
        raise TypeError("Model not defined, please select one of the listed options")