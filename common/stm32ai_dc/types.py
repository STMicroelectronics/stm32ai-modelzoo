# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from datetime import datetime
from enum import Enum
import typing
from typing import Optional

LOGGER_NAME = "STM32AI_API"


class CliParameterType(str, Enum):
    """
    Define the types that can be used to indicate the type of the model
    """
    KERAS = "keras"
    TFLITE = "tflite"
    ONNX = "onnx"


class CliParameterCompression(str, Enum):
    """
    Define the compression values that can be used to compress a model
    """
    NONE = "none"
    LOSSLESS = "lossless"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CliParameterVerbosity(int, Enum):
    """
    Define the log verbosity of the command
    """
    NONE = 0
    NORMAL = 1
    HIGH = 2


class CliParameterOptimization(str, Enum):
    """
    Define the optimization to be used with the CLI
    """
    BALANCED = "balanced"
    TIME = "time"
    RAM = "ram"


class CliLibrarySerie(str, Enum):
    STM32H7 = "STM32H7"
    STM32F7 = "STM32F7"
    STM32F4 = "STM32F4"
    STM32L4 = "STM32L4"
    STM32G4 = "STM32G4"
    STM32F3 = "STM32F3"
    STM32U5 = "STM32U5"
    STM32L5 = "STM32L5"
    STM32F0 = "STM32F0"
    STM32L0 = "STM32L0"
    STM32G0 = "STM32G0"
    STM32C0 = "STM32C0"
    STM32WL = "STM32WL"
    STM32MP1 = "STM32MP1"


class CliLibraryIde(str, Enum):
    GCC = "gcc"
    IAR = "iar"
    KEIL = "keil"


class CliParameters(typing.NamedTuple):
    """
        Define the parameters that can be sent to the underlying command line call
    """
    # --------------------------------------------------------------------------------------
    #
    # Common Arguments
    # --------------------------------------------------------------------------------------
    model: str
    """ Required: model file """

    verbosity: CliParameterVerbosity = CliParameterVerbosity.NORMAL
    """  Optional: Command verbosity. Defaults to NORMAL """

    type: Optional[CliParameterType] = None
    """ Optional: Force model type detection when running command. Defaults to None """

    name: Optional[str] = None
    """ Optional: Name which will be used when generating C Code. Defaults to "network """

    compression: CliParameterCompression = CliParameterCompression.LOSSLESS
    """ Optional: Compression level. Defaults to "lossless" """

    allocateInputs: bool = True
    """ When set to true, activations buffer will be also used to handle the input buffers. Defaults to True """

    allocateOutputs: bool = True
    """ Optional: When set to true, activations buffer will be also used to handle the output buffers. Defaults to True """

    series: str = 'stm32f4'
    """ Optional: Defines a serie which will be used to calculate more accurate memory footprint. Defaults to "stm32f4" """

    splitWeights: Optional[bool] = False
    """ Optional:  generate a C-data file with a C-table by layer (not supported with the optional '--binary' option) """

    optimization: CliParameterOptimization = CliParameterOptimization.BALANCED
    """ 
        define global optimization objectives 
        - time: optimize the inference time, 
        - ram: minimize the size  of the requested ram, 
        - balanced: default, trade-off between the inference time and ram size
    """

    noOnnxOptimizer: Optional[bool] = None
    """ Optional: disable the ONNX optimizer pass """

    noOnnxIoTranspose: Optional[bool] = None
    """ Optional: disable the adding of the IO transpose layer if ONNX model is channel first """

    prefetchCompressedWeights: Optional[bool] = None
    """ Optional enable the prefetch of the compressed x4,x8 weights (extra space will be reserved in activations buffer) """
    # --------------------------------------------------------------------------------------
    #
    # Generate Arguments only
    # --------------------------------------------------------------------------------------
    binary: Optional[bool] = None
    """ Optional: generate model weights as a binary file """

    dll: Optional[bool] = None
    """ Optional:  generate the X86 library """

    ihex: Optional[bool] = None
    """ Optional: generate Intel hexadecimal object file format for relocatable model """

    address: Optional[str] = None
    """ Optional: address of the weight array (can be external memory) """

    copyWeightsAt: Optional[str] = None
    """ Optional: Include code to copy weights to specified address """

    relocatable: Optional[bool] = None
    """ Optional:  generate model as a relocatable binary file """

    noCFiles: Optional[bool] = False
    """ Optional: only the relocatable binary file is generated """
    # --------------------------------------------------------------------------------------
    #
    # Validate Arguments only
    # --------------------------------------------------------------------------------------
    batchSize: Optional[int] = None
    """ Optional: number of samples for the validation. Defaults to 10 """

    valinput: Optional[str] = None
    """ Optional: file to use as input for validation """

    valoutput: Optional[str] = None
    """ Optional: files to use as output for validation """

    range: Optional[list] = None
    """ Optional: requested range to generate randomly the input data (default=[0,1]) """

    full: Optional[bool] = None
    """ Optional: enable a full validation process """

    saveCsv: Optional[bool] = None
    """ Optional: force the storage of all io data in csv files """

    classifier: Optional[bool] = None
    """ Optional: force ACC metric computation (default: auto-detection) """

    noCheck: Optional[bool] = None
    """ Optional: disable internal checks (mode/model type dependent) """

    noExecModel: Optional[bool] = None
    """ Optional: Disable execution of the original model """

    seed: Optional[int] = None
    """ Optional: random seed used to initialize the pseudo-randomnumber generator [0, 2**32 - 1] """

    output: str = 'output'
    """ Optional: Output folder """
    # --------------------------------------------------------------------------------------
    #
    # Superset Arguments
    # --------------------------------------------------------------------------------------
    useCloud: bool = False
    """ Optional: Use Developer Cloud """

    includeLibraryForSerie: Optional[CliLibrarySerie] = None
    """ Optional: Include specific library for a given serie """

    includeLibraryForIde: CliLibraryIde = CliLibraryIde.GCC
    """ Optional: Include library for a given toolchain. Defaults to GCC """

    fromModel: Optional[str] = None
    """ 
        Optional: Defines, for statistics purpose, a model origin. 
        
        Should apply when model used is from STM32 Model Zoo
    """


