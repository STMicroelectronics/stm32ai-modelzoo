# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import collections
import fnmatch
import texttable
import os

# for common registries
from common.registries.dataset_registry import DATASET_WRAPPER_REGISTRY
from common.registries.model_registry import MODEL_WRAPPER_REGISTRY
from common.registries.trainer_registry import TRAINER_WRAPPER_REGISTRY
from common.registries.quantizer_registry import QUANTIZER_WRAPPER_REGISTRY
from common.registries.evaluator_registry import EVALUATOR_WRAPPER_REGISTRY
from common.registries.predictor_registry import PREDICTOR_WRAPPER_REGISTRY
from common.utils import LOGGER


# for tensorflow based object detection
import object_detection.tf.wrappers.models.standard_models
import object_detection.tf.wrappers.models.custom_models
import object_detection.tf.wrappers.datasets            # this is done so that registeration happens before get_dataloader is called
import object_detection.tf.wrappers.prediction          # this is done so that registeration happens before get_predictor is called
import object_detection.tf.wrappers.evaluation          # this is done so that registeration happens before get_evaluator is called
import object_detection.tf.wrappers.quantization        # this is done so that registeration happens before get_quantizer is called
import object_detection.tf.wrappers.training            # this is done so that registeration happens before get_trainer is called

# for pytorch based object detection
import object_detection.pt.wrappers.models
import object_detection.pt.wrappers.datasets
import object_detection.pt.wrappers.training
import object_detection.pt.wrappers.evaluation

from common.model_utils.tf_model_loader import load_model_from_path
from pathlib import Path
import torch
import tensorflow as tf
import onnxruntime


__all__ = ['get_dataloaders',
           "get_model",
           "get_trainer",
           "get_quantizer",
           "get_evaluator",
           "get_predictor",
           "list_models",
           "list_models_by_dataset",]

def get_dataloaders(cfg):
    """
    Tries to find a matching dataloader creation wrapper function in the registry and uses it to create a new dataloder dict.

    returns datasplits in the following format:
    {
       'train': train_data_loader,
       'valid': valid_data_loader,
       'quantization': quantization_data_loader,
       'test' : test_data_loader
       'predict' : predict_data_loader
    }
    TODO : add other keys like val, quant
    """
    #if mode not in ["benchmarking", "deployment"]:
    if cfg.dataset.dataset_name != "<unnamed>":
        data_split_wrapper_fn = DATASET_WRAPPER_REGISTRY.get(framework=cfg.model.framework,
                                                             dataset_name=cfg.dataset.dataset_name,
                                                             use_case=cfg.use_case)
        # The registered function expects a single cfg object
        return data_split_wrapper_fn(cfg)
    else:
        return {'train': None, 'valid': None, 'quantization': None, 'test': None, 'predict': None,}


def get_model(cfg):
    """
    Tries to find a matching model creation wrapper function in the registry and uses it to create a new model object.
    """
    allowed_exts = [".keras", ".h5", ".tflite", ".onnx"]
    model_path = getattr(cfg.model, "model_path", None)
    if model_path:
        _, ext = os.path.splitext(model_path)
        if ext.lower() in allowed_exts:
            LOGGER.info(f"Loading model from {model_path}")
            model = load_model_from_path(cfg, model_path)
            return model
    #        LOGGER.info(f"Loading model from {model_path}")
    #        _, ext = os.path.splitext(model_path)
    #        if ext.lower() in allowed_exts:
    #            model = load_model_from_path(cfg, model_path)
    #
    # Covers cases where there is no model_path provided, or pt checkpoints

    model_func = MODEL_WRAPPER_REGISTRY.get(model_name=cfg.model.model_name.lower(),
                                                use_case=cfg.use_case,
                                                framework=cfg.model.framework)

    # The registered function expects a single cfg object
    model = model_func(cfg)
    saved_model_dir = os.path.join(cfg.output_dir, cfg.general.saved_models_dir)
    os.makedirs(saved_model_dir, exist_ok=True)
    if cfg.model.framework == 'tf':
        saved_model = Path(saved_model_dir, cfg.model.model_name, cfg.model.model_name+".keras")
        saved_model.parent.mkdir(exist_ok=True)
        model.save(saved_model)
        setattr(model, 'model_path', saved_model)
        cfg.model.model_path = saved_model

    return model


def get_trainer(dataloaders, model, cfg):
    """
    Returns an instance of the trainer class from registry.
    """
    trainer_cls = TRAINER_WRAPPER_REGISTRY.get(
        trainer_name=cfg.training.trainer_name,
        framework=cfg.model.framework,
        use_case=cfg.use_case
    )

    # The registered function expects dataloaders, model and full config
    return trainer_cls(dataloaders=dataloaders, model=model, cfg=cfg)


