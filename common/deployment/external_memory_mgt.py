# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import json
import sys
from typing import Dict

from models_utils import get_model_name_and_its_input_shape


def update_activation_c_code(c_project_path: str, path_network_c_graph: str, available_AXIRAM: int, cfg = None, custom_objects: Dict = None):
    
    path_main_h=os.path.join(c_project_path, "Application/STM32H747I-DISCO/Inc/CM7/main.h")
    path_main_c=os.path.join(c_project_path, "Application/STM32H747I-DISCO/Src/CM7/main.c")
    path_ai_interface_h=os.path.join(c_project_path, "Application/STM32H747I-DISCO/Inc/CM7/ai_interface.h")

    ### Get NN preprocessing buffers size
    aspect_ratio = cfg.preprocessing.resizing.aspect_ratio
    _, input_shape = get_model_name_and_its_input_shape(model_path=cfg.general.model_path, custom_objects=custom_objects)
    network_height = input_shape[0]
    network_width = input_shape[1]
    network_channel = input_shape[2]
    # Grayscale
    if network_channel == 1:
        resize_buffer_size = network_height*network_width
    # RGB565
    if network_channel == 3:
        resize_buffer_size = network_height*network_width*2
    
    QVGA_width = 320
    QVGA_height = 240
    VGA_width = 640
    VGA_height = 480

    if aspect_ratio == "crop":
        if network_width <= QVGA_height and network_height <= QVGA_height:
            cam_res = "CAMERA_R320x240"
            cam_res_width = "QVGA_RES_HEIGHT"
            cam_res_height = "QVGA_RES_HEIGHT"
            cam_buffer_width = "QVGA_RES_HEIGHT"
            cam_buffer_height = "QVGA_RES_HEIGHT"
        elif network_width <= VGA_height and network_height <= VGA_height:
            cam_res = "CAMERA_R640x480"
            cam_res_width = "VGA_RES_HEIGHT"
            cam_res_height = "VGA_RES_HEIGHT"
            cam_buffer_width = "VGA_RES_HEIGHT"
            cam_buffer_height = "VGA_RES_HEIGHT"
    elif aspect_ratio == "padding":
        if network_width <= QVGA_width and network_height <= QVGA_width:
            cam_res = "CAMERA_R320x240"
            cam_res_width = "QVGA_RES_WIDTH"
            cam_res_height = "QVGA_RES_HEIGHT"
            cam_buffer_width = "QVGA_RES_WIDTH"
            cam_buffer_height = "QVGA_RES_WIDTH"
        elif network_width <= VGA_width and network_height <= VGA_width:
            cam_res = "CAMERA_R640x480"
            cam_res_width = "VGA_RES_WIDTH"
            cam_res_height = "VGA_RES_HEIGHT"
            cam_buffer_width = "VGA_RES_WIDTH"
            cam_buffer_height = "VGA_RES_WIDTH"
    else:
        if network_width <= QVGA_width and network_height <= QVGA_height:
            cam_res = "CAMERA_R320x240"
            cam_res_width = "QVGA_RES_WIDTH"
            cam_res_height = "QVGA_RES_HEIGHT"
            cam_buffer_width = "QVGA_RES_WIDTH"
            cam_buffer_height = "QVGA_RES_HEIGHT"
        elif network_width <= VGA_width and network_height <= VGA_height:
            cam_res = "CAMERA_R640x480"
            cam_res_width = "VGA_RES_WIDTH"
            cam_res_height = "VGA_RES_HEIGHT"
            cam_buffer_width = "VGA_RES_WIDTH"
            cam_buffer_height = "VGA_RES_HEIGHT"
    if not 'cam_res' in locals():
        ValueError("Needed camera resolution ({}x{}) exceeds VGA format. ".format(network_width,network_height))

    ### Generate main.h
    with open(os.path.join(path_main_h), 'r') as f1, open(os.path.join(os.path.dirname(path_main_h), 'main_modify.h'),'w') as f2:
        for lineNumber, line in enumerate(f1):
            if "#define CAMERA_RESOLUTION" in line:
                line = "#define CAMERA_RESOLUTION (" + cam_res + ")\n"
            elif "#define CAM_RES_WIDTH" in line:
                line = "#define CAM_RES_WIDTH (" + cam_res_width + ")\n"
            elif "#define CAM_RES_HEIGHT" in line:
                line = "#define CAM_RES_HEIGHT (" + cam_res_height + ")\n"
            f2.write(line)
    os.replace(os.path.join(os.path.dirname(path_main_h), 'main_modify.h'), path_main_h)

    if cam_buffer_width == "QVGA_RES_WIDTH":
        cam_buffer_width = QVGA_width
    elif cam_buffer_width == "QVGA_RES_HEIGHT":
        cam_buffer_width = QVGA_height
    elif cam_buffer_width == "VGA_RES_WIDTH":
        cam_buffer_width = VGA_width
    else:
        cam_buffer_width = VGA_height
    if cam_buffer_height == "QVGA_RES_WIDTH":
        cam_buffer_height = QVGA_width
    elif cam_buffer_height == "QVGA_RES_HEIGHT":
        cam_buffer_height = QVGA_height
    elif cam_buffer_height == "VGA_RES_WIDTH":
        cam_buffer_height = VGA_width
    else:
        cam_buffer_height = VGA_height
    # Grayscale
    if network_channel == 1:
        cam_buffer_size = cam_buffer_height*cam_buffer_width
    # RGB565
    if network_channel == 3:
        cam_buffer_size = cam_buffer_height*cam_buffer_width*2

    ### Generate main.c
    with open(os.path.join(path_network_c_graph), 'r') as f:
            graph = json.load(f)
    
    if "network_c_info.json" in os.path.join(path_network_c_graph):
        # List activations 
        activations = []
        for element in graph["memory_pools"]:
            if element["rights"] == "ACC_WRITE" and element["used_size_bytes"] != 0:
                activations.append(element)
        # Sort activations by size_bytes 
        activations = sorted(activations, key=lambda x: x['used_size_bytes'])
        writeLine = True
        with open(os.path.join(path_main_c), 'r') as f1, open(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'),'w') as f2:
            for lineNumber, line in enumerate(f1):
                # re.findall(" uint8_t NN_Activation_Buffer[AI_NETWORK_DATA_ACTIVATIONS_COUNT];", line)
                if line == " /*** @GENERATED CODE START - DO NOT TOUCH@ ***/\n":
                    # saveline = line
                    pool_list_str = []
                    for i, pool in enumerate(activations):
                        name_pool = "NN_Activation_Buffer_" + pool["name"] if pool["name"] != "heap_overlay_pool" else "NN_Activation_Buffer_AXIRAM"
                        line += """__attribute__((section(".""" + name_pool + """")))\n__attribute__ ((aligned (32)))\n"""
                        line += "static uint8_t " + name_pool + "[AI_ACTIVATION_" + str(i+1) + "_SIZE_BYTES + 32 - (AI_ACTIVATION_" + str(i+1) + "_SIZE_BYTES%32)];\n"
                        pool_list_str.append(name_pool)
                        if name_pool == "NN_Activation_Buffer_AXIRAM":
                            available_AXIRAM = available_AXIRAM - pool['used_size_bytes']
                    line +=  "ai_handle NN_Activation_Buffer[AI_ACTIVATION_BUFFERS_COUNT] = { "
                    for pool in pool_list_str:
                        line += pool + ", "
                    line += "};\n\n"
                    f2.write(line)
                    writeLine = False
                if line == " /*** @GENERATED CODE STOP - DO NOT TOUCH@ ***/\n":
                    writeLine = True 
                if writeLine == True:
                    f2.write(line)
        os.replace(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'), path_main_c)
        
        writeLine = True
        with open(os.path.join(path_main_c), 'r') as f1, open(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'),'w') as f2:
            for lineNumber, line in enumerate(f1):
                if """__attribute__((section(".CapturedImage_Buffer""" in line:
                    if cam_buffer_size < available_AXIRAM:
                        available_AXIRAM = available_AXIRAM - cam_buffer_size
                        line = """__attribute__((section(".CapturedImage_Buffer_AXIRAM")))\n"""
                    else:
                        line = """__attribute__((section(".CapturedImage_Buffer_SDRAM")))\n"""
                if """__attribute__((section(".RescaledImage_Buffer""" in line:
                    if resize_buffer_size < available_AXIRAM:
                        available_AXIRAM = available_AXIRAM - resize_buffer_size
                        line = """__attribute__((section(".RescaledImage_Buffer_AXIRAM")))\n"""
                    else:
                        line = """__attribute__((section(".RescaledImage_Buffer_SDRAM")))\n"""
                f2.write(line)
        os.replace(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'), path_main_c)
        
        ### Generate ai_interface.h
        input_buffer_name = "serving_default_image_input0_output_array"
        input_buffer_activation_buffer_index = 0

    else:
        number_of_pools =  len(graph["activations"])
        activations = dict(sorted(graph["activations"].items(), key=lambda item: item[1]['pool_size']))
        writeLine = True
        with open(os.path.join(path_main_c), 'r') as f1, open(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'),'w') as f2:
            for lineNumber, line in enumerate(f1):
                # re.findall(" uint8_t NN_Activation_Buffer[AI_NETWORK_DATA_ACTIVATIONS_COUNT];", line)
                if line == " /*** @GENERATED CODE START - DO NOT TOUCH@ ***/\n":
                    # saveline = line
                    pool_list_str = []
                    for i, pool in enumerate(activations.items()):
                        name_pool =  "NN_Activation_Buffer_" + pool[0] if pool[0] != "heap_overlay_pool" else "NN_Activation_Buffer_AXIRAM"
                        line +="""__attribute__((section("."""+ name_pool +"""")))\n__attribute__ ((aligned (32)))\n"""
                        line += "static uint8_t " + name_pool + "[AI_ACTIVATION_" + str(i+1) +"_SIZE_BYTES + 32 - (AI_ACTIVATION_" + str(i+1)+ "_SIZE_BYTES%32)];\n"
                        pool_list_str.append(name_pool)
                        if name_pool == "NN_Activation_Buffer_AXIRAM":
                            available_AXIRAM = available_AXIRAM - pool[1]['pool_size']
                    line +=  "ai_handle NN_Activation_Buffer[AI_ACTIVATION_BUFFERS_COUNT] " + "= { "
                    for pool in pool_list_str:
                        line += pool + ", "
                    line += "};\n\n"
                    f2.write(line)
                    writeLine = False
                if line == " /*** @GENERATED CODE STOP - DO NOT TOUCH@ ***/\n":
                    writeLine = True 
                if writeLine == True:
                    f2.write(line)
        os.replace(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'), path_main_c)
        with open(os.path.join(path_network_c_graph), 'r') as f:
                graph = json.load(f)
        number_of_pools =  len(graph["activations"])
        activations = dict(sorted(graph["activations"].items(), key=lambda item: item[1]['pool_size']))
        writeLine = True
        with open(os.path.join(path_main_c), 'r') as f1, open(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'),'w') as f2:
            for lineNumber, line in enumerate(f1):
                if """__attribute__((section(".CapturedImage_Buffer""" in line:
                    if cam_buffer_size < available_AXIRAM:
                        available_AXIRAM = available_AXIRAM - cam_buffer_size
                        line = """__attribute__((section(".CapturedImage_Buffer_AXIRAM")))\n"""
                    else:
                        line = """__attribute__((section(".CapturedImage_Buffer_SDRAM")))\n"""
                if """__attribute__((section(".RescaledImage_Buffer""" in line:
                    if resize_buffer_size < available_AXIRAM:
                        available_AXIRAM = available_AXIRAM - resize_buffer_size
                        line = """__attribute__((section(".RescaledImage_Buffer_AXIRAM")))\n"""
                    else:
                        line = """__attribute__((section(".RescaledImage_Buffer_SDRAM")))\n"""
                f2.write(line)
        os.replace(os.path.join(os.path.dirname(path_main_c), 'main_modify.c'), path_main_c)
        
        ### Generate ai_interface.h
        input_buffer_name = graph["inputs"][0]
        input_buffer_activation_buffer_index = 0
        for index, pool in enumerate(activations.items()):
            if len(list(filter(lambda buffer_name: buffer_name['buffer_name'] == input_buffer_name, pool[1]["buffer_offsets"]))) > 0:
                input_buffer_activation_buffer_index = index
     
    with open(os.path.join(path_ai_interface_h), 'r') as f1, open(os.path.join(os.path.dirname(path_ai_interface_h), 'interface_modify.h'),'w') as f2:
        for lineNumber, line in enumerate(f1):
            # re.findall(" uint8_t NN_Activation_Buffer[AI_NETWORK_DATA_ACTIVATIONS_COUNT];", line)
            if line == " /*** @GENERATED CODE START - DO NOT TOUCH@ ***/\n":
                line += "#define AI_NETWORK_INPUTS_IN_ACTIVATIONS_INDEX " + str(input_buffer_activation_buffer_index)
                line += "\n#define AI_NETWORK_INPUTS_IN_ACTIVATIONS_SIZE AI_ACTIVATION_"+ str(input_buffer_activation_buffer_index+1) + "_SIZE_BYTES\n\n"
                f2.write(line)
                writeLine = False
            if line == " /*** @GENERATED CODE STOP - DO NOT TOUCH@ ***/\n":
               writeLine = True 
            if writeLine == True:
                f2.write(line)
    os.replace(os.path.join(os.path.dirname(path_ai_interface_h), 'interface_modify.h'), path_ai_interface_h)