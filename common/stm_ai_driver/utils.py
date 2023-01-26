###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - Utilities
"""

import logging
import sys
import subprocess
import os
import re
import json
from pathlib import Path
from typing import Tuple, Union, List, Optional, Any, NamedTuple

from colorama import init, Fore, Style


_LOGGER_NAME_ = 'STMAIC'
STMAIC_LOGGER_NAME = _LOGGER_NAME_


class STMAICException(Exception):
    """Base exceptions for errors raised by STMAI driver"""
    error = 100

    def __init__(self, mess=None, idx=0):
        self.mess = mess
        self.idx = idx
        super(STMAICException, self).__init__(mess)

    def code(self):
        """Return code number"""  # noqa: DAR101,DAR201,DAR401
        return self.error + self.idx

    def __str__(self):
        """Return formatted error description"""  # noqa: DAR101,DAR201,DAR401
        _mess = ''
        if self.mess is not None:
            _mess = '{}'.format(self.mess)
        else:
            _mess = type(self).__doc__.split('\n')[0]
            _mess = '{}: {}'.format(type(self).__name__, _mess)
        _msg = 'E{}: {}'.format(self.code(), _mess)
        return _msg


class STMAICOptionError(STMAICException):
    """Invalid option"""
    error = 200


class STMAICFileError(STMAICException):
    """Invalid file"""
    error = 300


class STMAICToolsError(STMAICException):
    """Invalid tools configuration"""
    error = 400

    def __init__(self, mess=None, idx=0):
        if idx == 1 and mess:
            mess = f'Environment variable "{mess}" should be defined'
        super(STMAICToolsError, self).__init__(mess, idx)


class STMAICSyntaxError(STMAICException):
    """Syntax/Configuration issue"""
    error = 500


class STMAICJsonSyntaxError(STMAICException):
    """JSON Syntax error"""
    error = 600

    def __init__(self, mess=None, idx=0):
        if idx == 1 and mess:
            mess = mess.split('::')
            mess_ = f'(JSON) Property "{mess[0]}" should be defined'
            if len(mess) > 1:
                mess_ += f' for the conf. "{mess[1]}"'
            else:
                mess_ += '.'
            mess = mess_
        if idx == 2 and mess:
            mess = mess.split('::')
            mess_ = f'(JSON) Property "{mess[0]}" must be {mess[1]}'
            mess = mess_
        super(STMAICJsonSyntaxError, self).__init__(mess, idx)


class STMAiVersion:
    """Object to manage the STM AI version"""

    def __init__(self, version: Any = None, extra: str = ''):
        """Set the version"""
        if not version:
            version = '0.0.0'  # undefined value
        if isinstance(version, STMAiVersion):
            version = version.todict()  # copy mode
        if isinstance(version, str):
            vers = version.split(' ')[0].split('.')
            self.major = int(vers[0])
            self.minor = int(vers[1]) if len(vers) > 1 else 0
            self.micro = int(vers[2]) if len(vers) > 2 else 0
            self.extra = extra
        elif isinstance(version, dict):
            self.major = version.get('major', 0)
            self.minor = version.get('minor', 0)
            self.micro = version.get('micro', 0)
            self.extra = version.get('extra', '')
        else:
            raise ValueError(f'Invalid STM AI version definition {version}')

    def __eq__(self, other):
        if not isinstance(other, STMAiVersion):
            other = STMAiVersion(other)
        return self.toint() == other.toint()

    def __ge__(self, other):
        if not isinstance(other, STMAiVersion):
            other = STMAiVersion(other)
        return self.toint() >= other.toint()

    def __gt__(self, other):
        if not isinstance(other, STMAiVersion):
            other = STMAiVersion(other)
        return self.toint() > other.toint()

    def __le__(self, other):
        if not isinstance(other, STMAiVersion):
            other = STMAiVersion(other)
        return self.toint() <= other.toint()

    def __lt__(self, other):
        if not isinstance(other, STMAiVersion):
            other = STMAiVersion(other)
        return self.toint() < other.toint()

    def is_valid(self):
        """Indicate if the version is valid"""
        return self.major != 0 or self.minor != 0

    def todict(self):
        """Return a dict"""
        return {
            'major': self.major, 'minor': self.minor, 'micro': self.micro,
            'extra': self.extra
        }

    def toint(self, to_compare=False):
        """Return integer representation"""
        if to_compare:
            return self.major << 24 | self.minor << 16
        return self.major << 24 | self.minor << 16 | self.micro << 8

    def __str__(self):
        """Return a string human-readable representation"""
        if self.extra:
            return "{major}.{minor}.{micro} ({extra})".format(**self.todict())
        return "{major}.{minor}.{micro}".format(**self.todict())

    def __repr__(self):
        """Return a string representation"""
        return f'(major={self.major}, minor={self.minor}, micro={self.micro}, extra={self.extra})'


class ColorFormatter(logging.Formatter):
    """Color Formatter"""

    COLORS = {
        "WARNING": (Fore.YELLOW + Style.BRIGHT, 'W'),
        "ERROR": (Fore.RED + Style.BRIGHT, 'E'),
        "DEBUG": (Fore.CYAN, 'D'),
        "INFO": (Fore.GREEN, 'I'),
        "CRITICAL": (Fore.RED + Style.BRIGHT, 'C')
    }

    def format(self, record):
        color, lname = self.COLORS.get(record.levelname, "")
        if color:
            record.name = ''
            record.levelname = color + '[' + lname + ']' + Style.RESET_ALL
            record.msg = color + str(record.msg) + Style.RESET_ALL
        return logging.Formatter.format(self, record)


def get_logger(name=_LOGGER_NAME_, level=logging.WARNING, color=True):
    """Utility function to create a logger object"""

    logger = logging.getLogger(name)

    if not logger.propagate and logger.hasHandlers():
        # logger 'name' already created
        return logger

    if color:
        init()
    logger.setLevel(level)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    if color:
        color_formatter = ColorFormatter("%(levelname)s %(message)s")
        console.setFormatter(color_formatter)
    else:
        formatter = logging.Formatter(fmt='%(message)s')
        console.setFormatter(formatter)
    logger.addHandler(console)
    logger.propagate = False

    return logger


def set_log_level(level: Union[str, int] = logging.DEBUG):
    """Set the log level of the module"""

    if isinstance(level, str):
        level = level.upper()
    level = logging.getLevelName(level)

    logger = get_logger(_LOGGER_NAME_)
    logger.setLevel(level)
    logger.handlers[0].setLevel(level)


def run_shell_cmd(
        cmd_line: Union[str, List[str]],
        logger: logging.Logger = None,
        env: dict = None,
        cwd: str = None,
        parser=None) -> Tuple[int, List[str]]:
    """Execute a command in a shell and return the output"""

    startupinfo = None
    if sys.platform in ('win32', 'cygwin', 'msys'):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.SW_HIDE | subprocess.HIGH_PRIORITY_CLASS
        if isinstance(cmd_line, list):
            cmd_line[0] = cmd_line[0].replace('/', '\\')

    if isinstance(cmd_line, str):
        run_args = cmd_line
        str_args = cmd_line
    elif isinstance(cmd_line, list):
        str_args = ' '.join([str(x) for x in cmd_line])
        run_args = str_args

    if logger is not None:
        msg_ = f'[executing the command - (cwd={cwd} os={os.name})]'
        logger.debug(msg_)
        logger.debug('$ {}'.format(str_args))

    lines = []
    try:
        process = subprocess.Popen(run_args,
                                   env=env, cwd=cwd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,  # subprocess.PIPE,
                                   universal_newlines=True,
                                   startupinfo=startupinfo,
                                   shell=True,
                                   close_fds=True)

        while True:
            line = process.stdout.readline() if process.stdout is not None else ''
            if line == '' and process.poll() is not None:
                break
            if line:
                line = line.rstrip()
                if parser:
                    parser(line)
                if logger:
                    logger.debug(' ' + line)
                lines.append(line)

        return_code = process.returncode

        if process.stdout is not None:
            process.stdout.close()

        if logger:
            msg = '[returned code {} - {}]'.format(return_code, 'SUCCESS' if not return_code else 'FAILED')
            if return_code:
                logger.critical(msg)
            else:
                logger.debug(msg)
        if return_code:
            if logger and logger.getEffectiveLevel() > logging.DEBUG and lines:
                msg = '\n'.join(lines)
                logger.critical('-->\n$ ' + str_args + '\n' + msg + '')
                logger.critical('<--')
            raise RuntimeError(f'return code = {return_code}')

        return return_code, lines

    except (OSError, RuntimeError) as _exc:
        if logger and not isinstance(_exc, RuntimeError):
            msg = 'Unable to execute the command "{}"\n{}'.format(cmd_line, _exc)
            logger.error(msg)
        return -1, lines


def load_json_safe(path: Union[str, Path], *args, **kwargs) -> dict:
    """Load a JSON file and ignoring any single-line, multi-line comments and trailing commas"""

    single_line_comment = re.compile(r'("(?:(?=(\\?))\2.)*?")|(?:\/{2,}.*)')
    multi_line_comment = re.compile(r'("(?:(?=(\\?))\2.)*?")|(?:\/\*(?:(?!\*\/).)+\*\/)', flags=re.M | re.DOTALL)
    trailing_comma = re.compile(r',(?=\s*?[\}\]])')

    with open(path, 'r') as file_handle:
        unfiltered_json_string = file_handle.read()

    filtered_json_string = single_line_comment.sub(r'\1', unfiltered_json_string)
    filtered_json_string = multi_line_comment.sub(r'\1', filtered_json_string)
    filtered_json_string = trailing_comma.sub('', filtered_json_string)

    loaded_file = json.loads(filtered_json_string, *args, **kwargs)

    return loaded_file


class DictToObj:
    """Convert a dict to an object"""
    def __init__(self, in_dict: dict, name: Optional[str] = ''):
        self._obj_name = name.capitalize() if name else self.__class__.__name__
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
                setattr(self, key, [DictToObj(x, key) if isinstance(x, dict) else x for x in val])
            else:
                setattr(self, key, DictToObj(val, key) if isinstance(val, dict) else val)

    def __str__(self):
        msg = ', '.join([f'{key}={val}' for key, val in self.__dict__.items() if key != '_obj_name'])
        return f'{self._obj_name}({msg})'


class STMAiMetrics(NamedTuple):
    """Class to handle the main metrics"""
    ram: int = 0
    io: tuple = (0, 0)
    weights: int = 0
    macc: int = 0
    rt_ram: int = 0
    rt_flash: int = 0
    latency: float = 0.0


class STMAiTensorInfo(NamedTuple):
    """Class to handle the C-tensor info"""
    name: str = ''
    idx: int = 0
    shape: tuple = (0, 0, 0, 0)
    size: int = 0
    c_type: str = 'float'
    c_size: int = 0
    c_mem_pool: str = ''
    quantization: dict = {}


class STMAiModelInfo(NamedTuple):
    """Class to handle the C-model info"""
    name: str = ''
    type: str = ''
    format: str = 'float'
    stm_ai_version: STMAiVersion = STMAiVersion()
    c_name: str = 'network'
    series: str = 'generic'
    metrics: STMAiMetrics = STMAiMetrics()
    inputs: List[STMAiTensorInfo] = []
    outputs: List[STMAiTensorInfo] = []
