# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os

import numpy as np
import torch
from torch.utils.data import ConcatDataset, DataLoader

from common.registries.dataset_registry import DATASET_WRAPPER_REGISTRY
from object_detection.pt.src.data.ssd.data_preprocessing import (
    TestTransform, TrainAugmentation)
from object_detection.pt.src.data.ssd.datasets.voc import VOCDataset
from object_detection.pt.src.data.ssd.datasets.coco import CocoDataset
from object_detection.pt.src.models.ssd.detectors.config.mobilenetv1_ssd_config import \
    MOBILENET_CONFIG
from object_detection.pt.src.models.ssd.detectors.ssd import MatchPrior
from object_detection.pt.src.data.ssd.datasets.prediction_dataset import SSDPredictionDataset
from object_detection.pt.src.utils.ssd.misc import store_labels
import random
from torch.utils.data import DataLoader, ConcatDataset, Subset

def get_ssd_voc_dataloader_type_dict(cfg):
    train = valid = test = quantization = predict = False
    #print(cfg.dataset)
    # training requires train roots
    if getattr(cfg.dataset, "train_images_path", None):
        train = True

    # valid requires val root
    if getattr(cfg.dataset, "val_images_path", None):
        valid = True

    # test optional root (or fall back to val)
    if getattr(cfg.dataset, "test_images_path", None) or getattr(cfg.dataset, "val_images_path", None):
        test = True

    # quant: either explicit path OR fallback to train subset
    if getattr(cfg.dataset, "quantization_path", None) or train:
        quantization = True

    # predict: if prediction_path is provided
    if getattr(cfg.dataset, "prediction_path", None):
        predict = True

    return {
        "train": train,
        "valid": valid,
        "test": test,
        "quantization": quantization,
        "predict": predict,
    }

def _ssd_voc_build_transforms(cfg):
    # image size has to be int
    image_size = getattr(cfg.model, "input_shape", 300)
    if isinstance(image_size, list) or isinstance(image_size, tuple):
        image_size = int(image_size[-1])
    image_mean = getattr(cfg.preprocessing, "mean", [127, 127, 127])    
    image_std  = float(getattr(cfg.preprocessing, "std", 128.0))
    if isinstance(image_mean, list):
        image_mean = np.array(image_mean, dtype=np.float32)

    iou_thr = float(getattr(cfg.postprocessing, "IoU_eval_thresh", 0.5) or 0.5)
    train_transform = TrainAugmentation(image_size, image_mean, image_std)
    test_transform  = TestTransform(image_size, image_mean, image_std)
    ssd_cfg = MOBILENET_CONFIG()
    # MatchPrior is the "target_transform"
    target_transform = MatchPrior(
        ssd_cfg.priors,
        ssd_cfg.center_variance,
        ssd_cfg.size_variance,
        iou_thr,
    )

    return train_transform, test_transform, target_transform

def get_ssd_voc_train_loader(cfg):
    # train_roots = list(getattr(cfg.dataset, "training_path", []) or [])
    train_images_path = cfg.dataset.train_images_path
    train_annotations_path = cfg.dataset.train_annotations_path
    train_split = cfg.dataset.train_split
    
    if not train_images_path or not train_annotations_path or not train_split :
        raise ValueError("cfg.dataset.val_images_path, val_annotations_path, val_split must be a non-empty.")

    batch_size  = int(getattr(cfg.training, "batch_size", 32))
    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    train_transform, _, target_transform = _ssd_voc_build_transforms(cfg)


    # datasets = []
    # for root in train_roots:
    train_dataset = VOCDataset(
        cfg,
        train_images_path, 
        train_annotations_path, 
        train_split,
        # root,
        transform=train_transform,
        target_transform=target_transform,
    )
    # datasets.append(ds)

    # train_dataset = ConcatDataset(datasets)
    # train_dataset = ConcatDataset(ds)

    return DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )

