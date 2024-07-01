# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow import keras

import larq as lq
from larq import utils
import numpy as np


@utils.register_keras_custom_object
class STCustomDoReFa(lq.quantizers.DoReFaQuantizer):
    """
    Custom implementation of the DoReFa quantizer based on Larq library implementation of DoReFa

    Args:

    Returns:
        An object to be inserted in the network graph each time we want to instanciate a STCustomDoReFa quantizer.
    """
    precision = None

    def __init__(self, k_bit: int = 8, mode: str = "activations", **kwargs):
        """
            Constructor for STCustomDoReFa class

            Args:
                k_bit: quantizer bit width
                mode: can be either 'activations' or 'weights' because the quantizer is different for weights and activations

            Returns:
                A STCustomDoReFa quantizer object for 'weights' or 'activations' for the specified bit width.
        """
        self.precision = k_bit

        if mode not in ("activations", "weights"):
            raise ValueError(
                f"Invalid DoReFa quantizer mode {mode}. "
                "Valid values are 'activations' and 'weights'."
            )
        self.mode = mode

        super().__init__(k_bit=k_bit, mode=mode, **kwargs)

    def weight_preprocess(self, inputs):
        """
            Implements mathematical transformation of the weights for DoReFa quantization

            Args:
                inputs: weights tensor

            Returns:
                DoReFa transformed weights.
        """
        # Limit inputs to [-1, 1] range
        limited = tf.math.tanh(inputs)

        # Divider for max-value norm.
        dividend = tf.math.reduce_max(tf.math.abs(limited))

        # Need to stop the gradient here. Otherwise, for the maximum element,
        # which gives the dividend, normed is limited/limited (for this one
        # maximum digit). The derivative of y = x/x, dy/dx is just zero, when
        # one does the simplification y = x/x = 1. But TF does NOT do this
        # simplification when computing the gradient for the
        # normed = limited/dividend operation. As a result, this gradient
        # becomes complicated, because during the computation, "dividend" is
        # not just a constant, but depends on "limited" instead. Here,
        # tf.stop_gradient is used to mark "dividend" as a constant explicitly.
        dividend = tf.stop_gradient(dividend)

        # Norm and then scale from value range [-1,1] to [0,1] (the range
        # expected by the core quantization operation).
        # If the dividend used for the norm operation is 0, all elements of
        # the weight tensor are 0 and divide_no_nan returns 0 for all weights.
        # So if all elements of the weight tensor are zero, nothing is normed.
        return tf.math.divide_no_nan(limited, 2.0 * dividend) + 0.5

    def call(self, inputs):
        """
            Actual quantization of weights or activations

            Args:
                inputs: weights or activation tensor

            Returns:
                Tensor with quantized weights or activation
        """
        # Depending on quantizer mode (activation or weight) just clip inputs
        # on [0, 1] range or use weight preprocessing method.
        if self.mode == "activations":
            inputs = tf.clip_by_value(inputs, -1.0, 1.0 - 1 / 2 ** (self.precision - 1.0))
        elif self.mode == "weights":
            inputs = self.weight_preprocess(inputs)
        else:
            raise ValueError(
                f"Invalid DoReFa quantizer mode {self.mode}. "
                "Valid values are 'activations' and 'weights'."
            )

        if self.mode == "activations":
            @tf.custom_gradient
            def _k_bit_with_identity_grad_act(x):
                n = 2 ** (self.precision - 1)
                return tf.round(x * n) / n, lambda dy: dy

            outputs = _k_bit_with_identity_grad_act(inputs)
        elif self.mode == "weights":
            @tf.custom_gradient
            def _k_bit_with_identity_grad_weights(x):
                # symetric quantization
                n = 2 ** self.precision - 2
                return tf.round(x * n) / n, lambda dy: dy

            outputs = _k_bit_with_identity_grad_weights(inputs)
            outputs = 2.0 * outputs - 1.0

        return outputs

    def get_config(self):
        return {**super().get_config(), "k_bit": self.precision, "mode": self.mode}

