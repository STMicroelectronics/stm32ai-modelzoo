# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2019, 2022 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from datetime import datetime
from enum import Enum
import typing

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
    name: str = None
    model: str = None
    type: CliParameterType = None
    verbosity: CliParameterVerbosity = CliParameterVerbosity.NORMAL
    compression: CliParameterCompression = CliParameterCompression.LOSSLESS
    quantize: str = None
    custom: str = None
    allocateInputs: bool = True
    allocateOutputs: bool = True
    splitWeights: bool = False
    noOnnxOptimizer: bool = False
    noOnnxIoTranspose: bool = False
    prefetchCompressedWeights: bool = False
    target: str = None
    binary: bool = False
    dll: bool = False
    ihex: bool = False
    address: str = None
    copyWeightsAt: str = None
    relocatable: bool = False
    lib: str = None
    series: str = None
    noCFiles: bool = False
    batchSize: int = None
    mode: str = None
    desc: str = None
    valinput: str = None
    valoutput: str = None
    range: str = None
    full: bool = False
    saveCsv: bool = False
    classifier: bool = False
    noCheck: bool = False
    noExecModel: bool = False
    seed: str = None
    # workspace: str = None
    output: str = 'output'
    withReport: bool = False
    useCloud: bool = False
    optimization: CliParameterOptimization = CliParameterOptimization.BALANCED
    includeLibraryForSerie: CliLibrarySerie = None
    includeLibraryForIde: CliLibraryIde = CliLibraryIde.GCC
    fromModel: str = None


class AnalyzeResult(typing.NamedTuple):
    """
    Provide a simplified interface to access analyze results
    """
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

    def __str__(self) -> str:
        data = self._asdict()
        data.pop('report', None)  # Removing report from displayed output
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
        data.pop('graph', None) # Removing graph from displayed output
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
