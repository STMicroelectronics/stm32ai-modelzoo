# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import json
import typing
from common.stm32ai_dc.backend.cloud.file_service import FileService
from common.stm32ai_dc.errors import BenchmarkFailure, BenchmarkParameterError
from common.stm32ai_dc.errors import ModelNotFoundError, WrongTypeError
from common.stm32ai_dc.types import LOGGER_NAME, AtonParametersSchema, CliParameters, MpuParameters
from .helpers import send_get, send_post
from .endpoints import get_benchmark_boards_ep, get_benchmark_openapi_ep
from .endpoints import get_benchmark_service_ep
import time
import logging
from tqdm import tqdm

logger = logging.getLogger(LOGGER_NAME)


class BenchmarkService:
    def __init__(self, auth_token, silent = False) -> None:
        self.auth_token = auth_token
        self.main_route = get_benchmark_service_ep()
        self.benchmark_state = None
        self.silent = silent
        self.file_service = FileService(self.auth_token)

        self._use_stringify_args = False
        try:
            resp = send_get(get_benchmark_openapi_ep(), withToken=None).json()
            options_def = resp['paths']['/benchmark/{queue}']['post']
            options_def = options_def['requestBody']['content']
            options_def = options_def['application/json']['schema']
            options_def = options_def['properties']

            if 'model' in options_def and 'args' in options_def and  \
                    len(options_def.keys()) == 2:
                self._use_stringify_args = True
                logger.debug('Benchmark service configured to use old \
                    stringify args parameter')
        except Exception as e:
            logger.debug(e)
            logger.warn('Error when analyzing openapi definition of the API')

    def list_boards(self) -> dict:
        resp = send_get(
            get_benchmark_boards_ep(),
            withToken=self.auth_token)

        if resp.status_code == 200:
            json_resp = resp.json()
            resp.close()
            return json_resp
        else:
            logger.error(f"Error: server response code is: {resp.status_code}")

    def _get_cloud_models(self) -> typing.List[str]:
        return list(map(lambda x: x['name'], self.file_service.list_models()))

    def trigger_benchmark(self, options: typing.Union[CliParameters, MpuParameters], board_name: str, version: str = None):
        if not (isinstance(options, CliParameters) or isinstance(options, MpuParameters)):
            raise WrongTypeError(options, typing.Union[CliParameters, MpuParameters])

        def _build_arguments_dict(options: typing.Union[CliParameters, MpuParameters]):
            data = {}
            for field in options._fields:
                current_value = getattr(options, field)
                if field in ['model', 'output', 'atonnOptions'] or current_value is None:
                    continue
                if field == 'mpool':
                    with open(current_value, 'r') as f:
                        data[field] = json.load(f) # dump .mpool file as object in field
                    continue
                if version:
                    data['version'] = version
                try: 
                    data[field] = current_value.value
                except Exception as _:
                    if current_value is not None:
                        data[field] = current_value
            if (hasattr(options, 'atonnOptions')):
                data['atonnOptions'] = AtonParametersSchema().dump(options.atonnOptions)
            return data

        model_name = options.model if options.model else None
        data = _build_arguments_dict(options)

        cloud_models = self._get_cloud_models()
        if model_name not in cloud_models:
            raise ModelNotFoundError(f"model: {model_name} not found on cloud")

        if self._use_stringify_args:
            # Keeping "args" for compatilibity reason
            data_to_be_sent = {"args": json.dumps(data), "model": model_name}
        else:
            data_to_be_sent = data
            data_to_be_sent["model"] = model_name

        route = f'{self.main_route}/benchmark'
        if (isinstance(options, MpuParameters)):
            route += '/mpu'
        resp = send_post(
            f'{route}/{board_name.lower()}',
            withToken=self.auth_token,
            usingJson=data_to_be_sent)

        if resp.status_code == 200:
            json_resp = resp.json()
            resp.close()

            if 'benchmarkId' in json_resp:
                if 'model' not in json_resp:
                    logger.warning('No model confirmation in server response')
                if 'args' not in json_resp or \
                        not bool(resp.json().get('args')):
                    logger.warning('No args confirmation in server reponse')
                logger.debug(f'Triggering benchmark {json_resp}')
                return json_resp['benchmarkId']
            else:
                raise BenchmarkFailure("Error: server does not reply expected \
                    response")
        else:
            try:
                json_resp = resp.json()
                if 'errors' in json_resp:
                    raise BenchmarkParameterError(board_name, f"Wrong parameter\
                        : {json_resp.get('errors', None)}")
                else:
                    raise BenchmarkParameterError(board_name, f"Wrong parameter\
                        : {resp.text}")
            except json.JSONDecodeError:
                pass
            raise BenchmarkFailure(f"Error: server response code is \
                {resp.status_code}")

    def _get_run(self, benchmarkId: str):
        resp = send_get(f"{self.main_route}/benchmark/{benchmarkId}",
                        self.auth_token)

        if resp.status_code == 200:
            return resp.json()
        else:
            return None

    def wait_for_run(self, benchmark_id: str, timeout=900, pooling_delay=2):
        """
            Wait for a benchmark run to be completed.
            If no result until timeoutit returns None
        """
        current_state = None
        current_progress = 0
        start_time = time.time()
        is_over = False
        self.benchmark_state = None

        def calculate_percentage(step, total_step, progress):
            if total_step == 0:
                return 0  # Avoid division by zero
            return ((step - 1) / total_step) * 100 + (progress / total_step)
             
        with tqdm(total=100, desc="Waiting for benchmark", unit='%', leave=False, disable=self.silent) as pbar:
            while not is_over:
                if (time.time() - start_time) > timeout:
                    is_over = True

                result = self._get_run(benchmark_id)
                if result:
                    if isinstance(result, dict):
                        new_state = result.get('state', '').lower()
                        self.benchmark_state = new_state
                        if new_state != current_state:
                            current_state = new_state
                            start_time = time.time()
                        new_progress = calculate_percentage(
                            result.get('step', 0),
                            result.get('totalStep', 1),
                            result.get('progress', 0)
                        )
                        increment = new_progress - current_progress
                        current_progress = new_progress
                        pbar.update(increment)
                        pbar.set_description(f'Benchmarking: {new_state}')
                        if new_state == 'done':
                            return result
                        elif new_state == 'error':
                            logger.error(f'Benchmark return an error: {result}')
                            raise BenchmarkFailure(result.get('board', 'ND'),
                                                result.get('message', 'no info')
                                                )
                        elif new_state == 'waiting_for_build':
                            logger.debug(f'Benchmark({benchmark_id}) status: Project \
                                is waiting for build')
                        elif new_state == 'in_queue':
                            logger.debug(f'Benchmark({benchmark_id}) status: Model \
                                is in queue')
                        elif new_state == 'flashing':
                            logger.debug(f'Benchmark({benchmark_id}) status: \
                                Flashing remote board')
                        elif new_state == \
                                'generating_sources':
                            logger.debug(f'Benchmark({benchmark_id}) status: \
                                Generating sources')
                        elif new_state == \
                            'copying_sources':
                            logger.debug(f'Benchmark({benchmark_id}) status: \
                                Copying sources')
                        elif new_state == 'loading_sources':
                            logger.debug(f'Benchmark({benchmark_id}) status: \
                                Loading sources')
                        elif new_state == 'building':
                            logger.debug(f'Benchmark({benchmark_id}) status: \
                                Building sources')
                        elif new_state == 'validation':
                            logger.debug(f'Benchmark({benchmark_id}) status: \
                                Validating model')
                        else:
                            logger.warn(f"Unknown {result.get('state', '')} key \
                                received from server")
                    else:
                        logger.error("Error: Message received from server is not \
                            an object: ", result)
                        return None

                time.sleep(pooling_delay)
