# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import time
import requests
import os
import json
import typing
from stm32ai_dc.backend.cloud.file_service import FileService
from stm32ai_dc.errors import ModelNotFoundError, WrongTypeError
from stm32ai_dc.types import CliParameterCompression, CliParameterType
from stm32ai_dc.types import CliParameterVerbosity, CliParameters
from .helpers import get_main_route_api_version, get_ssl_verify_status
from .helpers import get_value_or_default, _get_env_proxy
from .endpoints import get_stm32ai_analyze_ep, get_stm32ai_generate_ep
from .endpoints import get_stm32ai_run, get_stm32ai_service_ep
from .endpoints import get_stm32ai_validate_ep


STM32AI_SERVICE_MIN_VERSION = 0.0


class Stm32AiService:
    def __init__(self, auth_token, version: typing.Union[str, None]) -> None:
        self.auth_token = auth_token
        self.version = version
        if auth_token is None:
            raise Exception("Authentication token can't be None")

        self.main_route = get_stm32ai_service_ep(version)

        # if get_main_route_api_version(self.main_route) \
        #         < STM32AI_SERVICE_MIN_VERSION:
        #     raise Exception(f"Error: STM32AI service endpoint used is older\
        #          ({get_main_route_api_version(self.main_route)}) than minimuim\
        #              required version ({STM32AI_SERVICE_MIN_VERSION}). API may\
        #                  not work as expected.")

        self.analyze_route = get_stm32ai_analyze_ep(version)
        self.generate_route = get_stm32ai_generate_ep(version)
        self.validate_route = get_stm32ai_validate_ep(version)
        self.file_service = FileService(self.auth_token)

    def trigger_analyze(self, options: CliParameters):
        return self._make_trigger_request(self.analyze_route, options)

    def trigger_generate(self, options: CliParameters):
        return self._make_trigger_request(self.generate_route, options)

    def trigger_validate(self, options: CliParameters):
        return self._make_trigger_request(self.validate_route, options)

    def _get_cloud_models(self) -> typing.List[str]:
        return list(map(lambda x: x['name'], self.file_service.list_models()))

    def _make_trigger_request(self, route: str, options: CliParameters):
        if type(options) != CliParameters:
            raise WrongTypeError(options, CliParameters)

        def _build_arguments_dict(options: CliParameters):
            data = {}
            for field in options._fields:
                current_value = getattr(options, field)
                if field in ['output'] or current_value is None:
                    continue
                # if isinstance(current_value, bool):
                #     if current_value:
                #         data[field] = ''
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

        model_file_path = get_value_or_default(options, 'model', None)
        data = _build_arguments_dict(options)
        data['statsType'] = os.environ.get('STATS_TYPE', None)

        if os.path.exists(model_file_path):
            cloud_models = self._get_cloud_models()
            uploaded = False
            if os.path.basename(model_file_path) not in cloud_models:
                uploaded = self.file_service.upload_model(modelPath=model_file_path)
            else:
                uploaded = True
            if uploaded:
                data['model'] = os.path.basename(model_file_path)

        cloud_models = self._get_cloud_models()
        if data['model'] not in cloud_models:
            raise ModelNotFoundError(f"model: {model_file_path} not \
                        found locally or on cloud")


        headers = {'Authorization': 'Bearer '+self.auth_token}
        resp = requests.post(
            route,
            data={"args": json.dumps(data)},
            headers=headers, verify=get_ssl_verify_status(),
            proxies=_get_env_proxy())

        if resp.status_code == 200:
            if resp.headers.get('Content-Type', None) == 'application/zip':
                if options.output is None:
                    print("No output directory specified, please specify one")
                    return {'status': 'ko'}
                with open(
                        os.path.join(options.output, 'output.zip'), 'wb') as f:
                    f.write(resp.content)
                return {'status': 'ok'}

            else:
                json_resp = resp.json()
                if json_resp is None:
                    print("Error server reply an empty response")
                    return None
                if 'runtimeId' in json_resp:
                    return json_resp['runtimeId']
                elif 'status' in json_resp and json_resp['status'] == 'ko':
                    print(f"Error: \
{json_resp['error'] if 'error' in json_resp else 'Unknown'}")
                else:
                    print("Unknow error when triggering action on server")
                    return None
        else:
            print(f"Error server reply with {resp.status_code} \
                HTTP code: '{resp.reason}', '{resp.text}'")
            return None

    def _get_run(self, runtime_id: str):
        headers = {'Authorization': 'Bearer '+self.auth_token}
        resp = requests.get(
            get_stm32ai_run(self.version, runtime_id), headers=headers,
            verify=get_ssl_verify_status(), proxies=_get_env_proxy())

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            print("Error server reply: Unauthorized")
        else:
            print(f"Error server reply with non 200 HTTP code: \
                {resp.status_code}")
        return None

    def wait_for_run(self, runtime_id: typing.Union[str, None], timeout=300, pooling_delay=2):
        """
        Wait for a run to give results.
        If no result have been fetched before timeout, it returns None
        """
        if not runtime_id:
            return None
        start_time = time.time()
        is_over = False
        while not is_over:
            if (time.time() - start_time) > timeout:
                is_over = True

            result = self._get_run(runtime_id)
            if result:
                if isinstance(result, object):
                    state = result.get('state', None)
                    if state != None:
                        if result.get('result', None) != None:
                            return result.get('result', {})
                        elif state.lower() == 'error':
                            return result
                else:
                    print("Error: Message received from server is not \
                        an object: ", result)
                    return None
                time.sleep(pooling_delay)
            else:
                time.sleep(pooling_delay)
