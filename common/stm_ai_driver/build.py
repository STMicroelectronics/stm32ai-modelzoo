###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - C-project Updater/Builder
"""

import os
import sys
import logging
import glob
import shutil
import re
from typing import Optional, List, Union, Any
from pathlib import Path
import tempfile

from .session import STMAiSession
from .board_config import STMAiBoardConfig
from .utils import run_shell_cmd, STMAICOptionError, _LOGGER_NAME_, STMAICToolsError
from .stm32_tools import STM32_TOOLS as STM32Tools
from .stm32_tools import get_stm32_board_interfaces

logger = logging.getLogger(_LOGGER_NAME_)


_EXT_FILE = ('.c', '.h', '.txt')
_STM_AI_LIB_PATTERN = r'NetworkRuntime[0-9]{3,}_[A-Za-z0-9]{3,}_[A-Z]{3,}.a'


def _get_file_and_subdirectory(root_dir: Union[str, Path]):
    """Return list of files/dirs from a given root directory"""

    root_dir = Path(root_dir).resolve()
    if not root_dir.name or not root_dir.is_dir():
        if root_dir.is_file():
            return [root_dir], []
        return [], []
    dirs = []
    files = []
    for item in glob.glob(os.path.join(root_dir, r'*')):  # type:Union[Path, str]
        item = Path(item)
        if item.is_dir():
            dirs.append(item)
        elif item.suffix in _EXT_FILE:
            files.append(item)
    return files, dirs


def _copy_tree(src, dst):
    """Recursively copy an entire directory tree rooted at src to a directory named dst"""
    # WA of shutil.copytree() before Python3.8+ to be able to copy a directory to
    # a directory already existed.
    # https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
    # - if dst doesn't exist, it is created
    # - if a file from src already exists in dst, the file in dst is overwritten
    # - files already existing in dst which don't exist in src are preserved
    # - Symlinks inside src are copied as symlinks, they are not resolved before copying.
    dst.mkdir(parents=True, exist_ok=True)
    for item in os.listdir(src):
        src_d = src / item
        dest_d = dst / item
        if src_d.is_dir():
            _copy_tree(src_d, dest_d)
        else:
            shutil.copy2(str(src_d), str(dest_d))


def _remove_tree(dst):
    """Remove current directory and sub_directories"""
    shutil.rmtree(dst, ignore_errors=True)


def _update_cube_ide_cproject(prj_dir: str, stm_ai_lib: str):
    """Update the cube.ide cproject file"""
    c_project = os.path.join(prj_dir, '.cproject')
    if os.path.isfile(c_project):
        with open(c_project, 'r+', encoding='utf-8') as c_prj_file:
            file_data = c_prj_file.read()
            if re.search(_STM_AI_LIB_PATTERN, file_data):
                n_file_data = re.sub(_STM_AI_LIB_PATTERN, stm_ai_lib, file_data)
                c_prj_file.truncate(0)
                c_prj_file.seek(0)
                c_prj_file.write(n_file_data)


def _update_source_tree(session: STMAiSession, user_files: Union[str, List[str], Path, List[Path]]) -> str:
    """Update the source tree"""

    conf = session.board.config

    if not conf.templates:
        if session.renderer_params() or user_files:
            logger.warning('"templates" property is empty, src tree is not updated!')
        return ''

    # build the list of updating operations
    operations = {}
    for item in conf.templates:
        src, dest, mode = item
        dest = Path(dest)
        tag = dest.name if (not src or mode == 'stm.ai.renderer') else src
        operations[tag] = [Path(src), dest, mode, dest.stem]

    # updated files/dir from the session
    s_files, s_dirs = _get_file_and_subdirectory(session.generated_dir)

    # updated files/dir from the user_files
    if isinstance(user_files, list):
        u_files, u_dirs = [], []
        for item in user_files:
            u_fs, u_ds = _get_file_and_subdirectory(item)
            u_files.extend(u_fs)
            u_dirs.extend(u_ds)
    else:
        u_files, u_dirs = _get_file_and_subdirectory(user_files)

    # process specific case, 'generated' directory
    for cdt_dir in u_dirs:
        if cdt_dir.name == 'generated':
            nu_files, nu_dirs = _get_file_and_subdirectory(cdt_dir)
            u_dirs.remove(cdt_dir)  # pylint: disable=modified-iterating-list
            u_files.extend(nu_files)
            u_dirs.extend(nu_dirs)
            break

    # user files are used before session files
    s_files_idx = len(u_files)
    s_dirs_idx = len(u_dirs)
    u_files.extend(s_files)
    u_dirs.extend(s_dirs)

    # check if a STM.AI lib is provided
    stm_ai_lib = ''
    for cdt_dir in u_dirs:
        logger.debug(f' -> searching stm.ai lib in \"{cdt_dir}\"')
        cdt_dir = Path(cdt_dir)
        for entry in cdt_dir.iterdir():
            if re.search(_STM_AI_LIB_PATTERN, str(entry)):
                stm_ai_lib = Path(entry).name
                logger.debug(f' found \"{stm_ai_lib}\"')
                break
        if stm_ai_lib:
            break

    # execute the operations
    count = 0
    not_updated = []
    for key, val in operations.items():
        src, dest, mode, _ = val
        cur_count = count
        if mode in ('copy', 'copy-file'):
            for idx, cdt_file in enumerate(u_files):
                if key == cdt_file.name:
                    tag = 'u' if idx < s_files_idx else 's'
                    logger.info(f' -> {tag}:copying file.. "{key}" to {dest}')
                    logger.debug(f'    src="{cdt_file}"')
                    shutil.copy(cdt_file, dest)
                    count += 1
                    break
        elif mode in 'stm.ai.renderer':
            if session.renderer_params():
                logger.info(f' -> rendering.. "{key}" to {dest}')
                logger.debug(f'    src="{src}"')
                session.render(str(src), str(dest))
                count += 1
        elif 'copy-dir' in mode:
            for idx, cdt_dir in enumerate(u_dirs):
                if key == cdt_dir.name:
                    tag = 'u' if idx < s_dirs_idx else 's'
                    if 'no-delete' not in mode:
                        if os.path.isdir(dest) and os.listdir(dest):
                            logger.info(f' -> {tag}:removing dir.. {dest}')
                            _remove_tree(dest)
                    logger.info(f' -> {tag}:copying dir.. "{key}" to {dest}')
                    logger.debug(f'    src="{cdt_dir}"')
                    _copy_tree(cdt_dir, dest)
                    count += 1
                    break
        else:
            logger.debug(f' -> "{key}" (mode="{mode}") not supported!')
        if count == cur_count:
            not_updated.append(key)

    if count != len(conf.templates):
        logger.warning(f'all the files are not be updated, {count}/{len(conf.templates)}!')
        logger.warning(f' -> {not_updated}')

    return stm_ai_lib


def _programm_dev_board(config, serial_number=None):
    """Call the flash command"""
    logger.info(f'flashing.. {config.name} {config.board}')
    cmd_line = config.flash_cmd

    if isinstance(cmd_line, list):
        str_args = ' '.join([str(x) for x in config.flash_cmd])
    else:
        str_args = config.flash_cmd

    class ParserErrorCube():
        """Parser of the --connect command"""

        def __init__(self):
            self._line_error = ''

        @property
        def error(self):
            """Return info"""
            return self._line_error

        def __call__(self, line):
            if line and 'error' in line.lower():
                self._line_error = line

    parser = None
    if (STM32Tools().CUBE_PROGRAMMER in str_args) or config.use_cube_prog:
        # check if valid board is connected (ST-Link SWD mode)
        parser = ParserErrorCube()
        st_links, _ = get_stm32_board_interfaces()
        warning_msg = 'board programming is SKIPPED!'

        def _connected_boards(st_links):
            for index_enum, st_link in enumerate(st_links):
                msg_ = ' id={}    board={}, sn={}'.format(index_enum, st_link['board'], st_link['sn'])
                logger.warning(msg_)

        if not st_links:
            logger.warning(warning_msg)
            msg_ = ' -> No valid STM32 development board is connected (ST-LINK/swd port)..'
            logger.warning(msg_)
            return
        # if sn is not defined, find the first sn associated to the board name if available
        found = None
        if isinstance(config.board, list):
            list_boards = [name.lower() for name in config.board]
        else:
            list_boards = config.board.lower()
        for st_link in st_links:
            if st_link['board'].lower() in list_boards:
                found = st_link['sn']
                break
        if config.board and not found:
            logger.warning(warning_msg)
            msg_ = f' -> no {config.board} board is connected (ST-LINK/swd port). '
            logger.warning(msg_)
            _connected_boards(st_links)

            """ Get approval to flash to the connected board"""
            if len(st_links) == 1:
                if sys.stdin.isatty():
                    msg_ = f'Do you confirm you want to flash the {st_links[0]["board"]} board? yes/no: '
                    flash_anyway = input(msg_)
                else:
                    flash_anyway = sys.stdin.readline().rstrip()
                if flash_anyway.lower() in ["yes", "y"]:
                    found = st_link['sn']
                    logger.warning("You can add your board in the section board in the stmaic_*.conf you're deploying to skip prompt")
                else:
                    found = None
                    return
            # """ Choose one of the connected board"""
            else:
                if sys.stdin.isatty():
                    msg_ = f'Do you want to flash one of the board? Enter the board id or False: '
                    index_board = input(msg_)
                else:
                    index_board = sys.stdin.readline().rstrip()
                if index_board.isnumeric():
                    found = st_links[int(index_board)]['sn']
                    logger.warning("You can add your board in the section board in the stmaic_*.conf you're deploying to skip prompt")
                else:
                    found = None
                    return
                
        serial_number = found if not serial_number else serial_number
        if len(st_links) > 1 and not serial_number:
            logger.warning(warning_msg)
            msg_ = ' -> muliple STM32 development boards are connected (ST-LINK/swd port). '
            msg_ += 'Please, set the serial number ("serial_number" argument)'
            logger.warning(msg_)
            _connected_boards(st_links)
            return
        if serial_number:
            found = False
            for st_link in st_links:
                if st_link['sn'] == serial_number:
                    found = True
                    break
            if not found:
                logger.warning(warning_msg)
                msg_ = f' -> provided serial number "{serial_number}" is invalid'
                logger.warning(msg_)
                _connected_boards(st_links)
                return
        port = re.search('port=swd', str_args, re.IGNORECASE)
        if port and serial_number:
            str_args = str_args[:port.start()] + f'port=swd sn={str(serial_number)} ' + str_args[port.end() + 1:]
    # logger.debug(' {}'.format(str_args))
    run_shell_cmd(str_args,
                  cwd=config.cwd,
                  logger=logger,
                  parser=parser)
    if parser and parser.error:
        logger.error(f'Board programming failed: "{parser.error}"')


def _makefile_builder(session: STMAiSession, conf: Any,
                      user_files: Union[str, List[str], Path, List[Path]],
                      no_templates: bool, serial_number: str, no_flash: bool):
    """Makefile builder engine"""

    logger.debug(' cwd=%s', str(conf.cwd))

    if hasattr(conf, 'clean_cmd'):
        logger.info(f'cleaning.. {conf.name}')
        # logger.debug(' {}'.format(conf.clean_cmd))
        run_shell_cmd(conf.clean_cmd,
                      cwd=conf.cwd,
                      logger=logger)

    update_c_files = not no_templates and not conf.no_templates
    if update_c_files:
        logger.info(f'updating.. {conf.name}')
        _update_source_tree(session, user_files)

    if hasattr(conf, 'build_cmd'):
        logger.info(f'building.. {conf.name}')
        # logger.debug(' {}'.format(conf.build_cmd))
        run_shell_cmd(conf.build_cmd,
                      cwd=conf.cwd,
                      logger=logger)

    if hasattr(conf, 'flash_cmd') and not no_flash:
        _programm_dev_board(conf, serial_number=serial_number)


def _cube_ide_builder(cube_ide_exe: str, session: STMAiSession, conf: Any,
                      user_files: Union[str, List[str], Path, List[Path]],
                      no_templates: bool, serial_number: str, no_flash: bool):
    """STM32 Cube IDE builder engine"""

    logger.debug(' cwd=%s', str(conf.cwd))

    prj_dir = os.path.abspath(conf.cproject_location)

    class ParserErrorCubeIde():
        """Parser error Cube IDE"""

        def __init__(self):
            self._line_error = ''

        @property
        def error(self):
            """Return info"""
            return self._line_error

        def __call__(self, line):
            if line and 'no config matched' in line.lower():
                self._line_error = line

    with tempfile.TemporaryDirectory() as tmpdirname:
        ws_dir = tmpdirname

        update_c_files = not no_templates and not conf.no_templates
        if update_c_files:
            logger.info(f'updating.. {conf.name}')
            stm_ai_lib = _update_source_tree(session, user_files)
        if stm_ai_lib and not session.board.stm_ai_version.is_valid():
            logger.info(f' -> updating cproject file \"{prj_dir}\" with \"{stm_ai_lib}\"')
            _update_cube_ide_cproject(prj_dir, stm_ai_lib)

        parser = ParserErrorCubeIde()
        logger.info(f'building.. {conf.name}')
        cmd = [cube_ide_exe]
        cmd.extend(['--launcher.suppressErrors', '-nosplash'])
        cmd.extend(['-application org.eclipse.cdt.managedbuilder.core.headlessbuild'])
        cmd.extend(['-import', f'{prj_dir}'])
        cmd.extend(['-data', f'{ws_dir}', '-cleanBuild', f'"{conf.cproject_name}/{conf.cproject_config}"'])
        run_shell_cmd(cmd,
                      cwd=conf.cwd,
                      logger=logger,
                      parser=parser)
        if parser and parser.error:
            logger.error(f'STM32CubeIDE build failed: "{parser.error}"')

        if hasattr(conf, 'flash_cmd') and not no_flash:
            _programm_dev_board(conf, serial_number=serial_number)


def cmd_build(
        session: STMAiSession,
        target: Optional[Union[STMAiBoardConfig, None]] = None,
        user_files: Union[str, List[str], Path, List[Path]] = '',
        no_flash: bool = False,
        **kwargs
):
    """Build service"""

    serial_number = kwargs.pop('serial_number', None)
    no_templates = kwargs.pop('no_templates', False)

    if target and session.board and session.board != target:
        raise STMAICOptionError("Board configuration object is different...", idx=1)

    if not target and not session.board:
        raise STMAICOptionError("Board configuration object should be provided...", idx=2)

    board = target if target else session.board
    session.set_board(board)

    used_conf = board.config

    if (session.stm_ai_version != board.stm_ai_version) and board.stm_ai_version.is_valid():
        logger.warning('deployment is SKIPPED !')
        logger.warning(f'  STM.AI version are differents.. {session.stm_ai_version} != {board.stm_ai_version}')
        return

    logger.info('deploying the c-project.. %s', str(board))

    # logger.info('checking series.. NOT YET IMPLEMENTED')
    # logger.info('checking memory... NOT YET IMPLEMENTED')

    if used_conf.builder == 'stm32_cube_ide':

        cube_ide_exe = STM32Tools().get_cube_ide()
        if not cube_ide_exe:
            logger.error('STM32_CUBE_IDE_EXE should be set')
            return

        _cube_ide_builder(cube_ide_exe[0], session, used_conf,
                          user_files, no_templates,
                          serial_number, no_flash)

        if used_conf.linked_conf and used_conf.linked_conf != used_conf.name:
            prev = used_conf.name
            used_conf = board.set_config(used_conf.linked_conf)
            _cube_ide_builder(cube_ide_exe[0], session, used_conf,
                              user_files, no_templates,
                              serial_number, no_flash)
            board.set_config(prev)

    elif used_conf.builder == 'makefile':

        _makefile_builder(session, used_conf, user_files, no_templates,
                          serial_number, no_flash)

    else:
        raise STMAICToolsError(f'Unsupported toolchain : {used_conf.builder}')
