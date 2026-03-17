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


activation_choice = "relu"

activation = {"relu" : nn.ReLU(inplace=True),
              "hswish" : nn.Hardswish(inplace=True) , 
              "silu" : nn.SiLU(inplace=True) ,
              }

class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, downsample=None, conv1_custom=None, conv2_custom=None):
        super(BasicBlock, self).__init__()

        self.conv1 = conv1_custom if conv1_custom is not None else nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.drop_block = nn.Identity()
        self.act1 = activation[activation_choice]
        self.aa = nn.Identity()

        self.conv2 = conv2_custom if conv2_custom is not None else nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.act2 = activation[activation_choice]

        self.downsample = downsample

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.drop_block(out)
        out = self.act1(out)
        out = self.aa(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.act2(out)

        return out

class STResNetMicro(nn.Module):

    def __init__(
        self,
        out_features=("dark3", "dark4", "dark5"),
    ):
        
        super().__init__()
        assert out_features, "please provide output features of STResNetMicro"
        self.out_features = out_features

        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 3, kernel_size=1, bias=False),
            nn.Conv2d(3, 8, kernel_size=7, stride=2, padding=3, bias=False),
            nn.Conv2d(8, 64, kernel_size=1, bias=False)
        )
        self.bn1 = nn.BatchNorm2d(64, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.act1 = activation[activation_choice]
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=1, ceil_mode=False)

        self.layer1 = nn.Sequential(
            BasicBlock(64, 64),
            BasicBlock(64, 64)
        )

        self.layer2 = nn.Sequential(
            BasicBlock(64, 128, stride=2,
                downsample=nn.Sequential(
                    nn.Conv2d(64, 128, kernel_size=1, stride=2, bias=False),
                    nn.BatchNorm2d(128)
                ),
                conv2_custom=nn.Sequential(
                    nn.Conv2d(128, 40, kernel_size=1, bias=False),
                    nn.Conv2d(40, 40, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(40, 128, kernel_size=1, bias=False)
                )
            ),
            BasicBlock(128, 128,
                conv1_custom=nn.Sequential(
                    nn.Conv2d(128, 88, kernel_size=1, bias=False),
                    nn.Conv2d(88, 88, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(88, 128, kernel_size=1, bias=False)
                ),
                conv2_custom=nn.Sequential(
                    nn.Conv2d(128, 32, kernel_size=1, bias=False),
                    nn.Conv2d(32, 32, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(32, 128, kernel_size=1, bias=False)
                )
            )
        )

        self.layer3 = nn.Sequential(
            BasicBlock(128, 256,
                stride=2,
                downsample=nn.Sequential(
                    nn.Sequential(
                        nn.Conv2d(128, 16, kernel_size=1, bias=False),
                        nn.Conv2d(16, 16, kernel_size=1, stride=2, bias=False),
                        nn.Conv2d(16, 256, kernel_size=1, bias=False)
                    ),
                    nn.BatchNorm2d(256)
                ),
                conv1_custom=nn.Sequential(
                    nn.Conv2d(128, 88, kernel_size=1, bias=False),
                    nn.Conv2d(88, 88, kernel_size=3, stride=2, padding=1, bias=False),
                    nn.Conv2d(88, 256, kernel_size=1, bias=False)
                ),
                conv2_custom=nn.Sequential(
                    nn.Conv2d(256, 72, kernel_size=1, bias=False),
                    nn.Conv2d(72, 72, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(72, 256, kernel_size=1, bias=False)
                )
            ),
            BasicBlock(256, 256,
                conv1_custom=nn.Sequential(
                    nn.Conv2d(256, 80, kernel_size=1, bias=False),
                    nn.Conv2d(80, 80, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(80, 256, kernel_size=1, bias=False)
                ),
                conv2_custom=nn.Sequential(
                    nn.Conv2d(256, 32, kernel_size=1, bias=False),
                    nn.Conv2d(32, 32, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(32, 256, kernel_size=1, bias=False)
                )
            )
        )

        self.layer4 = nn.Sequential(
            BasicBlock(256, 512,
                stride=2,
                downsample=nn.Sequential(
                    nn.Sequential(
                        nn.Conv2d(256, 24, kernel_size=1, bias=False),
                        nn.Conv2d(24, 24, kernel_size=1, stride=2, bias=False),
                        nn.Conv2d(24, 512, kernel_size=1, bias=False)
                    ),
                    nn.BatchNorm2d(512)
                ),
                conv1_custom=nn.Sequential(
                    nn.Conv2d(256, 80, kernel_size=1, bias=False),
                    nn.Conv2d(80, 80, kernel_size=3, stride=2, padding=1, bias=False),
                    nn.Conv2d(80, 512, kernel_size=1, bias=False)
                ),
                conv2_custom=nn.Sequential(
                    nn.Conv2d(512, 8, kernel_size=1, bias=False),
                    nn.Conv2d(8, 8, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(8, 512, kernel_size=1, bias=False)
                )
            ),
            BasicBlock(512, 512,
                conv1_custom=nn.Sequential(
                    nn.Conv2d(512, 72, kernel_size=1, bias=False),
                    nn.Conv2d(72, 72, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(72, 512, kernel_size=1, bias=False)
                ),
                conv2_custom=nn.Sequential(
                    nn.Conv2d(512, 64, kernel_size=1, bias=False),
                    nn.Conv2d(64, 64, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(64, 512, kernel_size=1, bias=False)
                )
            )
        )

        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(512, 1000)

  
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.global_pool(x)
        x = self.flatten(x)
        x = self.fc(x)
        
        return x
    
