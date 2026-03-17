# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import torch.nn as nn

from .detection.heads.yolo_head import YOLODHead
from .detection.necks.yolo_pafpn import YOLOPAFPN
from .detection.backbones.darknet import CSPDarknet


class YOLOD(nn.Module):
    """
    YOLOD model module. 
    The network returns loss values from three YOLO layers during training
    and detection results during test.
    """

    def __init__(self, backbone=None, neck=None, head=None):
        super().__init__()
        if backbone is None:
            backbone = CSPDarknet()
        if neck is None:
            neck = YOLOPAFPN()
        if head is None:
            head = YOLODHead(80)

        self.backbone = backbone
        self.neck = neck
        self.head = head

    def forward(self, x, targets=None):
        # fpn output content features of [dark3, dark4, dark5]
        csp_outs = self.backbone(x)
        fpn_outs = self.neck(csp_outs)

        if self.training:
            assert targets is not None
            loss, iou_loss, conf_loss, cls_loss, l1_loss, num_fg = self.head(
                fpn_outs, targets, x
            )
            outputs = {
                "total_loss": loss,
                "iou_loss": iou_loss,
                "l1_loss": l1_loss,
                "conf_loss": conf_loss,
                "cls_loss": cls_loss,
                "num_fg": num_fg,
            }
        else:
            outputs = self.head(fpn_outs)

        return outputs

    def visualize(self, x, targets, save_prefix="assign_vis_"):
        fpn_outs = self.backbone(x)
        self.head.visualize_assign_result(fpn_outs, targets, x, save_prefix)