# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import os
import functools
import typing
from stm32ai_dc.backend.cloud.benchmark_service import BenchmarkService
from stm32ai_dc.backend.cloud.file_service import FileService
from stm32ai_dc.backend.cloud.helpers import get_supported_versions
from stm32ai_dc.backend.cloud.login_service import LoginService
from stm32ai_dc.backend.cloud.user_service import UserService
from stm32ai_dc.backend.cloud.stm32ai_service import Stm32AiService
from stm32ai_dc.errors import (
    AnalyzeServerError,
    BenchmarkServerError,
    InvalidCredentialsException,
)
from stm32ai_dc.errors import FileFormatError, GenerateServerError
from stm32ai_dc.errors import InternalErrorThatShouldNotHappened
from stm32ai_dc.errors import ParameterError, ValidateServerError
from stm32ai_dc.errors import LoginFailureException
from stm32ai_dc.types import AnalyzeResult, BenchmarkResult, BoardData
from stm32ai_dc.types import GenerateResult, Stm32AiBackend, CliParameters
from stm32ai_dc.types import ValidateResult, ValidateResultMetrics


class CloudBackend(Stm32AiBackend):
    def __init__(
        self, username: str, password: str, version: typing.Union[str, None] = None
    ) -> None:
        self.username = username
        self.password = password
        self.version = version
        self.supportedVersions = get_supported_versions()
        self.login_service = LoginService()
        if version != None and version not in list(
            map(lambda x: x["version"], self.supportedVersions)
        ):
            print(f"[WARN] Version {version} is not supported by Developer Cloud.")
            for v in self.supportedVersions:
                if v.get("isLatest", False) == True:
                    latest = v
            if latest:
                self.version = latest.get("version", None)
                print(
                    f"[WARN] It will use the latest version by default ({self.version})"
                )

        if username is None or password is None:
            # Try to use previous tokens saved in home directory
            sso_resp = self.login_service.get_access_token()
            if sso_resp:
                self.auth_token = sso_resp
            else:
                raise LoginFailureException(
                    username, password, details="Empty login or stored token invalid."
                )
        else:
            try:
                self.auth_token = self.login_service.login(
                    username=username, password=password
                )
            except InvalidCredentialsException as e:
                raise e
            except Exception:
                raise LoginFailureException(
                    username,
                    password,
                    details="Login failure, try again and please check your credentials and/or your network",
                )

        if self.auth_token is None:
            raise LoginFailureException(
                username, password, details="Please check your credentials"
            )

        self.user_service = UserService(self.auth_token)
        self.stm32ai_service = Stm32AiService(self.auth_token, self.version)
        self.file_service = FileService(self.auth_token)
        self.benchmark_service = BenchmarkService(self.auth_token)

    def get_user(self):
        return self.user_service.get_user()

    def analyze(self, options: CliParameters) -> AnalyzeResult:
        rid = self.stm32ai_service.trigger_analyze(options)
        result = self.stm32ai_service.wait_for_run(rid)

        if result is None or "report" not in result or result["report"] is None:
            if result is None and "message" in result:
                raise AnalyzeServerError(
                    f"Missing data in server \
                    response: {result['message']}"
                )
            raise AnalyzeServerError("Missing data in server response")

        report = result["report"]
        graph = result["graph"]
        memory_footprint = graph.get("memory_footprint", {})
        analyze_result = AnalyzeResult(
            activations_size=memory_footprint.get("activations", 0),
            weights=memory_footprint.get("weights", 0),
            macc=graph["macc"],
            rom_size=memory_footprint.get("weights", 0),
            ram_size=memory_footprint.get("activations", 0),
            total_ram_io_size=functools.reduce(
                lambda a, b: a + b, memory_footprint.get("io", []), 0
            ),
            rom_compression_factor=report["rom_cfact"],
            report_version=report["report_version"],
            date_time=report["date_time"],
            cli_version_str=report["cli_version_str"],
            cli_parameters=report["cli_parameters"],
            report=report,
            graph=graph,
            estimated_library_flash_size=memory_footprint.get("kernel_flash", 0)
            + memory_footprint.get("extra_flash", 0)
            + memory_footprint.get("toolchain_flash", 0),
            estimated_library_ram_size=memory_footprint.get("kernel_ram", 0)
            + memory_footprint.get("extra_ram", 0)
            + memory_footprint.get("toolchain_ram", 0),
        )
        return analyze_result

    def generate(self, options: CliParameters) -> GenerateResult:
        import zipfile  # Local import to avoid global perf drawback

        if not os.path.exists(options.output):
            os.makedirs(options.output, exist_ok=True)

        rid = self.stm32ai_service.trigger_generate(options)
        result = self.stm32ai_service.wait_for_run(rid)

        if result is None or "url" not in result:
            if result is None and "message" in result:
                raise GenerateServerError(
                    f"Missing data in server \
                    response: {result.get('message')}"
                )
            raise GenerateServerError("Missing data in server response")

        local_filepath = self.file_service.download_generated_file(
            result.get("url", None), options.output
        )
        if local_filepath:
            # TODO: Check is file is really zip file or JSON content
            if zipfile.is_zipfile(local_filepath):
                zfile = zipfile.ZipFile(local_filepath)
                zfile.extractall(options.output)
                zfile.close()
                return GenerateResult(
                    server_url=result.get("url", None),
                    zipfile_path=local_filepath,
                    output_path=options.output,
                    graph=result.get("graph", {}),
                    report=result.get("report", {}),
                )
            else:
                raise FileFormatError(
                    "A zip file was expected \
                    as server reply"
                )
        raise InternalErrorThatShouldNotHappened("No local file received")

    def validate(self, options: CliParameters) -> ValidateResult:
        rid = self.stm32ai_service.trigger_validate(options)
        result = self.stm32ai_service.wait_for_run(rid)

        if (
            result is None
            or "report" not in result
            or result["report"] is None
            or "graph" not in result
        ):
            if result is None and "message" in result:
                raise ValidateServerError(
                    f"Missing data in server \
                    response: {result.get('message')}"
                )
            raise ValidateServerError("Missing data in server response")

        report = result["report"]
        graph = result.get("graph", {})
        memory_footprint = graph.get("memory_footprint", {})
        validate_result_metrics = []
        for valmetrics in report["val_metrics"]:
            validate_result_metrics.append(
                ValidateResultMetrics(
                    accuracy=valmetrics["acc"],
                    description=valmetrics["desc"],
                    l2r=valmetrics["l2r"],
                    mae=valmetrics["mae"],
                    mean=valmetrics["mae"],
                    rmse=valmetrics["rmse"],
                    std=valmetrics["std"],
                    ts_name=valmetrics["ts_name"],
                )
            )
        validate_result = ValidateResult(
            rom_size=memory_footprint.get("weights", 0),
            macc=graph.get("macc", 0),
            ram_size=memory_footprint.get("activations", 0),
            total_ram_io_size=functools.reduce(
                lambda a, b: a + b, memory_footprint.get("io", []), 0
            ),
            validation_metrics=validate_result_metrics,
            validation_error=report["val_error"],
            validation_error_description=report["val_error_desc"],
            rom_compression_factor=report["rom_cfact"],
            report_version=report["report_version"],
            date_time=report["date_time"],
            cli_version_str=report["cli_version_str"],
            cli_parameters=report["cli_parameters"],
            report=report,
            graph=graph,
            estimated_library_flash_size=memory_footprint.get("kernel_flash", 0)
            + memory_footprint.get("extra_flash", 0)
            + memory_footprint.get("toolchain_flash", 0),
            estimated_library_ram_size=memory_footprint.get("kernel_ram", 0)
            + memory_footprint.get("extra_ram", 0)
            + memory_footprint.get("toolchain_ram", 0),
        )
        return validate_result

    def benchmark(self, options: CliParameters, board_name: str, timeout=300):
        if options.model not in list(
            map(lambda x: x["name"], self.file_service.list_models())
        ):
            raise ParameterError(
                "options.model should be a file name that is \
                already uploaded on the cloud"
            )
        bid = self.benchmark_service.trigger_benchmark(
            options, board_name, self.version
        )
        result = self.benchmark_service.wait_for_run(bid, timeout=timeout)

        if result:
            report = result["report"]
            validate_result_metrics = []
            for valmetrics in report["val_metrics"]:
                validate_result_metrics.append(
                    ValidateResultMetrics(
                        accuracy=valmetrics["acc"],
                        description=valmetrics["desc"],
                        l2r=valmetrics["l2r"],
                        mae=valmetrics["mae"],
                        mean=valmetrics["mae"],
                        rmse=valmetrics["rmse"],
                        std=valmetrics["std"],
                        ts_name=valmetrics["ts_name"],
                    )
                )
            graph = result["graph"]
            exec_time = graph["exec_time"]
            memory_footprint = graph.get("memory_footprint", {})
            benchmark_result = BenchmarkResult(
                rom_size=memory_footprint.get("weights", 0),
                macc=graph.get("macc", 0),
                ram_size=memory_footprint.get("activations", 0),
                total_ram_io_size=functools.reduce(
                    lambda a, b: a + b, memory_footprint.get("io", []), 0
                ),
                validation_metrics=validate_result_metrics,
                validation_error=report["val_error"],
                validation_error_description=report["val_error_desc"],
                rom_compression_factor=report["rom_cfact"],
                report_version=report["report_version"],
                date_time=report["date_time"],
                cli_version_str=report["cli_version_str"],
                cli_parameters=report["cli_parameters"],
                report=report,
                graph=graph,
                cycles=exec_time.get("cycles", -1),
                duration_ms=exec_time.get("duration_ms", -1),
                device=exec_time.get("device", ""),
                cycles_by_macc=exec_time.get("cycles_by_macc", -1),
            )
            return benchmark_result
        else:
            raise BenchmarkServerError("Benchmark service return wrong format")

    def get_benchmark_boards(self):
        out: typing.List[BoardData] = []
        boards_data = self.benchmark_service.list_boards()
        for k in boards_data.keys():
            out.append(
                BoardData(
                    name=k,
                    boardCount=boards_data[k].get("boardCount", -1),
                    flashSize=boards_data[k].get("flashSize", ""),
                    deviceCpu=boards_data[k].get("deviceCpu", ""),
                    deviceId=boards_data[k].get("deviceId", ""),
                )
            )
        return out

    def list_models(self):
        return self.file_service.list_models()

    def upload_model(self, model_path: str):
        return self.file_service.upload_model(model_path)

    def delete_model(self, model_name: str):
        return self.file_service.delete_model(model_name)
