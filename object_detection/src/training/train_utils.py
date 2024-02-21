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
from typing import List, Optional
import lr_schedulers

class LRTensorBoard(tf.keras.callbacks.TensorBoard):
    """
    Custom TensorBoard callback that logs the learning rate during training.
    """

    def __init__(self, log_dir: str, **kwargs) -> None:
        # `log_dir` is the directory where the log files will be written.
        super().__init__(log_dir, **kwargs)
        self.lr_writer = tf.summary.create_file_writer(os.path.join(self.log_dir, 'metrics'))

    def on_epoch_end(self, epoch: int, logs=None) -> None:
        # Write the learning rate to the TensorBoard log file
        lr = getattr(self.model.optimizer, 'lr', None)
        if lr is not None:
            with self.lr_writer.as_default():
                tf.summary.scalar('learning_rate', lr, step=epoch)
        super().on_epoch_end(epoch, logs)

    def on_train_end(self, logs=None) -> None:
        super().on_train_end(logs)
        self.lr_writer.close()


def set_frozen_layers(model: tf.keras.Model, frozen_layers: str = None) -> None:
    """
    This function freezes (makes non-trainable) the layers that are 
    specified by the `frozen_layers` attribute.
    The indices are specified using the same syntax as in Python:
       2                      layer 2 (3rd layer from network input)
       (2)                    layer 2
       (4:8)                  layers 4 to 7
       (0:-1)                 layers 0 to before last
       (7:13, 16, 20:28, -1)  layers 7 to 12, 16, 20 to 27, last
    There can be any number of index slices in the attribute.
    The attribute must be between parentheses. Using square brackets
    would make it an array and it could be changed by the YAML loader.
      not be left unchanged by the

    Arguments:
        model (tf.keras.Model): the model.
        frozen_layers (str): the indices of the layers to freeze.

    Returns:
        None
    """
    frozen_layers = str(frozen_layers)
    frozen_layers = frozen_layers.replace(" ", "")
    frozen_slices = frozen_layers[1:-1] if frozen_layers[0] == "(" else frozen_layers

    num_layers = len(model.layers)
    indices = np.arange(num_layers)
    frozen_indices = np.zeros(num_layers, dtype=bool)
    for slice_ in frozen_slices.split(','):
        try:
            i = eval("indices[" + str(slice_) + "]")
        except:
            raise ValueError("\nInvalid syntax for `frozen_layers` attribute\nLayer index slices "
                             "should follow the Python syntax. Received {}\nPlease check the "
                             "'training' section of your configuration file.".format(frozen_layers))
        frozen_indices[i] = True

    # Freeze layers
    model.trainable = True
    num_trainable = num_layers
    for i in range(num_layers):
        if frozen_indices[i]:
            num_trainable -= 1
            model.layers[i].trainable = False


def get_optimizer(cfg: DictConfig) -> tf.keras.optimizers:
    """
    This function creates a Keras optimizer from the 'optimizer' section
    of the config file.
    The optimizer name, attributes and values used in the config file
    are used to create a string that is the call to the Keras optimizer
    with its arguments. Then, the string is evaluated. If the evaluation
    succeeds, the optimizer object is returned. If it fails, an error
    is thrown with a message that tells the user that the name and/or
    arguments of the optimizer are incorrect.

    Arguments:
        cfg (DictConfig): dictionary containing the 'optimizer' section of
                          the configuration file.
    Returns:
        tf.keras.optimizers: the Keras optimizer object.
    """

    message = "\nPlease check the 'training.optimizer' section of your configuration file."
    if type(cfg) != DefaultMunch:
        raise ValueError("\nInvalid syntax for optimizer{}".format(message))
    optimizer_name = list(cfg.keys())[0]
    optimizer_args = cfg[optimizer_name]

    # Get the optimizer
    if not optimizer_args:
        # The optimizer has no arguments.
        optimizer_text = "tf.keras.optimizers.{}()".format(optimizer_name)
    else:
        if type(optimizer_args) != DefaultMunch:
            raise ValueError("\nInvalid syntax for `{}` optimizer arguments{}".format(optimizer_name, message))
        text = "tf.keras.optimizers.{}(".format(optimizer_name)
        # Collect the arguments
        for k, v in optimizer_args.items():
            if type(v) == str:
                text += f'{k}=r"{v}", '
            else:
                text += f'{k}={v}, '
        optimizer_text = text[:-2] + ')'

    try:
        optimizer = eval(optimizer_text)
    except:
        raise ValueError("\nThe optimizer name `{}` is unknown or the arguments are invalid, got:\n"
                         "{}.{}".format(optimizer_name, optimizer_text, message))
    return optimizer


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

    def collect_callback_args(name, args=None, message=None):
        if args:
            if type(args) != DefaultMunch:
                raise ValueError(f"\nInvalid syntax for `{name}` callback arguments{message}")
            text = "("
            for k, v in args.items():
                if type(v) == str and v[:7] != "lambda ":
                    text += f'{k}=r"{v}", '
                else:
                    text += f'{k}={v}, '
            text = text[:-2] + ")"
        else:
            text = "()"
        return text


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
    elif model_type == 'tiny_yolo_v2':
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