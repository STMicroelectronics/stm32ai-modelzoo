# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import torch.nn as nn


from common.utils import LOGGER


# Mish is removed from this list
ST_ACT_TYPES = {
    'relu': nn.ReLU(inplace=True),
    'relu6': nn.ReLU6(inplace=True),
    'hswish': nn.Hardswish(inplace=True),
    'hardswish': nn.Hardswish(inplace=True),
    'silu': nn.SiLU(inplace=True),
    'lrelu': nn.LeakyReLU(0.1, inplace=True),
    'hsigmoid': nn.Hardsigmoid(inplace=True),
    'sigmoid': nn.Sigmoid(),
    'leakyrelu': nn.LeakyReLU(negative_slope=0.1, inplace=True),
    'leakyrelu_0.1': nn.LeakyReLU(negative_slope=0.1, inplace=True),
    'gelu': nn.GELU(),
}


def get_activation(activation_name):
    if activation_name:
        return ST_ACT_TYPES[activation_name]
    LOGGER.debug('No activation specified for get_activation. Returning nn.Identity()')
    return nn.Identity()


def autopad(k, p=None, d=1):  # kernel, padding, dilation
    # Pad to 'same' shape outputs
    if d > 1:
        k = (
            d * (k - 1) + 1 if isinstance(k, int) else [d * (x - 1) + 1 for x in k]
        )  # actual kernel-size
    if p is None:
        p = k // 2 if isinstance(k, int) else [x // 2 for x in k]  # auto-pad
    return p


def round_channels(channels, divisor=8):
    rounded_channels = max(int(channels + divisor / 2.0) // divisor * divisor, divisor)
    if float(rounded_channels) < 0.9 * channels:
        rounded_channels += divisor
    return rounded_channels


