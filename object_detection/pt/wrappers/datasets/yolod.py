# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import random

import torch
import torch.distributed as dist
from torch.utils.data import Subset

from common.registries.dataset_registry import DATASET_WRAPPER_REGISTRY
from object_detection.pt.src.data.yolod import worker_init_reset_seed
from object_detection.pt.src.data.yolod.augmentations.data_augment import (
    TrainTransform, ValTransform,PredTransform)
from object_detection.pt.src.data.yolod.datasets import COCODataset
from object_detection.pt.src.data.yolod.datasets.mosaicdetection import \
    MosaicDetection
from object_detection.pt.src.data.yolod.datasets.prediction_dataset import \
    PredictionDataset
# from object_detection.pt.src.data.yolod.datasets import MosaicDetection
from object_detection.pt.src.data.yolod.samplers import (InfiniteSampler,
                                                         YoloBatchSampler)
from object_detection.pt.src.utils.yolod import ( wait_for_the_master, get_world_size)
from object_detection.pt.src.data.yolod import DataLoader

# --------------------------- COCO ---------------------------

def get_dataloader_type_dict(cfg): 
    train = test = valid = quantization = predict = False
    if getattr(cfg.dataset, "train_annotations_path", None) and getattr(cfg.dataset, "train_images_path", None):
        train = True
    if getattr(cfg.dataset, "val_annotations_path", None) and getattr(cfg.dataset, "val_images_path", None):
        valid = True
    if getattr(cfg.dataset, "test_annotations_path", None) and getattr(cfg.dataset, "test_images_path", None):
        test = True
    if getattr(cfg.dataset, "quantization_path", None) or train:
        quantization = True
    if getattr(cfg.dataset, "prediction_path", None):
        predict = True
    
    return {
        "train": train,
        "valid": valid,  
        "test": test,   
        "quantization": quantization,
        "predict": predict,
    }

def get_train_loader(cfg): 
    
    if not hasattr(cfg, "dataset") or not hasattr(cfg, "training"):
        raise ValueError("cfg incomplete")

    data_root   = None
    train_ann   = getattr(cfg.dataset, "train_annotations_path", "instances_train2017.json")
    train_name  = getattr(cfg.dataset, "train_images_path", "train2017")    

    # --- size / loader knobs ---
    input_size      = getattr(cfg.model, "input_shape", [640, 640])
    if isinstance(input_size, list) or isinstance(input_size, tuple):
        input_size = input_size[-2:]
    if isinstance(input_size, int):
        input_size = [input_size, input_size]

    batch_size      = getattr(cfg.training, "batch_size", 16)
    num_workers     = getattr(cfg.dataset, "num_workers", 4)
    pin_memory      = getattr(cfg.training, "pin_memory", True)
    seed            = getattr(cfg.dataset, "seed", 123)


    # --- aug knobs ---
    aug = getattr(cfg, "aug", object())
    no_aug       = getattr(aug, "no_aug", False)
    flip_prob    = getattr(aug, "flip_prob", 0.5)
    hsv_prob     = getattr(aug, "hsv_prob", 1.0)
    degrees      = getattr(aug, "degrees", 10.0)
    translate    = getattr(aug, "translate", 0.1)
    mosaic_scale = getattr(aug, "mosaic_scale", (0.1, 2.0))
    mixup_scale  = getattr(aug, "mixup_scale", (0.5, 1.5))
    shear        = getattr(aug, "shear", 2.0)
    enable_mixup = getattr(aug, "enable_mixup", True)
    mosaic_prob  = getattr(aug, "mosaic_prob", 1.0)
    mixup_prob   = getattr(aug, "mixup_prob", 1.0)

    cache_img    = getattr(cfg.dataset, "cache_img", None)
    
    is_distributed = get_world_size() > 1
        
    # ----------------- Build datasets -----------------
    with wait_for_the_master():
        train_ds = COCODataset(
            data_dir=data_root,
            annotations_path=train_ann,
            images_path=train_name,
            img_size=input_size,
            preproc=TrainTransform(
                max_labels=50,
                flip_prob=flip_prob,
                hsv_prob=hsv_prob,
            ),
            cache=(cache_img is not None),
            cache_type=cache_img or "ram",
        )
