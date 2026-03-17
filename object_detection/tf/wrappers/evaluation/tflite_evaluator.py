# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from common.registries.evaluator_registry import EVALUATOR_WRAPPER_REGISTRY

from object_detection.tf.src.evaluation.tflite_evaluator import TFLiteQuantizedModelEvaluator

__all__ = ['TFLiteQuantizedModelEvaluator']

# Register the TFLite Evaluator class from another folder
EVALUATOR_WRAPPER_REGISTRY.register(
    evaluator_name="tflite_evaluator",
    framework="tf",
    use_case="object_detection"
)(TFLiteQuantizedModelEvaluator)

