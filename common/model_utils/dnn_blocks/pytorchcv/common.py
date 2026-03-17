# ---------------------------------------------------------------------------------------------
# Copyright (c) 2025 STMicroelectronics.
# All rights reserved.
#
# Copyright (c) 2018-2024 Oleg Sémery
#
# This software is licensed under terms that can be found in the LICENSE file in
# the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.
# Taken from: https://github.com/osmr/imgclsmob
# ---------------------------------------------------------------------------------------------
import torch
import torch.nn as nn


def channel_shuffle(x, groups):
    """
    Channel shuffle operation from 'ShuffleNet: An Extremely Efficient Convolutional Neural
    Network for Mobile Devices,' https://arxiv.org/abs/1707.01083.
    Parameters:
    ----------
    x : Tensor
        Input tensor.
    groups : int
        Number of groups.
    Returns:
    -------
    Tensor
        Resulted tensor.
    """
    batch, channels, height, width = x.size()
    # assert (channels % groups == 0)
    channels_per_group = channels // groups
    x = x.view(batch, groups, channels_per_group, height, width)
    x = torch.transpose(x, 1, 2).contiguous()
    x = x.view(batch, channels, height, width)
    return x


class ChannelShuffle(nn.Module):
    """
    Channel shuffle layer. This is a wrapper over the same operation. It is designed to save the number of groups.
    Parameters:
    ----------
    channels : int
        Number of channels.
    groups : int
        Number of groups.
    """

    def __init__(self, channels, groups):
        super(ChannelShuffle, self).__init__()
        if channels % groups != 0:
            raise ValueError("channels must be divisible by groups")
        self.groups = groups

    def forward(self, x):
        return channel_shuffle(x, self.groups)

    def __repr__(self):
        s = "{name}(groups={groups})"
        return s.format(name=self.__class__.__name__, groups=self.groups)
