# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBNAct(nn.Module):
    """Conv → BN → SiLU"""
    def __init__(self, in_ch, out_ch, k=3, s=1, p=1):
        super().__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, k, s, p, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
        self.act = nn.SiLU(inplace=True)

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))



class YOLOv11PAFPN(nn.Module):
    """
    YOLOv11 PAN-FPN style neck with configurable out_channels.
    Takes backbone features [C3, C4, C5] and outputs [P3, P4, P5].
    """
    def __init__(self, channels=[128, 256, 512], out_channels=[64, 128, 256]):
        super().__init__()

        c3, c4, c5 = channels
        p3, p4, p5 = out_channels

        # Top-down path
        self.reduce_conv_c5 = ConvBNAct(c5, p5, 1, 1, 0)
        self.reduce_conv_c4 = ConvBNAct(c4, p4, 1, 1, 0)
        self.reduce_conv_c3 = ConvBNAct(c3, p3, 1, 1, 0)

        # Feature fusion
        self.upsample = nn.Upsample(scale_factor=2, mode="nearest")

        # After fusion convs
        self.fuse_p4 = ConvBNAct(p5 + p4, p4, 3, 1, 1)
        self.fuse_p3 = ConvBNAct(p4 + p3, p3, 3, 1, 1)

        # Bottom-up path
        self.downsample_p3 = ConvBNAct(p3, p3, 3, 2, 1)
        self.fuse_p4_out = ConvBNAct(p3 + p4, p4, 3, 1, 1)

        self.downsample_p4 = ConvBNAct(p4, p4, 3, 2, 1)
        self.fuse_p5_out = ConvBNAct(p4 + p5, p5, 3, 1, 1)

    def forward(self, feats):
        c3, c4, c5 = feats["dark3"], feats["dark4"], feats["dark5"]
        # Top-down
        p5 = self.reduce_conv_c5(c5)         # 256
        p4 = self.fuse_p4(torch.cat([self.upsample(p5), self.reduce_conv_c4(c4)], dim=1))  # 128
        p3 = self.fuse_p3(torch.cat([self.upsample(p4), self.reduce_conv_c3(c3)], dim=1))  # 64

        # Bottom-up
        p4_out = self.fuse_p4_out(torch.cat([self.downsample_p3(p3), p4], dim=1))  # 128
        p5_out = self.fuse_p5_out(torch.cat([self.downsample_p4(p4_out), p5], dim=1))  # 256

        return p3, p4_out, p5_out


