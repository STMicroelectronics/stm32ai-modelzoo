# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


from .helpers import get_main_route_api_version, get_ssl_verify_status
from .helpers import send_get, send_post, _get_env_proxy
from .endpoints import get_file_service_ep
import requests
from requests.structures import CaseInsensitiveDict
import os

FILE_SERVICE_MIN_VERSION = 0.0


class FileService:
    def __init__(self, auth_token) -> None:
        self.auth_token = auth_token
        self.main_route = get_file_service_ep()
        self.models_route = self.main_route + '/files/models'
        self.validation_input_file_route = \
            self.main_route + '/files/validation/inputs'
        self.validation_outputs_file_route = \
            self.main_route + '/files/validation/outputs'
        self.generated_files_route = self.main_route + '/files/generated'

        # if get_main_route_api_version(self.main_route) < \
        #         FILE_SERVICE_MIN_VERSION:
        #     raise Exception(f"Error: File service endpoint used is older\
        #          ({get_main_route_api_version(self.main_route)}) than \
        #             minimuim required version ({FILE_SERVICE_MIN_VERSION}).\
        #                  API may not work as expected.")

    def _listFiles(self, path):
        resp = send_get(toUrl=path, withToken=self.auth_token)
        json_resp = resp.json()
        resp.close()

        if isinstance(json_resp, list):
            return json_resp
        else:
            return None

    def list_models(self):
        return self._listFiles(self.models_route)

    def listValidationInputFiles(self):
        return self._listFiles(self.validation_input_file_route)

    def listValidationOutputFiles(self):
        return self._listFiles(self.validation_outputs_file_route)

    def list_generated_files(self):
        return self._listFiles(self.generated_files_route)

    def _uploadFileTo(self, filePath, toRoute):
        files = {'file': open(filePath, 'rb')}
        resp = send_post(
            toUrl=toRoute,
            withToken=self.auth_token,
            usingFile=files)

        if resp.status_code == 200:
            json_resp = resp.json()
            if 'upload' in json_resp:
                if json_resp['upload'] is True:
                    return True
                else:
                    print('Error your file was not uploaded')
                    return False
            else:
                print(f'Error server does not reply \
                    expected reply: {json_resp}')
                return False
        else:
            print(f"Error server reply with {resp.status_code} HTTP code")
            return False

    def download_model(self, model_name, model_path):
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {self.auth_token}"

        resp = requests.get(
            url=f'{self.models_route}/{model_name}',
            headers=headers,
            verify=get_ssl_verify_status(),
            proxies=_get_env_proxy(),
            stream=True)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, mode="wb") as file:
            for chunk in resp.iter_content(chunk_size=10 * 1024):
                file.write(chunk)

    def upload_model(self, modelPath):
        return self._uploadFileTo(modelPath, toRoute=self.models_route)

    def upload_validation_input_file(self, filePath):
        return self._uploadFileTo(
            filePath,
            toRoute=self.validation_input_file_route)

    def upload_validation_output_file(self, filePath):
        return self._uploadFileTo(
            filePath,
            toRoute=self.validation_outputs_file_route)

    def _deleteFileFrom(self, fromRoute):
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {self.auth_token}"

        resp = requests.delete(
            fromRoute,
            headers=headers,
            verify=get_ssl_verify_status(),
            proxies=_get_env_proxy())

        json_resp = resp.json()
        resp.close()

        if resp.status_code == 200:
            if 'deleted' in json_resp:
                if json_resp['deleted'] is True:
                    return True
                else:
                    print('Error your file was not deleted')
                    return False
            else:
                print(f'Error server does not reply expected reply\
                    : {json_resp}')
                return False
        else:
            print(f"Error server reply with {resp.status_code} HTTP code")
            return False

    def delete_model(self, modelName):
        return self._deleteFileFrom(f'{self.models_route}/{modelName}')

    def deleteValidationInputFile(self, modelName):
        return self._deleteFileFrom(
            f'{self.validation_input_file_route}/{modelName}')

    def deleteValidationOutputFile(self, modelName):
        return self._deleteFileFrom(
            f'{self.validation_outputs_file_route}/{modelName}')

    def _download_file(self, url: str, to_local_filepath: str) -> str:
        """
            Download file from any URL and return the
            local file path or raise Error
        """
        if url.startswith('/'):
            url = url[1:]
        resp = send_get(url, self.auth_token)
        if resp.status_code == 200:
            # if resp.headers.get('Content-Type', None) == 'application/zip':
            with open(to_local_filepath, 'wb') as f:
                f.write(resp.content)
                f.close()
            return to_local_filepath
        else:
            raise Exception("FileService return non 200 HTTP code")

    def download_generated_file(
            self,
            filename: str,
            to_local_path: str) -> str:

        # If get full server path extract only filename
        base_name = os.path.basename(filename)
        os.makedirs(os.path.dirname(to_local_path), exist_ok=True)
        return self._download_file(
            f"{self.generated_files_route}/{base_name}",
            os.path.join(to_local_path, base_name))
