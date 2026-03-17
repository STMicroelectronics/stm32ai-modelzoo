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
from object_detection.pt.src.models.yolod.detection.necks.stresnet_pafpn import STResNetYOLOPAFPN
from object_detection.pt.src.models.yolod.detection.backbones.stresnet_milli import STResNetMilli
from object_detection.pt.src.models.yolod.detection.necks.stresnet_pafpn import STResNetYOLOPAFPN
from object_detection.pt.src.models.checkpoints import CHECKPOINT_STORAGE_URL, model_checkpoints
from pathlib import Path 

from object_detection.pt.src.models.yolod.yolod import YOLOD
import torch 

class STYOLOMilli():
    
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        depth = self.cfg.model.depth or 0.33
        width = self.cfg.model.width or 0.25
        
        depth = 0.33
        width = 0.25
        act = self.cfg.model.act or 'silu'
        depthwise = self.cfg.model.depthwise or True
        # act = getattr(self.cfg.model, "act", 'silu')        
        # depthwise = getattr(self.cfg.model, "depthwise", True)
        
        in_channels = [256, 512, 1024]
        out_features = ["dark3", "dark4", "dark5"]
        num_classes = getattr(self.cfg.model, "num_classes", 80)
        
        
        self.backbone = STResNetMilli(out_features=out_features)
        
        # if cfg.model.pretrained : 
        #     ckpt = torch.load(Path(CHECKPOINT_STORAGE_URL, model_checkpoints["st_resnetmilli_actrelu_pt_datasetimagenet_res224"]), weights_only=False, map_location=torch.device(cfg.device))
        #     self.backbone.load_state_dict(ckpt['state_dict'], strict=False)
            
        self.neck = STResNetYOLOPAFPN(depth=depth, width=width, in_channels=in_channels, in_features=out_features, act=act, depthwise=depthwise)
        self.head = YOLODHead(self.cfg, num_classes, width=width, in_channels=in_channels, act=act, depthwise=depthwise)
        self.model = YOLOD(self.backbone, self.neck, self.head)

        self.model.apply(self.init_yolo)
        self.model.head.initialize_biases(1e-2)  

        
    def get_model(self): 
        return self.model         
        
    def init_yolo(self, M):
        for m in M.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eps = 1e-3
                m.momentum = 0.03
        


    