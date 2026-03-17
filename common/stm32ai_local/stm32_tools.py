###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - STM32 tools (helpers)
"""

import logging
import shutil
import os
import sys
from pathlib import Path
from typing import Union, Tuple, List

from .utils import _LOGGER_NAME_, STMAIC_DEBUG_ENV, run_shell_cmd

logger = logging.getLogger(_LOGGER_NAME_)


def _get_app(exec_name: str, env_var: str) -> Union[Tuple[str, Path, str], None]:
    """Return name, filepath and src type of the executable"""

    # Env variable is used in priority
    app_env = Path(os.environ.get(env_var, ''))
    if app_env:
        # check if valid
        path = str(app_env.parent)
        file_app_ = shutil.which(app_env.name, path=path)
        if file_app_:
            return app_env.stem, app_env.parent, 'env'

    # Check if available in the PATH
    file_app_path = shutil.which(exec_name)
    if file_app_path:
        app_path = Path(file_app_path)
        return app_path.stem, app_path.parent, 'path'

    return None


class STM32Tools:
    """Object to handle the STM32 tools (singleton object)"""

    CUBE_IDE = 'stm32cubeidec'
    MAKE = 'make'
    MAKE_ALT = 'mingw32-make'
    GCC_COMPILER = 'arm-none-eabi-gcc'
    CUBE_PROGRAMMER = 'STM32_Programmer_CLI'
    CUBE_SIGNING_TOOL = 'STM32_SigningTool_CLI'

    def __init__(self):
        """Detect the STM32 tools"""

        self._cube_ide_drv = _get_app(STM32Tools.CUBE_IDE, 'STM32_CUBE_IDE_EXE')
        self._gcc_compiler = _get_app(STM32Tools.GCC_COMPILER, 'STM32_ARM_GCC_COMPILER_EXE')
        self._make = _get_app(STM32Tools.MAKE, 'STM32_MAKE_EXE')
        if not self._make:
            self._make = _get_app(STM32Tools.MAKE_ALT, '')
        self._cube_prg = _get_app(STM32Tools.CUBE_PROGRAMMER, 'STM32_CUBE_PROG_EXE')
        self._signing_tool = _get_app(STM32Tools.CUBE_SIGNING_TOOL, 'STM32_SIGNINGTOOL_CLI')
        self._platform = sys.platform

        if self._cube_ide_drv:
            ide = self._cube_ide_drv[1] / self._cube_ide_drv[0]
            self.refresh(ide)

    def __call__(self):
        """."""
        return self

    def _second_chance(self):
        """Second/last chance to retreive the STM32CubeIDE driver"""
        if self._cube_ide_drv:
            return
        logger.debug('retrieving STM32CubeIDE driver.. (second chance)')
        self._cube_ide_drv = _get_app(STM32Tools.CUBE_IDE, 'STM32_CUBE_IDE_EXE')
        if self._cube_ide_drv:
            ide = self._cube_ide_drv[1] / self._cube_ide_drv[0]
            self.refresh(ide)

    def refresh(self, cube_ide_exe: Union[Path, str]):
        """Update the application detection"""

        if not self._cube_ide_drv and cube_ide_exe:
            cube_ide_exe = Path(cube_ide_exe)
            path = str(cube_ide_exe.parent)
            file_app = shutil.which(cube_ide_exe.name, path=path)
            if file_app:
                app = Path(file_app)
                self._cube_ide_drv = app.stem, app.parent, 'args'

        if self._cube_ide_drv and not self._gcc_compiler:
            self._gcc_compiler = self._from_cube_ide(
                STM32Tools.GCC_COMPILER,
                pattern='com.st.stm32cube.ide.mcu.externaltools.gnu-tools*'
            )

        if self._cube_ide_drv and not self._make:
            self._make = self._from_cube_ide(
                STM32Tools.MAKE,
                pattern='com.st.stm32cube.ide.mcu.externaltools.make*'
            )

        if self._cube_ide_drv and not self._cube_prg:
            self._cube_prg = self._from_cube_ide(
                STM32Tools.CUBE_PROGRAMMER,
                pattern='com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer*'
            )

        if self._cube_ide_drv and not self._signing_tool:
            self._signing_tool = self._from_cube_ide(
                STM32Tools.CUBE_SIGNING_TOOL,
                pattern='com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer*'
            )

        # Update PATH
        for value in self.todict().values():
            if value and 'path' not in value[2]:
                # print('add path {}'.format(str(value[1])))
                os.environ["PATH"] = str(value[1]) + os.pathsep + os.environ["PATH"]

    def get_cube_ide(self):
        """Return CUBE IDE driver information"""
        self._second_chance()
        return self._cube_ide_drv

    def get_cube_programmer(self):
        """Return CUBE Programmer information"""
        self._second_chance()
        return self._cube_prg

    def get_cube_signing_tool(self):
        """Return CUBE Signing tool information"""
        self._second_chance()
        return self._signing_tool

    def get_compiler(self):
        """Return ARM compiler information"""
        self._second_chance()
        return self._gcc_compiler

    def get_make(self):
        """Return make app information"""
        self._second_chance()
        return self._make

    def _from_cube_ide(self, exec_name: str, pattern: str) -> Union[Tuple[str, Path, str], None]:
        """Retrieve the executable from the STM32 Cube IDE installation"""

        cube_ide = self._cube_ide_drv
        if not cube_ide:
            return None

        cdts = sorted(Path(os.path.join(cube_ide[1], 'plugins')).glob(pattern), reverse=True)
        cdts = [cdt for cdt in cdts if cdt.is_dir()]
        if cdts:
            exec_path = cdts[0] / 'tools' / 'bin'
            return (exec_name, exec_path, 'cube-ide')

        return None

    def todict(self):
        """Return a dict with the detected STM32 tools"""

        res = {}
        res[STM32Tools.CUBE_IDE] = self._cube_ide_drv
        res[STM32Tools.MAKE] = self._make
        res[STM32Tools.GCC_COMPILER] = self._gcc_compiler
        res[STM32Tools.CUBE_PROGRAMMER] = self._cube_prg
        res[STM32Tools.CUBE_SIGNING_TOOL] = self._signing_tool

        return res

    def check(self):
        """Check that the STM32 tools are available"""

        self._second_chance()

        if self._make:
            my_env = None  # os.environ.copy()
            # my_env["PATH"] = str(self._make[1]) + os.pathsep + my_env["PATH"]
            run_shell_cmd([str(self._make[0]), '--version'], env=my_env, logger=logger)

        if self._gcc_compiler:
            my_env = None  # os.environ.copy()
            # my_env["PATH"] = str(self._gcc_compiler[1]) + os.pathsep + my_env["PATH"]
            run_shell_cmd([str(self._gcc_compiler[0]), '--version'], env=my_env, logger=logger)

        if self._cube_prg:
            my_env = None  # os.environ.copy()
            # my_env["PATH"] = str(self._cube_prg[1]) + os.pathsep + my_env["PATH"]
            run_shell_cmd([str(self._cube_prg[0]), '--version'], env=my_env, logger=logger)

        if self._signing_tool:
            my_env = None  # os.environ.copy()
            # my_env["PATH"] = str(self._cube_prg[1]) + os.pathsep + my_env["PATH"]
            run_shell_cmd([str(self._signing_tool[0]), '--version'], env=my_env, logger=logger)

        if self._cube_ide_drv:
            cmd = [str(self._cube_ide_drv[0]), '-nosplash',
                   '-application org.eclipse.cdt.managedbuilder.core.headlessbuild',
                   '--help']
            run_shell_cmd(cmd, logger=logger)


STM32_TOOLS = STM32Tools()


class STM32ProgListCommandParser():
    """Parser for STM32CubeProgrammer --list option"""

    def __init__(self):
        self._st_link = None
        self._uart = None
        self._st_links = []
        self._uarts = []
        self._no_st_link_detected = False

    def no_st_link_detected(self):
        """Indicates if no st-link has been detected normaly"""
        return self._no_st_link_detected

    def st_links(self):
        """List of connected board through ST-link"""
        return self._st_links

    def uarts(self):
        """List of connected board through Uart VCP"""
        return self._uarts

    def __call__(self, line):
        """Parse a line"""
        if not isinstance(line, str):
            return
        if 'STLink Interface' in line:
            self._st_link = dict()
            # logger.debug('Found {}'.format(line))
            return
        if self._st_link is not None and 'ST-LINK SN' in line:
            self._st_link['sn'] = line.split()[-1]
            return
        if self._st_link is not None and 'ST-LINK FW' in line:
            self._st_link['fw'] = line.split()[-1]
            self._st_links.append(self._st_link)
            self._st_link = dict()
            return
        if 'UART Interface' in line:
            self._uart = dict()
            self._st_link = None
            # logger.debug('Found {}'.format(line))
            return
        if self._uart is not None and 'Port:' in line:
            self._uart['port'] = line.split(':')[-1].strip()
            return
        if self._uart is not None and 'Description:' in line:
            if 'STMicroelectronics' in line:
                self._uart['description'] = line.split(':')[-1].strip()
                self._uarts.append(self._uart)
            self._uart = dict()
        if 'Error: No ST-Link detected!' in line:
            self._no_st_link_detected = True
        return


class STM32ProgConnectCommandParser():
    """Parser of the --connect command"""

    def __init__(self):
        self._desc = dict()

    @property
    def desc(self):
        """Return info"""
        return self._desc

    def __call__(self, line):
        """Parse a line"""
        if not isinstance(line, str):
            return
        if 'ST-LINK SN' in line:
            self._desc['sn'] = line.split(':')[-1].strip()
        elif 'ST-LINK FW' in line:
            self._desc['fw'] = line.split(':')[-1].strip()
        elif 'Board' in line:
            self._desc['board'] = line.split(':')[-1].strip()
        elif 'Device ID' in line:
            self._desc['device_id'] = line.split(':')[-1].strip()
        elif 'Device name' in line:
            self._desc['device_name'] = line.split(':')[-1].strip()
        elif 'Device type' in line:
            self._desc['device_type'] = line.split(':')[-1].strip()
        elif 'Device CPU' in line:
            self._desc['device_cpu'] = line.split(':')[-1].strip()


def _stm32_get_info(app, serial_number=None, series:str=""):
    """Return description of the connected board"""
    cmd_line = [app, '--connect', 'port=SWD', 'mode=UR', 'reset=HWrst']
    if series == "stm32n6":
        cmd_line = [app, '--connect', 'port=SWD', 'mode=HOTPLUG', '-hardRst']
    if serial_number:
        cmd_line.append(f'sn={serial_number}')
    parser = STM32ProgConnectCommandParser()
    cur_logger = logger if os.environ.get(STMAIC_DEBUG_ENV, None) else None
    run_shell_cmd(cmd_line, logger=cur_logger, parser=parser, assert_on_error=True)
    return parser.desc


def get_stm32_board_interfaces(series:str="") -> Tuple[List[dict], List[dict]]:
    """Return tuple of dict with the connected ST-Link:SWD/UART interfaces"""

    app = STM32_TOOLS.get_cube_programmer()
    if app:
        parser = STM32ProgListCommandParser()
        cmd_line = [app[0], '--list']
        err, lines = run_shell_cmd(cmd_line, logger=logger, parser=parser)
        if err != 0 and not parser.no_st_link_detected():
            if not logger and logger.getEffectiveLevel() > logging.DEBUG:
                for line in lines:
                    logger.error(line)
        st_links = parser.st_links()
        uarts = parser.uarts()
        for idx, st_link in enumerate(st_links):
            st_links[idx] = _stm32_get_info(app[0], serial_number=st_link['sn'], series=series)
        return st_links, uarts

    logger.warning(f'"{STM32Tools.CUBE_PROGRAMMER}" application is not available')
    return [], []


def reset_stm32_board(serial_number=None):
    """Reset the board"""
    app = STM32_TOOLS.get_cube_programmer()
    if app:
        cmd_line = [app[0], '--connect', 'port=SWD', 'mode=UR', 'reset=HWrst']
        if serial_number:
            cmd_line.append(f'sn={serial_number}')
        cur_logger = logger if os.environ.get(STMAIC_DEBUG_ENV, None) else None
        run_shell_cmd(cmd_line, logger=cur_logger)
