# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import shutil

import stm_ai_driver as stmaic
from hydra.core.hydra_config import HydraConfig


def stm32ai_deploy(cfg, debug=False, additional_files=None, stmaic_conf_filename: str = 'stmaic_c_project.conf'):

    def stmaic_local_call(cfg, session):
        # Add environment variables
        os.environ["STM32_AI_EXE"] = cfg.stm32ai.path_to_stm32ai
        # Set the tools
        tools = stmaic.STMAiTools()
        session.set_tools(tools)
        print("Selected tools : ", tools, flush=True)

        shutil.rmtree(stm32ai_output, ignore_errors=True)
        opt = stmaic.STMAiCompileOptions(allocate_inputs=True, allocate_outputs=True)
        opt.optimization = cfg.stm32ai.optimization

        stmaic.compile(session, opt)

    # Add environment variables
    os.environ["STM32_CUBE_IDE_EXE"] = cfg.stm32ai.path_to_cubeIDE

    # set level of verbosity for stmaic driver
    if debug:
        stmaic.set_log_level('debug')
    elif cfg.stm32ai.verbosity > 0:
        stmaic.set_log_level('info')

    # 1 - create a session
    session = stmaic.load(cfg.model.model_path, workspace_dir=HydraConfig.get().runtime.output_dir)
    stm32ai_output = os.path.join(HydraConfig.get().runtime.output_dir, "stm32ai_files")

    # 2 - set the board configuration
    board_conf = os.path.join(cfg.stm32ai.c_project_path, stmaic_conf_filename)
    board = stmaic.STMAiBoardConfig(board_conf)
    session.set_board(board)
    print("Selected board : ", board, flush=True)

    # 3 - compile the model
    user_files = []
    print("Compiling the model : ", cfg.model.model_path, flush=True)
    if cfg.stm32ai.footprints_on_target:
        if os.path.exists(stm32ai_output):
            shutil.move(stm32ai_output, os.path.join(HydraConfig.get().runtime.output_dir, "generated"))
            stm32ai_output = os.path.join(HydraConfig.get().runtime.output_dir, "generated")

            # Checking if STM32Cube.AI was used locally to add the Lib/Inc generation
            if not os.listdir(stm32ai_output) or ('Lib' or 'Inc') not in os.listdir(stm32ai_output):
                stmaic_local_call(cfg, session)
        else:
            stmaic_local_call(cfg, session)
    else:
        stmaic_local_call(cfg, session)

    # 4 - build and flash the STM32 c-project
    print("Building the STM32 c-project..", flush=True)

    user_files.extend([os.path.join(HydraConfig.get().runtime.output_dir, "C_header/ai_model_config.h")])
    if additional_files:
        for f in additional_files:
            user_files.extend([os.path.join(HydraConfig.get().runtime.output_dir, f)])
            
    stmaic.build(session, user_files=user_files)

    print('done')
