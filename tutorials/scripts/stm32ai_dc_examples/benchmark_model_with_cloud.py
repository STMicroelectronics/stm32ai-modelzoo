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
- Benchmark
- Get Benchmark Results
- Delete a model from your workspace
"""

import sys
import os
# Append sys.path in order to add import folder for STM32AI
dir_name = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(dir_name, '..')))
sys.path.append(os.path.abspath('../../../common'))
from stm32ai_dc.types import MpuParameters
from stm32ai_dc import Stm32Ai, CloudBackend, CliParameters
from stm32ai_dc.errors import ParameterError, BenchmarkServerError

# Get username/password from your environment
username = os.environ.get('STM32AI_USERNAME', None)
password = os.environ.get('STM32AI_PASSWORD', None)

# Upload a model available locally
models_dir_path = '../models'
model_path = os.path.join(models_dir_path, 'mobilenet_v1_0.25_96.h5')

# Create STM32AI Class with Cloud Backend, given a username/password and a possible version
# Version set to "None" will use the latest version available in Developer Cloud
ai = Stm32Ai(CloudBackend(username, password, version=None))

# List boards available for a benchmark in STM32Cube.AI Developer Cloud
boards = ai.get_benchmark_boards()
print(boards)

# Boards length should be greater than zero
# A length equals to zero mean a current maintenance or a failure
if len(boards) == 0:
    print("No board detected remotely, can't start benchmark")
    sys.exit(0)

# Benchmarking local model
# Upload a model
ai.upload_model(model_path)
# Extracting file basename
model_name = os.path.basename(model_path)

# Start benchmark with a board name from "board" object
try:
    res = ai.benchmark(CliParameters(model=model_name), 'STM32H747I-DISCO')
    # Print results
    print("Result from cloud file:", res)
    # Delete model
    ai.delete_model(model_name)
except ParameterError as e:
    print("An error occured while benchmarking your model", e)
except BenchmarkServerError as e:
    print("An error occured while running your  benchmark on our server", e)

# Start benchmark on MPU
try:
    res = ai.benchmark(MpuParameters(model=model_name), 'STM32MP257F-EV1')
    # Print results
    print("Result from cloud file:", res)
    # Delete model
    ai.delete_model(model_name)
except ParameterError as e:
    print("An error occured while benchmarking your model", e)
except BenchmarkServerError as e:
    print("An error occured while running your  benchmark on our server", e)