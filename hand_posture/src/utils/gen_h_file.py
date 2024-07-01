#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import sys
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend
from typing import Tuple, Dict, Optional
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf, DictConfig, open_dict

from models_utils import get_model_name_and_its_input_shape
from handposture_dictionnary import hand_posture_dict


def gen_h_user_file(config: DictConfig = None, model_path: str = None) -> None:
    """
    Generates a C header file containing user configuration for the AI model.

    Args:
        config: A configuration object containing user configuration for the AI model.
    """


    class Flags:
        def __init__(self, **entries):
            self.__dict__.update(entries)


    params = Flags(**config)
    '''y values change to [0,1,2,...] -> change the class names order to be aligned with the model'''
    newdict = {key: hand_posture_dict[key] for key in params.dataset.class_names}
    newdict = dict(sorted(newdict.items(), key=lambda item: item[1]))
    params.dataset.class_names = list(newdict)
    class_names = list(newdict)

    _, input_shape = get_model_name_and_its_input_shape(model_path)
    classes = '{\\\n'
    evk_labels = '{\\\n'
    for i, x in enumerate(class_names):
        if i == (len(class_names) - 1):
            classes = classes + '   "' + str(x) + '"' + '};\\\n'
            evk_labels = evk_labels + '   ' + str(hand_posture_dict[x]) + '};\\\n'
        else:
            classes = classes + '   "' + str(x) + '"' + ' ,' + ('\\\n' if (i % 5 == 0 and i != 0) else '')
            evk_labels = evk_labels + '   ' + str(hand_posture_dict[x]) + ' ,' + ('\\\n' if (i % 5 == 0 and i != 0) else '')

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    with open(os.path.join(path, "ai_model_config.h"), "wt") as f:
        f.write("/**\n")
        f.write("  ******************************************************************************\n")
        f.write("  * @file    ai_model_config.h\n")
        f.write("  * @author  ST Imaging Division and Artificial Intelligence Solutions group (AIS)\n")
        f.write("  * @brief   User header file for Preprocessing configuration\n")
        f.write("  ******************************************************************************\n")
        f.write("  * @attention\n")
        f.write("  *\n")
        f.write("  * Copyright (c) 2022 STMicroelectronics.\n")
        f.write("  * All rights reserved.\n")
        f.write("  *\n")
        f.write("  * This software is licensed under terms that can be found in the LICENSE file in\n")
        f.write("  * the root directory of this software component.\n")
        f.write("  * If no LICENSE file comes with this software, it is provided AS-IS.\n")
        f.write("  *\n")
        f.write("  ******************************************************************************\n")
        f.write("  */\n\n")
        f.write("/* ---------------    Generated code    ----------------- */\n")
        f.write("#ifndef __AI_MODEL_CONFIG_H__\n")
        f.write("#define __AI_MODEL_CONFIG_H__\n\n\n")
        f.write("/* I/O configuration */\n")
        f.write("#define NB_CLASSES        ({})\n".format(len(class_names)))
        f.write("#define INPUT_HEIGHT        ({})\n".format(int(input_shape[0])))
        f.write("#define INPUT_WIDTH       ({})\n".format(int(input_shape[1])))
        f.write("#define INPUT_CHANNELS        ({})\n".format(int(input_shape[2])))
        f.write("\n")
        f.write("/* Classes */\n")
        f.write("#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {}\n".format(classes))
        f.write("#define EVK_LABEL_TABLE const int evk_label_table[NB_CLASSES] = {}\n".format(evk_labels))
        f.write("\n")
        f.write("/* Pre_processing */\n")
        f.write("#define BACKGROUND_REMOVAL ({})\n".format(params.preprocessing.Background_distance))
        f.write("#define MAX_DISTANCE ({})\n".format(params.preprocessing.Max_distance))
        f.write("#define MIN_DISTANCE ({})\n".format(params.preprocessing.Min_distance))
        f.write("\n")
        f.write("#endif      /* __AI_MODEL_CONFIG_H__  */\n")
