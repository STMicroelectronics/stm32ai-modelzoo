# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


from .helpers import get_main_route_api_version, send_get, send_post
from .endpoints import get_user_service_ep

USER_SERVICE_MIN_VERSION = 0.0


class UserService:
    def __init__(self, auth_token) -> None:
        self.auth_token = auth_token
        self.main_route = get_user_service_ep()

        # if get_main_route_api_version(self.main_route) < \
        #         USER_SERVICE_MIN_VERSION:
        #     raise Exception(f"Error: User service endpoint used is older \
        #         ({get_main_route_api_version(self.main_route)}) than minimuim \
        #             required version ({USER_SERVICE_MIN_VERSION}). API may \
        #                 not work as expected.")
        self.user_route = self.main_route + '/login/authenticate'

    def get_user(self) -> dict:
        resp = send_post(self.user_route, self.auth_token, {
            "access_token": self.auth_token
        })

        json_resp = resp.json()
        resp.close()
        if json_resp['sub'] != None:
            return json_resp
        else:
            return None