def get_quantizer(dataloaders, model, cfg):
    """
    Returns an instance of the quantizer class from registry.
    """
    quantizer_cls = QUANTIZER_WRAPPER_REGISTRY.get(
        quantizer_name=cfg.quantization.quantizer.lower(),
        framework=cfg.model.framework,
        use_case=cfg.use_case
    )

    # The registered function expects dataloaders, model and full config
    return quantizer_cls(dataloaders=dataloaders, model=model, cfg=cfg)

def get_evaluator(dataloaders, model, cfg):
    """
    Returns an instance of the evaluator class from registry.
    """
    if isinstance(model, tf.keras.Model):
        evaluator_name = "keras_evaluator"
    elif 'Interpreter' in str(type(model)):
        evaluator_name = "tflite_evaluator"
    elif isinstance(model, onnxruntime.InferenceSession):
        evaluator_name = "onnx_evaluator"
    elif isinstance(model, torch.nn.Module):
        model_name = cfg.model.model_name.lower()
        # Will not work if user is providing custom format.
        if "ssd" in model_name:
            evaluator_name = "ssd" 
        # ---- YOLOD----
        elif "yolod" in model_name:
            evaluator_name = "yolod"
        else : 
            evaluator_name = "torch_evaluator"        
    else:
        raise TypeError("Unsupported model type for evaluation")

    evaluator_cls = EVALUATOR_WRAPPER_REGISTRY.get(
        evaluator_name=evaluator_name,
        framework=cfg.model.framework,
        use_case=cfg.use_case,   
    )

    return evaluator_cls(dataloaders=dataloaders, model=model, cfg=cfg)


def get_predictor(dataloaders, model, cfg):
    """
    Returns an instance of the predictor class from registry.
    """
    if isinstance(model, tf.keras.Model):
        predictor_name = "keras_predictor"
    elif 'Interpreter' in str(type(model)):
        predictor_name = "tflite_predictor"
    elif isinstance(model, onnxruntime.InferenceSession):
        predictor_name = "onnx_predictor"
    else:
        raise TypeError("Unsupported model type for predictor")

    predictor_cls = PREDICTOR_WRAPPER_REGISTRY.get(
        predictor_name=predictor_name,
        framework=cfg.model.framework,
        use_case=cfg.use_case
    )

    # The registered function expects dataloaders, model and full config
    return predictor_cls(dataloaders=dataloaders, model=model, cfg=cfg)


def list_models(
    filter_string='',
    match_all=True,
    print_table=True,
    with_checkpoint=False,
):
    """
    A helper function to list all existing models based on text filters
    You can provide list of strings like model_name, use_case, framework.
    It will print a table of corresponding available models

    :param filter: a string or list of strings containing model name, use_case , framework or "model_name_use_case_framework"
    to use as a filter
    :param print_table: Whether to print a table with matched models (if False, return as a list)
    """
    #print(MODEL_WRAPPER_REGISTRY.registry_dict.keys())
    if with_checkpoint:
        all_model_keys = MODEL_WRAPPER_REGISTRY.pretrained_models.keys()
    else:
        all_model_keys = MODEL_WRAPPER_REGISTRY.registry_dict.keys()
    all_models = {
        model_key.model_name + '_' + model_key.use_case + '_' + model_key.framework: model_key
        for model_key in all_model_keys
    }
    models = set()
    include_filters = (
        filter_string if isinstance(filter_string, (tuple, list)) else [filter_string]
    )
    matched_sets = []
    for keyword in include_filters:
        matched = set(fnmatch.filter(all_models.keys(), f'*{keyword}*'))
        matched_sets.append(matched)   # append always, even if empty

    if match_all:
        # If ANY matched set is empty → intersection is empty
        if any(len(s) == 0 for s in matched_sets):
            models = set()
        else:
            models = set.intersection(*matched_sets)
    else:
        # match_any behavior (if you need it)
        models = set().union(*matched_sets)

    found_model_keys = [all_models[model] for model in sorted(models)]

    if not print_table:
        return found_model_keys

    # Build a table with counts per model name (dataset_name removed)
    model_counts = collections.Counter(mk.model_name for mk in found_model_keys)

    table = texttable.Texttable()
    rows = [['Model name', 'Count']]
    for model_name, count in model_counts.items():
        rows.append([model_name, count])

    table.add_rows(rows)
    LOGGER.info(table.draw())

    return found_model_keys


def list_models_by_dataset(dataset_name, with_checkpoint=False):
    return [
        model_key.model_name
        for model_key in list_models(dataset_name, print_table=False, with_checkpoint=with_checkpoint)
        if model_key.dataset_name == dataset_name
    ]
