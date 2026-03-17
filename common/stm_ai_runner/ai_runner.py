###################################################################################
#   Copyright (c) 2021,2024 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
ST AI runner - Unified interface for ST.AI delpoyed models
"""

import sys
from abc import ABC, abstractmethod
import time as t
import logging
from typing import Tuple, List, Optional, Any, NamedTuple, Union, Dict
from enum import Enum, Flag
import tqdm

import numpy as np

from .utils import get_logger, TableWriter, truncate_name
from .stm_ai_utils import IOTensor
from .__version__ import __version__


LEGACY_INFO_DICT_VERSION = (1, 2)
STAI_INFO_DICT_VERSION = (2, 0)
_LOGGER_FILE_NAME_ = 'ai_runner.log'


class AiRunnerError(Exception):
    """Base exceptions for errors raised by AIRunner"""
    error = 800
    idx = 0

    def __init__(self, mess=None):
        self.mess = mess
        super(AiRunnerError, self).__init__(mess)

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
        _msg = 'E{}({}): {}'.format(self.code(),
                                    type(self).__name__,
                                    _mess)
        return _msg


class HwIOError(AiRunnerError):
    """Low-level IO error"""
    idx = 1


class NotInitializedMsgError(AiRunnerError):
    """Message is not fully initialized"""
    idx = 2


class InvalidMsgError(AiRunnerError, ValueError):
    """Message is not correctly formatted"""
    idx = 3


class InvalidParamError(AiRunnerError):
    """Invali parameter"""
    idx = 4


class InvalidModelError(AiRunnerError):
    """Invali Model"""
    idx = 5


class NotConnectedError(AiRunnerError):
    """STM AI run-time is not connected"""
    idx = 10


def generate_rnd(types, shapes, batch_size=4, rng=np.random.RandomState(42), val=None):
    """Generate list of random arrays"""  # noqa: DAR101,DAR201,DAR401
    no_list = False
    if not isinstance(types, list) and not isinstance(shapes, list):
        types, shapes = [types], [shapes]
        no_list = True
    batch_size = max(1, batch_size)
    inputs = []

    for type_, shape_ in zip(types, shapes):
        shape_ = (batch_size,) + shape_[1:]
        if val is not None and len(val) == 1:
            in_ = np.full(shape_, val[0])
        elif type_ == bool:
            in_ = rng.randint(2, size=shape_).astype(bool)
        elif type_ != np.float32:
            if val is not None:
                high = min(np.iinfo(type_).max, max(val))
                low = max(np.iinfo(type_).min, min(val) if min(val) < np.iinfo(type_).max else np.iinfo(type_).max)
            else:
                high = np.iinfo(type_).max
                low = np.iinfo(type_).min
            #  “discrete uniform” distribution
            in_ = rng.randint(low=low, high=high + 1, size=shape_)
        else:
            if val is not None:
                low, high = min(val), max(val)
            else:
                low, high = -1.0, 1.0
            # uniformly distributed over the half-open interval [low, high)
            in_ = rng.uniform(low=low, high=high, size=shape_)

        in_ = np.ascontiguousarray(in_.astype(type_))
        inputs.append(in_)
    return inputs[0] if no_list else inputs


class AiHwDriver(ABC):
    """Base class to handle the LL IO COM functions"""
    def __init__(self):
        self._parent = None
        self._hdl = None
        self._logger = None

    @property
    def is_connected(self):
        """Indicate if the driver is connected"""
        # noqa: DAR101,DAR201,DAR401
        return bool(self._hdl)

    def set_parent(self, parent):
        """"Set parent object"""  # noqa: DAR101,DAR201,DAR401
        self._parent = parent
        if hasattr(self._parent, 'get_logger'):
            self._logger = self._parent.get_logger()

    def get_config(self):
        """Return a dict with the specific config"""  # noqa: DAR101,DAR201,DAR401
        return dict()

    @abstractmethod
    def _connect(self, desc=None, **kwargs):
        pass

    @abstractmethod
    def _disconnect(self):
        pass

    @abstractmethod
    def _read(self, size, timeout=0):
        return 0

    @abstractmethod
    def _write(self, data, timeout=0):
        return 0

    def _write_memory(self, target_add, data, timeout=0):  # pylint: disable=unused-argument
        """Direct write memory"""  # noqa: DAR101,DAR201,DAR401
        return 0

    def connect(self, desc=None, **kwargs):
        """Connect the driver"""  # noqa: DAR101,DAR201,DAR401
        self.disconnect()
        return self._connect(desc=desc, **kwargs)

    def disconnect(self):
        """Disconnect the driver"""
        if self.is_connected:
            self._disconnect()

    def read(self, size, timeout=0):
        """Read the data"""  # noqa: DAR101,DAR201,DAR401
        if self.is_connected:
            return self._read(size, timeout)
        raise NotConnectedError()

    def write(self, data, timeout=0):
        """Write the data"""  # noqa: DAR101,DAR201,DAR401
        if self.is_connected:
            return self._write(data, timeout)
        raise NotConnectedError()

    def write_memory(self, target_add, data, timeout=0):
        """Direct write memory"""  # noqa: DAR101,DAR201,DAR401
        if self.is_connected:
            return self._write_memory(target_add, data, timeout)
        raise NotConnectedError()

    def short_desc(self, full: bool = True):
        """Return short human description"""  # noqa: DAR101,DAR201,DAR401 pylint: disable=unused-argument
        return 'UNDEFINED'


