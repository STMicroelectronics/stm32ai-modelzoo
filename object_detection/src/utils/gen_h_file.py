# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import os
import glob
import re


from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from postprocessing.tflite_ssd_postprocessing_removal.ssd_model_cut_function import ssd_post_processing_removal
import numpy as np
import tensorflow as tf
 
from cfg_utils import aspect_ratio_dict


def gen_h_user_file(config: DictConfig = None, quantized_model_path: str = None) -> None:
    """
    Generates a C header file containing user configuration for the AI model.
 
    Args:
        config: A configuration object containing user configuration for the AI model.
        quantized_model_path: The path to the quantized model file.
 
    """
 
    class Flags:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    params = Flags(**config)
    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    input_details = interpreter_quant.get_input_details()[0]
    output_details = interpreter_quant.get_output_details()[0]
    input_shape = input_details['shape']

    class_names = params.dataset.class_names

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    TFLite_Detection_PostProcess_id = False
    XY, WH = None, None

    if params.general.model_type == "st_ssd_mobilenet_v1":
        classes = '{\\\n"background",'

    elif params.general.model_type =="ssd_mobilenet_v2_fpnlite":

        name_of_post_process_layer='TFLite_Detection_PostProcess'

        for op in interpreter_quant._get_ops_details():
            if op['op_name'] == name_of_post_process_layer:
                TFLite_Detection_PostProcess_id = op['index']


        if TFLite_Detection_PostProcess_id:
            print('[INFO] : This TFLITE model contains a post-processing layer')
            anchors_path = os.path.join(path,'anchors.h')
            path_cut_model, XY, WH = ssd_post_processing_removal(quantized_model_path, TFLite_Detection_PostProcess_id, anchors_path)
            quantized_model_path = path_cut_model
        else:
            print('[INFO] : This TFLITE model doesnt contain a post-processing layer')

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


    with open(os.path.join(path, "ai_model_config.h"), "wt") as f:
        f.write("/**\n")
        f.write("  ******************************************************************************\n")
        f.write("  * @file    ai_model_config.h\n")
        f.write("  * @author  Artificial Intelligence Solutions group (AIS)\n")
        f.write("  * @brief   User header file for Preprocessing configuration\n")
        f.write("  ******************************************************************************\n")
        f.write("  * @attention\n")
        f.write("  *\n")
        f.write("  * Copyright (c) 2024 STMicroelectronics.\n")
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
        if params.general.model_type == "st_ssd_mobilenet_v1" or params.general.model_type == "ssd_mobilenet_v2_fpnlite":
            f.write("#define NB_CLASSES        ({})\n".format(len(class_names)+1))
        else:
            f.write("#define NB_CLASSES        ({})\n".format(len(class_names)))
        f.write("#define INPUT_HEIGHT      ({})\n".format(int(input_shape[1])))
        f.write("#define INPUT_WIDTH       ({})\n".format(int(input_shape[2])))
        f.write("#define INPUT_CHANNELS    ({})\n".format(int(input_shape[3])))
        f.write("\n")
        f.write("/* Classes */\n")
        f.write("#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {}\n".format(classes))
        f.write("\n\n")
        f.write("/***** Preprocessing configuration *****/\n\n")
        f.write("/* Cropping configuration */\n")
        yaml_opt = [False, "crop", "padding"]
        opt = ["ASPECT_RATIO_FIT", "ASPECT_RATIO_CROP", "ASPECT_RATIO_PADDING"]
        f.write("#define ASPECT_RATIO_FIT      (1)\n")
        f.write("#define ASPECT_RATIO_CROP     (2)\n")
        f.write("#define ASPECT_RATIO_PADDING  (3)\n")
        f.write("\n")
        f.write("#define ASPECT_RATIO_MODE    {}\n".format(aspect_ratio_dict[params.preprocessing.resizing.aspect_ratio]))
        f.write("\n")

        f.write("/***** Postprocessing configuration *****/\n\n")
        f.write("/* Postprocessing type configuration */\n")
        f.write("#define POSTPROCESS_CENTER_NET (1)\n")
        f.write("#define POSTPROCESS_YOLO_V2    (2)\n")
        f.write("#define POSTPROCESS_ST_SSD     (3)\n")
        f.write("#define POSTPROCESS_SSD        (4)\n\n")

        if (params.general.model_type == "st_ssd_mobilenet_v1" or params.general.model_type == "ssd_mobilenet_v2_fpnlite") and not TFLite_Detection_PostProcess_id:
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_ST_SSD\n\n")
        elif TFLite_Detection_PostProcess_id:
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_SSD\n\n")
        elif params.general.model_type == "CENTER_NET":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_CENTER_NET\n\n")
        elif params.general.model_type == "tiny_yolo_v2" or "st_yolo_lc_v1":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_YOLO_V2\n\n")
        else:
            raise TypeError("please select one of this supported post processing options [CENTER_NET, st_yolo_lc_v1, tiny_yolo_v2, st_ssd_mobilenet_v1, ssd_mobilenet_v2_fpnlite ]")

        if (params.general.model_type == "st_ssd_mobilenet_v1" or params.general.model_type == "ssd_mobilenet_v2_fpnlite") and not TFLite_Detection_PostProcess_id:
            f.write("/* Postprocessing ST_SSD configuration */\n")
            f.write("#define AI_OBJDETECT_SSD_ST_PP_NB_CLASSES         ({})\n".format(len(class_names)+1))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OBJDETECT_SSD_ST_PP_TOTAL_DETECTIONS   ({})\n".format(int(output_details['shape'][1])))
        elif  TFLite_Detection_PostProcess_id:
            f.write("\n/* Postprocessing SSD configuration */\n")
            f.write("#define AI_OBJDETECT_SSD_PP_XY_SCALE           ({})\n".format(XY))
            f.write("#define AI_OBJDETECT_SSD_PP_WH_SCALE           ({})\n".format(WH))
            f.write("#define AI_OBJDETECT_SSD_PP_NB_CLASSES         ({})\n".format(len(class_names)+1))
            f.write("#define AI_OBJDETECT_SSD_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OBJDETECT_SSD_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OBJDETECT_SSD_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OBJDETECT_SSD_PP_TOTAL_DETECTIONS   ({})\n".format(int(output_details['shape'][1])))
        else:
            f.write("\n/* Postprocessing TINY_YOLO_V2 configuration */\n")

            f.write("#define AI_OBJDETECT_YOLOV2_PP_NB_CLASSES      ({})\n".format(len(class_names)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH      ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_NB_INPUT_BOXES  (AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH * AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT)\n")
            f.write("#define AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS      ({})\n".format(int(len(params.postprocessing.yolo_anchors)/2)))
            anchors_string = "{" + ", ".join([f"{((x/int(input_shape[1]))*int(input_shape[1]//params.postprocessing.network_stride)):.6f}" for x in params.postprocessing.yolo_anchors]) + "}"
            f.write("static const float32_t AI_OBJDETECT_YOLOV2_PP_ANCHORS[2*AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS] ={};\n".format(anchors_string))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))

        f.write("\n")

        f.write("/* Input color format configuration */\n")
        yaml_opt = ["rgb", "bgr", "grayscale"]
        opt = ["RGB_FORMAT", "BGR_FORMAT", "GRAYSCALE_FORMAT"]
        f.write("#define RGB_FORMAT          (1)\n")
        f.write("#define BGR_FORMAT          (2)\n")
        f.write("#define GRAYSCALE_FORMAT    (3)\n")
        f.write("\n")
        f.write("#define PP_COLOR_MODE    {}\n".format(opt[yaml_opt.index(params.preprocessing.color_mode)]))
        f.write("\n")
        f.write("/* Input/Output quantization configuration */\n")
        opt = ["UINT8_FORMAT", "INT8_FORMAT", "FLOAT32_FORMAT"]
        f.write("#define UINT8_FORMAT      (1)\n")
        f.write("#define INT8_FORMAT       (2)\n")
        f.write("#define FLOAT32_FORMAT    (3)\n")
        f.write("\n")
        f.write("#define QUANT_INPUT_TYPE     {}\n".format(
            opt[[np.uint8, np.int8, np.float32].index(input_details['dtype'])]))
        f.write("#define QUANT_OUTPUT_TYPE    {}\n".format(
            opt[[np.uint8, np.int8, np.float32].index(output_details['dtype'])]))
        f.write("\n")
        f.write("#endif      /* __AI_MODEL_CONFIG_H__ */\n")
    
    return TFLite_Detection_PostProcess_id, quantized_model_path