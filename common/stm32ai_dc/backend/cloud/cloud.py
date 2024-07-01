# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import os
import functools
import typing
from stm32ai_dc.backend.cloud.generate_nbg_service import GenerateNbgService
from stm32ai_dc.backend.cloud.benchmark_service import BenchmarkService
from stm32ai_dc.backend.cloud.file_service import FileService
from stm32ai_dc.backend.cloud.helpers import get_supported_versions
from stm32ai_dc.backend.cloud.login_service import LoginService
from stm32ai_dc.backend.cloud.user_service import UserService
from stm32ai_dc.backend.cloud.stm32ai_service import Stm32AiService
from stm32ai_dc.errors import GenerateNbgFailure, AnalyzeServerError, BenchmarkServerError, InvalidCrendetialsException
from stm32ai_dc.errors import FileFormatError, GenerateServerError
from stm32ai_dc.errors import InternalErrorThatShouldNotHappened
from stm32ai_dc.errors import ParameterError, ValidateServerError
from stm32ai_dc.errors import LoginFailureException
from stm32ai_dc.types import AnalyzeResult, BackendVersionType, BenchmarkResult, BoardData, MpuBenchmarkResult, MpuParameters
from stm32ai_dc.types import GenerateResult, Stm32AiBackend, CliParameters
from stm32ai_dc.types import ValidateResult, ValidateResultMetrics


