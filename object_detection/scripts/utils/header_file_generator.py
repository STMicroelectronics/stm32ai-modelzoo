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


def gen_h_user_file(config, quantized_model_path):
    class Flags:
        def __init__(self, **entries):
            self.__dict__.update(entries)
    params = Flags(**config)
    class_names = params.dataset.class_names
    input_shape = params.model.input_shape

    classes = ''
    for i, x in enumerate(params.dataset.class_names):
        if i == (len(class_names) - 1):
            classes = classes + '"' + str(x) + '"'
        else:
            classes = classes + '"' + str(x) + '"' + ','

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
        f.write("  * Copyright (c) 2018 STMicroelectronics.\n")
        f.write("  * All rights reserved.\n")
        f.write("  *\n")
        f.write("  * This software component is licensed by ST under Ultimate Liberty license\n")
        f.write("  * SLA0044, the \"License\"; You may not use this file except in compliance with\n")
        f.write("  * the License. You may obtain a copy of the License at:\n")
        f.write("  *                             www.st.com/SLA0044\n")
        f.write("  *\n")
        f.write("  ******************************************************************************\n")
        f.write("  */\n\n")
        f.write("/* ---------------    Generated code    ----------------- */\n")
        f.write("#ifndef __AI_MODEL_CONFIG_H__\n")
        f.write("#define __AI_MODEL_CONFIG_H__\n\n\n")
        f.write("#ifdef __cplusplus\n")
        f.write("  extern \"C\" {\n")
        f.write("#endif\n\n")
        f.write("/* I/O configuration */\n")
        f.write("#define NB_CLASSES        ({})\n".format(len(class_names)))
        f.write("#define INPUT_HEIGHT        ({})\n".format(int(input_shape[0])))
        f.write("#define INPUT_WIDTH       ({})\n".format(int(input_shape[1])))
        f.write("#define INPUT_CHANNELS        ({})\n".format(int(input_shape[2])))
        f.write("\n")
        f.write("const char classes[NB_CLASSES] = {{{}}};\n".format(classes))
        f.write("\n")
        f.write("/* Preprocessing configuration */\n")
        f.write("#define PP_RESIZING_FLAG       ({})\n".format(int(1 if params.pre_processing.resizing else 0)))
        f.write("#define PP_RESIZING_INTERPOLATION_BILINEAR       ({})\n".format(int(params.pre_processing.resizing == 'bilinear')))
        f.write("#define PP_RESIZING_INTERPOLATION_NEAREST       ({})\n".format(int(params.pre_processing.resizing == 'nearest')))
        f.write("#define PP_RESIZING_INTERPOLATION_BICUBIC       ({})\n".format(int(params.pre_processing.resizing == 'bicubic')))
        f.write("#define PP_RESIZING_INTERPOLATION_AREA       ({})\n".format(int(params.pre_processing.resizing == 'area')))
        f.write("#define PP_RESIZING_INTERPOLATION_GAUSSIAN       ({})\n".format(int(params.pre_processing.resizing == 'gaussian')))
        f.write("\n")
        f.write("/* Post processing configuration */\n")
        f.write("#define PP_NMS_THRESH       ({})\n".format(float(params.post_processing.NMS_thresh)))
        f.write("#define PP_SCORE_THRESH       ({})\n".format(float(params.post_processing.confidence_thresh)))
        f.write("\n")
        f.write("#define PP_KEEP_ASPECT_RATIO       ({})\n".format(int(1 if params.pre_processing.aspect_ratio else 0)))
        f.write("\n")
        f.write("#define PP_COLOR_MODE_RGB    ({})\n".format(int(params.pre_processing.color_mode == 'rgb')))
        f.write("#define PP_COLOR_MODE_BGR    ({})\n".format(int(params.pre_processing.color_mode == 'bgr')))
        f.write("\n")
        f.write("/* Quantization configuration */\n")
        f.write("#define QUANT_INPUT_UINT8    ({})\n".format(int(np.uint8 == input_details['dtype'])))
        f.write("#define QUANT_INPUT_INT8    ({})\n".format(int(np.int8 == input_details['dtype'])))
        f.write("#define QUANT_INPUT_FLOAT32    ({})\n".format(int(np.float32 == input_details['dtype'])))
        f.write("#define QUANT_INPUT_ZERO_POINT    ({})\n".format(float(input_details['quantization'][1])))
        f.write("#define QUANT_INPUT_SCALE    ({})\n".format(float(input_details['quantization'][0])))
        f.write("\n")
        f.write("#define QUANT_OUTPUT_UINT8    ({})\n".format(int(np.uint8 == output_details['dtype'])))
        f.write("#define QUANT_OUTPUT_INT8    ({})\n".format(int(np.int8 == output_details['dtype'])))
        f.write("#define QUANT_OUTPUT_FLOAT32    ({})\n".format(int(np.float32 == output_details['dtype'])))
        f.write("#define QUANT_OUTPUT_ZERO_POINT    ({})\n".format(float(output_details['quantization'][1])))
        f.write("#define QUANT_OUTPUT_SCALE    ({})\n".format(float(output_details['quantization'][0])))
        f.write("\n")
        f.write("#endif      /* __AI_MODEL_CONFIG_H__  */\n")
        f.write("}\n")
