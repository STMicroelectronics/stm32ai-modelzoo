###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI runner - Common helper services to manage the STM.AI type
"""

import ctypes as ct
from abc import ABC, abstractmethod
from typing import Dict

import numpy as np


RT_ST_AI_NAME = 'ST.AI'


def stm_ai_error_to_str(err_code, err_type):
    """
    Return a human readable description of the ai run-time error

    see <AICore>::EmbedNets git (src/api/ai_platform.h file)

    Parameters
    ----------
    err_code
        stm.ai error code
    err_type
        stm.ai error err_type

    Returns
    -------
    str
        human readable description of the error

    """

    type_switcher = {
        0x00: 'None',
        0x01: 'Tools Platform Api Mismatch',
        0x02: 'Types Mismatch',
        0x10: 'Invalid handle',
        0x11: 'Invalid State',
        0x12: 'Invalid Input',
        0x13: 'Invalid Output',
        0x14: 'Invalid Param',
        0x15: 'Invalid Signature',
        0x16: 'Invalid Size',
        0x17: 'Invalid Value',
        0x30: 'Init Failed',
        0x31: 'Allocation Failed',
        0x32: 'Deallocation Failed',
        0x33: 'Create Failed'
    }

    code_switcher = {
        0x0000: 'None',
        0x0010: 'Network',
        0x0011: 'Network Params',
        0x0012: 'Network Weights',
        0x0013: 'Network Activations',
        0x0014: 'Layer',
        0x0015: 'Tensor',
        0x0016: 'Array',
        0x0017: 'Invalid Ptr',
        0x0018: 'Invalid Size',
        0x0019: 'Invalid Format',
        0x0020: 'Out-Of-Range',
        0x0021: 'Invalid Batch',
        0x0030: 'Missed Init',
        0x0040: 'In Use',
        0x0041: 'Code Lock',
    }

    desc_ = 'type="{}"(0x{:x})'.format(type_switcher.get(err_type, str(err_type)), err_type)
    desc_ += ', code="{}"(0x{:x})'.format(code_switcher.get(err_code, str(err_code)), err_code)

    return desc_


def stm_ai_node_type_to_str(op_type_id, with_id=True):
    """  # noqa: DAR005
    Return a human readable description of a c-node

    see <AICore>::EmbedNets git (src/layers/layers_list.h file)

    Parameters
    ----------
    op_type_id
        stm.ai operator id
    with_id:
        add numerical value in the description

    Returns
    -------
    str
        human readable description of the c-node
    """

    base = 0x100  # stateless operator
    base_2 = 0x180  # stateful operator
    op_type_id = op_type_id & 0xFFFF
    ls_switcher = {
        0: 'Output',
        base: 'Base',
        base + 1: 'Add',
        base + 2: 'BN',
        base + 3: 'Conv2D',
        base + 4: 'Dense',
        base + 6: 'LRN',
        base + 7: 'NL',
        base + 8: 'Norm',
        base + 9: 'Conv2dPool',
        base + 10: 'Transpose',
        base + 11: 'Pool',
        base + 12: 'Softmax',
        base + 13: 'Split',
        base + 14: 'TimeDelay',
        base + 15: 'TimeDistributed',
        base + 16: 'Concat',
        base + 17: 'GEMM',
        base + 18: 'Upsample',
        base + 19: 'Eltwise',
        base + 20: 'EltwiseInt',
        base + 21: 'InstNorm',
        base + 22: 'Pad',
        base + 23: 'Slice',
        base + 24: 'Tile',
        base + 25: 'Reduce',
        base + 26: 'RNN',
        base + 27: 'Resize',
        base + 28: 'Gather',
        base + 29: 'Pack',
        base + 30: 'UnPack',
        base + 31: 'ArgMax',
        base + 32: 'ArgMin',
        base + 33: 'Cast',
        base + 34: 'iForest',
        base + 35: 'SvmReg',
        base + 36: 'AFeatureExtract',
        base + 37: 'SVC',
        base + 38: 'ZipMap',
        base + 39: 'Where',
        base + 40: 'DQConv2D',
        base + 41: 'DQPool',
        base + 42: 'LinearClassifier',
        base + 43: 'TreeEnsembleClassifier',
        base + 44: 'DQDense',
        base + 45: 'TopK',
        base + 50: 'Reverse',
        base + 51: 'ReduceLogSumExp',
        base + 52: 'ReduceL1',
        base + 63: 'LiteGraph',
        base + 64: 'Container',
        base + 65: 'Lambda',
        base + 66: 'TreeEnsembleRegressor',
        base_2: 'Stateful',
        base_2 + 1: 'LSTM',
        base_2 + 2: 'Custom',
        base_2 + 3: 'GRU',
    }
    desc_ = '{}'.format(ls_switcher.get(op_type_id, str(op_type_id)))
    if with_id:
        desc_ += ' (0x{:x})'.format(op_type_id)
    return desc_


def qmn_to_str(bits: int, fbits: int, signed: bool) -> str:
    """Return short description of the format Qm.n"""  # noqa: DAR101,DAR201,DAR401

    m_i = bits - fbits - 1 if signed else bits - fbits
    pref_ = '' if signed else 'U'
    if m_i:
        return f'{pref_}Q{m_i}.{fbits}'
    return f'{pref_}Q{fbits}'


class AiBufferFormat(ct.c_uint32):
    """ Map C 'ai_buffer_format' enum to Python enum. """  # noqa: DAR101,DAR201,DAR401

    # see api/ai_platform.h file (and src/api/ai_datatypes_format.h file)
    AI_BUFFER_FORMAT_NONE = 0x00000040
    AI_BUFFER_FORMAT_FLOAT = 0x00821040

    AI_BUFFER_FORMAT_U1 = 0x000400c0
    AI_BUFFER_FORMAT_U8 = 0x00040440
    AI_BUFFER_FORMAT_U16 = 0x00040840
    AI_BUFFER_FORMAT_U32 = 0x00041040
    AI_BUFFER_FORMAT_U64 = 0x00042040

    AI_BUFFER_FORMAT_S1 = 0x008400c0
    AI_BUFFER_FORMAT_S8 = 0x00840440
    AI_BUFFER_FORMAT_S16 = 0x00840840
    AI_BUFFER_FORMAT_S32 = 0x00841040
    AI_BUFFER_FORMAT_S64 = 0x00842040

    AI_BUFFER_FORMAT_Q = 0x00840040
    AI_BUFFER_FORMAT_Q7 = 0x00840447
    AI_BUFFER_FORMAT_Q15 = 0x0084084f

    AI_BUFFER_FORMAT_UQ = 0x00040040
    AI_BUFFER_FORMAT_UQ7 = 0x00040447
    AI_BUFFER_FORMAT_UQ15 = 0x0004084f
    AI_BUFFER_FORMAT_BOOL = 0x00060440

    """ Buffer Format Flags """
    MASK = 0x01ffffff       # non-flag bits
    MASK_Q = 0xffffc000
    TYPE_MASK = 0x019e3f80  # bits required for type identification
    FBIT_SHIFT = 0x40       # zero point for signed fractional bits

    """ Bit mask definitions """

    #
    # format 32b / MASK = 0x01FF FFFF  (b24..b0)
    #
    #          b30          1b - CONST
    #          b29          1b - STATIC
    #          b28
    #          b27          1b - IO
    #          b26..b25
    # -----------------------------------------------------------------
    #          b24          1b - COMPLEX type
    #          b23          1b - 1:signed 0:unsigned
    #     b22..b21          2b 0x3 - = 00b
    #     b20..b17          4b 0xF - type ID - 0:None 1:Float Q:2 BOOL:3 - ((type_id) & 0xF) << 17
    #     b16..b14          3b 0x7 - = 000b
    #      b13..b7          7b 0x7F - number of bits     0..128(2^7)     = ((bits) & 0x7F) << 7
    #       b6..b0          7b 0x7F - number of fraction bits 0..64(2^6) = (((fbits) + 64) & 0x7F) << 0
    #
    # ex: UQ15 0x0004084f
    #     0000 000 0 0 00 0010 000 0010000 1001111
    #                      '2'         '16' '79'- 64 = 15
    #     S8 0x00840440
    #     0000 000 0 1 00 0010 000 0001000 1000000
    #                s     '2'         '8' '64' - 64 = 0
    #     U8 0x00040440
    #     0000 000 0 0 00 0010 000 0001000 1000000
    #                      '2'         '8' '64' - 64 = 0
    #     S1 0x008400c0
    #     0000 000 0 1 00 0010 000 0000001 1000000
    #                s     '2'         '1'  '64' - 64 = 0
    #     UQ7 0x00040447
    #     0000 000 0 0 00 0010 000 0001000 1000111
    #                u     '2'         '8'  '71' - 64 = 7
    #     Q15 0x0084084f
    #     0000 000 0 1 00 0010 000 0010000 1001111
    #                s     '2'        '16'  '79' - 64 = 15
    #

    FLOAT_MASK = 0x1
    FLOAT_SHIFT = 24

    SIGN_MASK = 0x1
    SIGN_SHIFT = 23

    TYPE_ID_MASK = 0xF
    TYPE_ID_SHIFT = 17

    BITS_MASK = 0x7F
    BITS_SHIFT = 7

    FBITS_MASK = 0x7F
    FBITS_SHIFT = 0

    # = AI_BUFFER_FMT_TYPE_XX definition
    TYPE_NONE = 0x0
    TYPE_FLOAT = 0x1
    TYPE_Q = 0x2
    TYPE_INTEGER = 0x2
    TYPE_BOOL = 0x3
    TYPE_FXP = 0xF

    FLAG_CONST = 0x1 << 30
    FLAG_STATIC = 0x1 << 29
    FLAG_IS_IO = 0x1 << 27

    def to_dict(self):
        # noqa: DAR101,DAR201,DAR401
        """Return a dict with fmt field values"""
        fmt = self.value
        _dict = {
            'sign': (fmt >> self.SIGN_SHIFT) & self.SIGN_MASK,
            'type': (fmt >> self.TYPE_ID_SHIFT) & self.TYPE_ID_MASK,
        }
        # for legacy test - remove usage of the self.FLOAT_SHIFT (b24)
        _dict['float'] = 1 if self.is_float() else 0
        _dict['bits'] = self.bits()
        _dict['fbits'] = self.fbits()
        _dict['np_type'] = self.to_np_type()
        _dict['packet_mode'] = self.packed()
        return _dict

    def to_np_type(self):
        # noqa: DAR101,DAR201,DAR401
        """Return numpy type based on AI buffer format definition"""
        fmt = self.value

        _type = (fmt >> self.TYPE_ID_SHIFT) & self.TYPE_ID_MASK
        _bits = (fmt >> self.BITS_SHIFT) & self.BITS_MASK
        _sign = (fmt >> self.SIGN_SHIFT) & self.SIGN_MASK

        if _type == self.TYPE_FLOAT:
            if _bits == 32:
                return np.float32
            if _bits == 16:
                return np.float16
            return np.float64

        if _type == self.TYPE_NONE:
            return np.void

        if _type == self.TYPE_BOOL:
            return bool

        if _type in (self.TYPE_Q, self.TYPE_FXP):
            if _sign and _bits == 1:
                # packet32 bit format
                return np.int32
            if _bits == 1:
                # packet32 bit format
                return np.uint32
            if _sign and _bits == 8:
                return np.int8
            if _sign and _bits == 16:
                return np.int16
            if _sign and _bits == 32:
                return np.int32
            if _sign and _bits == 64:
                return np.int64
            if _bits == 8:
                return np.uint8
            if _bits == 16:
                return np.uint16
            if _bits == 32:
                return np.uint32
            if _bits == 64:
                return np.uint64

        msg_ = f'AI type ({_type}/{_bits}/{_sign}) to numpy type not supported'
        raise NotImplementedError(msg_)

    @staticmethod
    def to_fmt(np_type, is_io=True, static=False, const=False, bits=None, fbits=None):
        """Convert numpy dtype to AiBufferFormat"""
        # noqa: DAR101,DAR201,DAR401

        np_to_ai_format = {
            np.void: AiBufferFormat.AI_BUFFER_FORMAT_NONE,
            np.bool_: AiBufferFormat.AI_BUFFER_FORMAT_BOOL,
            np.float32: AiBufferFormat.AI_BUFFER_FORMAT_FLOAT,
            np.uint8: AiBufferFormat.AI_BUFFER_FORMAT_U8,
            np.uint16: AiBufferFormat.AI_BUFFER_FORMAT_U16,
            np.uint32: AiBufferFormat.AI_BUFFER_FORMAT_U32,
            np.uint64: AiBufferFormat.AI_BUFFER_FORMAT_U64,
            np.int8: AiBufferFormat.AI_BUFFER_FORMAT_S8,
            np.int16: AiBufferFormat.AI_BUFFER_FORMAT_S16,
            np.int32: AiBufferFormat.AI_BUFFER_FORMAT_S32,
            np.int64: AiBufferFormat.AI_BUFFER_FORMAT_S64,
        }

        if np_type in [bool, bool, np.bool_]:
            fmt = AiBufferFormat.AI_BUFFER_FORMAT_BOOL
        else:
            fmt = np_to_ai_format.get(np_type, None)
        if bits and bits == 1:
            fmt = AiBufferFormat.AI_BUFFER_FORMAT_S1 if fmt == AiBufferFormat.AI_BUFFER_FORMAT_S32\
                else AiBufferFormat.AI_BUFFER_FORMAT_U1

        if fmt is None:
            msg_ = 'numpy type {} is not supported'.format(str(np_type))
            raise NotImplementedError(msg_)

        if bits is not None and ((fmt >> AiBufferFormat.BITS_SHIFT) & AiBufferFormat.BITS_MASK) != bits:
            msg_ = 'number of bits {}/{} is not consistent'.format(str(np_type), bits)
            raise NotImplementedError(msg_)

        if is_io:
            fmt |= AiBufferFormat.FLAG_IS_IO
        if static:
            fmt |= AiBufferFormat.FLAG_STATIC
        if const:
            fmt |= AiBufferFormat.FLAG_CONST

        if fbits and fbits != 0:
            fmt &= ~(AiBufferFormat.FBITS_MASK << AiBufferFormat.FBITS_SHIFT)
            fmt = fmt + (((fbits + 64) & AiBufferFormat.FBITS_MASK) << AiBufferFormat.FBITS_SHIFT)

        return AiBufferFormat(fmt)

    def __eq__(self, other):
        """Check if two objects are equal"""  # noqa: DAR101,DAR201,DAR401
        if isinstance(other, AiBufferFormat):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False

    def is_supported(self):
        # noqa: DAR101,DAR201,DAR401
        """Check if provided format is valid"""
        cdt = False
        dict_ = self.to_dict()
        if dict_['type'] == self.TYPE_FLOAT:
            cdt = dict_['sign'] == 1 and dict_['float'] and\
                dict_['fbits'] == 0 and dict_['bits'] in [16, 32] and\
                dict_['np_type'] in [np.float32, np.float16] and dict_['packet_mode'] == ''
        elif dict_['type'] == self.TYPE_BOOL:
            cdt = dict_['sign'] == 0 and dict_['float'] == 0 and\
                dict_['fbits'] == 0 and dict_['bits'] == 8 and\
                dict_['np_type'] == bool and dict_['packet_mode'] == ''
        elif dict_['type'] in [self.TYPE_Q, self.TYPE_INTEGER, self.TYPE_FXP]:
            cdt = dict_['float'] == 0 and dict_['bits'] in [1, 8, 16, 32, 64]
            if dict_['bits'] == 1:  # packed mode
                cdt = cdt and dict_['packet_mode'] == '1b' and\
                    dict_['np_type'] in [np.uint32, np.int32] and\
                    dict_['fbits'] == 0
            else:
                cdt = cdt and dict_['packet_mode'] == ''
                if dict_['sign']:
                    cdt = cdt and dict_['np_type'] in [np.int64, np.int32, np.int16, np.int8]
                else:
                    cdt = cdt and dict_['np_type'] in [np.uint64, np.uint32, np.uint16, np.uint8]
        if not cdt:
            msg_ = f'invalid/unsupported format {dict_}'
            raise NotImplementedError(msg_)

    def bits(self):
        # noqa: DAR101,DAR201,DAR401
        """Return number of bits"""
        fmt = self.value
        return (fmt >> self.BITS_SHIFT) & self.BITS_MASK

    def fbits(self):
        # noqa: DAR101,DAR201,DAR401
        """Return number of fraction bits"""
        fmt = self.value
        return ((fmt >> self.FBITS_SHIFT) & self.FBITS_MASK) - 64

    def packed(self):
        # noqa: DAR101,DAR201,DAR401
        """Return packed def"""
        bits = self.bits()
        return f'{bits}b' if bits < 8 and self.is_packed() else ''

    def is_bool(self):
        # noqa: DAR101,DAR201,DAR401
        """Is a bool type"""
        fmt = self.value
        return (fmt >> self.TYPE_ID_SHIFT) & self.TYPE_ID_MASK ==\
            self.TYPE_BOOL

    def is_float(self):
        # noqa: DAR101,DAR201,DAR401
        """Is a float type"""
        fmt = self.value
        return (fmt >> self.TYPE_ID_SHIFT) & self.TYPE_ID_MASK ==\
            self.TYPE_FLOAT

    def is_integer(self):
        # noqa: DAR101,DAR201,DAR401
        """Is an integer type"""
        fmt = self.value
        type_id = (fmt >> AiBufferFormat.TYPE_ID_SHIFT) & AiBufferFormat.TYPE_ID_MASK
        fbits = (fmt >> AiBufferFormat.FBITS_SHIFT) & AiBufferFormat.FBITS_MASK
        return type_id in [self.TYPE_Q, self.TYPE_INTEGER] and fbits == 64

    def is_fxp(self):
        # noqa: DAR101,DAR201,DAR401
        """Is a fixed-point number"""
        fmt = self.value
        type_id = (fmt >> AiBufferFormat.TYPE_ID_SHIFT) & AiBufferFormat.TYPE_ID_MASK
        if type_id in [AiBufferFormat.TYPE_FXP]:
            return True
        fbits = (fmt >> self.FBITS_SHIFT) & self.FBITS_MASK
        return type_id in [self.TYPE_Q] and fbits != 64

    def is_signed(self):
        # noqa: DAR101,DAR201,DAR401
        """Is signed"""
        fmt = self.value
        return (fmt >> self.SIGN_SHIFT) & self.SIGN_MASK

    def is_packed(self):
        # noqa: DAR101,DAR201,DAR401
        """Is packed data"""
        fmt = self.value
        return fmt & self.MASK in [
            self.AI_BUFFER_FORMAT_S1,
            self.AI_BUFFER_FORMAT_U1
        ]

    def get_converter(self, shape, quant):
        """
        Return the converter to be used to get data

        Parameters
        ----------
        shape: tuple
            The shape of the associated tensor

        quant: dict
            The quantization information

        Returns
        -------
        converter

        Raises
        ------
        ValueError
            input data value, dtype or dim are invalid
        """
        if quant is not None:
            if not isinstance(quant, dict)\
                    or not all([key in quant for key in ['scale', 'zero_point']]):
                msg_ = "Invalid quantization parameters, a dict with valid 'scale'/'zero_point'"
                msg_ += f' keys is expected: {quant}'
                raise ValueError(msg_)
        if self.is_bool():
            return AiBoolConverter(shape)
        if self.is_packed():
            return Ai1b32bPackConverter(shape, pad_value=0, signed=self.is_signed())
        if self.is_integer() and quant is not None and quant['scale']:
            return AiQuantUniformConverter(shape, scale=quant['scale'], zp=quant['zero_point'], dtype=self.to_np_type())
        if self.is_fxp():
            return AiFixedPointConverter(shape, fbits=self.fbits(), dtype=self.to_np_type())
        return AiIdentityConverter(shape)


class AiConverter(ABC):
    """Base class to handle the ai converter functions"""

    def __init__(self, shape_in, name='Identity'):
        """Constructor"""  # noqa: DAR101,DAR201,DAR401
        self._name = name
        self._shape_in = shape_in

    @property
    def name(self) -> str:
        """Return name of the converter"""
        # noqa: DAR101,DAR201,DAR401
        return self._name

    def __str__(self):
        """Short description of the converter"""  # noqa: DAR101,DAR201,DAR401
        return self.name

    def get_c_size(self, shape_in):
        """Size in bytes to store the converted data (c-level)"""  # noqa: DAR101,DAR201,DAR401
        shape_in = shape_in if shape_in else self._shape_in
        return self._get_c_size(shape_in)

    def get_c_shape(self, shape_in):
        """Shape of the converted data"""  # noqa: DAR101,DAR201,DAR401
        shape_in = shape_in if shape_in else self._shape_in
        return self._get_c_shape(shape_in)

    def __call__(self, data_in, shape_in):
        """Quantize/Pack the numpy array"""  # noqa: DAR101,DAR201,DAR401
        shape_in = shape_in if shape_in else self._shape_in
        data_in = data_in.reshape((-1,) + shape_in[1:])
        return self._process_in(data_in, shape_in)

    def to_float32(self, data_in, shape_in):
        """Dequantize/Unpack the numpy array"""  # noqa: DAR101,DAR201,DAR401
        shape_in = shape_in if shape_in else self._shape_in
        shape_out = self.get_c_shape(shape_in)
        data_in = data_in.reshape((-1,) + shape_out[1:])
        return self._to_float32(data_in, shape_in).astype(np.float32)

    def _get_c_size(self, shape_in):
        """Size of the storage in bytes (c-level)"""  # noqa: DAR101,DAR201,DAR401
        return np.prod(shape_in)

    def _get_c_shape(self, shape_in):
        """Shape of the converted data (c-level)"""  # noqa: DAR101,DAR201,DAR401
        return shape_in

    @abstractmethod
    def _process_in(self, data_in, shape_in):
        """Quantize/Pack the numpy array"""
        # noqa: DAR101,DAR201,DAR401

    @abstractmethod
    def _to_float32(self, data_in, _):
        """Dequantize/Unpack the numpy array"""
        # noqa: DAR101,DAR201,DAR401

    @abstractmethod
    def get_desc(self) -> str:
        """Return short description"""  # noqa: DAR101,DAR201,DAR401

    def get_quantization_params(self) -> Dict:
        """Return quantization parameters"""  # noqa: DAR101,DAR201,DAR401
        return {}


class AiIdentityConverter(AiConverter):
    """Identity Converter"""

    def _process_in(self, data_in, _):
        """Quantize/Pack the numpy array"""  # noqa: DAR101,DAR201,DAR401
        new_type = np.float32 if np.issubdtype(data_in.dtype, np.floating) else data_in.dtype
        return data_in.astype(new_type)

    def _to_float32(self, data_in, _):
        """Dequantize/Unpack the numpy array"""  # noqa: DAR101,DAR201,DAR401
        return data_in.astype(np.float32)

    def get_desc(self) -> str:
        """Return short description"""  # noqa: DAR101,DAR201,DAR401
        return ''


class AiBoolConverter(AiConverter):
    """Bool converter"""

    def __init__(self, shape_in):
        """Constructor"""  # noqa: DAR101,DAR201,DAR401
        super(AiBoolConverter, self).__init__(shape_in, 'Boolean')

    def __str__(self):
        """Short description of the converter"""  # noqa: DAR101,DAR201,DAR401
        return self.name

    def _process_in(self, data_in, _):
        """Quantize the numpy array"""  # noqa: DAR101,DAR201,DAR401
        data_ = np.vectorize(lambda a: a > 0)(data_in)
        return data_.astype(np.bool_)

    def _to_float32(self, data_in, _):
        """Dequantize the numpy array"""  # noqa: DAR101,DAR201,DAR401
        data_ = np.vectorize(lambda a: 1.0 if a else 0.0)(data_in)
        return data_.astype(np.float32)

    def get_desc(self) -> str:
        """Return short description"""  # noqa: DAR101,DAR201,DAR401
        return self.name


class AiQuantUniformConverter(AiConverter):
    """Converter to/from quantized data (scale/zero_point scheme)"""

    def __init__(self, shape_in, scale, zp, dtype, name='QLinear'):
        """ """  # noqa: DAR101,DAR201,DAR401
        self._scale = scale
        self._zp = zp
        self._dtype = dtype
        super(AiQuantUniformConverter, self).__init__(shape_in, name)

    def __str__(self):
        """Short description of the converter"""  # noqa: DAR101,DAR201,DAR401
        return f'{self.name}({self.get_desc()})'

    def _process_in(self, data_in, _):
        """Quantize the numpy array"""  # noqa: DAR101,DAR201,DAR401
        iinfo_ = np.iinfo(self._dtype)
        data_q_ = np.round(np.asarray(data_in) / self._scale) + self._zp
        data_q_ = np.clip(data_q_, iinfo_.min, iinfo_.max)
        return data_q_.astype(self._dtype)

    def _to_float32(self, data_in, _):
        """Dequantize the numpy array"""  # noqa: DAR101,DAR201,DAR401
        data_r_ = (data_in.astype(np.int32) - np.int32(self._zp)) * self._scale
        return data_r_.astype(np.float32)

    def get_quantization_params(self):
        """Return quantization parameters"""  # noqa: DAR101,DAR201,DAR401
        return {'scale': self._scale, 'zero_point': self._zp}

    def get_desc(self) -> str:
        """Return short description"""  # noqa: DAR101,DAR201,DAR401
        return f'{self._scale:.9f},{self._zp},{np.dtype(self._dtype)}'


class AiFixedPointConverter(AiQuantUniformConverter):
    """FixedPoint/Qmn converter"""

    def __init__(self, shape_in, fbits, dtype):
        """ """  # noqa: DAR101,DAR201,DAR401
        self._fbits = fbits
        scaling_factor = 2 ** (-fbits)
        super(AiFixedPointConverter, self).__init__(shape_in, scaling_factor, 0,
                                                    dtype, 'FixedPoint')

    def __str__(self):
        """Short description of the converter"""  # noqa: DAR101,DAR201,DAR401
        soff_ = super(AiFixedPointConverter, self).get_desc()
        return f'{self.name}({soff_},{self.get_desc()})'

    def get_desc(self) -> str:
        """Return short description of the format Qm.n"""  # noqa: DAR101,DAR201,DAR401
        iinfo_ = np.iinfo(self._dtype)
        signed_ = iinfo_.min < 0
        return qmn_to_str(iinfo_.bits, self._fbits, signed_)


class Ai1b32bPackConverter(AiConverter):
    """Converter to/from signed 1b (32b packet)"""

    def __init__(self, shape_in, pad_value=0, signed=True):
        """
        Constructor of converter object for 1b (32b packet)
        bit-order: 'little' or MSB first (axis=-1 or channel dim)

        Parameters
        ----------
        shape_in
            tuple, list, int: shape of the tensor
        pad_value
            int, str: pad value, 0 or 1 (default: 0)
        signed
            bool: indicates if signed/unsigned binary scheme is used (default: True)
        """
        self._signed = signed
        if isinstance(pad_value, int):
            pad_value = 1 if pad_value > 0 else 0
        if isinstance(pad_value, str):
            pad_value = 0 if pad_value == '0' or pad_value.lower() == 'zero' else 1
        self._pad_value = pad_value
        super(Ai1b32bPackConverter, self).__init__(shape_in, name='1b-32bpacked')

    def __str__(self):
        """Short description of the converter"""  # noqa: DAR101,DAR201,DAR401
        return f'{self.name}(pad={self._pad_value})'

    def _get_c_size(self, shape_in):
        """Size in bytes to store the packed data"""  # noqa: DAR101,DAR201,DAR401
        nb_chans = shape_in[-1]
        nb_32b_chans = int(np.ceil(nb_chans / 32))
        return int(np.prod(shape_in) / nb_chans) * nb_32b_chans

    def _get_c_shape(self, shape_in):
        """Shape of the converted data"""  # noqa: DAR101,DAR201,DAR401
        nb_32b_chans = int(np.ceil(shape_in[-1] / 32))
        return shape_in[:-1] + (nb_32b_chans,)

    def _process_in(self, data_in, shape_in):
        """  # noqa: DAR005
        Pack the numpy array

        Parameters
        ----------
        data_in
            ndarray: numpy array with the data
        shape_in:
            tuple: shape of the input

        Returns
        -------
        ndarray
            data with the packed values

        Raises
        ------
        ValueError
            input data value, dtype or dim are invalid
        """
        n_shape_in = (data_in.shape[0],) + shape_in[1:]
        if np.prod(n_shape_in) != data_in.size:
            msg_ = 'Invalid number of elements: {} expected {}'.format(data_in.size, np.prod(shape_in))
            raise ValueError(msg_)
        data_in = data_in.reshape(n_shape_in)
        nb_chans = n_shape_in[-1]
        nb_32b_chans = int(np.ceil(nb_chans / 32))
        if data_in.ndim > 1:
            outer_shape = data_in.shape[:-1]
            end_shape = outer_shape + (nb_32b_chans,)
        else:
            outer_shape = (1,)
            end_shape = (nb_32b_chans,)
        data_out = np.empty(0, dtype=np.int32)
        for val in data_in.reshape((np.prod(outer_shape), nb_chans)):
            packet_vec = _pack32bits_vector(val, _x_to_bit_signed, self._pad_value)
            data_out = np.append(data_out, packet_vec)
        data_out = data_out.reshape(end_shape)
        return data_out

    def _to_float32(self, data_in, shape_in):
        """  # noqa: DAR005
        Unpack the numpy array

        Parameters
        ----------
        data_in
            ndarray: numpy array with the packet data
        shape_in:
            tuple: shape of the output

        Returns
        -------
        ndarray
            data with the unpacked values

        Raises
        ------
        ValueError
            input data value, dtype or dim are invalid
        """
        nb_chans = shape_in[-1]
        if (data_in.dtype != np.int32 and self._signed) or (data_in.dtype != np.uint32 and not self._signed):
            msg_ = 'Invalid dtype: {} expected {}'.format(
                data_in.dtype, np.dtype(np.int32) if self._signed else np.dtype(np.uint32))
            raise ValueError(msg_)
        nb_32b_chans = int(np.ceil(nb_chans / 32))
        process_shape = (-1, nb_32b_chans)

        shape_out = (data_in.shape[0],) + shape_in[1:] if len(shape_in) > 1 else shape_in[0]
        nb_elems = int(data_in.size / nb_32b_chans) * nb_chans
        if np.prod(shape_out) != nb_elems:
            msg_ = 'Unpack - Invalid number of elements: {}->{} expected {}'.format(
                data_in.shape, nb_elems, np.prod(shape_in))
            raise ValueError(msg_)

        data_out = np.empty(0, dtype=np.float32)
        for val in data_in.reshape(process_shape):
            unpacket_vec = _unpack32bits_vector(val, _bit_to_float32_signed, nb_chans)
            data_out = np.append(data_out, unpacket_vec)
        data_out = data_out.reshape(shape_out)

        return data_out

    def get_desc(self) -> str:
        """Return short description of the scheme"""  # noqa: DAR101,DAR201,DAR401
        return self.name


class IOTensor():
    """Class to handle/abstract the ai buffer"""

    def __init__(self, fmt, shape, quant=None):
        """
        Constructor of the IOTensor object

        Parameters
        ----------
        fmt
            uint32 raw ai format description (see AiBufferFormat)
        shape
            tuple, list shape of the io tensor
        quant
            dict quantization parameters (default: None, supported keys: 'scale' and 'zero_point')
        """
        if not isinstance(fmt, AiBufferFormat):
            if isinstance(fmt, int):
                fmt = AiBufferFormat(fmt)
            else:
                fmt = AiBufferFormat(fmt.value)
        self._raw_fmt = fmt
        if not isinstance(shape, (list, tuple)):
            shape = [shape]
        self._shape = tuple(shape)
        self._name = ''
        self._tag = ''
        self._c_addr = 0
        self._memory_pool = None
        fmt.is_supported()
        self._packet_mode = fmt.packed()
        self._np_type = fmt.to_np_type()
        self._converter = fmt.get_converter(self._shape, quant)
        new_quant = self._converter.get_quantization_params()
        if quant is None:
            self._quant = new_quant
        else:
            self._quant = quant

    def set_name(self, name):
        """Set the name of the tensor"""  # noqa: DAR101,DAR201,DAR401
        self._name = name

    def set_tag(self, tag):
        """Set the tag of the tensor"""  # noqa: DAR101,DAR201,DAR401
        self._tag = tag

    def set_c_addr(self, addr):
        """Set the device address of the tensor"""  # noqa: DAR101,DAR201,DAR401
        self._c_addr = addr

    def set_memory_pool(self, name=None):
        """Set the name of the associated memory pool is available"""  # noqa: DAR101,DAR201,DAR401
        self._memory_pool = name

    @property
    def name(self):
        """Name of the tensor"""
        # noqa: DAR101,DAR201,DAR401
        return self._name

    @property
    def tag(self):
        """tag of the tensor"""
        # noqa: DAR101,DAR201,DAR401
        return self._tag

    @property
    def c_addr(self):
        """device address of the tensor"""
        # noqa: DAR101,DAR201,DAR401
        return self._c_addr

    @property
    def memory_pool(self):
        """associated memory pool"""
        # noqa: DAR101,DAR201,DAR401
        return self._memory_pool

    @property
    def raw_fmt(self):
        """Raw ai format of the ai buffer"""
        # noqa: DAR101,DAR201,DAR401
        return self._raw_fmt

    @property
    def dtype(self):
        """Numpy data type for the ai buffer storage"""
        # noqa: DAR101,DAR201,DAR401
        return self._np_type

    @property
    def shape(self):
        """Shape of the tensor"""
        # noqa: DAR101,DAR201,DAR401
        return self._shape

    @property
    def size(self):
        """Number of elements"""
        # noqa: DAR101,DAR201,DAR401
        return np.prod(self._shape)

    @property
    def quant_params(self):
        """Quantization parameters"""
        # noqa: DAR101,DAR201,DAR401
        return self._quant

    @property
    def is_packed(self):
        """Is packed"""
        # noqa: DAR101,DAR201,DAR401
        return self._raw_fmt.is_packed()

    @property
    def is_bool(self):
        """Is bool"""
        # noqa: DAR101,DAR201,DAR401
        return self._raw_fmt.is_bool()

    @property
    def is_signed(self):
        """Is signed"""
        # noqa: DAR101,DAR201,DAR401
        return AiBufferFormat.is_signed(self._raw_fmt)

    @property
    def is_fxp(self):
        """Is Fixed-point format"""
        # noqa: DAR101,DAR201,DAR401
        return self._raw_fmt.is_fxp()

    @property
    def is_quantized(self):
        """Is quantized"""
        # noqa: DAR101,DAR201,DAR401
        return isinstance(self.quant_params, dict) and self.quant_params.get('scale', None) and\
            (self._raw_fmt.is_integer() or self._raw_fmt.is_fxp())

    def pack(self, data_in):
        """Call the convert operation if packed type only"""  # noqa: DAR101,DAR201,DAR401
        if self.is_packed:
            return self._converter(data_in, self._shape)
        return data_in

    def unpack(self, data_in):
        """Call the convert operation if packed type only"""  # noqa: DAR101,DAR201,DAR401
        if self.is_packed:
            # return self._converter.to_float32(data_in, self._shape)
            return self.dequantize(data_in)
        return data_in

    def quantize(self, data_in):
        """Quantize/pack the data if necessary"""  # noqa: DAR101,DAR201,DAR401
        # default check to prevent the case where data is already quantized
        if data_in.dtype == self.dtype and data_in.size == self.get_c_size(data_in.shape):
            return data_in
        # only quantized/packed/bool data are converted
        if self.is_quantized or self.is_packed or self.is_bool or self.is_fxp:
            return self._converter(data_in, self._shape)
        # default quantization (casting mode)
        if self.dtype != data_in.dtype:
            return data_in.astype(self.dtype)
        return data_in

    def dequantize(self, data_in):
        """Dequantize/unpack the data if necessary"""  # noqa: DAR101,DAR201,DAR401
        if np.issubdtype(data_in.dtype, np.floating):
            return data_in.astype(np.float32)
        return self._converter.to_float32(data_in, self._shape)

    def to_float32(self, data_in):
        """Dequentize/Unpack the data if necessary"""  # noqa: DAR101,DAR201,DAR401
        return self.dequantize(data_in)

    def zeros(self):
        """Return a new numpy array, filled with zeros for the storage"""  # noqa: DAR101,DAR201,DAR401
        return np.zeros((self.get_c_size(),), dtype=self.dtype)

    def get_c_size_in_bytes(self):
        """Return the size of the storage in bytes"""  # noqa: DAR101,DAR201,DAR401
        return self.get_c_size() * np.dtype(self._np_type).itemsize

    def get_c_size(self, shape=None):
        """Number of elements for the storage."""  # noqa: DAR101,DAR201,DAR401
        shape = self._shape if shape is None else shape
        return self._converter.get_c_size(shape)

    def get_c_shape(self, shape=None):
        """Shape of the torage."""  # noqa: DAR101,DAR201,DAR401
        shape = self._shape if shape is None else shape
        return self._converter.get_c_shape(shape)

    def get_quant_desc(self):
        """Return short humain description of the quant/pack scheme"""  # noqa: DAR101,DAR201,DAR401
        return self._converter.get_desc()

    def to_str(self, selector: str = 'all', short: bool = True) -> str:
        """Return short human description"""  # noqa: DAR101,DAR201,DAR401

        def _with(specifier: str):
            if f'no-{specifier}' in selectors_:
                return False
            return 'all' in selectors_ or specifier in selectors_

        def _shape(shape_):
            return f"[{','.join([str(dim) for dim in shape_])}]"

        def _type(dtype_, from_dtype=False):
            dtype_ = np.dtype(dtype_)
            if np.issubdtype(dtype_, np.floating):
                return f'f{dtype_.itemsize * 8}'
            if dtype_ in (np.bool_,):
                return 'b8' if short else 'bool8'
            if from_dtype:
                if short:
                    str_ = f"{dtype_.kind}{dtype_.itemsize * 8}"
                else:
                    str_ = f"{dtype_.name}"
            else:
                if short:
                    str_ = 'i' if self.is_signed else 'u'
                else:
                    str_ = 'int' if self.is_signed else 'uint'
                str_ += str(self.raw_fmt.bits())
            return str_

        selectors_ = selector.lower().split('+')

        shape_desc = f'{_type(self.dtype, not self.raw_fmt.is_packed())}{_shape(self.shape)}'
        q_scheme_desc = ''
        sep_ = ':' if short else ', '
        q_params = self.quant_params
        if self.raw_fmt.is_packed():
            shape_desc += f"/{_type(self.dtype, True)}{_shape(self.get_c_shape())}"
            q_scheme_desc = f"{sep_}{self._converter}"
        elif self.raw_fmt.is_fxp():
            q_scheme_desc = f"{sep_}{self._converter}"
        elif 'scale' in q_params and q_params['scale']:
            q_scheme_desc = f"{sep_}{self._converter}"

        res_ = f"'{self.name}'{sep_}" if _with('name') else ''
        res_ += f'{shape_desc}'
        if short:
            res_ += f'{sep_}{self.get_c_size_in_bytes()}' if _with('size') else ''
        else:
            res_ += f'{sep_}{self.get_c_size_in_bytes()} Bytes' if _with('size') else ''
        res_ += f'{q_scheme_desc}' if _with('scheme') else ''
        res_ += f'{sep_}{self.memory_pool}' if _with('loc') else ''

        return res_

    def desc(self, full=False):
        """Human description"""  # noqa: DAR101,DAR201,DAR401
        if full:
            desc = 'IOTensor: '
            desc += f'{self.name}, ' if self.name else ''
            desc += f'{self._tag}, '
            if self.c_addr:
                desc += f', 0x{self.c_addr:08x} '
            desc += self.to_str('all+no-loc+no-name', short=False)
        else:
            desc = f'{self.name}, ' if self.name else ''
            desc += f'{self._tag}, '
            desc += self.to_str('all+no-loc+no-name', short=False)

        return desc

    def __str__(self):
        """Return description"""  # noqa: DAR101,DAR201,DAR401
        return self.desc(full=True)

    def __repr__(self):
        return self.__str__()


def _x_to_bit_signed(val):
    """  # noqa: DAR101,DAR201,DAR401
    Element-wise operator to convert original binary value to internal bit representation.
    Positive value is coded with a `0`, negative value is coded with a `1`
    (sign bit is used to binarize the data)

        {-1, 1} -> {1, 0}

        y = ( 1 - sign(x) ) / 2
    """
    return ((1 - np.sign(val)) / 2).astype(int)


def _bit_to_float32_signed(val):
    """  # noqa: DAR101,DAR201,DAR401
    Element-wise operator to convert internal bit representation value to fp32 binary value

        {1, 0} -> {-1, 1}

        y = 1 - 2 * x
    """
    if not all([v in (0, 1) for v in val]):
        msg_ = 'Invalid bit value'
        raise ValueError(msg_)

    return (1 - 2 * val).astype(np.float32)


def _pack32bits_vector(vec, bin_op, pad_value=0):
    """Packs the elements of a binary-valued array into bits in a int32 array"""  # noqa: DAR101,DAR201,DAR401
    # bit-order: 'little' or MSB first
    # axis = -1
    acc32, shift = np.uint32(0), 31
    res = []
    elems = bin_op(np.array(vec).flatten())
    for bit_val in elems:
        acc32 |= bit_val << shift
        shift -= 1
        if shift == -1:
            res.append(acc32)
            acc32, shift = np.uint32(0), 31
    if shift != 31:
        while shift != -1:
            acc32 |= pad_value << shift
            shift -= 1
        res.append(acc32)
    return np.array(res, dtype=np.uint32).astype(np.int32)


def _unpack32bits_vector(vec, bin_op, count):
    """Unpacks elements of a uint32 array into a binary-valued output array."""  # noqa: DAR101,DAR201,DAR401
    res = []
    shift = 31
    elems = vec.flatten().tolist() if isinstance(vec, np.ndarray) else vec
    for val in elems:
        while shift >= 0 and count > 0:
            bit_val = (val & (0x1 << shift)) >> shift
            if count > 0:
                res.append(bit_val)
            count -= 1
            shift -= 1
        shift = 31
    return bin_op(np.array(res))


def st_neural_art_node_type_to_str(op_type_id):
    """  # noqa: DAR005
    Return a human readable description of a ST Neural ART-node

    Parameters
    ----------
    op_type_id
        EPOCH operator id/index

    Returns
    -------
    str
        human readable description of the c-node
    """
    id_ = op_type_id & 0xF
    desc_ = ''  # default name (HW epoch)
    if id_ == 1:  # Extra HW epoch
        sub_id = (op_type_id & 0xFFFF) >> 4
        desc_ += f'epoch (extra HW.{sub_id})'
    elif id_ == 2:  # SW epoch
        desc_ += 'epoch (SW)'
    elif id_ == 3:  # hybrid epoch
        desc_ += 'epoch (HYBRID)'
    elif id_ == 4:  # epoch controller
        desc_ += 'epoch (EC)'
    else:  # default HW
        desc_ += 'epoch'

    return desc_
