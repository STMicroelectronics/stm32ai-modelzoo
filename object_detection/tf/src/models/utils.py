#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import tensorflow as tf
from omegaconf import DictConfig
from tensorflow.keras import layers

def prepare_kwargs_for_model(cfg: DictConfig):

    dropout = cfg.training.dropout if cfg.training and 'dropout' in cfg.training else None
    model_kwargs = {
        'pretrained': getattr(cfg.model, 'pretrained', True),
        'num_classes': getattr(cfg.dataset, 'num_classes', 80),
        'model_type': getattr(cfg.model, 'model_type', None),
        'width_mul': getattr(cfg.model, 'width_mul', None),
        'depth_mul': getattr(cfg.model, 'depth_mul', None),
        'input_shape': getattr(cfg.model, 'input_shape', None),
        'num_anchors': getattr(cfg.postprocessing, 'num_anchors', None),
        'dropout': dropout,
    }
    return model_kwargs


def model_family(model_type: str) -> str:
    if model_type in ("ssd_mobilenet_v2_fpnlite"):
        return "ssd_mobilenet_v2_fpnlite"
    elif model_type in ("yolov2t", "st_yololcv1"):
        return "yolo"
    elif model_type in ("yolov8n", "yolov11n", "yolov5u"):
        return "yolov8n"
    elif model_type in ("st_yoloxn"):
        return "st_yoloxn"
    elif model_type in ("yolov4t", "yolov4"):
        return "yolov4"
    elif model_type in ("face_detect_front"):
        return "face_detect_front"
    elif model_type in ("st_yolod"):
        return "st_yolod"
    elif model_type in ("ssd"):
        return "ssd"
    else:
        raise ValueError(f"Internal error: unknown model type {model_type}")


def load_model_for_training(cfg: DictConfig) -> tuple:
    """"
    Loads a model for training.
    
    The model to train can be:
    - a model from the Model Zoo
    - a user model (BYOM)
    - a model previously trained during a training that was interrupted.
    
    When a training is run, the following files are saved in the saved_models
    directory:
        base_model.h5(.keras):
            Model saved before the training started. Weights are random.
        best_weights.h5(.keras):
            Best weights obtained since the beginning of the training.
        last_weights.h5(.keras):
            Weights saved at the end of the last epoch.
    
    To resume a training, the last weights are loaded into the base model.
    """
     
    model = None
                        
    # Resume a previously interrupted training
    if cfg.model.resume_training_from:
        resume_dir = os.path.join(cfg.model.resume_training_from, cfg.general.saved_models_dir)
        print(f"[INFO] : Resuming training from directory {resume_dir}\n")
        
        message = "\nUnable to resume training."
        if not os.path.isdir(resume_dir):
            raise FileNotFoundError(f"\nCould not find resume directory {resume_dir}{message}")
        model_path = os.path.join(resume_dir, "base_model.keras")
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"\nCould not find model file {model_path}{message}\n")
        last_weights_path = os.path.join(resume_dir, "last_weights.weights.h5")
        if not os.path.isfile(last_weights_path):
            raise FileNotFoundError(f"\nCould not find model weights file {last_weights_path}{message}\n")
        
        model = tf.keras.models.load_model(model_path, compile=False)
        model.load_weights(last_weights_path)

    return model