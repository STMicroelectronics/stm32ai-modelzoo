# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from pathlib import Path
from urllib.parse import urljoin
from typing import Any
from common.model_utils.torch_utils import load_pretrained_weights
from common.registries.model_registry import MODEL_WRAPPER_REGISTRY
from common.utils import LOGGER
from object_detection.pt.src.models.checkpoints import (CHECKPOINT_STORAGE_URL,
                                                        model_checkpoints)
from object_detection.pt.src.models.yolod.detection.detectors.yolod_nano import YOLODNano
from object_detection.pt.src.models.yolod.detection.detectors.yolod_tiny import YOLODTiny
from object_detection.pt.src.models.yolod.detection.detectors.styolo_pico import STYOLOPico
from object_detection.pt.src.models.yolod.detection.detectors.styolo_nano import STYOLONano
from object_detection.pt.src.models.yolod.detection.detectors.styolo_tiny import STYOLOTiny
from object_detection.pt.src.models.yolod.detection.detectors.styolo_milli import STYOLOMilli
from object_detection.pt.src.models.yolod.detection.detectors.styolo_micro import STYOLOMicro

def load_checkpoint_od(model, cfg):
    """
    Load pretrained weights into an already-defined model.
    """
    pretrained_dataset = cfg.model.pretrained_dataset.lower()
    model_name = cfg.model.model_name

    # Direct model path — highest priority
    if getattr(cfg.model, "model_path", None):
        ckpt_path = cfg.model.model_path
        model = load_pretrained_weights(model, str(ckpt_path))
        print(f"Loaded {model_name} pretrained on model_path you provided")
        return model

    elif pretrained_dataset == 'coco' or pretrained_dataset == 'coco_person':
        checkpoint_key = f"{model_name}_dataset{pretrained_dataset}_res{cfg.model.pretrained_input_shape[-1]}"
        if checkpoint_key not in model_checkpoints:
            print(f"No checkpoint found for {checkpoint_key}")
            return model
        ckpt_path = urljoin(CHECKPOINT_STORAGE_URL + "/", model_checkpoints[checkpoint_key])
        model = load_pretrained_weights(model, str(ckpt_path))
        print(f"Loaded {model_name} pretrained on {pretrained_dataset}")
        return model
    elif cfg.model.pretrained:  
        if cfg.model.pretrained_dataset == 'coco': 
            checkpoint_key = f'{cfg.model.model_name}_dataset{cfg.model.pretrained_dataset}_res{cfg.model.pretrained_input_shape[-1]}'
            ckpt_path = str(Path(CHECKPOINT_STORAGE_URL, model_checkpoints[checkpoint_key]))
            model = load_pretrained_weights(model, ckpt_path, device='cuda')
        return model
    else : 
        return model 

@MODEL_WRAPPER_REGISTRY.register(
    model_name="st_yolodv1nano_actrelu_pt", use_case="object_detection", framework="torch", has_checkpoint=True
)
def get_yolo_nano(cfg):
    model = YOLODNano(cfg).get_model()
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model

@MODEL_WRAPPER_REGISTRY.register(
    model_name="st_yolodv1tiny_actrelu_pt", use_case="object_detection", framework="torch", has_checkpoint=True
)
def get_yolo_tiny(cfg):
    model = YOLODTiny(cfg).get_model()
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model

@MODEL_WRAPPER_REGISTRY.register( 
    model_name="st_yolodv2micro_actrelu_pt", use_case="object_detection", framework="torch", has_checkpoint=False
)
def get_styolo_micro(cfg):
    model = STYOLOMicro(cfg).get_model()
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model

@MODEL_WRAPPER_REGISTRY.register(
    model_name="st_yolodv2nano_actrelu_pt", use_case="object_detection", framework="torch", has_checkpoint=False
)
def get_styolo_nano(cfg):
    model = STYOLONano(cfg).get_model()
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model

@MODEL_WRAPPER_REGISTRY.register(
    model_name="st_yolodv2pico_actrelu_pt", use_case="object_detection", framework="torch", has_checkpoint=False
)
def get_styolo_pico(cfg):
    model = STYOLOPico(cfg).get_model()
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model

@MODEL_WRAPPER_REGISTRY.register(
    model_name="st_yolodv2tiny_actrelu_pt", use_case="object_detection", framework="torch", has_checkpoint=False
)
def get_styolo_tiny(cfg):
    model = STYOLOTiny(cfg).get_model()
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model

@MODEL_WRAPPER_REGISTRY.register(
    model_name="st_yolodv2milli_actrelu_pt", use_case="object_detection", framework="torch", has_checkpoint=False
)
def get_styolo_milli(cfg):
    model = STYOLOMilli(cfg).get_model()
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model