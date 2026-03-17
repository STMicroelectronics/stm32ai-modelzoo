###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - C project description loader
"""

import json
import os
import logging
from typing import Optional, Union, List, Any

from .utils import load_json_safe
from .utils import DictToObj, STMAiVersion, _LOGGER_NAME_
from .utils import STMAICFileError, STMAICJsonSyntaxError
from .stm32_tools import STM32_TOOLS as STM32Tools

logger = logging.getLogger(_LOGGER_NAME_)


class CProjectDescReader:
    """Helper class to read the C project description file"""

    def __init__(self, c_project_path: str, series: str):

        self._conf_path = c_project_path
        self._dict = load_json_safe(self._conf_path)

        # check JSON file version
        json_version = self._dict['version']
        if json_version != '0.1':
            raise STMAICJsonSyntaxError('version"::"1.0"', idx=2)

        self._update(os.path.normpath(os.path.dirname(self._conf_path)), series)

    def __getattr__(self, attr):
        if attr == 'configurations':
            return [DictToObj(c, c['name']) for c in self._dict[attr]]
        return self._dict[attr]

    def _update(self, project_folder: str, series: str):

        # check/update

        if 'description' not in self._dict:
            self._dict['description'] = 'no desription'

        g_builder = self._dict.get('builder', 'makefile')
        g_series = series or self._dict.get('series', 'x86')
        g_board = self._dict.get('board', '')

        if 'configurations' not in self._dict or not isinstance(self._dict['configurations'], list)\
                or len(self._dict['configurations']) == 0:
            desc_ = 'configurations : [ { name: " ", ...} ]'
            raise STMAICJsonSyntaxError(f'{desc_}', idx=1)

        # update the ${xxx} tags
        env = self._dict.get('env', dict())
        memory_pool = self._dict.get('memory_pool', dict())

        for item in env.items():
            if not isinstance(item[1], str):
                raise STMAICJsonSyntaxError(f'{item[0]}::string', idx=2)

        if 'ProjectFolder' not in env:
            env['ProjectFolder'] = project_folder.replace('\\', '/')

        if 'STM32CubeProgrammer' not in env:
            prog_cli = STM32Tools().get_cube_programmer()
            prog_cli = prog_cli[0] if prog_cli else 'NOT FOUND'
            env['STM32CubeProgrammer'] = prog_cli

        if 'STM32SigningTool' not in env:
            prog_cli = STM32Tools().get_cube_signing_tool()
            prog_cli = prog_cli[0] if prog_cli else 'NOT FOUND'
            env['STM32SigningTool'] = prog_cli

        if 'STM32Make' not in env:
            prog_make = STM32Tools().get_make()
            prog_make = prog_make[0] if prog_make else 'NOT FOUND'
            env['STM32Make'] = prog_make

        if 'cwd' not in env:
            env['cwd'] = env['ProjectFolder']

        self._dict['env'] = env

        # update the 'memory_pool_path' value
        if memory_pool:
            if 'memory_pool_path' in memory_pool:
                memory_pool["memory_pool_path"] = memory_pool["memory_pool_path"].replace("${ProjectFolder}", env['ProjectFolder'])
            if "neuralart_user_path" in memory_pool:
                memory_pool["neuralart_user_path"] = memory_pool["neuralart_user_path"].replace("${ProjectFolder}", env['ProjectFolder'])
            if "mpool" in memory_pool:
                memory_pool["mpool"] = memory_pool["mpool"].replace("${ProjectFolder}", env['ProjectFolder'])
        # update first the 'env' values
        for item in env.items():
            for tag in env:
                full_tag = '${0}{1}{2}'.format('{', tag, '}')
                env[item[0]] = env[item[0]].replace(full_tag, env[tag])

        json_string = json.dumps(self._dict)

        # update the whole json file contents
        for tag in env:
            full_tag = '${0}{1}{2}'.format('{', tag, '}')
            json_string = json_string.replace(full_tag, env[tag])

        # re-create the dict
        self._dict = json.loads(json_string)

        def to_bool(cur_dict, cur_key):
            item = cur_dict.get(cur_key, None)
            if item and isinstance(item, str):
                if item.strip().lower() in ('false', '0', 'n', 'no'):
                    return False
                elif item.strip().lower() == ('true', '1', 'y', 'yes'):
                    return True
            return item

        # update configurations
        for conf in self._dict['configurations']:
            conf_name = conf["name"]
            conf['builder'] = conf.get('builder', g_builder).lower()
            conf['series'] = conf.get('series', g_series).lower()
            conf['board'] = conf.get('board', g_board)
            conf['cwd'] = conf.get('cwd', env['cwd'])
            conf['use_cube_prog'] = to_bool(env, 'use_cube_prog')
            conf['use_arm_none_eabi_gcc'] = to_bool(env, 'use_arm_none_eabi_gcc')
            conf['use_makefile'] = to_bool(env, 'use_makefile')
            conf['no_templates'] = to_bool(conf, 'no_templates')
            conf['linked_conf'] = conf.get('linked_conf', '')
            if memory_pool:
                if 'internalFlash_size' in memory_pool:
                    conf['internalFlash_size'] = conf.get('internalFlash_size', memory_pool['internalFlash_size'])
                if 'externalFlash_size' in memory_pool:
                    conf['externalFlash_size'] = conf.get('externalFlash_size', memory_pool['externalFlash_size'])
                if 'application_size' in memory_pool:
                    conf['application_size'] = conf.get('application_size', memory_pool['application_size'])
                if 'lib_size' in memory_pool:
                    conf['lib_size'] = conf.get('lib_size', memory_pool['lib_size'])
                if 'memory_pool_path' in memory_pool:
                    conf['memory_pool_path'] = conf.get('memory_pool_path', memory_pool['memory_pool_path'])
                # stm32 with neuralart
                if 'mpool' in memory_pool:
                    conf['mpool'] = conf.get('mpool', memory_pool['mpool'])
                if 'neuralart_user_path' in memory_pool:
                    conf['neuralart_user_path'] = conf.get('neuralart_user_path', memory_pool['neuralart_user_path'])
                if 'profile' in memory_pool:
                    conf['profile'] = conf.get('profile', memory_pool['profile'])

            tpls = conf.get('templates', None)
            if isinstance(tpls, str):
                conf['templates'] = self._dict.get(tpls, list())
                conf['no_templates'] = bool(not conf['templates'])
            elif isinstance(tpls, list):
                conf['templates'] = tpls
            else:
                conf['templates'] = self._dict.get('templates', list())

            # check/set the stm_ai_version and toolchain
            stm_ai_runtime = self._dict.get('stm_ai_runtime', {'version': '0.0.0', 'toolchain': 'gcc'})
            if not stm_ai_runtime.get('toolchain', ''):
                stm_ai_runtime['toolchain'] = 'gcc'
            if stm_ai_runtime['toolchain'] != 'gcc':
                raise STMAICJsonSyntaxError('stm_ai_runtime.toolchain::"gcc"', idx=2)

            conf['stm_ai_version'] = STMAiVersion(stm_ai_runtime['version'])
            conf['toolchain'] = stm_ai_runtime['toolchain'].lower()

            # check/set the builder operations
            if conf['builder'] not in ('stm32_cube_ide', 'makefile'):
                raise STMAICJsonSyntaxError('builder::"stm32_cube_ide" or "makefile"', idx=2)

            if conf['builder'] == 'stm32_cube_ide':
                if 'cproject_location' not in conf:
                    raise STMAICJsonSyntaxError(f'cproject_location::{conf_name}', idx=1)
                if 'cproject_config' not in conf:
                    raise STMAICJsonSyntaxError(f'cproject_config::{conf_name}', idx=1)
                if 'cproject_name' not in conf:
                    raise STMAICJsonSyntaxError(f'cproject_name::{conf_name}', idx=1)


class STMAiBoardConfig:
    """Class object to handle the c-project description"""

    def __init__(self, project_path: Optional[str] = '',
                 config_name: Optional[str] = ''):
        """."""

        series = ''
        if isinstance(project_path, str) and not os.path.isfile(project_path):
            if project_path.lower().startswith('stm32') or project_path.lower() == 'x86':
                series = project_path

        if not project_path or series:
            # default c-project is used
            project_path = os.path.join(os.path.dirname(__file__),
                                        'resources', 'generic_board.json')

        logger.info(f'loading conf file.. "{project_path}" config="{config_name}"')

        if not os.path.isfile(project_path):
            raise STMAICFileError(f'"{project_path}" is not a regular file')

        self._nn_project = CProjectDescReader(project_path, series)

        logger.debug('supporting configurations:')
        for conf in self._nn_project.configurations:
            ext_ = f' -> {conf.linked_conf}' if conf.linked_conf else ''
            logger.debug(f' {conf.name}{ext_}')

        self._conf = self._nn_project.configurations[0]
        if config_name:
            self._conf = self.set_config(config_name)

        logger.info(f'"{self._conf.name}" configuration is used')

    @property
    def description(self) -> str:
        """Return the description property from the STM32 C-project file"""
        return self._nn_project.description

    @property
    def env(self) -> List[str]:
        """Return the set of the global "env" environment variables as a dict"""
        return self._nn_project.env

    @property
    def stm_ai_version(self) -> STMAiVersion:
        """Return the expected STM AI version"""
        return self.config.stm_ai_version

    @property
    def config(self) -> Any:
        """Return selected configuration"""
        return self._conf

    def configs(self) -> list:
        """Return name of the different configurations"""
        return [conf.name for conf in self._nn_project.configurations]

    def set_config(self, config_name: Optional[str] = None) -> Union[DictToObj, None]:
        """Set and return a configuratiion"""
        if config_name is None:
            return self._conf

        if config_name not in self.configs():
            raise STMAICFileError(f'Configuration "{config_name}" not available', idx=4)

        for conf in self._nn_project.configurations:
            if conf.name == config_name:
                self._conf = conf
                break

        return self._conf

    def summary(self, pr_f=None):
        """Display a summary of the selected configuration"""
        conf_ = self.config
        pr_f = pr_f if pr_f else print  # noqa:T202
        title = f'Configuration "{conf_.name}" / {self.description}'
        pr_f(f'\n{title}')
        pr_f('-' * len(title))
        pr_f(f' series             : {conf_.series} (board="{conf_.board}")')
        pr_f(f' stm_ai_version     : {conf_.stm_ai_version}')
        pr_f(f' builder            : {conf_.builder} (toolchain="{conf_.toolchain}")')
        pr_f(f'  cwd               : {conf_.cwd}')
        if conf_.builder == 'stm32_cube_ide':
            pr_f(f'  cproject_name     : {conf_.cproject_name}')
            pr_f(f'  cproject_config   : {conf_.cproject_config}')
            pr_f(f'  cproject_location : {conf_.cproject_location}')
        if conf_.builder == 'makefile':
            if hasattr(conf_, 'clean_cmd'):
                pr_f(f'  clean_cmd         : {conf_.clean_cmd}')
            if hasattr(conf_, 'build_cmd'):
                pr_f(f'  build_cmd         : {conf_.build_cmd}')
        if hasattr(conf_, 'flash_cmd'):
            pr_f(f'  flash_cmd         : {conf_.flash_cmd}')
        if hasattr(conf_, 'sign_cmd'):
            pr_f(f'  sign_cmd         : {conf_.sign_cmd}')
        if hasattr(conf_, 'flash_network_data_cmd'):
            pr_f(f'  flash_network_data_cmd         : {conf_.flash_network_data_cmd}')
        if hasattr(conf_, 'flash_fsbl_cmd'):
            pr_f(f'  flash_fsbl_cmd         : {conf_.flash_fsbl_cmd}')
        pr_f('')

    def __str__(self):
        """Return short description"""
        return f'"{self.description}" ({self.config.builder}/{self.config.name}/{self.config.series})'
