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
from io import StringIO
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
STMAIC_DEBUG_ENV = 'STMAIC_DEBUG'


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
            _mess = f'{self.mess}'
        else:
            _mess = type(self).__doc__.split('\n', maxsplit=1)[0]
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


def get_logger(name=_LOGGER_NAME_, level=logging.WARNING, color=False):
    """Utility function to create a logger object"""
    # setting default value to color=False to avoid unwanted characters in terminal

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
        color_formatter = ColorFormatter(fmt="%(levelname)s %(message)s")
        console.setFormatter(color_formatter)
    else:
        formatter = logging.Formatter(fmt='%(message)s')
        console.setFormatter(formatter)
    logger.addHandler(console)
    logger.propagate = False

    return logger


def set_log_level(level: Union[str, int] = logging.DEBUG):
    """Set the log level of the module"""

    if os.environ.get(STMAIC_DEBUG_ENV, None):
        level = logging.DEBUG

    if isinstance(level, str):
        level = level.upper()
    level = logging.getLevelName(level)

    logger = get_logger(_LOGGER_NAME_)
    logger.setLevel(level)
    logger.handlers[0].setLevel(level)


def run_shell_cmd(
        cmd_line: Union[str, List[str]],
        logger: Optional[logging.Logger] = None,
        env: Optional[dict] = None,
        cwd: Optional[str] = None,
        parser=None,
        assert_on_error: bool = False) -> Tuple[int, List[str]]:
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

        if logger is not None:
            msg = '[returned code = {} - {}]'.format(return_code, 'SUCCESS' if not return_code else 'FAILED')
            if return_code:
                logger.warning(msg)
            else:
                logger.debug(msg)

        if return_code:
            lines.insert(0, '$ args: {}'.format(str_args))
            lines.insert(0, '$ cwd:  {}'.format(str(cwd)))
            if assert_on_error:
                raise RuntimeError('invalid command ' + '\"{}\"'.format(str_args))
            for line in lines:
                logger.warning(line)

        return return_code, lines

    except (OSError, ValueError, FileNotFoundError, RuntimeError) as excep_:
        process.kill()
        if isinstance(excep_, RuntimeError) and assert_on_error:
            raise excep_
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


class TableWriter(StringIO):
    """Pretty-print tabular data (table form)"""

    N_SPACE = 2

    def __init__(self, indent: int = 0, csep: str = ' '):
        """Create the Table instance"""  # noqa: DAR101,DAR201
        self._header = []  # type: List[str]
        self._notes = []  # type: List[str]
        self._datas = []  # type: List[Union[List[str], str]]
        self._title = ''  # type: str
        self._fmt = ''  # type: str
        self._sizes = []  # type: List[int]
        self._indent = int(max(indent, 0))
        self._csep = csep
        super(TableWriter, self).__init__()

    def set_header(self, items: Union[List[str], str]):
        """Set the name of the columns"""  # noqa: DAR101,DAR201
        items = self._update_sizes(items)
        self._header = items

    def set_title(self, title: str):
        """Set the title (optional)"""  # noqa: DAR101,DAR201
        self._title = title

    def set_fmt(self, fmt: str):
        """Set format description (optional)"""  # noqa: DAR101,DAR201
        self._fmt = fmt

    def add_note(self, note: str):
        """Add a note (footer position)"""  # noqa: DAR101,DAR201
        self._notes.append(note)

    def add_row(self, items: Union[List[str], str]):
        """Add a row (list of item)"""  # noqa: DAR101,DAR201
        items = self._update_sizes(items)
        self._datas.append(items)

    def add_separator(self, value: str = '-'):
        """Add a separtor (line)"""  # noqa: DAR101,DAR201
        self._datas.append(value)

    def _update_sizes(self, items: Union[List[str], str]) -> List[str]:
        """Update the column sizes"""  # noqa: DAR101,DAR201,DAR401
        items = [items] if isinstance(items, str) else items
        if not self._sizes:
            self._sizes = [len(str(item)) + TableWriter.N_SPACE for item in items]
        else:
            if len(items) > len(self._sizes):
                raise ValueError('Size of the provided row is invalid')
            for i, item in enumerate(items):
                self._sizes[i] = max(len(str(item)) + TableWriter.N_SPACE, self._sizes[i])
        return items

    def _write_row(self, items: List[str], fmt):
        """Create a formated row"""  # noqa: DAR101,DAR201
        nfmt = ['.'] * len(self._sizes)
        for i, val in enumerate(fmt):
            if i < len(nfmt):
                nfmt[i] = val
        row = ''
        for i, item in enumerate(items):
            sup = self._sizes[i] - len(str(item))
            if nfmt[i] == '>':
                row += ' ' * sup + str(item) + ' ' * len(self._csep)
            else:
                row += str(item) + ' ' * sup + ' ' * len(self._csep)
        self.write(row)

    def _write_separator(self, val: str):
        """Create a formatted separator"""  # noqa: DAR101,DAR201
        row = ''
        for size in self._sizes:
            row += val * size + self._csep
        self.write(row)

    def write(self, msg: str, newline: str = '\n'):
        """Write fct"""  # noqa: DAR101,DAR201
        super(TableWriter, self).write(' ' * self._indent + msg + newline)

    def getvalue(self, fmt: str = '', endline: bool = False):
        """Buid and return the formatted table"""  # noqa: DAR101,DAR201

        fmt = fmt if fmt else self._fmt

        self.write('')
        if self._title:
            self.write(self._title)
            self._write_separator('-')
        if self._header:
            self._write_row(self._header, fmt)
            self._write_separator('-')
        for data in self._datas:
            if isinstance(data, str):
                self._write_separator(data)
            else:
                self._write_row(data, fmt)
        if endline or self._notes:
            self._write_separator('-')
        for note in self._notes:
            self.write(note)
        buff = super(TableWriter, self).getvalue()
        return buff

    def __str__(self):
        return self.getvalue()


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
