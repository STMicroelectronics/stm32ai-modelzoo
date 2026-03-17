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
import subprocess
import platform
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
import tensorflow as tf
import shutil
from typing import Optional
from pathlib import Path

import common.stm32ai_local as stmaic
from common.benchmarking import cloud_connect, cloud_analyze, benchmark_model
from common.stm32ai_dc import (CliLibraryIde, CliLibrarySerie, CliParameters)
from .external_memory_mgt import update_activation_c_code

import json
import re
from typing import Dict, List

def check_submodule(c_project_path: str):
    """
    Check if the project submodule is initialized in the C project path.

    Args:
        c_project_path (str): Path to the  C project.
    """
    BOLD_YELLOW = "\033[1;33m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"
    from git import Repo, InvalidGitRepositoryError

    # Get absolute path of the current script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Initialize the git repo by searching parent directories from the script directory
    try:
        repo = Repo(script_dir, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise InvalidGitRepositoryError(f"No git repository found from path {script_dir}")

    submodule_path = c_project_path.lstrip('./').rstrip("./")

    # Find the submodule object by path
    submodule = None
    for sm in repo.submodules:
        print(sm.path)
        if sm.path == submodule_path:
            submodule = sm
            break

    if submodule is None:
        raise ValueError(f"Submodule '{submodule_path}' not found.")

    # Check if submodule is initialized by trying to get its repo
    try:
        sub_repo = submodule.module()
        initialized = True
    except InvalidGitRepositoryError:
        print(f"{RESET}{BOLD_RED}[ERROR]:{RESET} Submodule '{submodule_path}' is not initialized. Please run 'git submodule update --init {submodule_path}'.")
        initialized = False
        sub_repo = None
        return False

    if initialized:
        # Commit recorded in main repo
        main_commit = submodule.hexsha

        # Current commit in submodule repo
        current_commit = sub_repo.head.commit.hexsha
        if main_commit != current_commit:
            print(f"{RESET}{BOLD_RED}[ERROR]:{RESET} Submodule '{submodule_path}' is not at the expected commit.")
            print(f"         Main repo expects commit {main_commit} but submodule is at commit {current_commit}.")
            print(f"         Please run 'git submodule update --init {submodule_path}' to sync the submodule.")
            return False
        if sub_repo.is_dirty(untracked_files=True):
            print(f"{RESET}{BOLD_YELLOW}[WARNING]:{RESET} Submodule '{submodule_path}' has uncommitted changes. Please commit or stash them.")
            return True
    return True

def _keep_internal_weights(path_network_data_params: str):
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


def _dispatch_weights(internalFlashSizeFlash_KB: str,
                     kernelFlash_KB: str,
                     applicationSizeFlash_KB: str,
                     path_network_c_info: str,
                     path_network_data_params: str):

    with open(os.path.join(path_network_c_info), 'r') as f:
        graph = json.load(f)

    # Remove non-flash elements
    for i in range(len(graph["memory_pools"])-1,0,-1):
        element = graph["memory_pools"][i]
        if element["rights"] != "ACC_READ":
            graph["memory_pools"].remove(element)

    # Sort weights from large weights to small ones
    sorted_weights = sorted(graph["memory_pools"], key=lambda item: item['used_size_bytes'], reverse=True)

    internalFlashSize_inBytes = int(re.split('(\d+)', internalFlashSizeFlash_KB)[1])*10**3
    kernel_flash_inBytes = int(re.split('(\d+)', kernelFlash_KB)[1])*10**3
    application_size_flash_inBytes = int(re.split('(\d+)', applicationSizeFlash_KB)[1])*10**3

    freeInternalFlashSize =  internalFlashSize_inBytes - kernel_flash_inBytes - application_size_flash_inBytes
    ExternalWeightArray = []
    InternalWeightArray = []
    for detail in sorted_weights:
        if (freeInternalFlashSize - detail["used_size_bytes"]) > 0:
            bytes_number = detail["used_size_bytes"]
            # Can fit in Internal Flash
            InternalWeightArray.append(detail["name"])
            # We fit the weights, reduce free size accordingly
            freeInternalFlashSize = freeInternalFlashSize - bytes_number
        else:
            # No free space in Internal Flash
            ExternalWeightArray.append(detail["name"])

    with open(path_network_data_params,'r') as f1,\
        open(os.path.join(os.path.dirname(path_network_data_params), 'network_data_params_modify.c'),'w') as f2:
        for lineNumber, line in enumerate(f1):
            if line == '#include "network_data_params.h"\n':
                line = '#define AI_EXTERNAL_FLASH    __attribute__((section(".ExternalFlashSection")))\n\
#define AI_INTERNAL_FLASH    __attribute__((section(".InternalFlashSection")))\n' + line
        # @Todo maybe remove tuple to test
            weight = re.findall("const ai_u(?:\d+) \D_network_(.*)_\D(?:\d+)\[(?:\d+)\]", line)
            if weight != []:
                if weight[0] in InternalWeightArray:
                    line = 'AI_INTERNAL_FLASH\n' + line
                elif weight[0] in ExternalWeightArray:
                    line = 'AI_EXTERNAL_FLASH\n' + line
            f2.write(line)
    os.replace(os.path.join(os.path.dirname(path_network_data_params), 'network_data_params_modify.c'), path_network_data_params)


def stm32ai_deploy(target: bool = False,
                   stlink_serial_number: str = None,
                   stedgeai_core_version: str = None,
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
                   cfg = None,
                   custom_objects: Dict = None) -> None:
    """
    Deploy an STM32 AI model to a target device.

    Args:
        target (bool): Whether to generate the STM32Cube.AI library and header files on the target device. Defaults to False.
        stedgeai_core_version (str): Version of the STEdgeAI Core to use.
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

    def _stmaic_local_call(session):
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
            print("[INFO] : Offline CubeAI used; Selected tools: ", tools, flush=True)

            # Clean up the STM32Cube.AI output directory
            shutil.rmtree(stm32ai_output, ignore_errors=True)
            # Set the compiler options
            opt = stmaic.STMAiCompileOptions(no_inputs_allocation=False, no_outputs_allocation=False)
            opt.optimization = optimization

            # Compile the AI model
            stmaic.compile(session, opt)

        else:
            split_weights =  False
            split_ram = False

            # Get footprints of the given model
            benchmark_model(optimization=optimization, model_path=model_path,
                            path_to_stm32ai=path_to_stm32ai, stm32ai_output=stm32ai_output,
                            stedgeai_core_version=stedgeai_core_version, get_model_name_output=get_model_name_output)
            with open(os.path.join(stm32ai_output, 'network_c_info.json'), 'r') as f:
                report = json.load(f)

            needed_rom = report["memory_footprint"]["weights"]
            needed_ram = report["memory_footprint"]["activations"]

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
            print("[INFO] : Offline CubeAI used; Selected tools: ", tools, flush=True)

            # Clean up the STM32Cube.AI output directory
            shutil.rmtree(stm32ai_output, ignore_errors=True)

            # Set the compiler options
            opt = stmaic.STMAiCompileOptions(no_inputs_allocation=False, no_outputs_allocation=False, split_weights=split_weights)
            opt.optimization = optimization

            if split_ram:
                print("[INFO] : Dispatch activations in different ram pools to fit the large model")
                # Compile the AI model
                stmaic.compile(session=session, options=opt, target=session._board_config)
            else:
                stmaic.compile(session=session, options=opt)

            path_network_c_info = os.path.join(session.workspace, "network_c_info.json")

            update_activation_c_code(c_project_path, model_path=model_path, path_network_c_info=path_network_c_info, available_AXIRAM=available_default_ram, aspect_ratio=aspect_ratio, custom_objects=custom_objects)

            if split_weights:
                print("[INFO] : Dispatch weights between internal and external flash to fit the large model")

                # @Todo check if fits as well in external and not too large for external as well
                _dispatch_weights(internalFlashSizeFlash_KB=board.config.internalFlash_size,
                                 kernelFlash_KB=board.config.lib_size,
                                 applicationSizeFlash_KB=board.config.application_size,
                                 path_network_c_info=path_network_c_info,
                                 path_network_data_params=os.path.join(session.generated_dir, "network_data.c"))
            else:
                print("[INFO] : Weights fit in internal flash")

                # @Todo check if fits as well in external and not too large for external as well
                _keep_internal_weights(
                                 path_network_data_params=os.path.join(session.generated_dir, "network_data.c"))


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
    # Wrap the following in a try/except block for use cases which either don't pass cfg as argument
    # Or UCs which don't have a preprocessing.resizing.aspect_ratio in config.
    # Temporary band-aid fix
    try:
        aspect_ratio=cfg.preprocessing.resizing.aspect_ratio
    except:
        pass
    print("[INFO] : Compiling the model and generating optimized C code + Lib/Inc files: ", model_path, flush=True)
    if on_cloud:
        # Connect to STM32Cube.AI Developer Cloud
        login_success, ai, _ = cloud_connect(stedgeai_core_version=stedgeai_core_version, credentials=credentials)
        if login_success:
            # Generate the model C code and library
            if not check_large_model:

                ai.generate(CliParameters(model=model_path, output=stm32ai_output, fromModel=get_model_name_output,
                        includeLibraryForSerie=CliLibrarySerie(stm32ai_serie.upper()),
                        includeLibraryForIde=CliLibraryIde(stm32ai_ide.lower())))

            else:
                split_weights = False
                split_ram = False

                # Get footprints of the given model
                results = cloud_analyze(ai=ai, model_path=model_path, optimization=optimization,
                                get_model_name_output=get_model_name_output)
                needed_ram = int(results["activations_size"])
                needed_rom = int(results["weights"])

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

                path_network_c_info = os.path.join(session.generated_dir, "network_c_info.json")

                # update activations buffers in case it has been modified in former deploy
                update_activation_c_code(c_project_path, model_path=model_path, path_network_c_info=path_network_c_info, available_AXIRAM=available_default_ram, aspect_ratio=aspect_ratio, custom_objects=custom_objects)

                if split_weights:
                    # @Todo check if fits as well in external and not too large for external as well
                    _dispatch_weights(internalFlashSizeFlash_KB=board.config.internalFlash_size,
                                    kernelFlash_KB=board.config.lib_size,
                                    applicationSizeFlash_KB="10KB",
                                    path_network_c_info=path_network_c_info,
                                    path_network_data_params=os.path.join(stm32ai_output, "network_data.c"))
                else:
                    print("[INFO] : Weights fit in internal flash")

                    # @Todo check if fits as well in external and not too large for external as well
                    _keep_internal_weights(
                                    path_network_data_params=os.path.join(session.generated_dir, "network_data.c"))

            if os.path.exists(stm32ai_output):
                # Move the existing STM32Cube.AI output directory to the output directory
                #os.rename(stm32ai_output,"generated")
                if not stm32ai_output.lower() == os.path.join(output_dir, "generated").lower():
                    shutil.move(stm32ai_output, os.path.join(output_dir, "generated"))
                    stm32ai_output = os.path.join(output_dir, "generated")

                # Check if STM32Cube.AI was used locally to add the Lib/Inc generation
                if not os.listdir(stm32ai_output) or ('Lib' or 'Inc') not in os.listdir(stm32ai_output):
                    _stmaic_local_call(session)
        else:
            _stmaic_local_call(session)
    else:
        _stmaic_local_call(session)

    print("[INFO] : Optimized C code + Lib/Inc files generation done.")

    # 4 - build and flash the STM32 c-project
    print("[INFO] : Building the STM32 c-project..", flush=True)

    user_files.extend([os.path.join(output_dir, "C_header/ai_model_config.h")])
    if additional_files:
        for f in additional_files:
            user_files.extend([os.path.join(output_dir, f)])

    stmaic.build(session, user_files=user_files, serial_number=stlink_serial_number)

def stm32ai_deploy_stm32n6(target: bool = False,
                   stlink_serial_number: str = None,
                   stedgeai_core_version: str = None,
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
                   build_conf: str = None,
                   cfg = None,
                   custom_objects: Dict = None,
                   input_data_type: str = '',
                   output_data_type: str = '',
                   inputs_ch_position: str = '',
                   outputs_ch_position: str = '',
                   name: str = 'network',
                   no_inputs_allocation: bool = False,
                   no_outputs_allocation: bool = False) -> None:
    """
    Deploy an STM32 AI model to a target device.

    Args:
        target (bool): Whether to generate the STM32Cube.AI library and header files on the target device. Defaults to False.
        c_project_path (str): Path to the STM32CubeIDE C project.
        verbosity (int, optional): Level of verbosity for the STM32Cube.AI driver. Defaults to None.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.
        model_path (str, optional): Path to the AI model file. Defaults to None.
        on_cloud(bool): whether to deploy using the cloud. Defaults to False
        config(list):

    Returns:
        split_weights (bool): return true if the weights has been splitted; False otherwise
    """
    def _stmaic_local_call(session):
        """
        Compile the AI model using the STM32Cube.AI compiler.

        Args:
            session (stmaic.STMAiSession): The STM32Cube.AI session object.

        Returns:
            None
        """
        # Add environment variables
        os.environ["STM32_AI_EXE"] = path_to_stm32ai
        # Set the tools
        tools = stmaic.STMAiTools()
        session.set_tools(tools)
        print("[INFO] : Offline CubeAI used; Selected tools: ", tools, flush=True)

        # Clean up the STM32Cube.AI output directory
        shutil.rmtree(stm32ai_output, ignore_errors=True)

        # Set the compiler options
        neural_art_path = session._board_config.config.profile + "@" + session._board_config.config.neuralart_user_path
        opt = stmaic.STMAiCompileOptions(st_neural_art=neural_art_path, input_data_type=input_data_type, inputs_ch_position=inputs_ch_position,
                                         output_data_type = output_data_type, outputs_ch_position = outputs_ch_position,
                                         name=name, no_outputs_allocation=no_outputs_allocation, no_inputs_allocation=no_inputs_allocation)

        # 2 - set the board configuration
        board_conf = os.path.join(c_project_path, stmaic_conf_filename)
        board = stmaic.STMAiBoardConfig(board_conf, build_conf)
        session.set_board(board)

        # Compile the AI model
        stmaic.compile(session=session, options=opt, target=session._board_config)

     # Add environment variables
    os.environ["STM32_CUBE_IDE_EXE"] = path_to_cube_ide

    # Set the level of verbosity for the STM32Cube.AI driver
    if debug:
        stmaic.set_log_level('debug')
    elif verbosity is not None:
        stmaic.set_log_level('info')

    ret = check_submodule(c_project_path)
    if not ret:
        sys.exit(1)

    # 1 - create a session
    session = stmaic.load(model_path, workspace_dir=output_dir)

    # 2 - set the board configuration
    board_conf = os.path.join(c_project_path, stmaic_conf_filename)
    board = stmaic.STMAiBoardConfig(board_conf, build_conf)
    session.set_board(board)
    print("[INFO] : Selected board : ", board, flush=True)
    # 3 - compile the model
    user_files = []
    print("[INFO] : Compiling the model and generating optimized C code + Lib/Inc files: ", model_path, flush=True)

    if on_cloud:
        # Connect to STM32Cube.AI Developer Cloud
        login_success, ai, _ = cloud_connect(stedgeai_core_version=stedgeai_core_version, credentials=credentials)

        if login_success:

            with open(session._board_config.config.neuralart_user_path) as file:
                neuralart_options = json.load(file)
            neuralart_options = neuralart_options['Profiles']['default']["options"].replace('--', "--atonnOptions.")

            # Generate the model C code and library
            ai.generate(CliParameters(model=model_path, output=stm32ai_output, fromModel=get_model_name_output, target="stm32n6", stNeuralArt="default",
                                    allocateInputs=False, allocateOutputs=False, mpool=board._conf.mpool, extraCommandLineArguments=neuralart_options,
                                    includeLibraryForSerie=CliLibrarySerie(stm32ai_serie.upper()),
                                    includeLibraryForIde=CliLibraryIde(stm32ai_ide.lower())))

            if os.path.exists(stm32ai_output):
                # Move the existing STM32Cube.AI output directory to the output directory
                #os.rename(stm32ai_output,"generated")
                if stm32ai_output != os.path.join(output_dir, "generated"):
                    shutil.move(stm32ai_output, os.path.join(output_dir, "generated"))
                stm32ai_output = os.path.join(output_dir, "generated")

                # Check if STM32Cube.AI was used locally to add the Lib/Inc generation
                if not os.listdir(stm32ai_output) or ('Lib' or 'Inc') not in os.listdir(stm32ai_output):
                    _stmaic_local_call(session)
        else:
            _stmaic_local_call(session)
    else:
        _stmaic_local_call(session)

    print("[INFO] : Optimized C code + Lib/Inc files generation done.")

    # 4 - build and flash the STM32 c-project
    print("[INFO] : Building the STM32 c-project..", flush=True)

    user_files.extend([os.path.join(output_dir, "C_header/app_config.h")])
    user_files.extend([os.path.join(output_dir, "C_header/ai_model_config.h")])
    if additional_files:
        for f in additional_files:
            user_files.extend([os.path.join(output_dir, f)])

    stmaic.build(session, user_files=user_files, serial_number=stlink_serial_number)


def stm32ai_deploy_mpu(target: bool = False,
                   board_ip_address: str = None,
                   board_deploy: str = None,
                   class_names: List = None,
                   c_project_path: str = None,
                   verbosity: int = None,
                   debug: bool = False,
                   model_path: str = None,
                   cfg = None) -> None:
    """
    Deploy an STM32 AI model to a target device.

    Args:
        target (bool): Whether to generate the STM32Cube.AI library and header files on the target device. Defaults to False.
        c_project_path (str): Path to the STM32CubeIDE C project.
        verbosity (int, optional): Level of verbosity for the STM32Cube.AI driver. Defaults to None.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.
        model_path (str, optional): Path to the AI model file. Defaults to None.
        on_cloud(bool): whether to deploy using the cloud. Defaults to False
        config(list):

    Returns:
        split_weights (bool): return true if the weights has been splitted; False otherwise
    """

    #verify if a board IP address provided
    if board_ip_address is None:
        print("Board IP address is missing, unable to deploy on target")
        return False

    #verify if the board IP address is reachable
    count = 5
    timeout = 100
    subprocess_timeout = 5
    count_params = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_params = '-w' if platform.system().lower() == 'windows' else '-W'
    model_extension = "tflite"

    cmd =  ['ping', count_params, str(count), timeout_params, str(timeout), board_ip_address]
    try:
        # Execute the command
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, text=True)
        # Check the return code to determine if ping was successful
        if res.returncode == 0:
            print(f"[INFO] : Board is reachable at {board_ip_address} address")
        else:
            print(f"[FAIL] : Board is not reachable at {board_ip_address} address")
            return False
    except subprocess.TimeoutExpired:
        print(f"[FAIL] : Board is not reachable, ping command timed out after {subprocess_timeout} seconds.")
        return False
    except Exception as e:
        print(f"[FAIL] : Verification of the IP failed : {e}.")
        return False

    #deploy application on the board

    # create the deploy directory on target if not already existing
    command = "mkdir -p " + board_deploy
    ssh = subprocess.run("ssh -o \"StrictHostKeyChecking no\" root@"+board_ip_address+" \""+command+"\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    if ssh.returncode != 0:
        print(f"[FAIL] deploy directory creation failed, code: {ssh.returncode}")
        return False

    # Populate the deploy directory with application code
    path_to_application = c_project_path + "Application/"
    path_to_resources = c_project_path + "Resources/"

    # create the class names txt if not already existing
    label_file = os.path.join(path_to_resources, 'class_names.txt')
    if isinstance(class_names, list) and all(isinstance(name, str) for name in class_names):
        with open(label_file, 'w') as file:
            for class_name in class_names:
                file.write(class_name + '\n')
    elif isinstance(class_names, str) and class_names.endswith('.txt'):
        shutil.copy(class_names, label_file)

    command = "scp -r " + path_to_application + " " + path_to_resources + " " + model_path + " root@" + board_ip_address + ":" + board_deploy
    deploy_res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)

    if deploy_res.returncode == 0 :
        print(f"[INFO] : Application code successfully installed on target")
    else:
        print(f"[FAIL] : Application code deployment failed : {deploy_res.stderr} ")
        return False

    #send target specific resources
    if "STM32MP2" in target:
        path_to_target_resources = c_project_path + "/STM32MP2/*.sh"
        model_extension = "nbg"
    else:
        path_to_target_resources = c_project_path + "/STM32MP1/*.sh"
        model_extension = "tflite"

    command = "scp -r -p " + path_to_target_resources + " root@" + board_ip_address + ":" + board_deploy + "/Resources"
    deploy_spe_res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)

    if deploy_spe_res.returncode != 0:
        print(f"[FAIL] : Application code deployment failed : {deploy_spe_res.stderr} ")
        return False

    # Define remote paths
    remote_application_path = os.path.join(board_deploy, "Application")
    remote_resources_path = os.path.join(board_deploy, "Resources")

    # Command to chmod +x all .sh files in Application folder
    chmod_application_cmd = f"chmod +x {remote_application_path}/*.sh"
    ssh_chmod_app = subprocess.run(
        f"ssh -o \"StrictHostKeyChecking no\" root@{board_ip_address} \"{chmod_application_cmd}\"",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60
    )
    if ssh_chmod_app.returncode != 0:
        print(f"[WARN] : chmod +x on Application/*.sh failed: {ssh_chmod_app.stderr.decode().strip()}")

    # Command to chmod +x all .sh files in Resources folder
    chmod_resources_cmd = f"chmod +x {remote_resources_path}/*.sh"
    ssh_chmod_res = subprocess.run(
        f"ssh -o \"StrictHostKeyChecking no\" root@{board_ip_address} \"{chmod_resources_cmd}\"",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60
    )
    if ssh_chmod_res.returncode != 0:
        print(f"[WARN] : chmod +x on Resources/*.sh failed: {ssh_chmod_res.stderr.decode().strip()}")

    # Find the application launch script name
    script_extension = ".sh"
    file_names = []
    for item in os.listdir(path_to_application):
        if Path(item).suffix == script_extension:
            file_names.append(os.path.basename(item))

    launch_script = None
    for file_name in file_names:
        if "launch_" in file_name:
            launch_script = file_name
            break

    if launch_script is None:
        print("[FAIL] : Launch script not found in Application folder")
        return False

    #launch the application
    command = board_deploy + "/Application/" + launch_script  + " " + model_extension + " "  + board_deploy
    print(f"[INFO] : To launch application directly on the target please run : {command}")
    command = "ssh -o \"StrictHostKeyChecking no\" root@"+board_ip_address+" \""+command+"\""
    print(f"[INFO] : To launch application from your host computer please run : {command}")

    return True