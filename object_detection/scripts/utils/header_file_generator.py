# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics.
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
import glob
import re


_LDFILE_PATTERN = r'STM32H747XIHx_CM7[_A-Za-z]*\.ld'

def gen_h_user_file(config, quantized_model_path):
    class Flags:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    params = Flags(**config)
    if params.post_processing.type == "SSD" and params.model.input_shape == [224, 224, 3]:
        _update_ldfile_cproject(params.stm32ai.c_project_path, "STM32H747XIHx_CM7_sdram.ld")
    else:
        _update_ldfile_cproject(params.stm32ai.c_project_path, "STM32H747XIHx_CM7.ld")

    class_names = params.dataset.class_names
    input_shape = params.model.input_shape

    if params.post_processing.type == "SSD":
        classes = '{\\\n"background",'
    else:
        classes = '{\\\n'

    for i, x in enumerate(params.dataset.class_names):
        if i == (len(class_names) - 1):
            classes = classes + '   "' + str(x) + '"' + '}\\'
        else:
            classes = classes + '   "' + str(x) + '"' + ' ,' + ('\\\n' if (i % 5 == 0 and i != 0) else '')

    # Quantization params
    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    input_details = interpreter_quant.get_input_details()[0]
    output_details = interpreter_quant.get_output_details()[0]

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    with open(os.path.join(path, "ai_model_config.h"), "wt") as f:
        f.write("/**\n")
        f.write("  ******************************************************************************\n")
        f.write("  * @file    ai_model_config.h\n")
        f.write("  * @author  Artificial Intelligence Solutions group (AIS)\n")
        f.write("  * @brief   User header file for Preprocessing configuration\n")
        f.write("  ******************************************************************************\n")
        f.write("  * @attention\n")
        f.write("  *\n")
        f.write("  * Copyright (c) 2023 STMicroelectronics.\n")
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
        if params.post_processing.type == "SSD":
            f.write("#define NB_CLASSES        ({})\n".format(len(class_names)+1))
        else:
            f.write("#define NB_CLASSES        ({})\n".format(len(class_names)))
        f.write("#define INPUT_HEIGHT      ({})\n".format(int(input_shape[0])))
        f.write("#define INPUT_WIDTH       ({})\n".format(int(input_shape[1])))
        f.write("#define INPUT_CHANNELS    ({})\n".format(int(input_shape[2])))
        f.write("\n")
        f.write("/* Classes */\n")
        f.write("#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {}\n".format(classes))
        f.write("\n\n")
        f.write("/***** Preprocessing configuration *****/\n\n")
        f.write("/* Resizing configuration */\n")
        f.write("#define NO_RESIZE              ({})\n".format(int(0 if params.pre_processing.resizing else 1)))
        f.write("#define INTERPOLATION_NEAREST  (1)\n")
        f.write("#define INTERPOLATION_BILINEAR (2)\n")
        f.write("\n")
        f.write("#define PP_RESIZING_ALGO  {}\n".format('INTERPOLATION_NEAREST'))
        f.write("\n")
        f.write("/* Input rescaling configuration */\n")
        f.write("#define PP_OFFSET       ({}f)\n".format(float(params.pre_processing.rescaling.offset)))
        f.write("#define PP_SCALE       ({}f)\n".format(float(params.pre_processing.rescaling.scale)))
        f.write("\n")
        f.write("/* Cropping configuration */\n")
        yaml_opt = [False, "crop", "padding"]
        opt = ["KEEP_ASPECT_RATIO_DISABLE", "KEEP_ASPECT_RATIO_CROP", "KEEP_ASPECT_RATIO_PADDING"]
        f.write("#define KEEP_ASPECT_RATIO_DISABLE 0\n")
        f.write("#define KEEP_ASPECT_RATIO_CROP    1\n")
        f.write("#define KEEP_ASPECT_RATIO_PADDING 2\n")
        f.write("\n")
        f.write("#define ASPECT_RATIO_MODE    {}\n".format(opt[yaml_opt.index(params.pre_processing.aspect_ratio)]))
        f.write("\n\n")

        f.write("/***** Postprocessing configuration *****/\n")
        f.write("/* Postprocessing type configuration */\n")
        f.write("\n")
        f.write("#define POSTPROCESS_CENTER_NET (0)\n")
        f.write("#define POSTPROCESS_YOLO       (1)\n")
        f.write("#define POSTPROCESS_SSD        (2)\n")

        if params.post_processing.type == "SSD":
            f.write("#define POSTPROCESS_TYPE POSTPROCESS_SSD\n")
        elif params.post_processing.type == "CENTER_NET":
            f.write("#define POSTPROCESS_TYPE POSTPROCESS_CENTER_NET\n")
        elif params.post_processing.type == "YOLO":
            f.write("#define POSTPROCESS_TYPE POSTPROCESS_YOLO\n")
        else:
            raise TypeError("please select one of this supported post processing options [CENTER_NET, YOLO, SSD]")

        if params.post_processing.type == "SSD":
            f.write("\n/* Postprocessing SSD configuration */\n")
            f.write("#define AI_OBJDETECT_SSD_ST_PP_NB_CLASSES         ({})\n".format(len(class_names)+1))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_IOU_THRESHOLD      ({})\n".format(float(params.post_processing.NMS_thresh)))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_CONF_THRESHOLD     ({})\n".format(float(params.post_processing.confidence_thresh)))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.post_processing.max_boxes_limit)))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_TOTAL_DETECTIONS   ({})\n".format(int(output_details['shape'][1])))
        else:
            raise TypeError(" Only the SSD option is supported for now ...")

        f.write("\n")

        f.write("/* Input color format configuration */\n")
        yaml_opt = ["rgb", "bgr", "grayscale"]
        opt = ["RGB_FORMAT", "BGR_FORMAT", "GRAYSCALE_FORMAT"]
        f.write("#define RGB_FORMAT          (1)\n")
        f.write("#define BGR_FORMAT          (2)\n")
        f.write("#define GRAYSCALE_FORMAT    (3)\n")
        f.write("\n")
        f.write("#define PP_COLOR_MODE    {}\n".format(opt[yaml_opt.index(params.pre_processing.color_mode)]))
        f.write("\n")
        f.write("/* Input/Output quantization configuration */\n")
        opt = ["UINT8_FORMAT", "INT8_FORMAT", "FLOAT32_FORMAT"]
        f.write("#define UINT8_FORMAT      (1)\n")
        f.write("#define INT8_FORMAT       (2)\n")
        f.write("#define FLOAT32_FORMAT    (3)\n")
        f.write("\n")
        f.write("#define QUANT_INPUT_TYPE    {}\n".format(
            opt[[np.uint8, np.int8, np.float32].index(input_details['dtype'])]))
        f.write("#define QUANT_OUTPUT_TYPE    {}\n".format(
            opt[[np.uint8, np.int8, np.float32].index(output_details['dtype'])]))
        f.write("\n")
        f.write("#endif      /* __AI_MODEL_CONFIG_H__  */\n")
        
        
def _update_ldfile_cproject(project_dir: str, stm_ai_lib: str):
    """Update the cube.ide cproject file"""
    c_project = glob.glob(project_dir + "/**/CM7/.cproject", recursive=True)[0]
    if os.path.isfile(c_project):
        with open(c_project, 'r+', encoding='utf-8') as c_prj_file:
            file_data = c_prj_file.read()
            if re.search(_LDFILE_PATTERN, file_data):
                n_file_data = re.sub(_LDFILE_PATTERN, stm_ai_lib, file_data)
                c_prj_file.truncate(0)
                c_prj_file.seek(0)
                c_prj_file.write(n_file_data)
