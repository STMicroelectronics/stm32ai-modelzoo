# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import logging
import os
import sys
import warnings
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
import tensorflow as tf
import shutil
import stm_ai_driver as stmaic
from hydra.core.hydra_config import HydraConfig
from typing import Optional
from common_benchmark import cloud_connect
from common_benchmark import cloud_analyze
from common_benchmark import benchmark_model
from stm32ai_dc import (CliLibraryIde, CliLibrarySerie, CliParameters)
import json
import re


def keep_internal_weights(path_network_data_params: str):
    with open(path_network_data_params,'r') as f1,\
        open(os.path.join(os.path.dirname(path_network_data_params), 'network_data_params_modify.c'),'w') as f2:
        for lineNumber, line in enumerate(f1):
            if line == '#include "network_data_params.h"\n':
                line = '#define AI_INTERNAL_FLASH    __attribute__((section(".InternalFlashSection")))\n' + line
            re.findall("const ai_u(?:\d+) (.*)\[(?:\d+)\]", line)
        # @Todo maybe remove tuple to test
            weight = re.findall("const ai_u(?:\d+) (.*)\[(?:\d+)\]", line)
            if weight != []:
                line = 'AI_INTERNAL_FLASH\n' + line
            f2.write(line)
    os.replace(os.path.join(os.path.dirname(path_network_data_params), 'network_data_params_modify.c'), path_network_data_params)


def dispatch_weights(internalFlashSizeFlash_KB: str,
                     kernelFlash_KB: str,
                     applicationSizeFlash_KB: str,
                     path_network_c_graph: str,
                     path_network_data_params: str):

    with open(os.path.join(path_network_c_graph), 'r') as f:
            graph = json.load(f)
    
    # Sort weights from large weights to small ones
    sorted_weights = dict(sorted(graph["weights"].items(), key=lambda item: item[1]['buffer_c_count'], reverse=True))
    
    internalFlashSize_inBytes = int(re.split('(\d+)', internalFlashSizeFlash_KB)[1])*10**3
    kernel_flash_inBytes = int(re.split('(\d+)', kernelFlash_KB)[1])*10**3
    application_size_flash_inBytes = int(re.split('(\d+)', applicationSizeFlash_KB)[1])*10**3
    
    freeInternalFlashSize =  internalFlashSize_inBytes - kernel_flash_inBytes - application_size_flash_inBytes
    ExternalWeightArray = []
    InternalWeightArray = []
    for weight_name, detail in sorted_weights.items():
        if (freeInternalFlashSize - detail["buffer_c_count"]*int(re.split('(\d+)', detail["buffer_c_type"])[1])/8) > 0:
            bytes_number = int(re.split('(\d+)', detail["buffer_c_type"])[1])/8
            # Can fit in Internal Flash
            InternalWeightArray.append(detail["buffer_c_name_addr"])
            # We fit the weights, reduce free size accordingly
            freeInternalFlashSize = freeInternalFlashSize - (detail["buffer_c_count"]*bytes_number)
        else:
            # No free space in Internal Flash
            ExternalWeightArray.append(detail["buffer_c_name_addr"])

    with open(path_network_data_params,'r') as f1,\
        open(os.path.join(os.path.dirname(path_network_data_params), 'network_data_params_modify.c'),'w') as f2:
        for lineNumber, line in enumerate(f1):
            if line == '#include "network_data_params.h"\n':
                line = '#define AI_EXTERNAL_FLASH    __attribute__((section(".ExternalFlashSection")))\n\
#define AI_INTERNAL_FLASH    __attribute__((section(".InternalFlashSection")))\n' + line
            re.findall("const ai_u(?:\d+) (.*)\[(?:\d+)\]", line)
        # @Todo maybe remove tuple to test
            weight = re.findall("const ai_u(?:\d+) (.*)\[(?:\d+)\]", line)
            if weight != []:
                if weight[0] in InternalWeightArray:
                    line = 'AI_INTERNAL_FLASH\n' + line
                elif weight[0] in ExternalWeightArray:
                    line = 'AI_EXTERNAL_FLASH\n' + line
            f2.write(line)
    os.replace(os.path.join(os.path.dirname(path_network_data_params), 'network_data_params_modify.c'), path_network_data_params)
                

