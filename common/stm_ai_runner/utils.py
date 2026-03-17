###################################################################################
#   Copyright (c) 2021, 2024 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
ST AI runner - Utilities
"""

import sys
import logging
import re
import copy
from io import StringIO
from typing import Union, List


from colorama import init, Fore, Style


_LOGGER_NAME_ = 'STAI-RUNNER'
STMAI_RUNNER_LOGGER_NAME = _LOGGER_NAME_


def escape_ansi(line):
    """Remove ANSI character from string"""
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', str(line))


class IndentFormatter(logging.Formatter):
    """Default Log Formatter"""

    indent = 0
    inc = 0

    def __init__(self, format_str="%(levelname)s %(message)s"):
        super().__init__(fmt=format_str)

    def enable_inc(self, enable: bool = True):
        """."""
        self.inc = 3 if enable else 0

    def is_target_msg(self, msg):
        """."""
        return msg and msg.strip().startswith('[TARGET:')

    def indent_msg(self, msg):
        """."""
        inc = 0
        clean_msg_ = escape_ansi(msg)
        if clean_msg_.startswith('->'):
            inc = self.inc
        if clean_msg_.startswith('<-'):
            self.indent -= self.inc
            self.indent = 0 if self.indent < 0 else self.indent
        if self.indent > 0:
            msg = ' ' * self.indent + msg
        self.indent += inc
        return msg


class ColorFormatter(IndentFormatter):
    """Color Formatter"""

    COLORS = {
        "W": Fore.LIGHTYELLOW_EX,  # WARNING
        "E": Fore.RED + Style.BRIGHT,  # ERROR
        "D": Fore.CYAN,  # DEBUG
        "I": Fore.GREEN,  # INFO
        "C": Fore.RED,  # CRITICAL
        "T": Fore.MAGENTA  # TARGET.INFO
    }

    def __init__(self, with_prefix=False):
        self.with_prefix = with_prefix
        super().__init__()

    def format(self, record):
        """Update/format the specified record"""
        if hasattr(record, 'original_levelname'):
            lvl_name = record.original_levelname
            target_msg = record.target_msg
            msg = self.indent_msg(record.original_msg)
        else:
            lvl_name = record.levelname
            target_msg = self.is_target_msg(str(record.msg))
            msg = self.indent_msg(str(record.msg))
        record.msg = msg
        slvl_name_ = lvl_name[0]
        slvl_name_ = 'T' if (target_msg and slvl_name_ == 'I') else slvl_name_
        cls_name_ = (':' + record.name) if self.with_prefix else ''
        color = self.COLORS.get(slvl_name_, '')
        add_prefix = lvl_name != "INFO" or self.with_prefix
        if color:
            if slvl_name_ == 'T' or add_prefix:
                record.levelname = color + '[' + slvl_name_ + cls_name_ + ']' + Style.RESET_ALL
                record.msg = color + record.msg + Style.RESET_ALL
            else:
                record.levelname = ''
        return super().format(record)


class DefaultFormatter(IndentFormatter):
    """Default Formatter"""

    def __init__(self, with_prefix=False):
        self.with_prefix = with_prefix
        super().__init__()

    def format(self, record):
        """Update/format the specified record"""
        if hasattr(record, 'original_levelname'):
            lvl_name = record.original_levelname
            target_msg = record.target_msg
            msg = self.indent_msg(record.original_msg)
        else:
            lvl_name = record.levelname
            target_msg = self.is_target_msg(str(record.msg))
            msg = self.indent_msg(str(record.msg))
        record.msg = escape_ansi(msg)  # remove ANSI characters
        cls_name_ = (':' + record.name) if self.with_prefix else ''
        slvl_name_ = 'T' if target_msg else lvl_name[0]
        add_prefix = lvl_name != "INFO" or self.with_prefix
        if slvl_name_ == 'T' or add_prefix:
            record.levelname = '[' + slvl_name_ + cls_name_ + ']'
        else:
            record.levelname = ''
        return super().format(record)


class FileFormatter(IndentFormatter):
    """File Formatter"""

    def __init__(self, with_prefix=False):
        """Constructor"""
        self.with_prefix = with_prefix
        super().__init__()

    def format(self, record):
        """Update/format the specified record"""
        record.original_levelname = record.levelname
        record.target_msg = self.is_target_msg(str(record.msg))
        record.original_msg = self.indent_msg(str(record.msg))
        record.msg = escape_ansi(record.original_msg)
        cls_name_ = (':' + record.name) if self.with_prefix else ''
        slvl_name_ = 'T' if record.target_msg else record.levelname[0]
        record.levelname = '[' + slvl_name_ + cls_name_ + ']'
        return super().format(record)


class DefaultStrHandler(logging.StreamHandler):
    """Default handler"""

    def __init__(self, stream=None):
        """."""
        stream = sys.stdout if stream is None else stream
        super(DefaultStrHandler, self).__init__(stream)


def get_logger(name=None, level=logging.WARNING, color=True, filename=None, with_prefix=True):
    """Utility function to create a logger object"""

    logger = logging.getLogger(name)

    if logger.handlers and len(logger.handlers) == 2 and isinstance(logger.handlers[1], DefaultStrHandler):
        # w/ log file
        return logger
    elif logger.handlers and len(logger.handlers) == 1 and isinstance(logger.handlers[0], DefaultStrHandler):
        # wo/ log file
        return logger

    if color:
        init()

    if filename is not None:
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename, mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh_formatter = FileFormatter(with_prefix=with_prefix)
        fh_formatter.enable_inc()
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)
    else:
        logger.setLevel(level)

    console = DefaultStrHandler()
    console.setLevel(level)
    if color:
        formatter = ColorFormatter(with_prefix=with_prefix)
    else:
        formatter = DefaultFormatter(with_prefix=with_prefix)
    formatter.enable_inc(filename is None)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.propagate = False

    return logger


def get_log_level(logger: logging.Logger):
    """Return effective log level for console"""

    if logger.handlers and len(logger.handlers) == 2 and isinstance(logger.handlers[1], DefaultStrHandler):
        # w/ log file
        return logger.handlers[1].level
    elif logger.handlers and len(logger.handlers) == 1 and isinstance(logger.handlers[0], DefaultStrHandler):
        # wo/ log file
        return logger.handlers[0].level

    return logger.getEffectiveLevel()


def set_log_level(level: Union[str, int] = logging.DEBUG, logger: Union[logging.Logger, None] = None):
    """Set the log level of the module"""  # noqa: DAR101,DAR201,DAR401

    if isinstance(level, str):
        level = level.upper()
    level = logging.getLevelName(level)

    if logger is None:
        logger = get_logger(_LOGGER_NAME_)
    logger.setLevel(level)
    if logger.handlers:
        logger.handlers[0].setLevel(level)


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


def truncate_name(name: str, maxlen: int = 30):
    """Return a truncated string"""  # noqa: DAR101, DAR201
    maxlen = max(maxlen, 4)
    l_, r_ = (3, 1) if maxlen <= 12 else (12, 10)
    return (name[:maxlen - l_] + ".." + name[-r_:]) if maxlen < len(name) else name
