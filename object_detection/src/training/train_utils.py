# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from munch import DefaultMunch
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf
from typing import List, Optional

from logs_utils import LRTensorBoard
from cfg_utils import collect_callback_args
import lr_schedulers


def get_callbacks(callbacks_dict: DictConfig, model_type: str = None, output_dir: str = None, logs_dir: str = None,
                  saved_models_dir: str = None) -> List[tf.keras.callbacks.Callback]:
    """
    This function creates the list of Keras callbacks to be passed to 
    the fit() function including:
      - the Model Zoo built-in callbacks that can't be redefined by the
        user (ModelCheckpoint, TensorBoard, CSVLogger).
      - the callbacks specified in the config file that can be either Keras
        callbacks or custom callbacks (learning rate schedulers).

    For each callback, the attributes and their values used in the config
    file are used to create a string that is the callback instantiation as
    it would be written in a Python script. Then, the string is evaluated.
    If the evaluation succeeds, the callback object is returned. If it fails,
    an error is thrown with a message saying that the name and/or arguments
    of the callback are incorrect.

    The function also checks that there is only one learning rate scheduler
    in the list of callbacks.

    Args:
        callbacks_dict (DictConfig): dictionary containing the 'training.callbacks'
                                     section of the configuration.
        model_type (str): string discribing the model type
        output_dir (str): directory root of the tree where the output files are saved.
        logs_dir (str): directory the TensorBoard logs and training metrics are saved.
        saved_models_dir (str): directory where the trained models are saved.

    Returns:
        List[tf.keras.callbacks.Callback]: A list of Keras callbacks to pass
                                           to the fit() function.
    """

    message = "\nPlease check the 'training.callbacks' section of your configuration file."
    lr_scheduler_names = lr_schedulers.get_scheduler_names()
    num_lr_schedulers = 0

    # Generate the callbacks used in the config file (there may be none)
    callback_list = []
    if callbacks_dict is not None:
        if type(callbacks_dict) != DefaultMunch:
            raise ValueError("\nInvalid callbacks syntax{}".format(message))
        for name in callbacks_dict.keys():
            if name in ("ModelCheckpoint", "TensorBoard", "CSVLogger"):
                raise ValueError(f"\nThe `{name}` callback is built-in and can't be redefined.{message}")
            if name in lr_scheduler_names:
                text = "lr_schedulers.{}".format(name)
            else:
                text = "tf.keras.callbacks.{}".format(name)

            # Add the arguments to the callback string
            # and evaluate it to get the callback object
            text += collect_callback_args(name, args=callbacks_dict[name], message=message)
            try:
                callback = eval(text)
            except:
                raise ValueError("\nThe callback name `{}` is unknown, or its arguments are incomplete "
                                "or invalid\nReceived: {}{}".format(name, text, message))
            callback_list.append(callback)

            # Only the val_loss metric is available (val_accuracy is not).
            if name in  ("ReduceLROnPlateau", "EarlyStopping"):
                args = callbacks_dict[name]
                if args.monitor and args.monitor != "val_loss":
                    raise ValueError(f"\nThe `monitor` argument of the `{name}` callback can only set to 'val_loss'.{message}")
                if args.mode and args.mode != "auto" and args.mode != "min":
                    raise ValueError(f"\nThe `mode` argument of the `{name}` callback should be set to 'auto' or 'min'.{message}")

            # Count LR schedulers
            if name in lr_scheduler_names + ["ReduceLROnPlateau", "LearningRateScheduler"]:
                num_lr_schedulers += 1

    # Check that there is only one scheduler
    if num_lr_schedulers > 1:
        raise ValueError(f"\nFound more than one learning rate scheduler{message}")

    if model_type == 'st_ssd_mobilenet_v1' or model_type == 'ssd_mobilenet_v2_fpnlite':
        save_only_weights = True
        model_file_name = "best_weights.h5"
    elif model_type == 'tiny_yolo_v2' or model_type == "st_yolo_lc_v1":
        save_only_weights = False
        model_file_name = "best_model.h5"
    else:
        raise ValueError(f"\nUnknown model_type, please use a valid model_type")

    # Add the Keras callback that saves the best model obtained so far
    callback = tf.keras.callbacks.ModelCheckpoint(
                        filepath=os.path.join(output_dir, saved_models_dir, model_file_name),
                        save_best_only=True,
                        save_weights_only=save_only_weights,
                        monitor="val_loss",
                        mode="min")
    callback_list.append(callback)

    # Add the Keras callback that saves the model at the end of the epoch
    # callback = tf.keras.callbacks.ModelCheckpoint(
    #                     filepath=os.path.join(output_dir, saved_models_dir, "last_train_model.h5"),
    #                     save_best_only=False,
    #                     save_weights_only=False,
    #                     monitor="val_loss",
    #                     mode="min")
    # callback_list.append(callback)

    # Add the TensorBoard callback
    callback = LRTensorBoard(log_dir=os.path.join(output_dir, logs_dir))
    callback_list.append(callback)

    # Add the CVSLogger callback (must be last in the list 
    # of callbacks to make sure it records the learning rate)
    callback = tf.keras.callbacks.CSVLogger(os.path.join(output_dir, logs_dir, "metrics", "train_metrics.csv"))
    callback_list.append(callback)

    return callback_list