def get_ssd_voc_validation_loader(cfg):
    
    val_images_path = cfg.dataset.val_images_path
    val_annotations_path = cfg.dataset.val_annotations_path
    val_split = cfg.dataset.val_split
    
    if not val_images_path or not val_annotations_path or not val_split :
        raise ValueError("cfg.dataset.val_images_path, val_annotations_path, val_split must be a non-empty.")
    
    # val_root = getattr(cfg.dataset, "validation_path", None)
    # if not val_root:
    #     raise ValueError("cfg.dataset.validation_path must be provided for VOC validation.")

    batch_size  = int(getattr(cfg.training, "batch_size", 32))
    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, target_transform = _ssd_voc_build_transforms(cfg)

    val_dataset = VOCDataset(
        cfg,
        val_images_path, 
        val_annotations_path, 
        val_split,
        # val_root,
        transform=test_transform,
        target_transform=target_transform,
        is_test=True,
    )

    return DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )

def get_ssd_voc_test_loader(cfg): 
    
    test_split = cfg.dataset.test_split or cfg.dataset.val_split
    test_images_path = cfg.dataset.test_images_path or cfg.dataset.val_images_path
    test_annotations_path = cfg.dataset.test_annotations_path or cfg.dataset.val_annotations_path    
    
    if not test_images_path or not test_annotations_path or not test_split :
        raise ValueError("cfg.dataset.test_images_path, test_annotations_path, test_split must be a non-empty.")
    
    # test_root = getattr(cfg.dataset, "test_path", None) or getattr(cfg.dataset, "val_dataset", None)
    # if not test_root:
    #     raise ValueError("cfg.dataset.test_dataset or cfg.dataset.val_dataset must be provided for VOC test.")

    batch_size  = int(getattr(cfg.training, "batch_size", 32))
    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, target_transform = _ssd_voc_build_transforms(cfg)

    test_dataset = VOCDataset(
        cfg,
        test_images_path, 
        test_annotations_path, 
        test_split,
        # test_root,
        transform=test_transform,
        target_transform=target_transform,
        is_test=True,
    )

    return DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )

def get_ssd_voc_prediction_loader(cfg):
    prediction_path = getattr(cfg.dataset, "prediction_path", None)
    
    if not prediction_path:
        return None

    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, _ = _ssd_voc_build_transforms(cfg)

    pred_dataset = SSDPredictionDataset(prediction_path, transform=test_transform)
    
    return DataLoader(
        pred_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )

def get_ssd_voc_quantization_loader(cfg, train_loader):
    quant_path = getattr(cfg.dataset, "quantization_path", None)
    train_path = cfg.dataset.train_images_path
    quant_split = float(getattr(cfg.dataset, "quantization_split", 0.1) or 0.1)

    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, _ = _ssd_voc_build_transforms(cfg)

    # 1) explicit quantization path
    if quant_path:
        quant_ds = SSDPredictionDataset(quant_path, transform=test_transform)
        n = max(1, int(len(quant_ds) * quant_split))
        idxs = random.sample(range(len(quant_ds)), min(n, len(quant_ds)))
        subset = Subset(quant_ds, idxs)
        return DataLoader(
            subset,
            batch_size=1,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )

    # 2) fallback: subset of train dataset (only if quantization config section exists)
    if train_loader is not None and getattr(cfg, "quantization", None) is not None:
        quant_ds = SSDPredictionDataset(train_path, transform=test_transform)
        n = max(1, int(len(quant_ds) * quant_split))
        idxs = random.sample(range(len(quant_ds)), min(n, len(quant_ds)))
        subset = Subset(quant_ds, idxs)
        return DataLoader(
            subset,
            batch_size=32,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )

    return None

