###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Utility to parse a map file (GCC-based)
"""

import logging
from os import path
import argparse
import re
import sys

from typing import Optional, List, Union

from common.stm32ai_local.utils import TableWriter


__title__ = 'Utility - Extract info from a GCC-map file'
__version__ = '1.6'
__author__ = 'STMicroelectronics'


# History
#
#   v1.0 - Initial version
#   v1.1 - rework the parse process
#        - adapte for 'relocatable' map file
#   v1.2 - add option to merge the TFLm object file in a simple module
#   v1.3 - add new tflm pattern to consider the eIQ map file
#   v1.4 - fix lib/module path with blank
#   v1.5 - create CReadAndParseGccMap object to use the script as a lib
#   v1.6 - improve parsing of the loaded modules
#
#   v2.x - TODO - add c++ support / demangling of symbol names
#
# Internals
#
# - memory conf. : dict
#       key         name
#       value       { 'origin':str, 'size':int, 'attr': str, 'used': int }
#
# - common symbols : dict
#       key         name
#       value       { 'size': str, 'module': str}
#
# - loaded objects (.a or .o) : dict
#       key         short name
#       value       { 'full_path':str, 'type':['normal'|'lib toolchain']  }
#
# - logical section : ordered list
#       { 'name': str,      name of the logical section
#         'addr': str,      base address
#         'size': int,      total size
#         'c_size': int,    cumulate size of the symbols
#         'fill': int       cumulate size of the pad (*fill*)
#         'symbols' : { key:name, value: {..} }
#        }
#
#   symbols: dict
#           key         name
#           value       { 'raw': list(str)
#                         'module': str             short name of the module
#                         'alias' : [str]           alias
#                       }
#

_TFLM_SRC_PATH = ['eiq/tensorflow-lite', 'Middlewares/tensorflow']

# Helper functions


class FileReader():
    """Helper class to read a txt file"""

    def __init__(self, f_name):
        self.f_name = f_name
        self.file = None
        self.pos = 0
        self.line = None

    def _close(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def __enter__(self):
        self.pos = 0
        self.file = open(self.f_name, 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def __iter__(self):
        if self.file is None:
            self.pos = 0
            self.file = open(self.f_name, 'r')
        return self

    def __next__(self):
        if self.file is None:
            raise StopIteration
        self.line = self.file.readline()
        self.line = self.line.rstrip() if self.line else None
        self.pos += 1
        if self.line is not None:
            return self.line
        self.file.close()
        self.file = None
        raise StopIteration

    def readline(self):
        """."""  # noqa: DAR101,DAR201
        self.line = self.file.readline()
        self.line = self.line.rstrip() if self.line else None
        self.pos += 1
        return self.line

    def reset(self):
        """."""  # noqa: DAR101,DAR201
        if self.file is not None:
            self.file.close()
            self.pos = 0
            self.file = open(self.f_name, 'r')

    def close(self):
        """."""
        self._close()


def _skip_line(line):
    """Return True is the line can be skipped"""  # noqa: DAR101,DAR201

    if not line:
        return True
    # if line.endswith('size before relaxing)'):
    #    return True
    items = line.split()
    if items[0].startswith('*('):
        return True
    # if items[0].startswith('0x'):
    #    return True
    if 'ALIGN' in items or 'ORIGIN' in items or 'LOADADDR' in items or 'PROVIDE' in items:
        return True

    return False


def _get_memory(memories, addr):
    """Return name of the associated memory descriptor"""  # noqa: DAR101,DAR201

    if isinstance(addr, str) and addr.startswith('0x'):
        addr = int(addr, 0)

    for key, mem in memories.items():
        m_addr = int(mem['origin'], 0)
        m_add_last = m_addr + mem['size'] - 1
        # if (addr >= m_addr) and (addr <= m_add_last):
        if m_addr <= addr <= m_add_last:
            return key

    return None


def _addr_to_str_32b(addr):
    """Return readable address (hex 32b format)"""  # noqa: DAR101,DAR201,DAR401

    if isinstance(addr, str):
        if addr.startswith('0x'):
            addr = int(addr, 0)
        else:
            return ''

    if addr > 0xffffffff:
        raise ValueError('Provided address is invalid 0x{:x}'.format(addr))

    return '0x{:08x}'.format(addr)


def _split_full_path(item, tflm_mode=False):
    """Split file path - path and file name"""  # noqa: DAR101,DAR201

    f_path = item.replace('\\', '/')
    if '(' in f_path:
        f_path = f_path.split('(')[0]
    s_name = f_path.split('/')[-1]
    f_path = path.normpath(f_path).replace('\\', '/')
    if tflm_mode and any([tag in f_path for tag in _TFLM_SRC_PATH]):
        s_name = 'tflite_micro.a'
    return f_path, s_name


def _to_std_section(name_sec, sym=None):
    """Return std section name -> text, rodata, data and bss"""  # noqa: DAR101,DAR201

    # if available symbol name is used
    if sym:
        if sym['raw'][0].startswith('.rodata'):
            return 'rodata'
        if sym['raw'][0].startswith('.bss'):
            return 'bss'
        if sym['raw'][0].startswith('.text'):
            return 'text'
        if sym['raw'][0].startswith('.data'):
            return 'data'

    # else sec name is used
    if name_sec in ('.ARM', '.data'):
        return 'data'
    elif name_sec == '.bss' or 'heap' in name_sec or 'stack' in name_sec or name_sec == '._sdram':
        return 'bss'
    elif name_sec == '.rodata':
        return 'rodata'
    else:
        return 'text'


def _get_std_section_size(module_name, all_sections):
    """Compute the size of each std section for a given module"""  # noqa: DAR101,DAR201

    results = {'nb_syms': 0, 'data': 0, 'rodata': 0, 'bss': 0, 'text': 0}

    for sec in all_sections:
        for _, sym in sec['symbols'].items():
            if sym['module'] == module_name:
                results['nb_syms'] += 1
                results[_to_std_section(sec['name'], sym)] += sym['size']

    return results


def _process_common_symbol(reader, section, commons, items, n_items, logger):

    symbol = None
    if items[0] == 'COMMON' and n_items[1] in commons:
        common = commons[n_items[1]]
        logger.debug('{}: [symbol] COMMON - {} {}'.format(reader.pos, n_items, common))
        if items[1] == n_items[0]:  # same address
            items[2] = common['size']
            symbol = 'common.' + n_items[1]
        else:  # create a symbol
            section['symbols']['common.' + n_items[1]] = {
                'raw': [items[0], items[1], common['size'], items[3]],
                'module': common['module'],
                'alias': [],
                'size': int(common['size'], 0),
            }
    return symbol


def _get_symbol_name(n_items):

    if len(n_items) == 4 and n_items[1] == 'vtable':
        return 'vtable.' + n_items[3]
    else:
        return n_items[1]


def _parse_symbol(reader, section, modules, commons, logger, tflm):
    """Parse the symbol description"""  # noqa: DAR101,DAR201,DAR401

    # Expected patterns:
    #
    #  UC0 - |<symbol> <addr> <size> <module>
    #  UC1 - |<symbol>
    #        |  <addr> <size> <module>
    #  UC2 - |<symbol>
    #        |  <addr> <size> <module>
    #        |  <addr> <symbol2>            symbol = symbol2
    #        |  <addr> <symbol3>            == addr -> alias
    #        ...
    #  UC3 - |<symbol>
    #        |  <addr> <size> <module>
    #        |  <addr> <symbol2>            symbol = symbol2
    #        |  <addr2> <symbol3>           != addr -> new symbol (COMMON)
    #        ...

    items = reader.line.split()
    r_pos = reader.pos
    symbol = None
    alias = []
    cont = 0

    # if section['name'] == '.rodata':
    #    debug = True

    if items[0].startswith('0x'):
        return 0

    if '*fill*' in reader.line:
        section['fill'] += int(items[2], 0)
        msg_ = '{}: [symbol] "*fill*" in section "{}", size={} {}'.format(r_pos, section['name'],
                                                                          items[2], section['fill'])
        logger.debug(msg_)
        return 0

    if len(items) == 1:  # UCn > 0
        next(reader)
        n_items = reader.line.split()
        if n_items[0].startswith('0x'):
            items.extend(n_items)
        else:
            logger.warning('W:{}: enable to parse the symbol {}'.format(r_pos, items[0]))
            return 1  # current line is preserved

    next(reader)
    n_items = reader.line.split()
    while n_items and n_items[0].startswith('0x') and not _skip_line(reader.line):
        if reader.line.endswith('size before relaxing)'):
            section['relaxing_size'] += (int(n_items[0], 0) - int(items[2], 0))
            msg_ = '{}: [symbol] size before relaxing size {} -> {} ({})'.format(r_pos, n_items[0], items[2],
                                                                                 section['relaxing_size'])
            logger.debug(msg_)
            next(reader)
            n_items = reader.line.split()
            continue

        res = _process_common_symbol(reader, section, commons, items, n_items, logger)
        symbol = res if not symbol else symbol
        if not symbol and n_items[0] == items[1]:  # UC2 or UC3
            symbol = _get_symbol_name(n_items)
        else:
            alias.append(n_items[1])

        next(reader)
        n_items = reader.line.split()

    cont = 1

    if len(items) < 4 or not items[2].startswith('0x'):
        logger.warning('W:{}: symbol {} is skipped from section {}'.format(r_pos, items, section['name']))

    else:
        # section, symbol, items[] = ['name', 'address', 'size', 'module', ...]
        if symbol is None:
            if items[0].startswith(section['name'] + '.'):
                symbol = items[0][len(section['name']) + 1:]
            else:
                symbol = items[0]
        section['c_size'] += int(items[2], 0)
        _, short_name = _split_full_path(' '.join(items[3:]), tflm)
        if short_name not in modules and 'linker stubs' in reader.line:
            logger.warning('{}: -> unable to find the module {} - {}'.format(r_pos, short_name, items))
        else:
            if symbol in section['symbols']:
                symbol += '.' + str(r_pos)
            section['symbols'][symbol] = {
                'raw': items,
                'module': short_name,
                'alias': alias,
                'size': int(items[2], 0),
            }
        logger.debug('{}: [symbol] "{}" in section "{}", size={}, {} ({})'.format(r_pos, symbol,
                                                                                  section['name'],
                                                                                  items[2], short_name,
                                                                                  section['c_size']))

    return cont


class CReadAndParseGccMap():
    """Main class to parse a GCC-map file"""  # noqa: DAR101,DAR201,DAR401

    def __init__(self, map_file: str, debug: bool = False,
                 tflm: bool = False, logger: Optional[Union[logging.Logger, None]] = None):

        if not logger:
            logger = logging.getLogger('PARSE-GCC-MAP')
            logger.setLevel(logging.INFO)

        self._logger = logger
        self._tflm = tflm
        self._map_file = map_file

        self._logger.debug('')
        self._logger.debug('Parsing the map file: "%s"', map_file)

        self._commons = {}  # type: dict
        self._memories = {}  # type: dict
        self._modules = {}  # type: dict
        self._sections = []  # type: list
        self._ordered_modules = {}  # type: dict

        if not path.exists(map_file):
            raise RuntimeError(f'Invalid filepath {map_file}')

        self._parse(debug=debug)

    def _parse(self, debug: bool = False):
        """Parse the map file"""  # noqa: DAR101,DAR201,DAR401

        parsers = [
            self._parser_init,
            self._parser_common,
            self._parser_memory_configuration,
            self._parser_linker_and_memory_map,
            self._parser_final,
        ]

        cur_lvl = self._logger.getEffectiveLevel()
        if cur_lvl >= logging.DEBUG and not debug:
            self._logger.setLevel(logging.INFO)

        pars_idx = 0
        with FileReader(self._map_file) as reader:
            for _ in reader:
                if parsers[pars_idx] is not None:
                    if parsers[pars_idx](reader):
                        pars_idx += 1

        for key, module in self._modules.items():
            res = _get_std_section_size(key, self._sections)
            module.update(res)

        # add SYSTEM/dummy modules for stack/heap and *fill*
        extra = {
            '*FILL*': {'nb_syms': 0, 'data': 0, 'rodata': 0, 'bss': 0, 'text': 0},
            '*HEAP_STACK*': {'nb_syms': 0, 'data': 0, 'rodata': 0, 'bss': 0, 'text': 0}
        }
        for sec in self._sections:
            if sec['fill']:
                if 'heap' not in sec['name'] and 'stack' not in sec['name']:
                    ref = '*FILL*'
                else:
                    ref = '*HEAP_STACK*'
                extra[ref][_to_std_section(sec['name'])] += sec['fill']
                extra[ref]['nb_syms'] += 1

        # ordered the modules
        ordered_mod_ = sorted(self._modules.items(),
                              key=lambda item: item[1].get('text') + item[1].get('rodata'),
                              reverse=True)
        self._ordered_modules = dict(ordered_mod_)  # {k: v for k, v in ordered_mod_}
        self._ordered_modules.update(extra)

        self._logger.setLevel(cur_lvl)

    def _parser_init(self, reader):
        """Initial step to find the expected first line"""  # noqa: DAR101,DAR201,DAR401

        if reader.line.startswith('Archive member included to satisfy reference by file (symbol)'):
            return 1
        else:
            self._logger.error('%d: %s', reader.pos, reader.line)
            raise RuntimeError("Expected first line not found")

    def _parser_final(self, reader):
        """Final step to close the parser"""  # noqa: DAR101,DAR201,DAR401

        self._logger.debug('parsing done... %d', reader.pos)
        reader.close()
        return 0

    def _parser_common(self, reader):
        """Parser to analyze the common symbols"""  # noqa: DAR101,DAR201,DAR401

        if not reader.line.startswith('Allocating common symbols'):
            if reader.line.startswith('Discarded input sections'):
                self._logger.debug('"Allocating common symbols" section not found')
                return 1
            return 0

        self._logger.debug('parsing "Allocating common symbols" section... %d', reader.pos)

        next(reader)
        if 'Common symbol' not in reader.line or 'size' not in reader.line:
            raise RuntimeError(f'Invalid syntax {reader.line}')

        next(reader)
        next(reader)
        while reader.line:
            items = reader.line.split()
            r_pos = reader.pos
            if len(items) == 1:
                next(reader)
                n_items = reader.line.split()
                items.extend(n_items)
            msg_ = f'{r_pos}: common - {items}'
            self._logger.debug(msg_)
            _, short_name = _split_full_path(' '.join(items[2]), self._tflm)
            if items[0] in self._commons:
                raise ValueError('Common symbol already registered')
            else:
                self._commons[items[0]] = {
                    'module': short_name,
                    'size': items[1],
                }
            next(reader)

        self._logger.debug(' found %d common symbols', len(self._commons))
        return 1

    def _parser_memory_configuration(self, reader):
        """Parser to read the memory configuration section"""  # noqa: DAR101,DAR201,DAR401

        if not reader.line.startswith('Memory Configuration'):
            return 0

        self._logger.debug('parsing "Memory Configuration" section... %d', reader.pos)

        next(reader)  # remove empty line

        next(reader)
        if 'Name' not in reader.line or 'Origin' not in reader.line:
            raise RuntimeError(f'Invalid syntax {reader.line}')

        next(reader)
        while reader.line:
            self._logger.debug('%d: %s', reader.pos, reader.line)
            items = reader.line.split()
            self._memories[items[0]] = {
                'origin': items[1],
                'size': int(items[2], 0),
                'attr': items[3] if len(items) > 3 else '',
                'used': 0,
            }
            next(reader)

        self._logger.debug(' found %d memory descriptions', len(self._memories))

        if '*default*' not in self._memories:
            self._memories['*default*'] = {
                'origin': '0x0',
                'size': 0xFFFFFFFF,
                'attr': '',
                'used': 0,
            }

        return 1

    def _parse_loaded_modules(self, reader, in_file):
        """Parse loaded modules"""  # noqa: DAR101,DAR201,DAR401

        cur_line = reader.pos
        if in_file:
            while not reader.line.startswith('LOAD'):
                next(reader)

        def is_valid_module_line(line):
            if line.startswith('LOAD') or line.startswith('START GROUP') or line.startswith('END GROUP'):
                return True
            return False

        while is_valid_module_line(reader.line):
            if reader.line.startswith('LOAD'):
                items = reader.line.split()
                f_type = 'normal'
                object_path = ' '.join(items[1:])
                full_path, short_name = _split_full_path(object_path, self._tflm)
                if 'arm-none-eabi' in object_path:
                    f_type = 'lib toolchain'
                elif '.a' in short_name:
                    f_type = 'lib'
                msg_ = '{}: [module] {} (type={})'.format(reader.pos, short_name, f_type)
                self._logger.debug(msg_)
                if short_name in self._modules and 'toolchain' not in f_type:
                    self._logger.warning("module already registered %s %s", short_name, self._modules[short_name])
                self._modules[short_name] = {'full_path': full_path, 'type': f_type}
            next(reader)

        self._logger.debug(' found %d modules  ', len(self._modules))

        if in_file:
            reader.reset()
            while reader.pos != cur_line:
                next(reader)

    def _parser_linker_and_memory_map(self, reader):
        """Parser to read the Linker script and memory map section"""  # noqa: DAR101,DAR201,DAR401

        if not reader.line.startswith('Linker script and memory map'):
            return 0

        self._logger.debug('parsing "Linker script and memory map" section... %d', reader.pos)

        next(reader)  # remove empty line

        # Parsing loaded modules?

        next(reader)
        self._parse_loaded_modules(reader, not reader.line.startswith('LOAD'))

        # Parsing sections and symbols

        cur_section = None
        while not reader.line.startswith('/DISCARD/') and not reader.line.startswith('OUTPUT('):
            if _skip_line(reader.line):
                self._logger.debug('%d: -> line is skipped "%s"', reader.pos, reader.line)
                next(reader)
                continue
            if reader.line.startswith('.'):
                r_pos = reader.pos
                items = reader.line.split()
                if len(items) == 1:
                    next(reader)
                    if reader.line.strip().startswith('0x'):
                        items.extend(reader.line.split())
                    else:
                        self._logger.warning('%d: sub-section "%s" has been skipped', r_pos, str(items[0]))
                        cur_section = None
                        continue
                self._logger.debug('%d: [section] %s', r_pos, items)
                load_addr = ''
                if len(items) > 5 and items[3] == 'load':
                    # if 'bss' not in items[0] and 'stack' not in items[0] and 'heap' not in items[0]:
                    load_addr = items[5]
                if len(items) > 2 and '0x' in items[1]:
                    self._sections.append({
                        'name': items[0],
                        'addr': items[1],
                        'size': int(items[2], 0),
                        'c_size': 0,
                        'relaxing_size': 0,
                        'fill': 0,
                        'memory': _get_memory(self._memories, items[1]),
                        'load address': load_addr,
                        'symbols': dict()
                    })
                    cur_section = self._sections[-1]
                    self._memories[_get_memory(self._memories, items[1])]['used'] += int(items[2], 0)
                    if load_addr:
                        self._memories[_get_memory(self._memories, load_addr)]['used'] += int(items[2], 0)
            elif cur_section is None:
                if reader.line:
                    self._logger.debug('%d: -> no section is defined "%s"', reader.pos, reader.line)
            else:
                if not reader.line.startswith(' '):
                    if not reader.line.startswith('LOAD') and ' GROUP' not in reader.line:
                        self._logger.warning('%d: line is invalid - %s', reader.pos, reader.line)
                else:
                    if _parse_symbol(reader, cur_section, self._modules, self._commons, self._logger, self._tflm):
                        continue

            next(reader)

        self._logger.debug(' found %d sections  ', len(self._sections))
        nb_symbols = 0
        for sec in self._sections:
            nb_symbols += len(sec['symbols'])
        self._logger.debug(' found %d symbols  ', nb_symbols)

        return 1

    def _show_memories(self, indent: int = 1):
        """Display the physical memories"""  # noqa: DAR101,DAR201,DAR401

        table = TableWriter(indent=indent, csep='-')
        # table.set_title('Memory definition')
        table.set_header(['memory', 'size', 'org', 'used', 'usage (%)'])

        for key, mem in self._memories.items():
            if key != '*default*':
                row = [key]
                row.append('{:,d}'.format(mem['size']))
                row.append(_addr_to_str_32b(mem['origin']))
                row.append('{:,d}'.format(mem['used']))
                row.append('{:.2f}%'.format(mem['used'] * 100 / mem['size']))
                table.add_row(row)

        res = table.getvalue(fmt=' >>>>', endline=True)
        for line in res.splitlines():
            self._logger.info(line)
        table.close()

    def _show_sections(self, indent: int = 1):
        """Display the sections"""  # noqa: DAR101,DAR201,DAR401

        table = TableWriter(indent=indent)
        # table.set_title('Memory sections')
        table.set_header(['section', 'size', 'addr', '*fill*', 'diff', 'memory'])

        text_ = data_ = bss_ = total_ = 0
        for sec in self._sections:
            row = [sec['name']]
            row.append('{:,d}'.format(sec['size']))
            row.append('{:s}'.format(_addr_to_str_32b(sec['addr'])))
            row.append('{}'.format(sec['fill']))
            row.append('{:,d}'.format(sec['size'] - (sec['c_size'] + sec['fill'])))
            row.append('{}'.format(sec['memory']))
            table.add_row(row)
            total_ += sec['size']
            if sec['name'] == '.data' or sec['name'] == '.ARM' or sec['name'] == '.fini_array':
                data_ += sec['size']
            elif sec['name'] == '.bss' or 'heap' in sec['name'] or 'stack' in sec['name'] or sec['name'] == '._sdram':
                bss_ += sec['size']
            else:
                text_ += sec['size']
        table.add_note('text={} data={} bss={} total={}'.format(text_, data_, bss_, total_))

        res = table.getvalue(fmt=' >>>>>', endline=True)
        for line in res.splitlines():
            self._logger.info(line)
        table.close()

    def _show_modules(self, indent: int = 1):
        """Display the modules"""  # noqa: DAR101,DAR201,DAR401

        table = TableWriter(indent=indent)
        # table.set_title('Modules')
        table.set_header(['module', 'text', 'rodata', 'data', 'bss'])

        res = self.get_info_modules()

        for module in res['modules']:
            row = [module['name']]
            row.append('{:,d}'.format(module['text']))
            row.append('{:,d}'.format(module['rodata']))
            row.append('{:,d}'.format(module['data']))
            row.append('{:,d}'.format(module['bss']))
            table.add_row(row)

        table.add_separator()
        val_ = res['all']
        text, rodata, data, bss = val_['text'], val_['rodata'], val_['data'], val_['bss']
        table.add_row(['total', f'{text:,d}', f'{rodata:,d}', f'{data:,d}', f'{bss:,d}'])
        table.add_note('text={} data={} bss={}'.format(text + rodata, data, bss))

        res = table.getvalue(fmt=' >>>>', endline=True)
        for line in res.splitlines():
            self._logger.info(line)
        table.close()

    def summary(self, indent: int = 1):
        """Display summary of the parsed file"""  # noqa: DAR101,DAR201,DAR401
        self._show_memories(indent)
        self._show_sections(indent)
        self._show_modules(indent)

    def get_info_modules(self, filters=None, excludes=None):
        """Return text/rodata/data/bss section size"""  # noqa: DAR101,DAR201,DAR401

        res = {'modules': []}

        if filters and isinstance(filters, str):
            filters = [filters]

        def _is_module(filters, key):
            for fil_ in filters:
                pcomp_ = re.compile(fil_, re.IGNORECASE)
                if pcomp_.search(key):
                    return True
            return False

        text_, rodata_, data_, bss_ = 0, 0, 0, 0
        f_text_, f_rodata_, f_data_, f_bss_ = 0, 0, 0, 0

        for key, module in self._ordered_modules.items():
            text_ += module['text']
            rodata_ += module['rodata']
            data_ += module['data']
            bss_ += module['bss']

            if filters is None or _is_module(filters, key):
                if excludes and _is_module(excludes, key):
                    continue

                item = {
                    'name': key,
                    'text': module['text'],
                    'rodata': module['rodata'],
                    'data': module['data'],
                    'bss': module['bss'],
                    'file_path': module.get('full_path', ''),
                    'nb_syms': module['nb_syms']
                }

                res['modules'].append(item)

                f_text_ += module['text']
                f_rodata_ += module['rodata']
                f_data_ += module['data']
                f_bss_ += module['bss']

        res['filtered'] = {'text': f_text_, 'rodata': f_rodata_, 'data': f_data_, 'bss': f_bss_}
        res['all'] = {'text': text_, 'rodata': rodata_, 'data': data_, 'bss': bss_}
        res['filters'] = filters

        return res

    def summary_modules(self, filtered=None, indent: int = 1):
        """Display the modules"""  # noqa: DAR101,DAR201,DAR401

        if not filtered:
            self._show_modules()
            return

        if not isinstance(filtered, dict) or 'modules' not in filtered:
            return

        table = TableWriter(indent=indent)
        table.set_title('filters = {}'.format(filtered['filters']))
        table.set_header(['module', 'text', 'rodata', 'data', 'bss'])

        for module in filtered['modules']:
            sizes = [module['text'], module['rodata'], module['data'], module['bss']]
            fields = [module['name'], *['{:,d}'.format(val) for val in sizes]]
            table.add_row(fields)
        table.add_separator()

        if filtered['filters']:
            module = filtered['filtered']
        else:
            module = filtered['all']
        rt_total = [module['text'], module['rodata'], module['data'], module['bss']]
        fields = ['total', *['{:,d}'.format(val) for val in rt_total]]
        table.add_row(fields)

        res = table.getvalue(fmt=' >>>>', endline=False)
        for line in res.splitlines():
            self._logger.info(line)
        table.close()

    def show_symbols_by_module(self, filters=None, indent: int = 1):
        """Display symbol by modules"""  # noqa: DAR101,DAR201,DAR401
        if filters is None:
            return

        def _is_module(filters, key):
            for fil_ in filters:
                pcomp_ = re.compile(fil_, re.IGNORECASE)
                if pcomp_.search(key):
                    return True
            return False

        table = TableWriter(indent=indent, csep='-')
        table.set_title('Symbol size - filters = {}'.format(filters))
        table.set_header(['module', 'section', 'symbol', 'size'])

        for sec in self._sections:
            for key, sym in sec['symbols'].items():
                if _is_module(filters, sym['module']):
                    fields_ = [sym['module'], sec['name'], key, sym['size']]
                    table.add_row(fields_)

        res = table.getvalue(fmt='..>>', endline=False)
        for line in res.splitlines():
            self._logger.info(line)
        table.close()


def read_map_file(
        map_file: str,
        logger: logging.Logger,
        filters: Optional[List[str]] = None,
        symbols: bool = False,
        tflm: bool = False,
        debug: bool = False):
    """."""  # noqa: DAR101,DAR201,DAR401

    res = {}

    msg_ = f'Options: tflm={tflm} filters={filters}'
    logger.info(msg_)

    parser = CReadAndParseGccMap(map_file, debug=debug, tflm=tflm, logger=logger)
    parser.summary()

    if filters:
        res = parser.get_info_modules(filters=filters)
        parser.summary_modules(filtered=res)
        if symbols:
            parser.show_symbols_by_module(filters)

    return res


def main():
    """Script entry point."""  # noqa: DAR101,DAR201,DAR401

    class CustomFormatter(logging.Formatter):
        """Custom Formatter"""

        def format(self, record):
            if record.levelno == logging.INFO:
                log_fmt = '%(message)s'
            else:
                # log_fmt = '%(name)s:%(levelname)s:%(filename)s:%(lineno)d - %(message)s'
                log_fmt = '%(name)s:%(levelname)s:%(lineno)d - %(message)s'
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    parser = argparse.ArgumentParser(description='{} v{}'.format(__title__, __version__))

    parser.add_argument('map', metavar='FILE', type=str, help='map file')

    parser.add_argument('-m', '--module', type=str,
                        nargs='?', action='append', help='pattern to select the module (.o or .a)', default=None)
    parser.add_argument('-s', '--symbols', action='store_const', const=1,
                        help='shows the symbols of the selected modules')

    parser.add_argument('--verbosity', '-v',
                        nargs='?', const=1, type=int, choices=range(0, 3),
                        default=1, help="set verbosity level")

    parser.add_argument('--debug', action='store_const', const=1,
                        help='Enable internal log (DEBUG PURPOSE)')

    parser.add_argument('--tflm', action='store_const', const=1,
                        help='Merge the TFLm files (*.o) in a simple module (tflite_micro.a)')

    args = parser.parse_args()

    level = logging.WARNING
    if args.debug:
        level = logging.DEBUG
    elif args.verbosity > 0:
        level = logging.INFO

    logger = logging.getLogger('PARSE-MAP')
    logger.setLevel(level)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    formatter = CustomFormatter()
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info('Parsing the file %s %s', args.map, args.module)

    if not path.exists(args.map):
        raise RuntimeError(f'Invalid filepath {args.map}')

    modules = None
    if args.module:
        modules = args.module
        args.module = args.module[0]

    read_map_file(args.map, debug=args.debug, tflm=args.tflm,
                  filters=modules, logger=logger,
                  symbols=args.symbols)


if __name__ == '__main__':
    main()
