# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/


from common.registries.dataset_registry import DATASET_WRAPPER_REGISTRY
from object_detection.tf.src.datasets.pascal_voc import load_pascal_voc_like
from object_detection.tf.src.datasets import prepare_kwargs_for_dataloader, download_dataset

__all__ = ['get_pascal_voc']

@DATASET_WRAPPER_REGISTRY.register(framework='tf', dataset_name='pascal_voc', use_case="object_detection")
def get_pascal_voc(cfg):

    # Get dataloader kwargs
    args = prepare_kwargs_for_dataloader(cfg)
    
    # Add possibility to download the dataset here?
    if args['data_download'] and args['data_dir'] and args['training_path'] == None and\
        cfg.operation_mode in ['training', 'chain_tqe', 'chain_tqeb']:
        args['training_path'] = download_dataset(data_root=args['data_dir'],
                         dataset_name='pascal_voc')

    # Creates datasets
    dataloaders = load_pascal_voc_like(cfg=cfg, 
                                       image_size=args["image_size"],
                                       val_batch_size=args["val_batch_size"])

    return dataloaders