# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
import logging
import warnings
import numpy as np
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import tensorflow as tf
from typing import List, Dict, Union, Optional
import lr_schedulers

logger = tf.get_logger()
logger.setLevel(logging.ERROR)

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../evaluation'))
sys.path.append(os.path.abspath('../../../common'))

from train_utils import *
from load_models import get_tiny_yolo_v2_model
from train import get_optimizer, LRTensorBoard
from tiny_yolo_v2_evaluate import evaluate_tiny_yolo_v2
from tiny_yolo_v2_utils import CheckpointYoloCleanCallBack, YoloMapCallBack

def train_tiny_yolo_v2(cfg = None,train_ds = None, valid_ds = None, test_ds = None,train_gen = None, valid_gen = None):
    """
    Trains the model with the given configuration and datasets.

    If no test set is provided, the validation set is used instead
    to calculate the mAP.

    Args:
        cfg (DictConfig): configuration dictionary.
        train_ds (Dict): training dataset.
        valid_ds (Dict): validation dataset.
        test_ds (Dict): test dataset (optional).
        train_gen (generator): training generator.
        valid_gen (generator): validation generator.

    Returns:
        str: The trained model path.
    """
    output_dir = HydraConfig.get().runtime.output_dir
    saved_models_dir = cfg.general.saved_models_dir
    num_val_samples = len(valid_ds)
    num_train_samples = len(train_ds)
    batch_size = cfg.training.batch_size
    epochs = cfg.training.epochs
    classes = cfg.dataset.class_names
    anchors_list = cfg.postprocessing.yolo_anchors
    anchors = np.array(anchors_list).reshape(-1, 2)
    num_classes = len(classes)
    input_shape = cfg.training.model.input_shape

    optimizer = get_optimizer(cfg.training.optimizer)

    callbacks = get_callbacks(callbacks_dict=cfg.training.callbacks,
                              model_type=cfg.general.model_type,
                              output_dir=output_dir,
                              saved_models_dir=saved_models_dir,
                              logs_dir=cfg.general.logs_dir)
    checkpoint_clean = CheckpointYoloCleanCallBack(classes,anchors,int(input_shape[0]),os.path.join(output_dir, saved_models_dir))
    callbacks.append(checkpoint_clean)

    #yolo_map_callback = YoloMapCallBack(cfg, frq=4)
    #callbacks.append(yolo_map_callback)

    model = get_tiny_yolo_v2_model(cfg)
    model.compile(optimizer=optimizer, loss={'tiny_yolo_v2_loss': lambda y_true, y_pred: y_pred})
    model.summary()
    model.fit(train_gen,
    steps_per_epoch=max(1, num_train_samples//batch_size),
    validation_data= valid_gen,
    validation_steps=max(1, num_val_samples//batch_size),
    epochs=epochs,
    initial_epoch=0,
    workers=1,
    use_multiprocessing=False,
    max_queue_size=0,
    callbacks=callbacks)
    evaluate_tiny_yolo_v2(cfg,model_path=os.path.join(output_dir, saved_models_dir, "best_model.h5"))
    return os.path.join(output_dir, saved_models_dir, "best_model.h5")