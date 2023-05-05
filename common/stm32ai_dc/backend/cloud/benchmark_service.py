# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import json
import os
import typing
from stm32ai_dc.backend.cloud.file_service import FileService
from stm32ai_dc.errors import BenchmarkFailure, BenchmarkParameterError
from stm32ai_dc.errors import ModelNotFoundError, WrongTypeError
from stm32ai_dc.types import LOGGER_NAME, CliParameterCompression
from stm32ai_dc.types import CliParameterVerbosity, CliParameters
from stm32ai_dc.types import CliParameterType
from .helpers import send_get, send_post
from .endpoints import get_benchmark_boards_ep, get_benchmark_openapi_ep
from .endpoints import get_benchmark_service_ep
import time
import logging

logger = logging.getLogger(LOGGER_NAME)


class BenchmarkService:
    def __init__(self, auth_token) -> None:
        self.auth_token = auth_token
        self.main_route = get_benchmark_service_ep()
        self.benchmark_state = None
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

    def trigger_benchmark(self, options: CliParameters, boardName: str, version: str = None):
        if type(options) != CliParameters:
            raise WrongTypeError(options, CliParameters)

        def _build_arguments_dict(options: CliParameters):
            data = {}
            for field in options._fields:
                current_value = getattr(options, field)
                if field in ['model', 'output'] or current_value is None:
                    continue
                if version:
                    data['version'] = version
                if isinstance(current_value, CliParameterCompression):
                    data[field] = current_value.value
                elif isinstance(current_value, CliParameterType):
                    data[field] = current_value.value
                elif isinstance(current_value, CliParameterVerbosity):
                    data[field] = current_value.value
                else:
                    if current_value is not None:
                        data[field] = current_value
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

        resp = send_post(
            f'{self.main_route}/benchmark/{boardName.lower()}',
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
                    raise BenchmarkParameterError(boardName, f"Wrong parameter\
                        : {json_resp.get('errors', None)}")
                else:
                    raise BenchmarkParameterError(boardName, f"Wrong parameter\
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
            logger.error("Error server reply with non 200 HTTP code")
            return None

    def wait_for_run(self, benchmarkId: str, timeout=300, pooling_delay=2):
        """
            Wait for a benchmark run to be completed.
            If no result until timeoutit returns None
        """
        start_time = time.time()
        is_over = False
        self.benchmark_state = None
        while not is_over:
            if (time.time() - start_time) > timeout:
                is_over = True

            result = self._get_run(benchmarkId)
            if result:
                if isinstance(result, dict):
                    self.benchmark_state = result.get('state', '').lower()
                    if result.get('state', '').lower() == 'done':
                        return result.get('benchmark', {})
                    elif result.get('state', '').lower() == 'error':
                        logger.error(f'Benchmark return an error: {result}')
                        raise BenchmarkFailure(result.get('board', 'ND'),
                                               result.get('message', 'no info')
                                               )
                    elif result.get('state', '').lower() == 'waiting_for_build':
                        logger.debug(f'Benchmark({benchmarkId}) status: Project \
                            is waiting for build')
                    elif result.get('state', '').lower() == 'in_queue':
                        logger.debug(f'Benchmark({benchmarkId}) status: Model \
                            is in queue')
                    elif result.get('state', '').lower() == 'flashing':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Flashing remote board')
                    elif result.get('state', '').lower() == \
                            'generating_sources':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Generating sources')
                    elif result.get('state', '').lower() == 'loading_sources':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Loading sources')
                    elif result.get('state', '').lower() == 'building':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Building sources')
                    elif result.get('state', '').lower() == 'validation':
                        logger.debug(f'Benchmark({benchmarkId}) status: \
                            Validating model')
                    else:
                        logger.warn(f"Unknown {result.get('state', '')} key \
                            received from server")
                else:
                    logger.error("Error: Message received from server is not \
                        an object: ", result)
                    return None

            time.sleep(pooling_delay)
