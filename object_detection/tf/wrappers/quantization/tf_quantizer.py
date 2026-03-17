# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from common.registries.quantizer_registry import QUANTIZER_WRAPPER_REGISTRY

from object_detection.tf.src.quantization.tf_quantizer import TFLitePTQQuantizer

__all__ = ['TFLitePTQQuantizer']

# Register the TF PTQ Quantizer class from another folder
QUANTIZER_WRAPPER_REGISTRY.register(
    quantizer_name="tflite_converter",
    framework="tf",
    use_case="object_detection"
)(TFLitePTQQuantizer)

