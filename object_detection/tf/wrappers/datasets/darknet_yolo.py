# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


from common.registries.dataset_registry import DATASET_WRAPPER_REGISTRY
from object_detection.tf.src.datasets.darknet_yolo import load_darknet_yolo_like
from object_detection.tf.src.datasets import prepare_kwargs_for_dataloader

__all__ = ['get_darknet_yolo']

@DATASET_WRAPPER_REGISTRY.register(framework='tf', dataset_name='darknet_yolo', use_case="object_detection")
def get_darknet_yolo(cfg):

    # Get dataloader kwargs
    args = prepare_kwargs_for_dataloader(cfg)

    # Creates datasets
    dataloaders = load_darknet_yolo_like(cfg=cfg, 
                                         image_size=args["image_size"],
                                         val_batch_size=args["val_batch_size"])

    return dataloaders