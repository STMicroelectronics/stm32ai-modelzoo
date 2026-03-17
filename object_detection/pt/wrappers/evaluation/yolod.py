
# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.

import torch
import torch.distributed as dist

from common.registries.evaluator_registry import EVALUATOR_WRAPPER_REGISTRY
from object_detection.pt.src.data.yolod.augmentations.data_augment import \
    ValTransform
from object_detection.pt.src.data.yolod.datasets import (COCODataset,
                                                         VOCDetection)


@EVALUATOR_WRAPPER_REGISTRY.register(
    evaluator_name="yolod",
    framework="torch",
    use_case="object_detection",
)
class YOLODEvaluatorWrapper:
    def __init__(self, dataloaders, model, cfg):
        self.dataloaders = dataloaders["test"]
        self.model = model
        self.cfg = cfg

    def evaluate(self):
        evaluator = self._build_evaluator()

        model_to_eval = (
            self.model.module if hasattr(self.model, "module") else self.model
        )
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_to_eval.to(device).eval()

        with torch.no_grad():
            result = evaluator.evaluate(
                model_to_eval,
                half=False,
                return_outputs=False,
            )
        return result
    
    def get_eval_dataset(self, **kwargs):
        testdev = kwargs.get("testdev", False)
        legacy = kwargs.get("legacy", False)

        if self.cfg.dataset.dataset_name == "coco": 
                    
            return COCODataset(
                data_dir=self.cfg.dataset.data_dir,                
                annotations_path=self.dataset.val_annotations_path,
                images_path=self.cfg.dataset.val_images_path,
                # json_file=self.cfg.dataset.val_ann if not testdev else self.test_ann,
                # name="val2017" if not testdev else "test2017",
                img_size=self.cfg.model.input_shape[1:],
                preproc=ValTransform(legacy=legacy),
            )
        elif self.cfg.dataset.dataset_name == "voc":    
            
            return VOCDetection(
                data_dir=self.cfg.dataset.data_dir,
                image_sets=[('2007', 'test')],
                img_size=self.cfg.model.input_shape[1:],
                preproc=ValTransform(legacy=legacy),
            )
        else : 
            print ("only voc and coco datasets are supported")

    def get_eval_loader(self, batch_size, is_distributed, **kwargs):
        valdataset = self.get_eval_dataset(**kwargs)

        if is_distributed and dist.is_available() and dist.is_initialized():
            batch_size = batch_size // dist.get_world_size()
            sampler = torch.utils.data.distributed.DistributedSampler(
                valdataset, shuffle=False
            )
        else:
            sampler = torch.utils.data.SequentialSampler(valdataset)

        dataloader_kwargs = {
            "num_workers": self.cfg.dataset.data_num_workers,
            "pin_memory": True,
            "sampler": sampler,
        }
        dataloader_kwargs["batch_size"] = batch_size
        val_loader = torch.utils.data.DataLoader(valdataset, **dataloader_kwargs)

        return val_loader

    def _build_evaluator(self):
        from object_detection.pt.src.evaluation.yolod.evaluators import (
            COCOEvaluator, VOCEvaluator)
        cfg = self.cfg
        
        
        if cfg.dataset.dataset_name == "coco":
            
            num_classes = getattr(self.cfg.model, "num_classes", 80)
            return COCOEvaluator(
                dataloader = self.dataloaders, 
                # dataloader=self.get_eval_loader(cfg.training.batch_size, is_distributed=False),
                img_size=cfg.model.input_shape[1:],
                confthre=cfg.postprocessing.confidence_thresh,
                nmsthre=cfg.postprocessing.NMS_thresh,
                num_classes=num_classes,
            )
        else:
            num_classes = getattr(self.cfg.model, "num_classes", 20)
            return VOCEvaluator(
                dataloader=self.get_eval_loader(cfg.training.batch_size, is_distributed=False),
                img_size=cfg.test.test_size,
                confthre=cfg.test.test_conf,
                nmsthre=cfg.test.nmsthre,
                num_classes=num_classes,
            )