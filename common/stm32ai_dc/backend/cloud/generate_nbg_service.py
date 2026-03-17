# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import logging
from common.stm32ai_dc.errors import GenerateNbgFailure
from common.stm32ai_dc.types import LOGGER_NAME
from .helpers import send_get, send_post
from .endpoints import get_generate_nbg_service_ep
import time

logger = logging.getLogger(LOGGER_NAME)


class GenerateNbgService:
    def __init__(self, auth_token) -> None:
        self.auth_token = auth_token
        self.main_route = get_generate_nbg_service_ep()

    def trigger_optimize(self, model_name):
        data_to_be_sent = {}
        data_to_be_sent["model"] = model_name
        route = f'{self.main_route}/optimize'
        resp = send_post(
            route,
            withToken=self.auth_token,
            usingJson=data_to_be_sent)

        if resp.status_code == 200:
            json_resp = resp.json()
            resp.close()

            if 'runtimeId' in json_resp:
                if 'model' not in json_resp:
                    logger.warning('No model confirmation in server response')
                logger.debug(f'Triggering optimize {json_resp}')
                return json_resp['runtimeId']
            else:
                raise GenerateNbgFailure("Error: server does not reply expected \
                    response")

    def _get_run(self, benchmarkId: str):
        resp = send_get(f"{self.main_route}/run/{benchmarkId}",
                        self.auth_token)

        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error("Error server reply with non 200 HTTP code")
            return None

    def wait_for_run(self, runtime_id: str, timeout=300, pooling_delay=2):
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

            result = self._get_run(runtime_id)
            if result:
                if isinstance(result, dict):
                    self.benchmark_state = result.get('state', '').lower()
                    if result.get('state', '').lower() == 'done':
                        return result
                    elif result.get('state', '').lower() == 'error':
                        logger.error(f'Optimize return an error: {result}')
                        raise GenerateNbgFailure(result.get('board', 'ND'),
                                               result.get('message', 'no info')
                                               )
                    elif result.get('state', '').lower() == 'in_queue':
                        logger.debug(f'Optimize({runtime_id}) status: Model \
                            is in queue')
                    else:
                        logger.warn(f"Unknown {result.get('state', '')} key \
                            received from server")
                else:
                    logger.error("Error: Message received from server is not \
                        an object: ", result)
                    return None

            time.sleep(pooling_delay)
