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
import shutil
import numpy as np
import tensorflow as tf

from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from common.utils import aspect_ratio_dict, color_mode_n6_dict
from object_detection.tf.src.postprocessing.tflite_ssd_postprocessing_removal.ssd_model_cut_function import ssd_post_processing_removal




def gen_h_user_file_h7(config: DictConfig = None, quantized_model_path: str = None) -> None:
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
    if quantized_model_path.lower().endswith('.tflite'):
        interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
        input_details = interpreter_quant.get_input_details()[0]
        output_details = interpreter_quant.get_output_details()[0]
        input_shape = input_details['shape']
    elif quantized_model_path.lower().endswith('.onnx'):
        import onnxruntime


        params = config

        model = onnxruntime.InferenceSession(quantized_model_path)
        inputs  = model.get_inputs()
        outputs = model.get_outputs()
        input_shape_raw = inputs[0].shape
        input_shape = [1,input_shape_raw[2],input_shape_raw[3],input_shape_raw[1]]
    else:
        raise TypeError("Please provide a TFLITE or ONNX model for N6 deployment")

    class_names = params.dataset.class_names

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    TFLite_Detection_PostProcess_id = False
    XY, WH = None, None

    if params.model.model_type == "st_ssd_mobilenet_v1":
        classes = '{\\\n"background",'

    elif params.model.model_type =="ssd_mobilenet_v2_fpnlite":

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
        if params.model.model_type == "st_ssd_mobilenet_v1" or params.model.model_type == "ssd_mobilenet_v2_fpnlite":
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
        f.write("#define POSTPROCESS_SSD        (4)\n")
        f.write("#define POSTPROCESS_ST_YOLO_X  (5)\n\n")

        if (params.model.model_type == "st_ssd_mobilenet_v1" or params.model.model_type == "ssd_mobilenet_v2_fpnlite") and not TFLite_Detection_PostProcess_id:
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_ST_SSD\n\n")
        elif TFLite_Detection_PostProcess_id:
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_SSD\n\n")
        elif params.model.model_type == "CENTER_NET":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_CENTER_NET\n\n")
        elif (params.model.model_type == "yolov2t" or params.model.model_type =="st_yololcv1"):
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_YOLO_V2\n\n")
        elif params.model.model_type == "st_yoloxn":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_ST_YOLO_X\n\n")
        else:
            raise TypeError("please select one of this supported post processing options [CENTER_NET,st_yoloxn, st_yololcv1, yolov2t, st_ssd_mobilenet_v1, ssd_mobilenet_v2_fpnlite ]")

        if (params.model.model_type == "st_ssd_mobilenet_v1" or params.model.model_type == "ssd_mobilenet_v2_fpnlite") and not TFLite_Detection_PostProcess_id:
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
        elif (params.model.model_type == "yolov2t" or params.model.model_type == "st_yololcv1"):
            f.write("\n/* Postprocessing TINY_YOLO_V2 configuration */\n")
            yolo_anchors = np.concatenate(params.postprocessing.yolo_anchors).flatten()
            f.write("#define AI_OBJDETECT_YOLOV2_PP_NB_CLASSES      ({})\n".format(len(class_names)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH      ({})\n".format(int(input_shape[2]//params.postprocessing.network_stride)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_NB_INPUT_BOXES  (AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH * AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT)\n")
            f.write("#define AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS      ({})\n".format(int(len(yolo_anchors)/2)))
            anchors_string = "{" + ", ".join([f"{(x):.6f}" for x in yolo_anchors]) + "}"
            f.write("static const float32_t AI_OBJDETECT_YOLOV2_PP_ANCHORS[2*AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS] ={};\n".format(anchors_string))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OBJDETECT_YOLOV2_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))
        elif (params.model.model_type == "st_yoloxn"):
            f.write("\n/* Postprocessing ST_YOLO_X configuration */\n")
            yolo_anchors = np.concatenate(params.postprocessing.yolo_anchors).flatten()
            f.write("#define AI_OBJDETECT_YOLOVX_PP_NB_CLASSES        ({})\n".format(len(class_names)))

            f.write("#define AI_OBJDETECT_YOLOVX_PP_L_GRID_WIDTH      ({})\n".format(int(input_shape[2]//params.postprocessing.network_stride[0])))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_L_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride[0])))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_L_NB_INPUT_BOXES  (AI_OBJDETECT_YOLOVX_PP_L_GRID_WIDTH * AI_OBJDETECT_YOLOVX_PP_L_GRID_HEIGHT)\n")

            f.write("#define AI_OBJDETECT_YOLOVX_PP_M_GRID_WIDTH      ({})\n".format(int(input_shape[2]//params.postprocessing.network_stride[1])))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_M_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride[1])))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_M_NB_INPUT_BOXES  (AI_OBJDETECT_YOLOVX_PP_M_GRID_WIDTH * AI_OBJDETECT_YOLOVX_PP_M_GRID_HEIGHT)\n")

            f.write("#define AI_OBJDETECT_YOLOVX_PP_S_GRID_WIDTH      ({})\n".format(int(input_shape[2]//params.postprocessing.network_stride[2])))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_S_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride[2])))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_S_NB_INPUT_BOXES  (AI_OBJDETECT_YOLOVX_PP_S_GRID_WIDTH * AI_OBJDETECT_YOLOVX_PP_S_GRID_HEIGHT)\n")            

            f.write("#define AI_OBJDETECT_YOLOVX_PP_NB_ANCHORS        ({})\n".format(int(len(yolo_anchors)/2)))

            anchors_string = "{" + ", ".join([f"{(x*int(input_shape[2]//params.postprocessing.network_stride[0])):.6f}" for row in params.postprocessing.yolo_anchors for x in row]) + "}"
            f.write("static const float32_t AI_OBJDETECT_YOLOVX_PP_L_ANCHORS[2*AI_OBJDETECT_YOLOVX_PP_NB_ANCHORS] ={};\n".format(anchors_string))

            anchors_string = "{" + ", ".join([f"{(x*int(input_shape[2]//params.postprocessing.network_stride[1])):.6f}" for row in params.postprocessing.yolo_anchors for x in row]) + "}"
            f.write("static const float32_t AI_OBJDETECT_YOLOVX_PP_M_ANCHORS[2*AI_OBJDETECT_YOLOVX_PP_NB_ANCHORS] ={};\n".format(anchors_string))

            anchors_string = "{" + ", ".join([f"{(x*int(input_shape[2]//params.postprocessing.network_stride[2])):.6f}" for row in params.postprocessing.yolo_anchors for x in row]) + "}"
            f.write("static const float32_t AI_OBJDETECT_YOLOVX_PP_S_ANCHORS[2*AI_OBJDETECT_YOLOVX_PP_NB_ANCHORS] ={};\n".format(anchors_string))

            f.write("#define AI_OBJDETECT_YOLOVX_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OBJDETECT_YOLOVX_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))

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


def gen_h_user_file_n6(config: DictConfig = None, quantized_model_path: str = None) -> None:
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
    if quantized_model_path.lower().endswith('.tflite'):
        interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
        input_details = interpreter_quant.get_input_details()[0]
        output_details = interpreter_quant.get_output_details()[0]
        input_shape = input_details['shape']
    elif quantized_model_path.lower().endswith('.onnx'):
        import onnxruntime


        params = config

        model = onnxruntime.InferenceSession(quantized_model_path)
        inputs  = model.get_inputs()
        outputs = model.get_outputs()
        input_shape_raw = inputs[0].shape
        input_shape = [1,input_shape_raw[2],input_shape_raw[3],input_shape_raw[1]]
    else:
        raise TypeError("Please provide a TFLITE or ONNX model for N6 deployment")

    class_names = params.dataset.class_names

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    TFLite_Detection_PostProcess_id = False
    XY, WH = None, None

    if params.model.model_type == "st_ssd_mobilenet_v1":
        classes = '{\\\n"background",'

    elif params.model.model_type =="ssd_mobilenet_v2_fpnlite":

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
    
    if params.model.model_type == "face_detect_front":
        outs_info = interpreter_quant.get_output_details()
        #print(outs_info)
        output_shapes =[]
        for buffer in outs_info:
            output_shapes.append(buffer["shape"])
        sorted_shapes = sorted(output_shapes, key=lambda arr: (arr[1], arr[2]), reverse=True)
        SSD_OPTIONS_FRONT = {
        'num_layers': 4,
        'input_size_height': 128,
        'input_size_width': 128,
        'anchor_offset_x': 0.5,
        'anchor_offset_y': 0.5,
        'strides': [8, 16, 16, 16],
        'interpolated_scale_aspect_ratio': 1.0}
        from object_detection.tf.src.postprocessing  import ssd_generate_anchors
        anchors=ssd_generate_anchors(SSD_OPTIONS_FRONT)
        anch_0_rows = int(sorted_shapes[0][1])
        anch_1_rows = int(sorted_shapes[2][1])
        anch_0 = anchors[:anch_0_rows, :]
        anch_1 = anchors[anch_0_rows:, :]
        anch_0_flat = anch_0.reshape(int(anch_0.shape[0] * anch_0.shape[1]))
        anch_1_flat = anch_1.reshape(int(anch_1.shape[0] * anch_1.shape[1]))
        # Format the array elements as strings with 'f' suffix for floats in C
        formatted_anch_0_flat = ", ".join(f"{x:.6f}" for x in anch_0_flat)
        c_anch_0_str = f"const float32_t g_Anchors_0[{int(anch_0.shape[0] * anch_0.shape[1])}] = {{ {formatted_anch_0_flat} }};"
        formatted_anch_1_flat = ", ".join(f"{x:.6f}" for x in anch_1_flat)
        c_anch_1_str = f"const float32_t g_Anchors_1[{int(anch_1.shape[0] * anch_1.shape[1])}] = {{ {formatted_anch_1_flat} }};"
        
        with open(os.path.join(path, "fd_blazeface_anchors_0.h"), "wt") as f:
            f.write("#ifndef __ANCHORS_0_H__\n")
            f.write("#define __ANCHORS_0_H__\n\n")
            f.write(c_anch_0_str)
            f.write("\n")
            f.write("#endif /* __ANCHORS_0_H__ */\n")

        with open(os.path.join(path, "fd_blazeface_anchors_1.h"), "wt") as f:
            f.write("#ifndef __ANCHORS_1_H__\n")
            f.write("#define __ANCHORS_1_H__\n\n")
            f.write(c_anch_1_str)
            f.write("\n")
            f.write("#endif /* __ANCHORS_1_H__ */\n")

        # Copy the anchors to the C project
        anchors_0_path_C = os.path.join(params.deployment.c_project_path, 'Application', params.deployment.hardware_setup.board, 'Inc', 'fd_blazeface_anchors_0.h')
        anchors_1_path_C = os.path.join(params.deployment.c_project_path, 'Application', params.deployment.hardware_setup.board, 'Inc', 'fd_blazeface_anchors_1.h')
        if os.path.exists(anchors_0_path_C):
            os.remove(anchors_0_path_C)
        if os.path.exists(anchors_1_path_C):
            os.remove(anchors_1_path_C)
        shutil.copy(os.path.join(path, "fd_blazeface_anchors_0.h"), anchors_0_path_C)
        shutil.copy(os.path.join(path, "fd_blazeface_anchors_1.h"), anchors_1_path_C)

    with open(os.path.join(path, "app_config.h"), "wt") as f:
        f.write("/**\n")
        f.write("******************************************************************************\n")
        f.write("* @file    app_config.h\n")
        f.write("* @author  GPM Application Team\n")
        f.write("*\n")
        f.write("******************************************************************************\n")
        f.write("* @attention\n")
        f.write("*\n")
        f.write("* Copyright (c) 2023 STMicroelectronics.\n")
        f.write("* All rights reserved.\n")
        f.write("*\n")
        f.write("* This software is licensed under terms that can be found in the LICENSE file\n")
        f.write("* in the root directory of this software component.\n")
        f.write("* If no LICENSE file comes with this software, it is provided AS-IS.\n")
        f.write("*\n")
        f.write("******************************************************************************\n")
        f.write("*/\n\n")
        f.write("/* ---------------    Generated code    ----------------- */\n")
        f.write("#ifndef APP_CONFIG\n")
        f.write("#define APP_CONFIG\n\n")
        f.write('#include "arm_math.h"\n\n')
        f.write("#define USE_DCACHE\n\n")
        f.write("/*Defines: CMW_MIRRORFLIP_NONE; CMW_MIRRORFLIP_FLIP; CMW_MIRRORFLIP_MIRROR; CMW_MIRRORFLIP_FLIP_MIRROR;*/\n")
        f.write("#define CAMERA_FLIP CMW_MIRRORFLIP_NONE\n\n")
        f.write("")
        f.write("#define ASPECT_RATIO_CROP (1) /* Crop both pipes to nn input aspect ratio; Original aspect ratio kept */\n")
        f.write("#define ASPECT_RATIO_FIT (2) /* Resize both pipe to NN input aspect ratio; Original aspect ratio not kept */\n")
        f.write("#define ASPECT_RATIO_FULLSCREEN (3) /* Resize camera image to NN input size and display a fullscreen image */\n")
        f.write("#define ASPECT_RATIO_MODE {}\n".format(aspect_ratio_dict[params.preprocessing.resizing.aspect_ratio]))
        f.write("\n")

        f.write("/* Postprocessing type configuration */\n")

        if (params.model.model_type == "st_ssd_mobilenet_v1" or params.model.model_type == "ssd_mobilenet_v2_fpnlite") and not TFLite_Detection_PostProcess_id:
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_OD_ST_SSD_UF\n")
        elif TFLite_Detection_PostProcess_id:
            raise TypeError("Not supported yet on N6")
        elif params.model.model_type == "CENTER_NET":
            raise TypeError("Not supported yet on N6")
        elif (params.model.model_type == "yolov2t" or params.model.model_type == "st_yololcv1"):
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_OD_YOLO_V2_UI\n\n")
        elif params.model.model_type in ("yolov8n", "yolov11n", "yolov5u"):
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_OD_YOLO_V8_UI\n")
        elif params.model.model_type == "st_yoloxn":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_OD_ST_YOLOX_UI\n")
        elif params.model.model_type == "face_detect_front":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_OD_BLAZEFACE_UI\n")
        else:
            raise TypeError("Please select one of the supported model_type")
        f.write("\n")
        f.write("#define COLOR_BGR (0)\n")
        f.write("#define COLOR_RGB (1)\n")
        f.write("#define COLOR_MODE {}\n".format(color_mode_n6_dict[params.preprocessing.color_mode]))

        f.write("/* Classes */\n")
        if params.model.model_type == "st_ssd_mobilenet_v1" or params.model.model_type == "ssd_mobilenet_v2_fpnlite":
            f.write("#define NB_CLASSES        ({})\n".format(len(class_names)+1))
        else:
            f.write("#define NB_CLASSES   ({})\n".format(len(class_names)))
        f.write("#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {}\n".format(classes))

        if (params.model.model_type == "st_ssd_mobilenet_v1" or params.model.model_type == "ssd_mobilenet_v2_fpnlite") and not TFLite_Detection_PostProcess_id:
            f.write("/* Postprocessing ST_SSD configuration */\n")
            f.write("#define AI_OD_SSD_ST_PP_NB_CLASSES         ({})\n".format(len(class_names)+1))
            f.write("#define AI_OD_SSD_ST_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OD_SSD_ST_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_SSD_ST_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OD_SSD_ST_PP_TOTAL_DETECTIONS   ({})\n".format(int(output_details['shape'][1])))
        elif  TFLite_Detection_PostProcess_id:
            f.write("\n/* Postprocessing SSD configuration */\n")
            f.write("#define AI_OD_SSD_PP_XY_SCALE           ({})\n".format(XY))
            f.write("#define AI_OD_SSD_PP_WH_SCALE           ({})\n".format(WH))
            f.write("#define AI_OD_SSD_PP_NB_CLASSES         ({})\n".format(len(class_names)+1))
            f.write("#define AI_OD_SSD_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OD_SSD_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_SSD_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OD_SSD_PP_TOTAL_DETECTIONS   ({})\n".format(int(output_details['shape'][1])))
        elif (params.model.model_type in ("yolov2t", "st_yololcv1")):
            f.write("\n/* Postprocessing TINY_YOLO_V2 configuration */\n")

            f.write("#define AI_OD_YOLOV2_PP_NB_CLASSES      ({})\n".format(len(class_names)))
            f.write("#define AI_OD_YOLOV2_PP_NB_ANCHORS      ({})\n".format(int(len(params.postprocessing.yolo_anchors))))
            f.write("#define AI_OD_YOLOV2_PP_GRID_WIDTH      ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride)))
            f.write("#define AI_OD_YOLOV2_PP_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride)))
            f.write("#define AI_OD_YOLOV2_PP_NB_INPUT_BOXES  (AI_OD_YOLOV2_PP_GRID_WIDTH * AI_OD_YOLOV2_PP_GRID_HEIGHT)\n")
            anchors_string = "{" + ", ".join([f"{x:.6f}" for row in params.postprocessing.yolo_anchors for x in row]) + "}"
            f.write("static const float32_t AI_OD_YOLOV2_PP_ANCHORS[2*AI_OD_YOLOV2_PP_NB_ANCHORS] ={};\n".format(anchors_string))
            f.write("#define AI_OD_YOLOV2_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_YOLOV2_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OD_YOLOV2_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))

        elif (params.model.model_type == "st_yoloxn"):
            f.write("\n/* Postprocessing ST_YOLO_X configuration */\n")
            yolo_anchors = np.concatenate(params.postprocessing.yolo_anchors).flatten()
            f.write("#define AI_OD_ST_YOLOX_PP_NB_CLASSES        ({})\n".format(len(class_names)))

            f.write("#define AI_OD_ST_YOLOX_PP_L_GRID_WIDTH      ({})\n".format(int(input_shape[2]//params.postprocessing.network_stride[0])))
            f.write("#define AI_OD_ST_YOLOX_PP_L_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride[0])))
            f.write("#define AI_OD_ST_YOLOX_PP_L_NB_INPUT_BOXES  (AI_OD_ST_YOLOX_PP_L_GRID_WIDTH * AI_OD_ST_YOLOX_PP_L_GRID_HEIGHT)\n")

            f.write("#define AI_OD_ST_YOLOX_PP_M_GRID_WIDTH      ({})\n".format(int(input_shape[2]//params.postprocessing.network_stride[1])))
            f.write("#define AI_OD_ST_YOLOX_PP_M_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride[1])))
            f.write("#define AI_OD_ST_YOLOX_PP_M_NB_INPUT_BOXES  (AI_OD_ST_YOLOX_PP_M_GRID_WIDTH * AI_OD_ST_YOLOX_PP_M_GRID_HEIGHT)\n")

            f.write("#define AI_OD_ST_YOLOX_PP_S_GRID_WIDTH      ({})\n".format(int(input_shape[2]//params.postprocessing.network_stride[2])))
            f.write("#define AI_OD_ST_YOLOX_PP_S_GRID_HEIGHT     ({})\n".format(int(input_shape[1]//params.postprocessing.network_stride[2])))
            f.write("#define AI_OD_ST_YOLOX_PP_S_NB_INPUT_BOXES  (AI_OD_ST_YOLOX_PP_S_GRID_WIDTH * AI_OD_ST_YOLOX_PP_S_GRID_HEIGHT)\n")

            f.write("#define AI_OD_ST_YOLOX_PP_NB_ANCHORS        ({})\n".format(int(len(yolo_anchors)/2)))

            anchors_string = "{" + ", ".join([f"{(x*int(input_shape[2]//params.postprocessing.network_stride[0])):.6f}" for row in params.postprocessing.yolo_anchors for x in row]) + "}"
            f.write("static const float32_t AI_OD_ST_YOLOX_PP_L_ANCHORS[2*AI_OD_ST_YOLOX_PP_NB_ANCHORS] ={};\n".format(anchors_string))

            anchors_string = "{" + ", ".join([f"{(x*int(input_shape[2]//params.postprocessing.network_stride[1])):.6f}" for row in params.postprocessing.yolo_anchors for x in row]) + "}"
            f.write("static const float32_t AI_OD_ST_YOLOX_PP_M_ANCHORS[2*AI_OD_ST_YOLOX_PP_NB_ANCHORS] ={};\n".format(anchors_string))

            anchors_string = "{" + ", ".join([f"{(x*int(input_shape[2]//params.postprocessing.network_stride[2])):.6f}" for row in params.postprocessing.yolo_anchors for x in row]) + "}"
            f.write("static const float32_t AI_OD_ST_YOLOX_PP_S_ANCHORS[2*AI_OD_ST_YOLOX_PP_NB_ANCHORS] ={};\n".format(anchors_string))

            f.write("#define AI_OD_ST_YOLOX_PP_IOU_THRESHOLD      ({})\n".format(float(params.postprocessing.NMS_thresh)))
            f.write("#define AI_OD_ST_YOLOX_PP_CONF_THRESHOLD     ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_ST_YOLOX_PP_MAX_BOXES_LIMIT    ({})\n".format(int(params.postprocessing.max_detection_boxes)))

        elif (params.model.model_type in ("yolov8n", "yolov11n", "yolov5u")):
            f.write("\n/* Postprocessing YOLO_V8 configuration */\n")

            if quantized_model_path.lower().endswith('.tflite'):
                out_shape = output_details["shape"]
            elif quantized_model_path.lower().endswith('.onnx'):
                out_shape = outputs[0].shape
            else:
                raise TypeError("Please provide a TFLITE or ONNX model for N6 deployment")

            f.write("#define AI_OD_YOLOV8_PP_NB_CLASSES        ({})\n".format(int(out_shape[1]-4)))
            f.write("#define AI_OD_YOLOV8_PP_TOTAL_BOXES       ({})\n".format(int(out_shape[2])))
            f.write("#define AI_OD_YOLOV8_PP_MAX_BOXES_LIMIT   ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OD_YOLOV8_PP_CONF_THRESHOLD    ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_YOLOV8_PP_IOU_THRESHOLD     ({})\n".format(float(params.postprocessing.NMS_thresh)))

        elif (params.model.model_type in ("face_detect_front")):
            f.write("\n/* Postprocessing OD_BLAZEFACE configuration */\n")

            outs_info = interpreter_quant.get_output_details()
            #print(outs_info)
            output_shapes =[]
            for buffer in outs_info:
                output_shapes.append(buffer["shape"])
            sorted_shapes = sorted(output_shapes, key=lambda arr: (arr[1], arr[2]), reverse=True)

            f.write("#define AI_OD_BLAZEFACE_PP_NB_KEYPOINTS      ({})\n".format(int((sorted_shapes[0][2]-4)/2)))
            f.write("#define AI_OD_BLAZEFACE_PP_NB_CLASSES        ({})\n".format(int(sorted_shapes[-1][-1])))
            f.write("#define AI_OD_BLAZEFACE_PP_IMG_SIZE          ({})\n".format(int(input_shape[1])))
            f.write("#define AI_OD_BLAZEFACE_PP_OUT_0_NB_BOXES    ({})\n".format(int(sorted_shapes[0][1])))
            f.write("#define AI_OD_BLAZEFACE_PP_OUT_1_NB_BOXES    ({})\n".format(int(sorted_shapes[-1][1])))

            f.write("#define AI_OD_BLAZEFACE_PP_MAX_BOXES_LIMIT   ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OD_BLAZEFACE_PP_CONF_THRESHOLD    ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_BLAZEFACE_PP_IOU_THRESHOLD     ({})\n".format(float(params.postprocessing.NMS_thresh)))



        f.write('#define WELCOME_MSG_1         "{}"\n'.format(os.path.basename(params.model.model_path)))
        # @Todo retieve info from stedgeai output
        if config.deployment.hardware_setup.board == 'NUCLEO-N657X0-Q':
            f.write('#define WELCOME_MSG_2         ((char *[2]) {"Model Running in STM32 MCU", "internal memory"})')
        else:
            f.write('#define WELCOME_MSG_2       "{}"\n'.format("Model Running in STM32 MCU internal memory"))

        f.write("\n")
        f.write("#endif      /* APP_CONFIG */\n")

    return TFLite_Detection_PostProcess_id, quantized_model_path


def gen_h_user_file_n6_onnx_ssd(config, quantized_model_path: str = None) -> None:

    """
    Generates a C header file containing user configuration for the AI model.

    Args:
        config: A configuration object containing user configuration for the AI model.
        quantized_model_path: The path to the quantized model file.

    """

    import onnxruntime
    import sys

    params = config

    model = onnxruntime.InferenceSession(quantized_model_path)
    inputs  = model.get_inputs()
    outputs = model.get_outputs()
    input_shape_raw = inputs[0].shape

    class_names = params.dataset.class_names

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    classes = '{\\\n"background",'

    for i, x in enumerate(params.dataset.class_names):
        if i == (len(class_names) - 1):
            classes = classes + '   "' + str(x) + '"' + '}\\'
        else:
            classes = classes + '   "' + str(x) + '"' + ' ,' + ('\\\n' if (i % 5 == 0 and i != 0) else '')
    
    if params.model.model_type == "ssd":
        from object_detection.tf.src.postprocessing  import generate_ssd_priors
        center_variance = 0.1
        size_variance = 0.2

        image_size =  (input_shape_raw[2], input_shape_raw[3], input_shape_raw[1])
        model_anchor_centers = generate_ssd_priors(image_size[0])

        anch_arr = model_anchor_centers.numpy()

        anch_flat = anch_arr.reshape(int(anch_arr.shape[0] * anch_arr.shape[1]))
        # Format the array elements as strings with 'f' suffix for floats in C
        formatted_anch_flat = ", ".join(f"{float(x)}" for x in anch_flat)
        c_anch_str = f"const float32_t g_Anchors[{int(anch_arr.shape[0] * anch_arr.shape[1])}] = {{ {formatted_anch_flat} }};"

        with open(os.path.join(path, "ssd_anchors.h"), "wt") as f:
            f.write("#ifndef __ANCHORS_H__\n")
            f.write("#define __ANCHORS_H__\n\n")
            f.write(c_anch_str)
            f.write("\n")
            f.write("#endif /* __ANCHORS_H__ */\n")

        # Copy the anchors to the C project
        anchors_path_C = os.path.join(params.deployment.c_project_path, 'Application', params.deployment.hardware_setup.board, 'Inc', 'ssd_anchors.h')


        if os.path.exists(anchors_path_C):
            os.remove(anchors_path_C)
        

        shutil.copy(os.path.join(path, "ssd_anchors.h"), anchors_path_C)

    with open(os.path.join(path, "app_config.h"), "wt") as f:
        f.write("/**\n")
        f.write("******************************************************************************\n")
        f.write("* @file    app_config.h\n")
        f.write("* @author  GPM Application Team\n")
        f.write("*\n")
        f.write("******************************************************************************\n")
        f.write("* @attention\n")
        f.write("*\n")
        f.write("* Copyright (c) 2023 STMicroelectronics.\n")
        f.write("* All rights reserved.\n")
        f.write("*\n")
        f.write("* This software is licensed under terms that can be found in the LICENSE file\n")
        f.write("* in the root directory of this software component.\n")
        f.write("* If no LICENSE file comes with this software, it is provided AS-IS.\n")
        f.write("*\n")
        f.write("******************************************************************************\n")
        f.write("*/\n\n")
        f.write("/* ---------------    Generated code    ----------------- */\n")
        f.write("#ifndef APP_CONFIG\n")
        f.write("#define APP_CONFIG\n\n")
        f.write('#include "arm_math.h"\n\n')
        f.write("#define USE_DCACHE\n\n")
        f.write("/*Defines: CMW_MIRRORFLIP_NONE; CMW_MIRRORFLIP_FLIP; CMW_MIRRORFLIP_MIRROR; CMW_MIRRORFLIP_FLIP_MIRROR;*/\n")
        f.write("#define CAMERA_FLIP CMW_MIRRORFLIP_NONE\n\n")
        f.write("")
        f.write("#define ASPECT_RATIO_CROP (1) /* Crop both pipes to nn input aspect ratio; Original aspect ratio kept */\n")
        f.write("#define ASPECT_RATIO_FIT (2) /* Resize both pipe to NN input aspect ratio; Original aspect ratio not kept */\n")
        f.write("#define ASPECT_RATIO_FULLSCREEN (3) /* Resize camera image to NN input size and display a fullscreen image */\n")
        f.write("#define ASPECT_RATIO_MODE {}\n".format(aspect_ratio_dict[params.preprocessing.resizing.aspect_ratio]))
        f.write("\n")

        f.write("/* Postprocessing type configuration */\n")

        if params.model.model_type == "ssd":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_OD_SSD_UI\n")
        else:
            raise TypeError("Please select one of the supported model_type")
        f.write("\n")
        f.write("#define COLOR_BGR (0)\n")
        f.write("#define COLOR_RGB (1)\n")
        f.write("#define COLOR_MODE {}\n".format(color_mode_n6_dict[params.preprocessing.color_mode]))

        f.write("/* Classes */\n")
        f.write("#define NB_CLASSES   ({})\n".format(len(class_names)+1))
        f.write("#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {}\n".format(classes))

        if params.model.model_type == "ssd":
            f.write("\n/* Postprocessing SSD configuration */\n")

            f.write("#define AI_OD_SSD_PP_NB_CLASSES        ({})\n".format(len(class_names)+1))
            f.write("#define AI_OD_SSD_PP_TOTAL_DETECTIONS   ({})\n".format(int(anch_arr.shape[0])))
            f.write("#define AI_OD_SSD_PP_XY_VARIANCE        ({})\n".format(float(center_variance)))
            f.write("#define AI_OD_SSD_PP_WH_VARIANCE        ({})\n".format(float(size_variance)))

            f.write("#define AI_OD_SSD_PP_MAX_BOXES_LIMIT   ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OD_SSD_PP_CONF_THRESHOLD    ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_SSD_PP_IOU_THRESHOLD     ({})\n".format(float(params.postprocessing.NMS_thresh)))



        f.write('#define WELCOME_MSG_1         "{}"\n'.format(os.path.basename(params.model.model_path)))
        # @Todo retieve info from stedgeai output
        if config.deployment.hardware_setup.board == 'NUCLEO-N657X0-Q':
            f.write('#define WELCOME_MSG_2         ((char *[2]) {"Model Running in STM32 MCU", "internal memory"})')
        else:
            f.write('#define WELCOME_MSG_2       "{}"\n'.format("Model Running in STM32 MCU internal memory"))

        f.write("\n")
        f.write("#endif      /* APP_CONFIG */\n")

    return None, quantized_model_path

def gen_h_user_file_n6_onnx_yolod(config, quantized_model_path: str = None) -> None:

    """
    Generates a C header file containing user configuration for the AI model.

    Args:
        config: A configuration object containing user configuration for the AI model.
        quantized_model_path: The path to the quantized model file.

    """

    import onnxruntime
    import sys

    params = config

    model = onnxruntime.InferenceSession(quantized_model_path)
    inputs  = model.get_inputs()
    outputs = model.get_outputs()
    input_shape_raw = inputs[0].shape

    class_names = params.dataset.class_names

    path = os.path.join(HydraConfig.get().runtime.output_dir, "C_header/")

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)

    classes = '{\\\n'

    for i, x in enumerate(params.dataset.class_names):
        if i == (len(class_names) - 1):
            classes = classes + '   "' + str(x) + '"' + '}\\'
        else:
            classes = classes + '   "' + str(x) + '"' + ' ,' + ('\\\n' if (i % 5 == 0 and i != 0) else '')
    
    if params.model.model_type == "st_yolod":
        image_size =  (input_shape_raw[2], input_shape_raw[3], input_shape_raw[1])

    with open(os.path.join(path, "app_config.h"), "wt") as f:
        f.write("/**\n")
        f.write("******************************************************************************\n")
        f.write("* @file    app_config.h\n")
        f.write("* @author  GPM Application Team\n")
        f.write("*\n")
        f.write("******************************************************************************\n")
        f.write("* @attention\n")
        f.write("*\n")
        f.write("* Copyright (c) 2023 STMicroelectronics.\n")
        f.write("* All rights reserved.\n")
        f.write("*\n")
        f.write("* This software is licensed under terms that can be found in the LICENSE file\n")
        f.write("* in the root directory of this software component.\n")
        f.write("* If no LICENSE file comes with this software, it is provided AS-IS.\n")
        f.write("*\n")
        f.write("******************************************************************************\n")
        f.write("*/\n\n")
        f.write("/* ---------------    Generated code    ----------------- */\n")
        f.write("#ifndef APP_CONFIG\n")
        f.write("#define APP_CONFIG\n\n")
        f.write('#include "arm_math.h"\n\n')
        f.write("#define USE_DCACHE\n\n")
        f.write("/*Defines: CMW_MIRRORFLIP_NONE; CMW_MIRRORFLIP_FLIP; CMW_MIRRORFLIP_MIRROR; CMW_MIRRORFLIP_FLIP_MIRROR;*/\n")
        f.write("#define CAMERA_FLIP CMW_MIRRORFLIP_NONE\n\n")
        f.write("")
        f.write("#define ASPECT_RATIO_CROP (1) /* Crop both pipes to nn input aspect ratio; Original aspect ratio kept */\n")
        f.write("#define ASPECT_RATIO_FIT (2) /* Resize both pipe to NN input aspect ratio; Original aspect ratio not kept */\n")
        f.write("#define ASPECT_RATIO_FULLSCREEN (3) /* Resize camera image to NN input size and display a fullscreen image */\n")
        f.write("#define ASPECT_RATIO_MODE {}\n".format(aspect_ratio_dict[params.preprocessing.resizing.aspect_ratio]))
        f.write("\n")

        f.write("/* Postprocessing type configuration */\n")

        if params.model.model_type == "st_yolod":
            f.write("#define POSTPROCESS_TYPE    POSTPROCESS_OD_ST_YOLOD_UI\n")
        else:
            raise TypeError("Please select one of the supported model_type")
        f.write("\n")
        f.write("#define COLOR_BGR (0)\n")
        f.write("#define COLOR_RGB (1)\n")
        f.write("#define COLOR_MODE {}\n".format(color_mode_n6_dict[params.preprocessing.color_mode]))

        f.write("/* Classes */\n")
        f.write("#define NB_CLASSES   ({})\n".format(len(class_names)))
        f.write("#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {}\n".format(classes))

        if params.model.model_type == "st_yolod":
            f.write("\n/* Postprocessing ST_YOLOD configuration */\n")

            f.write("#define AI_OD_YOLO_D_PP_NB_CLASSES         ({})\n".format(len(class_names)))
            f.write("#define AI_OD_YOLO_D_PP_IMG_WIDTH          ({})\n".format(int(image_size[0])))
            f.write("#define AI_OD_YOLO_D_PP_IMG_HEIGHT         ({})\n".format(int(image_size[1])))
            f.write("#define AI_OD_YOLO_D_PP_STRIDE_0           ({})\n".format(8))
            f.write("#define AI_OD_YOLO_D_PP_STRIDE_1           ({})\n".format(16))
            f.write("#define AI_OD_YOLO_D_PP_STRIDE_2           ({})\n".format(32))

            f.write("#define AI_OD_YOLO_D_PP_MAX_BOXES_LIMIT   ({})\n".format(int(params.postprocessing.max_detection_boxes)))
            f.write("#define AI_OD_YOLO_D_PP_CONF_THRESHOLD    ({})\n".format(float(params.postprocessing.confidence_thresh)))
            f.write("#define AI_OD_YOLO_D_PP_IOU_THRESHOLD     ({})\n".format(float(params.postprocessing.NMS_thresh)))



        f.write('#define WELCOME_MSG_1         "{}"\n'.format(os.path.basename(params.model.model_path)))
        # @Todo retieve info from stedgeai output
        if config.deployment.hardware_setup.board == 'NUCLEO-N657X0-Q':
            f.write('#define WELCOME_MSG_2         ((char *[2]) {"Model Running in STM32 MCU", "internal memory"})')
        else:
            f.write('#define WELCOME_MSG_2       "{}"\n'.format("Model Running in STM32 MCU internal memory"))

        f.write("\n")
        f.write("#endif      /* APP_CONFIG */\n")

    return None, quantized_model_path