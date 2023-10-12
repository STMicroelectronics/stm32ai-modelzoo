# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


from json import JSONDecodeError, dump, load
from typing import Union
import requests
import html
import re
from urllib.parse import urlparse, parse_qs, urljoin
import os
import time
from pathlib import Path

from stm32ai_dc.errors import InvalidCredentialsException, LoginFailureException

from .helpers import get_ssl_verify_status, _get_env_proxy
from .endpoints import get_login_authenticate_ep, get_login_service_ep

LOGIN_SERVICE_MIN_VERSION = 0.0


class LoginService:
    def __init__(self) -> None:
        self.token_file = Path.joinpath(Path.home(), '.stmai_token')
        self.main_route = get_login_service_ep()
        # if get_main_route_api_version(self.main_route) < LOGIN_SERVICE_MIN_VERSION:
        # raise Exception(f"Error: Login service endpoint used is older ({get_main_route_api_version(self.main_route)}) than minimuim required version ({LOGIN_SERVICE_MIN_VERSION}). API may not work as expected.")

        self.authenticate_route = get_login_authenticate_ep()
        self.auth_token = None

    def get_access_token(self) -> Union[str, None]:
        sso_resp = self.read_token_from_storage()
        if (sso_resp['expires_at'] != None):
            date = time.time()
            expiration_date = sso_resp['expires_at'] * 1000
            if (expiration_date < date):
                # is expired
                refresh_resp = self.refresh()
                if (refresh_resp['access_token']):
                    return refresh_resp['access_token']
            else:
                return sso_resp['access_token']
        return None

    def refresh(self) -> Union[dict, None]:
        sso_resp = self.read_token_from_storage()
        if (sso_resp['refresh_token']):
            refresh_route = self.main_route + '/login/refresh'
            s = requests.session()
            s.proxies = _get_env_proxy()
            s.verify = get_ssl_verify_status()
            resp = s.post(refresh_route, data={
                'refresh_token': sso_resp['refresh_token']
            })
            json_resp = resp.json()
            if (json_resp['sub']):
                self.save_token_response(json_resp)
                return json_resp
        return None

    def save_token_response(self, token) -> bool:
        with open(self.token_file, 'w') as f:
            dump(token, f)

    def read_token_from_storage(self) -> Union[dict, None]:
        if (os.path.exists(self.token_file) == False):
            return None
        f = open(self.token_file, 'r')
        token = load(f)
        return token

    def login(self, username, password) -> str:
        for i in range(5):
            try:
                self._login(username, password)
                return self.auth_token
            except InvalidCredentialsException as e:
                raise e
            except Exception as e:
                print('Login issue, retry (' + str(i+1) + '/5)')
                time.sleep(5)


    def _login(self, username, password) -> str:
        # Starts a requests sesson
        s = requests.session()
        s.proxies = _get_env_proxy()
        s.verify = get_ssl_verify_status()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv59.0) Gecko/20100101',
        })
        provider = 'https://sso.st.com'
        client_id = 'oidc_prod_client_app_stm32ai'
        redirect_uri = 'https://stm32ai-cs.st.com/callback'

        # Get connection initialization procedure
        resp = s.get(
            url=provider + "/as/authorization.oauth2",
            params={
                "response_type": "code",
                "client_id": client_id,
                "scope": "openid",
                "redirect_uri": redirect_uri,
                "response_mode": "query"
            },
            allow_redirects=True,
        )

        # Continue through my.st.com website
        # resp = s.get(
        #     url=resp.headers["Location"],
        #     allow_redirects=True,
        # )

        page = resp.text

        # Find POST URL
        form_action = html.unescape(
            re.search('<form\s+.*?\s+action="(.*?)"', page, re.DOTALL).group(1))

        # Find LT value. This is required by my.st.com in order to perform login
        lt_value = html.unescape(
            re.search('<input.*name="lt".*value="(.*)" />', page).group(1))

        parsed_url = urlparse(resp.url)
        # Construct Login URL = https://my.st.com/cas/login/......
        login_url = urljoin(parsed_url.scheme + "://" +
                            parsed_url.netloc, form_action)
        resp = s.post(
            url=login_url,
            data={
                "username": username,
                "password": password,
                "_eventId": "Login",
                "lt": lt_value
            },
            allow_redirects=False,
        )

        if (resp.status_code == 200):
            failure_regex = re.search(r'You have provided the wrong password. You have \d+ attempts left after which your account password will expire.', resp.text)
            if (failure_regex):
                raise InvalidCredentialsException

        redirect = resp.headers['Location']
        is_ready = False
        while is_ready == False:
            resp = s.get(
                url=redirect,
                allow_redirects=False,
            )
            status_code = resp.status_code
            # While redirection, follow redirect, until redirection starts with our needed URL (stm32ai-cs.st.com)
            if status_code == 302:
                redirect = resp.headers['Location']
                is_ready = redirect.startswith(redirect_uri)
            else:
                is_ready = True

        # Retrieve params from redirect URL
        query = urlparse(redirect).query
        redirect_params = parse_qs(query)

        # Expect to have a "code" value in this redirection. We won't follow the redirect but we will instead do manually thre request
        auth_code = redirect_params['code'][0]

        # Get tokens with POST endpoint

        resp = s.post(
            url='https://stm32ai-cs.st.com/api/user_service/login/callback',
            data={
                "redirect_url": redirect_uri,
                "code": auth_code
            },
            allow_redirects=False,
            verify=get_ssl_verify_status(),
            proxies=_get_env_proxy(),
        )

        # Response should be 200
        assert (resp.status_code == 200)

        # Token is stored in response as JSON
        try:
            json_resp = resp.json()
            if json_resp['access_token']:
                # Connection has correctly been done, continue
                self.save_token_response(json_resp)
                self.auth_token = json_resp['access_token']
                return self.auth_token
            else:
                raise LoginFailureException(
                    self.username, self.password, details=f"Authentication server did not succeed: {resp}")
        except JSONDecodeError as e:
            raise LoginFailureException(
                self.username, self.password, 'Error while decoding server reply')

        # resp = requests.post(self.authenticate_route, {
        #     "username": self.username,
        #     "password": self.password
        # }, verify=get_ssl_verify_status(), proxies=_get_env_proxy())
        # try:
        #     json_resp = resp.json()
        #     if json_resp['status'] == 'ok':
        #         jwt_token = json_resp['result']
        #         if not jwt_token:
        #             raise LoginFailureException(self.username, self.password, details='Authentication token is empty. Check your credentials.')
        #         self.auth_token = jwt_token
        #         return jwt_token
        #     else:
        #         raise LoginFailureException(self.username, self.password, details=f"Authentication server did not succeed: {resp}")
        # except  JSONDecodeError as e:
        #     raise LoginFailureException(self.username, self.password, 'Error while decoding server reply')
