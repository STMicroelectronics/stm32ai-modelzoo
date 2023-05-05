# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE
#  * file in the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


"""
Main Features
--------------------------------------------------------------------------------------------

- Login to STM32Cube.AI Developer Cloud
- Upload a model
- Generate C Code from a model on a given STM32 Serie

"""

import sys
import os
dir_name = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(dir_name, '..')))
sys.path.append(os.path.abspath('../../../common'))
from stm32ai_dc import Stm32Ai, CloudBackend, CliParameters, ModelNotFoundError
from stm32ai_dc import CliLibrarySerie, CliLibraryIde

# Get username/password from your environment
username = os.environ.get('STM32AI_USERNAME', None)
password = os.environ.get('STM32AI_PASSWORD', None)

# Create STM32AI Class with Cloud Backend, given a username/password and a possible version
# Version set to "None" will use the latest version available in Developer Cloud
ai = Stm32Ai(CloudBackend(username, password, version=None))

# Get model from "models" folder
models_dir_path = '../models'
model_path = os.path.join(models_dir_path, 'mobilenet_v1_0.25_96.h5')

# Generate model using local file and get Runtime library
# Multiple STM32 Series are supported
# IDE Libraries are GCC, IAR, Keil
# Output folder is $PWD/output_01
res = ai.generate(CliParameters(
    model=model_path,
    includeLibraryForSerie=CliLibrarySerie.STM32H7,
    includeLibraryForIde=CliLibraryIde.IAR,
    output='./output_01'
    ))
print("Result from local file:", res, flush=True)

# Generate from a model uploaded to the cloud
ai.upload_model(model_path)
model_name = os.path.basename(model_path)
print("Result from cloud file:", ai.generate(
        CliParameters(model=model_name, output='./output_02')), flush=True)
ai.delete_model(model_name)

# Generate with an unknown model throws exception
try:
    ai.generate(CliParameters(model="not_existing_model.h5"))
except ModelNotFoundError:
    print("Unknown model correctly raised error")
