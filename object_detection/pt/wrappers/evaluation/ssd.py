# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


import os

import torch

from common.registries.evaluator_registry import EVALUATOR_WRAPPER_REGISTRY
from object_detection.pt.src.data.ssd.datasets.voc import VOCDataset
from object_detection.pt.src.data.ssd.datasets.coco import CocoDataset 
from object_detection.pt.src.evaluation.ssd.voc_eval import ssd_voc_evaluate
from object_detection.pt.src.evaluation.ssd.coco_eval import ssd_coco_evaluate

from object_detection.pt.src.models.ssd.detectors.mobilenet_v2_ssd import (
    create_mobilenetv2_ssd, create_mobilenetv2_ssd_predictor)

from object_detection.pt.src.models.ssd.detectors.mobilenet_v2_ssd_lite import (
    create_mobilenetv2_ssd_lite, create_mobilenetv2_ssd_lite_predictor)
from object_detection.pt.src.models.ssd.detectors.mobilenetv1_ssd import (
    create_mobilenetv1_ssd, create_mobilenetv1_ssd_predictor)
from object_detection.pt.src.models.ssd.detectors.mobilenetv1_ssd_lite import (
    create_mobilenetv1_ssd_lite, create_mobilenetv1_ssd_lite_predictor)
from object_detection.pt.src.models.ssd.detectors.mobilenetv3_ssd_lite import (
    create_mobilenetv3_large_ssd_lite, create_mobilenetv3_small_ssd_lite,
    create_mobilenetv3_ssd_lite_predictor)
from object_detection.pt.src.models.ssd.detectors.squeezenet_ssd_lite import (
    create_squeezenet_ssd_lite, create_squeezenet_ssd_lite_predictor)


@EVALUATOR_WRAPPER_REGISTRY.register(
    evaluator_name="ssd",
    framework="torch",
    use_case="object_detection",
)
class SSDEvaluatorWrapper:
    def __init__(self, dataloaders, model, cfg):
        self.dataloaders = dataloaders
        self.model = model
        self.cfg = cfg
        self.dataset_name = cfg.dataset.dataset_name.lower()

        self.class_names = self._build_class_names()
        self.dataset = None

    def _build_class_names(self):
        """Return class_names list based on dataset type."""
        # VOC 20-class
        if "voc" in self.dataset_name:
            return [
                "background",
                "aeroplane",
                "bicycle",
                "bird",
                "boat",
                "bottle",
                "bus",
                "car",
                "cat",
                "chair",
                "cow",
                "diningtable",
                "dog",
                "horse",
                "motorbike",
                "person",
                "pottedplant",
                "sheep",
                "sofa",
                "train",
                "tvmonitor",
            ]
        elif "coco" in self.dataset_name:
            if hasattr(self.cfg.dataset, "class_names") and self.cfg.dataset.class_names:
                return ["background"] + list(self.cfg.dataset.class_names)
            # Fallback: Load from dataset during evaluate()
            return None
        else:
            raise ValueError(f"Unsupported dataset_name for SSD eval: {self.dataset_name}")

    def _build_device(self):
        # use_cuda = bool(getattr(self.cfg.general, "use_cuda", True))
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # return torch.device(
        #     "cuda:0" if (torch.cuda.is_available() and use_cuda) else "cpu"
        # )

    def _build_dataset(self):
        """Build eval dataset for VOC or COCO."""
        ds_cfg = self.cfg.dataset

        if "voc" in self.dataset_name:
            
            # dataset_root = ds_cfg.validation_path
            # return VOCDataset(self.cfg, dataset_root, is_test=True)
            
            return VOCDataset(self.cfg, 
                              ds_cfg.val_images_path, 
                              ds_cfg.val_annotations_path, 
                              ds_cfg.val_split,
                              )

        elif "coco" in self.dataset_name:
            return CocoDataset(
                annotations_path=ds_cfg.val_annotations_path,
                images_path=ds_cfg.val_images_path,
                filter_empty_gt=False
            )

        else:
            raise ValueError(f"Unsupported dataset_name for SSD eval: {self.dataset_name}")

    def _build_net_and_predictor(self, num_classes, device):
        model_name = self.cfg.model.model_name
        net = self.model
        # ---------- build predictor ----------
        if model_name == "ssd_mobilenetv1_pt":
            predictor = create_mobilenetv1_ssd_predictor(net, device=device)
        elif model_name == "ssdlite_mobilenetv1_pt":
            predictor = create_mobilenetv1_ssd_lite_predictor(net, device=device)
        elif model_name in ("ssdlite_mobilenetv2_pt", "ssdlite_mobilenetv3large_pt", "ssdlite_mobilenetv3small_pt"):
            predictor = create_mobilenetv2_ssd_lite_predictor(net, device=device)
        elif model_name in ("ssd_mobilenetv2_pt"):
            predictor = create_mobilenetv2_ssd_predictor(net, device=device)            
        else:
            raise ValueError(f"No predictor found for model {model_name}")

        return predictor

    def evaluate(self):
        cfg = self.cfg
        device = self._build_device()
        dataset = self._build_dataset()

        if self.dataset is None:
             self.dataset = self._build_dataset()
        dataset = self.dataset

        # If class_names were not in config (COCO), get them from the dataset
        if self.class_names is None:
            if hasattr(dataset, "class_names"):
                self.class_names = dataset.class_names
            else:
                 raise ValueError("class_names not found in config or dataset.")

        predictor = self._build_net_and_predictor(len(self.class_names), device)

        iou_threshold = float(getattr(cfg.postprocessing, "IoU_eval_thresh", 0.5))
        use_2007_metric = True # bool(getattr(cfg, "use_2007_metric", True))

        if "voc" in self.dataset_name:
            metrics = ssd_voc_evaluate(
                predictor=predictor,
                dataset=dataset,
                class_names=self.class_names,
                iou_threshold=iou_threshold,
                use_2007_metric=use_2007_metric,
            )
        elif "coco" in self.dataset_name:
            metrics = ssd_coco_evaluate(
                predictor=predictor,
                dataset=dataset,
                class_names=self.class_names,
                iou_threshold=iou_threshold,
            )
        else:
            raise ValueError(f"Unsupported dataset_name for SSD eval: {self.dataset_name}")

        return metrics