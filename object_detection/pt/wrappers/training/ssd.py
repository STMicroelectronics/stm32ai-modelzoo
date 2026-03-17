# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from common.registries.trainer_registry import TRAINER_WRAPPER_REGISTRY
from object_detection.pt.src.training.ssd.trainer import SSDTrainer

TRAINER_WRAPPER_REGISTRY.register(trainer_name="ssd", framework="torch", use_case="object_detection")(SSDTrainer)
