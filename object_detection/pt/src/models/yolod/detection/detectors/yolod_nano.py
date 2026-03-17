# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Copyright (c) Megvii Inc. All rights reserved.

import torch.nn as nn

from object_detection.pt.src.models.yolod.detection.heads.yolo_head import YOLODHead
from object_detection.pt.src.models.yolod.detection.necks.yolo_pafpn import YOLOPAFPN
from object_detection.pt.src.models.yolod.detection.backbones.darknet import CSPDarknet
from object_detection.pt.src.models.yolod.yolod import YOLOD


class YOLODNano():
    
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg 
  
        depth = self.cfg.model.depth or 0.33
        width = self.cfg.model.width or 0.25
        act = self.cfg.model.act or 'silu'
        depthwise = self.cfg.model.depthwise or True
        # act = getattr(self.cfg.model, "act", 'silu')
        # depthwise = getattr(self.cfg.model, "depthwise", True)
        num_classes = getattr(self.cfg.model, "num_classes", 80)
        in_channels = [256, 512, 1024]
        
        self.backbone = CSPDarknet(depth, width, act=act, depthwise=depthwise)
        self.neck = YOLOPAFPN(depth, width, in_channels=in_channels, act=act, depthwise=depthwise)
                
        self.head = YOLODHead(self.cfg, num_classes, width, in_channels=in_channels, act=act, depthwise=depthwise)
        self.model = YOLOD(self.backbone,self.neck, self.head)

        # no init if loading pretrained weights for coco
        if cfg.model.pretrained and cfg.model.num_classes == 80: 
            pass 
        else : 
            # no pretrained backbone so init the complete model 
            self.model.apply(self.init_yolo)
            self.model.head.initialize_biases(1e-2)       
        
    def get_model(self): 
        return self.model         
        
    def init_yolo(self, M, type='scratch'):    
        for m in M.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eps = 1e-3
                m.momentum = 0.03
    