class AnalyzeResult(typing.NamedTuple):
    """
    Provide a simplified interface to access analyze results
    """
    activations_size: int
    weights: int
    macc: int
    rom_size: int
    total_ram_io_size: int
    ram_size: int
    rom_compression_factor: float
    report_version: float
    date_time: str
    cli_version_str: str
    cli_parameters: str
    report: dict    # Complete output report
    graph: dict     # Graph report
    estimated_library_flash_size: int
    estimated_library_ram_size: int

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)  # Removing graph from displayed output
        return f"AnalyzeResult({data})"


class GenerateResult(typing.NamedTuple):
    server_url: str
    zipfile_path: str
    output_path: str
    graph: dict
    report: dict

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)  # Removing graph from displayed output
        return f"GenerateResult({data})"


class ValidateResultMetrics(typing.NamedTuple):
    """
    Provide a simplified interface to access validation metrics
    """
    accuracy: str
    description: str
    l2r: float
    mae: float
    mean: float
    rmse: float
    std: float
    ts_name: str


class ValidateResult(typing.NamedTuple):
    """
    Provide a simplified interface to access validation results and metrics
    """
    # AnalyzeResult
    macc: int
    rom_size: int
    total_ram_io_size: int
    ram_size: int
    rom_compression_factor: float
    report_version: float
    date_time: str
    cli_version_str: str
    cli_parameters: str
    report: dict  # Complete output report

    estimated_library_flash_size: int
    estimated_library_ram_size: int
    graph: dict  # Complete graph

    validation_metrics: typing.List[ValidateResultMetrics]
    validation_error: float
    validation_error_description: str

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)  # Removing report from displayed output
        return f"ValidateResult({data})"


class BenchmarkResult(typing.NamedTuple):
    # AnalyzeResult
    macc: int
    rom_size: int
    total_ram_io_size: int
    ram_size: int
    rom_compression_factor: float
    report_version: float
    date_time: str
    cli_version_str: str
    cli_parameters: str
    report: dict  # Complete output report

    # ValidationResult
    validation_metrics: typing.List[ValidateResultMetrics]
    validation_error: float
    validation_error_description: str

    # BenchmarkResult
    graph: dict
    cycles: int
    duration_ms: int
    device: str
    cycles_by_macc: int

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
        data.pop('graph', None)
        return f"BenchmarkResult({data})"


class BoardData(typing.NamedTuple):
    """ Provide interface to get data about a board"""
    name: str
    boardCount: int
    flashSize: str
    deviceCpu: str
    deviceId: str


class Stm32AiBackend:
    """"
    Interface used to define backend commands
    It throws an error if the command is not supported by the backend
    """
    # Standard commdands

    def analyze(self, options: CliParameters) -> AnalyzeResult:
        raise NotImplementedError("Analyze not implemented on this backend")

    def generate(self, options: CliParameters) -> GenerateResult:
        raise NotImplementedError("Generate not implemented on this backend")

    def validate(self, options: CliParameters) -> ValidateResult:
        raise NotImplementedError("Validate not implemented on this backend")

    def quantize(self, options: CliParameters):
        raise NotImplementedError("Quantize not implemented on this backend")

    # Cloud enabled commands
    def benchmark(self, options: CliParameters, board_name: str):
        raise NotImplementedError("Benchmark not implemented on this backend")

    def get_benchmark_boards(self) -> typing.List[BoardData]:
        raise NotImplementedError("Get benchmark boards not implemented on \
            this backend")

    def get_user(self):
        raise NotImplementedError("get_user not implemented on \
            this backend")

    def list_models(self):
        raise NotImplementedError("list_models not implemented on this\
             backend")

    def list_validation_input_files(self):
        raise NotImplementedError("list_validation_input_files not implemented\
             on this backend")

    def list_validation_output_files(self):
        raise NotImplementedError("list_validation_output_files not \
            implemented on this backend")

    def list_generated_files(self):
        raise NotImplementedError("list_generated_files not implemented on \
            this backend")

    def upload_model(self, modelPath: str):
        raise NotImplementedError("upload_model not implemented on this\
             backend")

    def upload_validation_input_file(self, filePath: str):
        raise NotImplementedError("upload_validation_input_file not \
            implemented on this backend")

    def upload_validation_output_file(self, filePath: str):
        raise NotImplementedError("upload_validation_output_file not\
             implemented on this backend")

    def download_model(self, modelPath):
        raise NotImplementedError("download_model not implemented on this\
             backend")

    def download_validation_input_file(self, filePath):
        raise NotImplementedError("download_validation_input_file not \
            implemented on this backend")

    def download_validation_output_file(self, filePath):
        raise NotImplementedError("download_validation_output_file not \
            implemented on this backend")

    def download_generated_file(self, filePath):
        raise NotImplementedError("download_generated_file not \
            implemented on this backend")

    def delete_model(self, modelName: str):
        raise NotImplementedError("delete_model not implemented on this \
            backend")

    def delete_validation_input_file(self, fileName: str):
        raise NotImplementedError("delete_validation_input_file not \
            implemented on this backend")

    def delete_validation_output_file(self, fileName: str):
        raise NotImplementedError("delete_validation_output_file not \
            implemented on this backend")

    def delete_generated_file(self, fileName: str):
        raise NotImplementedError("delete_generated_file not implemented on \
            this backend")