@DATASET_WRAPPER_REGISTRY.register(
    dataset_name="voc",
    use_case="object_detection",
    framework="torch",
)
def get_voc_ssd_dataloaders(cfg):
    types = get_ssd_voc_dataloader_type_dict(cfg)
    # print(types)

    train_loader = get_ssd_voc_train_loader(cfg) if types["train"] else None
    val_loader   = get_ssd_voc_validation_loader(cfg) if types["valid"] else None
    test_loader  = get_ssd_voc_test_loader(cfg) if types["test"] else None

    quant_loader = get_ssd_voc_quantization_loader(cfg, train_loader) if types["quantization"] else None
    pred_loader  = get_ssd_voc_prediction_loader(cfg) if types["predict"] else None

    return {
        "train": train_loader,
        "valid": val_loader,
        "test": test_loader,
        "quantization": quant_loader,
        "predict": pred_loader,
    }

def get_ssd_coco_dataloader_type_dict(cfg):
    train = valid = test = quantization = predict = False

    # training requires both images+anns
    if getattr(cfg.dataset, "train_images_path", None) and getattr(cfg.dataset, "train_annotations_path", None):
        train = True

    # valid requires both images+anns
    if getattr(cfg.dataset, "val_images_path", None) and getattr(cfg.dataset, "val_annotations_path", None):
        valid = True

    # test optional (fallback to val if val exists)
    if (
        (getattr(cfg.dataset, "test_images_path", None) and getattr(cfg.dataset, "test_annotations_path", None))
        or (getattr(cfg.dataset, "val_images_path", None) and getattr(cfg.dataset, "val_annotations_path", None))
    ):
        test = True

    # quant: either explicit path OR fallback to train subset
    if getattr(cfg.dataset, "quantization_path", None) or train:
        quantization = True

    # predict: if you provide prediction_path
    if getattr(cfg.dataset, "prediction_path", None):
        predict = True

    return {
        "train": train,
        "valid": valid,
        "test": test,
        "quantization": quantization,
        "predict": predict,
    }


def _ssd_coco_build_transforms(cfg):
    # image size has to be int
    image_size = getattr(cfg.model, "input_shape", 300)
    if isinstance(image_size, (list, tuple)):
        image_size = int(image_size[-1])

    image_mean = getattr(cfg.preprocessing, "mean", [127, 127, 127])
    image_std  = float(getattr(cfg.preprocessing, "std", 128.0))
    if isinstance(image_mean, list):
        image_mean = np.array(image_mean, dtype=np.float32)

    iou_thr = float(getattr(cfg.postprocessing, "IoU_eval_thresh", 0.5) or 0.5)

    train_transform = TrainAugmentation(image_size, image_mean, image_std)
    test_transform  = TestTransform(image_size, image_mean, image_std)

    ssd_cfg = MOBILENET_CONFIG()

    target_transform = MatchPrior(
        ssd_cfg.priors,
        ssd_cfg.center_variance,
        ssd_cfg.size_variance,
        iou_thr,
    )
    return train_transform, test_transform, target_transform


def get_ssd_coco_train_loader(cfg):
    train_images_path = getattr(cfg.dataset, "train_images_path", None)
    train_annotations_path = getattr(cfg.dataset, "train_annotations_path", None)
    if not train_images_path or not train_annotations_path:
        raise ValueError("cfg.dataset.train_images_path and cfg.dataset.train_annotations_path must be provided.")

    batch_size  = int(getattr(cfg.training, "batch_size", 32))
    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    train_transform, _, target_transform = _ssd_coco_build_transforms(cfg)

    # - skip_annotations=False -> load GT
    # - filter empty GT for training to avoid inf reg loss
    train_dataset = CocoDataset(
        images_path=train_images_path,
        annotations_path=train_annotations_path,
        transform=train_transform,
        target_transform=target_transform,
        skip_annotations=False,
        filter_empty_gt=True,   # for SSD training stability
    )

    return DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )


def get_ssd_coco_validation_loader(cfg):
    val_images_path = getattr(cfg.dataset, "val_images_path", None)
    val_annotations_path = getattr(cfg.dataset, "val_annotations_path", None)
    if not val_images_path or not val_annotations_path:
        raise ValueError("cfg.dataset.val_images_path and cfg.dataset.val_annotations_path must be provided.")

    batch_size  = int(getattr(cfg.training, "batch_size", 32))
    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, target_transform = _ssd_coco_build_transforms(cfg)

    # For loss eval keeping empty GT filtered is optional.
    val_dataset = CocoDataset(
        images_path=val_images_path,
        annotations_path=val_annotations_path,
        transform=test_transform,
        target_transform=target_transform,
        skip_annotations=False,
        filter_empty_gt=True,
    )

    return DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )


