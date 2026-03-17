# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import torch
from torch.nn import Conv2d, Sequential, ModuleList, BatchNorm2d
from torch import nn
from object_detection.pt.src.models.ssd.backbones.mobilenet_v2 import MobileNetV2
from torch.nn import Conv2d, Sequential, ModuleList, ReLU


from .ssd import SSD, GraphPath
from .predictor import Predictor
from .config.mobilenetv1_ssd_config import MOBILENET_CONFIG

def create_mobilenetv2_ssd(num_classes, width_mult=1.0, is_test=False):
    base_net = MobileNetV2(width_mult=width_mult).features

    source_layer_indexes = [
        GraphPath(14, 'conv', 3),
        19,
    ]

    extras = ModuleList([
        Sequential(
            Conv2d(1280, 512, kernel_size=1),
            ReLU(),
            Conv2d(512, 512, kernel_size=3, stride=2, padding=1),
            ReLU()
        ),
        Sequential(
            Conv2d(512, 256, kernel_size=1),
            ReLU(),
            Conv2d(256, 256, kernel_size=3, stride=2, padding=1),
            ReLU()
        ),
        Sequential(
            Conv2d(256, 256, kernel_size=1),
            ReLU(),
            Conv2d(256, 256, kernel_size=3, stride=2, padding=1),
            ReLU()
        ),
        Sequential(
            Conv2d(256, 64, kernel_size=1),
            ReLU(),
            Conv2d(64, 64, kernel_size=3, stride=2, padding=1),
            ReLU()
        )
    ])

    regression_headers = ModuleList([
        Conv2d(round(576 * width_mult), 6 * 4, kernel_size=3, padding=1),
        Conv2d(1280, 6 * 4, kernel_size=3, padding=1),
        Conv2d(512, 6 * 4, kernel_size=3, padding=1),
        Conv2d(256, 6 * 4, kernel_size=3, padding=1),
        Conv2d(256, 6 * 4, kernel_size=3, padding=1),
        Conv2d(64, 6 * 4, kernel_size=1),
    ])

    classification_headers = ModuleList([
        Conv2d(round(576 * width_mult), 6 * num_classes, kernel_size=3, padding=1),
        Conv2d(1280, 6 * num_classes, kernel_size=3, padding=1),
        Conv2d(512, 6 * num_classes, kernel_size=3, padding=1),
        Conv2d(256, 6 * num_classes, kernel_size=3, padding=1),
        Conv2d(256, 6 * num_classes, kernel_size=3, padding=1),
        Conv2d(64, 6 * num_classes, kernel_size=1),
    ])

    return SSD(num_classes, base_net, source_layer_indexes,
               extras, classification_headers, regression_headers, is_test=is_test, config=MOBILENET_CONFIG)

def create_mobilenetv2_ssd_predictor(net, candidate_size=200, nms_method=None, sigma=0.5, device=torch.device('cpu')):
    predictor = Predictor(net, MOBILENET_CONFIG().image_size, MOBILENET_CONFIG().image_mean,
                          MOBILENET_CONFIG().image_std,
                          nms_method=nms_method,
                          iou_threshold=MOBILENET_CONFIG().iou_threshold,
                          candidate_size=candidate_size,
                          sigma=sigma,
                          device=device)
    return predictor   
    
