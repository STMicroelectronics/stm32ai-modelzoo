# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import logging 
from .defaults import  DEFAULT_MODEL_CFG, DEFAULT_DATASET_CFG, DEFAULT_TRAINING_CFG
from types import SimpleNamespace


def merge_cfg(defaults: dict, user_cfg: dict, prefix=""):
    merged = {}
    used_defaults = {}

    for k, v in defaults.items():
        if k not in user_cfg or user_cfg[k] in [None, "", []]:
            merged[k] = v
            used_defaults[k] = v
        else:
            merged[k] = user_cfg[k]

    # keep extra user keys
    for k, v in user_cfg.items():
        if k not in merged:
            merged[k] = v

    return merged, used_defaults

def normalize_cfg(cfg):
    cfg.model, model_defaults = merge_cfg(
        DEFAULT_MODEL_CFG, getattr(cfg, "model", {})
    )
    cfg.dataset, dataset_defaults = merge_cfg(
        DEFAULT_DATASET_CFG, getattr(cfg, "dataset", {})
    )
    cfg.training, training_defaults = merge_cfg(
        DEFAULT_TRAINING_CFG, getattr(cfg, "training", {})
    )

    return cfg, {
        "model": model_defaults,
        "dataset": dataset_defaults,
        "training": training_defaults,
    }
def log_used_defaults(defaults_dict):
    for section, values in defaults_dict.items():
        if not values:
            continue
        logging.info(f"[Config] Using default values for `{section}`:")
        for k, v in values.items():
            logging.info(f"    {section}.{k} = {v}")

def dict_to_ns(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_ns(v) for k, v in d.items()})
    if isinstance(d, list):
        return [dict_to_ns(x) for x in d]
    return d
