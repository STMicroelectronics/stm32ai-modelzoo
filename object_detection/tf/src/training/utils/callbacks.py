# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
from munch import DefaultMunch
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf

from common.utils import LRTensorBoard, collect_callback_args
from common.training import lr_schedulers
from object_detection.tf.src.utils import calculate_objdet_metrics


class _ObjectDetectionMetrics(tf.keras.callbacks.Callback):

    def __init__(self, num_classes, iou_threshold, name=None):
        super().__init__()
        self.num_classes = num_classes
        self.iou_threshold = iou_threshold
        self.name = name

    def on_epoch_end(self, epoch, logs=None):

        # Calculate the average metrics for the data
        # collected by the test_step function
        groundtruths, detections = self.model.get_metrics_data()
        mpre, mrec, mAP = calculate_objdet_metrics(groundtruths, detections, self.iou_threshold, averages_only=True)
        
        # Add the metrics to the callbacks logs dictionary
        logs['val_mpre'] = mpre
        logs['val_mrec'] = mrec
        logs['val_map'] = mAP

        # Reset the metrics data collected by the test_step function
        self.model.reset_metrics_data()

    def on_test_batch_end(self, batch, logs=None):
        self.model.set_tmp_metrics_data(batch)


class MultiResCallback(tf.keras.callbacks.Callback):

    def __init__(self, image_sizes, period, name=None):
        super().__init__()
        self.resolutions = image_sizes
        self.period = period

    def on_train_batch_begin(self, batch, logs=None):
        res = self.resolutions[((batch-1)//self.period)%len(self.resolutions)]
        self.model.set_resolution(res)


def _get_callback_monitoring(args: DictConfig, callback_name: str = None, message: str = None) -> tuple:

    if not args.monitor:
        monitor = "val_loss"
    else:
        monitor = args.monitor
        valid = ("val_loss", "val_mpre", "val_mrec", "val_map")
        if monitor not in valid:
            raise ValueError(f"\nSupported values for the `monitor` argument of the '{callback_name}' "
                             f"callback are {valid}. Received {monitor}{message}")
    if not args.mode:
        mode = "auto"
    else:
        mode = args.mode
        valid = ("min", "max", "auto")
        if mode not in valid:
            raise ValueError("\nSupported values for the `mode` argument of the "
                            f"'{callback_name}' callback are {valid}. Received {mode}{message}")
    if mode == "auto":
        mode = "min" if monitor == "val_loss" else "max"

    if monitor in ("val_mpre", "val_mrec", "val_map") and mode == "min":
        print(f"WARNING: The `mode` argument of the '{callback_name}' callback is set to 'min'.",
              f"The '{monitor}' metrics will be minimized.")

    return monitor, mode


def _get_best_model_callback(cfg: DictConfig, 
                            saved_models_dir: str = None,
                            message: str = None) -> tf.keras.callbacks.Callback:

    monitor = "val_loss"
    mode = "min"
    if "ModelCheckpoint" in cfg:
        args = cfg["ModelCheckpoint"]

        for k in args.keys():
            if k not in ("monitor", "mode"):
                raise ValueError("\nThe 'ModelCheckpoint' callback is built-in. Only the "
                                f"`monitor` and `mode` arguments can be specified.{message}")
        monitor, mode = _get_callback_monitoring(args, callback_name="ModelCheckpoint", message=message)

    callback = tf.keras.callbacks.ModelCheckpoint(
                    filepath=os.path.join(saved_models_dir, "best_weights.weights.h5"),
                    save_best_only=True,
                    save_weights_only=True,
                    monitor=monitor,
                    mode=mode)
    return callback


def get_callbacks(cfg: DictConfig,
                  num_classes=None,
                  iou_eval_threshold=None,
                  image_sizes=None,
                  period=None,
                  saved_models_dir: str = None,
                  log_dir: str = None, 
                  metrics_dir: str = None) -> list[tf.keras.callbacks.Callback]:
                  
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
        output_dir (str): directory root of the tree where the output files are saved.
        logs_dir (str): directory the TensorBoard logs and training metrics are saved.
        saved_models_dir (str): directory where the trained models are saved.

    Returns:
        List[tf.keras.callbacks.Callback]: A list of Keras callbacks to pass
                                           to the fit() function.
    """

    # Make sure every callback has an arguments dictionary
    for name in cfg.keys():
        if not cfg[name]:
            cfg[name] = DefaultMunch.fromDict({})

    message = "\nPlease check the 'training.callbacks' section of your configuration file."
    lr_scheduler_names = lr_schedulers.get_scheduler_names()
    num_lr_schedulers = 0

    callback_list = []
    
    # The callback that calculates the object detection
    # metrics must be first in the list of callbacks.
    callback_list.append(_ObjectDetectionMetrics(num_classes, iou_eval_threshold))
    if image_sizes is not None and period is not None:
        callback_list.append(MultiResCallback(image_sizes,period))

    for name, args in cfg.items():
        # The ModelCheckpoint callback is handled separately.
        if name == "ModelCheckpoint":
            continue

        if name in ("TensorBoard", "CSVLogger"):
            raise ValueError(f"\nThe `{name}` callback is built-in and can't be redefined.{message}")

        if name in  ("ReduceLROnPlateau", "EarlyStopping"):
            monitor, mode = _get_callback_monitoring(args, callback_name=name, message=message)
            args.monitor = monitor
            args.mode = mode
    
        if name in lr_scheduler_names:
            text = "lr_schedulers.{}".format(name)
        else:
            text = "tf.keras.callbacks.{}".format(name)

        # Add the arguments to the callback string
        # and evaluate it to get the callback object
        text += collect_callback_args(name, args, message=message)
        try:
            callback = eval(text)
        except:
            raise ValueError("\nThe callback name `{}` is unknown, or its arguments are incomplete "
                             "or invalid\nReceived: {}{}".format(name, text, message))
        callback_list.append(callback)

        # Count LR schedulers
        if name in ["ReduceLROnPlateau", "LearningRateScheduler"] + lr_scheduler_names:
            num_lr_schedulers += 1
    
    # Check that there is only one scheduler
    if num_lr_schedulers > 1:
        raise ValueError(f"\nFound more than one learning rate scheduler{message}")

    # Add the Keras callback that saves the best model obtained so far
    callback = _get_best_model_callback(cfg, saved_models_dir=saved_models_dir, message=message)
    callback_list.append(callback)

    # Add the Keras callback that saves the model at the end of the epoch
    callback = tf.keras.callbacks.ModelCheckpoint(
                    filepath=os.path.join(saved_models_dir, "last_weights.weights.h5"),
                    save_best_only=False,
                    save_weights_only=True,
                    save_freq='epoch')
    callback_list.append(callback)

    # Add the TensorBoard callback
    callback = LRTensorBoard(log_dir=log_dir)
    callback_list.append(callback)

    # Add the CVSLogger callback (must be last in the list 
    # of callbacks to make sure it records the learning rate)
    callback = tf.keras.callbacks.CSVLogger(os.path.join(metrics_dir, "train_metrics.csv"))
    callback_list.append(callback)

    return callback_list

