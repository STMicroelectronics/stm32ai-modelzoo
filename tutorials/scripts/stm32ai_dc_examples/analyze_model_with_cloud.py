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
- Analyze a model
- Get analyze results
- Delete a model from your workspace
"""


import sys
import os
# Append sys.path in order to add import folder for STM32AI
dir_name = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(dir_name, '..')))
sys.path.append(os.path.abspath('../../../common'))
from stm32ai_dc import Stm32Ai, CloudBackend, CliParameters, ModelNotFoundError

# Get username/password from your environment 
username = os.environ.get('STM32AI_USERNAME', None)
password = os.environ.get('STM32AI_PASSWORD', None)

# Upload a model available locally
models_dir_path = '../models'
model_path = os.path.join(models_dir_path, 'mobilenet_v1_0.25_96.h5')

# Create STM32AI Class with Cloud Backend, given a username/password and a possible version
# Version set to "None" will use the latest version available in Developer Cloud
ai = Stm32Ai(CloudBackend(username, password, version=None))

# Two options are available here
# - Analyze from a local file:
#       - If path is from your local filesystem, it will upload it in Dev. Cloud and execute the command
print("Result from local file:", ai.analyze(CliParameters(model=model_path)))
#       - Else, you can upload it will assume availability in your workspace and execute analysis given arguments set in CLI parameters
try:
    # Upload a model
    ai.upload_model(model_path)
    # Extracting file basename
    model_name = os.path.basename(model_path)
    print("Result from cloud file:", ai.analyze(CliParameters(model=model_name)))
except ModelNotFoundError:
    print('Model not found')

# Once you are done with your model, you can delete it
ai.delete_model(model_name)