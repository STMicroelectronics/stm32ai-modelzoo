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

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend
from typing import Tuple, Dict, Optional
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf, DictConfig, open_dict
from cfg_utils import aspect_ratio_dict

def gen_h_user_file(config: DictConfig = None, quantized_model_path: str = None, board: str = None) -> None:
    """
    Generates a C header file containing user configuration for the AI model.

    Args:
        config: A configuration object containing user configuration for the AI model.
        quantized_model_path: The path to the quantized model file.
        board: the name of the board
    """

    class Flags:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    params = Flags(**config)
    class_names = params.dataset.class_names
    # input_shape = params.deployment.model.input_shape

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
    input_shape = input_details['shape']
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
        f.write("#define NB_CLASSES        ({})\n".format(len(class_names)))
        f.write("#define INPUT_HEIGHT      ({})\n".format(int(input_shape[1])))
        f.write("#define INPUT_WIDTH       ({})\n".format(int(input_shape[2])))
        f.write("#define INPUT_CHANNELS    ({})\n".format(int(input_shape[3])))
        f.write("\n")
        f.write("/* Classes */\n")
        f.write("#define CLASSES_TABLE const char* classes_table[NB_CLASSES] = {}\n".format(classes))
        f.write("\n\n")
        f.write("/***** Preprocessing configuration *****/\n\n")
        f.write("/* Aspect Ratio configuration */\n")
        f.write("#define ASPECT_RATIO_FIT        (1)\n")
        f.write("#define ASPECT_RATIO_CROP       (2)\n")
        f.write("#define ASPECT_RATIO_PADDING    (3)\n\n")
        f.write("#define ASPECT_RATIO_MODE    {}\n".format(
            aspect_ratio_dict[params.preprocessing.resizing.aspect_ratio]))
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
        if str(board).split(",")[0] == "NUCLEO-H743ZI2":
            f.write("/* Display configuration */\n")
            f.write("#define DISPLAY_INTERFACE_USB (1)\n")
            f.write("#define DISPLAY_INTERFACE_SPI (2)\n")
            f.write("\n")
            f.write("#define DISPLAY_INTERFACE    {}\n".format(
                params.deployment.hardware_setup.output))
            f.write("\n")
            f.write("/* Camera configuration */\n")
            f.write("#define CAMERA_INTERFACE_DCMI (1)\n")
            f.write("#define CAMERA_INTERFACE_USB  (2)\n")
            f.write("#define CAMERA_INTERFACE_SPI  (3)\n")
            f.write("\n")
            f.write("#define CAMERA_INTERFACE    {}\n".format(
                str(params.deployment.hardware_setup.input)))
            f.write("\n")
            f.write("/* Camera Sensor configuration */\n")
            f.write("#define CAMERA_SENSOR_OV5640 (1)\n")
            f.write("\n")
            f.write("#define CAMERA_SENSOR CAMERA_SENSOR_OV5640\n")
            f.write("\n")

        f.write("#endif      /* __AI_MODEL_CONFIG_H__ */\n")

        # Code do not compile when the USB display files and USB camera files are included at the same time: this code removes the unecessary files
        if str(board).split(",")[0] == "NUCLEO-H743ZI2":
            if params.deployment.hardware_setup.output == "DISPLAY_INTERFACE_USB" and params.deployment.hardware_setup.input == "CAMERA_INTERFACE_USB":
                raise ValueError("\033[31mThere is only one USB port on the Nucleo-H743ZI2 board. You can't select CAMERA_INTERFACE_USB as input and DISPLAY_INTERFACE_USB as output at the same time. \033[39m")

            # .project lines for USB display
            USB_display_str_usb_disp = ["\t\t\t<name>Middlewares/STM32_USB_Display/usb_disp.c</name>\n", "\t\t\t<locationURI>PARENT-3-PROJECT_LOC/Middlewares/ST/STM32_USB_Display/Src/usb_disp.c</locationURI>\n"]
            USB_display_str_usb_disp_desc = ["\t\t\t<name>Middlewares/STM32_USB_Display/usb_disp_desc.c</name>\n", "\t\t\t<locationURI>PARENT-3-PROJECT_LOC/Middlewares/ST/STM32_USB_Display/Src/usb_disp_desc.c</locationURI>\n"]
            USB_display_str_usb_disp_format = ["\t\t\t<name>Middlewares/STM32_USB_Display/usb_disp_format.c</name>\n", "\t\t\t<locationURI>PARENT-3-PROJECT_LOC/Middlewares/ST/STM32_USB_Display/Src/usb_disp_format.c</locationURI>\n"]
            USB_display_str_usbd_conf = ["\t\t\t<name>Middlewares/STM32_USB_Display/usbd_conf.c</name>\n", "\t\t\t<locationURI>PARENT-3-PROJECT_LOC/Middlewares/ST/STM32_USB_Display/Src/usbd_conf.c</locationURI>\n"]
            
            # .project lines for USB camera
            USB_camera_str_nucleo_h743zi2_camera_usb = ["\t\t\t<name>Drivers/BSP/NUCLEO_H743ZI2/nucleo_h743zi2_camera_usb.c</name>\n", "\t\t\t<locationURI>PARENT-3-PROJECT_LOC/Drivers/BSP/NUCLEO-H743ZI2/nucleo_h743zi2_camera_usb.c</locationURI>\n"]

            # .project link
            project_file_link = "\t\t<link>\n"
            # .project type
            project_file_type = "\t\t\t<type>1</type>\n"
            # .project delink
            project_file_delink = "\t\t</link>\n"
            # .project last line
            project_file_last_lines = "\t</linkedResources>\n</projectDescription>"

            # Update .project file to avoid USB conflict
            with open('../../stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2/STM32CubeIDE/.project', 'r') as project_file:
                project_file_data = project_file.read()
            
            # Remove all configuration lines
            project_file_data = project_file_data.replace(project_file_link + USB_display_str_usb_disp[0] + project_file_type + USB_display_str_usb_disp[1] + project_file_delink, '')
            project_file_data = project_file_data.replace(project_file_link + USB_display_str_usb_disp_desc[0] + project_file_type + USB_display_str_usb_disp_desc[1] + project_file_delink, '')
            project_file_data = project_file_data.replace(project_file_link + USB_display_str_usb_disp_format[0] + project_file_type + USB_display_str_usb_disp_format[1] + project_file_delink, '')
            project_file_data = project_file_data.replace(project_file_link + USB_display_str_usbd_conf[0] + project_file_type + USB_display_str_usbd_conf[1] + project_file_delink, '')
            project_file_data = project_file_data.replace(project_file_link + USB_camera_str_nucleo_h743zi2_camera_usb[0] + project_file_type + USB_camera_str_nucleo_h743zi2_camera_usb[1] + project_file_delink, '')

            if params.deployment.hardware_setup.output == "DISPLAY_INTERFACE_USB":
                # Write USB display lines
                project_file_data = project_file_data.replace(project_file_last_lines, \
                                                              project_file_link + USB_display_str_usb_disp[0] + project_file_type + USB_display_str_usb_disp[1] + project_file_delink \
                                                              + project_file_link + USB_display_str_usb_disp_desc[0] + project_file_type + USB_display_str_usb_disp_desc[1] + project_file_delink \
                                                              + project_file_link + USB_display_str_usb_disp_format[0] + project_file_type + USB_display_str_usb_disp_format[1] + project_file_delink \
                                                              + project_file_link + USB_display_str_usbd_conf[0] + project_file_type + USB_display_str_usbd_conf[1] + project_file_delink \
                                                              + project_file_last_lines)
            
            elif params.deployment.hardware_setup.input == "CAMERA_INTERFACE_USB":
                # Write USB camera lines
                project_file_data = project_file_data.replace(project_file_last_lines, \
                                                              project_file_link + USB_camera_str_nucleo_h743zi2_camera_usb[0] + project_file_type + USB_camera_str_nucleo_h743zi2_camera_usb[1] + project_file_delink \
                                                              + project_file_last_lines)

            with open('../../stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2/STM32CubeIDE/.project', 'w') as project_file:
                project_file.write(project_file_data)
