# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import urllib.parse as urlparse
from urllib.parse import urljoin
from collections import namedtuple
from typing import Any, Callable, Dict, Tuple

from torch.hub import load_state_dict_from_url

from common.registries.model_registry import MODEL_WRAPPER_REGISTRY
from object_detection.pt.src.models.ssd.detectors.config.mobilenetv1_ssd_config import \
    MOBILENET_CONFIG
from object_detection.pt.src.models.ssd.detectors.config.squeezenet_ssd_config import \
    SQUEEZENET_CONFIG
from object_detection.pt.src.models.ssd.detectors.mobilenet_v2_ssd import \
    create_mobilenetv2_ssd
from object_detection.pt.src.models.ssd.detectors.mobilenet_v2_ssd_lite import \
    create_mobilenetv2_ssd_lite
from object_detection.pt.src.models.ssd.detectors.mobilenetv1_ssd import \
    create_mobilenetv1_ssd
from object_detection.pt.src.models.ssd.detectors.mobilenetv1_ssd_lite import \
    create_mobilenetv1_ssd_lite
from object_detection.pt.src.models.ssd.detectors.mobilenetv3_ssd_lite import (
    create_mobilenetv3_large_ssd_lite, create_mobilenetv3_small_ssd_lite)
from object_detection.pt.src.models.ssd.detectors.squeezenet_ssd_lite import \
    create_squeezenet_ssd_lite
from object_detection.pt.src.models.checkpoints import CHECKPOINT_STORAGE_URL, model_checkpoints
from pathlib import Path
from common.model_utils.torch_utils import load_pretrained_weights

def load_checkpoint_od(model, cfg):
    """
    Load pretrained weights into an already-defined model.
    """
    dataset = cfg.model.pretrained_dataset.lower()
    model_name = cfg.model.model_name

    # Direct model path — highest priority
    if getattr(cfg.model, "model_path", None):
        ckpt_path = cfg.model.model_path
        model = load_pretrained_weights(model, str(ckpt_path))
        print(f"Loaded {model_name} pretrained on model_path you provided")
        return model

    elif dataset in ["voc", "coco", "coco_person"]:
        checkpoint_key = f"{model_name}_dataset{dataset}_res{cfg.model.input_shape[1]}"
        if checkpoint_key not in model_checkpoints:
            print(f"No checkpoint found for {checkpoint_key}")
            return model
        ckpt_path = urljoin(CHECKPOINT_STORAGE_URL + "/", model_checkpoints[checkpoint_key])
        model = load_pretrained_weights(model, str(ckpt_path))
        print(f"Loaded {model_name} pretrained on {dataset}")
        return model
    else:
        raise ValueError(
            f'Could not find a pretrained checkpoint for model {model_name} on dataset {dataset}. \n'
            'Use pretrained=False if you want to create a untrained model.'
        )


def load_state_dict_partial(model, pretrained_dict):
    model_dict = model.state_dict()
    pretrained_dict = {
        k: v
        for k, v in pretrained_dict.items()
        if k in model_dict and v.size() == model_dict[k].size()
    }
    model_dict.update(pretrained_dict)
    model.load_state_dict(model_dict)
    print(f'Loaded {len(pretrained_dict)}/{len(model_dict)} modules')

def load_pretrained_weights_tmp(model, checkpoint_url, progress, device):
    pretrained_dict = load_state_dict_from_url(
        checkpoint_url,
        progress=progress,
        check_hash=True,
        map_location=device,
    )
    load_state_dict_partial(model, pretrained_dict)
    return model

__all__ = []


@MODEL_WRAPPER_REGISTRY.register(model_name='ssd_mobilenetv1_pt',
        use_case='object_detection', framework='torch')
def get_mb1_ssd(cfg):
    
    model = create_mobilenetv1_ssd(cfg.model.num_classes+1)
    if cfg.model.pretrained : 
        base_net_path = urljoin(CHECKPOINT_STORAGE_URL + "/", model_checkpoints['mobilenetv1_base'])
        model.init_from_base_net(base_net_path)
        print(f"Init from base net for SSD {base_net_path}")
    config = MOBILENET_CONFIG()
    model.config = config
#    model.priors = config.priors.to('cuda')
    model.priors = config.priors.to(cfg.device)
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)

    return model.to(cfg.device)
#    return model.to('cuda')