def stm32ai_deploy(target: bool = False,
                   stm32ai_version: str = None,
                   c_project_path: str = None,
                   output_dir: str = None,
                   stm32ai_output: str = None,
                   optimization: str = None,
                   path_to_stm32ai: str = None,
                   path_to_cube_ide: str = None,
                   additional_files: list = None,
                   stmaic_conf_filename: str = 'stmaic_c_project.conf',
                   verbosity: int = None,
                   debug: bool = False,
                   model_path: str = None,
                   get_model_name_output: str = None,
                   stm32ai_ide: str = None,
                   stm32ai_serie: str = None,
                   credentials: list[str] = None,
                   on_cloud: bool =False,
                   check_large_model:bool = False, 
                   cfg = None) -> None:
    """
    Deploy an STM32 AI model to a target device.

    Args:
        target (bool): Whether to generate the STM32Cube.AI library and header files on the target device. Defaults to False.
        stm32ai_version (str): Version of the STM32Cube.AI backend to use.
        c_project_path (str): Path to the STM32CubeIDE C project.
        output_dir (str): Path to the output directory.
        stm32ai_output (str: Path to the STM32Cube.AI output directory. Defaults to None.
        optimization (str, optional): Optimization level for the STM32Cube.AI compiler. Defaults to None.
        path_to_stm32ai (str): Path to the STM32Cube.AI compiler executable. Defaults to None.
        path_to_cube_ide (str: Path to the STM32CubeIDE executable. Defaults to None.
        stmaic_conf_filename (list): List of the additional files generated by the deployment that needs to be copied in the C application. Defaults to None.
        stmaic_conf_filename (str): Path to the configuration file used to build the C application. Defaults to 'stmaic_c_project.conf'.
        verbosity (int, optional): Level of verbosity for the STM32Cube.AI driver. Defaults to None.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.
        model_path (str, optional): Path to the AI model file. Defaults to None.
        get_model_name_output(str): Path to the output directory for the generated model name
        stm32ai_ide: IDE to generate code for
        stm32ai_serie: STM32 series to generate code for
        credentials list[str]: User credentials used before to connect.
        on_cloud(bool): whether to deploy using the cloud. Defaults to False
        check_large_model: Launch an analysis to check if the model fit in internal memory, if not it will dispatch in internal and external

    Returns:
        split_weights (bool): return true if the weights has been splitted; False otherwise
    """

    def stmaic_local_call(session):
        """
        Compile the AI model using the STM32Cube.AI compiler.

        Args:
            session (stmaic.STMAiSession): The STM32Cube.AI session object.

        Returns:
            None
        """
        if not check_large_model:
            # Add environment variables
            os.environ["STM32_AI_EXE"] = path_to_stm32ai
            # Set the tools
            tools = stmaic.STMAiTools()
            session.set_tools(tools)
            print("[INFO] Offline CubeAI used; Selected tools: ", tools, flush=True)

            # Clean up the STM32Cube.AI output directory
            shutil.rmtree(stm32ai_output, ignore_errors=True)
            # Set the compiler options
            opt = stmaic.STMAiCompileOptions(allocate_inputs=True, allocate_outputs=True)
            opt.optimization = optimization

            # Compile the AI model
            stmaic.compile(session, opt)
        
        else:
            from external_memory_mgt import update_activation_c_code

            split_weights =  False
            split_ram = False
            
            # Get footprints of the given model
            benchmark_model(optimization=optimization, model_path=model_path, 
                            path_to_stm32ai=path_to_stm32ai, stm32ai_output=stm32ai_output, 
                            stm32ai_version=stm32ai_version, get_model_name_output=get_model_name_output)
            with open(os.path.join(stm32ai_output, 'network_report.json'), 'r') as f:
                report = json.load(f)
            
            needed_rom = report["model_size"] 
            needed_ram = int(report["ram_size"][0])
            
            with open(os.path.join(board.config.memory_pool_path), 'r') as f:
                memory_pool = json.load(f)
                
            available_default_ram = int(next(item for item in memory_pool['memory']['mempools'] if item["name"] == "AXIRAM")["size"]["value"])*10**3
            externalRamSize_inBytes = int(next(item for item in memory_pool['memory']['mempools'] if item["name"] == "SDRAM")["size"]["value"])*10**3
            
            split_ram = available_default_ram < needed_ram

            internalFlashSize_inBytes = int(re.split('(\d+)', board.config.internalFlash_size)[1])*10**3
            externalFlashSize_inBytes = int(re.split('(\d+)', board.config.externalFlash_size)[1])*10**3
            application_size_flash_inBytes = int(re.split('(\d+)', board.config.application_size)[1])*10**3
            if needed_rom > externalFlashSize_inBytes + internalFlashSize_inBytes - application_size_flash_inBytes:
                raise ValueError("\033[31m The Model is too large (too much weights) to fit in the Board. It won't be compiled\033[39m")
            if needed_ram > externalRamSize_inBytes + available_default_ram:
                raise ValueError("\033[31m The Model is too large (too much activations) to fit in the Board. It won't be compiled\033[39m")

            split_weights = needed_rom > (internalFlashSize_inBytes - application_size_flash_inBytes)

            # Add environment variables
            os.environ["STM32_AI_EXE"] = path_to_stm32ai
            
            # Set the tools
            tools = stmaic.STMAiTools()
            session.set_tools(tools)
            print("[INFO] Offline CubeAI used; Selected tools: ", tools, flush=True)

            # Clean up the STM32Cube.AI output directory
            shutil.rmtree(stm32ai_output, ignore_errors=True)
            
            # Set the compiler options
            opt = stmaic.STMAiCompileOptions(allocate_inputs=True, allocate_outputs=True, split_weights=split_weights)
            opt.optimization = optimization
            
            if split_ram:
                print("[INFO]: Dispatch activations in different ram pools to fit the large model")
                # Compile the AI model
                stmaic.compile(session=session, options=opt, target=session._board_config)
            else:
                stmaic.compile(session=session, options=opt)
            
            update_activation_c_code(c_project_path, path_network_c_graph=os.path.join(session.workspace, "network_c_graph.json"), available_AXIRAM=available_default_ram, cfg=cfg)
                    
            if split_weights:
                print("[INFO]: Dispatch weights between internal and external flash to fit the large model")
                
                # @Todo check if fits as well in external and not too large for external as well
                dispatch_weights(internalFlashSizeFlash_KB=board.config.internalFlash_size,
                                 kernelFlash_KB=board.config.lib_size,
                                 applicationSizeFlash_KB=board.config.application_size,
                                 path_network_c_graph=os.path.join(session.workspace, "network_c_graph.json"),
                                 path_network_data_params=os.path.join(session.generated_dir, "network_data_params.c"))
            else:
                print("[INFO]: Weights fit in internal flash")
                
                # @Todo check if fits as well in external and not too large for external as well
                keep_internal_weights(
                                 path_network_data_params=os.path.join(session.generated_dir, "network_data_params.c"))
        

    # Add environment variables
    os.environ["STM32_CUBE_IDE_EXE"] = path_to_cube_ide

    # Set the level of verbosity for the STM32Cube.AI driver
    if debug:
        stmaic.set_log_level('debug')
    elif verbosity is not None:
        stmaic.set_log_level('info')

    # 1 - create a session
    session = stmaic.load(model_path, workspace_dir=output_dir)

    # 2 - set the board configuration
    board_conf = os.path.join(c_project_path, stmaic_conf_filename)
    board = stmaic.STMAiBoardConfig(board_conf)
    session.set_board(board)
    print("[INFO] : Selected board : ", board, flush=True)

    # 3 - compile the model
    user_files = []
    print("[INFO] : Compiling the model and generating optimized C code + Lib/Inc files: ", model_path, flush=True)
    if on_cloud:
        # Connect to STM32Cube.AI Developer Cloud
        login_success, ai, _ = cloud_connect(stm32ai_version=stm32ai_version, credentials=credentials)
        if login_success:
            # Generate the model C code and library
            if not check_large_model:
                
                ai.generate(CliParameters(model=model_path, output=stm32ai_output, fromModel=get_model_name_output,
                        includeLibraryForSerie=CliLibrarySerie(stm32ai_serie.upper()),
                        includeLibraryForIde=CliLibraryIde(stm32ai_ide.lower())))

            else:
                from external_memory_mgt import update_activation_c_code
                split_weights = False
                split_ram = False
                
                # Get footprints of the given model
                results = cloud_analyze(ai=ai, model_path=model_path, optimization=optimization,
                                get_model_name_output=get_model_name_output)
                needed_ram = int(results["ram_size"])
                needed_rom = int(results["rom_size"])

                with open(os.path.join(board.config.memory_pool_path), 'r') as f:
                    memory_pool = json.load(f)
                available_default_ram = int(next(item for item in memory_pool['memory']['mempools'] if item["name"] == "AXIRAM")["size"]["value"])*10**3
                externalRamSize_inBytes = int(next(item for item in memory_pool['memory']['mempools'] if item["name"] == "SDRAM")["size"]["value"])*10**3
                
                split_ram = available_default_ram < needed_ram

                internalFlashSize_inBytes = int(re.split('(\d+)', board.config.internalFlash_size)[1])*10**3
                externalFlashSize_inBytes = int(re.split('(\d+)', board.config.externalFlash_size)[1])*10**3
                application_size_flash_inBytes = int(re.split('(\d+)', board.config.application_size)[1])*10**3
                if needed_rom > externalFlashSize_inBytes + internalFlashSize_inBytes - application_size_flash_inBytes:
                    raise ValueError("\033[31m The Model is too large (too much weights) to fit in the Disco Board. It won't be compiled\033[39m")
                if needed_ram > externalRamSize_inBytes + available_default_ram:
                    raise ValueError("\033[31m The Model is too large (too much activations) to fit in the Disco Board. It won't be compiled\033[39m")

                split_weights = needed_rom > (internalFlashSize_inBytes - application_size_flash_inBytes)

                # memory_pool_path = board.config.memory_pool_path if hasattr(board.config, 'memory_pool_path') in locals() else None
                memory_pool_path = board.config.memory_pool_path if split_ram else None
                    
                ai.generate(CliParameters(model=model_path, output=stm32ai_output, fromModel=get_model_name_output,
                                            includeLibraryForSerie=CliLibrarySerie(stm32ai_serie.upper()),
                                            splitWeights=split_weights, target_info=memory_pool_path,
                                            includeLibraryForIde=CliLibraryIde(stm32ai_ide.lower())))
                # update activations buffers in case it has been modified in former deploy
                update_activation_c_code(c_project_path, path_network_c_graph=os.path.join(stm32ai_output, "network_c_graph.json"), available_AXIRAM=available_default_ram, cfg=cfg)

                if split_weights:
                    # @Todo check if fits as well in external and not too large for external as well
                    dispatch_weights(internalFlashSizeFlash_KB=board.config.internalFlash_size,
                                    kernelFlash_KB=board.config.lib_size,
                                    applicationSizeFlash_KB="10KB",
                                    path_network_c_graph=os.path.join(stm32ai_output, "network_c_graph.json"),
                                    path_network_data_params=os.path.join(stm32ai_output, "network_data_params.c"))
                else:
                    print("[INFO]: Weights fit in internal flash")
                    
                    # @Todo check if fits as well in external and not too large for external as well
                    keep_internal_weights(
                                    path_network_data_params=os.path.join(session.generated_dir, "network_data_params.c"))

            if os.path.exists(stm32ai_output):
                # Move the existing STM32Cube.AI output directory to the output directory
                #os.rename(stm32ai_output,"generated")
                shutil.move(stm32ai_output, os.path.join(output_dir, "generated"))
                stm32ai_output = os.path.join(output_dir, "generated")

                # Check if STM32Cube.AI was used locally to add the Lib/Inc generation
                if not os.listdir(stm32ai_output) or ('Lib' or 'Inc') not in os.listdir(stm32ai_output):
                    stmaic_local_call(session)
        else:
            stmaic_local_call(session)
    else:
        stmaic_local_call(session)

    print("[INFO] : Optimized C code + Lib/Inc files generation done.")

    # 4 - build and flash the STM32 c-project
    print("[INFO] : Building the STM32 c-project..", flush=True)

    user_files.extend([os.path.join(output_dir, "C_header/ai_model_config.h")])
    if additional_files:
        for f in additional_files:
            user_files.extend([os.path.join(output_dir, f)])

    stmaic.build(session, user_files=user_files)