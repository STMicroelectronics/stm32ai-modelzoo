###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - Fake STM32 app
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import glob
import os
import shutil
from typing import Optional


from common.stm32ai_local.session import STMAiSession
from common.stm32ai_local.utils import run_shell_cmd, _LOGGER_NAME_
from common.stm32ai_local.stm_ai_tools import STMAiTools


logger = logging.getLogger(_LOGGER_NAME_)


def _get_compile_options(session: STMAiSession, tools: STMAiTools, ld_script: str, series: Optional[str] = None):

    c_flags_core = tools.ai_runtime_compiler_options(series) + ' '
    #  -std=gnu11 -Os
    c_flags = c_flags_core + "-Wall -fdata-sections -ffunction-sections -fstack-usage --specs=nano.specs -Og"

    ld_flags = f'-T{ld_script} {c_flags_core} -Wl,-Map={session.c_name}.map,--cref -Wl,--gc-sections -static '
    ld_flags += '-specs=nosys.specs -specs=nano.specs '
    ld_flags += '-Wl,--start-group -lm -Wl,--end-group -Wl,--print-memory-usage -Wl,-no-enum-size-warning '
    ld_flags += f'-o {session.c_name}.elf'

    return {'c_flags': c_flags, 'ld_flags': ld_flags}


def _compile_c(arm_non_eabi_gcc, c_file: str, c_flags, inc_dir, build_dir):

    cmd_line = arm_non_eabi_gcc + ' '
    cmd_line += c_flags + ' '
    cmd_line += ''.join([' -I{} '.format(v) for v in inc_dir])
    cmd_line += f'-c {c_file} '
    err, _ = run_shell_cmd(cmd_line, cwd=build_dir, logger=logger)

    return err


def _link(arm_non_eabi_gcc, o_files, ld_flags, build_dir):

    cmd_line = arm_non_eabi_gcc + ' '
    cmd_line += ld_flags + ' '
    cmd_line += ''.join([' {} '.format(v) for v in o_files])
    err, _ = run_shell_cmd(cmd_line, cwd=build_dir, logger=logger)

    return err


def stm32app_build(
        session: STMAiSession,
        arm_none_eabi_gcc: Optional[str] = None
):
    """Build the stma32 application"""

    tools = session.tools
    series = session.series
    series = series if (series or series == 'default') else 'stm32h7'

    arm_none_eabi_gcc = arm_none_eabi_gcc if arm_none_eabi_gcc else 'arm-none-eabi-gcc'

    # retrieve the c_files to be compiled
    c_files = glob.glob(os.path.join(os.path.dirname(__file__), 'resources', 'stm32_app', '*.[cs]'))
    c_files.extend(glob.glob(os.path.join(session.generated_dir, '*.c')))

    tpl_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources', 'templates', 'stm32_app_main.c'))
    ld_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources', 'stm32_app', 'stm32xx_2_16M.ld'))

    build_dir = session.build_dir
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    tpl_dst = os.path.join(build_dir, 'stm32_app_main.c')
    # session.render(tpl_file, tpl_dst)
    c_files.extend([tpl_dst])

    inc_dir = [os.path.abspath(session.generated_dir), tools.ai_runtime_inc()]

    options = _get_compile_options(session, tools, ld_script, series)
    for c_file in c_files:
        _compile_c(arm_none_eabi_gcc, os.path.abspath(c_file), options['c_flags'], inc_dir, build_dir)

    o_files = glob.glob(os.path.join(session.build_dir, '*.o'))
    o_files = [os.path.basename(f_) for f_ in o_files]
    o_files.extend([tools.ai_runtime_lib(series=series)])
    _link(arm_none_eabi_gcc, o_files, options['ld_flags'], build_dir)

    return os.path.join(build_dir, f'{session.c_name}.map')
