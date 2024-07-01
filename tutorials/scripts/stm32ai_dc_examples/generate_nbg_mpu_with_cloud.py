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
- Get result of a tflite model through STM32MPU Optimization Tool
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
model_path = os.path.join(models_dir_path, 'mobilenet_v1_0.25_96_int8.tflite')

# Create STM32AI Class with Cloud Backend, given a username/password and a possible version
# Version set to "None" will use the latest version available in Developer Cloud
ai = Stm32Ai(CloudBackend(username, password, version=None))

try:
    # Upload a model
    ai.upload_model(model_path)
    # Extracting file basename
    model_name = os.path.basename(model_path)
    res = ai.generate_nbg(model_name)
    print("Optimized Model Name:", res)
    ai.download_model(res, './output/' + res)
except ModelNotFoundError:
    print('Model not found')