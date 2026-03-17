# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
DEFAULT_MODEL_CFG = {
    "framework": "torch",
    "model_type": "st_yolod",
    "model_name": None,
    "pretrained": False,
    "pretrained_dataset": None,
    "input_shape": [3, 640, 640],
    "pretrained_input_shape": None,
    "depthwise": False,
    "depth": 0.33,
    "width": 0.25,
    "num_classes": None,
    "act": "silu",
}

DEFAULT_DATASET_CFG = {
    "format": "coco",
    "dataset_name": None,
    "seed": 42,
    "num_workers": 4,
    "data_dir": None,

    "train_images_path": None,
    "train_annotations_path": None,
    "val_images_path": None,
    "val_annotations_path": None,

    "prediction_path": None,
    "quantization_path": None,
    "quantization_split": 0.1,

    "mosaic_prob": 1.0,
    "mixup_prob": 1.0,
    "hsv_prob": 1.0,
    "flip_prob": 0.5,
    "degrees": 10.0,
    "translate": 0.1,
    "shear": 2.0,
    "enable_mixup": True,
}

DEFAULT_TRAINING_CFG = {
    "trainer_name": "yolod",
    "batch_size": 32,
    "epochs": 300,
    "warmup_epochs": 1,
    "warmup_lr": 0.0,
    "min_lr_ratio": 0.05,
    "scheduler": "yoloxwarmcos",
    "no_aug_epochs": 15,
    "ema": True,
    "weight_decay": 5e-4,
    "momentum": 0.9,
    "print_interval": 50,
    "eval_interval": 1,
    "fp16": True,
}