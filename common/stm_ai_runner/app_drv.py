###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Base driver to manage the App (generated for the lite validation)
"""

from abc import abstractmethod
import ast
import os
import struct

import numpy as np


from .ai_runner import AiRunner, AiRunnerDriver, LEGACY_INFO_DICT_VERSION
from .stm_ai_utils import AiBufferFormat, IOTensor


class AppDriver(AiRunnerDriver):
    """Class to handle generic application"""

    def __init__(self, parent):
        self._app = None
        self._info = None
        self._sample_counter = 0
        super(AppDriver, self).__init__(parent)

    @abstractmethod
    def _run_application(self, _sample):
        """
        Run the wrapped application

        Parameters
        ----------
        _sample: int
            The sample index to be evaluated (0 for inspection)
        """

    @abstractmethod
    def _get_device_info(self):
        """  # noqa: DAR202
        Create the dictionary with device info

        Returns
        -------
        dict
            A dictionary with device info
        """

    @staticmethod
    def is_valid(file_path):
        """
        Check if the provided path is a valid path

        Parameters
        ----------
        file_path: str
            The path to be checked

        Returns
        -------
        bool
            True if the path is valid, false otherwise
        """
        if isinstance(file_path, str):
            return os.path.exists(file_path)
        return False, ''

    def connect(self, desc=None, **kwargs):
        """
        Connect to application

        Parameters
        ----------
        desc: str
            The application
        kwargs
            The other arguments
        """
        self._app = desc

    @property
    def is_connected(self):
        """Indicate if the application is set"""
        # noqa: DAR101,DAR201,DAR401
        return bool(self._app)

    def disconnect(self):
        """
        Do nothing
        """
        self._app = None

    def discover(self, flush=False):
        """  # noqa: DAR101
        Return the list of available networks based on filename

        Returns
        -------
        list
            The list of available networks
        """
        if self._app:
            filename = os.path.splitext(os.path.basename(self._app))[0]
            if filename.endswith('_main'):
                return [filename[:-5]]
        return []

    def _c_format_to_ai_buffer_format(self, c_format):
        """
        Given the string corresponding to an array format returns the AIBufferFmt

        Parameters
        ----------
        c_format: str
            The c format

        Returns
        -------
        AiBufferFormat
            The corresponding buffer format

        Raises
        ------
        AssertionError
            If the c format is not supported
        """
        if c_format == 'AI_ARRAY_FORMAT_FLOAT':
            return AiBufferFormat.to_fmt(np.float32, is_io=True)
        elif c_format == 'AI_ARRAY_FORMAT_S32':
            return AiBufferFormat.to_fmt(np.int32, is_io=True)
        elif c_format == 'AI_ARRAY_FORMAT_U32':
            return AiBufferFormat.to_fmt(np.uint32, is_io=True)
        elif c_format == 'AI_ARRAY_FORMAT_S16':
            return AiBufferFormat.to_fmt(np.int16, is_io=True)
        elif c_format == 'AI_ARRAY_FORMAT_U16':
            return AiBufferFormat.to_fmt(np.uint16, is_io=True)
        elif c_format == 'AI_ARRAY_FORMAT_S8':
            return AiBufferFormat.to_fmt(np.int8, is_io=True)
        elif c_format == 'AI_ARRAY_FORMAT_U8':
            return AiBufferFormat.to_fmt(np.uint8, is_io=True)
        elif c_format == 'AI_ARRAY_FORMAT_S1':
            return AiBufferFormat.to_fmt(np.int32, is_io=True, bits=1)
        elif c_format == 'AI_ARRAY_FORMAT_BOOL':
            return AiBufferFormat.to_fmt(np.bool_, is_io=True)
        raise AssertionError('Not expected c format {}'.format(c_format))

    @property
    def capabilities(self):
        """
        Return list with the capabilities

        Returns
        -------
        list
            List of capabilities
        """
        return [AiRunner.Caps.IO_ONLY]

    def get_info(self, _c_name=None):
        """
        Get c-network details

        Returns
        -------
        dict
            Empty dictionary

        Raises
        ------
        AssertionError
            If an unexpected key is found in the log
        """
        if self._info is None:
            output, _ = self._run_application(0)
            info = dict()
            info['runtime'] = dict()
            info['runtime']['capabilities'] = self.capabilities
            info['device'] = self._get_device_info()
            info['version'] = LEGACY_INFO_DICT_VERSION
            processing = False
            for line in output:
                self._logger.debug(line)
                if '__START_SELF_INSPECTION__' in line:
                    processing = True
                elif '__STOP_SELF_INSPECTION__' in line:
                    processing = False
                elif processing:
                    tokens = line.split(':')
                    if len(tokens) != 2:
                        raise AssertionError('Unexpected line in log: {}'.format(line))
                    key = tokens[0]
                    value = tokens[1]
                    if key == 'runtime_name':
                        info['runtime']['name'] = value
                    elif key == 'runtime_version':
                        info['runtime']['version'] = tuple(int(subvalue) for subvalue in value.split('.'))
                    elif key == 'runtime_tools_version':
                        info['runtime']['tools_version'] = tuple(int(subvalue) for subvalue in value.split('.'))
                    elif key == 'runtime_compiler':
                        info['runtime']['compiler'] = value
                    elif key == 'runtime_protocol':
                        info['runtime']['protocol'] = value
                    elif key == 'n_inputs':
                        info['inputs'] = [{} for i in range(int(value))]
                        for input_index in range(int(value)):
                            info['inputs'][input_index]['name'] = 'input_' + str(input_index + 1)
                    elif key == 'n_outputs':
                        info['outputs'] = [{} for i in range(int(value))]
                        for output_index in range(int(value)):
                            info['outputs'][output_index]['name'] = 'output_' + str(output_index + 1)
                    elif 'inputtensor' in key:
                        input_index = int(key.split('_')[1])
                        io_tensor_data = value.split('#')
                        if len(io_tensor_data) != 5:
                            raise AssertionError(str(io_tensor_data))
                        if io_tensor_data[3] != 'None' and io_tensor_data[4] != 'None':
                            quant = dict()
                            quant['scale'] = ast.literal_eval(io_tensor_data[3])[0]
                            quant['zero_point'] = ast.literal_eval(io_tensor_data[4])[0]
                        else:
                            quant = None
                        info['inputs'][input_index - 1]['io_tensor'] = IOTensor(
                            self._c_format_to_ai_buffer_format(io_tensor_data[1]), ast.literal_eval(io_tensor_data[0]),
                            quant
                        )
                    elif 'outputtensor' in key:
                        output_index = int(key.split('_')[1])
                        io_tensor_data = value.split('#')
                        if len(io_tensor_data) != 5:
                            raise AssertionError(str(io_tensor_data))
                        if io_tensor_data[3] != 'None' and io_tensor_data[4] != 'None':
                            quant = dict()
                            quant['scale'] = ast.literal_eval(io_tensor_data[3])[0]
                            quant['zero_point'] = ast.literal_eval(io_tensor_data[4])[0]
                        else:
                            quant = None
                        info['outputs'][output_index - 1]['io_tensor'] = IOTensor(
                            self._c_format_to_ai_buffer_format(io_tensor_data[1]), ast.literal_eval(io_tensor_data[0]),
                            quant
                        )
                    elif key in {'macc', 'weights', 'activations'}:
                        info[key] = int(value)
                    else:
                        info[key] = value
            self._info = info

        return self._info

    def invoke_sample(self, _s_inputs, **kwargs):
        """  # noqa: DAR101
        Invoke the c-network with a given input (sample mode)

        Returns
        -------
        outputs, elapsed_time
            The generated output and the elapsed time

        Raises
        ------
        AssertionError
            If any output buffer is not in a supported format
        """
        self._sample_counter = self._sample_counter + 1
        profiler = kwargs.pop('profiler')
        process_output, elapsed_time = self._run_application(self._sample_counter)
        profiler['debug']['exec_times'].append(elapsed_time)
        profiler['c_durations'].append(elapsed_time)
        outputs = []
        output_index = 0
        current_output = []
        ai_buffer_format = None
        unpack_format = None
        processing = False
        for line in process_output:
            self._logger.debug(line)
            if '__START_OUTPUT' in line:
                processing = True
                current_output = []
                ai_buffer_format = self._info['outputs'][output_index]['io_tensor'].raw_fmt
                if ai_buffer_format.is_float():
                    unpack_format = '!f'
                elif ai_buffer_format.is_integer():
                    unpack_format = '!i'
                # Case unsigned integer:
                elif ai_buffer_format.is_integer() and not ai_buffer_format.is_signed():
                    unpack_format = '!I'
                elif ai_buffer_format.is_packed() or ai_buffer_format.is_signed():
                    unpack_format = '!i'
                elif ai_buffer_format.is_bool():
                    unpack_format = '!?'
                else:
                    raise AssertionError('Unexpected buffer format: {}'
                                         .format(str(ai_buffer_format.to_dict())))
            elif '__END_OUTPUT' in line:
                processing = False
                data = np.array(current_output, dtype=ai_buffer_format.to_np_type())
                shape = self._info['outputs'][output_index]['io_tensor'].shape
                if ai_buffer_format.is_packed():
                    nb_32b_chans = int(np.ceil(shape[-1] / 32))
                    shape = shape[:-1] + (nb_32b_chans,)

                data = np.reshape(data, shape)
                outputs.append(data)
                output_index = output_index + 1
            elif processing:
                if ai_buffer_format.is_bool():
                    # Take the last 2 chars of each value in the line. They represent a byte expressed in hex
                    values = [v[-2:] for v in line.split()]
                else:
                    values = line.split()
                current_output.extend([struct.unpack(unpack_format, bytes.fromhex(value))[0] for value in values])
        return outputs, elapsed_time