class CloudBackend(Stm32AiBackend):
    def __init__(
            self, 
            username: str, 
            password: str, 
            version: typing.Union[str, None] = None,
            platform: BackendVersionType = BackendVersionType.STM32,
        ) -> None:
        self.username = username
        self.password = password
        self.version = version
        self.supportedVersions = get_supported_versions()
        self.login_service = LoginService()
        try:
            user_version = next(x for x in self.supportedVersions if x.get('platform',{}).get(platform, x['version']) == version)
            self.version = user_version['version']
        except Exception as e:    
            print(
                f'[WARN] Version {self.version} for platform {platform} is not supported by Developer Cloud.')
            for v in self.supportedVersions:
                if (v.get('isLatest', False) == True):
                    latest = v
            if (latest):
                self.version = latest.get('version', None)
                print(
                    f"[WARN] It will use the latest version by default ({self.version}, {platform} version: {latest.get('platform').get(platform, '---')})")
        if username is None or password is None or not len(username) or not len(password):
            # Try to use previous tokens saved in home directory
            sso_resp = self.login_service.get_access_token()
            if (sso_resp):
                self.auth_token = sso_resp
            else:
                raise LoginFailureException(
                    username,
                    password,
                    details='Empty login or stored token invalid.')
        else:
            try:
                self.auth_token = self.login_service.login(
                    username=username, password=password)
            except InvalidCrendetialsException as e :
                raise e
            except Exception:
                raise LoginFailureException(
                    username,
                    password,
                    details='Login failure, try again and please check your credentials and/or your network'
                )

        if self.auth_token is None:
            raise LoginFailureException(
                username,
                password,
                details='Please check your credentials')

        self.user_service = UserService(self.auth_token)
        self.stm32ai_service = Stm32AiService(self.auth_token, self.version)
        self.file_service = FileService(self.auth_token)
        self.benchmark_service = BenchmarkService(self.auth_token)
        self.generate_nbg_service = GenerateNbgService(self.auth_token)

    def get_user(self):
        return self.user_service.get_user()

    def analyze(self, options: CliParameters) -> AnalyzeResult:
        rid = self.stm32ai_service.trigger_analyze(options)
        result = self.stm32ai_service.wait_for_run(rid)

        if result is None or 'report' not in result\
                or result['report'] is None:
            if result is None and 'message' in result:
                raise AnalyzeServerError(f"Missing data in server \
                    response: {result['message']}")
            raise AnalyzeServerError('Missing data in server response')

        report = result.get('report', None)
        graph = result.get('graph', None)
        info = result.get('info', None)
        date_time = info['environment']['generated_model']['generated_time'] if info is not None else report['date_time']
        cli_version_str = info['environment']['tools'][0]['version']  if info is not None else report['cli_version_str']
        cli_parameters = info['environment']['tools'][0]['arguments']  if info is not None else report['cli_parameters']
        memory_footprint = graph.get('memory_footprint', {}) if graph else info.get('memory_footprint', {})
        analyze_result = AnalyzeResult(
            activations_size=memory_footprint.get('activations', 0),
            weights=memory_footprint.get('weights', 0),
            macc=graph['macc'] if graph else 0,
            rom_size=memory_footprint.get('weights', 0)
            + memory_footprint.get('kernel_flash', 0)
            + memory_footprint.get('toolchain_flash', 0),
            ram_size=memory_footprint.get('activations', 0)
            + functools.reduce(
                lambda a, b: a+b,
                memory_footprint.get('io', []), 0)
            + memory_footprint.get('kernel_ram', 0)
            + memory_footprint.get('toolchain_ram',
                                   memory_footprint.get('extra_ram', 0)),
            total_ram_io_size=functools.reduce(
                lambda a, b: a+b,
                memory_footprint.get('io', []), 0),
            report=report,
            graph=graph,
            info=info,
            date_time=date_time,
            cli_version_str=cli_version_str,
            cli_parameters=cli_parameters,
            estimated_library_flash_size=memory_footprint.get(
                'kernel_flash', -1),
            estimated_library_ram_size=memory_footprint.get(
                'kernel_ram', -1)
        )
        return analyze_result

    def generate(self, options: CliParameters) -> GenerateResult:
        import zipfile  # Local import to avoid global perf drawback

        if not os.path.exists(options.output):
            os.makedirs(options.output, exist_ok=True)

        rid = self.stm32ai_service.trigger_generate(options)
        result = self.stm32ai_service.wait_for_run(rid)

        if result is None or 'url' not in result:
            if result is None and 'message' in result:
                raise GenerateServerError(f"Missing data in server \
                    response: {result.get('message')}")
            raise GenerateServerError('Missing data in server response')

        local_filepath = self.file_service.download_generated_file(
            result.get('url', None),
            options.output)
        if local_filepath:
            # TODO: Check is file is really zip file or JSON content
            if zipfile.is_zipfile(local_filepath):
                zfile = zipfile.ZipFile(local_filepath)
                zfile.extractall(options.output)
                zfile.close()
                return GenerateResult(
                    server_url=result.get('url', None),
                    zipfile_path=local_filepath, output_path=options.output,
                    graph=result.get('graph', {}),
                    report=result.get('report', {}))
            else:
                raise FileFormatError("A zip file was expected \
                    as server reply")
        raise InternalErrorThatShouldNotHappened("No local file received")

    def validate(self, options: CliParameters) -> ValidateResult:
        rid = self.stm32ai_service.trigger_validate(options)
        result = self.stm32ai_service.wait_for_run(rid)

        if result is None or 'report' not in result \
                or result['report'] is None or 'graph' not in result:
            if result is None and 'message' in result:
                raise ValidateServerError(f"Missing data in server \
                    response: {result.get('message')}")
            raise ValidateServerError('Missing data in server response')

        report = result.get('report', {})
        graph = result.get('graph', {})
        cinfo = result.get('info', None)

        if cinfo != None:
            validate_result_metrics = []
            for valmetrics in cinfo['validation']['val_metrics']:
                validate_result_metrics.append(ValidateResultMetrics(
                    accuracy=valmetrics['acc'],
                    description=valmetrics['desc'],
                    l2r=valmetrics['l2r'],
                    mae=valmetrics['mae'],
                    mean=valmetrics['mean'],
                    rmse=valmetrics['rmse'],
                    std=valmetrics['std'],
                    ts_name=valmetrics.get('ts_name', '')
                ))
            cinfo_graph = cinfo['graphs'][0]
            memory_footprint=cinfo.get('memory_footprint', {})
            validate_result = ValidateResult(
                rom_size=memory_footprint['weights'],
                macc=functools.reduce(lambda a, b: a+b, map(lambda a: a['macc'], cinfo_graph['nodes']), 0),
                ram_size=memory_footprint['activations'],
                total_ram_io_size=functools.reduce(
                    lambda a, b: a+b,
                    memory_footprint['io'], 0),
                validation_metrics=validate_result_metrics,
                validation_error=cinfo['validation']['val_error'],
                validation_error_description=cinfo['validation']['val_error_desc'],
                # rom_compression_factor=report['rom_cfact'],
                # report_version=report['report_version'],
                date_time=cinfo['environment']['generated_model']['generated_time'],
                cli_version_str=cinfo['environment']['tools'][0]['version'],
                cli_parameters=cinfo['environment']['tools'][0]['arguments'],
                report=report,
                graph=graph,
                info=cinfo,
                estimated_library_flash_size=memory_footprint.get("kernel_flash", 0)
                    + memory_footprint.get("extra_flash", 0)
                    + memory_footprint.get("toolchain_flash", 0),
                estimated_library_ram_size=memory_footprint.get("kernel_ram", 0)
                    + memory_footprint.get("extra_ram", 0)
                    + memory_footprint.get("toolchain_ram", 0),
            )
            return validate_result
        else:
            validate_result_metrics = []
            for valmetrics in report['val_metrics']:
                validate_result_metrics.append(ValidateResultMetrics(
                    accuracy=valmetrics['acc'],
                    description=valmetrics['desc'],
                    l2r=valmetrics['l2r'],
                    mae=valmetrics['mae'],
                    mean=valmetrics['mae'],
                    rmse=valmetrics['rmse'],
                    std=valmetrics['std'],
                    ts_name=valmetrics['ts_name']
                ))
            validate_result = ValidateResult(
                rom_size=report['rom_size'],
                macc=report['rom_n_macc'],
                ram_size=report['ram_size'][0],
                total_ram_io_size=functools.reduce(
                    lambda a, b: a+b,
                    report.get('ram_io_size', 0), 0),
                validation_metrics=validate_result_metrics,
                validation_error=report['val_error'],
                validation_error_description=report['val_error_desc'],
                # rom_compression_factor=report['rom_cfact'],
                # report_version=report['report_version'],
                date_time=report['date_time'],
                cli_version_str=report['cli_version_str'],
                cli_parameters=report['cli_parameters'],
                report=report,
                graph=graph,
                info=None,
                estimated_library_flash_size=memory_footprint.get("kernel_flash", 0)
                    + memory_footprint.get("toolchain_flash", 0)
                    + memory_footprint.get("extra_flash", 0),
                estimated_library_ram_size=memory_footprint.get("kernel_ram", 0)
                    + memory_footprint.get("extra_ram", 0)
                    + memory_footprint.get("toolchain_ram", 0),
            )
            return validate_result

    def benchmark(self, options: typing.Union[CliParameters, MpuParameters], board_name: str, timeout: int):
        if options.model not in list(map(lambda x: x['name'], self.file_service.list_models())):
            raise ParameterError("options.model should be a file name that is \
                already uploaded on the cloud")
        bid = self.benchmark_service.trigger_benchmark(
            options, board_name, self.version)
        result = self.benchmark_service.wait_for_run(bid, timeout=timeout)
        if (isinstance(options, MpuParameters)):
            benchmark_report = result.get('benchmark', {})
            exec_time = benchmark_report.get('exec_time', {})
            tool_version = benchmark_report.get('tool_version', {})
            benchmark_result = MpuBenchmarkResult(
                device=benchmark_report.get('board', 'N/A'),
                duration_ms=exec_time.get('duration_ms', -1),
                npu_percent=exec_time.get('npu_percent', -1),
                gpu_percent=exec_time.get('gpu_percent', -1),
                cpu_percent=exec_time.get('cpu_percent', -1),
                rom_size=benchmark_report.get('model_size', -1),
                ram_size=benchmark_report.get('ram_peak', -1),
                date_time=benchmark_report.get('date'),
                info=benchmark_report,
                cli_version_str=tool_version.get('name') + ' ' + tool_version.get('major') + '.' + tool_version.get('minor') + '.' + tool_version.get('micro')
            )
            return benchmark_result
        elif (isinstance(options, CliParameters)):
            if result.get('benchmark', {}).get('info', None) != None:
                cinfo = result['benchmark']['info']
                memory_mapping = result.get('memoryMapping', {}) if result.get('memoryMapping') is not None else {}
                report = result['benchmark']['report']
                validate_result_metrics = []
                for valmetrics in cinfo.get('validation', {}).get('val_metrics', []):
                    validate_result_metrics.append(ValidateResultMetrics(
                        accuracy=valmetrics['acc'],
                        description=valmetrics['desc'],
                        l2r=valmetrics['l2r'],
                        mae=valmetrics['mae'],
                        mean=valmetrics['mean'],
                        rmse=valmetrics['rmse'],
                        std=valmetrics['std'],
                        ts_name=valmetrics.get('ts_name', '')
                    ))
                cinfo_graph = cinfo['graphs'][0]
                graph = result['benchmark']['graph']
                exec_time = cinfo_graph.get('exec_time', graph.get('exec_time', {}))
                c_arrays = {}
                for arr in [b for b in  cinfo['buffers'] if b['is_param'] == True]:
                    c_arrays[arr['name']] = arr
                memory_footprint = memory_mapping.get('memoryFootprint', cinfo.get("memory_footprint", {}))
                memory_pools = [p for p in cinfo.get('memory_pools', []) if p.get('size_bytes', -1) >= 0]
                internal_memory_pools = [p for p in memory_pools if "EXTERNAL" not in p['name']]
                external_memory_pools = [p for p in memory_pools if "EXTERNAL" in p['name']]
                layers_in_internal_flash = memory_mapping.get('layersInExternalFlash', [])
                layers_in_external_flash = memory_mapping.get('layersInInternalFlash', [])
                internal_flash_usage = functools.reduce(lambda a, b: a+b, map(lambda a: c_arrays.get(a + "_array", {}).get('size_bytes', 0), layers_in_internal_flash), 0)
                external_flash_usage = functools.reduce(lambda a, b: a+b, map(lambda a: c_arrays.get(a + "_array", {}).get('size_bytes', 0), layers_in_external_flash), 0)
                benchmark_result = BenchmarkResult(
                    rom_size=memory_footprint['weights'],
                    macc=functools.reduce(lambda a, b: a+b, map(lambda a: a['macc'], cinfo_graph['nodes']), 0),
                    ram_size=memory_footprint['activations'],
                    total_ram_io_size=functools.reduce(
                        lambda a, b: a+b,
                        memory_footprint['io'], 0),
                    validation_metrics=validate_result_metrics,
                    validation_error=cinfo.get('validation', {}).get('val_error', ''),
                    validation_error_description=cinfo.get('validation', {}).get('val_error_desc', ''),
                    # rom_compression_factor=report['rom_cfact'],
                    # report_version=report['report_version'],
                    date_time=cinfo['environment']['generated_model']['generated_time'],
                    cli_version_str=cinfo['environment']['tools'][0]['version'],
                    cli_parameters=cinfo['environment']['tools'][0]['arguments'],
                    report=report,
                    graph=graph,
                    info=cinfo,
                    cycles=exec_time.get('cycles', -1),
                    duration_ms=exec_time.get('duration_ms', -1),
                    device=cinfo['environment'].get('device', ""),
                    cycles_by_macc=exec_time.get('cycles_by_macc', -1),
                    estimated_library_flash_size=memory_footprint.get("kernel_flash", 0)
                        + memory_footprint.get("extra_flash", 0)
                        + memory_footprint.get("toolchain_flash", 0),
                    estimated_library_ram_size=memory_footprint.get("kernel_ram", 0)
                        + memory_footprint.get("extra_ram", 0)
                        + memory_footprint.get("toolchain_ram", 0),
                    use_external_ram=memory_mapping.get("useExternalRam", False),
                    use_external_flash=memory_mapping.get("useExternalFlash", False),
                    internal_ram_consumption=functools.reduce(lambda a, b: a + b.get("used_size_bytes", 0), internal_memory_pools, 0),
                    external_ram_consumption=functools.reduce(lambda a, b: a + b.get("used_size_bytes", 0), external_memory_pools, 0),
                    internal_flash_consumption=internal_flash_usage,
                    external_flash_consumption=external_flash_usage,
                )
                return benchmark_result
            elif result:
                benchmark = result.get('benchmark', {})
                memory_mapping = result.get('memoryMapping', {}) if result.get('memoryMapping') is not None else {}
                report = benchmark['report']
                validate_result_metrics = []
                for valmetrics in report['val_metrics']:
                    validate_result_metrics.append(ValidateResultMetrics(
                        accuracy=valmetrics['acc'],
                        description=valmetrics['desc'],
                        l2r=valmetrics['l2r'],
                        mae=valmetrics['mae'],
                        mean=valmetrics['mean'],
                        rmse=valmetrics['rmse'],
                        std=valmetrics['std'],
                        ts_name=valmetrics['ts_name']
                    ))
                graph = benchmark['graph']
                exec_time = graph['exec_time']
                c_arrays = {}
                for arr in graph.get('c_arrays', []):
                    c_arrays[arr['name']] = arr
                memory_footprint = memory_mapping.get('memoryFootprint', graph.get("memory_footprint", {}))
                memory_pools = [p for p in graph.get('memory_pools', []) if p.get('size_bytes', -1) >= 0]
                internal_memory_pools = [p for p in memory_pools if "EXTERNAL" not in p['name']]
                external_memory_pools = [p for p in memory_pools if "EXTERNAL" in p['name']]
                layers_in_internal_flash = memory_mapping.get('layersInExternalFlash', [])
                layers_in_external_flash = memory_mapping.get('layersInInternalFlash', [])
                internal_flash_usage = functools.reduce(lambda a, b: a+b, map(lambda a: c_arrays.get(a + "_array").get('c_size_in_byte'), layers_in_internal_flash), 0)
                external_flash_usage = functools.reduce(lambda a, b: a+b, map(lambda a: c_arrays.get(a + "_array").get('c_size_in_byte'), layers_in_external_flash), 0)
                benchmark_result = BenchmarkResult(
                    rom_size=report['rom_size'],
                    macc=report['rom_n_macc'],
                    ram_size=report['ram_size'][0],
                    total_ram_io_size=functools.reduce(
                        lambda a, b: a+b,
                        report.get('ram_io_size', 0), 0),
                    validation_metrics=validate_result_metrics,
                    validation_error=report['val_error'],
                    validation_error_description=report['val_error_desc'],
                    # rom_compression_factor=report['rom_cfact'],
                    # report_version=report['report_version'],
                    date_time=report['date_time'],
                    cli_version_str=report['cli_version_str'],
                    cli_parameters=report['cli_parameters'],
                    report=report,
                    graph=graph,
                    info=None,
                    cycles=exec_time.get('cycles', -1),
                    duration_ms=exec_time.get('duration_ms', -1),
                    device=exec_time.get('device', ""),
                    cycles_by_macc=exec_time.get('cycles_by_macc', -1),
                    estimated_library_flash_size=memory_footprint.get("kernel_flash", 0)
                        + memory_footprint.get("extra_flash", 0)
                        + memory_footprint.get("toolchain_flash", 0),
                    estimated_library_ram_size=memory_footprint.get("kernel_ram", 0)
                        + memory_footprint.get("extra_ram", 0)
                        + memory_footprint.get("toolchain_ram", 0),
                    use_external_ram=memory_mapping.get("useExternalRam", False),
                    use_external_flash=memory_mapping.get("useExternalFlash", False),
                    internal_ram_consumption=functools.reduce(lambda a, b: a + b.get("used_size", 0), internal_memory_pools, 0),
                    external_ram_consumption=functools.reduce(lambda a, b: a + b.get("used_size", 0), external_memory_pools, 0),
                    internal_flash_consumption=internal_flash_usage,
                    external_flash_consumption=external_flash_usage,
                )
                return benchmark_result
            else:
                raise BenchmarkServerError("Benchmark service return wrong format")

    def generate_nbg(self, model_name, timeout = 300):
        bid = self.generate_nbg_service.trigger_optimize(
            model_name)
        result = self.generate_nbg_service.wait_for_run(bid, timeout=timeout)
        if result.get('blobName', None) != None:
            return result.get('blobName')
        else:
            raise GenerateNbgFailure('NBG Generation failed. No file found')

    def get_benchmark_boards(self):
        out: typing.List[BoardData] = []
        boards_data = self.benchmark_service.list_boards()
        for k in boards_data.keys():
            out.append(BoardData(
                name=k,
                boardCount=boards_data[k].get('boardCount', -1),
                flashSize=boards_data[k].get('flashSize', ''),
                deviceCpu=boards_data[k].get('deviceCpu', ''),
                deviceId=boards_data[k].get('deviceId', '')))
        return out

    def list_models(self):
        return self.file_service.list_models()

    def upload_model(self, model_path: str):
        return self.file_service.upload_model(model_path)

    def download_model(self, model_name: str, path: str):
        return self.file_service.download_model(model_name, path)

    def delete_model(self, model_name: str):
        return self.file_service.delete_model(model_name)
