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

activation_choice = "relu"

activation = {"relu" : nn.ReLU(inplace=True),
              "hswish" : nn.Hardswish(inplace=True) , 
              "silu" : nn.SiLU(inplace=True) ,
              }

# ---- BasicBlock definition ----
class BasicBlock(nn.Module):
    def __init__(self, conv1, bn1, conv2, bn2, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv1
        self.bn1 = bn1
        self.drop_block = nn.Identity()
        
        # self.act1 = nn.ReLU(inplace=True)
        self.act1 = activation[activation_choice]
        self.aa = nn.Identity()
        self.conv2 = conv2
        self.bn2 = bn2
        # self.act2 = nn.ReLU(inplace=True)
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



class STResNetNano(nn.Module):
    
    def __init__(
        self,
        out_features=("dark3", "dark4", "dark5"),
    ):
        
        super(STResNetNano, self).__init__()
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
            BasicBlock(
                conv1=nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, bias=False),
                bn1=nn.BatchNorm2d(64),
                conv2=nn.Sequential(
                    nn.Conv2d(64, 32, kernel_size=1, bias=False),
                    nn.Conv2d(32, 32, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(32, 64, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(64),
            ),
            BasicBlock(
                conv1=nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1, bias=False),
                bn1=nn.BatchNorm2d(64),
                conv2=nn.Sequential(
                    nn.Conv2d(64, 40, kernel_size=1, bias=False),
                    nn.Conv2d(40, 40, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(40, 64, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(64),
            ),
        )

        # layer2
        self.layer2 = nn.Sequential(
            BasicBlock(
                conv1=nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False),
                bn1=nn.BatchNorm2d(128),
                conv2=nn.Sequential(
                    nn.Conv2d(128, 32, kernel_size=1, bias=False),
                    nn.Conv2d(32, 32, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(32, 128, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(128),
                downsample=nn.Sequential(
                    nn.Conv2d(64, 128, kernel_size=1, stride=2, bias=False),
                    nn.BatchNorm2d(128),
                ),
            ),
            BasicBlock(
                conv1=nn.Sequential(
                    nn.Conv2d(128, 64, kernel_size=1, bias=False),
                    nn.Conv2d(64, 64, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(64, 128, kernel_size=1, bias=False),
                ),
                bn1=nn.BatchNorm2d(128),
                conv2=nn.Sequential(
                    nn.Conv2d(128, 16, kernel_size=1, bias=False),
                    nn.Conv2d(16, 16, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(16, 128, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(128),
            ),
        )

        # layer3
        self.layer3 = nn.Sequential(
            BasicBlock(
                conv1=nn.Sequential(
                    nn.Conv2d(128, 48, kernel_size=1, bias=False),
                    nn.Conv2d(48, 48, kernel_size=3, stride=2, padding=1, bias=False),
                    nn.Conv2d(48, 256, kernel_size=1, bias=False),
                ),
                bn1=nn.BatchNorm2d(256),
                conv2=nn.Sequential(
                    nn.Conv2d(256, 16, kernel_size=1, bias=False),
                    nn.Conv2d(16, 16, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(16, 256, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(256),
                downsample=nn.Sequential(
                    nn.Sequential(
                        nn.Conv2d(128, 8, kernel_size=1, bias=False),
                        nn.Conv2d(8, 8, kernel_size=1, stride=2, bias=False),
                        nn.Conv2d(8, 256, kernel_size=1, bias=False),
                    ),
                    nn.BatchNorm2d(256),
                ),
            ),
            BasicBlock(
                conv1=nn.Sequential(
                    nn.Conv2d(256, 48, kernel_size=1, bias=False),
                    nn.Conv2d(48, 48, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(48, 256, kernel_size=1, bias=False),
                ),
                bn1=nn.BatchNorm2d(256),
                conv2=nn.Sequential(
                    nn.Conv2d(256, 8, kernel_size=1, bias=False),
                    nn.Conv2d(8, 8, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(8, 256, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(256),
            ),
        )

        # layer4
        self.layer4 = nn.Sequential(
            BasicBlock(
                conv1=nn.Sequential(
                    nn.Conv2d(256, 32, kernel_size=1, bias=False),
                    nn.Conv2d(32, 32, kernel_size=3, stride=2, padding=1, bias=False),
                    nn.Conv2d(32, 512, kernel_size=1, bias=False),
                ),
                bn1=nn.BatchNorm2d(512),
                conv2=nn.Sequential(
                    nn.Conv2d(512, 8, kernel_size=1, bias=False),
                    nn.Conv2d(8, 8, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(8, 512, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(512),
                downsample=nn.Sequential(
                    nn.Sequential(
                        nn.Conv2d(256, 8, kernel_size=1, bias=False),
                        nn.Conv2d(8, 8, kernel_size=1, stride=2, bias=False),
                        nn.Conv2d(8, 512, kernel_size=1, bias=False),
                    ),
                    nn.BatchNorm2d(512),
                ),
            ),
            BasicBlock(
                conv1=nn.Sequential(
                    nn.Conv2d(512, 48, kernel_size=1, bias=False),
                    nn.Conv2d(48, 48, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(48, 512, kernel_size=1, bias=False),
                ),
                bn1=nn.BatchNorm2d(512),
                conv2=nn.Sequential(
                    nn.Conv2d(512, 8, kernel_size=1, bias=False),
                    nn.Conv2d(8, 8, kernel_size=3, padding=1, bias=False),
                    nn.Conv2d(8, 512, kernel_size=1, bias=False),
                ),
                bn2=nn.BatchNorm2d(512),
            ),
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
    
    
