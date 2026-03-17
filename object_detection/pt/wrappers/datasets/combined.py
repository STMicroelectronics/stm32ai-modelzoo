from common.registries.dataset_registry import DATASET_WRAPPER_REGISTRY

from object_detection.pt.wrappers.datasets.yolod import get_coco_detection
from object_detection.pt.wrappers.datasets.ssd import get_coco_ssd_dataloaders

@DATASET_WRAPPER_REGISTRY.register(framework='torch', dataset_name='coco', use_case='object_detection')
def get_coco_dataloaders(cfg):
    if "yolod" in cfg.model.model_name:
        return get_coco_detection(cfg)
    elif "ssd" in cfg.model.model_name:
        return get_coco_ssd_dataloaders(cfg)
    else:
        raise ValueError("cfg.model.model_name should have ssd or yolod in it")