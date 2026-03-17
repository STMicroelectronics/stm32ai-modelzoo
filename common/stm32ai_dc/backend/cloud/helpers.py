# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import os
import typing
import requests
from requests.adapters import HTTPAdapter, Retry
from requests.structures import CaseInsensitiveDict
from common.stm32ai_dc.backend.cloud.endpoints import get_supported_versions_ep
from common.stm32ai_dc.errors import ServerRouteNotFound


def get_ssl_verify_status():
    if os.environ.get('NO_SSL_VERIFY'):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return False
    else:
        return True


def get_main_route_api_version(main_route_url: str) -> float:
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(
        main_route_url,
        headers=headers,
        verify=get_ssl_verify_status(),
        proxies=_get_env_proxy())
    try:
        json_resp = resp.json()
        if json_resp['status'] == 'ok':
            api_info = json_resp['result']
            if not api_info:
                return 0
            if not api_info['apiVersion']:
                print(f"Warning: API main route ({main_route_url}) does not \
                    have an apiVersion field")
                return 0
            else:
                api_version = api_info['apiVersion']
                return api_version
        else:
            return 0
    except Exception:
        return 0


def _get_env_proxy():
    proxy_config = {}
    http_proxy = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')
    https_proxy = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')
    if http_proxy != None:
        proxy_config['http_proxy'] = http_proxy
    if https_proxy != None:
        proxy_config['https_proxy'] = https_proxy
    proxy_config = proxy_config if len(proxy_config) else None
    return proxy_config


def get_value_or_default(obj: typing.NamedTuple, key: str, default: any):
    try:
        return getattr(obj, key) if getattr(obj, key) is not None else default
    except Exception:
        return default


def send_get(
        toUrl: str,
        withToken: str,
        usingParams: dict = None) -> requests.Response:
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {withToken}"


    s = requests.Session()
    retries = Retry(total=5,
                backoff_factor=0.5)

    s.mount(toUrl, HTTPAdapter(max_retries=retries))

    resp = s.get(
        toUrl,
        headers=headers,
        verify=get_ssl_verify_status(),
        params=usingParams,
        proxies=_get_env_proxy(),
    )

    if resp.status_code == 404:
        raise ServerRouteNotFound(f"Trying to reach: {toUrl}")
    return resp


def send_post(
        toUrl: str,
        withToken: str,
        usingData: dict = None,
        usingFile: dict = None,
        usingJson=None) -> requests.Response:
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {withToken}"

    resp = requests.post(
        toUrl,
        headers=headers,
        verify=get_ssl_verify_status(),
        data=usingData,
        files=usingFile,
        json=usingJson,
        proxies=_get_env_proxy())
    return resp

def get_supported_versions():
    resp = requests.get(
        get_supported_versions_ep(),
        verify=get_ssl_verify_status(),
        proxies=_get_env_proxy())
    return resp.json()
