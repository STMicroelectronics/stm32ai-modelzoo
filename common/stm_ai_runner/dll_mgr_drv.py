###################################################################################
#   Copyright (c) 2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
STM AI runner - Driver to manage the DLL (generated for the X86 validation)
"""

import ctypes as ct
import os
import fnmatch
import time as t
import platform
import tempfile
import shutil
import random
import string
from enum import Flag
import logging

import numpy as np

from .ai_runner import AiRunnerDriver, AiRunner, STAI_INFO_DICT_VERSION
from .ai_runner import HwIOError, AiRunnerError
from .stm_ai_utils import stm_ai_error_to_str, AiBufferFormat, IOTensor
from .stm_ai_utils import stm_ai_node_type_to_str, RT_ST_AI_NAME
from .stm_ai_utils import AiIdentityConverter, AiBoolConverter, Ai1b32bPackConverter, AiQuantUniformConverter

_AI_MAGIC_MARKER = 0xA1FACADE

_SHARED_LIB_EXT = ['.so', '.dll', '.dylib']

__version__ = "2.0"


def _find_files(directory, pattern):
    for root, _, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def get_library_name(path_name):
    """
    Return full name of the shared lib, including the extension

    Parameters
    ----------
    path_name
        full path of the shared library file

    Returns
    -------
    str
        full path with specific extension

    Raises
    ------
    OSError
        File not found
    """
    if not os.path.isfile(path_name):
        for ext in _SHARED_LIB_EXT:
            if os.path.isfile(path_name + ext):
                return path_name + ext
    else:
        return path_name
    raise OSError('"{}" not found'.format(path_name))


class _TemporaryLibrary:
    """Utility class - Temporary copy of the library"""

    def __init__(self, full_name, copy_mode=False):
        self._c_dll = None  # Library object
        self._dir = os.path.dirname(full_name)
        self._name = os.path.basename(full_name)
        if copy_mode:
            name_, ext_ = os.path.splitext(os.path.basename(full_name))
            name_ += '_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            self._name = name_ + ext_
            self._dir = tempfile.gettempdir()
            self._tmp_full_name = os.path.join(self._dir, self._name)
            shutil.copyfile(full_name, self._tmp_full_name)
        else:
            self._tmp_full_name = None

    @property
    def full_path(self):
        """Return full path of the used shared library"""
        # noqa: DAR101,DAR201,DAR401
        if self._tmp_full_name:
            return self._tmp_full_name
        else:
            return os.path.join(self._dir, self._name)

    def load_library(self):
        """Load the library"""  # noqa: DAR101,DAR201,DAR401
        self._c_dll = np.ctypeslib.load_library(self._name, self._dir)
        return self._c_dll

    def __call__(self):
        """Callable method"""  # noqa: DAR201
        return self._c_dll

    def unload_library(self):
        """Unload the library"""
        if self._c_dll is not None:
            if self._tmp_full_name:
                hdl_ = self._c_dll._handle  # pylint: disable=protected-access
                if os.name == 'nt':
                    ct.windll.kernel32.FreeLibrary(ct.c_void_p(hdl_))
                self._c_dll = None
            else:
                self._c_dll = None
        if self._tmp_full_name and os.path.isfile(self._tmp_full_name):
            try:
                os.remove(self._tmp_full_name)
                self._tmp_full_name = None
            except OSError:
                pass

    def __del__(self):
        """Destructor"""
        self.unload_library()


def _split(full_name):
    name_ = os.path.basename(full_name)
    name_, ext_ = os.path.splitext(name_)
    norm_path_ = os.path.normpath(full_name)
    dir_ = os.path.dirname(norm_path_)
    return norm_path_, dir_, name_, ext_


def check_and_find_stm_ai_dll(desc):
    """Check and return stm.ai dll(s)"""  # noqa: DAR101,DAR201,DAR401
    cdt, cdt_obs = '', ''
    invalid_keys = ['libai_inspector.', 'libai_observer.',
                    'libai_helper_convert.']

    if os.path.isdir(desc):
        for f_name in _find_files(desc, 'libai_*.*'):
            if all(x not in f_name for x in invalid_keys) and\
                    not f_name.endswith('.a'):
                cdt = os.path.normpath(f_name)
                break
    elif os.path.isfile(desc):
        norm_path_, _, _, ext_ = _split(desc)
        if ext_ in _SHARED_LIB_EXT:
            cdt = norm_path_
    else:
        norm_path_, _, _, ext_ = _split(desc)
        if not ext_:
            for ext_ in _SHARED_LIB_EXT:
                f_lib = norm_path_ + ext_
                if os.path.isfile(f_lib):
                    cdt = f_lib
                    break

    if cdt:
        # check if not an excluded file
        if not all(x not in cdt for x in invalid_keys):
            cdt, cdt_obs = '', ''
        # check if expected dll observer is available
        _, dir_, _, ext_ = _split(cdt)
        f_obs = os.path.join(dir_, "libai_observer" + ext_)
        if os.path.isfile(f_obs):
            cdt_obs = f_obs

    return bool(cdt), cdt, cdt_obs


def _wrap_api(lib, funcname, restype, argtypes):
    """Helper function to simplify wrapping CTypes functions."""  # noqa: DAR101,DAR201,DAR401
    func = getattr(lib, funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func


def _rounded_up(val, align):
    """Rounding up intger"""  # noqa: DAR101,DAR201,DAR401
    return -(-val // align)


def _get_array_from_act(io_tensor, ptr_data, arr=None):
    """Return numpy array from act buffer"""  # noqa: DAR101,DAR201,DAR401
    # a new ndarray is created with a buffer located inside the activations buffer
    #  if provided, items from the user ndarray are copied in
    c_shape = (1, io_tensor.get_c_size())
    size = io_tensor.get_c_size_in_bytes()
    data = ct.cast(ptr_data, ct.POINTER(ct.c_uint8 * size))
    bytebuf = np.ctypeslib.as_array(data.contents, (size, ))
    dst_ = np.reshape(np.frombuffer(bytebuf, io_tensor.dtype), c_shape)
    if arr is not None:
        np.copyto(dst_, arr.reshape(c_shape), casting='no')
    return dst_


class GuardedNumpyArray():
    """Create a guarded numpy array"""  # noqa: DAR101,DAR201,DAR401

    def __init__(self, arr, name='input'):
        """Build a new object with extra bytes and copy the original inside"""  # noqa: DAR101,DAR201,DAR401
        self._name = name
        c_size = arr.itemsize * arr.size
        buffer = np.zeros((_rounded_up(c_size, 8) + 2,), dtype=np.uint64)
        self._garray = np.require(buffer, dtype=np.uint64,
                                  requirements=['C', 'O', 'W', 'A'])
        ptr_data = ct.cast(self._garray.ctypes.data + 8,
                           ct.POINTER(ct.c_uint8))
        dst = ct.cast(ptr_data, ct.POINTER(ct.c_uint8 * c_size))
        bytebuf = np.ctypeslib.as_array(dst.contents, (c_size, ))
        self._array = np.reshape(np.frombuffer(bytebuf, arr.dtype), arr.shape)
        np.copyto(self._array, arr, casting='no')

    def __call__(self):
        """Return the guarded numpy array"""  # noqa: DAR101,DAR201,DAR401
        return self._array

    def __del__(self):
        """Release the guarded numpy array"""  # noqa: DAR101,DAR201,DAR401
        if self._garray[0] != 0 or self._garray[-1] != 0:
            msg = 'Data has been written outside the \'{}\' buffer'.format(self._name)
            raise HwIOError(msg)


class Printable(ct.Structure):
    """C struct interface for printable field contents; used for debug and
    logging."""  # noqa: DAR101,DAR201,DAR401

    def __str__(self):
        """Print the content of the structure."""  # noqa: DAR101,DAR201,DAR401
        msg = "[{}]".format(self.__class__.__name__)

        for field in self._fields_:
            member = getattr(self, field[0])
            # parse pointer addresses
            try:
                if hasattr(member, 'contents'):
                    member = hex(ct.addressof(member.contents))
            except ValueError:  # NULL pointer
                member = "NULL"

            indented = "\n".join("  " + line for line in str(member).splitlines())
            msg += "\n  {}:{}".format(field[0], indented)

        return msg + "\n"


class PrintableUnion(ct.Union):
    """C union interface for printable field contents; used for debug and
    logging."""  # noqa: DAR101,DAR201,DAR401

    def __str__(self):
        """Print the content of the structure."""  # noqa: DAR101,DAR201,DAR401
        msg = "[{}]".format(self.__class__.__name__)

        for field in self._fields_:
            member = getattr(self, field[0])
            # parse pointer addresses
            try:
                if hasattr(member, 'contents'):
                    member = hex(ct.addressof(member.contents))
            except ValueError:  # NULL pointer
                member = "NULL"

            indented = "\n".join("  " + line for line in str(member).splitlines())
            msg += "\n  {}:{}".format(field[0], indented)

        return msg + "\n"


class AiPlatformVersion(Printable):
    """Wrapper for C 'ai_platform_version' struct."""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [('major', ct.c_uint, 8),
                ('minor', ct.c_uint, 8),
                ('micro', ct.c_uint, 8),
                ('reserved', ct.c_uint, 8)]

    def to_ver(self):
        """Return 3d tuple with the version"""  # noqa: DAR201
        return (self.major, self.minor, self.micro)

    def to_int(self):
        """Return integer packed version"""  # noqa: DAR201
        return int((self.major << 24) + (self.minor << 16) + (self.micro << 8))

    def __call__(self):
        """Return integer packed version"""  # noqa: DAR201
        return self.to_int()


class AiIntqInfo(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_intq_info' struct."""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [('scale', ct.POINTER(ct.c_float)),
                ('zeropoint', ct.POINTER(ct.c_void_p))]


class AiIntqInfoList(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_intq_info_list' struct."""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [('flags', ct.c_uint, 16),
                ('size', ct.c_uint, 16),
                ('info', ct.POINTER(AiIntqInfo))]
    AI_BUFFER_META_FLAG_SCALE_FLOAT = 0x00000001
    AI_BUFFER_META_FLAG_ZEROPOINT_U8 = 0x00000002
    AI_BUFFER_META_FLAG_ZEROPOINT_S8 = 0x00000004
    AI_BUFFER_META_FLAG_ZEROPOINT_U16 = 0x00000008
    AI_BUFFER_META_FLAG_ZEROPOINT_S16 = 0x00000010


class AiBufferMetaInfo(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_buffer_meta_info' struct."""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [('flags', ct.c_uint, 32),
                ('intq_info_list', ct.POINTER(AiIntqInfoList))]

    """ Meta Info Flags """
    AI_BUFFER_META_HAS_INTQ_INFO = 0x00000001


class AiBufferShape(Printable):     # pylint: disable=too-few-public-methods
    """."""  # noqa: DAR101,DAR201,DAR401

    # Index in the shape (see ai_platform.h file AI_SHAPE_XXX macros)
    #  channel  first      last
    #  4d       BCWH       BHWC
    #  5d       BCWHD      BHWDC
    #  6d       BCWHDE     BHWDEC
    N_BATCHES = 0  # AI_SHAPE_BATCH
    IN_CHANNELS = 0  # AI_SHAPE_IN_CHANNEL
    CHANNELS = 1  # AI_SHAPE_CHANNEL
    WIDTH = 2  # AI_SHAPE_WIDTH
    HEIGHT = 3  # AI_SHAPE_HEIGHT
    DEPTH = 4  # AI_SHAPE_DEPTH
    EXTENSION = 5  # AI_SHAPE_EXTENSION

    # Buffer Shapes supported types
    SHAPE_BCWH = 1
    SHAPE_BHWC = 2

    _fields_ = [('type', ct.c_uint, 8),
                ('size', ct.c_uint, 24),
                ('data', ct.POINTER(ct.c_uint))]

    def __init__(self, type=0, size=0, data=None):     # pylint: disable=redefined-builtin
        """Class constructor"""     # noqa: DAR101
        self._index = 0
        assert (data is None and size == 0) or (data is not None and size > 0)
        super(AiBufferShape, self).__init__(type, size, data)

    def __str__(self):
        """."""  # noqa: DAR101,DAR201
        _payload = tuple(self.data[i] for i in range(self.size))
        return "{} type({}) size({})".format(_payload, self.type, self.size)

    def __iter__(self):
        """."""  # noqa: DAR101,DAR201
        self._index = 0 if self.data else self.size
        return self

    def __next__(self):
        """ Returns the next value from thew shape data member """   # noqa: DAR201,DAR401
        if self._index < self.size:
            self._index += 1
            assert self.data
            return self.data[self._index - 1]
        # End of Iteration
        raise StopIteration

    def get(self, pos):
        """Return the value at index pos of the shape """   # noqa: DAR101,DAR201
        return self.data[pos] if pos < self.size else 0

    @property
    def bhwc(self):
        """Return the shape as a tuple according the expected format"""
        # noqa: DAR201,DAR401
        if self.type == AiBufferShape.SHAPE_BHWC:
            return tuple(self.data[i] for i in range(self.size))
        if self.size == 5:
            return (self.data[AiBufferShape.N_BATCHES],
                    self.data[AiBufferShape.HEIGHT],
                    self.data[AiBufferShape.WIDTH],
                    self.data[AiBufferShape.DEPTH],
                    self.data[AiBufferShape.CHANNELS])
        if self.size == 6:
            return (self.data[AiBufferShape.N_BATCHES],
                    self.data[AiBufferShape.HEIGHT],
                    self.data[AiBufferShape.WIDTH],
                    self.data[AiBufferShape.DEPTH],
                    self.data[AiBufferShape.EXTENSION],
                    self.data[AiBufferShape.CHANNELS])
        return (self.data[AiBufferShape.N_BATCHES],
                self.data[AiBufferShape.HEIGHT],
                self.data[AiBufferShape.WIDTH],
                self.data[AiBufferShape.CHANNELS])

    @classmethod
    def to_bcwh(cls, shape):
        """Convert BHWC order to BCWH order"""
        # noqa: DAR201,DAR101,DAR401
        if len(shape) == 4:
            return (shape[0], shape[3], shape[2], shape[1])  # BHWC -> BCWH
        if len(shape) == 5:
            return (shape[0], shape[4], shape[2], shape[1], shape[3])  # BHWDC -> BCWHD
        if len(shape) == 6:
            return (shape[0], shape[5], shape[2], shape[1], shape[3], shape[4])   # BHWDEC -> BCWHDE
        raise ValueError("Invalid shape size - only [4,5,6] is supported")


