###################################################################################
#   Copyright (c) 2024 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Module implementing logging facilities
"""

import logging
import sys
from io import StringIO
from typing import List, Union, Optional, Any

from colorama import init, Fore, Style


__author__ = "GPM/AIS"
__copyright__ = "Copyright (c) 2024, STMicroelectronics"
__license__ = "Limited License Agreement - SLA0069"


def _attr_to_str(attr_desc, attr_val, indent=0):
    """Convert attr/value to string"""  # noqa: DAR101,DAR201
    post_ = 21 - len(attr_desc) - indent
    sep_ = ' : ' if attr_desc else '   '
    return ' ' * indent + str(attr_desc) + ' ' * post_ + sep_ + str(attr_val)


def h_bar_to_str(val, loc_max, glob_max, m_size=20):
    """Generate a str with a horizontal bar graph"""  # noqa: DAR101,DAR201
    nb_ = val / loc_max if loc_max else 0.0
    nb_ = int(nb_ * m_size)
    line = '|' + '|' * nb_
    line += ' ' * (m_size - nb_)
    if val and glob_max:
        nb_ = val * 100 / glob_max
    else:
        nb_ = 0.0
    line += '{:.1f}%'.format(nb_).rjust(7)
    return line


class LoggerWriter:
    """Handle the write operation of the log"""

    def __init__(self, write_fn=None, length=120, eol=False, indent=0):
        self._str = ''
        self._l = length
        self._indent = indent
        self._eol = eol
        if write_fn:
            self._w = lambda s: write_fn(s + ('\n' if self._eol else ''))
        else:
            self._w = None

    @property
    def ident(self):
        """Return indentation size"""
        # noqa: DAR101,DAR201
        return self._indent

    def _adjust_indent(self, indent):
        """Adjust indentation"""  # noqa: DAR101,DAR201
        return indent + self._indent if indent is not None else self._indent

    def __call__(self, _str, indent=None, end='\n'):
        """Callable method"""  # noqa: DAR101
        self.print(_str, indent, end)

    def h1(self, _str, indent=None):
        """Print header section"""  # noqa: DAR101
        # pylint: disable=C0103
        self.print(' ', indent)
        self.print(_str, indent)

    def prattr(self, _str, _val, indent=None, end='\n'):
        """Print an attribute value"""  # noqa: DAR101
        indent = self._adjust_indent(indent)
        if self._w:
            self._w(_attr_to_str(_str, _val, indent))
        self._str += '{}'.format(_attr_to_str(_str, _val, indent)) + end

    def psep(self, sep='-', indent=None, length=None, end='\n'):
        """Print a separator line"""  # noqa: DAR101
        indent = self._adjust_indent(indent)
        _len = length if length is not None else self._l
        if self._w:
            self._w(' ' * indent + ''.ljust(_len, sep))
        self._str += '{}'.format(' ' * indent + ''.ljust(_len, sep)) + end

    def print(self, _str, indent=None, end='\n'):  # noqa: T202
        """Print a simple string"""  # noqa: DAR101
        _str = str(_str)
        indent = self._adjust_indent(indent)
        bk_line = _str and _str[0] == '\n'
        _str = _str[1:] if bk_line else _str
        if self._w:
            if bk_line:
                self._w('\n')
            self._w(' ' * indent + '{}'.format(_str))
        if bk_line:
            self._str += end
        self._str += ' ' * indent + '{}'.format(_str) + end

    def append(self, _str, end='\n'):
        """Append a new line in the string buffer"""  # noqa: DAR101,DAR201
        _id = ' ' * self._indent if self._indent else ''
        if self._w:
            self._w('{}'.format(_id + str(_str)))
        self._str += '{}'.format(_id + str(_str)) + end

    def prow(self, fields, sizes, indent=None, end='\n'):
        """Print a row of a table"""  # noqa: DAR101
        indent = self._adjust_indent(indent)
        if len(fields) > len(sizes):
            return
        line = ''
        _p = 0
        for i, _f in enumerate(fields):
            _p += sizes[i]
            if i > 0:
                line = line[:-1] + ' '
            line += str(_f)
            line = line[:_p]
            line += ' ' * (_p - len(line))
        line = line[:-1]
        if self._w:
            self._w(' ' * indent + line)
        self._str += ' ' * indent + line + end

    def __str__(self):
        """Return the generated string buffer"""  # noqa: DAR201
        return self._str


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


def print_table(header, rows, pr_fn, colalign=None,
                title: str = None, sep: bool = False,
                tablefmt="simple_outline"):
    """."""

    from tabulate import tabulate

    res = tabulate(rows, headers=header, tablefmt=tablefmt,
                   colalign=colalign, disable_numparse=True)

    nline = ''
    if sep:
        pr_fn('')
    lines_ = res.splitlines()
    if tablefmt == 'simple':
        nline = lines_[1]
    if nline:
        pr_fn(nline)
    for line in lines_:
        pr_fn(line)
    if nline:
        pr_fn(nline)
    if title:
        pr_fn(' Table: ' + title)
    if sep:
        pr_fn('')


class IndentFormatter(logging.Formatter):
    """Default Log Formatter"""

    indent = 0
    inc = 0

    def __init__(self, format_str="%(levelname)s%(message)s"):
        super(IndentFormatter, self).__init__(fmt=format_str)

    def enable_inc(self, enable: bool = True):
        """."""
        self.inc = 3 if enable else 0

    def indent_msg(self, msg):
        """."""
        inc = 0
        if msg.startswith('->'):
            inc = self.inc
        if msg.startswith('<-'):
            self.indent -= self.inc
            self.indent = 0 if self.indent < 0 else self.indent
        if self.indent > 0:
            msg = ' ' * self.indent + msg
        self.indent += inc
        return msg


class ColorFormatter(IndentFormatter):
    """Color Formatter"""

    COLORS = {
        "WARNING": (Fore.LIGHTYELLOW_EX, 'W'),
        "ERROR": (Fore.RED + Style.BRIGHT, 'E'),
        "DEBUG": (Fore.CYAN, 'D'),
        "INFO": (Fore.GREEN, 'I'),
        "CRITICAL": (Fore.RED + Style.BRIGHT, 'C')
    }

    def format(self, record):
        """Format the specified record as text"""

        record.msg = self.indent_msg(str(record.msg))
        record.name = ''
        color, lname = self.COLORS.get(record.levelname, ('', ''))
        if color:
            if record.levelname != "INFO":
                record.levelname = color + '[' + lname + ']' + Style.RESET_ALL
                record.msg = color + ' ' + record.msg + Style.RESET_ALL
            else:
                record.levelname = ''
        return logging.Formatter.format(self, record)


class DefaultFormatter(IndentFormatter):
    """Default Formatter"""

    def format(self, record):
        """Format the specified record as text"""

        record.msg = self.indent_msg(str(record.msg))
        record.name = ''
        if record.levelname != "INFO":
            record.levelname = '[' + record.levelname[0] + ']'
        else:
            record.levelname = ''
        record.msg = ' ' + record.msg
        return logging.Formatter.format(self, record)


class FileFormatter(IndentFormatter):
    """File Formatter"""

    def format(self, record):
        """Format the specified record as text"""

        record.msg = self.indent_msg(str(record.msg))
        # return logging.Formatter.format(self, record)
        return super(FileFormatter, self).format(record)


class DefaultStrHandler(logging.StreamHandler):
    """Default handler"""

    def __init__(self, stream=None):
        """."""
        stream = sys.stdout if stream is None else stream
        super(DefaultStrHandler, self).__init__(stream)


def get_logger(name=None, level=logging.WARNING, color=False, filename=None):
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

    logger.setLevel(logging.NOTSET)

    if filename:
        fh = logging.FileHandler(filename, mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh_formatter = FileFormatter(format_str="[%(levelname).1s] %(message)s")
        fh_formatter.enable_inc()
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

    console = DefaultStrHandler()
    console.setLevel(level)
    if color:
        formatter = ColorFormatter()
    else:
        formatter = DefaultFormatter()
    formatter.enable_inc(filename is None)
    console.setFormatter(formatter)

    logger.addHandler(console)

    return logger


def get_print_fcts(cur_logger: logging.Logger,
                   logger: Optional[Union[str, logging.Logger, Any]] = None,
                   full: bool = False):
    """."""

    if isinstance(logger, str):
        logger_ = logging.getLogger(logger)
        print_fn = logger_.info
        print_deb_fn = cur_logger.debug
    elif logger is None:
        print_fn = cur_logger.info
        print_deb_fn = cur_logger.debug
    elif isinstance(logger, logging.Logger):
        print_fn = logger.info
        print_deb_fn = logger.debug
    elif callable(logger):
        print_fn = logger
        print_deb_fn = None if not full else logger

    if full:
        print_deb_fn = print_fn

    return print_fn, print_deb_fn
