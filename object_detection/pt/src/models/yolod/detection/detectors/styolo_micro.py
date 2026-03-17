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
from object_detection.pt.src.models.yolod.detection.backbones.stresnet_micro import STResNetMicro 
from object_detection.pt.src.models.yolod.detection.backbones.stresnet_micro_bn import STResNetMicroBN 
from object_detection.pt.src.models.yolod.detection.necks.yolov11_pafpn import YOLOv11PAFPN
from object_detection.pt.src.models.checkpoints import CHECKPOINT_STORAGE_URL, model_checkpoints
from pathlib import Path 
from object_detection.pt.src.models.yolod.yolod import YOLOD
import torch 

def sanity_check(model, ckpt):     
    error = False
    for name, module in model.named_modules():
            if isinstance(module, (nn.Conv2d, nn.Linear)):
                # print(f'Layer: {name} | weight shape: {module.weight.shape} | checkpoint : {ckpt["state_dict"][name].shape}')
                key = f'{name}.weight'
                if key not in ckpt["state_dict"].keys():         
                    print (f'missing key : {key}')
                    error = True
                else : 
                    print(f'Layer: {name} | weight shape: {module.weight.shape}')
                    print(f'checkpoint : {ckpt["state_dict"][key].shape}')
    total_params = sum(p.numel() for p in model.parameters())
    print (f'total params : {total_params}')
    
    if error: 
        print (f'Sanity Check FAILED')
    else : 
        print (f'Sanity check PASSED')
        
        
class STYOLOMicro():
    
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg 
        depth = 0.33
        width = 0.25
        # act = getattr(self.cfg.model, "act", 'silu')
        # depthwise = getattr(self.cfg.model, "depthwise", True)
        act = self.cfg.model.act or 'silu'
        depthwise = self.cfg.model.depthwise or True
        
        in_channels = [256, 512, 1024]
        out_features = ["dark3", "dark4", "dark5"]
        num_classes = getattr(self.cfg.model, "num_classes", 80)
        
        self.backbone = STResNetMicroBN(out_features=out_features)        
        self.neck = STResNetYOLOPAFPN(depth=depth, width=width, in_channels=in_channels, in_features=out_features, act=act, depthwise=depthwise)
        self.head = YOLODHead(self.cfg, num_classes, width, in_channels=in_channels, act=act, depthwise=depthwise)
        self.model = YOLOD(self.backbone, self.neck, self.head)

        if cfg.model.pretrained : 
            ckpt = torch.load(Path(CHECKPOINT_STORAGE_URL, model_checkpoints["st_resnetmicro_actrelu_pt_datasetimagenet_res224"]), weights_only=False, map_location=torch.device(cfg.device))
            # sanity_check(self.backbone, ckpt)
            self.backbone.load_state_dict(ckpt['state_dict'], strict=False)
            
        self.model.apply(self.init_yolo)
        self.model.head.initialize_biases(1e-2)  
        

        
    def get_model(self): 
        return self.model         
        
    def init_yolo(self, M):
        for m in M.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eps = 1e-3
                m.momentum = 0.03
                
                

    



    
        
