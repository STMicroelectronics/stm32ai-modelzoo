###################################################################################
#   Copyright (c) 2021, 2024 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
ST AI runner - Driver for proto buff messages
"""

import logging
import os
import time as t
from typing import List, Tuple, Dict

import numpy as np

from google.protobuf.internal.encoder import _VarintBytes  # type: ignore

from .ai_runner import AiRunner, AiRunnerDriver, AiHwDriver, STAI_INFO_DICT_VERSION
from .ai_runner import HwIOError, InvalidMsgError, NotInitializedMsgError, AiRunnerError
from .ai_runner import InvalidParamError, InvalidModelError
from .stm32_utility import stm32_id_to_str, stm32_attr_config, bsdchecksum, dump_ihex_file
from . import stm32msg_pb2 as stm32msg
from .stm_ai_utils import stm_ai_node_type_to_str, AiBufferFormat, IOTensor
from .stm_ai_utils import RT_ST_AI_NAME, st_neural_art_node_type_to_str
from .tflm_utils import tflm_node_type_to_str
from .utils import set_log_level, get_log_level


__version__ = '2.1'


def _to_version(ver):
    """Convert uint32 version to tuple (major, minor, sub)"""  # noqa: DAR101,DAR201,DAR401
    return (ver >> 24 & 0xFF, ver >> 16 & 0xFF, ver >> 8 & 0xFF)


_SUPPORTED_AI_ARM_TOOLS = {
    stm32msg.AI_GCC: 'GCC',
    stm32msg.AI_IAR: 'IAR',
    stm32msg.AI_MDK_5: 'AC5',
    stm32msg.AI_MDK_6: 'AC6',
    stm32msg.AI_HTC: 'HTC',
    stm32msg.AI_GHS: 'GHS',
}


def _tools_desc(tools_id: int) -> str:
    """Return short description of the associated tools"""  # noqa: DAR101,DAR201,DAR401
    return _SUPPORTED_AI_ARM_TOOLS.get(tools_id, '<undef>')


class AiRunTimeDecoder():
    """Default decoder for generic AI RT"""
    def __init__(self, rt_id: int = 0, name: str = 'undefined'):
        self._rt_id: int = rt_id
        self._name: str = name
        self._config = {}

    def set_rt_id(self, rt_id: int):
        """set the full runtime id"""  # noqa: DAR101,DAR201,DAR401
        self._rt_id = rt_id

    @property
    def compiler_id(self):
        """Return compiler ID"""
        # noqa: DAR101,DAR201,DAR401
        return self._rt_id >> stm32msg.AI_TOOLS_POS & 0xFF

    @property
    def extra(self):
        """Return extra info"""
        # noqa: DAR101,DAR201,DAR401
        return self._rt_id >> 24 & 0xFF

    def _def_api_name(self):
        """Return default (id=0) API name"""  # noqa: DAR101,DAR201,DAR401
        return ''

    @property
    def api_id(self):
        """Return api ID"""
        # noqa: DAR101,DAR201,DAR401
        return self._rt_id >> stm32msg.AI_RT_API_POS & 0xFF

    @property
    def api_desc(self):
        """Return api desc"""
        # noqa: DAR101,DAR201,DAR401
        msg_ = self._def_api_name()
        if self.api_id & stm32msg.AI_RT_API_ST_AI:
            msg_ = 'st-ai'
        if self.api_id & stm32msg.AI_RT_API_RELOC:
            msg_ += '+reloc'
        if self.api_id & stm32msg.AI_RT_API_LITE:
            msg_ = '+lite'
        return msg_

    @property
    def name(self):
        """return name fo the RT decoder"""
        # noqa: DAR101,DAR201,DAR401
        return f'{self._name} ({self.api_desc} api)'

    def has_params(self):
        """Indicates if the size of the params is provided"""  # noqa: DAR101,DAR201,DAR401
        return self.extra & 2 == 0

    def has_activations(self):
        """Indicates if the size of the activations is provided"""  # noqa: DAR101,DAR201,DAR401
        return self.extra & 1 == 0

    def has_macc(self):
        """Indicates if the macc is provided"""  # noqa: DAR101,DAR201,DAR401
        return self.extra & 4 == 0

    def op_desc(self, _):
        """return desc of the operator"""  # noqa: DAR101,DAR201,DAR401
        return "undefined"

    def op_type(self, op_type):
        """return type of the operator"""  # noqa: DAR101,DAR201,DAR401
        return op_type & 0x7FFF

    def m_id(self, _):
        """return index of the operator"""  # noqa: DAR101,DAR201,DAR401
        return -1

    def get_tag(self, idx_node, idx_tens, _):
        """return associated tag of the operator"""  # noqa: DAR101,DAR201,DAR401
        return f'N.{idx_node}.{idx_tens}'

    def default_name_tensor(self, node_idx, tens_idx):
        """return default name of the tensor"""  # noqa: DAR101,DAR201,DAR401
        return f'ai_tens_n_{node_idx}_{tens_idx}'

    def default_name_node(self, node_idx, _):
        """return name of the operator"""  # noqa: DAR101,DAR201,DAR401
        return f'ai_node_{node_idx}'

    def counter_decode(self, counter_type, counters):
        """return perf counters"""  # noqa: DAR101,DAR201,DAR401
        cts = []
        type_ = counter_type >> stm32msg.COUNTER_FMT_POS & stm32msg.COUNTER_FMT_MASK
        if type_ == stm32msg.COUNTER_FMT_64B:
            for idx in range(len(counters) // 2):
                c_v = counters[idx * 2] | counters[idx * 2 + 1] << 32
                cts.append(c_v)
        elif type_ == stm32msg.COUNTER_FMT_32B:
            for c_v in counters:
                cts.append(c_v)
        return cts

    def _counter_desc(self, _):
        """return default short description of the counter"""  # noqa: DAR101,DAR201,DAR401
        return "counter"

    def counter_desc(self, counter_type):
        """return short description of the counter"""  # noqa: DAR101,DAR201,DAR401
        type_ = counter_type & stm32msg.COUNTER_TYPE_MASK
        if type_ == stm32msg.COUNTER_TYPE_CPU:
            return "CPU cycles"
        return self._counter_desc(counter_type)

    def _extract_runtime_desc(self, rt_desc: str, rt_ver: Tuple[int]):
        """Return tuple with extracted desc_, build and version"""  # noqa: DAR101,DAR201,DAR401
        rt_ver_ = '.'.join([str(v_) for v_ in _to_version(rt_ver)])
        desc_ = rt_desc.split()
        rt_build_ = ''
        rt_desc_ = rt_desc
        if desc_ and desc_[-1]:
            try:
                rt_build_ = '-' + hex(int(desc_[-1], 16)).lower()
                rt_build_ = rt_build_.replace('0x', '')
                rt_desc_ = ' '.join(desc_[:-1])
            except ValueError:
                rt_build_ = ''
        return rt_desc_, rt_build_, rt_ver_

    def runtime_desc(self, rt_desc: str, rt_ver: Tuple[int]):
        """Return description of runtime lib"""  # noqa: DAR101,DAR201,DAR401
        compiler_ = _tools_desc(self.compiler_id)
        desc_, build_, ver_ = self._extract_runtime_desc(rt_desc, rt_ver)
        return f'v{ver_}{build_} compiled with {desc_} ({compiler_})'

    def build_option_parameter(self, user_options: int = 0, sample_idx: int = -1):
        """Build the 'option' parameter (run command, default)"""
        param_option = 1 if (sample_idx >= 0 and sample_idx == 0) else 0
        param_option |= (user_options << 8)
        return param_option

    def __str__(self) -> str:
        """."""
        desc_ = f'RT_DECODER: {self.name}, id=0x{self._rt_id:x}, compiler={_tools_desc(self.compiler_id)}'
        desc_ += f', act={self.has_activations()}, params={self.has_params()}, macc={self.has_macc()}'
        return desc_


class AiRtStmAiDecoder(AiRunTimeDecoder):
    """Decoder for generic/legacy STM.AI RT"""

    def _def_api_name(self):
        """Return default (id=0) API name"""  # noqa: DAR101,DAR201,DAR401
        return 'legacy'

    def op_desc(self, layer_type):
        return stm_ai_node_type_to_str(layer_type & 0x7FFF)

    def m_id(self, m_id):
        return m_id


class AiRtTFLMDecoder(AiRunTimeDecoder):
    """Decoder for generic TFLM RT"""

    def _def_api_name(self):
        """Return default (id=0) API name"""  # noqa: DAR101,DAR201,DAR401
        return 'tflm'

    def op_desc(self, layer_type):
        return tflm_node_type_to_str(layer_type & 0x7FFF)

    def default_name_tensor(self, node_idx, tens_idx):
        return f'tflm_tens_n_{node_idx}_{tens_idx}'

    def runtime_desc(self, rt_desc: str, rt_ver: Tuple[int]):
        """Return description of runtime lib"""  # noqa: DAR101,DAR201,DAR401
        compiler_ = _tools_desc(self.compiler_id)
        desc_, build_, ver_ = self._extract_runtime_desc(rt_desc, rt_ver)
        return f'v{ver_}{build_} from {desc_} ({compiler_})'


class AiRtSTNeuralARTDecoder(AiRunTimeDecoder):
    """Decoder for generic STNeuralART RT"""

    def _def_api_name(self):
        return 'LL_ATON'

    def op_desc(self, layer_type):
        return st_neural_art_node_type_to_str(layer_type & 0x7FFF)

    def default_name_tensor(self, node_idx, tens_idx):
        return f'aton_tens_n_{node_idx}_{tens_idx}'

    def default_name_node(self, _, m_id):
        num_ = m_id & 0xFFFF
        num_last_ = m_id >> 16
        if num_last_ & 0x8000:
            return f'EpochBlock_{num_} ({0xFFFF - num_last_ + 1})'
        if num_ != num_last_:
            return f'EpochBlock_{num_} -> {num_last_}'
        return f'EpochBlock_{num_}'

    def m_id(self, _):
        return '-'  # '{}.{}'.format(m_id & 0xFFFF, m_id >> 16)

    def get_tag(self, _, idx_tens, m_id):
        return f'E.{m_id & 0xFFFF}.{idx_tens}'

    def _counter_desc(self, counter_type):
        """return default short description of the counter"""  # noqa: DAR101,DAR201,DAR401
        return f'NPU counters {counter_type}'

    def runtime_desc(self, rt_desc: str, rt_ver: Tuple[int]):
        """Return description of runtime lib"""  # noqa: DAR101,DAR201,DAR401
        compiler_ = _tools_desc(self.compiler_id)
        desc_, build_, ver_ = self._extract_runtime_desc(rt_desc, rt_ver)
        return f'{desc_} (optimized SW lib v{ver_}{build_} {compiler_})'


_SUPPORTED_AI_RT = {
    stm32msg.AI_RT_STM_AI: AiRtStmAiDecoder(stm32msg.AI_RT_STM_AI, RT_ST_AI_NAME),
    stm32msg.AI_RT_TFLM: AiRtTFLMDecoder(stm32msg.AI_RT_TFLM, 'TFLM'),
    stm32msg.AI_RT_TVM: AiRunTimeDecoder(stm32msg.AI_RT_TVM, 'TVM'),
    stm32msg.AI_RT_ATONN: AiRtSTNeuralARTDecoder(stm32msg.AI_RT_ATONN, 'ST Neural ART'),
    stm32msg.AI_RT_GLOW: AiRunTimeDecoder(stm32msg.AI_RT_GLOW, 'GLOW'),
    stm32msg.AI_RT_STM_AI_RELOC: AiRtStmAiDecoder(stm32msg.AI_RT_STM_AI_RELOC, RT_ST_AI_NAME + '/RELOC')
}


def op_type_to_str(op_type, rt_decoder=None):
    """Decode operator type field from aiOperatorMsg"""  # noqa: DAR101,DAR201,DAR401
    flags = op_type >> stm32msg.OPERATOR_FLAG_POS
    res = []
    if flags == stm32msg.OPERATOR_FLAG_NONE:
        res.append('NONE')
    if flags & stm32msg.OPERATOR_FLAG_INTERNAL == stm32msg.OPERATOR_FLAG_INTERNAL:
        res.append('INTERNAL')
    if flags & stm32msg.OPERATOR_FLAG_LAST:
        res.append('LAST')
    if flags & stm32msg.OPERATOR_FLAG_WITHOUT_TENSOR == stm32msg.OPERATOR_FLAG_WITHOUT_TENSOR:
        res.append('WITHOUT_TENSOR')
    res = '|'.join(res)
    res = f'{hex(op_type)}/' + res
    if isinstance(rt_decoder, AiRunTimeDecoder):
        res = res + f',"{rt_decoder.op_desc(op_type)}"'
    return res


def op_msg_to_str(op_msg, rt_decoder):
    """."""  # noqa: DAR101,DAR201,DAR401
    msg_fmt_ = ' name="{}" counters=\"{}\"{} dur={:.3f}ms id={}.{} type={}'
    counter_type_ = rt_decoder.counter_desc(op_msg.counter_type)
    counters_ = rt_decoder.counter_decode(op_msg.counter_type, op_msg.counters)
    sub_id = op_msg.id >> 16
    sub_id = -(0xFFFF - sub_id + 1) if sub_id & 0x8000 else sub_id
    return msg_fmt_.format(op_msg.name, counter_type_, counters_,
                           op_msg.duration, op_msg.id & 0xFFFF, sub_id,  # op_msg.id >> 16,
                           op_type_to_str(op_msg.type, rt_decoder))


def _get_rt_decoder(rt_id: int) -> AiRunTimeDecoder:
    """Return RT decoder for a given RunTime"""  # noqa: DAR101,DAR201,DAR401
    decoder = _SUPPORTED_AI_RT.get(rt_id & 0xFF, AiRunTimeDecoder())
    decoder.set_rt_id(rt_id)
    return decoder


class DeviceDecoder():
    """Default decoder for generic device"""
    def __init__(self, sys_info_msg):
        self._sys_info_msg = sys_info_msg
        self._config = {}
        self._s_msgs = []

    def _is_stellar_family(self):
        """Return true if the device ID is in the stellar family"""
        # SR5E1, SR6P3, SR6P6, SR6P7, SR6G3 
        # SR6G6, SR6G7, SR6P7G7, SR6P3E
        stellar_ids = {
            0x2511, 0x2643, 0x2646, 0x2647, 0x2633,
            0x2636, 0x2637, 0x2A47, 0x2663
        }
        return self.get_dev_id() in stellar_ids

    def _is_stm32_npu(self):
        """."""
        return self.get_dev_id() in [0x486, 0x47B] # 0x486: N6 / 0x47B: H7P

    def family(self) -> str:
        """Return family description"""  # noqa: DAR101,DAR201,DAR401
        return 'stellar' if self._is_stellar_family() else 'stm32'

    def get_dev_id(self) -> int:
        """Return device ID value"""  # noqa: DAR101,DAR201,DAR401
        return self._sys_info_msg.devid

    def get_sys_clk(self) -> int:
        """Return sys/mcu clock value (Hertz)"""  # noqa: DAR101,DAR201,DAR401
        return self._sys_info_msg.sclock

    def get_bus_clk(self) -> int:
        """Return main bus clock value (Hertz)"""  # noqa: DAR101,DAR201,DAR401
        return self._sys_info_msg.hclock

    def get_dev_id_str(self) -> str:
        """Return short desc of the associated device ID"""  # noqa: DAR101,DAR201,DAR401
        return stm32_id_to_str(self.get_dev_id())

    def get_attrs(self) -> List[str]:
        """Return the device settings"""  # noqa: DAR101,DAR201,DAR401
        attrs_ = stm32_attr_config(self._sys_info_msg.cache)
        if self._is_stm32_npu() and self._config:
            npu_cache = int(self._config.get('npu_cache', '0'))
            attrs_.append(f'npu_cache={npu_cache}')
            for key, val in self._config.items():
                if 'freq' in key:
                    attrs_.append(f'{key}={int(int(val) / 1000000)}MHz')
        elif self._is_stm32_npu() and hasattr(self._sys_info_msg, 'extra'):
            attrs_.append(f'npu_freq={int(self._sys_info_msg.extra[1] / 1000000)}MHz')
            attrs_.append(f'nic_freq={int(self._sys_info_msg.extra[2] / 1000000)}MHz')
        return attrs_

    def get_runtime_mode(self) -> str:
        """Return a short description of the used run-time"""  # noqa: DAR101,DAR201,DAR401
        return "bare-metal"

    def get_desc(self) -> str:
        """Return short description of the device settings"""  # noqa: DAR101,DAR201,DAR401
        desc_ = self.family() + ' family - '
        desc_ += stm32_id_to_str(self._sys_info_msg.devid)
        desc_ += f' @{self._sys_info_msg.sclock / 1000000:.0f}/'
        desc_ += f'{self._sys_info_msg.hclock / 1000000:.0f}MHz'
        return desc_

    def set_device_extra(self, s_msgs: List[str]):
        """Save the config info from the 's:' message"""
        self._s_msgs = [msg_.replace('s:config:','') for msg_ in s_msgs]
        self._s_msgs.append(f'dev_family:{self.family()}')
        self._s_msgs.append(f'dev_desc:{stm32_id_to_str(self.get_dev_id())}')
        for s_msg_ in s_msgs:
            tokens_ = s_msg_.split(':')
            if len(tokens_) > 3 and tokens_[0] == 's' and tokens_[1] == 'config':
                self._config[tokens_[2]] = ':'.join(tokens_[3:])

    def get_device_extra(self):
        """Return device config ('s:' message format)"""
        return self._s_msgs

    def __str__(self) -> str:
        """."""
        desc_ = f'DEV_DECODER: {self.get_desc()}, {self.get_attrs()}'
        return desc_


def _get_device_decoder(sys_info_msg):
    """Return DEVICE decoder object for a given Device ID"""  # noqa: DAR101,DAR201,DAR401
    return DeviceDecoder(sys_info_msg)


def _get_shape_from_msg(msg):
    """Helper fct to return a tuple with the effective shape"""  # noqa: DAR101,DAR201,DAR401
    # see "ai_platform.h" file
    #
    #   - AI_SHAPE_BCWH format
    #       define AI_SHAPE_EXTENSION      (0x5)
    #       define AI_SHAPE_DEPTH          (0x4)
    #       define AI_SHAPE_HEIGHT         (0x3)
    #       define AI_SHAPE_WIDTH          (0x2)
    #       define AI_SHAPE_CHANNEL        (0x1)
    #       define AI_SHAPE_IN_CHANNEL     (0x0)
    #       define AI_SHAPE_BATCH          (0x0)
    #       define AI_SHAPE_TIME           (0x0)
    #
    # s_size = msg.n_dims & 0xFFFFFF = len(msg.dims)

    s_type = msg.n_dims >> stm32msg.F_SHAPE_FMT_POS
    shape = (1,)

    if (s_type & 0xF) == stm32msg.F_SHAPE_FMT_UND or (s_type & 0xF) == stm32msg.F_SHAPE_FMT_RAW:
        # returned shape is used as-is
        shape = tuple(msg.dims)
        return shape

    if (s_type & 0xF) == stm32msg.F_SHAPE_FMT_ST_AI:
        # ST.AI shape format
        if not s_type & stm32msg.F_SHAPE_FMT_HAS_BATCH or msg.dims[0] != 1:
            shape = (1,) + tuple(msg.dims)
        else:
            shape = tuple(msg.dims)
        return shape

    if s_type == stm32msg.F_SHAPE_FMT_BHWC:
        if len(msg.dims) == 1:  # b
            shape = (msg.dims[0],)
        elif len(msg.dims) == 2:  # bx
            shape = (msg.dims[0], 1, 1, msg.dims[1])
        elif len(msg.dims) == 3:  # bxy
            shape = (msg.dims[0], msg.dims[1], 1, msg.dims[2])
        elif len(msg.dims) == 4:  # bhwc
            shape = (msg.dims[0], msg.dims[1], msg.dims[2], msg.dims[3])
        elif len(msg.dims) == 5:  # bhwdc
            shape = (msg.dims[0], msg.dims[1], msg.dims[2], msg.dims[3], msg.dims[4])
        elif len(msg.dims) == 6:  # bhwdec
            shape = (msg.dims[0], msg.dims[1], msg.dims[2], msg.dims[3], msg.dims[4], msg.dims[5])
        return shape

    if s_type == stm32msg.F_SHAPE_FMT_BCHW:  # chw (ONNX or STNeuralART RT)
        if len(msg.dims) == 4:  # rank4 (a,b,c,d) gen code = (a,c,d,b)
            shape = (msg.dims[0], msg.dims[3], msg.dims[1], msg.dims[2])
            return shape
        elif len(msg.dims) == 5:  # rank4 (a,b,c,d,e) gen code = (a,b,d,e,c)
            shape = (msg.dims[0], msg.dims[1], msg.dims[4], msg.dims[2], msg.dims[3])
            return shape
        elif len(msg.dims) == 6:  # rank4 (a,b,c,d,e,f) gen code = (a,b,c,e,f,d)
            shape = (msg.dims[0], msg.dims[1], msg.dims[2], msg.dims[5], msg.dims[3], msg.dims[4])
            return shape
        else:
            raise HwIOError(f'STNeuralART tensor not yet considered, dims={msg.dims}')

    if s_type == stm32msg.F_SHAPE_FMT_BCWH:
        if len(msg.dims) == 1:  # bhwc, flatten buffer (memory chunk for acts/params)
            shape = (1, 1, 1, msg.dims[0])
        elif len(msg.dims) == 4:  # bhwc
            shape = (msg.dims[0], msg.dims[3], msg.dims[2], msg.dims[1])
        elif len(msg.dims) == 5:  # bhwdc
            shape = (msg.dims[0], msg.dims[3], msg.dims[2], msg.dims[4], msg.dims[1])
        elif len(msg.dims) == 6:  # bhwdec
            shape = (msg.dims[0], msg.dims[3], msg.dims[2], msg.dims[4], msg.dims[5], msg.dims[1])

    return shape


def _tensor_to_io_tensor(msg, name=None, tag=None):
    """Convert a TensorDescMsg to a IOTensor object"""  # noqa: DAR101,DAR201,DAR401
    msg = msg.desc if isinstance(msg, stm32msg.aiTensorMsg) else msg
    quant = {
        'scale': np.float32(msg.scale),
        'zero_point': np.array([msg.zeropoint]).astype(AiBufferFormat(msg.format).to_np_type())[0]
    }
    io_tensor = IOTensor(AiBufferFormat(msg.format), _get_shape_from_msg(msg), quant)
    io_tensor.set_name(msg.name if msg.name else name if name else '')
    io_tensor.set_tag(tag if tag else '')
    io_tensor.set_c_addr(msg.addr)
    if msg.flags & stm32msg.TENSOR_FLAG_IN_MEMPOOL:
        if msg.flags & stm32msg.TENSOR_FLAG_MEMPOOL:
            io_tensor.set_memory_pool('mempool')
        else:
            io_tensor.set_memory_pool('activations')
    elif msg.flags & (stm32msg.TENSOR_FLAG_INPUT | stm32msg.TENSOR_FLAG_OUTPUT):
        io_tensor.set_memory_pool('user')
    if not io_tensor.is_packed and np.abs(msg.size - io_tensor.size) > 3:
        msg_ = f'Received TensorDesc is not consistent: {io_tensor} - {io_tensor.size} -> {msg.size}'
        raise HwIOError(msg_)
    return io_tensor


def _decode_tensor_msg(msg, name, tag):
    """Decode aiTensorMsg to ndarray/IOTensor object"""  # noqa: DAR101,DAR201,DAR401
    tensor_msg = msg.tensor if isinstance(msg, stm32msg.respMsg) else msg

    io_tensor = _tensor_to_io_tensor(tensor_msg, name, tag)
    is_last = tensor_msg.desc.flags & stm32msg.TENSOR_FLAG_LAST == stm32msg.TENSOR_FLAG_LAST

    data = tensor_msg.data
    c_shape = io_tensor.get_c_shape()
    dt_ = np.dtype(io_tensor.dtype)
    dt_ = dt_.newbyteorder('<')

    if not data.datas or (tensor_msg.desc.flags & stm32msg.TENSOR_FLAG_NO_DATA):
        return np.array([], dtype=dt_), io_tensor, is_last
    # mutable_arr = np.frombuffer(bytearray(data.datas), dtype=dt_)
    mutable_arr = np.fromstring(data.datas, dtype=dt_)

    return np.reshape(mutable_arr, c_shape), io_tensor, is_last


def _get_model_io_desc(io_tensors):
    """Return list with descrion of the IO tensors"""  # noqa: DAR101,DAR201,DAR401
    items = []
    for io_tensor in io_tensors:
        item = {
            'name': io_tensor.name,
            'shape': io_tensor.shape,
            'type': io_tensor.dtype,
            'io_tensor': io_tensor,
        }
        if io_tensor.memory_pool:
            item['memory_pool'] = f"in '{io_tensor.memory_pool}' buffer"
        else:
            item['memory_pool'] = 'user'
        item.update(io_tensor.quant_params)
        items.append(item)
    return items


class AiPbMsg(AiRunnerDriver):
    """Class to handle the messages (protobuf-based)"""

    def __init__(self, parent, io_drv: AiHwDriver):
        """Constructor"""  # noqa: DAR101,DAR201,DAR401
        if not hasattr(io_drv, 'set_parent'):
            raise InvalidParamError('Invalid IO Hw Driver type (io_drv)')
        self._req_id = 0
        self._io_drv: AiHwDriver = io_drv
        self._models: Dict = {}  # cache the description of the models
        self._sync = None  # cache for the sync message
        self._sys_info = None  # cache for sys info message
        self._packet_out_size = stm32msg.IO_OUT_PACKET_SIZE
        self._packet_in_size = stm32msg.IO_IN_PACKET_SIZE
        super(AiPbMsg, self).__init__(parent)
        self._io_drv.set_parent(self)
        msg_ = f'creating {self} (v{__version__})'
        self._logger.debug(msg_)
        msg_ = f'creating {self._io_drv}'
        self._logger.debug(msg_)
        self._target_msg: List[str] = []  # used to store the 's:' from target

    @property
    def is_connected(self):
        return self._io_drv.is_connected

    def connect(self, desc=None, **kwargs):
        """Connect to the st.ai run-time"""  # noqa: DAR101,DAR201,DAR401
        if self._io_drv.is_connected:
            self._logger.debug("driver is already connected..")
            return False
        return self._io_drv.connect(desc, logger=self._logger, **kwargs)

    @property
    def capabilities(self):
        """Return list with capabilities"""
        # noqa: DAR101,DAR201,DAR401
        if self.is_connected:
            cap_ = [AiRunner.Caps.IO_ONLY]
            if self._sync.capability & stm32msg.CAP_OBSERVER:
                cap_.extend([AiRunner.Caps.PER_LAYER, AiRunner.Caps.PER_LAYER_WITH_DATA])
            if self._sync.capability & stm32msg.CAP_SELF_TEST:
                cap_.append(AiRunner.Caps.SELF_TEST)
            if self._sync.capability & stm32msg.CAP_RELOC:
                cap_.append(AiRunner.Caps.RELOC)
            if self._sync.capability & stm32msg.CAP_READ_WRITE:
                cap_.append(AiRunner.Caps.MEMORY_RW)
            if self._sync.capability & stm32msg.CAP_USBC:
                cap_.append(AiRunner.Caps.USBC)
            return cap_
        return []

    def disconnect(self):
        self._models = dict()
        self._sys_info = None
        self._sync = None
        self._cmd_disconnect()
        self._io_drv.disconnect()

    def short_desc(self) -> str:
        """Return human readable description"""  # noqa: DAR101,DAR201,DAR401
        msg_ver_ = f'{stm32msg.P_VERSION_MAJOR}.{stm32msg.P_VERSION_MINOR}'
        io_drv_ = self._io_drv.short_desc(False)
        return f'Proto-buffer driver v{__version__} (msg v{msg_ver_}) ({io_drv_})'

    def _log_msg(self, msg_, desc_):
        """Helper fct to log a PB msg"""

        self._logger.debug('-> [%s msg]', desc_)
        for line_ in str(msg_).splitlines():
            self._logger.debug(line_)
        self._logger.debug('<- [%s msg]', desc_)

    def _waiting_io_ack(self, timeout):
        """Wait a ack"""  # noqa: DAR101,DAR201,DAR401
        start_time = t.perf_counter()
        while True:
            if self._io_drv.read(1):
                break
            if t.perf_counter() - start_time > timeout / 1000.0:
                return False
        return True

    def _write_io_packet(self, payload, delay=0):
        iob = bytearray(self._packet_out_size + 2)
        iob[0] = (len(payload) >> 8) & 0xFF
        iob[1] = len(payload) & 0xFF
        for i, val in enumerate(payload):
            iob[i + 2] = val
        if not delay:
            _w = self._io_drv.write(iob)
        else:
            _w = 0
            for elem in iob:
                _w += self._io_drv.write(elem.to_bytes(1, 'big'))
                t.sleep(delay)
        return _w

    def _write_delimited(self, mess, timeout=5000):
        """Helper function to write a message prefixed with its size"""  # noqa: DAR101,DAR201,DAR401

        if not mess.IsInitialized():
            raise NotInitializedMsgError

        buff = mess.SerializeToString()
        _head = _VarintBytes(mess.ByteSize())

        buff = _head + buff

        packs = [buff[i:i + self._packet_out_size]
                 for i in range(0, len(buff), self._packet_out_size)]

        n_w = self._write_io_packet(packs[0])
        for pack in packs[1:]:
            if not self._waiting_io_ack(timeout):
                break
            n_w += self._write_io_packet(pack)

        return n_w

    def _parse_and_check(self, data, msg_type=None):
        """Parse/convert and check the received buffer"""  # noqa: DAR101,DAR201,DAR401
        resp = stm32msg.respMsg()
        try:
            resp.ParseFromString(data)
        except BaseException as exc_:
            raise InvalidMsgError(str(exc_))
        if msg_type is None:
            return resp
        elif resp.WhichOneof('payload') != msg_type:
            raise InvalidMsgError('receive \'{}\' instead \'{}\''.format(
                resp.WhichOneof('payload'), msg_type))
        return None

    def _waiting_msg(self, timeout, msg_type=None):
        """Helper function to receive a message"""  # noqa: DAR101,DAR201,DAR401
        buf = bytearray()

        packet_s = int(self._packet_in_size + 2)
        if timeout == 0:
            t.sleep(0.2)

        start_time = t.monotonic()
        while True:
            p_buf = bytearray()
            while len(p_buf) < packet_s:
                io_buf = self._io_drv.read(packet_s - len(p_buf))
                if io_buf:
                    p_buf += io_buf
                else:
                    cum_time = t.monotonic() - start_time
                    if timeout and (cum_time > timeout / 1000):
                        raise TimeoutError(
                            'STM32 - read timeout {:.1f}ms/{}ms'.format(cum_time * 1000, timeout))
                    if timeout == 0:
                        return self._parse_and_check(buf, msg_type)
            last = p_buf[0] & stm32msg.IO_HEADER_EOM_FLAG
            # cbuf[0] = cbuf[0] & 0x7F & ~stm32msg.IO_HEADER_SIZE_MSK
            # p_buf[0] &= 0x7F  # & ~stm32msg.IO_HEADER_SIZE_MSK)
            size = (p_buf[0] & 0x7F) << 8 | p_buf[1] & 0xFF
            if last:
                # buf += p_buf[1:1 + p_buf[0]]
                buf += p_buf[2:2 + size]
                break
            # buf += p_buf[1:packet_s]
            buf += p_buf[2:packet_s]
        resp = self._parse_and_check(buf, msg_type)
        return resp

    def _send_request(self, cmd, param=0, name=None, opt=0):
        """Build a request msg and send it"""  # noqa: DAR101,DAR201,DAR401
        self._req_id += 1
        req_msg = stm32msg.reqMsg()
        req_msg.reqid = self._req_id
        req_msg.cmd = cmd
        req_msg.param = param
        req_msg.opt = opt
        if name is not None and isinstance(name, str):
            req_msg.name = name
        else:
            req_msg.name = ''
        n_w = self._write_delimited(req_msg)
        return n_w, req_msg

    def _send_ack(self, param=0, err=0):
        """Build an acknowledge msg and send it"""  # noqa: DAR101,DAR201,DAR401
        ack_msg = stm32msg.ackMsg(param=param, error=err)
        return self._write_delimited(ack_msg)

    def _device_log(self, resp):
        """Process a log message from a device"""  # noqa: DAR101,DAR201,DAR401
        if resp.WhichOneof('payload') == 'log':
            self._send_ack()
            cur_lvl = get_log_level(self._logger)
            msg_lvl = int(resp.log.level)
            if resp.log.str.startswith('s:'):
                self._target_msg.append(resp.log.str)
            if resp.log.str.startswith('s:') and cur_lvl > logging.DEBUG:
                msg_lvl = 2
            msg = f'[TARGET:{resp.log.level}] {resp.log.str}'
            if msg_lvl < 2:
                self._logger.info(msg)
            elif msg_lvl == 2:
                self._logger.debug(msg)
            elif msg_lvl == 3:
                self._logger.warning(msg)
            else:
                self._logger.error(msg)
            return True
        return False

    def _waiting_answer(self, timeout=10000, msg_type=None, state=None):
        """Wait an answer/msg from the device and post-process it"""  # noqa: DAR101,DAR201,DAR401

        cont = True
        while cont:  # to manage the "log" msg
            resp = self._waiting_msg(timeout=timeout)
            if resp.reqid != self._req_id:
                raise InvalidMsgError('SeqID is not valid - {} instead {}'.format(
                    resp.reqid, self._req_id))
            cont = self._device_log(resp)

        if msg_type and resp.WhichOneof('payload') != msg_type:
            err_msg = 'receive \'{}\' instead \'{}\''.format(
                resp.WhichOneof('payload'), msg_type)
            if resp.state == stm32msg.S_ERROR:
                err_msg += ' [{},{}]'.format(resp.ack.error, resp.ack.param)
            raise InvalidMsgError(err_msg)

        if state is not None and state != resp.state:
            raise HwIOError('Invalid state: {} instead {}'.format(
                resp.state, state))

        return resp

    def _cmd_sync(self, timeout):
        """SYNC command"""  # noqa: DAR101,DAR201,DAR401
        self._packet_in_size = stm32msg.IO_IN_PACKET_SIZE
        self._packet_out_size = stm32msg.IO_OUT_PACKET_SIZE
        self._send_request(stm32msg.CMD_SYNC)
        resp = self._waiting_answer(timeout=timeout, msg_type='sync',
                                    state=stm32msg.S_IDLE)
        return resp.sync

    def _cmd_sys_info(self, timeout):
        """SYS_INFO command"""  # noqa: DAR101,DAR201,DAR401
        self._send_request(stm32msg.CMD_SYS_INFO)
        resp = self._waiting_answer(timeout=timeout, msg_type='sinfo',
                                    state=stm32msg.S_IDLE)
        if resp.sinfo.com_param != 0:
            self._packet_in_size = resp.sinfo.com_param
            self._packet_out_size = resp.sinfo.com_param
        return resp.sinfo

    def _cmd_disconnect(self):
        """DISCONNECT command"""  # noqa: DAR101,DAR201,DAR401
        self._send_request(stm32msg.CMD_DISCONNECT)
        self._packet_in_size = stm32msg.IO_IN_PACKET_SIZE
        self._packet_out_size = stm32msg.IO_OUT_PACKET_SIZE
        self._logger.debug('disconnect PB command sent..')

    def _cmd_model_info(self, timeout, param=0):
        """NETWORK_INFO command"""  # noqa: DAR101,DAR201,DAR401
        self._send_request(stm32msg.CMD_NETWORK_INFO, param=param)
        resp = self._waiting_answer(timeout=timeout, state=None)  # stm32msg.S_IDLE)
        if resp.WhichOneof('payload') == 'minfo':
            return resp.minfo
        elif resp.WhichOneof('payload') == 'ack':
            if resp.ack.error == stm32msg.E_GENERIC:
                rt_id_str = _get_rt_decoder(self._sync.rtid).name
                raise InvalidModelError('Model for {} is not initialized ({})'.format(
                    param, rt_id_str))
        return None

    def _cmd_run(self, timeout, c_name, param, opt=0):
        """NETWORK_RUN command"""  # noqa: DAR101,DAR201,DAR401
        self._send_request(stm32msg.CMD_NETWORK_RUN, param=param, name=c_name, opt=opt)
        resp = self._waiting_answer(timeout=timeout, msg_type='ack',
                                    state=stm32msg.S_WAITING)
        return resp

    def _cmd_memory_checksum(self, timeout, addr, size):
        """MEMORY_CHECKSUM command"""  # noqa: DAR101,DAR201,DAR401
        self._send_request(stm32msg.CMD_MEMORY_CHECKSUM, param=addr, opt=size)
        resp = self._waiting_answer(timeout=timeout, msg_type='ack',
                                    state=stm32msg.S_DONE)
        return resp

    def _cmd_memory_write(self, timeout, addr, size):
        """MEMORY_WRITE command"""  # noqa: DAR101,DAR201,DAR401
        self._send_request(stm32msg.CMD_MEMORY_WRITE, param=addr, opt=size)
        resp = self._waiting_answer(timeout=timeout, msg_type='ack',
                                    state=stm32msg.S_WAITING)
        return resp

    def _cmd_memory_read(self, timeout, addr, size):
        """MEMORY_READ command"""  # noqa: DAR101,DAR201,DAR401
        self._send_request(stm32msg.CMD_MEMORY_READ, param=addr, opt=size)
        resp = self._waiting_answer(timeout=timeout, msg_type='ack',
                                    state=stm32msg.S_PROCESSING)
        return resp

    def _get_protocol_version(self):
        """Return tuple with PB protocol version"""
        if self._sync is None:
            return 0, 0
        return self._sync.version >> 8, self._sync.version & 0xFF

    def _protocol_is_supported(self):
        """Indicate if the protocol version is supported"""  # noqa: DAR101,DAR201,DAR401
        major, minor = self._get_protocol_version()
        if major == stm32msg.P_VERSION_MAJOR and minor <= stm32msg.P_VERSION_MINOR:
            return True
        err_msg = f'COM Protocol is not supported: {major}.{minor},'
        err_msg += f' expected {stm32msg.P_VERSION_MAJOR}.{stm32msg.P_VERSION_MINOR}'
        raise HwIOError(err_msg)

    def _send_data(self, data, buffertype=0, addr=0, is_last=False, state=None):
        """Send a data to the device and wait an ack"""  # noqa: DAR101,DAR201,DAR401

        if isinstance(data, np.ndarray):
            dt_ = np.dtype(data.dtype.type)
            dt_ = dt_.newbyteorder('<')
            datas = bytes(data.astype(dt_).flatten().tobytes())
        else:
            datas = data

        if not isinstance(datas, (bytearray, bytes)):
            err_msg = f'Invalid data type: {type(datas)} instead bytes'
            raise HwIOError(err_msg)

        data_msg = stm32msg.aiDataMsg()
        data_msg.addr = addr  # pylint: disable=no-member
        data_msg.type = buffertype  # pylint: disable=no-member
        data_msg.datas = bytes(datas)  # pylint: disable=no-member
        data_msg.size = len(data_msg.datas)  # pylint: disable=no-member
        self._write_delimited(data_msg)

        state = state if state is not None\
            else stm32msg.S_DONE if is_last else stm32msg.S_WAITING
        resp = self._waiting_answer(msg_type='ack', state=state)
        return resp

    def _send_input_buffer(self, data, is_last=False):
        """Send the data from a buffer to the device and wait an ack"""  # noqa: DAR101,DAR201,DAR401

        state = stm32msg.S_PROCESSING if is_last else stm32msg.S_WAITING
        resp = self._send_data(data, state=state)
        self._send_ack()
        return resp

    def _receive_data(self):
        """Receive a data from the device and sent an ack"""  # noqa: DAR101,DAR201,DAR401
        resp = self._waiting_answer(msg_type='data')
        if resp.state == stm32msg.S_PROCESSING:
            self._send_ack()
        is_last = resp.state == stm32msg.S_DONE
        data_msg = resp.data
        buffertype = data_msg.type
        data = data_msg.datas
        addr = data_msg.addr
        return (data, addr, buffertype, is_last)

    def is_alive(self, timeout=500):
        """"Indicate if the connection is always alive"""  # noqa: DAR101,DAR201,DAR401
        try:
            self._sync = self._cmd_sync(timeout)
            self._log_msg(self._sync, 'sync')
            pb_vers_ = self._get_protocol_version()
            self._logger.debug('CMD_SYNC v%s.%s', pb_vers_[0], pb_vers_[1])
        except (AiRunnerError, TimeoutError) as exc_:
            self._logger.debug('is_alive() %s', str(exc_))
            return False
        return self._protocol_is_supported()

    def _to_device(self, dev_decoder):
        """Return a dict with the device settings"""  # noqa: DAR101,DAR201,DAR401
        return {
            'dev_type': dev_decoder.family(),
            'desc': dev_decoder.get_desc(),
            'dev_id': dev_decoder.get_dev_id(),
            'system': dev_decoder.get_runtime_mode(),
            'sys_clock': dev_decoder.get_sys_clk(),
            'bus_clock': dev_decoder.get_bus_clk(),
            'attrs': dev_decoder.get_attrs(),
            'extra': dev_decoder.get_device_extra()
        }

    def _to_runtime(self, model_info, rt_decoder):
        """Return a dict with the runtime attributes"""  # noqa: DAR101,DAR201,DAR401
        return {
            'protocol': self.short_desc(),
            'name': rt_decoder.name,
            'rt_lib_desc': rt_decoder.runtime_desc(model_info.runtime_desc,
                                                   model_info.runtime_version),
            'compiler': _tools_desc(rt_decoder.compiler_id),
            'version': _to_version(model_info.runtime_version),
            'capabilities': self.capabilities,
            'tools_version': _to_version(model_info.tool_version),
        }

    def _model_to_dict(self, model):
        """Return a dict with the network info"""  # noqa: DAR101,DAR201,DAR401
        model_info = model['info']
        rt_decoder_ =  model['rt_decoder']
        dev_decoder_ = model['dev_decoder']
        params_size_ = sum([p.size for p in model_info.params])
        acts_size_ = sum([p.size for p in model_info.activations])
        return {
            'version': STAI_INFO_DICT_VERSION,
            'name': model_info.name,
            'rt': rt_decoder_.name,
            'compile_datetime': model_info.compile_datetime,
            'hash': model_info.signature,
            'n_init_time': model_info.n_init_time,
            'n_install_time': model_info.n_install_time,
            'n_nodes': model_info.n_nodes,
            'inputs': _get_model_io_desc(model['tens_inputs']),
            'outputs': _get_model_io_desc(model['tens_outputs']),
            'weights': params_size_ if rt_decoder_.has_params() else None,
            'activations': acts_size_ if rt_decoder_.has_activations() else None,
            'mempools': {
                'params': _get_model_io_desc(model['tens_params']),
                'activations': _get_model_io_desc(model['tens_activations'])
            },
            'macc': model_info.n_macc if rt_decoder_.has_macc() else None,
            'runtime': self._to_runtime(model_info, rt_decoder_),
            'device': self._to_device(dev_decoder_),
        }

    def get_info(self, c_name=None):
        """Return a dict with the network info of a given model"""  # noqa: DAR101,DAR201,DAR401
        if not self._models:
            return dict()
        if c_name is None or c_name not in self._models:  # .keys():
            # first c-model is used
            c_name = self._models.keys()[0]
        model = self._models[c_name]
        if 'cache_info' not in model:
            model['cache_info'] = self._model_to_dict(model)
        return model['cache_info']

    def _register_model(self, model_info_msg):
        """Register a new model"""  # noqa: DAR101,DAR201,DAR401
        def _build_io_tensor_list(info_io, prefix, ptag):
            items = []
            for idx, desc in enumerate(info_io):
                tag = f'{ptag}.{idx}'
                items.append(_tensor_to_io_tensor(desc, f'{prefix}_{idx + 1}', tag))
            return items
        rt_decoder_ = _get_rt_decoder(model_info_msg.rtid)
        dev_decoder_ = _get_device_decoder(self._sys_info)
        dev_decoder_.set_device_extra(self._target_msg)
        self._logger.debug(str(rt_decoder_))
        self._logger.debug(str(dev_decoder_))
        self._models[model_info_msg.name] = {
            'info': model_info_msg,
            'tens_inputs': _build_io_tensor_list(model_info_msg.inputs, 'input', 'I'),
            'tens_outputs': _build_io_tensor_list(model_info_msg.outputs, 'output', 'O'),
            'tens_activations': _build_io_tensor_list(model_info_msg.activations, 'act', 'A'),
            'tens_params': _build_io_tensor_list(model_info_msg.params, 'param', 'W'),
            'rt_decoder': rt_decoder_,
            'dev_decoder': dev_decoder_,
        }
        return model_info_msg.name

    def discover(self, flush=False):
        """Build the list of the available model"""  # noqa: DAR101,DAR201,DAR401
        if flush:
            self._models.clear()
        if self._models:
            return list(self._models.keys())
        param, cont = 0, True

        if self._sys_info is None:
            self._sys_info = self._cmd_sys_info(timeout=500)
        self._log_msg(self._sys_info, 'sys_info')
        self._logger.debug('set packet size to %d/%d bytes', self._packet_in_size,
                           self._packet_out_size)

        while cont:
            self._target_msg = []  # reset buffer to store the 's:' message from target
            n_info = self._cmd_model_info(timeout=5000, param=param)
            if n_info is not None:
                self._log_msg(n_info, 'model_info')
            if n_info is not None:
                name = self._register_model(n_info)
                msg = f'discover() found="{name}"'
                self._logger.debug(msg)
                param += 1
            else:
                cont = False
        return list(self._models.keys())

    def _receive_features(self, profiler, callback, rt_decoder):
        """Collect the intermediate/hidden values"""  # noqa: DAR101,DAR201,DAR401

        # main loop to receive the datas
        idx_node = 0
        duration = 0.0
        req_state = stm32msg.S_PROCESSING
        self._target_msg = []

        while True:  # to iterate on the internal operators
            self._logger.debug('-' * 40)
            resp = self._waiting_answer(msg_type='op', timeout=50000, state=req_state)
            cur_op = resp.op
            if cur_op.type >> stm32msg.OPERATOR_FLAG_POS == stm32msg.OPERATOR_FLAG_NONE:
                # not an internal operator
                if idx_node != 0 and profiler:
                    # to prevent the case, where OPERATOR_FLAG_LAST is not used by the RT
                    profiler['c_durations'].append(duration)
                return resp
            # self._send_ack()

            node_name = cur_op.name if cur_op.name else rt_decoder.default_name_node(idx_node, cur_op.id)
            self._logger.debug(f'INTERNAL OPERATOR (idx={idx_node}, name={node_name})')
            # self._logger.debug('{}'.format(cur_op))
            self._logger.debug(op_msg_to_str(cur_op, rt_decoder))
            counters_ = rt_decoder.counter_decode(cur_op.counter_type, resp.op.counters)

            idx_tens = 0
            io_tensors, shapes, features, types, scales, zeropoints = [], [], [], [], [], []
            while True:  # to iterate on the internal tensors

                if cur_op.type >> 24 & stm32msg.OPERATOR_FLAG_WITHOUT_TENSOR\
                        == stm32msg.OPERATOR_FLAG_WITHOUT_TENSOR:
                    break

                resp = self._waiting_answer(msg_type='tensor', timeout=100, state=req_state)
                cur_tensor = resp.tensor

                self._logger.debug('INTERNAL TENSOR #{}'.format(idx_tens))
                # self._logger.debug('{}'.format(cur_tensor.desc))

                # self._send_ack()
                tag = rt_decoder.get_tag(idx_node, idx_tens, cur_op.id)
                def_tens_name = rt_decoder.default_name_tensor(idx_node, idx_tens)
                feature, io_tensor, is_last = _decode_tensor_msg(cur_tensor, def_tens_name, tag)
                io_tensors.append(io_tensor)
                shapes.append(io_tensor.shape)
                types.append(io_tensor.dtype)
                scales.append(io_tensor.quant_params['scale'])
                zeropoints.append(io_tensor.quant_params['zero_point'])
                features.append(feature)

                self._logger.debug(' {}'.format(io_tensor.desc(full=True)))
                self._logger.debug(' last={}, data_size={}'.format(is_last, feature.size * feature.itemsize))

                idx_tens += 1

                if is_last:  # last tensor
                    break

            if profiler:
                duration += cur_op.duration
                self._target_msg = [v_.replace('s:node:','') for v_ in self._target_msg]
                if idx_node >= len(profiler['c_nodes']):
                    item = {
                        'name': cur_op.name if cur_op.name else rt_decoder.default_name_node(idx_node, cur_op.id),
                        'counters': {
                            'type': rt_decoder.counter_desc(cur_op.counter_type),
                            'values': [counters_]
                        },
                        'c_durations': [cur_op.duration],
                        'm_id': rt_decoder.m_id(cur_op.id),
                        'layer_type': rt_decoder.op_type(cur_op.type),
                        'layer_desc': rt_decoder.op_desc(cur_op.type),
                        'type': types,
                        'shape': shapes,  # feature.shape,
                        'scale': scales,
                        'zero_point': zeropoints,
                        'io_tensors': io_tensors,
                        'data': features if features is not None else None,
                        'extra': [self._target_msg]
                    }
                    profiler['c_nodes'].append(item)
                else:
                    item = profiler['c_nodes'][idx_node]
                    item['c_durations'].append(cur_op.duration)
                    item['counters']['values'].append(counters_)
                    for idx, _ in enumerate(features):
                        item['data'][idx] = np.append(item['data'][idx], features[idx], axis=0)
                    item['extra'].append(self._target_msg)
                self._target_msg = []

            if callback:
                callback.on_node_end(idx_node,
                                     features if features is not None else None,
                                     logs={'dur': cur_op.duration,
                                           'shape': shapes,
                                           'm_id': rt_decoder.m_id(cur_op.id),
                                           'layer_type': rt_decoder.op_type(cur_op.type)})

            # end main loop / last operator
            if cur_op.type >> stm32msg.OPERATOR_FLAG_POS & stm32msg.OPERATOR_FLAG_LAST:
                break

            idx_node += 1

        if profiler:
            profiler['c_durations'].append(duration)

        return None

    def invoke_sample(self, s_inputs, **kwargs):
        """Invoke the model (sample mode)"""  # noqa: DAR101,DAR201,DAR401

        if s_inputs[0].shape[0] != 1:
            raise HwIOError('Should be called with a batch size of 1')

        name = kwargs.pop('name', None)

        if name is None or name not in self._models:
            raise InvalidParamError('Invalid requested model name: ' + name)

        model = self._models[name]

        rt_decoder = model['rt_decoder']
        profiler = kwargs.pop('profiler', None)
        mode = kwargs.pop('mode', AiRunner.Mode.IO_ONLY)
        callback = kwargs.pop('callback', None)
        sample_idx = kwargs.pop('sample_idx', -1)
        option = kwargs.pop('option', 0)

        param = stm32msg.P_RUN_MODE_IO_ONLY
        if mode & AiRunner.Mode.PER_LAYER:
            param |= stm32msg.P_RUN_MODE_PER_LAYER
        if mode & AiRunner.Mode.PER_LAYER_WITH_DATA:
            param |= stm32msg.P_RUN_MODE_PER_LAYER_WITH_DATA

        if (mode & AiRunner.Mode.CONST_VALUE) or (mode & AiRunner.Mode.FIXED_INPUT):
            param |= stm32msg.P_RUN_CONF_CONST_VALUE
        if mode & AiRunner.Mode.DEBUG:
            param |= stm32msg.P_RUN_CONF_DEBUG

        if mode & AiRunner.Mode.PERF_ONLY:
            param |= stm32msg.P_RUN_MODE_PERF
            param |= stm32msg.P_RUN_CONF_CONST_VALUE
            param &= ~stm32msg.P_RUN_MODE_PER_LAYER_WITH_DATA

        option = rt_decoder.build_option_parameter(option, sample_idx)
        direct_write_ = False
        if self._io_drv.write_memory(0, None) == 1:
            param |= stm32msg.P_RUN_CONF_DIRECT_WRITE
            direct_write_ = True

        self._logger.debug(f'-> Requested RUN mode: {mode} (param={bin(param)}, option={hex(option)})')

        s_outputs = []
        self._target_msg = []

        # start a RUN task
        self._cmd_run(timeout=1000, c_name=name, param=param, opt=option)

        # send the inputs
        for idx, input_ in enumerate(s_inputs):
            is_last = (idx + 1) == model['info'].n_inputs
            target_addr = model['tens_inputs'][idx].c_addr
            self._logger.debug(f'SEND INPUT TENSOR #{idx} ({input_.shape}/{input_.dtype}) last={is_last}..')
            if (direct_write_ and target_addr) or (param & stm32msg.P_RUN_CONF_CONST_VALUE):
                if direct_write_ and target_addr:
                    dt_ = np.dtype(input_.dtype.type)
                    dt_ = dt_.newbyteorder('<')
                    datas = bytes(input_.astype(dt_).flatten().tobytes())
                    self._io_drv.write_memory(target_addr, datas)
                input0_ = np.array(input_.flatten()[0]).astype(input_.dtype)
                if not direct_write_:
                    self._logger.debug(f' buffer is filled with a simple value: {input0_}')
                self._send_input_buffer(input0_, is_last=is_last)
            else:
                self._send_input_buffer(input_, is_last=is_last)

        # receive the features
        resp = self._receive_features(profiler, callback, model['rt_decoder'])

        # receive final operation info (model)
        if resp is None:
            self._logger.debug('-' * 40)
            resp = self._waiting_answer(msg_type='op', timeout=50000, state=stm32msg.S_PROCESSING)
        # self._send_ack()
        self._logger.debug('INFERENCE DONE')
        self._logger.debug(op_msg_to_str(resp.op, model['rt_decoder']))
        counter_type_ = model['rt_decoder'].counter_desc(resp.op.counter_type)
        counters_ = model['rt_decoder'].counter_decode(resp.op.counter_type, resp.op.counters)

        inference_dur = resp.op.duration
        if profiler:
            profiler['debug']['counters']['type'] = counter_type_
            profiler['debug']['counters']['values'].append(counters_)
            profiler['debug']['stack_usage'] = resp.op.stack_used
            profiler['debug']['heap_usage'] = resp.op.heap_used

        # receive outputs of the model
        for idx in range(model['info'].n_outputs):
            is_last = (idx + 1) == model['info'].n_outputs
            self._logger.debug('RECEIVE OUTPUT TENSOR #{} last={}..'.format(idx, is_last))
            state = stm32msg.S_DONE if is_last else stm32msg.S_PROCESSING
            resp = self._waiting_answer(msg_type='tensor', timeout=50000, state=state)
            tag = 'O_{}'.format(idx)
            output, io_tens_, tens_is_last = _decode_tensor_msg(resp, '', tag)
            s_outputs.append(output)
            if is_last != tens_is_last:
                msg = 'Number of received output tensor is not valid'
                raise HwIOError(msg)
            self._logger.debug(' {}'.format(io_tens_.desc(full=True)))
            # if not is_last:
            #    self._send_ack()

        if profiler:
            profiler['debug']['exec_times'].append(inference_dur)
            if mode & (AiRunner.Mode.PER_LAYER | AiRunner.Mode.PER_LAYER_WITH_DATA):
                dur = profiler['c_durations'][-1]
            else:
                dur = inference_dur
                profiler['c_durations'].append(inference_dur)
        else:
            dur = inference_dur

        self._logger.debug(f'<- done (target dur={dur:.03f}ms)')

        return s_outputs, dur

    def extension(self, name=None, **kwargs):
        """Specific command"""  # noqa: DAR101,DAR201,DAR401

        ihex_files = kwargs.pop('ihex', [])
        cmd = kwargs.pop('cmd', None)
        resp_ = {'error': stm32msg.E_GENERIC, 'crc': 0, 'data': None}

        if not self._io_drv.is_connected:
            self._logger.error('No board is connected..')
            return resp_

        # -- specific cmd for unit-tests
        if cmd == 'unit-test':
            return self._unit_tests(name=name, **kwargs)

        if cmd == 'self-test':
            return self._self_tests(name=name, **kwargs)

        # -- read/write cmd
        if AiRunner.Caps.MEMORY_RW not in self.capabilities:
            self._logger.error('RW memory capatibility not available')
            return resp_

        # read/write data to/from memory
        if cmd in ['write-in-memory', 'read-in-memory', 'checksum-in-memory']:
            return self._rw_memory_services(cmd, **kwargs)

        # write ihex files
        if not ihex_files or cmd != 'write':
            self._logger.error('ihex files should be provided with the \'write\' cmd')
            return resp_

        msg_ = f'loading {len(ihex_files)} ihex file(s) (name=\'{name}\')'
        self._logger.info(msg_)
        fill_zeros = kwargs.pop('fill_zeros', True)

        for ihex_file in ihex_files:
            self._logger.info('loading {}'.format(ihex_file))
            segs = dump_ihex_file(ihex_file, fill_with_zeros=fill_zeros) if os.path.isfile(ihex_file) else []
            if not segs:
                msg_ = ' \'{}\' Intel HEX file is empty or invalid'.format(ihex_file)
                self._logger.warning(msg_)
                return {'error': stm32msg.E_INVALID_PARAM, 'crc': 0, 'data': None}
            for seg in segs:
                if not seg['data']:
                    continue
                resp_ = self._rw_memory_services('write-in-memory',
                                                 target_addr=seg['addr'],
                                                 data=seg['data'])
                if resp_['error'] != stm32msg.E_NONE:
                    break

        return resp_

    def _rw_memory_services(self, cmd, **kwargs):
        """Memory RW services"""  # noqa: DAR101,DAR201,DAR401

        target_addr = kwargs.pop('target_addr', 0)
        data = kwargs.pop('data', None)
        size = kwargs.pop('size', 0)
        timeout = kwargs.pop('timeout', 500)

        if not target_addr:
            return {'error': stm32msg.E_INVALID_PARAM, 'crc': 0, 'data': None}

        if size and cmd == 'checksum-in-memory':
            resp = self._cmd_memory_checksum(timeout=timeout, addr=target_addr, size=size)
            return {'error': resp.ack.error, 'crc': resp.ack.param, 'data': None}

        if data is not None and cmd == 'write-in-memory':
            if not isinstance(data, (bytearray, bytes)):
                msg = 'Invalid data type: {} instead bytes'.format(type(data))
                raise HwIOError(msg)
            size = len(data)
            resp = self._cmd_memory_write(timeout=timeout, addr=target_addr, size=size)
            if resp.ack.error != stm32msg.E_NONE:
                return {'error': resp.ack.error, 'crc': 0, 'data': None}
            w_size = 0
            pw_data = data[0:resp.ack.param]
            addr = target_addr
            while pw_data:
                w_size += len(pw_data)
                hash_ = bsdchecksum(pw_data)
                resp = self._send_data(pw_data, addr=addr, is_last=(w_size == size))
                bsd = resp.ack.param
                self._logger.debug('writing data @{}/{} bsd={}'.format(hex(addr), len(pw_data), bsd))
                if hash_ != bsd:
                    return {'error': stm32msg.E_GENERIC, 'crc': 0, 'data': None}
                addr += len(pw_data)
                pw_data = data[w_size:w_size + len(pw_data)]
            return {'error': stm32msg.E_NONE, 'crc': 0, 'data': None}

        if size and cmd == 'read-in-memory':
            resp = self._cmd_memory_read(timeout=timeout, addr=target_addr, size=size)
            if resp.ack.error != stm32msg.E_NONE:
                return {'error': resp.ack.error, 'crc': 0, 'data': None}
            r_size = size
            r_data = bytes()
            while r_size:
                seg_data, _, _, _ = self._receive_data()
                r_data += seg_data
                r_size -= len(seg_data)
            return {'error': stm32msg.E_NONE, 'crc': 0, 'data': r_data}

        return {'error': stm32msg.E_INVALID_PARAM, 'crc': 0, 'data': None}

    def _unit_tests(self, **kwargs):
        """Unit tests"""  # noqa: DAR101,DAR201,DAR401

        test_id = kwargs.pop('test_id', None)
        params = kwargs.pop('params', 1)
        if not isinstance(params, list):
            params = [params]
        timeout = kwargs.pop('timeout', 500)

        self._logger.debug(f'<unit-test:{test_id}> params={params}')

        if test_id == 0:  # Send a sync request (~is_alive)
            while params[0]:
                sync = self._cmd_sync(timeout)
                self._log_msg(sync, f'sync ({params[0]})')
                params[0] -= 1
            info = {
                'version': '{}.{}'.format(sync.version >> 8, sync.version & 0xFF),
                'capability': sync.capability,
                'arm_tools': sync.rtid >> 8,
                'ai_rt': sync.rtid & 0xFF,
            }
            return info

        if test_id == 1:  # send a sys info request
            while params[0]:
                sys_info = self._cmd_sys_info(timeout)
                self._log_msg(sys_info, f'sys_info ({params[0]})')
                params[0] -= 1
            return {'devid': hex(sys_info.devid), 'sclock': int(sys_info.sclock)}

        if test_id == 10:  # send invalid CMD ID req
            self._send_request(stm32msg.CMD_TEST_UNSUPPORTED)
            resp = self._waiting_answer(timeout=timeout, msg_type='ack',
                                        state=stm32msg.S_ERROR)
            return resp.ack.error == stm32msg.E_INVALID_PARAM

        if test_id == 20:  # Send a model info request
            info = self._cmd_model_info(timeout, param=params[0])
            self._log_msg(info, f'info ({params[0]})')
            return info

        return False

    def _self_tests(self, **kwargs):
        """Embedded self-tests"""  # noqa: DAR101,DAR201,DAR401

        test_id = kwargs.pop('test_id', None)
        params = kwargs.pop('params', 1)
        if not isinstance(params, list):
            params = [params]
        timeout = kwargs.pop('timeout', 500)
        e_test_id = kwargs.pop('e_test_id', None)
        if e_test_id is not None:
            e_test_id = e_test_id & 0xFFFF
        else:
            e_test_id = params[0] & 0xFFFF
        opt = kwargs.pop('opt', 0)

        # embedded self-tests (see aiPbMgr.c file, aiPbTestCmd() fct)
        if test_id == 100:
            name = kwargs.pop('name', None)
            self._send_request(stm32msg.CMD_TEST, name=name, param=e_test_id, opt=opt)
            resp = self._waiting_answer(timeout=timeout, msg_type='ack')
            return {'error': resp.ack.error, 'param': resp.ack.param, 'state': resp.state}

        if test_id == 101:
            name = kwargs.pop('name', None)
            self._send_request(stm32msg.CMD_TEST, name=name, param=e_test_id, opt=opt)
            resp = self._waiting_answer(timeout=timeout, msg_type='op')
            return {'op': resp.op, 'state': resp.state}

        if test_id == 102:  # send data msg
            e_test_id = 30
            buffer = kwargs.pop('buffer', None)
            param = ((buffer.size * buffer.itemsize) << 16) + e_test_id
            self._send_request(stm32msg.CMD_TEST, param=param, opt=opt)
            self._waiting_answer(timeout=timeout, msg_type='ack', state=stm32msg.S_WAITING)
            if opt == 0:
                resp = self._send_data(buffer, state=stm32msg.S_DONE)
            else:
                resp = self._send_input_buffer(buffer, is_last=True)
                t.sleep(0.3)
            return {'error': resp.ack.error, 'param': resp.ack.param, 'state': resp.state}

        if test_id == 103:  # receive data msg
            e_test_id = 40
            size = kwargs.pop('size', 512)
            param = (size << 16) + e_test_id
            self._send_request(stm32msg.CMD_TEST, param=param, opt=opt)
            self._waiting_answer(timeout=timeout, msg_type='ack', state=stm32msg.S_WAITING)
            data, addr, btype, _ = self._receive_data()
            resp = self._waiting_answer(timeout=timeout, msg_type='ack', state=stm32msg.S_DONE)
            res = {
                'error': resp.ack.error,
                'param': resp.ack.param,
                'state': resp.state,
                'data': np.reshape(np.frombuffer(data, dtype=np.uint8), (1, int(len(data)))),
                'type': btype,
                'addr': addr,
                'size': len(data)
            }
            return res

        if test_id == 104:  # send data msg
            e_test_id = 50
            buffer = kwargs.pop('buffer', None)
            param = ((buffer.size * buffer.itemsize) << 16) + e_test_id
            self._send_request(stm32msg.CMD_TEST, param=param, opt=opt)
            self._waiting_answer(timeout=timeout, msg_type='ack', state=stm32msg.S_WAITING)
            resp = self._send_data(buffer, state=stm32msg.S_PROCESSING)
            org_hash = resp.ack.param
            data, addr, btype, _ = self._receive_data()
            resp = self._waiting_answer(timeout=timeout, msg_type='ack', state=stm32msg.S_DONE)
            res = {
                'error': resp.ack.error,
                'param': resp.ack.param,
                'state': resp.state,
                'data': data,
                'type': btype,
                'addr': addr,
                'hash': org_hash
            }
            return res

        if test_id == 200:  # receive aiTensorMsg
            e_test_id = 100
            conf = kwargs.pop('conf', 0)
            param = (conf << 16) + e_test_id
            self._send_request(stm32msg.CMD_TEST, param=param, opt=opt)
            self._waiting_answer(timeout=timeout, msg_type='ack', state=stm32msg.S_WAITING)
            resp = self._waiting_answer(msg_type='tensor', timeout=500, state=stm32msg.S_DONE)
            data, io_tensor, is_last = _decode_tensor_msg(resp, None, 'tag')
            resp = self._waiting_answer(timeout=timeout, msg_type='ack', state=stm32msg.S_DONE)
            res = {
                'error': resp.ack.error,
                'param': resp.ack.param,
                'state': resp.state,
                'data': data,
                'io_tensor': io_tensor,
                'is_last': is_last
            }
            return res

        return False