class AiRunnerDriver(ABC):
    """Base class interface for an AI Runner driver"""
    def __init__(self, parent):
        if not hasattr(parent, 'get_logger'):
            raise InvalidParamError('Invalid parent type, get_logger() attr is expected')
        self._parent = parent
        self._logger = parent.get_logger()

    def get_logger(self):
        """
        Return logger object

        Returns
        -------
        log
            logger object from the parent
        """
        return self._logger

    @abstractmethod
    def connect(self, desc=None, **kwargs):
        """Connect to the stm.ai run-time"""
        # noqa: DAR101,DAR201,DAR401
        return False

    @property
    def is_connected(self):
        """Indicate if the diver is connected"""
        # noqa: DAR101,DAR201,DAR401
        return False

    @abstractmethod
    def disconnect(self):
        """Disconnect to the stm.ai run-time"""
        # noqa: DAR101,DAR201,DAR401

    @abstractmethod
    def discover(self, flush=False):
        """Return list of available networks"""
        # noqa: DAR101,DAR201,DAR401
        return []

    @abstractmethod
    def get_info(self, c_name=None):
        """Get c-network details (including runtime)"""
        # noqa: DAR101,DAR201,DAR401
        return dict()

    @abstractmethod
    def invoke_sample(self, s_inputs, **kwargs):
        """Invoke the c-network with a given input (sample mode)"""
        # noqa: DAR101,DAR201,DAR401
        return [], dict()

    def extension(self, name=None, **kwargs):
        """Call specific command (driver dependent)"""  # noqa: DAR101,DAR201,DAR401
        # noqa: DAR101,DAR201,DAR401
        _ = name
        _ = kwargs
        return False


class AiTensorType(Enum):
    """AiTensor type"""
    UNDEFINED = 0
    INPUT = 1
    OUTPUT = 2
    INTERNAL = 3

    def __repr__(self):
        """."""  # noqa: DAR201
        return self.name

    def __str__(self):
        """."""  # noqa: DAR201
        return self.name


class AiTensorDesc(NamedTuple):
    """Class to describe the IO tensor"""
    iotype: AiTensorType = AiTensorType.UNDEFINED
    name: str = ''
    shape: Tuple = (0,)
    dtype: Any = 0
    scale: List[np.float32] = []
    zero_point: List[np.int32] = []

    def __str__(self):
        """."""  # noqa: DAR201
        desc_ = f'{self.iotype} \'{self.name}\' {np.dtype(self.dtype)}{self.shape}'
        if self.scale and self.scale[0] != 0:
            desc_ += f' {self.scale} {self.zero_point}'
        return desc_