class AiBuffer(Printable):
    """Wrapper for C 'ai_buffer' struct."""
    _fields_ = [('format', AiBufferFormat),
                ('data', ct.c_void_p),
                ('meta_info', ct.POINTER(AiBufferMetaInfo)),
                ('flags', ct.c_uint, 32),
                ('size', ct.c_uint, 32),
                ('shape', AiBufferShape)]

    def __init__(self, fmt, shape, data=None, meta_info=None, shape_order=AiBufferShape.SHAPE_BHWC):
        """Class constructor"""     # noqa: DAR101
        # shape should be stored as BCWH type
        if shape_order == AiBufferShape.SHAPE_BHWC:
            shape = AiBufferShape.to_bcwh(shape)
            shape_order = AiBufferShape.SHAPE_BCWH
        self._shape = np.asarray(shape, dtype=np.uint32)
        shape_data = ct.cast(self._shape.ctypes.data, ct.POINTER(ct.c_uint))
        ai_shape = AiBufferShape(type=shape_order, size=len(self._shape), data=shape_data)
        hwc_shape = ai_shape.bhwc
        n_items = np.prod(hwc_shape[:-1]) * AiBuffer.pad(fmt, hwc_shape[-1])
        super(AiBuffer, self).__init__(fmt, data, meta_info, flags=0x0, size=n_items, shape=ai_shape)

    @property
    def size(self):
        """Return the size, number of items"""
        # noqa: DAR201
        return self.size

    @property
    def n_batches(self):
        """Legacy support to n_batches deprecated field"""
        # noqa: DAR201
        return self.shape.get(AiBufferShape.N_BATCHES)

    @property
    def height(self):
        """Legacy support to height deprecated field"""
        # noqa: DAR201
        return self.shape.get(AiBufferShape.HEIGHT)

    @property
    def width(self):
        """Legacy support to width deprecated field"""
        # noqa: DAR201
        return self.shape.get(AiBufferShape.WIDTH)

    @property
    def channels(self):
        """Legacy support to channels deprecated field"""
        # noqa: DAR201
        return self.shape.get(AiBufferShape.CHANNELS)

    @property
    def depth(self):
        """Legacy support to depth deprecated field"""
        # noqa: DAR201
        return self.shape.get(AiBufferShape.DEPTH)

    @classmethod
    def pad(cls, fmt, value):
        """Manage buffer padding"""
        # noqa: DAR101,DAR201
        assert value >= 0
        if fmt.value in {AiBufferFormat.AI_BUFFER_FORMAT_S1, AiBufferFormat.AI_BUFFER_FORMAT_U1}:
            return (value + 31) // value if value > 0 else 0
        return value

    @classmethod
    def from_ndarray(cls, ndarray, fmt=None, shape=None):
        """Wrap a Numpy array's internal buffer to an AiBuffer without copy."""
        # noqa: DAR101,DAR201,DAR401

        #
        # Only arrays with 4 dimensions or less can be mapped because AiBuffer
        # encodes only 4 dimensions; the Numpy dtype is mapped to the
        # corresponding AiBuffer type.
        #
        assert shape is not None
        # if len(ndarray.shape) > 4:
        #    raise ValueError("Arrays with more than 4 dimensions are not supported")

        # if shape is None:
        #    ndshape = ndarray.shape[:-1] + (1, ) * (4 - len(ndarray.shape)) + (ndarray.shape[-1],)
        # else:
        # ndshape = shape
        if fmt is None:
            fmt = AiBufferFormat.to_fmt(ndarray.dtype.type)
        # assert(len(ndshape) == 4)
        # print("  [from_ndarray] : {}".format(fmt))
        return cls(fmt, shape, data=ct.cast(ndarray.ctypes.data, ct.c_void_p))

    @classmethod
    def from_bytes(cls, bytebuf):
        """Wrap a Python bytearray object to AiBuffer."""
        # noqa: DAR101,DAR201,DAR401
        if not isinstance(bytebuf, bytearray):
            raise RuntimeError("Buffer is not a stream of bytes.")

        data = (ct.POINTER(ct.c_byte * len(bytebuf))).from_buffer(bytebuf)
        return cls(AiBufferFormat.AI_BUFFER_FORMAT_U8, 1, 1, 1, len(bytebuf), ct.c_void_p(ct.addressof(data)))

    def to_ndarray(self):
        """Wrap the AiBuffer internal buffer into a Numpy array object."""  # noqa: DAR101,DAR201,DAR401

        #
        # # The AiBuffer type is mapped to the corresponding Numpy's dtype.
        # The memory is managed by the code which instantiated the AiBuffer;
        # create a copy with 'ndarray.copy()' if the buffer was instantiated by
        # the C library before unloading the library.
        #
        dtype = self.format.to_np_type()
        shape = (self.n_batches, self.height, self.width, self.channels)
        size = np.dtype(dtype).itemsize * int(np.prod(shape))

        # WARNING: the memory is owned by the C library
        # don't let it go out of scope before copying the array content
        data = ct.cast(self.data, ct.POINTER(ct.c_byte * size))
        bytebuf = np.ctypeslib.as_array(data.contents, (size, ))

        return np.reshape(np.frombuffer(bytebuf, dtype), shape)


