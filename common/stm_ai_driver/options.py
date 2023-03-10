###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI driver - Option manager
"""

import logging

from typing import Optional, List, Union, Any
from dataclasses import dataclass


from .utils import STMAiVersion, _LOGGER_NAME_


logger = logging.getLogger(_LOGGER_NAME_)


def _to_cli_arg(key: str, val: Any, vers: Union[str, STMAiVersion, None] = None, name='Options'):
    """Internal: Return key/val as a STM.AI CLI arg"""

    if key and key.startswith('_'):
        return ''

    vers_ = STMAiVersion(vers)
    opts_ = _COMPILE_OPTIONS_.copy()
    if vers_ > '7.2':
        opts_.update(_COMPILE_OPTIONS_7_3_0_)
    elif vers_ > '7.1':
        opts_.update(_COMPILE_OPTIONS_7_2_0_)
    arg = opts_.get(key, None)
    if arg is None and vers_.is_valid() and val:
        msg_ = f'{name}: the "{key}/{val}" option is not supported with {vers_}'
        logger.warning(msg_)
    if arg is None or val is None:
        return ''
    if key == 'extra':
        return ''
    if bool in arg[1] and isinstance(val, bool) and bool(val) != arg[0]:
        return '{}'.format(arg[2])
    if int in arg[1] and isinstance(val, int) and int(val) != arg[0]:
        return '{} {}'.format(arg[2], int(val))
    if str in arg[1] and isinstance(val, str) and val != arg[0]:
        return '{} {}'.format(arg[2], str(val))
    if type(val) in arg[1] and val != arg[0]:
        return '{} {}'.format(arg[2], str(val))
    return ''


_COMPILE_OPTIONS_ = {
    'allocate_inputs': (False, (bool,), '--allocate-inputs'),
    'allocate_outputs': (False, (bool,), '--allocate-outputs'),
    'dll': (False, (bool,), '--dll'),
    'compression': ('lossless', (str, int), '-c'),
    "split_weights": (False, (bool,), '--split-weights'),
    "no_onnx_io_transpose": (False, (bool,), '--no-onnx-io-transpose'),
    "no_onnx_optimize": (False, (bool,), '--no-onnx-optimize'),
    "verbosity": (1, (int,), '--verbosity'),
    "name": ('network', (str,), '--name'),
    'extra': ('', (str, list), ''),
}


_COMPILE_OPTIONS_7_2_0_ = {
    'quiet': (False, (bool,), '--quiet'),
}


_COMPILE_OPTIONS_7_3_0_ = {
    'quiet': (False, (bool,), '--quiet'),
    'optimization': ('default', (str,), '-O'),
}


@dataclass
class STMAiCompileOptions:
    """Class to handle the compilation options"""
    extra: Optional[Union[str, List[str], None]] = None
    dll: bool = False
    allocate_inputs: bool = False
    allocate_outputs: bool = False
    compression: Union[str, int, None] = None
    verbosity: int = 1
    split_weights: bool = False
    no_onnx_io_transpose: bool = False
    no_onnx_optimize: bool = False
    name: str = 'network'
    quiet: bool = False  # since 7.2
    optimization: Union[str, None] = None  # since 7.3
    _version: Union[str, STMAiVersion, None] = None

    def to_cli_args(self, vers: Union[str, STMAiVersion, None] = None):
        """Return simple str with the STM.AI CLI args"""
        self._version = vers
        msg_ = [_to_cli_arg(key, val, vers, self.__class__.__name__) for key, val in self.__dict__.items()]
        if self.extra:
            val = [self.extra] if isinstance(self.extra, str) else self.extra
            msg_.append(' '.join([str(v_) for v_ in val]))
        msg_ = [v_ for v_ in msg_ if v_]
        return ' '.join(msg_)

    def used_options(self):
        """Return used options"""
        return self.to_cli_args(self._version)

    def __str__(self):
        msg = ', '.join([f'{key}={val}' for key, val in self.__dict__.items()])
        return f'{self.__class__.__name__}({msg})'