def get_ssd_coco_test_loader(cfg):
    # fallback to val if test not provided
    test_images_path = getattr(cfg.dataset, "test_images_path", None) or getattr(cfg.dataset, "val_images_path", None)
    test_annotations_path = getattr(cfg.dataset, "test_annotations_path", None) or getattr(cfg.dataset, "val_annotations_path", None)

    if not test_images_path or not test_annotations_path:
        raise ValueError("Need test_images_path+test_annotations_path (or val fallback) for COCO test loader.")

    batch_size  = int(getattr(cfg.training, "batch_size", 32))
    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, target_transform = _ssd_coco_build_transforms(cfg)

    test_dataset = CocoDataset(
        images_path=test_images_path,
        annotations_path=test_annotations_path,
        transform=test_transform,
        target_transform=target_transform,
        skip_annotations=False,
        filter_empty_gt=True,
    )

    return DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )


def get_ssd_coco_prediction_loader(cfg):
    prediction_path = getattr(cfg.dataset, "prediction_path", None)
    if not prediction_path:
        return None

    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, _ = _ssd_coco_build_transforms(cfg)

    pred_dataset = SSDPredictionDataset(prediction_path, transform=test_transform)
    return DataLoader(
        pred_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )


def get_ssd_coco_quantization_loader(cfg, train_loader):
    quant_path  = getattr(cfg.dataset, "quantization_path", None)
    train_path = cfg.dataset.train_images_path 
    quant_split = float(getattr(cfg.dataset, "quantization_split", 0.1) or 0.1)

    num_workers = int(getattr(cfg.dataset, "num_workers", 4))
    pin_memory  = bool(torch.cuda.is_available() and getattr(cfg.general, "use_cuda", True))

    _, test_transform, _ = _ssd_coco_build_transforms(cfg)

    # 1) explicit quantization path
    if quant_path:
        quant_ds = SSDPredictionDataset(quant_path, transform=test_transform)
        n = max(1, int(len(quant_ds) * quant_split))
        idxs = random.sample(range(len(quant_ds)), min(n, len(quant_ds)))
        subset = Subset(quant_ds, idxs)
        return DataLoader(
            subset,
            batch_size=1,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )

    # 2) fallback: subset of train dataset
    if train_loader is not None and getattr(cfg, "quantization", None) is not None:
        quant_ds = SSDPredictionDataset(train_path, transform=test_transform)
        # base_train_ds = train_loader.dataset
        n = max(1, int(len(quant_ds) * quant_split))
        idxs = random.sample(range(len(quant_ds)), min(n, len(quant_ds)))
        subset = Subset(quant_ds, idxs)
        return DataLoader(
            subset,
            batch_size=32,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        )

    return None


# @DATASET_WRAPPER_REGISTRY.register(
#     dataset_name="coco_ssd",
#     use_case="object_detection",
#     framework="torch",
# )
def get_coco_ssd_dataloaders(cfg):
    types = get_ssd_coco_dataloader_type_dict(cfg)

    train_loader = get_ssd_coco_train_loader(cfg) if types["train"] else None
    val_loader   = get_ssd_coco_validation_loader(cfg) if types["valid"] else None
    test_loader  = get_ssd_coco_test_loader(cfg) if types["test"] else None

    quant_loader = get_ssd_coco_quantization_loader(cfg, train_loader) if types["quantization"] else None
    pred_loader  = get_ssd_coco_prediction_loader(cfg) if types["predict"] else None

    return {
        "train": train_loader,
        "valid": val_loader,
        "test": test_loader,
        "quantization": quant_loader,
        "predict": pred_loader,
    }
