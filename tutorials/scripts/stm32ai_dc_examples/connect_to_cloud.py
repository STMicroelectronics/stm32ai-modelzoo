# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2023 STMicroelectronics. All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath('../../../common'))
from stm32ai_dc import Stm32Ai, CloudBackend

"""
Main Features
--------------------------------------------------------------------------------------------

- Login to STM32Cube.AI Developer Cloud
- Get user informations
"""

# Get username/password from your environment
username = os.environ.get('STM32AI_USERNAME', None)
password = os.environ.get('STM32AI_PASSWORD', None)

# Create STM32AI Class with Cloud Backend, given a username/password and a possible version
# Version set to "None" will use the latest version available in Developer Cloud
ai = Stm32Ai(CloudBackend(username, password, version=None))

# Get user informations
print(f"Connected to the cloud with user: {ai.get_user()}")
