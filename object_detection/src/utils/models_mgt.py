#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
from typing import Tuple, Dict, List, Optional
import tensorflow as tf

from st_ssd_mobilenet_v1 import st_ssd_mobilenet_v1
from ssd_mobilenet_v2_fpnlite import ssd_mobilenet_v2_fpnlite
from tiny_yolo_v2 import tiny_yolo_v2_model


def get_model(cfg: Dict = None, class_names: List[str] = None) -> tf.keras.Model:
    """
    Returns a MobileNet-based SSD model based on the configuration provided.

    Args:
        cfg (Dict): The model configuration to use.
        class_names: List of class names.

    Returns:
        tf.keras.Model: A MobileNet-based SSD model.

    Raises:
        TypeError: If the model name is not 'st_ssd_mobilenet_v1' or 'ssd_mobilenet_v2_fpnlite',
         or if alpha is not in [0.25, 0.50, 0.75, 1.0] for 'st_ssd_mobilenet_v1' or [0.35, 0.50, 0.75, 1.0] for 'ssd_mobilenet_v2_fpnlite'.
    """
    # Check if a model configuration was provided
    if cfg is None:
        raise ValueError("Please provide a model configuration.")
    # Check if the model name is valid
    if cfg.general.model_type.lower() != 'st_ssd_mobilenet_v1' and cfg.general.model_type.lower() != 'ssd_mobilenet_v2_fpnlite':
        raise TypeError("Invalid model name. Please select 'st_ssd_mobilenet_v1' or 'ssd_mobilenet_v2_fpnlite'.")
    # Check if the alpha value is valid
    if cfg.general.model_type.lower() == 'st_ssd_mobilenet_v1' and cfg.training.model.alpha not in [0.25, 0.50, 0.75, 1.0]:
        raise TypeError("Invalid alpha value. Please select alpha from [0.25, 0.50, 0.75, 1.0].")
    if cfg.general.model_type.lower() == 'ssd_mobilenet_v2_fpnlite' and cfg.training.model.alpha not in [0.35, 0.50, 0.75, 1.0]:
        raise TypeError("Invalid alpha value. Please select alpha from [0.35, 0.50, 0.75, 1.0].")

    if cfg.general.model_type.lower() == 'st_ssd_mobilenet_v1':
        return st_ssd_mobilenet_v1(input_shape=cfg.training.model.input_shape, class_names=class_names,
                         model_alpha=cfg.training.model.alpha, pretrained_weights=cfg.training.model.pretrained_weights)
    elif cfg.general.model_type.lower() == 'ssd_mobilenet_v2_fpnlite':
        return ssd_mobilenet_v2_fpnlite(input_shape=cfg.training.model.input_shape, class_names=class_names,
                                model_alpha=cfg.training.model.alpha, pretrained_weights=cfg.training.model.pretrained_weights)


def get_tiny_yolo_v2_model(cfg):
    """
    Create a YOLOv2 model

    Args:
        cfg (DictConfig): The configuration object.
    Returns:
        A Keras Model object representing the YOLOv2 model.
    """
    if cfg.general.model_type.lower() == "tiny_yolo_v2" or cfg.general.model_type.lower() == "st_yolo_lc_v1":
        return tiny_yolo_v2_model(cfg)
