###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - STM AI tools manager
"""

import os
import logging
import shutil
import glob
import sys
import re
from pathlib import Path
from typing import List, Union, Tuple

from common.stm32ai_local.utils import (STMAICToolsError,
                                 STMAiVersion,
                                 _LOGGER_NAME_,
                                 load_json_safe,
                                 run_shell_cmd)


logger = logging.getLogger(_LOGGER_NAME_)


_X_CUBE_AI_PACK_TAG = 'x-cube-ai'
_X_CUBE_AI_REPO_TAG = 'repo'


def _fix_list_cmd(cmd: List[str], root_dir: str, host_os: str):
    """Update the items"""
    if not cmd:
        return []
    cmd_ = []
    for item in cmd:
        if 'root_dir' in item:
            item = item.format(root_dir=root_dir)
        if 'host_os' in item:
            item = item.format(host_os=host_os)
        cmd_.append(item)
    return cmd_


def _is_stm_ai_repo_path(path: str) -> Tuple[str, STMAiVersion]:
    """Indicate if the path is a repo directory"""
    version_ = {}

    if not path:
        return '', STMAiVersion()

    path = os.path.normpath(path)
    if os.path.isdir(os.path.join(path, 'new_root')):
        from importlib import import_module
        try:
            mod = import_module('src.irs.stm_ai_version_constants')
            version_ = getattr(mod, 'STM_AI_VERSION')
        except ImportError:
            path = ''
        return path, STMAiVersion(dict(version_))

    return '', STMAiVersion()


def _get_stm32ai_cli(root_path: Union[str, Path], host_os: str) -> List[Tuple[STMAiVersion, Path, Path]]:
    """Return a list a tuple with the version and the path of the stm ai executable"""
    results = []
    cdts = []
    root_path = Path(root_path)
    if root_path.is_file():  # valid file is passed
        filepath = root_path
    elif len(list(root_path.rglob("stedgeai.exe"))) > 0:
        filepath = list(root_path.rglob("stedgeai.exe"))
    elif len(list(root_path.rglob("stedgeai"))) > 0:
        filepath = list(root_path.rglob("stedgeai"))
    elif len(list(root_path.rglob("stm32ai.exe"))) > 0:
        filepath = list(root_path.rglob("stm32ai.exe"))
    elif len(list(root_path.rglob("stm32ai"))) > 0:
        filepath = list(root_path.rglob("stm32ai"))
    else:
        logger.error(' \"%s\" path is not valid..', root_path)
        return []
    logger.info(' Cube AI Path: \"%s\".', filepath)
    cdt = Path(filepath)
    if cdt.suffix in ('.exe', '') and host_os in str(cdt):
        logger.debug(' checking if \"%s\" is valid..', cdt)
        idx = 2
        middlewares = cdt.parent / '..' / '..' / 'Middlewares'
        if not middlewares.is_dir():
            idx = 1
            middlewares = cdt.parent / '..' / 'Middlewares'
        if not middlewares.is_dir():
            idx = 0
            middlewares = cdt.parent / 'Middlewares'
        cmd_line = str(filepath) + ' --version'
        err, lines = run_shell_cmd(cmd_line, logger=logger)
        pattern = re.compile(r'STM32CubeAI (\d+\.\d+\.\d+)')
        lines_conc = "".join(lines)
        version = pattern.findall(lines_conc)
        if version == []:
            raise ValueError('Unable to find the CubeAi version')
        ver = STMAiVersion(version[0], '{} pack'.format(_X_CUBE_AI_PACK_TAG))
        results.append((ver, cdt.parents[idx], cdt))
        logger.debug(' found %s (v=%s)', cdt, version)
    if not results:
        logger.warning(' No valid STM AI installation has been found from \"%s\"', root_path)

    for exec_ in results:

        if not os.access(exec_[2], os.X_OK):
            raise STMAICToolsError(' \"{}\" is not an executable'.format(exec_[2]))

    return sorted(results, reverse=True)


class STMAiTools:
    """Object to handle the STM AI tools"""

    def __init__(self, root_dir: str = '', version: Union[STMAiVersion, str] = '') -> None:
        """Set the used STM AI tools"""

        self._executable = None
        stm_ai_version = None
        stm_ai_repo = ''
        stm_ai_pack = ''
        version = STMAiVersion(version) if version else ''

        self._ai_runtime_libs = load_json_safe(os.path.join(os.path.dirname(__file__),
                                                            'resources', 'ai_runtime_libs.json'))
        dev_env = os.path.join(os.path.dirname(__file__), '..', '_internal_', 'ai_runtime_libs_repo.json')
        if Path(dev_env).is_file():
            ai_runtime_libs_dev = load_json_safe(dev_env)
            self._ai_runtime_libs["repo"] = ai_runtime_libs_dev['repo']

        msg_ = f'setting STM.AI tools.. root_dir="{root_dir}", req_version="{version}"'
        logger.info(msg_)

        # STM AI CLI from the binary pack is considered in priority
        if not root_dir:
            root_dir = os.environ.get('STM32_AI_EXE', '')
            if not root_dir:
                root_dir = os.environ.get('STM_AI_EXE', '')
            if root_dir:
                logger.debug(' STM32_AI_EXE is used: %s', root_dir)
            if not root_dir:
                location = shutil.which('stm32ai')
                if location:
                    root_dir = os.path.dirname(location)
                    logger.debug(' STM.AI executable: %s', root_dir)
                else:
                    home = str(Path.home())
                    root_dir = os.path.join(home, 'STM32Cube', 'Repository', 'Packs',
                                            'STMicroelectronics', 'X-CUBE-AI')
                    if not os.path.isdir(root_dir):
                        root_dir = ''

        if root_dir == 'repo' and not os.path.isdir(root_dir):
            root_dir = ''

        if root_dir:
            host_os = self._ai_runtime_libs['host_os'][sys.platform]
            cdts = _get_stm32ai_cli(root_dir, host_os)
            if cdts and not version:
                stm_ai_version = cdts[0][0]
                stm_ai_pack = str(cdts[0][1])
                self._executable = str(cdts[0][2])
            else:
                for cdt in cdts:
                    if version == cdt[0]:
                        stm_ai_version = cdt[0]
                        stm_ai_pack = str(cdt[1])
                        self._executable = str(cdt[2])
                        break
            if not cdts:
                root_dir = ''

        if not root_dir and 'repo' in self._ai_runtime_libs:
            root_dir = os.environ.get('STM_AI_REPO', '')
            if root_dir:
                logger.debug('STM_AI_REPO is used: %s', root_dir)
            stm_ai_repo, stm_ai_version = _is_stm_ai_repo_path(root_dir)
            if version and version != stm_ai_version:
                stm_ai_repo = ''

        self._root_path = stm_ai_repo if stm_ai_repo else stm_ai_pack
        self._version = stm_ai_version
        if not self._root_path or not self._version:
            if root_dir:
                msg_ = f'Can\'t find tools (version="{version}") from "{root_dir}"'
                logger.error(msg_)
                raise STMAICToolsError(msg_, idx=1)
            env_exe = os.environ.get('STM32_AI_EXE')
            raise STMAICToolsError(f'Can\'t find the stm32ai app: STM32_AI_EXE={env_exe} {version}')

        msg_ = f' root_path={self._root_path} -> {str(self)}'
        logger.debug(msg_)

        self._tag = _X_CUBE_AI_PACK_TAG if stm_ai_pack else _X_CUBE_AI_REPO_TAG if stm_ai_repo else None

        self._stm32_tools = load_json_safe(os.path.join(os.path.dirname(__file__),
                                                        'resources', 'stm32_tools.json'))

        if not self._tag or not self._root_path:
            raise STMAICToolsError("No STM.AI is defined")

    @property
    def location(self):
        """Return root directory of the selected X-CUBE-AI tool"""
        return self._root_path

    @property
    def version(self):
        """Return version value"""
        return self._version

    def get_full_version(self) -> str:
        """Retreive the full tools version"""

        cmd_ = self.executable()
        cmd_.extend(['--version'])
        err, log = run_shell_cmd(cmd_, logger=logger)

        if not err:
            return log[0]
        return f'error = {err}'

    def executable(self) -> List[str]:
        """Return executable"""

        if self._executable:
            return [self._executable]

        host_os = self._ai_runtime_libs['host_os'][sys.platform]
        exec_ = _fix_list_cmd(self._ai_runtime_libs[self._tag]['executable'],
                              self._root_path,
                              host_os)
        exec_ = os.path.join(exec_[0], *exec_[1:])
        return [exec_]

    def python_path(self) -> str:
        """Return specific Python path if requested"""

        if self._ai_runtime_libs[self._tag].get('python_path', None):
            host_os = self._ai_runtime_libs['host_os'][sys.platform]
            python_path_ = _fix_list_cmd(self._ai_runtime_libs[self._tag]['python_path'],
                                         self._root_path, host_os)
            python_path_ = os.path.join(python_path_[0], *python_path_[1:])
            logger.debug(' python path: %s', python_path_)
            return python_path_

        return ''

    def ai_runtime_inc(self) -> str:
        """Return path of the C-header files of the AI network runtime lib"""

        extra = os.path.normpath(self._ai_runtime_libs[self._tag]['inc_lib'])
        return os.path.join(self._root_path, extra)

    def neural_art(self, series='', toolchain='gcc') -> str:
        """Return path and lib of the AI network runtime lib"""

        toolchain = toolchain.lower()
        descs = self._ai_runtime_libs[self._tag][toolchain]
        for desc in descs:
            if series in desc['series']:
                if 'neuralart_dir' in desc:
                    neuralart_dir = os.path.join(self._root_path, os.path.normpath(desc['neuralart_dir']))
                    return neuralart_dir

    def ai_runtime_lib(self, series='stm32f4', toolchain='gcc') -> str:
        """Return path and lib of the AI network runtime lib"""

        toolchain = toolchain.lower()
        lib_ext = self._ai_runtime_libs[self._tag]['lib_extension'][toolchain]
        descs = self._ai_runtime_libs[self._tag][toolchain]
        for desc in descs:
            if series in desc['series']:
                lib_dir = os.path.join(self._root_path, os.path.normpath(desc['lib_dir']))
                return glob.glob(os.path.join(lib_dir, f'{lib_ext}'))[0]

        msg_ = f'Can\'t find the lib path for "{toolchain}/{series}"'
        raise STMAICToolsError(msg_, idx=2)

    def ai_runtime_compiler_options(self, series='stm32f4', toolchain='gcc') -> str:
        """Return C mcu compiler options for the AI network runtime lib"""

        toolchain = toolchain.lower()
        descs = self._ai_runtime_libs[self._tag][toolchain]
        for desc in descs:
            if series in desc['series']:
                return desc['core_flags']

        msg_ = f'Can\'t find the compiler options for "{toolchain}/{series}"'
        raise STMAICToolsError(msg_, idx=3)

    def __str__(self):
        """Return human readable version of the selected STM AI tools"""
        stm_ai_version = "undefined"
        if self._version:
            stm_ai_version = str(self._version)
        return stm_ai_version
