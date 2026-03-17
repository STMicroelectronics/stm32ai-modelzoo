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
import torch
import torch.nn as nn
import torch.nn.functional as F

activation_choice = "silu"

activation = {"relu" : nn.ReLU(inplace=True),
              "hswish" : nn.Hardswish(inplace=True) , 
              "silu" : nn.SiLU(inplace=True) ,
              }

class BasicBlock(nn.Module):
    def __init__(self, inplanes, planes, stride=1, conv1_cfg=None, conv2_cfg=None, downsample=None):
        super().__init__()

        # conv1 as Sequential Tucker-style block
        self.conv1 = self._make_seq(inplanes, conv1_cfg if conv1_cfg else [(inplanes, planes, 3, stride, 1)])
        self.bn1 = nn.BatchNorm2d(planes)
        self.drop_block = nn.Identity()
        self.act1 = activation[activation_choice]
        self.aa = nn.Identity()

        # conv2 as Sequential Tucker-style block
        self.conv2 = self._make_seq(planes, conv2_cfg if conv2_cfg else [(planes, planes, 3, 1, 1)])
        self.bn2 = nn.BatchNorm2d(planes)
        self.act2 = activation[activation_choice]

        self.downsample = downsample

    def _make_seq(self, in_ch, cfg):
        """
        cfg = [(in_c, out_c, k, s, p), ...]
        """
        layers = []
        for (c_in, c_out, k, s, p) in cfg:
            layers.append(nn.Conv2d(c_in, c_out, kernel_size=k, stride=s, padding=p, bias=False))
        return nn.Sequential(*layers)

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.act1(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.act2(out)
        return out


class STResNetPico(nn.Module):
    def __init__(
        self,
        out_features=("dark3", "dark4", "dark5"),
    ):
        
        super(STResNetPico, self).__init__()
        assert out_features, "please provide output features of STResNetMicro"
        self.out_features = out_features

        # stem
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 3, kernel_size=1, stride=1, bias=False),
            nn.Conv2d(3, 8, kernel_size=7, stride=2, padding=3, bias=False),
            nn.Conv2d(8, 32, kernel_size=1, stride=1, bias=False),
        )
        self.bn1 = nn.BatchNorm2d(32)
        self.act1 = activation[activation_choice]
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.proj = nn.Conv2d(32, 64, kernel_size=1, stride=1, bias=False)

        # layer1
        self.layer1 = nn.Sequential(
            BasicBlock(64, 64,
                       conv1_cfg=[(64, 24, 1, 1, 0), (24, 24, 3, 1, 1), (24, 64, 1, 1, 0)],
                       conv2_cfg=[(64, 16, 1, 1, 0), (16, 16, 3, 1, 1), (16, 64, 1, 1, 0)]),
            BasicBlock(64, 64,
                       conv1_cfg=[(64, 24, 1, 1, 0), (24, 24, 3, 1, 1), (24, 64, 1, 1, 0)],
                       conv2_cfg=[(64, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 64, 1, 1, 0)]),
        )

        # layer2
        self.layer2 = nn.Sequential(
            BasicBlock(64, 128, stride=2,
                       conv1_cfg=[(64, 24, 1, 1, 0), (24, 24, 3, 2, 1), (24, 128, 1, 1, 0)],
                       conv2_cfg=[(128, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 128, 1, 1, 0)],
                       downsample=nn.Sequential(
                           nn.Sequential(
                               nn.Conv2d(64, 8, kernel_size=1, stride=1, bias=False),
                               nn.Conv2d(8, 8, kernel_size=1, stride=2, bias=False),
                               nn.Conv2d(8, 128, kernel_size=1, stride=1, bias=False),
                           ),
                           nn.BatchNorm2d(128),
                       )),
            BasicBlock(128, 128,
                       conv1_cfg=[(128, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 128, 1, 1, 0)],
                       conv2_cfg=[(128, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 128, 1, 1, 0)]),
        )

        # layer3
        self.layer3 = nn.Sequential(
            BasicBlock(128, 256, stride=2,
                       conv1_cfg=[(128, 8, 1, 1, 0), (8, 8, 3, 2, 1), (8, 256, 1, 1, 0)],
                       conv2_cfg=[(256, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 256, 1, 1, 0)],
                       downsample=nn.Sequential(
                           nn.Sequential(
                               nn.Conv2d(128, 8, kernel_size=1, stride=1, bias=False),
                               nn.Conv2d(8, 8, kernel_size=1, stride=2, bias=False),
                               nn.Conv2d(8, 256, kernel_size=1, stride=1, bias=False),
                           ),
                           nn.BatchNorm2d(256),
                       )),
            BasicBlock(256, 256,
                       conv1_cfg=[(256, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 256, 1, 1, 0)],
                       conv2_cfg=[(256, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 256, 1, 1, 0)]),
        )

        # layer4
        self.layer4 = nn.Sequential(
            BasicBlock(256, 512, stride=2,
                       conv1_cfg=[(256, 8, 1, 1, 0), (8, 8, 3, 2, 1), (8, 512, 1, 1, 0)],
                       conv2_cfg=[(512, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 512, 1, 1, 0)],
                       downsample=nn.Sequential(
                           nn.Sequential(
                               nn.Conv2d(256, 8, kernel_size=1, stride=1, bias=False),
                               nn.Conv2d(8, 8, kernel_size=1, stride=2, bias=False),
                               nn.Conv2d(8, 512, kernel_size=1, stride=1, bias=False),
                           ),
                           nn.BatchNorm2d(512),
                       )),
            BasicBlock(512, 512,
                       conv1_cfg=[(512, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 512, 1, 1, 0)],
                       conv2_cfg=[(512, 8, 1, 1, 0), (8, 8, 3, 1, 1), (8, 512, 1, 1, 0)]),
        )



    def forward(self, x):
        outputs = {}
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.maxpool(x)
        x = self.proj(x)
        
        outputs["stem"] = x
        x = self.layer1(x)
        outputs["dark2"] = x
        x = self.layer2(x)
        outputs["dark3"] = x
        x = self.layer3(x)
        outputs["dark4"] = x
        x = self.layer4(x)
        outputs["dark5"] = x
        return {k: v for k, v in outputs.items() if k in self.out_features}