# Mosaic / MixUp wrapper for training
    train_view = train_ds if no_aug else MosaicDetection(
        dataset=train_ds,
        mosaic=not no_aug,
        img_size=input_size,
        preproc=TrainTransform(
            max_labels=120,
            flip_prob=flip_prob,
            hsv_prob=hsv_prob,
        ),
        degrees=degrees,
        translate=translate,
        mosaic_scale=mosaic_scale,
        mixup_scale=mixup_scale,
        shear=shear,
        enable_mixup=enable_mixup,
        mosaic_prob=mosaic_prob,
        mixup_prob=mixup_prob,
    )

    # ----------------- Samplers / Loaders -----------------
    if is_distributed and dist.is_available() and dist.is_initialized():
        world_size = dist.get_world_size()
        eff_bs = max(1, batch_size // world_size)
    else:
        eff_bs = batch_size

    sampler = InfiniteSampler(len(train_view), seed=seed)
    batch_sampler = YoloBatchSampler(
        sampler=sampler,
        batch_size=eff_bs,
        drop_last=False,
        mosaic=not no_aug,
    )

    train_loader = DataLoader(
        train_view,
        num_workers=num_workers,
        pin_memory=pin_memory,
        batch_sampler=batch_sampler,
        worker_init_fn=worker_init_reset_seed,
    )
    
    return train_loader
    
def get_validation_loader(cfg): 
    
    if not hasattr(cfg, "dataset") or not hasattr(cfg, "training"):
        raise ValueError("cfg incomplete")

    data_root   = None
    val_ann     = getattr(cfg.dataset, "val_annotations_path",   "instances_val2017.json")
    val_name    = getattr(cfg.dataset, "val_images_path",   "val2017")
    

    # --- size / loader knobs ---
    input_size      = getattr(cfg.model, "input_shape", [640, 640])
    if isinstance(input_size, list) or isinstance(input_size, tuple):
        input_size = input_size[-2:]
    if isinstance(input_size, int):
        input_size = [input_size, input_size]

    batch_size      = getattr(cfg.training, "batch_size", 16)
    test_batch_size = getattr(cfg.training, "test_batch_size", batch_size)
    num_workers     = getattr(cfg.dataset, "num_workers", 4)
    pin_memory      = getattr(cfg.training, "pin_memory", True)
    is_distributed  = get_world_size() > 1
    
    # --- aug knobs ---
    legacy       = getattr(cfg.dataset, "legacy", False)
    testdev      = getattr(getattr(cfg, "eval", object()), "testdev", False)
    
    eval_ds = COCODataset(
        data_dir=data_root,
        annotations_path=val_ann,
        images_path=val_name,
        img_size=input_size,
        preproc= ValTransform(legacy=legacy),
        cache=False,
        cache_type="ram",
    )

    if is_distributed:
            batch_size = batch_size // dist.get_world_size()
            sampler = torch.utils.data.distributed.DistributedSampler(
                eval_ds, shuffle=False
            )
    else:
        sampler = torch.utils.data.SequentialSampler(eval_ds)

    dataloader_kwargs = {
        "num_workers": num_workers,
        "pin_memory": pin_memory,
        "sampler": sampler,
    }
    dataloader_kwargs["batch_size"] = batch_size
    
    # val_loader = DataLoader(
    #     eval_ds,
    #     batch_size=test_batch_size or batch_size,
    #     shuffle=False,
    #     num_workers=num_workers,
    #     pin_memory=pin_memory,
    #     sampler=sampler
    # )
    val_loader = torch.utils.data.DataLoader(eval_ds, **dataloader_kwargs)
    
    return val_loader
    
def get_test_loader(cfg):
    
    if not hasattr(cfg, "dataset") or not hasattr(cfg, "training"):
        raise ValueError("cfg incomplete")

    data_root   = None
    test_ann     = getattr(cfg.dataset, "test_annotations_path",   "test_val2017.json")
    test_name    = getattr(cfg.dataset, "test_images_path",   None)

    # --- size / loader knobs ---
    input_size      = getattr(cfg.model, "input_shape", [640, 640])
    if isinstance(input_size, list) or isinstance(input_size, tuple):
        input_size = input_size[-2:]
    if isinstance(input_size, int):
        input_size = [input_size, input_size]

    batch_size      = getattr(cfg.training, "batch_size", 16)
    test_batch_size = getattr(cfg.training, "test_batch_size", batch_size)
    num_workers     = getattr(cfg.dataset, "num_workers", 4)
    pin_memory      = getattr(cfg.training, "pin_memory", True)

    # --- aug knobs ---
    legacy       = getattr(cfg.dataset, "legacy", False)
    
    # ----------------- Build datasets -----------------
    
    with wait_for_the_master():
        test_ds = COCODataset(
            data_dir=data_root,
            annotations_path=test_ann,
            images_path=test_name,
            img_size=input_size,
            preproc=ValTransform(legacy=legacy),
            cache=False,
            cache_type="ram",
        )

    test_loader = torch.utils.data.DataLoader(
        test_ds,
        batch_size=test_batch_size or batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    
    return test_loader
    
def get_prediction_loader(cfg): 
    
    
    pred_loader = None
    prediction_path = getattr(cfg.dataset, "prediction_path", None)
    num_workers     = getattr(cfg.dataset, "num_workers", 4)
    pin_memory      = getattr(cfg.training, "pin_memory", True)
    legacy       = getattr(cfg.dataset, "legacy", False)
    
    # --- size / loader knobs ---
    input_size      = getattr(cfg.model, "input_shape", [640, 640])
    if isinstance(input_size, list) or isinstance(input_size, tuple):
        input_size = input_size[-2:]
    if isinstance(input_size, int):
        input_size = [input_size, input_size]
        
    if prediction_path:
        pred_dataset = PredictionDataset(
            prediction_path,
            input_size=input_size,
            transform=PredTransform(legacy=legacy),
        )
        pred_loader = torch.utils.data.DataLoader(
            pred_dataset,
            batch_size=1,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )

    else:
        pred_loader = None
    
    return pred_loader
    
def get_quantization_loader(cfg, train_loader): 


    if not hasattr(cfg, "dataset") or not hasattr(cfg, "training"):
            raise ValueError("cfg incomplete")
    legacy       = getattr(cfg.dataset, "legacy", False)
    quantization_path = getattr(cfg.dataset, "quantization_path",   None)
    train_images_path = cfg.dataset.train_images_path or None 
    

    # --- size / loader knobs ---
    input_size      = getattr(cfg.model, "input_shape", [640, 640])
    if isinstance(input_size, list) or isinstance(input_size, tuple):
        input_size = input_size[-2:]
    if isinstance(input_size, int):
        input_size = [input_size, input_size]

    num_workers     = getattr(cfg.dataset, "num_workers", 4)
    pin_memory      = getattr(cfg.training, "pin_memory", True)
    
    if quantization_path: # need to test (empty string or None):
        quantization_split = getattr(cfg.dataset, "quantization_split", 0.1) 

        quant_dataset = PredictionDataset(
            quantization_path,
            input_size=input_size,
            transform=PredTransform(legacy=legacy), 
        )
        
        num_quant_samples = int(len(quant_dataset) * quantization_split)
        num_quant_samples = max(1, num_quant_samples)
        quant_indices = random.sample(range(len(quant_dataset)), num_quant_samples)

        quant_subset = Subset(quant_dataset, quant_indices)
        
        quant_loader = torch.utils.data.DataLoader(
            quant_subset,
            batch_size=1,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )

    elif train_loader is not None and getattr(cfg, "quantization", None) is not None:
        
        quantization_split = getattr(cfg.dataset, "quantization_split", 0.1)
        quant_dataset = PredictionDataset(
            train_images_path,
            input_size=input_size,
            transform=PredTransform(legacy=legacy), 
        )
        
        num_quant_samples = int(len(quant_dataset) * quantization_split)
        num_quant_samples = max(1, num_quant_samples)
        quant_indices = random.sample(range(len(quant_dataset)), num_quant_samples)

        quant_subset = Subset(quant_dataset, quant_indices)
        
        quant_loader = torch.utils.data.DataLoader(
            quant_subset,
            batch_size=1,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )
        
    else:
        quant_loader = None
    
    return quant_loader 

#@DATASET_WRAPPER_REGISTRY.register(framework='torch', dataset_name='coco', use_case='object_detection')
def get_coco_detection(cfg):
    
    dataloader_dict =  get_dataloader_type_dict(cfg)
    train_loader = val_loader = test_loader = quant_loader = pred_loader = None
    if dataloader_dict["train"]:     
        train_loader = get_train_loader(cfg)
    if dataloader_dict["valid"]:  
        val_loader = get_validation_loader(cfg)
    if dataloader_dict["test"]: 
        test_loader = get_test_loader(cfg)
    elif dataloader_dict["valid"]:
        test_loader = get_validation_loader(cfg)
    if dataloader_dict["quantization"]: 
        quant_loader = get_quantization_loader(cfg, train_loader) 
    if dataloader_dict["predict"]:
        pred_loader = get_prediction_loader(cfg)   


    return {
        "train": train_loader,
        "valid": val_loader,
        "test": test_loader,
        "quantization": quant_loader,
        "predict": pred_loader,
    }


# ----------------------------- VOC -----------------------------

@DATASET_WRAPPER_REGISTRY.register(framework='torch', dataset_name='voc_yolod', use_case='object_detection')
def get_voc_detection(
    data_root,
    train_sets=(('2007', 'trainval'), ('2012', 'trainval')),
    val_sets=(('2007', 'test'),),
    input_size=(640, 640),
    batch_size=16,
    test_batch_size=None,
    distributed=False,
    num_workers=4,
    pin_memory=True,
    no_aug=False,
    flip_prob=0.5,
    hsv_prob=1.0,
    degrees=10.0,
    translate=0.1,
    mosaic_scale=(0.1, 2.0),
    mixup_scale=(0.5, 1.5),
    shear=2.0,
    enable_mixup=True,
    mosaic_prob=1.0,
    mixup_prob=1.0,
    cache_img=None,       
    legacy=False,
    seed=0,
    **kwargs,
):
    import torch.distributed as dist
    # todo : fix this import 
    from torch.utils.data import DataLoader

    from object_detection.pt.src.data.yolod import worker_init_reset_seed
    from object_detection.pt.src.data.yolod.augmentations.data_augment import (
        TrainTransform, ValTransform)
    from object_detection.pt.src.data.yolod.datasets import VOCDetection
    from object_detection.pt.src.data.yolod.datasets.mosaicdetection import \
        MosaicDetection
    from object_detection.pt.src.data.yolod.samplers import (InfiniteSampler,
                                                             YoloBatchSampler)
    from object_detection.pt.src.utils.yolod import wait_for_the_master

    if isinstance(input_size, int):
        input_size = (input_size, input_size)

    # ----------------- Build datasets -----------------
    with wait_for_the_master():
        train_ds = VOCDetection(
            data_dir=data_root,
            image_sets=list(train_sets),
            img_size=input_size,
            preproc=TrainTransform(
                max_labels=50,
                flip_prob=flip_prob,
                hsv_prob=hsv_prob,
            ),
            cache=(cache_img is not None),
            cache_type=cache_img or "ram",
        )

        eval_ds = VOCDetection(
            data_dir=data_root,
            image_sets=list(val_sets),
            img_size=input_size,
            preproc=ValTransform(legacy=legacy),
            cache=False,
            cache_type="ram",
        )

    # Mosaic / MixUp wrapper for training
    train_view = train_ds if no_aug else MosaicDetection(
        dataset=train_ds,
        mosaic=not no_aug,
        img_size=input_size,
        preproc=TrainTransform(
            max_labels=120,
            flip_prob=flip_prob,
            hsv_prob=hsv_prob,
        ),
        degrees=degrees,
        translate=translate,
        mosaic_scale=mosaic_scale,
        mixup_scale=mixup_scale,
        shear=shear,
        enable_mixup=enable_mixup,
        mosaic_prob=mosaic_prob,
        mixup_prob=mixup_prob,
    )

    # ----------------- Samplers / Loaders -----------------
    if distributed and dist.is_available() and dist.is_initialized():
        world_size = dist.get_world_size()
        eff_bs = max(1, batch_size // world_size)
    else:
        eff_bs = batch_size

    sampler = InfiniteSampler(len(train_view), seed=seed)
    batch_sampler = YoloBatchSampler(
        sampler=sampler,
        batch_size=eff_bs,
        drop_last=False,
        mosaic=not no_aug,
    )

    train_loader = DataLoader(
        train_view,
        num_workers=num_workers,
        pin_memory=pin_memory,
        batch_sampler=batch_sampler,
        worker_init_fn=worker_init_reset_seed,
    )

    val_loader = DataLoader(
        eval_ds,
        batch_size=test_batch_size or batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )

    return {'train': train_loader, 'valid': val_loader}