# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from .keras_evaluator import KerasModelEvaluator
from .onnx_evaluator import ONNXModelEvaluator
from .tflite_evaluator import TFLiteQuantizedModelEvaluator
