# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


from common.registries.dataset_registry import DATASET_WRAPPER_REGISTRY
from object_detection.tf.src.datasets.coco import load_coco_like
from object_detection.tf.src.datasets import prepare_kwargs_for_dataloader, download_dataset

__all__ = ['get_coco']

@DATASET_WRAPPER_REGISTRY.register(framework='tf', dataset_name='coco', use_case="object_detection")
def get_coco(cfg):

    # Get dataloader kwargs
    args = prepare_kwargs_for_dataloader(cfg)

    # Add possibility to download the dataset here?
    if args['data_download'] and args['data_dir'] and args['training_path'] == None and\
        cfg.operation_mode in ['training', 'chain_tqe', 'chain_tqeb']:
        args['training_path'] = download_dataset(data_root=args['data_dir'],
                         dataset_name='coco')

    # Creates datasets
    dataloaders = load_coco_like(cfg=cfg, 
                                 image_size=args["image_size"],
                                 val_batch_size=args["val_batch_size"])

    return dataloaders