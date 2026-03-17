###################################################################################
#   Copyright (c) 2022 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################
"""
Driver to run validation on MPU target hardware
"""
import subprocess
import re
import os
import numpy as np

from .ai_runner import AiRunner, AiRunnerDriver, HwIOError, STAI_INFO_DICT_VERSION
from .stm_ai_utils import AiBufferFormat, IOTensor


class MpuTargetDriver(AiRunnerDriver):
    """
    Class to handle MPU target
    """

    def __init__(self, parent):
        super(MpuTargetDriver, self).__init__(parent)
        self.info = None
        self.framework = None
        self.model = None
        self.model_name = None
        self.major = None
        self.micro = None
        self.minor = None
        self.cpu_exec = 0
        self.remote_user = "root"
        self.remote_host = "192.168.7.1"
        self.remote_path = "/usr/local"
        self._logger = parent.get_logger()

    def find_file(self, starting_directory, target_filename):
        # noqa: DAR101,DAR201,DAR401
        """Find a file in a directory"""
        for root, _, files in os.walk(starting_directory):
            if target_filename in files:
                return os.path.join(root, target_filename)
        return None

    def connect(self, desc=None, **kwargs):
        # noqa: DAR101,DAR201,DAR401
        """Connect to the stm.ai run-time"""
        # connect to the board and send NN model
        descriptor = desc.split(":", maxsplit=3)
        self.model = kwargs['context'].get_option('general.model')[0]
        if len(descriptor) > 0:
            self.remote_host = descriptor[0]
        if len(descriptor) > 1:
            if "cpu" in descriptor[1]:
                self.cpu_exec = 1
        if len(descriptor) > 2:
            self.model = descriptor[2]
        self.framework = self.model.split('.')[-1]
        self.model_name = self.model.split("/")[-1]

        # List all files and directories
        if "onnx" in self.framework:
            nbg_file = self.model_name.split('.onnx')[0] + ".nb"
        if "tflite" in self.framework:
            nbg_file = self.model_name.split('.tflite')[0] + ".nb"
        file = self.find_file(".", nbg_file)
        if file is not None:
            if self.cpu_exec == 1:
                self._logger.info(f"\nTarget inference running on CPU using {self.framework} model: {self.model}")
            else:
                self._logger.info(f"\nTarget inference running on NPU using NBG model: {file}")
                self.model = file
                self.framework = self.model.split('.')[-1]
                self.model_name = self.model.split("/")[-1]
        else:
            raise HwIOError("\nError: No NBG (.nb) file detected. To run the inference on NPU \
                            \nplease use \'generate\' command before using \'validate\' command")

        ssh_command = "None"
        if self.framework == "tflite":
            ssh_command = f"ssh {self.remote_user}@{self.remote_host} \"python3 -c \
                'import tflite_runtime as tf; print(tf.__version__)'\""

        elif self.framework == "onnx":
            ssh_command = f"ssh {self.remote_user}@{self.remote_host} \"python3 -c \
                'import onnxruntime; print(onnxruntime.__version__)'\""

        elif self.framework == "nb":
            ssh_command = f"ssh {self.remote_user}@{self.remote_host} 'ls -d \
                /usr/local/bin/nbg-benchmark-*/'"

        result = subprocess.run(ssh_command, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        if self.framework == "nb":
            version = re.findall(r'\d+', result.stdout.decode("utf-8"))
            version = str(version[0]) + '.' + str(version[1]) + '.' + str(version[2])
        else:
            version = result.stdout.decode("utf-8").rstrip()

        self.major = version.split(".")[0]
        self.micro = version.split(".")[1]
        self.minor = version.split(".")[2]

        scp_command = f"scp {self.model} {self.remote_user}@{self.remote_host}:{self.remote_path}"
        result = subprocess.run(scp_command, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if result.returncode == 0:
            return True
        else:
            self._logger.info('Could not connect to local ethernet devices.')
        return False

    @property
    def is_connected(self):
        """Indicate if the diver is connected"""
        # noqa: DAR101,DAR201,DAR401
        ssh_command = f"ssh {self.remote_user}@{self.remote_host} 'touch /tmp'"
        result = subprocess.run(ssh_command, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if result.returncode != 0:
            return False
        return True

    def disconnect(self):
        """Disconnect to the stm.ai run-time"""
        # noqa: DAR101,DAR201,DAR401
        self.info = None

    def discover(self, flush=False):
        # noqa: DAR101,DAR201,DAR401
        """Return list of available networks"""
        return ["network"]

    def get_clock(self):
        # noqa: DAR101,DAR201,DAR401
        """get ISPU clock frequency"""
        clock = 0
        if self.is_connected:
            ssh_command = f"ssh {self.remote_user}@{self.remote_host} cat /sys/kernel/debug/gc/clk"
            result = subprocess.run(ssh_command, shell=True, executable='/bin/bash',
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            clock = int(re.findall(r'\d+', result.stdout.decode("utf-8"))[-1])
            if result.returncode != 0:
                raise HwIOError('Cannot get clock')
        return clock

    def get_macc(self):
        # noqa: DAR101,DAR201,DAR401
        """get number of maccs"""
        return 0

    def get_tensor_info(self, req):
        # noqa: DAR101,DAR201,DAR401
        """get tensors info"""

        if self.is_connected:
            path = "/usr/local/" + self.model_name
            local_file_path = "runtime.py"
            remote_file_path = "/tmp/runtime.py"
            num_io = 0
            code = f"""\
from stai_mpu import stai_mpu_network
def get_tensor_info(req):
    # Initialization of network class
    name = []
    stai_mpu_model = stai_mpu_network(model_path=\"{path}\")
    # Iterate over all inputs
    if req == 0:
        num_io = stai_mpu_model.get_num_inputs()
        input_tensor_infos = stai_mpu_model.get_input_infos()
        tensors = [ dict() for i in range(num_io) ]
        for i in range(0, num_io):
            # Get input name
            name.append(str(\"input_\"+str(i)+\"_\"+input_tensor_infos[i].get_name()))
            quant = None
            type = input_tensor_infos[i].get_qtype()
            n_scale = input_tensor_infos[i].get_scale()
            n_zeropoint = input_tensor_infos[i].get_zero_point()
            shape = tuple(input_tensor_infos[i].get_shape())
            t_format = input_tensor_infos[i].get_dtype()
    # Iterate over all outputs
    if req == 1:
        num_io = stai_mpu_model.get_num_outputs()
        output_tensor_infos = stai_mpu_model.get_output_infos()
        tensors = [ dict() for i in range(num_io) ]
        for i in range(0, num_io):
            # Get output name
            name.append(str(\"output_\"+str(i)+\"_\"+output_tensor_infos[i].get_name()))
            type = output_tensor_infos[i].get_qtype()
            quant = None
            n_scale = output_tensor_infos[i].get_scale()
            n_zeropoint = output_tensor_infos[i].get_zero_point()
            shape = tuple(output_tensor_infos[i].get_shape())
            t_format = output_tensor_infos[i].get_dtype()
    return type, n_scale, n_zeropoint, shape, t_format, num_io, name
if __name__ == \"__main__\":
    type, n_scale, n_zeropoint, shape, t_format, num_io, name = get_tensor_info({req})
    print(" ||| ")
    print(type, n_scale, n_zeropoint, shape, t_format, num_io, name, sep=" | ")
    print(" ||| ")"""

        with open(local_file_path, "w") as file:
            file.write(code)

        scp_command = f'scp {local_file_path} {self.remote_user}@{self.remote_host}:{remote_file_path}'
        result = subprocess.run(scp_command, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if result.returncode != 0:
            raise HwIOError('Could not transfer runtime file.')

        ssh_command = f"ssh {self.remote_user}@{self.remote_host} 'python3 {remote_file_path} {req}'"
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, check=True)
        result_out = result.stdout.split(' ||| ')[1].replace("\n", "").split(" | ")
        quant = None
        if result.returncode == 0:
            n_scale = float(result_out[1])
            n_zeropoint = float(result_out[2])
            num_io = int(result_out[5])
            t_format = result_out[4]
            name = result_out[6]
            if "float" in t_format:
                t_format = 0x01821040
            elif "uint8" in t_format:
                t_format = 0x00040440
            else:
                t_format = 0x00840440
            shape = []
            elements = result_out[3].strip('()').split(',')
            for element in elements:
                shape.append(int(element))
            if n_scale >= 0 and n_zeropoint >= 0 and result_out[0] != "none":
                quant = dict()
                quant['scale'] = n_scale
                quant['zero_point'] = n_zeropoint
        else:
            raise HwIOError('Could not get info from target.')

        tensors = [{} for i in range(num_io)]
        for i in range(0, num_io):
            name_i = name.strip('[\'()\']').split(',')[i]
            # Iterate over all inputs
            if req == 0:
                tensors[i]['name'] = name_i
                tensors[i]['io_tensor'] = IOTensor(AiBufferFormat(t_format), tuple(shape), quant)

            # Iterate over all outputs
            if req == 1:
                tensors[i]['name'] = name_i
                tensors[i]['io_tensor'] = IOTensor(AiBufferFormat(t_format), tuple(shape), quant)

        return tensors

    def get_activations(self):
        # noqa: DAR101,DAR201,DAR401
        """get activation sizes"""
        activations = []
        return activations

    def get_weights(self):
        # noqa: DAR101,DAR201,DAR401
        """get weight sizes"""
        weights = []
        return weights

    def get_runtime_info(self):
        # noqa: DAR101,DAR201,DAR401
        """get runtime info"""
        runtime = dict()
        runtime['name'] = "ST.AI"

        if self.is_connected:
            ssh_command = f"ssh {self.remote_user}@{self.remote_host} x-linux-ai -v"
            result = subprocess.run(ssh_command, shell=True, executable='/bin/bash',
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if result.returncode == 0:
                version_x_linux = []
                version_fw = []
                version = result.stdout.decode("utf-8").strip()
                version = version.split('v')[-1].split('.')
                version_x_linux.append(int(version[0]))
                version_x_linux.append(int(version[1]))
                version_x_linux.append(int(version[2]))
                version_fw.append(int(self.major))
                version_fw.append(int(self.micro))
                version_fw.append(int(self.minor))
                runtime['version'] = tuple(version_x_linux)
                runtime['tools_version'] = tuple(version_fw)
                runtime['capabilities'] = self.capabilities
            else:
                raise HwIOError('Cannot get runtime versions')
        return runtime

    def get_info(self, c_name=None):
        # noqa: DAR101,DAR201,DAR401
        """Get c-network details (including runtime)"""

        if self.info is None:
            info = dict()
            info['runtime'] = dict()
            info['runtime']['name'] = 'STM.AI'
            info['device'] = dict()
            info['device']['desc'] = 'MP2 VSI NPU'
            info['device']['dev_type'] = 'npu'
            info['device']['sys_clock'] = self.get_clock()
            info['macc'] = self.get_macc()
            info['version'] = STAI_INFO_DICT_VERSION
            info['inputs'] = self.get_tensor_info(0)
            info['outputs'] = self.get_tensor_info(1)
            info['activations'] = self.get_activations()
            info['weights'] = self.get_weights()
            info['name'] = self.discover()[0]
            info['runtime'] = self.get_runtime_info()
            info['n_nodes'] = None

            self.info = info

        return self.info

    def invoke_sample(self, s_inputs, **kwargs):
        # noqa: DAR101,DAR201,DAR401
        """Invoke the c-network with a given input (sample mode)"""

        for data_in in s_inputs:
            np.save("./npy_data.npy", data_in)
            path = "/usr/local/" + self.model_name
            inf_time = 0
            outputs = []
            n_outputs = len(self.info['outputs'])
            local_file_path = "invoke.py"
            remote_file_dir = "/tmp/"
            remote_file_path = "/tmp/invoke.py"
            code = f"""\
from stai_mpu import stai_mpu_network
import numpy as np
from timeit import default_timer as timer
# def invoke():
# Initialization of network class
stai_mpu_model = stai_mpu_network(model_path=\"{path}\")
num_out = stai_mpu_model.get_num_outputs()
num_in = stai_mpu_model.get_num_inputs()
input_tensor_infos = stai_mpu_model.get_input_infos()
input_data = np.load("/tmp/npy_data.npy")
for i in range(num_in):
    if input_tensor_infos[i].get_dtype() == np.float32:
        input_data = (np.float32(input_data))
stai_mpu_model.set_input(i, input_data)
start_time = timer()
stai_mpu_model.run()
stop_time = timer()
nn_inference_time = stop_time - start_time
output_data = []
for i in range(num_out):
    output = stai_mpu_model.get_output(index=i)
    np.save("/tmp/npy_out"+str(i)+".npy",output)
print(" ||| ")
print(nn_inference_time, sep = " | ")
print(" ||| ")"""

        with open(local_file_path, "w") as file:
            file.write(code)

        scp_command = f'scp {local_file_path} npy_data.npy {self.remote_user}@{self.remote_host}:{remote_file_dir}'
        result = subprocess.run(scp_command, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        ssh_command = f"ssh {self.remote_user}@{self.remote_host} 'python3 {remote_file_path}'"

        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, check=True)
        result_out = result.stdout.split(" ||| ")[-2].replace("\n", "").split(" | ")
        if result.returncode == 0:
            inf_time = float(result_out[0]) * 1000
            for i in range(n_outputs):
                scp_command = f'scp {self.remote_user}@{self.remote_host}:/tmp/npy_out{str(i)}.npy ./npy_out{i}.npy'
                result = subprocess.run(scp_command, shell=True, executable='/bin/bash',
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                if result.returncode == 0:
                    outputs.append(np.load(f"./npy_out{i}.npy"))
                else:
                    raise HwIOError('Could not transfer runtime file.')
        else:
            raise HwIOError('Could not transfer runtime file.')

        profiler = kwargs.pop('profiler')
        profiler['debug']['exec_times'].append(inf_time)
        profiler['c_durations'].append(inf_time)
        self.clean()
        return outputs, inf_time

    def clean(self):
        """ Clean the generated files after testing """
        ssh_command = f"ssh {self.remote_user}@{self.remote_host} \
            'rm -rf /tmp/*.py /tmp/*.tflite /tmp/*.nb /tmp/*.onnx /tmp/*.npy'"
        local_file_command = "rm -rf invoke.py runtime.py npy_data*.npy npy_out*.npy"

        # Run the clean command
        result = subprocess.run(ssh_command, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        res = os.system(local_file_command)
        # Check the exit code
        if res != 0 or result.returncode != 0:
            self._logger.debug('Error while cleaning.')

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

    def short_desc(self):
        """
        Return human readable description

        Returns
        -------
        str
            Human readable description
        """
        """Report a human description of the connection state"""  # noqa: DAR101,DAR201,DAR401
        desc = 'ETHERNET:' + str(self.remote_host) + ':' + str(self.model)
        desc += ':connected' if self.is_connected else ':not connected'
        return desc
