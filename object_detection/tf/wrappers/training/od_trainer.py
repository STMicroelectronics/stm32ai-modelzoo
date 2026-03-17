# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from common.registries.trainer_registry import TRAINER_WRAPPER_REGISTRY

from object_detection.tf.src.training import ODTrainer

__all__ = ['ODTrainer']

# Register the trainer class from another folder
TRAINER_WRAPPER_REGISTRY.register(
    trainer_name="od_trainer",
    framework="tf",
    use_case="object_detection"
)(ODTrainer)