class AiBufferArray(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_buffer_array' struct."""
    _fields_ = [('flags', ct.c_uint, 16),
                ('size', ct.c_uint, 16),
                ('buffer', ct.POINTER(AiBuffer))]

    def get_size(self):
        """Return total size in bytes of a buffer array"""  # noqa: DAR201
        size = sum([self.buffer[i].channels for i in range(self.size)])
        return size


class AiIoTensor(Printable):
    """Wrapper for C 'ai_io_tensor' struct"""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [
        ('format', AiBufferFormat),
        ('data', ct.POINTER(ct.c_uint8)),
        ('scale', ct.c_float),
        ('zeropoint', ct.c_int32),
        ('shape', AiBufferShape)
    ]

    def to_ndarray(self):
        """Wrap the AiBuffer internal buffer into a Numpy array object."""  # noqa: DAR101,DAR201,DAR401

        #
        # The AiBuffer type is mapped to the corresponding Numpy's dtype.
        # The memory is managed by the code which instantiated the AiBuffer;
        # create a copy with 'ndarray.copy()' if the buffer was instantiated by
        # the C library before unloading the library.
        #
        io_tensor = IOTensor(self.format, self.shape.bhwc)
        size = io_tensor.get_c_size_in_bytes()

        # WARNING: the memory is owned by the C library
        # don't let it go out of scope before copying the array content
        data = ct.cast(self.data, ct.POINTER(ct.c_byte * size))
        bytebuf = np.ctypeslib.as_array(data.contents, (size, ))

        return np.frombuffer(bytebuf, io_tensor.dtype)


class AiObserverIoNode(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_observer_node' struct"""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [
        ('c_idx', ct.c_uint16),
        ('type', ct.c_uint16),
        ('id', ct.c_uint16),
        ('n_tensors', ct.c_uint16),
        ('elapsed_ms', ct.c_float),
        ('tensors', ct.POINTER(AiIoTensor)),
    ]
    AI_OBSERVER_NONE_EVT = 0
    AI_OBSERVER_INIT_EVT = (1 << 0)
    AI_OBSERVER_PRE_EVT = (1 << 1)
    AI_OBSERVER_POST_EVT = (1 << 2)
    AI_OBSERVER_FIRST_EVT = (1 << 8)
    AI_OBSERVER_LAST_EVT = (1 << 9)


class AiError(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_error' struct."""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [
        ('type', ct.c_uint, 8),
        ('code', ct.c_uint, 24)
    ]

    def __str__(self):
        """Return human description of the error"""  # noqa: DAR101,DAR201,DAR401
        return 'type={} code={}'.format(self.type, self.code)


class AiNetworkBuffers(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_network_buffers' struct."""
    _fields_ = [('map_signature', ct.c_uint, 32),
                ('map_weights', AiBufferArray),
                ('map_activations', AiBufferArray)]

    MAP_SIGNATURE = 0xA1FACADE


class AiNetworkParams(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_network_params' struct."""  # noqa: DAR101,DAR201,DAR401
    _fields_ = [
        ('params', AiBuffer),
        ('activations', AiBuffer)
    ]


class AiNetworkParamsUnion(ct.Union):   # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_network_params' struct."""
    _fields_ = [('params', AiNetworkParams),
                ('buffers', AiNetworkBuffers)]

    def valid_signature(self):
        # noqa: DAR201
        """Check signature of the union datastruct to determine struct semantic"""
        return self.buffers.map_signature == AiNetworkBuffers.MAP_SIGNATURE

    def get_buffers(self):
        # noqa: DAR201
        """Return info about params as AIBufferArray objects"""
        if self.valid_signature():
            params = self.buffers.map_weights
            activations = self.buffers.map_activations
        else:
            params = AiBufferArray(0x0, 1, ct.pointer(self.params.params))
            activations = AiBufferArray(0x0, 1, ct.pointer(self.params.activations))

        assert isinstance(params, AiBufferArray) and isinstance(activations, AiBufferArray)
        return params, activations

    def get_params(self):
        # noqa: DAR201
        """Return info about params as AIBuffer objects"""
        if self.valid_signature():
            def _buffer_array_to_ai_buffer(buffer_array):
                assert isinstance(buffer_array, AiBufferArray)
                res = AiBuffer(AiBufferFormat.AI_BUFFER_FORMAT_U8, (1, 1, 1, buffer_array.get_size()), None, None)
                return res

            params = _buffer_array_to_ai_buffer(self.buffers.map_weights)
            activations = _buffer_array_to_ai_buffer(self.buffers.map_activations)
        else:
            params = self.params.params
            activations = self.params.activations

        assert isinstance(params, AiBuffer) and isinstance(activations, AiBuffer)

        return params, activations

    def get_ai_buffers(self):
        # noqa: DAR201
        """Return info about params as a list of AIBuffer objects"""
        if self.valid_signature():
            def _buffer_array_to_ai_buffer_list(buffer_array):
                assert isinstance(buffer_array, AiBufferArray)
                res = []
                for i in range(buffer_array.size):
                    buff = buffer_array.buffer[i]
                    res.append(AiBuffer(buff.format, (buff.n_batches, buff.height, buff.width, buff.channels),
                                        buff.data, None))
                return res
            params = _buffer_array_to_ai_buffer_list(self.buffers.map_weights)
            activations = _buffer_array_to_ai_buffer_list(self.buffers.map_activations)
        else:
            params = [self.params.params]
            activations = [self.params.activations]

        return params, activations


class AiNetworkReport(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C 'ai_network_report' struct."""
    _fields_ = [
        ('model_name', ct.c_char_p),
        ('model_signature', ct.c_char_p),
        ('model_datetime', ct.c_char_p),
        ('compile_datetime', ct.c_char_p),
        ('runtime_revision', ct.c_char_p),
        ('runtime_version', AiPlatformVersion),
        ('tool_revision', ct.c_char_p),
        ('tool_version', AiPlatformVersion),
        ('tool_api_version', AiPlatformVersion),
        ('api_version', AiPlatformVersion),
        ('interface_api_version', AiPlatformVersion),
        ('n_macc', ct.c_uint64),
        ('n_inputs', ct.c_uint, 16),
        ('n_outputs', ct.c_uint, 16),
        ('inputs', ct.POINTER(AiBuffer)),
        ('outputs', ct.POINTER(AiBuffer)),
        ('buffers', AiNetworkParamsUnion),
        ('n_nodes', ct.c_uint, 32),
        ('signature', ct.c_uint, 32)
    ]

    @property
    def c_model_name(self):
        """Support to new field c_model_name"""
        # noqa: DAR201
        return self.model_name

    @property
    def c_compile_datetime(self):
        """Support to new field c_compile_datetime"""
        # noqa: DAR201
        return self.compile_datetime

    @property
    def c_model_datetime(self):
        """Support to new field c_model_datetime"""
        # noqa: DAR201
        return self.model_datetime


class StAiReturnCode(ct.c_int32):
    """ Class corresponding to C stai_return_code """

    # see stai/include/stai.h
    STAI_SUCCESS = 0x000000
    STAI_RUNNING_NO_WFE = 0x000010
    STAI_RUNNING_WFE = 0x000011
    STAI_DONE = 0x000012
    STAI_ERROR_GENERIC = 0x020000
    STAI_ERROR_NETWORK_INVALID_API_ARGUMENTS = 0x020001
    STAI_ERROR_NETWORK_INVALID_CONTEXT_HANDLE = 0x030000
    STAI_ERROR_NETWORK_INVALID_CONTEXT_SIZE = 0x030001
    STAI_ERROR_NETWORK_INVALID_CONTEXT_ALIGNMENT = 0x030002
    STAI_ERROR_NETWORK_INVALID_INFO = 0x030010
    STAI_ERROR_NETWORK_INVALID_RUN = 0x030020
    STAI_ERROR_NETWORK_INVALID_RUNTIME = 0x030030
    STAI_ERROR_NETWORK_INVALID_ACTIVATIONS_PTR = 0x040000
    STAI_ERROR_NETWORK_INVALID_ACTIVATIONS_NUM = 0x040001
    STAI_ERROR_NETWORK_INVALID_IN_PTR = 0x040010
    STAI_ERROR_NETWORK_INVALID_IN_NUM = 0x040011
    STAI_ERROR_NETWORK_INVALID_OUT_PTR = 0x040020
    STAI_ERROR_NETWORK_INVALID_OUT_NUM = 0x040021
    STAI_ERROR_NETWORK_INVALID_STATES_PTR = 0x040030
    STAI_ERROR_NETWORK_INVALID_STATES_NUM = 0x040031
    STAI_ERROR_NETWORK_INVALID_WEIGHTS_PTR = 0x040040
    STAI_ERROR_NETWORK_INVALID_WEIGHTS_NUM = 0x040041
    STAI_ERROR_NETWORK_INVALID_CALLBACK = 0x040050
    STAI_ERROR_NOT_IMPLEMENTED = 0x040060
    STAI_ERROR_INVALID_BUFFER_ALIGNMENT = 0x040070

    # asynchronous execution errors
    STAI_ERROR_NOT_CURRENT_NETWORK = 0x050000
    STAI_ERROR_NETWORK_STILL_RUNNING = 0x050001

    # platform (de-)init errors
    STAI_ERROR_STAI_INIT_FAILED = 0x060000
    STAI_ERROR_STAI_DEINIT_FAILED = 0x060001

    def __eq__(self, other):
        return int(self.value) == other

    def __str__(self):
        value = int(self.value)
        if value == self.STAI_SUCCESS:
            return 'SUCCESS'
        if value == self.STAI_ERROR_NETWORK_INVALID_ACTIVATIONS_PTR:
            return 'ERROR_NETWORK_INVALID_ACTIVATIONS_PTR'
        if value == self.STAI_ERROR_NETWORK_INVALID_ACTIVATIONS_NUM:
            return 'ERROR_NETWORK_INVALID_ACTIVATIONS_NUM'
        if value == self.STAI_ERROR_NETWORK_INVALID_IN_PTR:
            return 'ERROR_NETWORK_INVALID_IN_PTR'
        if value == self.STAI_ERROR_NETWORK_INVALID_OUT_PTR:
            return 'ERROR_NETWORK_INVALID_OUT_PTR'
        return str(value)


class StAiFormat(ct.c_int32):
    """ Class corresponding to C stai return code """
    STAI_FORMAT_NONE = 0x00000040
    STAI_FORMAT_FLOAT16 = 0x00820840
    STAI_FORMAT_FLOAT32 = 0x00821040
    STAI_FORMAT_FLOAT64 = 0x00822040

    STAI_FORMAT_U1 = 0x000400c0
    STAI_FORMAT_U4 = 0x00040240
    STAI_FORMAT_U8 = 0x00040440
    STAI_FORMAT_U16 = 0x00040840
    STAI_FORMAT_U32 = 0x00041040

    STAI_FORMAT_S1 = 0x008400c0
    STAI_FORMAT_S4 = 0x00840240
    STAI_FORMAT_S8 = 0x00840440
    STAI_FORMAT_S16 = 0x00840840
    STAI_FORMAT_S32 = 0x00841040

    STAI_FORMAT_Q = 0x00840040
    STAI_FORMAT_Q3 = 0x00840243
    STAI_FORMAT_Q7 = 0x00840447
    STAI_FORMAT_Q15 = 0x0084084f

    STAI_FORMAT_UQ = 0x00040040
    STAI_FORMAT_UQ3 = 0x00040243
    STAI_FORMAT_UQ7 = 0x00040447
    STAI_FORMAT_UQ15 = 0x0004084f

    STAI_FORMAT_BOOL = 0x00060440

    """ STAI Buffer Format Flags """
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

    # = STAI_BUFFER_FMT_TYPE_XX definition
    TYPE_NONE = 0x0
    TYPE_FLOAT = 0x1
    TYPE_Q = 0x2
    TYPE_INTEGER = 0x2
    TYPE_BOOL = 0x3
    TYPE_FXP = 0xF

    FLAG_CONST = 0x1 << 30
    FLAG_STATIC = 0x1 << 29
    FLAG_IS_IO = 0x1 << 27

    def __eq__(self, other):
        """Check if two objects are equal"""  # noqa: DAR101,DAR201,DAR401
        if isinstance(other, StAiFormat):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return False

    def to_dict(self):
        # noqa: DAR101,DAR201,DAR401
        """Return a dict with fmt field values"""
        fmt = self.value
        _dict = {
            'sign': (fmt >> self.SIGN_SHIFT) & self.SIGN_MASK,
            'type': (fmt >> self.TYPE_ID_SHIFT) & self.TYPE_ID_MASK,
        }
        _dict['float'] = 1 if self.is_float() else 0
        _dict['bits'] = self.bits()
        _dict['fbits'] = self.fbits()
        _dict['np_type'] = self.to_np_type()
        _dict['packet_mode'] = self.packed()
        return _dict

    def is_supported(self):
        """
        Return if not None

        Returns
        -------
        bool
            True if not None
        """
        return self.value != self.STAI_FORMAT_NONE

    def is_bool(self):
        # noqa: DAR101,DAR201,DAR401
        """Is a bool type"""
        fmt = self.value
        return (fmt >> self.TYPE_ID_SHIFT) & self.TYPE_ID_MASK == self.TYPE_BOOL

    def is_float(self):
        # noqa: DAR101,DAR201,DAR401
        """Is a float type"""
        fmt = self.value
        return (fmt >> self.TYPE_ID_SHIFT) & self.TYPE_ID_MASK == self.TYPE_FLOAT

    def is_integer(self):
        """
        Returns if self is an integer type

        Returns
        -------
        bool
            If self is integer
        """
        if self.value in [self.STAI_FORMAT_S1, self.STAI_FORMAT_S4, self.STAI_FORMAT_S8, self.STAI_FORMAT_S16,
                          self.STAI_FORMAT_S32]:
            return True
        if self.value in [self.STAI_FORMAT_U1, self.STAI_FORMAT_U4, self.STAI_FORMAT_U8, self.STAI_FORMAT_U16,
                          self.STAI_FORMAT_U32]:
            return True
        return False

    def to_np_type(self):
        """
        Convert a format described by StAiFormat into numpy array

        Returns
        -------
        np.dtype
            A numpy type

        Raises
        ------
        NotImplementedError
            If format string is not recognized
        """
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

        msg_ = f'STAI type ({_type}/{_bits}/{_sign}) to numpy type not supported'
        raise NotImplementedError(msg_)

    def bits(self):
        """
        Return the number of bits

        Returns
        -------
        int
            The number of bits
        """
        if self.is_bool():
            return 1
        fmt = self.value
        return (fmt >> self.BITS_SHIFT) & self.BITS_MASK

    def fbits(self):
        """
        Return the number of fraction bits

        Returns
        -------
        int
            The number of fraction bits
        """
        fmt = self.value
        return ((fmt >> self.FBITS_SHIFT) & self.FBITS_MASK) - 64

    def is_packed(self):
        """
        Return if self is a packed format

        Returns
        -------
        True
            If self is a packed format
        """
        return self.value in {self.STAI_FORMAT_S1, self.STAI_FORMAT_U1}

    def packed(self):
        """
        Return string for packed type

        Returns
        -------
        str
            Packed
        """
        bits = self.bits()
        return '{}b'.format(bits) if bits < 8 and self.is_packed() else ''

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
        AssertionError
            If the format has not an associated converter
        """
        fmt_enum = self.value
        if fmt_enum == self.STAI_FORMAT_BOOL:
            return AiBoolConverter(shape)
        elif fmt_enum in {self.STAI_FORMAT_S1, self.STAI_FORMAT_U1}:
            signed = fmt_enum == self.STAI_FORMAT_S1
            return Ai1b32bPackConverter(shape, pad_value=0, signed=signed)
        elif self.is_integer() and quant and quant['scale']:
            return AiQuantUniformConverter(shape, scale=quant['scale'], zp=quant['zero_point'], dtype=self.to_np_type())
        elif self.is_float() and self.bits() == 32:
            return AiIdentityConverter(shape)
        elif fmt_enum in {self.STAI_FORMAT_S32, self.STAI_FORMAT_U32, self.STAI_FORMAT_S8, self.STAI_FORMAT_U8}:
            return AiIdentityConverter(shape)
        else:
            raise AssertionError('Unexpected STAI format {}'.format(str(self.value)))


StAiFlags = ct.c_int32


StAiNetwork = ct.c_uint8


StAiSize = ct.c_int32


class StAiArray(Printable):  # pylint: disable=too-few-public-methods
    """Base class for all stai_array_*"""
    def tolist(self):
        """
        Returns the content of self transformed into a list

        Returns
        -------
        list
            The content of self transformed into a list
        """

        data = getattr(self, 'data')
        size = getattr(self, 'size')
        data = [data[index] for index in range(size)]
        return data


class StAiArrayF32(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_f32"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_float))
    ]


class StAiArrayS8(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_s16"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_int8))
    ]


class StAiArrayS16(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_s16"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_int16))
    ]


class StAiArrayS32(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_s32"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_int32))
    ]


class StAiArrayU8(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_s16"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_uint8))
    ]


class StAiArrayU16(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_s16"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_uint16))
    ]


class StAiArrayU32(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_s32"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_uint32))
    ]


class StAiArrayPtr(StAiArray):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_array_s32"""
    _fields_ = [
        ('size', StAiSize),
        ('data', ct.POINTER(ct.c_void_p))
    ]


StAiShape = StAiArrayS32


class StAiTensor(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_tensor"""
    _fields_ = [
        ('size_bytes', StAiSize),
        ('flags', StAiFlags),
        ('format', StAiFormat),
        ('shape', StAiShape),
        ('scale', StAiArrayF32),
        ('zeropoint', StAiArrayS16),
        ('name', ct.c_char_p)
    ]

    @property
    def data(self):
        """Address of data"""
        # noqa: DAR101,DAR201,DAR401
        return self.address

    def _get_converter(self):
        shape = (self.shape.data[index] for index in range(self.shape.size))
        if self.format.value == StAiFormat.STAI_FORMAT_BOOL:
            return AiBoolConverter(shape)
        elif self.format.value in {StAiFormat.STAI_FORMAT_S1, StAiFormat.STAI_FORMAT_U1}:
            signed = self.format.value == StAiFormat.STAI_FORMAT_S1
            return Ai1b32bPackConverter(shape, pad_value=0, signed=signed)
        elif self.format.value in {StAiFormat.STAI_FORMAT_S8, StAiFormat.STAI_FORMAT_U8, StAiFormat.STAI_FORMAT_U16, StAiFormat.STAI_FORMAT_S16} and self.scale:
            return AiQuantUniformConverter(shape, scale=self.scale, zp=self.zeropoint, dtype=self.format.to_np_type)
        elif self.format.is_float() and self.format.bits() == 32:
            return AiIdentityConverter(shape)
        elif self.format.value in {StAiFormat.STAI_FORMAT_S32, StAiFormat.STAI_FORMAT_U32}:
            return AiIdentityConverter(shape)
        else:
            raise AssertionError('Unexpected format {}'.format(self.format.value))

    def get_c_size(self):
        """
        Return the number of elements for the storage

        Returns
        -------
        The number of elements for the storage
        """
        shape = tuple(self.shape.data[index] for index in range(self.shape.size))
        return self._get_converter().get_c_size(shape)

    def get_c_shape(self):
        """
        Return the c shape of the storage

        Returns
        -------
        The shape of the storage
        """
        shape = tuple(self.shape.data[index] for index in range(self.shape.size))
        return self._get_converter().get_c_shape(shape)

    def get_scale_zeropoint(self):
        """Return a dict of the scale/zero_point keys"""  # noqa: DAR101,DAR201,DAR401
        if self.scale.size and self.zeropoint.size:
            if self.format.value in {StAiFormat.STAI_FORMAT_S8, StAiFormat.STAI_FORMAT_S1}:
                zp_ = np.int8(ct.cast(self.zeropoint.data, ct.POINTER(ct.c_int8))[0])
            elif self.format.value in {StAiFormat.STAI_FORMAT_U8, StAiFormat.STAI_FORMAT_U1}:
                zp_ = np.uint8(ct.cast(self.zeropoint.data, ct.POINTER(ct.c_uint8))[0])
            elif self.format.value == StAiFormat.STAI_FORMAT_S16:
                zp_ = np.int16(ct.cast(self.zeropoint.data, ct.POINTER(ct.c_int16))[0])
            elif self.format.value == StAiFormat.STAI_FORMAT_U16:
                zp_ = np.uint16(ct.cast(self.zeropoint.data, ct.POINTER(ct.c_uint16))[0])
            else:
                raise ValueError('Format not recognized: {}'.format(self.format.value))
            return {"scale": self.scale.data[0], "zero_point": zp_}
        else:
            return {"scale": None, "zero_point": np.uint8(0)}

    def to_ndarray(self, data):
        """
        Wrap data into a Numpy array object

        Parameters
        ----------
        data
            Pointer to actual data

        Returns
        -------
        A numpy array wrapping data
        """
        io_tensor = IOTensor(self.format, self.shape.tolist())
        size = io_tensor.get_c_size_in_bytes()
        data = ct.cast(data, ct.POINTER(ct.c_byte * size))
        bytebuf = np.ctypeslib.as_array(data.contents, (size,))
        return np.frombuffer(bytebuf, io_tensor.dtype)


StAiTensorPtr = ct.POINTER(StAiTensor)


class StAiVersion(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_version"""
    _fields_ = [
        ('major', ct.c_uint8),
        ('minor', ct.c_uint8),
        ('micro', ct.c_uint8),
        ('reserved', ct.c_uint8)
    ]

    def to_ver(self):
        """Return 3d tuple with the version"""  # noqa: DAR201
        return (self.major, self.minor, self.micro)


class StAiNetworkInfo(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_network_info"""
    _fields_ = [
        ('model_signature', ct.c_char_p),

        ('c_compile_datetime', ct.c_char_p),
        ('c_model_name', ct.c_char_p),
        ('c_model_datetime', ct.c_char_p),
        ('c_model_signature', ct.c_uint32),

        ('runtime_version', StAiVersion),
        ('tool_version', StAiVersion),
        ('api_version', StAiVersion),

        ('n_macc', ct.c_uint64),

        ('n_nodes', ct.c_uint32),

        ('flags', ct.c_int32),

        ('n_inputs', ct.c_uint16),
        ('n_outputs', ct.c_uint16),
        ('n_activations', ct.c_uint16),
        ('n_weights', ct.c_uint16),
        ('n_states', ct.c_uint16),

        ('inputs', StAiTensorPtr),
        ('outputs', StAiTensorPtr),
        ('activations', StAiTensorPtr),
        ('weights', StAiTensorPtr),
        ('states', StAiTensorPtr)
    ]


StAiNetworkInfoPtr = ct.POINTER(StAiNetworkInfo)


StAiNetworkPtr = ct.POINTER(StAiNetwork)


StAiPtr = ct.c_void_p


class StAiRunMode(ct.c_int32):
    """ Class corresponding to C stai run mode """
    MODE_SYNC = 0x1
    MODE_ASYNC = 0x2


STAI_FLAG_PREALLOCATED = (0x1 << 0)

STAI_FLAG_CHANNEL_FIRST = (0x1 << 6)
STAI_FLAG_CHANNEL_LAST = (0x1 << 7)
STAI_FLAG_HAS_BATCH = (0x1 << 8)

STAI_FLAG_ACTIVATIONS = (0x1 << 26)
STAI_FLAG_INPUTS = (0x1 << 27)
STAI_FLAG_OUTPUTS = (0x1 << 28)
STAI_FLAG_STATES = (0x1 << 29)


class StAiFlagsDef(Flag):
    """ Class corresponding to C stai flags (see stai.h) """
    FLAG_NONE = 0x0
    FLAG_PREALLOCATED = 0x1 << 0
    FLAG_REPLACEABLE = 0x1 << 2
    FLAG_OVERRIDE = 0x1 << 3
    FLAG_CHANNEL_FIRST = 0x1 << 6
    FLAG_CHANNEL_LAST = 0x1 << 7
    FLAG_HAS_BATCH = 0x1 << 8
    FLAG_ACTIVATIONS = 0x1 << 26
    FLAG_INPUTS = 0x1 << 27
    FLAG_OUTPUTS = 0x1 << 28
    FLAG_STATES = 0x1 << 29
    FLAG_WEIGHTS = 0x1 << 30

    def __and__(self, val):
        return int(self.value) & val


##############################################################################
StAiEventId = ct.c_int32


StAiEventPayloadPtr = ct.c_void_p


StAiEventCallback = ct.CFUNCTYPE(None, ct.c_void_p, StAiEventId, StAiEventPayloadPtr)


class StAiEventNodeStartStop(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_event_node_start_stop"""
    _fields_ = [
        ('node_id', ct.c_int32),
        ('buffers', StAiArrayPtr)
    ]


StAiEventNodeStartStopPtr = ct.POINTER(StAiEventNodeStartStop)


CoreTimerTs = ct.c_uint32


class CoreTimer(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C core_timer"""
    _fields_ = [
        ('name', ct.c_char_p),
        ('start', CoreTimerTs),
        ('elapsed', CoreTimerTs)
    ]


class StAiNodeDetails(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_node_details"""
    _fields_ = [
        ('id', ct.c_int32),
        ('type', ct.c_int16),
        ('input_tensors', StAiArrayS32),
        ('output_tensors', StAiArrayS32)
    ]


StAiNodeDetailsPtr = ct.POINTER(StAiNodeDetails)


class StAiNetworkDetails(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper for C stai_network_details"""
    _fields_ = [
        ('tensors', StAiTensorPtr),
        ('nodes', StAiNodeDetailsPtr),
        ('n_nodes', ct.c_uint32)
    ]


StAiNetworkDetailsPtr = ct.POINTER(StAiNetworkDetails)


class StAiObserverCtx(Printable):  # pylint: disable=too-few-public-methods
    """Wrapper to C stai_observer_ctx"""
    _fields_ = [
        ('elapsed_time', ct.c_float),
        ('timer', CoreTimer),
        ('nested_callback', StAiEventCallback),
        ('details', StAiNetworkDetailsPtr),
        ('c_idx', ct.c_int32)
    ]


StAiObserverCtxPtr = ct.POINTER(StAiObserverCtx)


STAI_EVENT_NODE_START = 0x01
STAI_EVENT_NODE_STOP = 0x02


class AiDllBackend:
    """
    Backend ensuring the wrapping of the shared lib functions to Python functions
    """
    def __init__(self, libname, dir_path, logger, name='network', reload=False):
        """Constructor"""  # noqa: DAR101,DAR201,DAR401

        self._shared_lib = None  # library object when loaded
        self._shared_obs_lib = None
        self._logger = logger
        self._tmp_lib = None

        path_name = get_library_name(os.path.join(dir_path, libname))

        self._tmp_lib = _TemporaryLibrary(path_name, copy_mode=reload)
        self._logger.debug(f'loaded shared library: {self._tmp_lib.full_path} ({bool(reload)})')

        self._shared_lib = self._tmp_lib.load_library()

        try:
            self._shared_obs_lib = np.ctypeslib.load_library('libai_observer', dir_path)
        except OSError:
            self._shared_obs_lib = None

        self.stai_apis = {}
        self.ai_network_create = None
        # First try legacy binding should be checked first to check if we are in compatibility mode
        while True:
            try:
                self.ai_network_create = _wrap_api(
                    self._shared_lib, f'ai_{name}_create',
                    AiError, [ct.POINTER(ct.c_void_p), ct.POINTER(AiBuffer)])
            except AttributeError:
                if name == 'network':
                    # try to use the name used to generate the name of the file
                    _, _, name_, _ = _split(libname)
                    name = name_.replace('libai_', '')
                    if name == 'network':
                        # Name of the file is also network
                        break
                else:
                    break
            else:
                break
        # Legacy binding
        if self.ai_network_create:
            # Wrapper for 'ai_network_get_error' C API
            self.ai_network_get_error = _wrap_api(
                self._shared_lib, f'ai_{name}_get_error',
                AiError, [ct.c_void_p])

            # Wrapper for 'ai_network_init' C API
            self.ai_network_init = _wrap_api(
                self._shared_lib, f'ai_{name}_init',
                ct.c_bool, [ct.c_void_p, ct.POINTER(AiNetworkParamsUnion)])

            # Wrapper for 'ai_network_destroy' C API
            self.ai_network_destroy = _wrap_api(
                self._shared_lib, f'ai_{name}_destroy', ct.c_void_p, [ct.c_void_p])

            # Wrapper for 'ai_network_get_report' C API (NEW)
            try:
                self.ai_network_get_report = _wrap_api(
                    self._shared_lib, f'ai_{name}_get_report',
                    ct.c_bool, [ct.c_void_p, ct.POINTER(AiNetworkReport)])
            except AttributeError as exc:
                msg = 'ai_network_get_report() not available'
                self._logger.debug(msg)
                self.ai_network_get_report = None
                raise HwIOError(msg) from exc

            # Wrapper for 'ai_network_run' C API
            self.ai_network_run = _wrap_api(
                self._shared_lib,
                f'ai_{name}_run', ct.c_int,
                [ct.c_void_p,
                 ct.POINTER(AiBuffer),
                 ct.POINTER(AiBuffer)])

            # Wrapper for 'ai_network_data_activations_buffer_get' C API
            self.ai_network_data_activations_buffer_get = _wrap_api(
                self._shared_lib,
                f'ai_{name}_data_activations_buffer_get', AiBuffer, [ct.c_void_p])

            # Wrapper for 'ai_network_data_weights_buffer_get' C API
            self.ai_network_data_weights_buffer_get = _wrap_api(
                self._shared_lib,
                f'ai_{name}_data_weights_buffer_get', AiBuffer, [ct.c_void_p])

            # Wrapper for 'ai_network_data_params_get' C API (NEW)
            try:
                self.ai_network_data_params_get = _wrap_api(
                    self._shared_lib, f'ai_{name}_data_params_get',
                    ct.c_bool, [ct.POINTER(AiNetworkParamsUnion)])
            except AttributeError as exc:
                # msg = 'ai_network_data_params_get() not available'
                msg = f'{exc} not available'
                self._logger.debug(msg)
                self.ai_network_data_params_get = None
                raise HwIOError(msg) from exc

            # Wrapper for 'ai_observer_io_node_cb' C API
            self.ai_observer_io_node_cb = ct.CFUNCTYPE(
                ct.c_uint32,
                ct.c_uint32,
                ct.POINTER(AiObserverIoNode)
            )

            if self._shared_obs_lib is None:
                return

            # Wrapper for 'ai_platform_observer_io_register' C API
            self.ai_platform_observer_io_register = _wrap_api(
                self._shared_obs_lib,
                'ai_platform_observer_io_register',
                ct.c_bool,
                [ct.c_void_p,
                 self.ai_observer_io_node_cb,
                 ct.c_uint32])

            # Wrapper for 'ai_platform_observer_io_unregister' C API
            self.ai_platform_observer_io_unregister = _wrap_api(
                self._shared_obs_lib,
                'ai_platform_observer_io_unregister',
                ct.c_bool,
                [ct.c_void_p,
                 self.ai_observer_io_node_cb])
        else:
            stai_apis = [
                (StAiSize, 'get_context_size', []),
                (StAiReturnCode, 'get_info', [StAiNetworkPtr, StAiNetworkInfoPtr]),
                (StAiReturnCode, 'get_inputs', [StAiNetworkPtr, ct.POINTER(StAiPtr), ct.POINTER(StAiSize)]),
                (StAiReturnCode, 'get_outputs', [StAiNetworkPtr, ct.POINTER(StAiPtr), ct.POINTER(StAiSize)]),
                (StAiReturnCode, 'init', [StAiNetworkPtr]),
                (StAiReturnCode, 'run', [StAiNetworkPtr, StAiRunMode]),
                (StAiReturnCode, 'set_activations', [StAiNetworkPtr, ct.POINTER(StAiPtr), StAiSize]),
                (StAiReturnCode, 'set_states', [StAiNetworkPtr, ct.POINTER(StAiPtr), StAiSize]),
                (StAiReturnCode, 'set_inputs', [StAiNetworkPtr, ct.POINTER(StAiPtr), StAiSize]),
                (StAiReturnCode, 'set_outputs', [StAiNetworkPtr, ct.POINTER(StAiPtr), StAiSize]),
                (StAiReturnCode, 'set_weights', [StAiNetworkPtr, ct.POINTER(StAiPtr), StAiSize]),
                (StAiReturnCode, 'set_callback', [StAiNetworkPtr, StAiEventCallback, ct.c_void_p])
            ]
            try:
                for stai_api in stai_apis:
                    return_type = stai_api[0]
                    function_name = 'stai_' + name + '_' + stai_api[1]
                    arguments = stai_api[2]
                    self.stai_apis[stai_api[1]] = _wrap_api(self._shared_lib, function_name, return_type, arguments)
                    self._logger.debug('%s found', function_name)
            except AttributeError as exc:
                raise HwIOError(f'{stai_api} cannot be found') from exc
            # Bind call back
            if self._shared_obs_lib:
                self.stai_apis['stai_callback_per_layer'] = _wrap_api(self._shared_obs_lib, 'stai_callback_per_layer',
                                                                      None,
                                                                      [ct.c_void_p, StAiEventId, StAiEventPayloadPtr])
                try:
                    self.stai_apis['stai_network_details'] = StAiNetworkDetails.in_dll(self._shared_lib,
                                                                                       'g_' + name + '_details')
                except AttributeError:
                    self.stai_apis['stai_network_details'] = None

    def capabilities(self, name):
        """Return list with the capabilities"""  # noqa: DAR101,DAR201,DAR401
        if self._shared_obs_lib is not None and not self.stai_apis:
            # Check if we are in emulation mode
            try:
                _wrap_api(
                    self._shared_lib, f'stai_{name}_init',
                    StAiReturnCode, [StAiNetworkPtr])
                # Legacy APIs + StAI APIs -> Emulation mode
                return [AiRunner.Caps.IO_ONLY]
            except AttributeError:
                # Legacy only
                return [AiRunner.Caps.IO_ONLY, AiRunner.Caps.PER_LAYER, AiRunner.Caps.PER_LAYER_WITH_DATA]
        caps = [AiRunner.Caps.IO_ONLY, AiRunner.Caps.PER_LAYER]
        if self.stai_apis['stai_network_details']:
            caps += [AiRunner.Caps.PER_LAYER_WITH_DATA]
        return caps

    def release(self):
        """Release, upload the shared libraries"""  # noqa: DAR101,DAR201,DAR401
        if self._tmp_lib is not None:
            self._tmp_lib.unload_library()
            self._tmp_lib = None
            self._shared_lib = None
        if self._shared_obs_lib is not None:
            del self._shared_obs_lib
            self._shared_obs_lib = None

    def __del__(self):
        self.release()


class AiDllDriver(AiRunnerDriver):
    """Class to handle the DLL"""

    def __init__(self, parent):
        """Constructor"""  # noqa: DAR101,DAR201,DAR401
        self._backend = None
        self._handle = None
        self._dll_name = None
        self._name = None
        self._activations = None
        self._states = None
        self._io_from_act = True
        self._info = None  # cache the description of the models
        self._s_dur = 0.0
        self._profiler = None
        self._callback = None
        self._stai_observer_callback = None
        self._cookie_callback = None
        self._weights_ptr_map = None
        self._buffers_data = None
        self._mode = AiRunner.Mode.IO_ONLY
        self.ghosted_observer_io_node_cb = None
        self._tens_inputs = []
        self._tens_outputs = []
        self._guarded_inputs = []
        self._io_extra_bytes = False
        self._in_buffers = []
        self._out_buffers = []
        self._states = []
        self._use_legacy_api = False
        super(AiDllDriver, self).__init__(parent)

    @staticmethod
    def is_valid(file_path):
        """Check if the provided path is a valid path"""
        # noqa: DAR101,DAR201,DAR401
        if isinstance(file_path, str):
            res, dll_path, _ = check_and_find_stm_ai_dll(file_path)
            return res, dll_path
        return False, ''

    @property
    def is_connected(self):
        """Indicate if the DLL is loaded"""
        # noqa: DAR101,DAR201,DAR401
        return bool(self._backend)

    @property
    def capabilities(self):
        """Return list with the capabilities"""
        # noqa: DAR101,DAR201,DAR401
        if self.is_connected:
            return self._backend.capabilities(self._name)
        return []

    def _load_weights(self, weights):
        """Load weight as a list of bytearrays"""   # noqa: DAR101,DAR201,DAR401
        buffers_data, weights = [], weights if isinstance(weights, list) else [weights]

        for weight in weights:
            # Use the data from a binary file
            if isinstance(weight, str) and weight.endswith('.bin') and os.path.isfile(weight):
                self._logger.debug(' loading weights from binary file: {}'.format(weight))
                with open(weight, 'rb') as bin_file:
                    buffers_data.append(bytearray(bin_file.read()))
                    bin_file.close()
            # Use the data from a simple bytearray object
            elif isinstance(weight, bytearray):
                self._logger.debug(' loading weights from bytearray object size: {}'.format(len(weight)))
                buffers_data.append(weight)
            # Use the data from the X-CUBE-AI code generator v6+
            elif 'buffer_data' in weight:
                self._logger.debug(' loading weights from STM.AI object size: {}'.format(len(weight['buffer_data'])))
                buffers_data.append(weight['buffer_data'])
            else:
                raise HwIOError('Invalid weights object: binary file, bytearray, STM.AI object.. are expected')

        assert all([isinstance(b, bytearray) for b in buffers_data])
        buffers_size = sum([len(b) for b in buffers_data])

        return buffers_data, buffers_size

    def _set_c_buffer_with_remap_table(self, buffers_data):
        """Create and set a remap table for multiple buffers"""  # noqa: DAR101,DAR201,DAR401
        assert all([isinstance(b, bytearray) for b in buffers_data])

        size, count = sum([len(b) for b in buffers_data]), len(buffers_data) + 2

        # Create list of c-type object with the provided buffers
        #  note: minimum 8-bytes size is requested to map a bytearray
        buffers = []
        for i, buffer in enumerate(buffers_data):
            if len(buffer) < 8:  # minimum size should be 8 for ctype map
                buffers_data[i] = buffer + bytearray(8 - len(buffer))
            buffers.append((ct.POINTER(ct.c_uint8 * len(buffers_data[i]))).from_buffer(buffers_data[i]))

        if len(buffers_data) == 1:
            # As a simple buffer(binary format) w/o remap entries
            return ct.cast(ct.addressof(buffers[0]), ct.POINTER(ct.c_uint8)), None

        msg = f' Building the c-remap table, nb_entry=1+{count - 2}+1 ({size} bytes)'
        self._logger.debug(msg)

        # Create the magic marker
        magic_marker = ct.cast(_AI_MAGIC_MARKER, ct.POINTER(ct.c_uint8))

        # Build and init the remap table
        #  note: the params_ptr_map object is returned to be owned (ref_count>0) by the caller
        #        before to use it by the DLL.
        buffers_ptr = [magic_marker]
        buffers_ptr += [ct.cast(ct.addressof(b), ct.POINTER(ct.c_uint8)) for b in buffers]
        buffers_ptr += [magic_marker]

        params_ptr_map = (ct.POINTER(ct.c_uint8) * count)(*buffers_ptr)

        return (ct.cast(ct.addressof(params_ptr_map), ct.POINTER(ct.c_uint8)), params_ptr_map)

    def _set_params_data(self, params, weights):
        """Set weights buffers"""  # noqa: DAR101,DAR201,DAR401
        self._weights_ptr_map = None
        self._buffers_data, buffers_size = self._load_weights(weights)
        expected_size = params.get_size()
        buffers_count, params_count = len(self._buffers_data), params.size

        if buffers_count != params_count:
            msg = f'Provided weights count are incompatible (got: {buffers_count} expected: {params_count})'
            raise HwIOError(msg)

        if buffers_size != expected_size:
            msg = f'Provided weights size are incompatible (got: {buffers_size} expected: {expected_size})'
            raise HwIOError(msg)

        if buffers_size <= 0:
            return

        has_data_count = sum([bool(params.buffer[i].data) for i in range(params_count)])
        if has_data_count > 0 and has_data_count != params_count:
            self._logger.warning(f'Detect mixed weights configuration: #{has_data_count}/{params_count} has data.')

        for i in range(params_count):
            buffer_i = params.buffer[i]
            buffer_size, param_size = len(self._buffers_data[i]), buffer_i.channels
            buffer_i_empty = not buffer_i.data

            if buffer_size != param_size:
                msg = f'Provided weights #{i} size are incompatible (got: {buffer_size} expected: {param_size})'
                raise HwIOError(msg)

            if not buffer_i_empty and param_size > 0:
                self._logger.debug(f' Weights buffer #{i}/{params_count} from the DLL is used')
            elif buffer_i_empty and not param_size:
                raise HwIOError(f' Weights buffer #{i}/{params_count} is empty')
            elif buffer_i_empty and param_size:
                self._logger.debug(f' Weights buffer #{i}/{params_count} from STM.AI is used')
                if len(self._buffers_data[i]) < 8:  # minimum size should be 8 for ctype map
                    self._buffers_data[i] += bytearray(8 - len(self._buffers_data[i]))
                data_ptr = (ct.POINTER(ct.c_uint8 * len(self._buffers_data[i]))).from_buffer(self._buffers_data[i])
                params.buffer[i].data = ct.cast(ct.addressof(data_ptr), ct.c_void_p)

        self._logger.debug(f'Loaded #{params_count} Network Weights: loaded {buffers_size} Bytes.')

    def _set_activations_data(self, activations):
        """Allocate and set activations buffer"""  # noqa: DAR101,DAR201,DAR401
        align = 8  # buffer is 8-bytes aligned
        self._activations = []

        has_data_count = sum([bool(activations.buffer[i].data) for i in range(activations.size)])
        if has_data_count > 0 and has_data_count != activations.size:
            msg = 'Detect mixed activations configuration: #{}/{} has data.'.format(has_data_count, activations.size)
            self._logger.debug(msg)

        for i in range(activations.size):
            shape = (1, 1, 1, _rounded_up(activations.buffer[i].channels, align))
            msg = ' allocating {} bytes for activations buffer #{}/{} {}'.format(shape[3] * align, i + 1,
                                                                                 activations.size,
                                                                                 activations.buffer[i].channels)
            self._logger.debug(msg)
            if shape[3] > 0:
                # network has activations buffers
                activations_buffer = np.zeros(shape, dtype=np.uint64)
                # activations_buffer = np.empty(shape, dtype=np.uint64)
                self._activations.append(np.require(activations_buffer, dtype=np.uint64,
                                                    requirements=['C', 'O', 'W', 'A']))
                activations_ptr = self._activations[i].ctypes.data
            else:
                self._activations.append(None)
                activations_ptr = None
            assert len(self._activations) == (i + 1)
            activations.buffer[i].data = ct.cast(activations_ptr, ct.c_void_p)

    def _bootstrap_network_params(self, weights):
        """
        Bind network model params to network

        Parameters
        ----------
        weights
            The weight to be bound

        Raises
        ------
        HwIOError
            If weights are not compatible with the network
        """
        self._buffers_data, buffers_size = self._load_weights(weights)

        expected_size = sum([self._info.weights[weight_index].size_bytes
                             for weight_index in range(self._info.n_weights)])

        buffers_count, params_count = len(self._buffers_data), self._info.n_weights

        if buffers_count != params_count:
            msg = f'Provided weights count are incompatible (got: {buffers_count} expected: {params_count})'
            raise HwIOError(msg)

        if buffers_size != expected_size:
            msg = f'Provided weights size are incompatible (got: {buffers_size} expected: {expected_size})'
            raise HwIOError(msg)

        if buffers_size <= 0:
            return

        weight_pointers = []
        for weight_index in range(self._info.n_weights):
            # minimum size should be 8 for ctype map
            if len(self._buffers_data[weight_index]) < 8:
                self._buffers_data[weight_index] += bytearray(8 - len(self._buffers_data[weight_index]))
            data_ptr = (ct.POINTER(ct.c_uint8 * len(self._buffers_data[weight_index]))) \
                .from_buffer(self._buffers_data[weight_index])
            weight_pointers.append(ct.cast(ct.addressof(data_ptr), StAiPtr))

        weight_pointers = (StAiPtr * len(weight_pointers))(*weight_pointers)
        n_weights = len(weight_pointers)

        return_value = self._backend.stai_apis['set_weights'](
            ct.cast(self._handle, StAiNetworkPtr), ct.cast(weight_pointers, ct.POINTER(StAiPtr)),
            n_weights)
        self._logger.debug('Executed stai_%s_set_weights with outcome %s', self._name, return_value)
        if return_value != StAiReturnCode.STAI_SUCCESS:
            raise HwIOError('stai_{}_set_weights failed with error {}'
                            .format(self._name, str(return_value)))

    def _bootstrap_legacy_network_params(self, weights):
        """Get and bind network model params using supported APIs"""     # noqa: DAR101,DAR201,DAR401
        self._info = AiNetworkReport()
        res, params = None, AiNetworkParamsUnion()
        if self._backend.ai_network_data_params_get:
            res = self._backend.ai_network_data_params_get(ct.pointer(params))
        if not res:
            raise HwIOError('ai_network_data_params_get() failed')

        self._logger.debug(' activations buffer: {}'.format(params.buffers.map_activations.get_size()))
        self._logger.debug(' weights buffer: {}'.format(params.buffers.map_weights.get_size()))

        # set weights buffer(s)
        if not weights:
            # no weights are provided, should be available in the DLL
            buffers, _ = params.get_ai_buffers()
            for buff in buffers:
                if not bool(buff.data):
                    msg = 'Shared library should be generated with the weights'
                    raise HwIOError(msg)
        else:
            self._set_params_data(params.buffers.map_weights, weights)

        # set activations buffer
        self._set_activations_data(params.buffers.map_activations)

        return params

    def connect(self, desc=None, **kwargs):
        """Connect to the shared library"""  # noqa: DAR101,DAR201,DAR401

        self.disconnect()

        dll_name = kwargs.pop('dll_name', None)
        weights = kwargs.pop('weights', [])
        reload = kwargs.pop('reload', None)
        context = kwargs.pop('context', None)
        # internal_apis = str(context.get_internal_apis()).lower() if context else ''
        # public_apis = str(context.get_public_apis()).lower() if context else ''
        self._name = context.get_option('general.name') if context else 'network'
        details = context.get_option('validate.details') if context else None

        if reload is None:
            if os.environ.get('AI_RUNNER_FORCE_NO_DLL_COPY', None):
                reload = False
            else:
                reload = True

        if dll_name is None:
            dir_path, dll_name = os.path.split(desc)
        else:
            dir_path = desc

        self._logger.debug('loading {} (from {})'.format(dll_name, dir_path))
        try:
            self._backend = AiDllBackend(dll_name, dir_path, name=self._name, logger=self._logger, reload=reload)
        except Exception as ctx:  # pylint: disable=broad-except
            self._logger.debug('{}'.format(str(ctx)))
            self._backend = None
            raise HwIOError(str(ctx))

        self._dll_name = os.path.join(dir_path, dll_name)

        self._use_legacy_api = not self._backend.stai_apis
        self._logger.debug(f' capabilities: {self.capabilities}')

        if not self._use_legacy_api:
            network_context_size = self._backend.stai_apis['get_context_size']()

            self._handle = ct.ARRAY(StAiNetwork, network_context_size)()

            return_value = self._backend.stai_apis['init'](ct.cast(self._handle, StAiNetworkPtr))
            self._logger.debug('Executed stai_%s_init with outcome %s', self._name, return_value)
            if return_value != StAiReturnCode.STAI_SUCCESS:
                raise HwIOError('stai_{}_init failed with error {}'.format(self._name, str(return_value)))

            self._info = StAiNetworkInfo()
            self._logger.debug(str(ct.byref(self._info)))

            return_value = self._backend.stai_apis['get_info'](ct.cast(self._handle, StAiNetworkPtr),
                                                               ct.byref(self._info))
            self._logger.debug('Executed stai_%s_get_info with outcome %s', self._name, return_value)
            if return_value != StAiReturnCode.STAI_SUCCESS:
                raise HwIOError('stai_{}_get_info failed with error {}'.format(self._name, str(return_value)))
            self._logger.debug(str(ct.byref(self._info)))
            self._logger.debug('Network info %s', str(self._info))

            for idx in range(self._info.n_inputs):
                st_ai_tensor = self._info.inputs[idx]
                shape = st_ai_tensor.shape.tolist()
                # Second condition is workaround for batch in the middle
                if not st_ai_tensor.flags & STAI_FLAG_HAS_BATCH or shape[0] != 1:
                    shape = [1] + shape
                self._logger.debug(' inputs #{}: size={} shape={}'.format(idx + 1, np.prod(shape), shape))
                quant = st_ai_tensor.get_scale_zeropoint()
                io_tens = IOTensor(st_ai_tensor.format, shape, quant)
                io_tens.set_name('input_{}'.format(idx + 1))
                io_tens.set_tag('I.{}'.format(idx))
                self._logger.debug(f' -> {io_tens}')
                self._tens_inputs.append(io_tens)

            self._tens_outputs = []
            for idx in range(self._info.n_outputs):
                st_ai_tensor = self._info.outputs[idx]
                shape = st_ai_tensor.shape.tolist()
                # Second condition is workaround for batch in the middle
                if not st_ai_tensor.flags & STAI_FLAG_HAS_BATCH or shape[0] != 1:
                    shape = [1] + shape
                self._logger.debug(' outputs #{}: size={} shape={}'.format(idx + 1, np.prod(shape), shape))
                quant = st_ai_tensor.get_scale_zeropoint()
                io_tens = IOTensor(st_ai_tensor.format, shape, quant)
                io_tens.set_name('output_{}'.format(idx + 1))
                io_tens.set_tag('O.{}'.format(idx))
                self._logger.debug(f' -> {io_tens}')
                self._tens_outputs.append(io_tens)

            if not self._info.flags & STAI_FLAG_ACTIVATIONS:
                self._activations = []
                activation_pointers = []

                for activation_index in range(self._info.n_activations):
                    activation = self._info.activations[activation_index]
                    size = activation.shape.data[0]

                    shape = (size,)
                    activations_buffer = np.zeros(shape, dtype=np.uint64)
                    numpy_array = np.require(activations_buffer, dtype=np.uint64,
                                             requirements=['C', 'O', 'W', 'A'])
                    self._activations.append(numpy_array)
                    activation_ptr = numpy_array.ctypes.data
                    activation_pointers.append(ct.cast(activation_ptr, StAiPtr))

                activation_pointers = (StAiPtr * len(activation_pointers))(*activation_pointers)
                n_activations = len(activation_pointers)

                return_value = self._backend.stai_apis['set_activations'](
                    ct.cast(self._handle, StAiNetworkPtr), ct.cast(activation_pointers, ct.POINTER(StAiPtr)),
                    n_activations)
                self._logger.debug('Executed stai_%s_set_activations with outcome %s', self._name, return_value)
                if return_value != StAiReturnCode.STAI_SUCCESS:
                    raise HwIOError('stai_{}_set_activations failed with error {}'
                                    .format(self._name, str(return_value)))

            if not self._info.flags & STAI_FLAG_STATES:
                self._states = []
                state_pointers = []

                for state_index in range(self._info.n_states):
                    state = self._info.states[state_index]
                    size = state.shape.data[0]

                    shape = (size,)
                    states_buffer = np.zeros(shape, dtype=np.uint64)
                    numpy_array = np.require(states_buffer, dtype=np.uint64,
                                             requirements=['C', 'O', 'W', 'A'])
                    self._states.append(numpy_array)
                    state_ptr = numpy_array.ctypes.data
                    state_pointers.append(ct.cast(state_ptr, StAiPtr))

                state_pointers = (StAiPtr * len(state_pointers))(*state_pointers)
                n_states = len(state_pointers)

                return_value = self._backend.stai_apis['set_states'](
                    ct.cast(self._handle, StAiNetworkPtr), ct.cast(state_pointers, ct.POINTER(StAiPtr)),
                    n_states)
                self._logger.debug('Executed stai_%s_set_states with outcome %s', self._name, return_value)
                if return_value != StAiReturnCode.STAI_SUCCESS:
                    raise HwIOError('stai_{}_set_states failed with error {}'
                                    .format(self._name, str(return_value)))

            if self._info.flags & STAI_FLAG_INPUTS:
                n_inputs = self._info.n_inputs
                input_pointers = [0] * n_inputs
                input_pointers = (StAiPtr * n_inputs)(*input_pointers)
                return_value = self._backend.stai_apis['get_inputs'](
                    ct.cast(self._handle, StAiNetworkPtr), ct.cast(input_pointers, ct.POINTER(StAiPtr)),
                    ct.byref(ct.c_int32(n_inputs)))
                self._logger.debug('Executed stai_%s_get_inputs with outcome %s', self._name, return_value)
                if return_value != StAiReturnCode.STAI_SUCCESS:
                    raise HwIOError('stai_{}_get_inputs failed with error {}'
                                    .format(self._name, str(return_value)))
                for idx in range(self._info.n_inputs):
                    self._logger.debug('Setting address of input %s to %s', str(idx), str(input_pointers[idx]))
                    self._tens_inputs[idx].set_c_addr(input_pointers[idx])

            if self._info.flags & STAI_FLAG_OUTPUTS:
                n_outputs = self._info.n_outputs
                output_pointers = [0] * n_outputs
                output_pointers = (StAiPtr * n_outputs)(*output_pointers)
                return_value = self._backend.stai_apis['get_outputs'](
                    ct.cast(self._handle, StAiNetworkPtr), ct.cast(output_pointers, ct.POINTER(StAiPtr)),
                    ct.byref(ct.c_int32(n_outputs)))
                self._logger.debug('Executed stai_%s_get_outputs with outcome %s', self._name, return_value)
                if return_value != StAiReturnCode.STAI_SUCCESS:
                    raise HwIOError('stai_{}_get_outputs failed with error {}'
                                    .format(self._name, str(return_value)))
                for idx in range(self._info.n_outputs):
                    self._tens_outputs[idx].set_c_addr(output_pointers[idx])

            if weights:
                self._bootstrap_network_params(weights)

            if AiRunner.Caps.PER_LAYER in self.capabilities and (details is None or details != AiRunner.Mode.IO_ONLY):
                @StAiEventCallback
                def nested_observer_cb(cookie, event_id, event_payload):
                    """
                    Python callback used by stai_callack per layer

                    Parameters
                    ----------
                    cookie
                        The network context passed to the callback

                    event_id
                        The type of the event

                    event_payload
                        The node context passed to the callback

                    Raises
                    ------
                    HwIOError
                        If network details information is not coherent
                    """
                    full_validation = \
                        self._mode & AiRunner.Mode.PER_LAYER_WITH_DATA == AiRunner.Mode.PER_LAYER_WITH_DATA and\
                        self._profiler
                    context = ct.cast(cookie, StAiObserverCtxPtr).contents
                    payload = ct.cast(event_payload, StAiEventNodeStartStopPtr).contents
                    c_idx = context.c_idx
                    if c_idx == 0 and event_id & STAI_EVENT_NODE_START:
                        self._s_dur = 0.0
                        self._logger.debug('Reset duration')
                    elif event_id & STAI_EVENT_NODE_STOP:
                        self._logger.debug('Previous duration %s', str(self._s_dur))
                        self._s_dur += context.elapsed_time
                        self._logger.debug('Updated duration to %s', str(self._s_dur))
                        profiler = self._profiler
                        if profiler:
                            details = context.details.contents
                            node_details = details.nodes[c_idx]
                            if c_idx == len(profiler['c_nodes']) and details:
                                self._logger.debug('First time executed layer %s', str(c_idx))
                                io_tensors = []
                                output_buffers = payload.buffers.tolist()
                                if len(output_buffers) != node_details.output_tensors.size:
                                    raise HwIOError(
                                        'Mismatch between number of output buffers and output tensors: {} vs. {}'
                                        .format(str(payload.buffers.size), str(node_details.output_tensors.size)))
                                shapes = []
                                types = []
                                scales = []
                                zeropoints = []
                                features = []
                                for output_tensor_index in range(payload.buffers.size):
                                    output_tensor_id = node_details.output_tensors.data[output_tensor_index]
                                    output_tensor = details.tensors[output_tensor_id]
                                    shape = output_tensor.shape.tolist()
                                    shapes.append(shape)
                                    types.append(output_tensor.format.to_np_type())
                                    scale = output_tensor.scale.tolist()
                                    if len(scale) > 1:
                                        raise HwIOError('Found activation tensor with multiple scales')
                                    elif len(scale) == 1:
                                        scale = scale[0]
                                    else:
                                        scale = None
                                    scales.append(scale)
                                    zeropoint = output_tensor.zeropoint.tolist()
                                    if len(zeropoint) > 1:
                                        raise HwIOError('Found activation tensor with multiple zeropoints')
                                    elif len(zeropoint) == 1:
                                        zeropoint = zeropoint[0]
                                    else:
                                        zeropoint = None
                                    zeropoints.append(zeropoint)
                                    shape = output_tensor.shape.tolist()
                                    io_ten = IOTensor(output_tensor.format, shape,
                                                      {'scale': scale,
                                                       'zero_point': zeropoint})
                                    io_ten.set_name('stai_tens_n_{}_{}'.format(c_idx, output_tensor_index))
                                    io_ten.set_tag('N.{}.{}'.format(c_idx, output_tensor_index))
                                    io_tensors.append(io_ten)
                                    if self._logger.level >= logging.DEBUG:
                                        self._logger.debug(f'cb: {io_ten}')
                                    if full_validation:
                                        feature = \
                                            output_tensor.to_ndarray(output_buffers[output_tensor_index]).copy()
                                        feature = feature.reshape((1,) + feature.shape)
                                    else:
                                        feature = np.array([], dtype=output_tensor.format.to_np_type())
                                    features.append(feature)

                                item = {
                                    'c_durations': [context.elapsed_time],
                                    'clks': [],
                                    'name': f'ai_node_{c_idx}',
                                    'm_id': node_details.id,
                                    'layer_type': node_details.type & 0x7FFF,
                                    'layer_desc': stm_ai_node_type_to_str(node_details.type & 0x7FFF),
                                    'type': types,
                                    'shape': shapes,
                                    'scale': scales,
                                    'zero_point': zeropoints,
                                    'io_tensors': io_tensors,
                                    'data': features,
                                }
                                profiler['c_nodes'].append(item)

                            else:
                                features = []
                                item = profiler['c_nodes'][c_idx]
                                if full_validation:
                                    output_buffers = payload.buffers.tolist()
                                    for output_tensor_index, output_buffer in enumerate(output_buffers):
                                        output_tensor_id = node_details.output_tensors.data[output_tensor_index]
                                        output_tensor = details.tensors[output_tensor_id]
                                        feature = output_tensor.to_ndarray(output_buffer)
                                        feature = feature.reshape((1,) + feature.shape)
                                        features.append(feature)
                                else:
                                    for output_tensor in item['io_tensors']:
                                        feature = np.array([], dtype=output_tensor.dtype)
                                        features.append(feature)

                                for idx, _ in enumerate(features):
                                    item['data'][idx] = np.append(item['data'][idx], features[idx], axis=0)
                                item['c_durations'].append(context.elapsed_time)
                            # End of last node
                            if c_idx == details.n_nodes - 1:
                                profiler['c_durations'].append(self._s_dur)

                self._stai_observer_callback = nested_observer_cb

                core_timer = CoreTimer()
                ct.byref(self._backend.stai_apis['stai_network_details'])
                self._cookie_callback = StAiObserverCtx(
                    0.0,
                    core_timer,
                    self._stai_observer_callback,
                    ct.cast(ct.byref(self._backend.stai_apis['stai_network_details']), StAiNetworkDetailsPtr),
                    -1
                )

                return_value = self._backend.stai_apis['set_callback'](
                    ct.cast(self._handle, StAiNetworkPtr),
                    ct.cast(self._backend.stai_apis['stai_callback_per_layer'], StAiEventCallback),
                    ct.byref(self._cookie_callback)
                )

                if return_value != StAiReturnCode.STAI_SUCCESS:
                    raise HwIOError('stai_{}_get_outputs failed with error {}'
                                    .format(self._name, str(return_value)))
            return True

        else:

            # Create an instance of the c-network
            self._handle = ct.c_void_p()
            try:
                error = self._backend.ai_network_create(ct.pointer(self._handle), None)
            except Exception as ctx:  # pylint: disable=broad-except
                self._logger.debug('{}'.format(str(ctx)))
                raise HwIOError(str(ctx))

            if error.code:
                msg = 'Unable to create the instance: {}'.format(stm_ai_error_to_str(error.code, error.type))
                self._logger.debug(msg)
                raise HwIOError(msg)
            self._logger.debug(' created instance: {}'.format(stm_ai_error_to_str(error.code, error.type)))

            # legacy API detection
            self._info = AiNetworkReport()
            # network init bootstrap with 7.1.0 supported APIs
            params_union = self._bootstrap_legacy_network_params(weights)

            # Initialize the c-network
            self._backend.ai_network_init(self._handle, ct.pointer(params_union))
            error = self._backend.ai_network_get_error(self._handle)
            err_msg = stm_ai_error_to_str(error.code, error.type)
            if error.code:
                msg = f'ai_network_init() failed\n AiError - {err_msg}'
                raise HwIOError(msg)
            self._logger.debug(f' initialized instance: {err_msg}')

            if params_union.valid_signature():
                # get the updated net report using newly supported APIs
                self._backend.ai_network_get_report(self._handle, ct.pointer(self._info))
            else:
                raise AssertionError('Signature is not valid')

            self._tens_inputs = []
            for idx in range(self._info.n_inputs):
                buffer = self._info.inputs[idx]
                shape = buffer.shape.bhwc
                self._logger.debug(f' inputs #{idx + 1}: size={buffer.size} shape={buffer.shape}/{shape}')
                io_tens = IOTensor(buffer.format.value, shape, self._get_scale_zeropoint(buffer))
                io_tens.set_c_addr(buffer.data)
                io_tens.set_name(f'input_{idx + 1}')
                io_tens.set_tag(f'I.{idx}')
                self._logger.debug(f' -> {io_tens}')
                self._tens_inputs.append(io_tens)

            self._tens_outputs = []
            for idx in range(self._info.n_outputs):
                buffer = self._info.outputs[idx]
                shape = buffer.shape.bhwc
                self._logger.debug(f' outputs #{idx + 1}: size={buffer.size} shape={buffer.shape}/{shape}')
                io_tens = IOTensor(buffer.format.value, shape, self._get_scale_zeropoint(buffer))
                io_tens.set_c_addr(buffer.data)
                io_tens.set_name(f'output_{idx + 1}')
                io_tens.set_tag(f'O.{idx}')
                self._logger.debug(f' -> {io_tens}')
                self._tens_outputs.append(io_tens)

            if AiRunner.Caps.PER_LAYER not in self.capabilities:
                return True

            @ct.CFUNCTYPE(ct.c_uint32, ct.c_uint32, ct.POINTER(AiObserverIoNode))
            def ghosted_observer_io_node_cb(flags, node):
                if flags & AiObserverIoNode.AI_OBSERVER_PRE_EVT:
                    self._io_node_pre_evt(flags, node)
                if flags & AiObserverIoNode.AI_OBSERVER_POST_EVT:
                    self._io_node_post_evt(flags, node)
                return 0

            self.ghosted_observer_io_node_cb = ghosted_observer_io_node_cb

            mode_ = AiObserverIoNode.AI_OBSERVER_PRE_EVT | AiObserverIoNode.AI_OBSERVER_POST_EVT
            self._logger.debug('registering ghosted observer')
            self._backend.ai_platform_observer_io_register(self._handle,
                                                           self.ghosted_observer_io_node_cb,
                                                           mode_)

            # at this point the model is ready to be used
        return True

    def _io_node_pre_evt(self, flags, node):
        """Pre-evt IO node call-back"""  # noqa: DAR101,DAR201,DAR401
        if flags & AiObserverIoNode.AI_OBSERVER_FIRST_EVT == AiObserverIoNode.AI_OBSERVER_FIRST_EVT:
            self._s_dur = 0.0
        else:
            self._s_dur += node[0].elapsed_ms
        if self._mode == AiRunner.Mode.IO_ONLY:
            return

        if self._callback:
            node_ = node[0]
            inputs = []
            for idx in range(node_.n_tensors):
                tens = node_.tensors[idx]
                inputs.append(tens.to_ndarray())
            extra_ = {'m_id': node_.id, 'layer_type': node_.type & 0x7FFF}
            self._callback.on_node_begin(node_.c_idx, inputs, logs=extra_)

    def _io_node_post_evt(self, flags, node):
        """Post-evt IO node call-back"""  # noqa: DAR101,DAR201,DAR401
        profiler = self._profiler
        node_ = node[0]
        self._s_dur += node_.elapsed_ms
        if self._mode == AiRunner.Mode.IO_ONLY:
            return

        io_tensors, shapes, features, types, scales, zeropoints = [], [], [], [], [], []
        for idx in range(node_.n_tensors):
            tens_ = node_.tensors[idx]
            shape = tens_.shape.bhwc
            if self._mode & AiRunner.Mode.PER_LAYER_WITH_DATA == AiRunner.Mode.PER_LAYER_WITH_DATA and\
                    (profiler or self._callback):
                feature = tens_.to_ndarray().copy()
            else:
                feature = np.array([], dtype=tens_.format.to_np_type())
            shapes.append(shape)

            types.append(tens_.format.to_np_type())
            scales.append(tens_.scale)
            zeropoints.append(tens_.zeropoint)
            io_tens = IOTensor(tens_.format.value, shapes[-1], {"scale": scales[-1], "zero_point": zeropoints[-1]})
            io_tens.set_name(f'ai_tens_n_{node_.c_idx}_{idx}')
            io_tens.set_tag(f'N.{node_.c_idx}.{idx}')
            io_tensors.append(io_tens)
            if feature.size:
                feature = feature.reshape(io_tensors[-1].get_c_shape())
            if self._logger.level >= logging.DEBUG:
                self._logger.debug(f'cb:post_evt:{node_.c_idx} -> {io_tens} data={feature.size}')

            features.append(feature)

        if profiler:
            if node_.c_idx >= len(profiler['c_nodes']):
                item = {
                    'c_durations': [node_.elapsed_ms],
                    'clks': [],
                    'name': f'ai_node_{node_.c_idx}',
                    'm_id': node_.id,
                    'layer_type': node_.type & 0x7FFF,
                    'layer_desc': stm_ai_node_type_to_str(node_.type & 0x7FFF),
                    'type': types,
                    'shape': shapes,
                    'scale': scales,
                    'zero_point': zeropoints,
                    'io_tensors': io_tensors,
                    'data': features if features is not None else None,
                }
                profiler['c_nodes'].append(item)
            else:
                item = profiler['c_nodes'][node_.c_idx]
                item['c_durations'].append(node_.elapsed_ms)
                for idx, _ in enumerate(features):
                    item['data'][idx] = np.append(item['data'][idx], features[idx], axis=0)

            if flags & AiObserverIoNode.AI_OBSERVER_LAST_EVT == AiObserverIoNode.AI_OBSERVER_LAST_EVT:
                profiler['c_durations'].append(self._s_dur)

        if self._callback:
            extra_ = {
                'm_id': node_.id,
                'layer_type': node_.type & 0x7FFF,
                'shape': shapes,
                'c_duration': node_.elapsed_ms
            }
            self._callback.on_node_end(node_.c_idx, features if features is not None else None, logs=extra_)

    def discover(self, flush=False):
        """Build the list of the available model"""  # noqa: DAR101,DAR201,DAR401
        if self._backend:
            return [self._info.c_model_name.decode('UTF-8')]
        return []

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        if self._backend:
            self._logger.debug(' releasing backend ({})...'.format(self._backend))
            # self._backend.ai_network_destroy(self._handle)
            if self.ghosted_observer_io_node_cb and AiRunner.Caps.PER_LAYER in self.capabilities:
                self._backend.ai_platform_observer_io_unregister(self._handle,
                                                                 self.ghosted_observer_io_node_cb)
            self._handle = None
            self._backend.release()
        self._activations = None
        self._weights_ptr_map = None
        self._buffers_data = None
        self._backend = None

    def short_desc(self):
        """Return human readable description"""  # noqa: DAR101,DAR201,DAR401
        io_ = self._dll_name
        return f'DLL Driver v{__version__} - Direct Python binding ({io_})'

    def _to_runtime(self, model_info):
        """Return a dict with the runtime attributes"""  # noqa: DAR101,DAR201,DAR401
        return {
            'protocol': f'DLL Driver v{__version__} - Direct Python binding',
            'name': f'{RT_ST_AI_NAME} (legacy api)' if self._use_legacy_api else f'{RT_ST_AI_NAME} (st-ai api)',
            'compiler': "",
            'version': model_info.runtime_version.to_ver(),
            'capabilities': self.capabilities,
            'tools_version': model_info.tool_version.to_ver(),
        }

    def _get_scale_zeropoint(self, buffer):
        """Return a dict of the scale/zero_point keys"""  # noqa: DAR101,DAR201,DAR401
        if buffer.meta_info:
            flags = buffer.meta_info[0].intq_info_list[0].flags
            entry = buffer.meta_info[0].intq_info_list[0].info[0]
            if flags & AiIntqInfoList.AI_BUFFER_META_FLAG_ZEROPOINT_S8:
                zp_ = np.int8(ct.cast(entry.zeropoint, ct.POINTER(ct.c_int8))[0])
            elif flags & AiIntqInfoList.AI_BUFFER_META_FLAG_ZEROPOINT_U8:
                zp_ = np.uint8(ct.cast(entry.zeropoint, ct.POINTER(ct.c_uint8))[0])
            elif flags & AiIntqInfoList.AI_BUFFER_META_FLAG_ZEROPOINT_S16:
                zp_ = np.int16(ct.cast(entry.zeropoint, ct.POINTER(ct.c_int16))[0])
            elif flags & AiIntqInfoList.AI_BUFFER_META_FLAG_ZEROPOINT_U16:
                zp_ = np.uint16(ct.cast(entry.zeropoint, ct.POINTER(ct.c_uint16))[0])
            else:
                raise ValueError('Flag not recognized')
            return {"scale": entry.scale[0], "zero_point": zp_}
        else:
            return {"scale": None, "zero_point": np.uint8(0)}

    def _get_io_tensors(self, buffers, io_tensors):
        """Return dict with descrion of the IO tensors"""  # noqa: DAR101,DAR201,DAR401
        items = []
        for idx, io_tensor in enumerate(io_tensors):
            buffer = buffers[idx]
            item = {
                'name': io_tensor.name,
                'shape': io_tensor.shape,
                'type': io_tensor.dtype,
                'io_tensor': io_tensor,
                'memory_pool': 'in activations buffer' if buffer.data else 'user'
            }
            item.update(io_tensor.quant_params)
            if not io_tensor.memory_pool:
                io_tensor.set_memory_pool(item['memory_pool'])
            items.append(item)
        return items

    def _get_mem_pools(self, prefix, params):
        """Return description of the pools"""  # noqa: DAR101,DAR201,DAR401
        items = []
        for idx, buffer in enumerate(params):
            item = {
                'name': '{}_{}'.format(prefix if prefix else 'tensor', idx + 1),
                'shape': (buffer.n_batches, buffer.height, buffer.width, buffer.channels),
                'type': buffer.format.to_np_type(),
            }
            items.append(item)
        return items

    def _model_to_dict(self, model_info):
        """Return a dict with the network info"""  # noqa: DAR101,DAR201,DAR401
        return {
            'name': model_info.c_model_name.decode('UTF-8'),
            'model_datetime': model_info.c_model_datetime.decode('UTF-8'),  # date of creation
            'compile_datetime': model_info.c_compile_datetime.decode('UTF-8'),  # date of compilation
            'hash': model_info.model_signature.decode('UTF-8'),
            'n_nodes': model_info.n_nodes,
            'macc': model_info.n_macc,
            'n_init_time': 0,
            'n_install_time': 0,
            'runtime': self._to_runtime(model_info),
            'device': {
                'desc': f'{platform.machine()}, {platform.processor()}, {platform.system()}',
                'dev_type': 'HOST',
                'dev_id': platform.machine() + ' ' + platform.processor(),
                'system': platform.system(),
                'machine': platform.machine(),
            },
        }

    def get_info(self, c_name=None):
        """Return a dict with the network info of the given c-model"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_connected:
            return dict()

        model_dict = self._model_to_dict(self._info)
        model_dict['version'] = STAI_INFO_DICT_VERSION

        if self._use_legacy_api:
            params, activations = self._info.buffers.get_ai_buffers()
            model_dict['inputs'] = self._get_io_tensors(self._info.inputs, self._tens_inputs)
            model_dict['outputs'] = self._get_io_tensors(self._info.outputs, self._tens_outputs)
            model_dict['weights'] = sum([p.size for p in params])
            model_dict['activations'] = sum([p.size for p in activations])
            model_dict['mempools'] = {
                'params': self._get_mem_pools('params', params),
                'activations': self._get_mem_pools('act', activations)
            }
        else:
            model_dict['inputs'] = []

            def flags_to_str(val):
                str_flags_ = ','.join([flag_def.name.lower() for flag_def in list(StAiFlagsDef) if flag_def & val])
                return str_flags_

            model_dict['flags'] = flags_to_str(self._info.flags)

            for input_buffer_index in range(self._info.n_inputs):
                input_buffer = self._info.inputs[input_buffer_index]
                if input_buffer.name:
                    name = input_buffer.name
                else:
                    name = 'input_' + str(input_buffer_index + 1)
                shape = input_buffer.shape
                io_tensor = self._tens_inputs[input_buffer_index]
                input_dict = {
                    'name': name,
                    'shape': tuple((shape.data[index] for index in range(shape.size))),
                    'type': input_buffer.format.to_np_type(),
                    'size_bytes': input_buffer.size_bytes,
                    'io_tensor': io_tensor,
                    'memory_pool': 'in activations buffer' if self._info.flags & STAI_FLAG_INPUTS else 'user'
                }
                input_dict.update(io_tensor.quant_params)
                if not io_tensor.memory_pool:
                    io_tensor.set_memory_pool(input_dict['memory_pool'])
                model_dict['inputs'].append(input_dict)

            if len(model_dict['inputs']) == 0:
                raise AssertionError('Number of inputs is {}'.format(str(len(model_dict['inputs']))))

            model_dict['outputs'] = []

            for output_buffer_index in range(self._info.n_outputs):
                output_buffer = self._info.outputs[output_buffer_index]
                name = output_buffer.name
                if output_buffer.name:
                    name = output_buffer.name
                else:
                    name = 'output_' + str(output_buffer_index + 1)
                shape = output_buffer.shape
                io_tensor = self._tens_outputs[output_buffer_index]
                output_dict = {
                    'name': name,
                    'shape': tuple((shape.data[index] for index in range(shape.size))),
                    'type': output_buffer.format.to_np_type(),
                    'size_bytes': output_buffer.size_bytes,
                    'io_tensor': io_tensor,
                    'memory_pool': 'in activations buffer' if self._info.flags & STAI_FLAG_OUTPUTS else 'user'
                }
                output_dict.update(io_tensor.quant_params)
                if not io_tensor.memory_pool:
                    io_tensor.set_memory_pool(output_dict['memory_pool'])
                model_dict['outputs'].append(output_dict)

            if len(model_dict['outputs']) == 0:
                raise AssertionError('Number of outputs is {}'.format(str(len(model_dict['outputs']))))

            model_dict['mempools'] = {
                'params': [],
                'activations': []
            }

            activations_byte_size = 0
            for activation_index in range(self._info.n_activations):
                activation = self._info.activations[activation_index]
                size_bytes = activation.size_bytes
                buffer = {
                    'name': activation.name,
                    'shape': (1, 1, 1, size_bytes),
                    'type': np.uint8
                }
                activations_byte_size += size_bytes
                model_dict['mempools']['activations'].append(buffer)
            model_dict['activations'] = activations_byte_size
            weights_byte_size = 0
            for weight_index in range(self._info.n_weights):
                weight = self._info.weights[weight_index]
                size_bytes = weight.size_bytes
                buffer = {
                    'name': weight.name,
                    'shape': (1, 1, 1, size_bytes),
                    'type': np.uint8
                }
                weights_byte_size += size_bytes
                model_dict['mempools']['params'].append(buffer)
            model_dict['weights'] = weights_byte_size
        return model_dict

    def _prepare_inputs(self, inputs):
        """Check and prepare the inputs for the c-runtime"""  # noqa: DAR101,DAR201,DAR401
        c_inputs = []
        for idx in range(self._info.n_inputs):
            io_tensor = self._tens_inputs[idx]
            if io_tensor.c_addr and self._io_from_act:
                self._logger.debug('Creating array into activation for input %s at address %s', str(idx),
                                   str(io_tensor.c_addr))
                dst_ = _get_array_from_act(io_tensor, io_tensor.c_addr, inputs[idx])
                c_inputs.append(dst_)
            else:
                if self._io_extra_bytes:
                    self._guarded_inputs.append(GuardedNumpyArray(inputs[idx]))
                    c_inputs.append(self._guarded_inputs[-1]())
                else:
                    c_inputs.append(np.require(inputs[idx], dtype=inputs[idx].dtype,
                                               requirements=['C', 'O', 'W', 'A']))
        return c_inputs

    def _prepare_outputs(self):
        """Prepare the outputs"""  # noqa: DAR101,DAR201,DAR401
        c_outputs = []
        for idx in range(self._info.n_outputs):
            io_tensor = self._tens_outputs[idx]
            dtype = io_tensor.dtype
            if io_tensor.c_addr and self._io_from_act:
                out_ = _get_array_from_act(io_tensor, io_tensor.c_addr)
                c_outputs.append(out_)
            else:
                out = io_tensor.zeros()
                c_outputs.append(np.require(out, dtype=dtype,
                                            requirements=['C', 'O', 'W', 'A']))
        return c_outputs

    def _post_outputs(self, c_outputs):
        """Finalize the outputs"""  # noqa: DAR101,DAR201,DAR401
        outputs = []
        if self._use_legacy_api:
            for idx, tensor_io in enumerate(self._tens_outputs):
                if self._info.outputs[idx].data and self._io_from_act:
                    outputs.append(c_outputs[idx].copy().reshape(tensor_io.get_c_shape()))
                else:
                    outputs.append(c_outputs[idx].reshape(tensor_io.get_c_shape()))
        else:
            for output_index in range(self._info.n_outputs):
                output_buffer = self._info.outputs[output_index]
                shape = output_buffer.get_c_shape()
                if not output_buffer.flags & STAI_FLAG_HAS_BATCH or shape[0] != 1:
                    shape = (1,) + shape
                if output_buffer.flags & STAI_FLAG_PREALLOCATED:
                    outputs.append(c_outputs[output_index].copy().reshape(shape))
                else:
                    outputs.append(c_outputs[output_index].reshape(shape))
        return outputs

    def _post_inputs(self):
        """Finalize the inputs"""  # noqa: DAR101,DAR201,DAR401
        for idx, g_input in enumerate(self._guarded_inputs):
            elem = g_input
            self._guarded_inputs[idx] = None
            del elem
        self._guarded_inputs = []

    def _get_io_buffers(self, inputs, outputs):

        assert self._info.n_inputs == len(inputs) and self._info.n_outputs == len(outputs)

        self._in_buffers = []
        for idx, arr in enumerate(inputs):
            io_tensor = self._tens_inputs[idx]
            self._in_buffers.append(AiBuffer.from_ndarray(arr, io_tensor.raw_fmt, io_tensor.shape))

        in_ = (AiBuffer * len(self._in_buffers))(*self._in_buffers)

        self._out_buffers = []
        for idx, arr in enumerate(outputs):
            io_tensor = self._tens_outputs[idx]
            self._out_buffers.append(AiBuffer.from_ndarray(arr, io_tensor.raw_fmt, io_tensor.shape))

        out_ = (AiBuffer * len(self._out_buffers))(*self._out_buffers)

        return in_, out_

    def invoke_sample(self, s_inputs, **kwargs):
        """Invoke the c-model with a sample (batch_size = 1)"""  # noqa: DAR101,DAR201,DAR401
        if s_inputs[0].shape[0] != 1:
            raise HwIOError('Should be called with a batch size of 1')

        if kwargs.pop('disable_io_from_act', None) is not None:
            self._io_from_act = False
        else:
            self._io_from_act = True
        self._profiler = kwargs.pop('profiler', None)

        self._callback = kwargs.pop('callback', None)
        self._mode = kwargs.pop('mode', AiRunner.Mode.IO_ONLY)
        self._io_extra_bytes = kwargs.pop('io_extra_bytes', False)
        self._s_dur = 0.0

        self._mode &= ~AiRunner.Mode.FIXED_INPUT
        self._mode &= ~AiRunner.Mode.DEBUG

        self._logger.debug('Requested RUN mode: {}'.format(self._mode))

        if self._mode & AiRunner.Mode.PER_LAYER == AiRunner.Mode.PER_LAYER \
                and AiRunner.Caps.PER_LAYER not in self.capabilities:
            raise HwIOError('Code does not support validation per-layer')

        if self._mode & AiRunner.Mode.PER_LAYER_WITH_DATA == AiRunner.Mode.PER_LAYER_WITH_DATA \
                and AiRunner.Caps.PER_LAYER_WITH_DATA not in self.capabilities:
            raise HwIOError('Code does not support validation per-layer')

        c_inputs = self._prepare_inputs(s_inputs)
        c_outputs = self._prepare_outputs()
        if self._use_legacy_api:
            in_buffers, out_buffers = self._get_io_buffers(c_inputs, c_outputs)

            start_time = t.perf_counter()
            run_batches = self._backend.ai_network_run(self._handle, in_buffers, out_buffers)
            error = self._backend.ai_network_get_error(self._handle)
            elapsed_time = (t.perf_counter() - start_time) * 1000.0
            if run_batches != c_inputs[0].shape[0]:
                msg = 'ai_network_run() failed: executed {} samples instead of {}'.format(str(run_batches),
                                                                                          str(c_inputs[0].shape[0]))
                raise AiRunnerError(msg)
            if error.code:
                msg = 'ai_network_run() failed\n AiError - {}'.format(stm_ai_error_to_str(error.code, error.type))
                raise AiRunnerError(msg)
        else:
            if not self._info.flags & STAI_FLAG_INPUTS:
                input_pointers = []

                for c_input in c_inputs:
                    input_pointers.append(ct.cast(c_input.ctypes.data, StAiPtr))
                input_pointers = (StAiPtr * len(input_pointers))(*input_pointers)
                n_inputs = len(input_pointers)
                return_value = self._backend.stai_apis['set_inputs'](
                    ct.cast(self._handle, StAiNetworkPtr), ct.cast(input_pointers, ct.POINTER(StAiPtr)),
                    n_inputs)
                self._logger.debug('Executed stai_%s_set_inputs with outcome %s', self._name, return_value)
                if return_value != StAiReturnCode.STAI_SUCCESS:
                    raise HwIOError('stai_{}_set_inputs failed with error {}'.format(self._name, str(return_value)))
            if not self._info.flags & STAI_FLAG_OUTPUTS:
                output_pointers = []
                for c_output in c_outputs:
                    output_pointers.append(ct.cast(c_output.ctypes.data, StAiPtr))
                output_pointers = (StAiPtr * len(output_pointers))(*output_pointers)
                n_outputs = len(output_pointers)
                return_value = self._backend.stai_apis['set_outputs'](
                    ct.cast(self._handle, StAiNetworkPtr), ct.cast(output_pointers, ct.POINTER(StAiPtr)),
                    n_outputs)
                self._logger.debug('Executed stai_%s_set_outputs with outcome %s', self._name, return_value)
                if return_value != StAiReturnCode.STAI_SUCCESS:
                    raise HwIOError('stai_{}_set_outputs failed with error {}'.format(self._name, str(return_value)))
            if self._cookie_callback:
                setattr(self._cookie_callback, 'c_idx', -1)
            start_time = t.perf_counter()
            return_value = self._backend.stai_apis['run'](ct.cast(self._handle, StAiNetworkPtr), StAiRunMode.MODE_SYNC)
            elapsed_time = (t.perf_counter() - start_time) * 1000.0
            self._logger.debug('Executed stai_%s_run with outcome %s', self._name, return_value)
            if return_value != StAiReturnCode.STAI_SUCCESS:
                raise HwIOError('stai_{}_run failed with error {}'.format(self._info.model_name, str(return_value)))

        outputs = self._post_outputs(c_outputs)
        self._post_inputs()

        dur_ = elapsed_time
        if self._profiler:
            self._profiler['debug']['exec_times'].append(elapsed_time)
            if self._mode & AiRunner.Mode.PER_LAYER != AiRunner.Mode.PER_LAYER and\
                    self._mode & AiRunner.Mode.PER_LAYER_WITH_DATA != AiRunner.Mode.PER_LAYER_WITH_DATA:
                # field is not filled by the callback, IO_ONLY, external measure is used
                self._profiler['c_durations'].append(dur_)
            else:
                dur_ = self._s_dur
        return outputs, dur_


def test_buffers_bind():
    """."""
    # shape_tuple = np.asarray((1, 2, 3), dtype=np.uint32)
    # data = ct.cast(shape_tuple.ctypes.data, ct.POINTER(ct.c_uint))
    # print(shape_tuple, data)
    # shape = AiBufferShape(type=1, size=len(shape_tuple), data=data)
    # print(str(shape))

    nparrays = [np.zeros(shape=(2, 1, 3, 4), dtype=np.float32),
                np.ones(shape=(2, 1, 3, 4), dtype=np.float32)]
    buffers = (AiBuffer * 2)(AiBuffer(), AiBuffer())

    tmp_lib = np.ctypeslib.load_library('libruntime_dll', '')
    ai_buffers_bind = _wrap_api(tmp_lib, 'ai_buffers_bind', ct.c_float, [ct.POINTER(AiBuffer), ct.c_uint32])
    print("  [ai_buffers_bind]: {}".format(ai_buffers_bind))  # noqa: T001, T201

    for idx, buffer in enumerate(buffers):
        # noqa: T001
        buffers[idx] = buffer.from_ndarray(nparrays[idx])
        # buffer = buffers[idx]
        # buffer.n_batches = 1
        # buffer.channels = 8
        print("-- #{} ---------------".format(idx))  # noqa: T001,T201
        print("  Buffer shape:  ({}, {}, {}, {}) -> {}".format(buffer.n_batches, buffer.channels,  # noqa: T001,T201
                                                               buffer.width,
                                                               buffer.height, str(buffer.shape)))
        print("  Buffer fmt: {} data: {} meta: {}"  # noqa: T001,T201
              .format(buffer.format, buffer.data, buffer.meta_info))
        # print(str(buffer))

        res = buffer.to_ndarray()
        print(str(res))  # noqa: T001,T201

    res = ai_buffers_bind(ct.cast(buffers, ct.POINTER(AiBuffer)), len(buffers))
    print("  res({})".format(res))  # noqa: T001,T201

    for idx, buffer in enumerate(buffers):
        print("-- #{} ---------------".format(idx))  # noqa: T001,T201
        print("  Buffer shape:  ({}, {}, {}, {}) -> {}".format(buffer.n_batches, buffer.channels,  # noqa: T001,T201
                                                               buffer.width,
                                                               buffer.height, str(tuple(buffer.shape))))
        print("  Buffer fmt: {} data: {} meta: {}"   # noqa: T001,T201
              .format(buffer.format, buffer.data, buffer.meta_info))
        res = buffer.to_ndarray()
        print(str(res))  # noqa: T001,T201


if __name__ == "__main__":
    # test_buffers_bind()
    pass
