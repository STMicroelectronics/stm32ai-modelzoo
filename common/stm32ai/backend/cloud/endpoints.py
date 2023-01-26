# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2019, 2022 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import os

USE_TEST_ROUTES_EV = 'USE_TEST_ROUTES'


class _BACKEND_ENDPOINTS:
    STM32AI_SERVICE_URL = 'https://stm32ai-cs.st.com/api/stm32ai'
    USER_SERVICE_URL = 'https://stm32ai-cs.st.com/api/user_service'
    FILE_SERVICE_URL = 'https://stm32ai-cs.st.com/api/file'
    BENCHMARK_SERVICE_URL = 'https://stm32ai-cs.st.com/api/benchmark'


class _BACKEND_TEST_ENDPOINTS:
    STM32AI_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/stm32ai'
    USER_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/user_service'
    FILE_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/file'
    BENCHMARK_SERVICE_URL = 'https://stm32ai-cs-qa.st.com/api/benchmark'


class _BACKEND_EV_NAME:
    STM32AI_SERVICE_URL = "STM32AI_SERVICE_URL"
    LOGIN_SERVICE_URL = "LOGIN_SERVICE_URL"
    USER_SERVICE_URL = "USER_SERVICE_URL"
    FILE_SERVICE_URL = "FILE_SERVICE_URL"
    BENCHMARK_SERVICE_URL = "BENCHMARK_SERVICE_URL"


# ######## User service related functions ########


def get_user_service_ep():
    """
    Main route to get user related data
    """
    if os.environ.get(_BACKEND_EV_NAME.USER_SERVICE_URL):
        return os.environ.get(_BACKEND_EV_NAME.USER_SERVICE_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return _BACKEND_TEST_ENDPOINTS.USER_SERVICE_URL
    else:
        return _BACKEND_ENDPOINTS.USER_SERVICE_URL


# ######## Login service related functions ########

def get_login_service_ep():
    """
    Main route to access login features
    """

    if os.environ.get(_BACKEND_EV_NAME.USER_SERVICE_URL):
        return os.environ.get(_BACKEND_EV_NAME.USER_SERVICE_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return _BACKEND_TEST_ENDPOINTS.USER_SERVICE_URL
    else:
        return _BACKEND_ENDPOINTS.USER_SERVICE_URL


def get_login_authenticate_ep():
    """
    Route on which user check authentication status (GET)
    and authenticate (POST)
    """
    return get_login_service_ep() + '/authenticate'


# ######## stm32ai related functions ########


def get_stm32ai_service_ep():
    """
    Main route to access stm32ai service
    """
    if os.environ.get(_BACKEND_EV_NAME.STM32AI_SERVICE_URL):
        return os.environ.get(_BACKEND_EV_NAME.STM32AI_SERVICE_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return _BACKEND_TEST_ENDPOINTS.STM32AI_SERVICE_URL
    else:
        return _BACKEND_ENDPOINTS.STM32AI_SERVICE_URL


def get_stm32ai_analyze_ep():
    return get_stm32ai_service_ep() + '/analyze'


def get_stm32ai_generate_ep():
    return get_stm32ai_service_ep() + '/generate'


def get_stm32ai_validate_ep():
    return get_stm32ai_service_ep() + '/validate'


def get_stm32ai_run(runtimeId: str):
    return get_stm32ai_service_ep()+f'/run/{runtimeId}'


def get_file_service_ep():
    """
    Main route to access the file service
    """
    if os.environ.get(_BACKEND_EV_NAME.FILE_SERVICE_URL):
        return os.environ.get(_BACKEND_EV_NAME.FILE_SERVICE_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return _BACKEND_TEST_ENDPOINTS.FILE_SERVICE_URL
    else:
        return _BACKEND_ENDPOINTS.FILE_SERVICE_URL


def get_benchmark_service_ep():
    """
    Main route to access benchmark service
    """
    if os.environ.get(_BACKEND_EV_NAME.BENCHMARK_SERVICE_URL):
        return os.environ.get(_BACKEND_EV_NAME.BENCHMARK_SERVICE_URL)

    if os.environ.get(USE_TEST_ROUTES_EV):
        return _BACKEND_TEST_ENDPOINTS.BENCHMARK_SERVICE_URL
    else:
        return _BACKEND_ENDPOINTS.BENCHMARK_SERVICE_URL


def get_benchmark_boards_ep():
    return f'{get_benchmark_service_ep()}/boards'


def get_benchmark_openapi_ep():
    return f'{get_benchmark_service_ep()}/api'