class AiRunnerSession:
    """
    Interface to use a model
    """

    def __init__(self, name: str):
        """Constructor"""  # noqa: DAR101,DAR201,DAR401
        self._parent: Optional[AiRunner] = None
        self._name: str = name

    def __str__(self):
        """Return c-name of the associated c-model"""  # noqa: DAR101,DAR201,DAR401
        return self.name

    @property
    def is_active(self) -> bool:
        """Indicate if the session is active"""
        # noqa: DAR101,DAR201,DAR401
        return self._parent is not None

    @property
    def is_connected(self) -> bool:
        """Indicate if the underlying driver/stack is connected"""
        # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.is_connected
        return False

    @property
    def name(self) -> Optional[str]:
        """Return the name of the model"""
        # noqa: DAR101,DAR201,DAR401
        return self._name

    def acquire(self, parent):
        """Set the parent"""  # noqa: DAR101
        self._parent = parent

    def release(self):
        """Release the resources"""
        self._parent = None

    def get_input_infos(self):
        """Get model input details"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.get_input_infos(self.name)
        return list()

    def get_inputs(self):
        """Get description of the inputs"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.get_inputs(self.name)
        return list()

    def get_output_infos(self):
        """Get model outputs details"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.get_output_infos(self.name)
        return list()

    def get_outputs(self):
        """Get description of the outputs"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.get_outputs(self.name)
        return list()

    def get_info(self):
        """Get model details (including runtime)"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.get_info(self.name)
        return dict()

    def generate_rnd_inputs(self, batch_size=4, rng=np.random.RandomState(42), val=None):
        """Generate input data with random values"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.generate_rnd_inputs(self.name, batch_size, rng, val)
        return []

    def invoke(self, inputs, **kwargs):
        """Invoke the c-network"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            kwargs.pop('name', None)
            return self._parent.invoke(inputs, name=self.name, **kwargs)
        return list(), dict()

    def extension(self, **kwargs):
        """Execute specific command"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            kwargs.pop('name', None)
            return self._parent.extension(name=self.name, **kwargs)
        return False

    def summary(self, print_fn=None, indent=0, level=0):
        """Summary model & runtime infos"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            return self._parent.summary(name=self.name, print_fn=print_fn,
                                        indent=indent, level=level)
        return None

    def print_profiling(self, inputs, profiler, outputs, print_fn=None, **kwargs):
        """Prints a summary of the stat/profiling informations"""  # noqa: DAR101,DAR201,DAR401
        if self._parent:
            self._parent.print_profiling(inputs, profiler, outputs, print_fn=print_fn, **kwargs)

    def disconnect(self):
        """Disconnect the run-time"""  # noqa: DAR101,DAR201,DAR401
        parent = self._parent
        if parent:
            self.release()
            parent.disconnect(force_all=False)


class AiRunnerCallback:
    """
    Abstract base class used to build new callbacks
    """
    def __init__(self):
        pass

    def on_sample_begin(self, idx):
        """
        Called at the beginning of each sample

        Parameters
        ----------
        idx
            Integer, index of the sample
        """

    def on_sample_end(self, idx, data, logs=None):  # pylint: disable=unused-argument
        """
        Called at the end of each sample

        Parameters
        ----------
        idx
            Integer, index of the sample
        data
            List, output tensors (numpy ndarray objects)
        logs
            Dict

        Returns
        -------
        bool
            True to continue, False to stop the inference
        """
        return True

    def on_node_begin(self, idx, data, logs=None):
        """
        Called before each c-node

        Parameters
        ----------
        idx
            Integer, index of the c-node
        data
            List, input tensors (numpy ndarray objects)
        logs
            Dict
        """

    def on_node_end(self, idx, data, logs=None):
        """
        Called at the end of each c-node

        Parameters
        ----------
        idx
            Integer, index of the c-node
        data
            List, output tensors
        logs
            Dict
        """


def _io_details_to_desc(details: List, iotype: AiTensorType = AiTensorType.INPUT) -> List[AiTensorDesc]:
    """Convert IO detail info to AiTensorDesc object"""  # noqa: DAR101,DAR201,DAR401
    res_ = []
    for detail_ in details:
        if detail_.get('scale', None):
            scale: List[np.float32] = [np.float32(detail_['scale'])]
            zp: List[np.int32] = [detail_['zero_point']]
        else:
            scale, zp = [np.float32(0.0)], [np.int32(0)]
        item = AiTensorDesc(
            iotype=iotype,
            name=detail_['name'],
            shape=tuple(detail_['shape']),
            dtype=detail_['type'],
            scale=scale,
            zero_point=zp,
        )
        res_.append(item)
    return res_


class AiRunner:
    """AI Runner, interpreter interface for st.ai runtime.

    !!! example
        ```python
           from stm_ai_runner import AiRunner
           runner = AiRunner()
           runner.connect('serial')  # connection to a board (default)
           ...
           outputs, _ = runner.invoke(input_data)  # invoke the model
        ```
    """

    class Caps(Enum):
        """Capability values"""
        IO_ONLY = 0
        PER_LAYER = 1
        PER_LAYER_WITH_DATA = PER_LAYER | 2
        SELF_TEST = 4
        RELOC = 8
        MEMORY_RW = 16
        USBC = 32

    class Mode(Flag):
        """Mode values"""
        IO_ONLY = 0
        PER_LAYER = 1 << 0
        PER_LAYER_WITH_DATA = 1 << 1
        FIXED_INPUT = 1 << 2                # deprecated
        CONST_VALUE = 1 << 2
        PERF_ONLY = 1 << 3
        DEBUG = 1 << 8

    def __init__(self, logger=None, debug=False, verbosity=0):
        """
        Constructor

        Parameters
        ----------
        logger
            Logger object which must be used
        debug
            Logger is created with DEBUG level if True
        verbosity
            Logger is created with INFO level if > 0
        """
        self._sessions = []
        self._names = []
        self._drv = None
        if logger is None:
            lvl = logging.DEBUG if debug else logging.INFO if verbosity else logging.INFO  # WARNING
            logger = get_logger(self.__class__.__name__, lvl, filename=_LOGGER_FILE_NAME_)  # , with_prefix=True)
        self._logger = logger
        self._logger.debug('creating "%s" object (v%s)', str(self.__class__.__name__), __version__)
        self._debug = debug
        self._last_err = None

    @staticmethod
    def version():
        """Return the version of the AiRunner module"""
        # noqa: DAR101,DAR201,DAR401
        return __version__

    def get_logger(self):
        """Return the logger object"""  # noqa: DAR101,DAR201,DAR401
        return self._logger

    def __repr__(self):
        return self.short_desc()

    def __str__(self):
        return self.short_desc()

    def get_error(self):
        """Return human readable description of the last error"""  # noqa: DAR101,DAR201,DAR401
        err_ = self._last_err
        self._last_err = None
        return err_

    @property
    def is_connected(self) -> bool:
        """Indicate if the driver/stack is connected"""
        # noqa: DAR101,DAR201,DAR401
        return False if not self._drv else self._drv.is_connected

    def _check_name(self, name: Optional[str]) -> Optional[str]:
        """Return a valid c-network name"""  # noqa: DAR101,DAR201,DAR401
        if not self._names:
            return None
        if isinstance(name, int):
            idx = max(0, min(name, len(self._names) - 1))
            return self._names[idx]
        if name is None or not isinstance(name, str):
            return self._names[0]
        if name in self._names:
            return name
        return None

    def get_info(self, name: Optional[str] = None):
        """
        Get model details (including runtime infos)

        Parameters
        ----------
        name
            c-name of the model (if None, first c-model is used)

        Returns
        -------
        dict
            Dict with the model information
        """
        name_ = self._check_name(name)
        return self._drv.get_info(name_) if name_ else dict()

    @property
    def name(self) -> Optional[str]:
        """Return default network c-name"""
        # noqa: DAR101,DAR201,DAR401
        return self._check_name(None)

    def get_input_infos(self, name=None):
        """
        Get model input details

        Parameters
        ----------
        name
            c-name of the model (if None, first c-model is used)

        Returns
        -------
        list
            List of dict with the input details
        """
        info_ = self.get_info(name)
        return info_['inputs'] if info_ else list()

    def get_inputs(self, name: Optional[str] = None) -> List[AiTensorDesc]:
        """
        Get description of the inputs

        Parameters
        ----------
        name
            c-name of the model (if None, first c-model is used)

        Returns
        -------
        list
            List of AiTensorDesc object
        """
        info_ = self.get_info(name)
        inputs_details = info_['inputs'] if info_ else []
        return _io_details_to_desc(inputs_details, iotype=AiTensorType.INPUT)

    def get_output_infos(self, name=None):
        """
        Get model output details

        Parameters
        ----------
        name
            c-name of the model (if None, first c-model is used)

        Returns
        -------
        list
            List of dict with the output details
        """
        info_ = self.get_info(name)
        return info_['outputs'] if info_ else list()

    def get_outputs(self, name: Optional[str] = None) -> List[AiTensorDesc]:
        """
        Get description of the outputs

        Parameters
        ----------
        name
            c-name of the model (if None, first c-model is used)

        Returns
        -------
        list
            List of AiTensorDesc object
        """
        info_ = self.get_info(name)
        outputs_details = info_['outputs'] if info_ else []
        return _io_details_to_desc(outputs_details, iotype=AiTensorType.OUTPUT)

    def _align_requested_mode(self, mode):
        """Align requested mode with drv capabilities"""  # noqa: DAR101,DAR201,DAR401
        aligned_mode = AiRunner.Mode.IO_ONLY
        if mode & AiRunner.Mode.PER_LAYER:
            if AiRunner.Caps.PER_LAYER in self._drv.capabilities:
                aligned_mode |= AiRunner.Mode.PER_LAYER
        if mode & AiRunner.Mode.PER_LAYER_WITH_DATA and\
           AiRunner.Caps.PER_LAYER_WITH_DATA in self._drv.capabilities:
            aligned_mode |= AiRunner.Mode.PER_LAYER
            aligned_mode |= AiRunner.Mode.PER_LAYER_WITH_DATA
        if mode & AiRunner.Mode.FIXED_INPUT:
            aligned_mode |= AiRunner.Mode.FIXED_INPUT
        if mode & AiRunner.Mode.DEBUG:
            aligned_mode |= AiRunner.Mode.DEBUG
        if mode & AiRunner.Mode.PERF_ONLY:
            aligned_mode |= AiRunner.Mode.PERF_ONLY
        return aligned_mode

    def _check_inputs(self, inputs, in_desc, io_mode):
        """Check the coherence of the inputs (data type and shape)"""  # noqa: DAR101,DAR201,DAR401

        def _reduce_shape(org_shape):
            """Remove the dim with 1 value"""  # noqa: DAR101,DAR201,DAR401
            r_shape = (org_shape[0],)
            for dim in org_shape[1:]:
                if dim != 1:
                    r_shape = r_shape + (dim,)
            return r_shape

        if len(inputs) != len(in_desc):
            msg = f'invalid input number -> {len(inputs)}, expected {len(in_desc)}'
            raise InvalidParamError(msg)

        if 'quantize' in io_mode:
            inputs = [desc_['io_tensor'].quantize(data_) for data_, desc_ in zip(inputs, in_desc)]

        for idx, ref in enumerate(in_desc):
            in_shape = (ref['io_tensor'].shape[0],) + inputs[idx].shape[1:]
            if inputs[idx].dtype != ref['io_tensor'].dtype:
                msg = f"input #{idx + 1} - invalid dtype -> \'{inputs[idx].dtype}\', expected \'{ref['type']}\'"
                raise InvalidParamError(msg)
            if _reduce_shape(in_shape) != _reduce_shape(ref['io_tensor'].get_c_shape()):
                msg = f"input #{idx + 1} - invalid shape -> {in_shape}, expected {ref['io_tensor'].get_c_shape()}"
                raise InvalidParamError(msg)

        return inputs

    def _check_outputs(self, outputs, out_desc, io_mode):
        """Check the outputs"""  # noqa: DAR101,DAR201,DAR401

        if len(outputs) != len(out_desc):
            msg = f'invalid output number -> {len(outputs)}, expected {len(out_desc)}'
            raise InvalidParamError(msg)

        if 'dequantize' in io_mode:
            outputs = [desc_['io_tensor'].dequantize(data_) for data_, desc_ in zip(outputs, out_desc)]

        return outputs

    def invoke(self, inputs: Union[np.ndarray, List[np.ndarray]], **kwargs) -> Tuple[List[np.ndarray], Dict]:
        """
        Generate output predictions, invoke the c-network run-time (batch mode)

        Parameters
        ----------
        inputs
            Input samples. A Numpy array, or a list of arrays in case where the model
            has multiple inputs.
        kwargs
            specific parameters

        Returns
        -------
        list
            list of numpy arrays (one by outputs)

        """
        name_ = self._check_name(kwargs.pop('name', None))

        if name_ is None:
            return [], {}

        in_desc = self.get_input_infos(name_)
        out_desc = self.get_output_infos(name_)
        # device_type = self._drv.get_info(name_)['device']['dev_type']

        if not isinstance(inputs, list):
            inputs = [inputs]

        io_mode = kwargs.pop('io_mode', None)
        if io_mode is not None and isinstance(io_mode, str):
            io_mode = io_mode.split('+')
        else:
            io_mode = []

        inputs = self._check_inputs(inputs, in_desc, io_mode)

        callback = kwargs.pop('callback', None)
        mode = self._align_requested_mode(kwargs.pop('mode', AiRunner.Mode.IO_ONLY))
        disable_pb = kwargs.pop('disable_pb', False) or self._debug
        io_extra_bytes = kwargs.pop('io_extra_bytes', False)
        option = kwargs.pop('option', 0)

        m_outputs = kwargs.pop('m_outputs', None)

        batch_size = inputs[0].shape[0]
        profiler = {
            'info': {},
            'mode': mode,  # Used AiRunner.Mode
            'c_durations': [],  # Inference time by sample w/o cb
            'c_nodes': [],
            'debug': {
                'exec_times': [],  # "real" inference time by sample w cb
                'host_duration': 0.0,  # host execution time (on whole batch)
                'counters': {'type': 0, 'values': []},  # RT counters
                'stack_usage': None,  # stack used
                'heap_usage': None  # heap used
            },
        }

        start_time = t.perf_counter()
        outputs = []
        prog_bar = None
        cont = True
        for batch in range(batch_size):
            if not prog_bar and not disable_pb and (t.perf_counter() - start_time) > 1:
                prog_bar = tqdm.tqdm(total=batch_size, file=sys.stdout, desc='STAI.IO',
                                     unit_scale=False,
                                     leave=False)
                prog_bar.update(batch)
            elif prog_bar:
                prog_bar.update(1)
            s_inputs = [np.expand_dims(in_[batch], axis=0) for in_ in inputs]
            if m_outputs:
                ms_outputs = [np.expand_dims(out_[batch], axis=0) for out_ in m_outputs]
            else:
                ms_outputs = None
            if callback:
                callback.on_sample_begin(batch)
            s_outputs, s_dur = self._drv.invoke_sample(s_inputs, name=name_,
                                                       profiler=profiler, mode=mode,
                                                       io_extra_bytes=io_extra_bytes,
                                                       sample_idx=batch,
                                                       option=option,
                                                       callback=callback, ms_outputs=ms_outputs)
            if batch == 0:
                outputs = s_outputs
            else:
                for idx, out_ in enumerate(s_outputs):
                    outputs[idx] = np.append(outputs[idx], out_, axis=0)
            if callback:
                cont = callback.on_sample_end(batch, s_outputs, logs={'dur': s_dur})
            if not cont:
                break
        profiler['debug']['host_duration'] = (t.perf_counter() - start_time) * 1000.0
        profiler['info'] = self.get_info(name_)
        if prog_bar:
            prog_bar.close()

        outputs = self._check_outputs(outputs, out_desc, io_mode)

        return outputs, profiler

    def generate_rnd_inputs(self, name=None, batch_size=4, rng=np.random.RandomState(42), val=None):
        """Generate input data with random values"""  # noqa: DAR101,DAR201,DAR401
        if isinstance(name, AiRunnerSession):
            name = name.name
        name_ = self._check_name(name)
        if name_ is None:
            return []
        info_ = self.get_input_infos(name_)
        datas = generate_rnd([t_['io_tensor'].dtype for t_ in info_],
                             [s_['io_tensor'].get_c_shape() for s_ in info_],
                             batch_size,
                             rng=rng,
                             val=val)
        return datas

    @property
    def names(self):
        """Return available models as a list of name"""
        # noqa: DAR101,DAR201,DAR401
        return self._names

    def _release_all(self):
        """Release all resources"""  # noqa: DAR101,DAR201,DAR401
        if self._names:
            self._logger.debug("_release_all(%s)", str(self))
        for ses_ in self._sessions:
            ses_.release()
            self._sessions.remove(ses_)
        self._names = []
        if self.is_connected:
            self._drv.disconnect()
            self._drv = None
        return True

    def short_desc(self):
        """Return short description of the associated run-time"""  # noqa: DAR101,DAR201,DAR401
        if self.is_connected:
            desc_ = '{} {}'.format(self._drv.short_desc(), self.names)
            return desc_
        return 'not connected'

    def connect(self, desc=None, **kwargs):
        """Connect to a given runtime defined by desc"""  # noqa: DAR101,DAR201,DAR401
        from .ai_resolver import ai_runner_resolver

        self._logger.debug("resolving('desc' parameter: '%s')..", str(desc))
        self._release_all()

        self._drv, desc_ = ai_runner_resolver(self, desc)

        if self._drv is None:
            self._last_err = desc_
            self._logger.debug(desc_)
            return False

        self._logger.debug("'desc' parameter for '%s' driver: '%s'", str(self._drv.__class__.__name__), str(desc_))
        self._logger.debug('connecting..')

        try:
            self._drv.connect(desc_, **kwargs)
        except Exception as e:   # pylint: disable=broad-except
            self._last_err = str(e)
            return False

        if not self._drv.is_connected:
            self._logger.debug('connection failed')
            self._release_all()
        else:
            self._logger.debug('connection successful')
            self._names = self._drv.discover(flush=True)
            for name_ in self._names:
                self._sessions.append(AiRunnerSession(name_))
        return self.is_connected

    def session(self, name: Optional[str] = None) -> Optional[AiRunnerSession]:
        """Return session handler for the given model name/idx"""  # noqa: DAR101,DAR201,DAR401
        if not self.is_connected:
            return None
        name = self._check_name(name)
        if name:
            for ses_ in self._sessions:
                if name == ses_.name:
                    ses_.acquire(self)
                    return ses_
        return None

    def disconnect(self, force_all: bool = True) -> bool:
        """Close the connection with the run-time"""  # noqa: DAR101,DAR201,DAR401
        if not force_all:
            # check is a session is on-going
            for ses_ in self._sessions:
                if ses_.is_active:
                    return True
        return self._release_all()

    def extension(self, name=None, **kwargs):
        """Execute specific command for a given model"""  # noqa: DAR101,DAR201,DAR401
        name_ = self._check_name(name)
        return self._drv.extension(name_, **kwargs) if name_ else False

    def summary(self, name=None, print_fn=None, indent=1, level=0):
        """Prints a summary of the model & associated runtime"""  # noqa: DAR101,DAR201,DAR401

        def _version_to_str(version):
            """."""   # noqa: DAR101,DAR201,DAR401
            return '.'.join([str(v) for v in version])

        print_drv = print if print_fn is None else print_fn  # noqa: T002,T202

        dict_info = self.get_info(name)
        if not dict_info:
            return

        table_w = TableWriter(indent=indent, csep='-')

        title = f"Summary '{dict_info['name']}' - {self._names}"
        table_w.set_title(title)

        # C-Model/RT description - report the model & RT info

        for idx, in_ in enumerate(dict_info['inputs']):
            name_ = truncate_name(in_['name'], 20)
            attr_ = f"I[{idx+1}/{len(dict_info['inputs'])}] \'{name_}\'"
            if 'io_tensor' in in_:
                table_w.add_row([attr_, ':', in_['io_tensor'].to_str('all+no-name', short=False)])
            else:
                input_description = str(in_['shape']) + ', ' + in_['format'].name + ', '\
                    + str(in_['size_bytes']) + ' bytes'
                table_w.add_row([attr_, ':', input_description])

        for idx, out_ in enumerate(dict_info['outputs']):
            name_ = truncate_name(out_['name'], 20)
            attr_ = f"O[{idx+1}/{len(dict_info['outputs'])}] \'{name_}\'"
            if 'io_tensor' in out_:
                table_w.add_row([attr_, ':', out_['io_tensor'].to_str('all+no-name', short=False)])
            else:
                output_description = str(out_['shape']) + ', ' + out_['format'].name + ', '\
                    + str(out_['size_bytes']) + ' bytes'
                table_w.add_row([attr_, ':', output_description])

        if 'flags' in dict_info and level > 0:
            table_w.add_row(['flags', ':', dict_info['flags']])

        table_w.add_row(['n_nodes', ':', dict_info['n_nodes']])

        if dict_info.get('activations', None) is not None:
            _ext = ''
            if 'mempools' in dict_info:
                acts = [s['shape'][-1] for s in dict_info['mempools']['activations']]
                if len(acts) > 1:
                    _ext = f'{acts} ({len(acts)} segments)'
            attr = f'{dict_info["activations"]} {_ext}'
            table_w.add_row(['activations', ':', attr])

        if dict_info.get('weights', None) is not None:
            _ext = ''
            if 'mempools' in dict_info:
                weights = [s['shape'][-1] for s in dict_info['mempools']['params']]
                if len(weights) > 1:
                    _ext = f'({len(weights)} segments)'
            attr = f'{dict_info["weights"]} {_ext}'
            table_w.add_row(['weights', ':', attr])

        if dict_info.get('macc', None) is not None:
            macc_ = dict_info['macc']
            table_w.add_row(['macc', ':', macc_])

        if dict_info.get('hash', ''):
            hash_ = dict_info['hash']
            table_w.add_row(['hash', ':', hash_])

        app_compiler_ = dict_info.get('compile_datetime', '<undefined>')
        table_w.add_row(['compile_datetime', ':', app_compiler_])

        table_w.add_separator()

        # Tools/Runtime section

        # protocol - Describe the ai_runner stack desc. to set the connection with the RT
        proto_ = dict_info['runtime'].get('protocol', '<undefined>')
        table_w.add_row(['protocol', ':', f"{proto_}"])

        # tools - Runtime name and version
        _rt_desc = f"{dict_info['runtime']['name']}"
        _rt_desc += f" v{_version_to_str(dict_info['runtime']['tools_version'])}"
        table_w.add_row(['tools', ':', _rt_desc])

        # runtime lib description
        rt_lib_desc_ = dict_info['runtime'].get('rt_lib_desc', '')
        if not rt_lib_desc_:
            rt_lib_desc_ = f"v{_version_to_str(dict_info['runtime']['version'])}"
        table_w.add_row(['runtime lib', ':', rt_lib_desc_])

        # aiValidation capabilities
        caps_ = [str(n).replace('Caps.', '') for n in dict_info['runtime']['capabilities']]
        table_w.add_row(['capabilities', ':', ', '.join(caps_)])

        # device description
        dev_desc_ = dict_info['device']['desc']
        table_w.add_row(['device.desc', ':', dev_desc_])
        dev_attrs_ = ','.join(dict_info['device'].get('attrs', []))
        if dev_attrs_:
            table_w.add_row(['device.attrs', ':', dev_attrs_])

        res = table_w.getvalue(endline=True)
        for line in res.splitlines():
            print_drv(line)
        table_w.close()

    def print_profiling(self, inputs, profiler, outputs, print_fn=None, **kwargs):
        """Prints a summary of the stat/profiling informations"""  # noqa: DAR101,DAR201,DAR401

        indent = kwargs.pop('indent', 1)
        tensor_info = kwargs.pop('tensor_info', False)
        debug = kwargs.pop('debug', False)
        no_details = kwargs.pop('no_details', False)

        print_drv = print if print_fn is None else print_fn  # noqa: T002,T202

        def build_row_stat_table(arr: np.ndarray, tens: IOTensor, n_samples: int = 1):
            row = [tens.tag, n_samples]

            shape_type_desc = tens.to_str('all+no-name+no-scheme+no-loc')

            if tens.is_packed:
                arr = tens.unpack(np.copy(arr))

            if arr.size == 0:
                min_ = max_ = '0'
            elif np.issubdtype(arr.dtype, np.floating):
                min_ = f'{arr.min():.03f}'
                max_ = f'{arr.max():.03f}'
            else:
                min_ = f'{arr.min()}'
                max_ = f'{arr.max()}'

            row.append(shape_type_desc)
            if arr.size == 0:
                row.extend(['n.a.', 'n.a.', 'n.a.', 'n.a.'])
            else:
                row.extend([min_, max_, f'{arr.mean():6.03f}', f'{arr.std():6.03f}'])
            row.append(' ' + tens.name)
            return row

        def build_perf_counters(counters):
            if not counters['values']:
                return ''
            values = np.array(counters['values']).astype(np.uint64)
            return [int(val) for val in np.mean(values, axis=0)]

        # performance counters
        perf_counters_per_layer = []
        perf_counters_cumul = ''
        perf_counters_name = 'counter'
        perf_counters_max = 0
        cpu_epoch_sw = 0
        if profiler['c_nodes']:
            if 'counters' in profiler['c_nodes'][0]:
                perf_counters_name = profiler['c_nodes'][0]['counters'].get('type', 'counter')
                for c_node in profiler['c_nodes']:
                    counters_ = build_perf_counters(c_node['counters'])
                    perf_counters_per_layer.append(counters_)
                    if 'epoch' in c_node['layer_desc'] and len(counters_) > 0:
                        if '(SW)' in c_node['layer_desc']:
                            cpu_epoch_sw += counters_[0] + counters_[2]
                        elif '(HYBRID)' in c_node['layer_desc']:
                            cpu_epoch_sw += counters_[0] + counters_[2]
                        elif '(extra ' in c_node['layer_desc']:
                            if counters_[2] > (2 * counters_[1]):
                                cpu_epoch_sw += counters_[0] + counters_[2]
                    if not perf_counters_cumul:
                        perf_counters_cumul = [0] * len(counters_)
                    for idx, val in enumerate(perf_counters_per_layer[-1]):
                        perf_counters_cumul[idx] += val
                        perf_counters_max = max(perf_counters_cumul)
        if not perf_counters_cumul and profiler['debug']['counters']:
            perf_counters_name = profiler['debug']['counters'].get('type', 'counter')
            counters_ = build_perf_counters(profiler['debug']['counters'])
            perf_counters_cumul = counters_
            perf_counters_max = max(counters_) if counters_ else 0

        version_ = f"{profiler['info']['version'][0]}.{profiler['info']['version'][1]}"
        name_net_ = profiler["info"]["name"]
        title = f'ST.AI Profiling results v{version_} - \"{name_net_}\"'

        table_w = TableWriter(indent=indent, csep='-')
        table_w.set_title(title)

        n_samples = len(profiler['c_durations'])
        c_dur_ = np.array(profiler['c_durations'])

        table_w.add_row(['nb sample(s)', ':', str(n_samples)])
        table_w.add_row(['duration', ':',
                         f'{c_dur_.mean():.03f} ms by sample ({c_dur_.min():.03f}/'
                         + f'{c_dur_.max():.03f}/{c_dur_.std():.03f})'])
        if profiler['info'].get('macc', None) is not None:
            table_w.add_row(['macc', ':', profiler['info']['macc']])
            dev_type_ = profiler['info']['device']['dev_type'].upper()
            if dev_type_ not in ('SIMULATOR', 'HOST') and profiler['info']['macc'] > 0:
                n_cycles = (c_dur_.mean() * profiler['info']['device']['sys_clock']) / 1000
                n_cycles_per_macc = n_cycles / profiler['info']['macc']
                table_w.add_row(['cycles/MACC', ':', f'{n_cycles_per_macc:.2f}'])

        if perf_counters_cumul:
            rep_values_ = ' '.join([f'{val:,}' for val in perf_counters_cumul])
            table_w.add_row([f'{perf_counters_name}', ':', f'[{rep_values_}]'])

        if 'n_init_time' in profiler['info']:
            if profiler['info']['n_init_time'] != 0:
                table_w.add_row(['network initialize time (ms)', ':', f"{profiler['info']['n_init_time']:.03f}"])

        if 'n_install_time' in profiler['info']:
            if profiler['info']['n_install_time'] != 0:
                table_w.add_row(['network installation time (ms)', ':', f"{profiler['info']['n_install_time']:.03f}"])

        if profiler['debug']['stack_usage'] is not None:
            stack_ = profiler['debug']['stack_usage']
            heap_ = profiler['debug']['heap_usage']
            if not (stack_ < 0 and heap_ < 0):
                stack_ = 'not monitored' if stack_ < 0 else stack_
                table_w.add_row(['used stack/heap', ':', f'{stack_}/{heap_} bytes'])

        table_w.add_separator()
        if debug:
            table_w.add_row(['DEVICE duration', ':',
                             '{:.03f} ms by sample (including callbacks)'.format(
                                 np.array(profiler['debug']['exec_times']).mean())])
            table_w.add_row(['HOST duration', ':', '{:.3f} s (total)'.format(
                profiler['debug']['host_duration'] / 1000)])
            table_w.add_row(['used mode', ':', profiler['mode']])
            nb_c_nodes = len(profiler['c_nodes']) if profiler['c_nodes'] else 'n.a.'
            table_w.add_row(['number of c-node', ':', nb_c_nodes])
            table_w.add_separator()

        res = table_w.getvalue()
        for line in res.splitlines():
            print_drv(line)
        table_w.close()

        if profiler['c_nodes'] and not no_details:
            dur_fmt = '{:.3f}'
            len_ = len(f'{perf_counters_max:,} ')
            counter_fmt = '{:' + str(len_) + ',}'
            counter_perc_fmt = '{:' + str(len_ - 1) + '.1f}%'
            total_ = 0
            table_w = TableWriter(indent=indent + 1, csep='-')
            table_w.set_title('Inference time per node')

            header = ['c_id', 'm_id', 'type', 'dur (ms)', '%', 'cumul ', '', 'name']
            if perf_counters_cumul:
                header[6] = perf_counters_name
            table_w.set_header(header)

            dur_all = np.array(profiler['c_durations']).mean()
            dur_cumul = 0
            perc_cumul = 0
            for c_id, c_node in enumerate(profiler['c_nodes']):
                durs = np.array(c_node['c_durations'])
                ext_ = ''
                if perf_counters_cumul:
                    counters_ = perf_counters_per_layer[c_id]
                    ext_ = '[{} ]'.format(' '.join([counter_fmt.format(val) for val in counters_]))
                dur_ = dur_fmt.format(durs.mean())
                perc_ = durs.mean() * 100 / dur_all
                perc_ = f'{perc_:.1f}%'
                perc_cumul += (durs.mean() * 100 / dur_all)
                dur_cumul += durs.mean()
                row = [c_id, c_node['m_id'], c_node['layer_desc'], dur_, perc_,
                       f'{perc_cumul:.1f}% ', ext_, c_node['name']]
                table_w.add_row(row)
            perf_counters_cumul_res = ''
            if perf_counters_cumul:
                perf_counters_cumul_res = '[{} ]'.format(' '.join([counter_fmt.format(val)
                                                                  for val in perf_counters_cumul]))

            if dur_cumul < dur_all:
                table_w.add_separator()

                no_layer_dur = dur_all - dur_cumul
                dur_ = dur_fmt.format(no_layer_dur)
                perc_ = no_layer_dur * 100 / dur_all
                perc_ = f'{perc_:.1f}%'
                perc_cumul += (no_layer_dur * 100 / dur_all)
                dur_cumul += no_layer_dur

                row = ['n/a', 'n/a', 'Inter-nodal', dur_, perc_, f'{perc_cumul:.1f}% ', '', 'n/a']
                table_w.add_row(row)

            table_w.add_separator()
            table_w.add_row(['total', '', '', dur_fmt.format(dur_cumul), '', '', perf_counters_cumul_res, ''])

            if perf_counters_cumul and len(perf_counters_cumul) > 1:
                inf_per_sec = 1000 / dur_cumul
                total_ = sum(perf_counters_cumul)
                perf_counters_cumul_res = '[{} ]'.format(' '.join([counter_perc_fmt.format((val * 100) / total_)
                                                                  for val in perf_counters_cumul]))
                table_w.add_row(['', '', '', f'{inf_per_sec:.2f} inf/s', '', '', perf_counters_cumul_res, ''])

            res = table_w.getvalue(fmt='...>>>..', endline=True)
            for line in res.splitlines():
                print_drv(line)
            table_w.close()

            # HW/SW activity
            if total_ > 0 and len(perf_counters_cumul) > 1:
                # Calculate total cpu activity ONLY FOR epoch HW (cpu prog + cpu clean)
                cpu_epoch_hw = total_ - perf_counters_cumul[1] - cpu_epoch_sw
                npu_perc_ = perf_counters_cumul[1] * 100 / total_
                sw_perc_ = cpu_epoch_sw * 100 / total_
                cpu_swctrl_percent = f'{cpu_epoch_hw * 100 / total_:.1f}%'
                indent_ = ' ' * indent
                print_drv(f'{indent_} HW: {npu_perc_:.1f}%, SW: {sw_perc_:.1f}%, SW ctrl: {cpu_swctrl_percent}')

        if not profiler['mode'] & AiRunner.Mode.PERF_ONLY and profiler['info']['inputs']:
            ext_indent = 1 if not no_details else 0
            table_w = TableWriter(indent=indent + ext_indent, csep='-')
            table_w.set_title('Statistic per tensor')
            table_w.set_header(['tensor', '#', 'type[shape]:size', 'min', 'max', 'mean', 'std', ' name'])
            c_nodes = profiler.get('c_nodes', [])

            for idx, c_in in enumerate(inputs):
                io_tensor = profiler['info']['inputs'][idx]['io_tensor']
                table_w.add_row(build_row_stat_table(c_in, io_tensor, n_samples))

            for c_id, c_node in enumerate(c_nodes):
                for idx, (data, io_tensor) in enumerate(zip(c_node['data'], c_node['io_tensors'])):
                    if data.size and not no_details:
                        table_w.add_row(build_row_stat_table(data, io_tensor, n_samples))

            for idx, c_out in enumerate(outputs):
                io_tensor = profiler['info']['outputs'][idx]['io_tensor']
                table_w.add_row(build_row_stat_table(c_out, io_tensor, n_samples))

            res = table_w.getvalue(fmt='...>>>>.', endline=True)
            for line in res.splitlines():
                print_drv(line)
            table_w.close()

        else:
            print_drv('')

        if tensor_info:  # display detailed info of each tensor

            def build_row_table(tens: IOTensor, with_data: str) -> List:
                desc_ = tens.to_str('all+no-name+no-loc', short=False)
                row = [tens.tag, desc_]
                row.append(tens.name)
                row.append(with_data)
                return row

            table_w = TableWriter(indent=indent + 1, csep='-')
            table_w.set_title('Info per tensor')
            table_w.set_header(['tensor', 'description', 'name', 'data'])

            perf_only = profiler['mode'] & AiRunner.Mode.PERF_ONLY

            for tens, c_in in zip(profiler['info']['inputs'], inputs):
                _addr = ' ' + str(hex(tens['io_tensor'].c_addr)) if tens['io_tensor'].c_addr else ''
                _addr = (f'{c_in.size != 0}' if not perf_only else 'False') + _addr
                table_w.add_row(build_row_table(tens['io_tensor'], _addr))

            if profiler['c_nodes']:
                for c_id, c_node in enumerate(profiler['c_nodes']):
                    for idx, (data, io_tensor) in enumerate(zip(c_node['data'], c_node['io_tensors'])):
                        _addr = ' ' + str(hex(io_tensor.c_addr)) if io_tensor.c_addr else ''
                        _addr = '{}'.format(data.size != 0) + _addr
                        table_w.add_row(build_row_table(io_tensor, _addr))

            for tens, c_out in zip(profiler['info']['outputs'], outputs):
                _addr = ' ' + str(hex(tens['io_tensor'].c_addr)) if tens['io_tensor'].c_addr else ''
                _addr = f'{c_out.size != 0}' + _addr
                table_w.add_row(build_row_table(tens['io_tensor'], _addr))

            res = table_w.getvalue(fmt='...>', endline=True)
            for line in res.splitlines():
                print_drv(line)
            table_w.close()


if __name__ == '__main__':
    pass
