# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
from timeit import default_timer as timer
from datetime import timedelta
import logging
import warnings
import numpy as np
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import tensorflow as tf
from typing import List, Dict, Union, Optional
import mlflow


logger = tf.get_logger()
logger.setLevel(logging.ERROR)

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from logs_utils import log_to_file, log_last_epoch_history
from gpu_utils import check_training_determinism
from train_utils import *
from models_mgt import get_tiny_yolo_v2_model
from train import get_optimizer
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
    checkpoint_clean = CheckpointYoloCleanCallBack(classes,anchors,int(input_shape[0]),os.path.join(output_dir, saved_models_dir), network_stride = cfg.postprocessing.network_stride)
    callbacks.append(checkpoint_clean)

    #yolo_map_callback = YoloMapCallBack(cfg, frq=4)
    #callbacks.append(yolo_map_callback)
    # logging the name of the dataset used for training
    if cfg.dataset.name: 
        log_to_file(output_dir, f"Dataset : {cfg.dataset.name}")

    model = get_tiny_yolo_v2_model(cfg)
    model.compile(optimizer=optimizer, loss={'tiny_yolo_v2_loss': lambda y_true, y_pred: y_pred})
    model.summary()

    # check if determinism can be enabled
    if cfg.general.deterministic_ops:
        sample_ds = train_gen.take(1)
        tf.config.experimental.enable_op_determinism()
        if not check_training_determinism(model, sample_ds):
            print("[WARNING]: Some operations cannot be run deterministically. Setting deterministic_ops to False.")
            tf.config.experimental.enable_op_determinism.__globals__["_pywrap_determinism"].enable(False)

    # Train the model
    print("[INFO] : Starting training...")
    start_time = timer()
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
    #save the last epoch history in the log file
    last_epoch=log_last_epoch_history(cfg, output_dir)
    end_time = timer()

    #calculate and log the runtime in the log file
    fit_run_time = int(end_time - start_time)
    average_time_per_epoch = round(fit_run_time / (int(last_epoch) + 1),2)
    print("Training runtime: " + str(timedelta(seconds=fit_run_time))) 
    log_to_file(cfg.output_dir, (f"Training runtime : {fit_run_time} s\n" + f"Average time per epoch : {average_time_per_epoch} s"))

    evaluate_tiny_yolo_v2(cfg,model_path=os.path.join(output_dir, saved_models_dir, "best_model.h5"))

    # Record the whole hydra working directory to get all info
    mlflow.log_artifact(output_dir)

    return os.path.join(output_dir, saved_models_dir, "best_model.h5")