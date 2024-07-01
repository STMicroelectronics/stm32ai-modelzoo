###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - "run" service
"""

import sys
import logging
import time

from typing import Optional, List, Union, Any, Tuple
from statistics import mean

from .session import STMAiSession
from .stm_ai_tools import STMAiTools
from .stm32_tools import get_stm32_board_interfaces, STM32_TOOLS, reset_stm32_board
from .utils import _LOGGER_NAME_


logger = logging.getLogger(_LOGGER_NAME_)


def cmd_run(
        session: STMAiSession,
        desc: str,
        inputs: Optional[Union[List, Any]] = None) -> Tuple[List, float, str]:
    """Run command"""

    exec_error = [], 0.0, 'NOT EXECUTED'  # type: Tuple[List, float, str]
    if not session.tools:
        session.set_tools(STMAiTools(version=session.stm_ai_version))
        logger.warning(f'setting the STM.AI tool: {session.tools}')

    logger.info(f'running model.. desc="{desc}"')

    # set PYTHONPATH if requested to load the ai_runner module
    #  from the X-CUBE-AI pack
    python_path_ext = session.tools.python_path()
    if python_path_ext:
        sys.path.insert(0, python_path_ext)

    from stm_ai_runner import AiRunner
    from stm_ai_runner import __version__ as ai_runner_version

    logger.info(f' AiRunner v{ai_runner_version}')

    ai_runner = AiRunner(logger=logger)

    if (not desc or 'serial' in desc.lower()) and STM32_TOOLS.get_cube_programmer():
        _, uarts = get_stm32_board_interfaces()
        com_ports = [uart['port'] for uart in uarts]
        if not com_ports:
            logger.warning('board execution is SKIPPED!')
            logger.warning(' -> no serial communication port is available!')
            return exec_error
        reset_stm32_board()
        time.sleep(2)

    ai_runner.connect(desc)

    if not ai_runner.is_connected:
        logger.error('Connection has failed (NO aiValidation FW or COM port is already used)..')
        return exec_error

    # display the network/run-time information
    ai_runner.summary(print_fn=logger.debug)

    mode = AiRunner.Mode.IO_ONLY
    if inputs is None:
        if int(ai_runner_version.split('.')[0]) > 2:
            mode |= AiRunner.Mode.PERF_ONLY
        inputs = ai_runner.generate_rnd_inputs(batch_size=2)

    outputs, profile = ai_runner.invoke(inputs, mode=mode)

    ai_runner.disconnect()

    if python_path_ext:
        sys.path.pop(0)

    desc = profile['info']['device']['desc']

    latency = mean(profile['c_durations'])
    session.set_latency(latency)

    return outputs, latency, desc
