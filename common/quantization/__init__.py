# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from .quant_utils import (get_weights_activations_quant_type, define_extra_options, get_calibration_method,
                          update_bit_width, count_weights, weights_based_layer_ranking, composite_score_layer_ranking)
from .quant_tools import tensors_inspection, onnx_tensor_names
from .onnx_quantizer import ImageDataReader, quantize_onnx