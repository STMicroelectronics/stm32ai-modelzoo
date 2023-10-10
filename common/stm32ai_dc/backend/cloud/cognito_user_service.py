import requests
from requests.adapters import HTTPAdapter, Retry
from requests.structures import CaseInsensitiveDict

from stm32ai_dc.backend.cloud.helpers import get_ssl_verify_status, _get_env_proxy
from stm32ai_dc.backend.cloud.endpoints import get_user_service_ep

USER_SERVICE_MIN_VERSION = 0.0


class CognitoUserService:
    def __init__(self, auth_token) -> None:
        self.auth_token = auth_token
        self.main_route = get_user_service_ep()

        self.user_route = self.main_route + "/login/authenticate"

    def get_user(self) -> dict:
        toUrl = self.user_route
        withToken = self.auth_token
        usingParams = None

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {withToken}"

        s = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5)

        s.mount(toUrl, HTTPAdapter(max_retries=retries))

        resp = s.get(
            toUrl,
            headers=headers,
            verify=get_ssl_verify_status(),
            params=usingParams,
            proxies=_get_env_proxy(),
        )
        resp.raise_for_status()

        json_resp = resp.json()
        resp.close()
        if "sub" in json_resp and json_resp["sub"] != None:
            return json_resp
        else:
            return None
