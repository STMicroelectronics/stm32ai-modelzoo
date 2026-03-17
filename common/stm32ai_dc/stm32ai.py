# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


"""
Main API entrypoint file.
stm32ai wrap a web based backend into a high-level transparent API for the user.
"""

import typing
from .types import AnalyzeResult, BenchmarkResult, BoardData, CliParameters, GenerateResult, MpuBenchmarkResult, Stm32AiBackend, ValidateResult


class Stm32Ai(Stm32AiBackend):
    def __init__(self, backend: Stm32AiBackend) -> None:
        self.backend = backend

    def analyze(self, options: CliParameters) -> AnalyzeResult:
        return self.backend.analyze(options)

    def generate(self, options: CliParameters) -> GenerateResult:
        return self.backend.generate(options)

    def validate(self, options: CliParameters) -> ValidateResult:
        return self.backend.validate(options)

    def quantize(self, options: CliParameters):
        return self.backend.quantize(options)
    
    def benchmark(self, options: CliParameters, board_name: str, timeout = 600) -> typing.Union[MpuBenchmarkResult, BenchmarkResult]:
        return self.backend.benchmark(options, board_name, timeout)
    
    def generate_nbg(self, model_name, timeout = 300):
        return self.backend.generate_nbg(model_name, timeout)

    def get_benchmark_boards(self) -> typing.List[BoardData]:
        return self.backend.get_benchmark_boards()

    def get_user(self):
        return self.backend.get_user()

    def list_models(self):
        return self.backend.list_models()

    def list_validation_input_files(self):
        return self.backend.list_validation_input_files()

    def list_validation_output_files(self):
        return self.backend.list_validation_output_files()
    
    def list_generated_files(self):
        return self.backend.list_generated_files(self)
    
    def upload_model(self, filePath: str):
        return self.backend.upload_model(filePath)

    def upload_validation_input_file(self, filePath: str):
        return self.backend.upload_validation_input_file(filePath)

    def upload_validation_output_file(self, filePath: str):
        return self.backend.upload_validation_output_file(filePath)

    def download_model(self, model_path, target):
        return self.backend.download_model(model_path, target)

    def download_validation_input_file(self, filePath):
        return self.backend.download_validation_input_file(filePath)

    def download_validation_output_file(self, filePath):
        return self.backend.download_validation_output_file(filePath)

    def download_generated_file(self, filePath):
        return self.backend.download_generated_file(filePath)

    def delete_model(self, modelName: str):
        return self.backend.delete_model(modelName)

    def delete_validation_input_file(self, fileName: str):
        return self.backend.delete_validation_input_file(fileName)

    def delete_validation_output_file(self, fileName: str):
        return self.backend.delete_validation_output_file(fileName)
    
    def delete_generated_file(self, fileName: str):
        return self.backend.delete_generated_file(fileName)
