###################################################################################
#   Copyright (c) 2024 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Module including exceptions definition
"""


_ERROR_INDEX_CLI = 100
_ERROR_INDEX_PP = 600


class ErrorException(Exception):
    """Base class for ST.AI exceptions"""
    error = 0
    idx = 0

    def __init__(self, mess=None):
        self.mess = mess
        super(ErrorException, self).__init__(mess)

    @property
    def code(self):  # pylint: disable=C0116
        return self.error + self.idx

    def __str__(self):
        _mess = ''
        if self.mess:
            _mess = '{}'.format(self.mess)
        else:
            _mess = '{}'.format(type(self).__doc__.split('\n')[0].strip())
        _msg = 'E{:03d}({}): {}'.format(self.code, type(self).__name__, _mess)
        return _msg


class RelocError(ErrorException):
    """Reloc error"""
    error = _ERROR_INDEX_PP


class RelocPPError(RelocError):
    """Reloc PP error"""
    idx = 1


class RelocPostProcessError(RelocError):
    """Reloc PP error"""
    idx = 1


class ElfPostProcessError(RelocError):
    """Elf PP error"""
    idx = 2


class BinaryHeaderError(RelocError):
    """Binary Header error"""
    idx = 3


class PrepareNetworkError(RelocError):
    """Prepare C-file error"""
    idx = 4


class ParserNetworkError(RelocError):
    """Parser C-file error"""
    idx = 5
    
class ParserJsonError(RelocError):
    """Parser C-file error"""
    idx = 6
