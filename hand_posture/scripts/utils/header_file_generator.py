# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import ssl

from hydra.core.hydra_config import HydraConfig

ssl._create_default_https_context = ssl._create_unverified_context
import os

import numpy as np
import tensorflow as tf
from handposture_dictionnary import hand_posture_dict


def gen_h_user_file(config, quantized_model_path):
    class Flags:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    params = Flags(**config)
    '''y values change to [0,1,2,...] -> change the class names order to be aligned with the model'''
    newdict = {key: hand_posture_dict[key] for key in params.dataset.class_names}
    newdict = dict(sorted(newdict.items(), key=lambda item: item[1]))
    params.dataset.class_names = list(newdict)

    class_names = params.dataset.class_names
    input_shape = params.model.input_shape
    # class_names_dbg = ["None", "FlatHand", "Like", "Love", "Dislike", "BreakTime", "CrossHands", "Fist"]
    # class_names = class_names_dbg
    classes = '{\\\n'
    evk_labels = '{\\\n'
    # for i, x in enumerate(params.dataset.class_names):
    for i, x in enumerate(class_names):
        if i == (len(class_names) - 1):
            classes = classes + '   "' + str(x) + '"' + '};\\\n'
            evk_labels = evk_labels + '   ' + str(hand_posture_dict[x]) + '};\\\n'
        else:
            classes = classes + '   "' + str(x) + '"' + ' ,' + ('\\\n' if (i % 5 == 0 and i != 0) else '')
            evk_labels = evk_labels + '   ' + str(hand_posture_dict[x]) + ' ,' + ('\\\n' if (i % 5 == 0 and i != 0) else '')

    # Quantization params
    # interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    # input_details = interpreter_quant.get_input_details()[0]
    # output_details = interpreter_quant.get_output_details()[0]

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
        f.write("#define BACKGROUND_REMOVAL ({})\n".format(params.pre_processing.Background_distance))
        f.write("#define MAX_DISTANCE ({})\n".format(params.pre_processing.Max_distance))
        f.write("#define MIN_DISTANCE ({})\n".format(params.pre_processing.Min_distance))
        f.write("\n")

        # f.write("/* Resizing configuration */\n")
        # f.write("#define NO_RESIZE       ({})\n".format(int(0 if params.pre_processing.resizing else 1)))
        # f.write("#define INTERPOLATION_NEAREST       (1)\n")
        # f.write("\n")
        # f.write("#define PP_RESIZING_ALGO       {}\n".format('INTERPOLATION_NEAREST'))
        # f.write("\n")
        # f.write("/* Input rescaling configuration */\n")
        # f.write("#define PP_OFFSET       ({}f)\n".format(float(params.pre_processing.rescaling.offset)))
        # f.write("#define PP_SCALE       ({}f)\n".format(float(params.pre_processing.rescaling.scale)))
        # f.write("\n")
        # if params.pre_processing.aspect_ratio:
        #     f.write("/* Cropping configuration */\n")
        #     f.write("#define PP_KEEP_ASPECT_RATIO     \n")
        #     f.write("\n")
        # f.write("/* Input color format configuration */\n")
        # yaml_opt = ["rgb", "bgr", "grayscale"]
        # opt = ["RGB_FORMAT", "BGR_FORMAT", "GRAYSCALE_FORMAT"]
        # f.write("#define RGB_FORMAT    (1)\n")
        # f.write("#define BGR_FORMAT    (2)\n")
        # f.write("#define GRAYSCALE_FORMAT    (3)\n")
        # f.write("#define PP_COLOR_MODE    {}\n".format(opt[yaml_opt.index(params.pre_processing.color_mode)]))
        # f.write("\n")
        # f.write("/* Input/Output quantization configuration */\n")
        # opt = ["UINT8_FORMAT", "INT8_FORMAT", "FLOAT32_FORMAT"]
        # f.write("#define UINT8_FORMAT    (1)\n")
        # f.write("#define INT8_FORMAT    (2)\n")
        # f.write("#define FLOAT32_FORMAT    (3)\n")
        # f.write("\n")
        # f.write("#define QUANT_INPUT_TYPE    {}\n".format(
        #     opt[[np.uint8, np.int8, np.float32].index(input_details['dtype'])]))
        # f.write("#define QUANT_OUTPUT_TYPE    {}\n".format(
        #     opt[[np.uint8, np.int8, np.float32].index(output_details['dtype'])]))
        # f.write("\n")
        f.write("#endif      /* __AI_MODEL_CONFIG_H__  */\n")
