import torch
from torch.nn import Conv2d, Sequential, ModuleList, ReLU, BatchNorm2d

from object_detection.pt.src.models.ssd.detectors.ssd import SSD
from object_detection.pt.src.models.ssd.detectors.predictor import Predictor
from object_detection.pt.src.models.ssd.detectors.config import vgg_ssd_config as config

import torch.nn as nn
from object_detection.pt.src.models.ssd.backbones.optimized.resnet_c import ResNet1M
from torchvision.models.resnet import resnet18, resnet34, resnet50, resnet101, resnet152
class ResNet(nn.Module):
    def __init__(self, backbone='resnet18'):
        super().__init__()
        if backbone == 'resnet18':
            backbone = ResNet1M()
            self.out_channels = [256, 512, 512, 256, 256, 128]
        elif backbone == 'resnet34':
            backbone = resnet34(pretrained=True)
            self.out_channels = [256, 512, 512, 256, 256, 256]
        elif backbone == 'resnet50':
            backbone = resnet50(pretrained=True)
            self.out_channels = [1024, 512, 512, 256, 256, 256]
        elif backbone == 'resnet101':
            backbone = resnet101(pretrained=True)
            self.out_channels = [1024, 512, 512, 256, 256, 256]
        else:  # backbone == 'resnet152':
            backbone = resnet152(pretrained=True)
            self.out_channels = [1024, 512, 512, 256, 256, 256]

        self.feature_extractor = nn.Sequential(*list(backbone.children())[:7])

        conv4_block1 = self.feature_extractor[-1][0]
        conv4_block1.conv1[1].stride = (1, 1)
        conv4_block1.conv2[1].stride = (1, 1)
        conv4_block1.downsample[0][0].stride = (1, 1)
        conv4_block1.downsample[0][1].stride = (1, 1)
        print(conv4_block1)


def create_resnet_ssd(num_classes, is_test=False, backbone="resnet18"):
    net = ResNet()
    base_net = ModuleList(net.feature_extractor)
    _io = net.out_channels
    _c = [256, 256, 128, 128, 128]
    source_layer_indexes = [
        len(base_net),
    ]
    extras = ModuleList([
        Sequential(
            nn.Conv2d(_io[0], _c[0], kernel_size=1, bias=False),
            nn.BatchNorm2d(_c[0]),
            nn.ReLU(inplace=True),
            nn.Conv2d(_c[0], _io[1], kernel_size=3, padding=1, stride=2, bias=False),
            nn.BatchNorm2d(_io[1]),
            nn.ReLU(inplace=True),
        ),
        Sequential(
            nn.Conv2d(_io[1], _c[1], kernel_size=1, bias=False),
            nn.BatchNorm2d(_c[1]),
            nn.ReLU(inplace=True),
            nn.Conv2d(_c[1], _io[2], kernel_size=3, padding=1, stride=2, bias=False),
            nn.BatchNorm2d(_io[2]),
            nn.ReLU(inplace=True),
        ),
        Sequential(
            nn.Conv2d(_io[2], _c[2], kernel_size=1, bias=False),
            nn.BatchNorm2d(_c[2]),
            nn.ReLU(inplace=True),
            nn.Conv2d(_c[2], _io[3], kernel_size=3, padding=1, stride=2, bias=False),
            nn.BatchNorm2d(_io[3]),
            nn.ReLU(inplace=True),
        ),
        Sequential(
            nn.Conv2d(_io[3], _c[3], kernel_size=1, bias=False),
            nn.BatchNorm2d(_c[3]),
            nn.ReLU(inplace=True),
            nn.Conv2d(_c[3], _io[4], kernel_size=3, bias=False),
            nn.BatchNorm2d(_io[4]),
            nn.ReLU(inplace=True),
        ),
        Sequential(
            nn.Conv2d(_io[4], _c[4], kernel_size=1, bias=False),
            nn.BatchNorm2d(_c[4]),
            nn.ReLU(inplace=True),
            nn.Conv2d(_c[4], _io[5], kernel_size=3, bias=False),
            nn.BatchNorm2d(_io[5]),
            nn.ReLU(inplace=True),
        )
    ])

    regression_headers = ModuleList([
        Conv2d(in_channels=_io[0], out_channels=4 * 4, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[1], out_channels=6 * 4, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[2], out_channels=6 * 4, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[3], out_channels=6 * 4, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[4], out_channels=4 * 4, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[5], out_channels=4 * 4, kernel_size=3, padding=1),
    ])

    classification_headers = ModuleList([
        Conv2d(in_channels=_io[0], out_channels=4 * num_classes, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[1], out_channels=6 * num_classes, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[2], out_channels=6 * num_classes, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[3], out_channels=6 * num_classes, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[4], out_channels=4 * num_classes, kernel_size=3, padding=1),
        Conv2d(in_channels=_io[5], out_channels=4 * num_classes, kernel_size=3, padding=1),
    ])

    return SSD(num_classes, base_net, source_layer_indexes,
               extras, classification_headers, regression_headers, is_test=is_test, config=config)


def create_resnet_predictor(net, candidate_size=200, nms_method=None, sigma=0.5, device=None):
    predictor = Predictor(net, config.image_size, config.image_mean,
                          nms_method=nms_method,
                          iou_threshold=config.iou_threshold,
                          candidate_size=candidate_size,
                          sigma=sigma,
                          device=device)
    return predictor