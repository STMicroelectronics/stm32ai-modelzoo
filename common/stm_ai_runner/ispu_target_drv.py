###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Driver to run validation on ISPU target hardware
"""
import serial
import serial.tools.list_ports
import numpy as np
import numpy.ma as ma
import math
import ctypes
import struct
import json

from .ai_runner import AiRunner, AiRunnerDriver, STAI_INFO_DICT_VERSION
from .ai_runner import HwIOError, InvalidMsgError, NotInitializedMsgError, AiRunnerError
from .ai_runner import InvalidParamError, InvalidModelError
from .stm_ai_utils import AiBufferFormat, IOTensor, stm_ai_node_type_to_str

ispu_timeout_error = 0x00000001
ispu_stack_error = 0x00000002
ispu_ucf_version_error = 0x00000004


__version__ = "1.0"


class IspuTargetDriver(AiRunnerDriver):
    """
    Class to handle ispu target
    """

    def __init__(self, parent):
        super(IspuTargetDriver, self).__init__(parent)

        self.ser = None
        self.block_size = 2
        self.ucf = ''
        self.info = None
        self.n_nodes = 0

    def _send_bytes(self, data_a, block_s):
        num_blocks = math.ceil(len(data_a) / block_s)
        block = 0
        while block < num_blocks:
            block_start = block * block_s
            if (block == num_blocks - 1):
                block_stop = len(data_a)
            else:
                block_stop = (block + 1) * block_s
            self.ser.write(data_a[block_start:block_stop:1])
            out = self.ser.readline().decode('utf-8')
            block = block + 1

    def _load_ucf(self, ucf):
        ucf_bytes = bytearray()

        try:
            fp = open(ucf, 'r')
        except OSError:
            msg = "Cannot open file " + ucf
            raise AiRunnerError(msg)

        if ucf.endswith(".ucf"):
            line = fp.readline()
            while line:
                if line[0] == 'A' and line[1] == 'c':
                    tmp = line.strip().split()
                    ucf_bytes.append(int(tmp[1], 16))
                    ucf_bytes.append(int(tmp[2], 16))
                elif line.startswith('WAIT'):
                    tmp = line.strip().split()
                    ucf_bytes.append(0xFF)
                    ucf_bytes.append(int(tmp[1], 10))
                line = fp.readline()
        elif ucf.endswith(".json"):
            json_data = json.load(fp)

            supported_reg_config = False
            json_format = json_data.get("json_format")

            if json_format is not None:
                format_type = json_format.get("type")
                format_ver = json_format.get("version")

                if format_type == "reg_config" and format_ver.startswith("2."):
                    supported_reg_config = True

            if not supported_reg_config:
                raise AiRunnerError(f"File " + ucf + " is not a supported JSON format.")

            for i in range(0, len(json_data['sensors'])):
                for j in range(0, len(json_data['sensors'][i]['configuration'])):
                    op = json_data['sensors'][i]['configuration'][j]
                    if 'type' in op and op['type'] == 'write':
                        addr = op['address'].replace('0x', '');
                        value = op['data'].replace('0x', '');
                        ucf_bytes.append(int(addr, 16))
                        ucf_bytes.append(int(value, 16))
                    elif 'type' in op and op['type'] == 'delay':
                        value = op['data'];
                        ucf_bytes.append(0xFF)
                        ucf_bytes.append(int(value, 10))
        else:
            raise AiRunnerError("File " + ucf + " has an unsupported extension")
        fp.close()

        cmd = '*ucf' + str(len(ucf_bytes)) + '\n'
        self.ser.write(bytearray(cmd, encoding='utf-8'))
        out = self.ser.readline().decode('utf-8')

        self._send_bytes(ucf_bytes, self.block_size)

        boot = int(self.ser.readline().decode('utf-8'), 0)
        if boot != 0:
            msg = ""
            if boot & ispu_timeout_error:
                msg += "Timeout during the ISPU boot. "
            if boot & ispu_stack_error:
                msg += "Detected stack overflow on the ISPU. The model might be using too much data RAM. "
            if boot & ispu_ucf_version_error:
                ver = self.ser.readline().decode('utf-8').strip()
                expected_ver = self.ser.readline().decode('utf-8').strip()
                if ver == '0.0.0':
                    msg += "The ISPU configuration file was built with an old version of the ISPU template"
                else:
                    msg += "The ISPU configuration file was built with version " + ver + " of the ISPU template"
                msg += ", but a template with version " + expected_ver + ".x is required."

            raise AiRunnerError(msg)

    def connect(self, desc=None, **kwargs):
        """Connect to the stm.ai run-time"""
        # noqa: DAR101,DAR201,DAR401

        port, rate, ucf = desc.split(":", maxsplit=2)

        ports = []
        if port == '':
            port_specified = 0
            available_ports = serial.tools.list_ports.comports()
            for p in sorted(available_ports):
                if p.vid == 1155:  # give priority if can confirm it is STMicroelectronics
                    ports.insert(0, p.device)
                else:
                    ports.append(p.device)
        else:
            port_specified = 1
            ports.append(port)

        bad_fw_version = 0
        fw_version = '0.0.0'

        for port in ports:
            try:
                ser = serial.Serial(
                    port=port,
                    baudrate=rate,
                    timeout=1,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                )

                ser.write(b'*ver\n')
                out = ser.readline().decode('utf-8')
                ser.close()

                if out.startswith('ISPU validation firmware'):
                    self.ser = serial.Serial(
                        port=port,
                        baudrate=rate,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS
                    )

                    version  = out.split()[3]
                    ver_split = version.split('.')

                    if ver_split[0] != '1' or ver_split[1] != '1':
                        bad_fw_version = 1
                        ser.close()
                        continue

                    self.ser.write(b'*blocksize\n')
                    out = self.ser.readline().decode('utf-8')
                    self.block_size = int(out)

                    self._load_ucf(ucf)
                    self.ucf = ucf

                    return True
            except AiRunnerError:
                raise
            except serial.SerialException as e:
                if isinstance(e, serial.SerialException) and e.errno == 13:
                    raise HwIOError('Could not connect to serial devices due to missing permissions.')
                else:
                    pass
            except Exception:
                pass

        if bad_fw_version:
            raise HwIOError('Detected ISPU validation firmware version ' + version + '. Please flash a firmware with version 1.1.x.')
        if port_specified:
            raise HwIOError('No serial device with ISPU validation firmware found on port ' + port + '.')
        else:
            raise HwIOError('No serial device with ISPU validation firmware found.')

        return False

    @property
    def is_connected(self):
        """Indicate if the diver is connected"""
        # noqa: DAR101,DAR201,DAR401
        return self.ser is not None

    def disconnect(self):
        """Disconnect to the stm.ai run-time"""
        # noqa: DAR101,DAR201,DAR401

        self.ser.close()
        self.ser = None
        self.block_size = 2
        self.ucf = ''
        self.info = None

    def discover(self, flush=False):
        """Return list of available networks"""
        # noqa: DAR101,DAR201,DAR401

        if self.is_connected:
            self.ser.write(b'*name\n')
            out = self.ser.readline().decode('utf-8')
            return [ out.strip() ]
        return []

    def get_clock(self):
        """get ISPU clock frequency"""
        # noqa: DAR101,DAR201,DAR401

        if self.is_connected:
            self.ser.write(b'*clock\n')
            out = self.ser.readline().decode('utf-8')
            return int(out.strip())
        return 0

    def get_macc(self):
        """get number of maccs"""
        # noqa: DAR101,DAR201,DAR401

        if self.is_connected:
            self.ser.write(b'*macc\n')
            out = self.ser.readline().decode('utf-8')
            return int(out.strip())
        return 0

    def get_activations(self):
        """get activation sizes"""
        # noqa: DAR101,DAR201,DAR401

        activations = []

        if self.is_connected:
            self.ser.write(b'*activation_sizes\n')

            out = self.ser.readline().decode('utf-8')
            num = int(out.strip())

            for i in range(num):
                out = self.ser.readline().decode('utf-8')
                activations.append(int(out.strip()))

        return activations

    def get_weights(self):
        """get weight sizes"""
        # noqa: DAR101,DAR201,DAR401

        weights = []

        if self.is_connected:
            self.ser.write(b'*weight_sizes\n')

            out = self.ser.readline().decode('utf-8')
            num = int(out.strip())

            for i in range(num):
                out = self.ser.readline().decode('utf-8')
                weights.append(int(out.strip()))

        return weights

    def get_runtime_info(self):
        """get runtime info"""
        # noqa: DAR101,DAR201,DAR401

        runtime = dict()
        runtime['name'] = "ST.AI"

        if self.is_connected:
            self.ser.write(b'*get_versions\n')

            version = []
            for i in range(3):
                out = self.ser.readline().decode('utf-8')
                version.append(int(out.strip()))
            runtime['version'] = tuple(version)

            version = []
            for i in range(3):
                out = self.ser.readline().decode('utf-8')
                version.append(int(out.strip()))
            runtime['tools_version'] = tuple(version)

        return runtime

    def get_tensor_info(self, fallback_prefix='tensor_'):
        """get tensors info"""
        # noqa: DAR101,DAR201,DAR401

        if self.is_connected:
            out = self.ser.readline().decode('utf-8')
            num = int(out.strip())

            tensors = []
            for i in range(num):
                out = self.ser.readline().decode('utf-8')
                t_format = int(out.strip(), 0)

                out = self.ser.readline().decode('utf-8')
                n_shape = int(out.strip())
                shape_list = []
                for j in range(n_shape):
                    out = self.ser.readline().decode('utf-8')
                    shape_list.append(int(out.strip()))
                shape = tuple(shape_list)

                out = self.ser.readline().decode('utf-8')
                n_scale = int(out.strip())
                scale = 1.0
                for j in range(n_scale):
                    out = self.ser.read(4)
                    scale = struct.unpack('f', bytearray(out))[0]

                out = self.ser.readline().decode('utf-8')
                n_zeropoint = int(out.strip())
                zeropoint = 0
                for j in range(n_zeropoint):
                    out = self.ser.readline().decode('utf-8')
                    zeropoint = int(out.strip())

                out = self.ser.readline().decode('utf-8')
                len_name = int(out.strip())
                name = fallback_prefix + str(i + 1)
                if len_name > 0:
                    name = self.ser.readline().decode('utf-8')

                quant = None
                if n_scale > 0 and n_zeropoint > 0:
                    quant = dict()
                    quant['scale'] = scale
                    quant['zero_point'] = zeropoint

                tensor = IOTensor(AiBufferFormat(t_format), shape, quant)
                tensor.set_name(name)

                tensors.append(tensor)

            return tensors

        return []

    def get_io_info(self, req):
        """get input or output tensors info"""
        # noqa: DAR101,DAR201,DAR401

        all_info = []

        if req == 0:
            self.ser.write(b'*get_in_info\n')
            fallback_prefix = 'input_'
        else:
            self.ser.write(b'*get_out_info\n')
            fallback_prefix = 'output_'

        tensors = self.get_tensor_info(fallback_prefix)
        for i in range(len(tensors)):
            info = dict()
            info['io_tensor'] = tensors[i]
            info['name'] = tensors[i].name
            all_info.append(info)

        return all_info

    def get_info(self, c_name=None):
        """Get c-network details (including runtime)"""
        # noqa: DAR101,DAR201,DAR401

        if self.info is None:
            info = dict()
            info['runtime'] = dict()
            info['runtime']['name'] = 'STM.AI'
            info['device'] = dict()
            info['device']['desc'] = 'ISPU hardware'
            info['device']['dev_type'] = 'ispu'
            info['device']['sys_clock'] = self.get_clock()
            info['macc'] = self.get_macc()
            info['version'] = STAI_INFO_DICT_VERSION
            info['inputs'] = self.get_io_info(0)
            info['outputs'] = self.get_io_info(1)
            info['activations'] = self.get_activations()
            info['weights'] = self.get_weights()
            info['name'] = self.discover()[0]
            info['runtime'] = self.get_runtime_info()
            info['runtime']['capabilities'] = self.capabilities
            info['runtime']['protocol'] = f'ISPU driver {__version__}'
            self.info = info

        return self.info

    def get_nodes_info(self):
        """get nodes info"""
        # noqa: DAR101,DAR201,DAR401

        c_nodes = []

        if self.is_connected:
            self.ser.write(b'*get_nodes\n')

            out = self.ser.readline().decode('utf-8')
            self.n_nodes = int(out.strip())

            for i in range(0, self.n_nodes):
                node = dict()

                node['name'] = f'ai_node_{i}'
                node['c_durations'] = [ ]
                node['io_tensors'] = []
                node['data'] = []

                out = self.ser.readline().decode('utf-8')
                node['m_id'] = int(out.strip())

                out = self.ser.readline().decode('utf-8')
                node['layer_desc'] = stm_ai_node_type_to_str(int(out.strip()))
                node['layer_type'] = int(out.strip())

                node['io_tensors'] = []
                node['shape'] = []
                node['type'] = []
                node['scale'] = []
                node['zero_point'] = []

                for i in range(2): # get both input and output tensors
                    tensors = self.get_tensor_info()
                    for tensor in tensors:
                        node['io_tensors'].append(tensor)
                        node['shape'].append(tensor.shape)
                        node['type'].append(tensor.dtype)
                        scale = 1
                        if 'scale' in tensor.quant_params:
                            scale = tensor.quant_params['scale']
                        node['scale'].append(scale)
                        zero_point = 0
                        if 'zero_point' in tensor.quant_params:
                            zero_point = tensor.quant_params['zero_point']
                        node['zero_point'].append(zero_point)

                c_nodes.append(node)

        return c_nodes

    def invoke_sample(self, s_inputs, **kwargs):
        """Invoke the c-network with a given input (sample mode)"""
        # noqa: DAR101,DAR201,DAR401

        mode = kwargs.pop('mode', AiRunner.Mode.IO_ONLY)
        profiler = kwargs.pop('profiler')

        if mode & AiRunner.Mode.PER_LAYER:
            if not profiler['c_nodes']:
                profiler['c_nodes'] = self.get_nodes_info()
        elif self.n_nodes == 0:
            self.get_nodes_info()

        in_i = 0
        for data_in in s_inputs:
            in_bytes = bytearray(data_in[0].flatten())

            cmd = '*in' + str(in_i) + ' ' + str(len(in_bytes)) + '\n'
            self.ser.write(bytearray(cmd, encoding='utf-8'))
            out = self.ser.readline()

            self._send_bytes(in_bytes, self.block_size)

            in_i = in_i + 1

        self.ser.write(b'*run\n')
        out = self.ser.readline().decode('utf-8')

        for i in range(0, self.n_nodes):
            out = self.ser.readline().decode('utf-8')
            rec = out.split()
            if rec[0] == 'ret':
                run = int(rec[1], 0)
                msg = ""
                if run & ispu_timeout_error:
                    msg += "Timeout during the ISPU inference execution. "
                if run & ispu_stack_error:
                    msg += "Detected stack overflow on the ISPU. The model might be using too much data RAM. "
                if run == 0:
                    msg += "Inference unexpectedly completed before all layers."
                raise AiRunnerError(msg)

            layer_time = int(rec[0].strip()) / 1000
            if mode & AiRunner.Mode.PER_LAYER:
                profiler['c_nodes'][i]['c_durations'].append(layer_time)

        out = self.ser.readline().decode('utf-8')
        rec = out.split()
        run = int(rec[1], 0)
        if run != 0:
            msg = ""
            if run & ispu_timeout_error:
                msg = msg + "Timeout during the ISPU inference execution. "
            if run & ispu_stack_error:
                msg = msg + "Detected stack overflow on the ISPU. The model might be using too much data RAM. "
            raise AiRunnerError(msg)

        out = self.ser.readline().decode('utf-8')
        exec_time = int(out.strip())
        exec_time = exec_time / 1000

        profiler['debug']['exec_times'].append(exec_time)
        profiler['c_durations'].append(exec_time)
        outputs = []

        n_outputs = len(self.info['outputs'])

        for out_i in range(n_outputs):
            shape = self.info['outputs'][out_i]['io_tensor'].shape
            np_format = self.info['outputs'][out_i]['io_tensor'].dtype
            n_bytes = int(self.info['outputs'][out_i]['io_tensor'].get_c_size_in_bytes())

            out = self.ser.read(n_bytes)
            values = np.frombuffer(bytearray(out), np_format, count=-1)

            outputs.append(np.reshape(values, shape))

        return outputs, exec_time

    @property
    def capabilities(self):
        """
        Return list with the capabilities

        Returns
        -------
        list
            List of capabilities
        """
        return [AiRunner.Caps.IO_ONLY, AiRunner.Caps.PER_LAYER]

    def short_desc(self):
        """
        Return human readable description

        Returns
        -------
        str
            Human readable description
        """
        return 'ISPU on target run of ' + self.ucf