@MODEL_WRAPPER_REGISTRY.register(model_name='ssdlite_mobilenetv1_pt',
        use_case='object_detection', framework='torch')
def get_mb1_ssd_lite(cfg):
    
    model = create_mobilenetv1_ssd_lite(cfg.model.num_classes+1)
    if cfg.model.pretrained : 
        base_net_path = urljoin(CHECKPOINT_STORAGE_URL + "/", model_checkpoints['mobilenetv1_base'])
        model.init_from_base_net(base_net_path)
        print(f"Init from base net for SSD {base_net_path}")
    config = MOBILENET_CONFIG()
    model.config = config
#    model.priors = config.priors.to('cuda')
    model.priors = config.priors.to(cfg.device)
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model.to(cfg.device)
#    return model.to('cuda')

@MODEL_WRAPPER_REGISTRY.register(model_name='ssd_mobilenetv2_pt',
        use_case='object_detection', framework='torch')
def get_mb2_ssd(cfg):
    width_mult = getattr(cfg.model, "width_mult", 1.0)
    model = create_mobilenetv2_ssd(cfg.model.num_classes+1, width_mult)
    if cfg.model.pretrained : 
        base_net_path = urljoin(CHECKPOINT_STORAGE_URL + "/", model_checkpoints['mobilenetv2_base'])
        model.init_from_base_net(base_net_path)
        print(f"Init from base net for SSD {base_net_path}")
    config = MOBILENET_CONFIG()
    model.config = config
#    model.priors = config.priors.to('cuda')
    model.priors = config.priors.to(cfg.device)
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model.to(cfg.device)
#    return model.to('cuda')

@MODEL_WRAPPER_REGISTRY.register(model_name='ssdlite_mobilenetv2_pt',
        use_case='object_detection', framework='torch')
def get_mb2_ssd_lite(cfg):
    width_mult = getattr(cfg.model, "width_mult", 1.0)
    model = create_mobilenetv2_ssd_lite(cfg.model.num_classes+1, width_mult)
    if cfg.model.pretrained : 
        base_net_path = urljoin(CHECKPOINT_STORAGE_URL + "/", model_checkpoints['mobilenetv2_base'])
        model.init_from_base_net(base_net_path)
        print(f"Init from base net for SSD {base_net_path}")
    config = MOBILENET_CONFIG()
    model.config = config
#    model.priors = config.priors.to('cuda')
    model.priors = config.priors.to(cfg.device)
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model.to(cfg.device)
#    return model.to('cuda')

@MODEL_WRAPPER_REGISTRY.register(model_name='ssdlite_mobilenetv3small_pt',
        use_case='object_detection', framework='torch')
def get_mb3_small_ssd_lite(cfg):
    width_mult = getattr(cfg.model, "width_mult", 1.0)
    model = create_mobilenetv3_small_ssd_lite(cfg.model.num_classes+1, width_mult)
    config = MOBILENET_CONFIG()
    model.config = config
#    model.priors = config.priors.to('cuda')
    model.priors = config.priors.to(cfg.device)
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model.to(cfg.device)
#    return model.to('cuda')

@MODEL_WRAPPER_REGISTRY.register(model_name='ssdlite_mobilenetv3large_pt',
        use_case='object_detection', framework='torch')
def get_mb3_large_ssd_lite(cfg):
    width_mult = getattr(cfg.model, "width_mult", 1.0)
    model = create_mobilenetv3_large_ssd_lite(cfg.model.num_classes+1, width_mult)
    config = MOBILENET_CONFIG()
    model.config = config
#    model.priors = config.priors.to('cuda')
    model.priors = config.priors.to(cfg.device)
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model.to(cfg.device)
#    return model.to('cuda')

@MODEL_WRAPPER_REGISTRY.register(model_name='ssdlite_squeezenet_pt',
        use_case='object_detection', framework='torch')
def get_squeezenet_ssd_lite(cfg):
    width_mult = getattr(cfg.model, "width_mult", 1.0)
    model = create_squeezenet_ssd_lite(cfg.model.num_classes+1, width_mult)
    config = SQUEEZENET_CONFIG()
    model.config = config
#    model.priors = config.priors.to('cuda')
    model.priors = config.priors.to(cfg.device)
    if cfg.model.pretrained:
        model = load_checkpoint_od(model, cfg)
    return model.to(cfg.device)
#    return model.to('cuda')