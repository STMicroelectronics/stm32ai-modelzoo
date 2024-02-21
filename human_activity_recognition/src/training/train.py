# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
from pathlib import Path
from timeit import default_timer as timer
from datetime import timedelta
from typing import Tuple, List, Dict, Optional

import mlflow
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf

from utils import model_summary, check_training_determinism
from models_mgt import get_keras_model
import lr_schedulers
from evaluate import evaluate_h5_model
from visualizer import vis_training_curves


class LRTensorBoard(tf.keras.callbacks.TensorBoard):
    """
    Custom TensorBoard callback that logs the learning rate during training.
    """

    def __init__(self, log_dir: str, **kwargs) -> None:
        '''
        `log_dir` is the directory where the log files will be written.
        '''
        super().__init__(log_dir, **kwargs)
        self.lr_writer = tf.summary.create_file_writer(os.path.join(self.log_dir, 'metrics'))

    def on_epoch_end(self, epoch: int, logs=None) -> None:
        '''
        Write the learning rate to the TensorBoard log file
        '''
        lr = getattr(self.model.optimizer, 'lr', None)
        if lr is not None:
            with self.lr_writer.as_default():
                tf.summary.scalar('learning_rate', lr, step=epoch)
        super().on_epoch_end(epoch, logs)

    def on_train_end(self, logs=None) -> None:
        '''
        on_train_end function
        '''
        super().on_train_end(logs)
        self.lr_writer.close()


def load_keras_model_to_train(cfg, model_path=None, num_classes=None) -> tf.keras.Model:
    """
    This function loads the model to train, which can be either a:
    - model from the zoo (ign, gmp, custom) .h5 model
    - a model loaded from a .h5 file with  the training is being resumed
    - or, a .h5 model outside of the model zoo.

    These 3 different cases are mutually exclusive.

    Arguments:
        cfg (DictConfig): a dictionary containing the 'training' section 
                          of the configuration file.
        model_path (str): a path to a .h5 file provided using the 
                          'general.model_path' attribute.

    Return:
        tf.keras.Model: a keras model.
    """
    print(cfg.dropout)
    if cfg.model:
        # Model from the zoo
        model = get_keras_model(cfg=cfg.model,
                                num_classes=num_classes,
                                dropout=cfg.dropout,
                                section="training.model")
        input_shape = cfg.model.input_shape

    elif model_path:
        # User model (h5 file)
        model = tf.keras.models.load_model(model_path)
        input_shape = tuple(model.input.shape[1:])

    elif cfg.resume_training_from:
        # Model saved during a previous training
        model = tf.keras.models.load_model(cfg.resume_training_from)
        input_shape = tuple(model.input.shape[1:])
    else:
        raise RuntimeError("\nInternal error: should have model,"
                           "model_path or resume_training_from")

    return model, input_shape


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
        except ValueError as val_err:
            raise ValueError("\nInvalid syntax for `frozen_layers` attribute\nLayer index slices "
                             f"should follow the Python syntax. Received {frozen_layers}\nPlease check the "
                             "'training' section of your configuration file.") from val_err
        frozen_indices[i] = True

    # Freeze layers
    model.trainable = True
    num_trainable = num_layers
    for i in range(num_layers):
        if frozen_indices[i]:
            num_trainable -= 1
            model.layers[i].trainable = False


def set_dropout_rate(model: tf.keras.Model, dropout_rate: float = None) -> None:
    """
    This function sets the dropout rate of the dropout layer if 
    the `dropout`attribute was used in the 'training' section of
    the config file.
    An error is thrown if:
    - The `dropout` attribute was used but the model does not
      include a dropout layer.
    - The model includes a dropout layer but the `dropout`attribute
      was not used to specify a rate.

    Arguments:
        model (tf.keras.Model): the model.
        dropout_rate (float): the dropout rate to set on the dropout layer.
        
    Returns:
        None
    """

    found_layer = False
    for layer in model.layers:
        layer_type = layer.__class__.__name__
        if layer_type == "Dropout":
            found_layer = True

    if found_layer:
        # The dropout rate must be specified.
        if not dropout_rate:
            raise ValueError("\nThe model includes a dropout layer."
                             "\nPlease use the 'training.dropout' "
                             "attribute in your configuration file to specify a dropout rate")
        for layer in model.layers:
            layer_type = layer.__class__.__name__
            if layer_type == "Dropout":
                layer.rate = dropout_rate
        print("[INFO] Set dropout rate to", dropout_rate)
    else:
        # The dropout rate can't be applied.
        if dropout_rate:
            raise ValueError("\nUnable to set the dropout rate specified by the 'training.dropout' "
                             "attribute in the configuration file\nThe model does not include "
                             "a dropout layer.")


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
    if not isinstance(cfg, DefaultMunch):
        raise ValueError(f"\nInvalid syntax for optimizer{message}")
    optimizer_name = list(cfg.keys())[0]
    optimizer_args = cfg[optimizer_name]

    # Get the optimizer
    if not optimizer_args:
        # The optimizer has no arguments.
        optimizer_text = f"tf.keras.optimizers.{optimizer_name}()"
    else:
        if not isinstance(optimizer_args, DefaultMunch):
            raise ValueError(f"\nInvalid syntax for `{optimizer_name}` optimizer arguments{message}")
        text = f"tf.keras.optimizers.{optimizer_name}("
        # Collect the arguments
        for k, v in optimizer_args.items():
            if isinstance(v, str):
                text += f'{k}=r"{v}", '
            else:
                text += f'{k}={v}, '
        optimizer_text = text[:-2] + ')'

    try:
        print(optimizer_text)
        optimizer = eval(optimizer_text)
    except ValueError as val_err:
        raise ValueError(f"\nThe optimizer name `{optimizer_name}` is unknown or,"
                         f"the arguments are invalid, got:\n{optimizer_text}.{message}") from val_err
    return optimizer


def get_loss(num_classes: int) -> tf.keras.losses:
    """
    Returns the appropriate loss function based on the number of classes in the dataset.

    Args:
        num_classes (int): The number of classes in the dataset.

    Returns:
        tf.keras.losses: The appropriate loss function based on the
          number of classes in the dataset.
    """
    # We use the sparse version of the categorical crossentropy because
    # this is what we use to load the dataset.
    if num_classes > 2:
        # loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)

    return loss


def get_callbacks(callbacks_dict: DictConfig, output_dir: str = None, logs_dir: str = None,
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

    The user may use the ModelSaver callback to periodically save the model 
    at the end of an epoch. If it is not used, a default ModelSaver is added
    that saves the model at the end of each epoch. The model file is named
    last_model.h5 and is saved in the output_dir/saved_models_dir directory
    (same directory as best_model.h5).

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

    def collect_callback_args(name, args=None, message=None):
        if args:
            if not isinstance(args, DefaultMunch):
                raise ValueError(f"\nInvalid syntax for `{name}` callback arguments{message}")
            text = "("
            for k, v in args.items():
                if isinstance(v, str) and v[:7] != "lambda ":
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
        if not isinstance(callbacks_dict, DefaultMunch):
            raise ValueError(f"\nInvalid callbacks syntax{message}")
        for name in callbacks_dict.keys():
            if name in ("ModelCheckpoint", "TensorBoard", "CSVLogger"):
                raise ValueError(f"\nThe `{name}` callback is built-in and can't be redefined.{message}")
            if name in lr_scheduler_names:
                text = f"lr_schedulers.{name}"
            else:
                text = f"tf.keras.callbacks.{name}"

            # Add the arguments to the callback string
            # and evaluate it to get the callback object
            text += collect_callback_args(name, args=callbacks_dict[name], message=message)
            try:
                callback = eval(text)
            except ValueError as error:
                raise ValueError(f"\nThe callback name `{name}` is unknown, or its arguments are incomplete "
                                 f"or invalid\nReceived: {text}{message}") from error
            callback_list.append(callback)

            if name in lr_scheduler_names + ["ReduceLROnPlateau", "LearningRateScheduler"]:
                num_lr_schedulers += 1

    # Check that there is only one scheduler
    if num_lr_schedulers > 1:
        raise ValueError(f"\nFound more than one learning rate scheduler{message}")

    # Add the Keras callback that saves the best model obtained so far
    callback = tf.keras.callbacks.ModelCheckpoint(
                        filepath=os.path.join(output_dir, saved_models_dir, "best_model.h5"),
                        save_best_only=True,
                        save_weights_only=False,
                        monitor="val_accuracy",
                        mode="max")
    callback_list.append(callback)

    # Add the Keras callback that saves the model at the end of the epoch
    callback = tf.keras.callbacks.ModelCheckpoint(
                    filepath=os.path.join(output_dir, saved_models_dir, "last_epoch_model.h5"),
                    save_best_only=False,
                    save_weights_only=False,
                    monitor="val_accuracy",
                    mode="max")
    callback_list.append(callback)

    # Add the TensorBoard callback
    callback = LRTensorBoard(log_dir=os.path.join(output_dir, logs_dir))
    callback_list.append(callback)

    # Add the CVSLogger callback (must be last in the list 
    # of callbacks to make sure it records the learning rate)
    callback = tf.keras.callbacks.CSVLogger(os.path.join(output_dir,
                                                         logs_dir, "metrics", "train_metrics.csv"))
    callback_list.append(callback)

    return callback_list


def train(cfg: DictConfig = None, train_ds: tf.data.Dataset = None,
          valid_ds: tf.data.Dataset = None, test_ds: Optional[tf.data.Dataset] = None) -> str:
    """
    Trains the model using the provided configuration and datasets.

    Args:
        cfg (DictConfig): The entire configuration file dictionary.
        train_ds (tf.data.Dataset): training dataset loader.
        valid_ds (tf.data.Dataset): validation dataset loader.
        test_ds (Optional, tf.data.Dataset): test dataset dataset loader.

    Returns:
        Path to the best model obtained
    """

    output_dir = cfg.output_dir
    saved_models_dir = cfg.general.saved_models_dir
    class_names = cfg.dataset.class_names
    num_classes = len(class_names)

    print("Dataset stats:")
    train_size = sum([x.shape[0] for x, _ in train_ds])
    valid_size = sum([x.shape[0] for x, _ in valid_ds])
    if test_ds:
        test_size = sum([x.shape[0] for x, _ in test_ds])

    print("  classes:", num_classes)
    print("  training set size:", train_size)
    print("  validation set size:", valid_size)
    if test_ds:
        print("  test set size:", test_size)
    else:
        print("  no test set")

    model, _ = load_keras_model_to_train(cfg.training, model_path=cfg.general.model_path,
                                   num_classes=num_classes)

    # Info messages about the model that was loaded
    if cfg.training.model:
        cfm = cfg.training.model
        print(f"[INFO] Using `{cfm.name}` model")
        if cfm.pretrained_weights:
            print(f"[INFO] Initialized model with '{cfm.pretrained_weights}' pretrained weights")
        elif cfm.pretrained_model_path:
            print(f"[INFO] Initialized model with weights from model file {cfm.pretrained_model_path}")
        else:
            print("[INFO] No pretrained weights were loaded, training from randomly initialized weights.")
    elif cfg.training.resume_training_from:
        print(f"[INFO] Resuming training from model file {cfg.training.resume_training_from}")
    elif cfg.general.model_path:
        print(f"[INFO] Loaded model file {cfg.general.model_path}")

    if not cfg.training.resume_training_from:
        # Set frozen layers
        if not cfg.training.frozen_layers or cfg.training.frozen_layers == "None":
            model.trainable = True
        else:
            set_frozen_layers(model, frozen_layers=cfg.training.frozen_layers)
        # Set dropout rate
        set_dropout_rate(model, dropout_rate=cfg.training.dropout)

    # Display a summary of the model
    if cfg.training.resume_training_from:
        model_summary(model)
        if len(model.layers) == 2:
            model_summary(model.layers[1])
        else:
            model_summary(model.layers[2])
    else:
        model_summary(model)

    # Compile the augmented model
    model.compile(loss=get_loss(num_classes=num_classes),
                  metrics=['accuracy'],
                  optimizer=get_optimizer(cfg=cfg.training.optimizer))

    callbacks = get_callbacks(callbacks_dict=cfg.training.callbacks,
                              output_dir=output_dir,
                              saved_models_dir=saved_models_dir,
                              logs_dir=cfg.general.logs_dir)

    # check if determinism can be enabled
    if cfg.general.deterministic_ops:
        sample_ds = train_ds.take(1)
        tf.config.experimental.enable_op_determinism()
        if not check_training_determinism(model, sample_ds):
            print("[WARNING]: Some operations cannot be run deterministically.\
                   Setting deterministic_ops to False.")
            tf.config.experimental.enable_op_determinism.__globals__["_pywrap_determinism"].enable(False)

    runtime_csv_path = os.path.join(output_dir,
                                    cfg.general.logs_dir,
                                    "metrics",
                                    "train_runtime.csv")
    if os.path.isfile(runtime_csv_path):
        os.remove(runtime_csv_path)

    # Train the model
    print("Starting training...")
    start_time = timer()
    history = model.fit(train_ds,
                        validation_data=valid_ds,
                        epochs=cfg.training.epochs,
                        callbacks=callbacks)
    end_time = timer()
    fit_run_time = int(end_time - start_time)
    print("Training runtime: " + str(timedelta(seconds=fit_run_time)))

    with open(runtime_csv_path, "w", encoding='utf-8') as f:
        f.write("epochs,runtime\n")
        f.write(f"{cfg.training.epochs},{fit_run_time}\n")

    # Visualize training curves
    vis_training_curves(history=history, output_dir=output_dir)
    best_model_path = os.path.join(output_dir,
                                   saved_models_dir,
                                   "best_model.h5")
    best_model = tf.keras.models.load_model(best_model_path)
    # Save a copy of the best model if requested
    if cfg.training.trained_model_path:
        best_model.save(cfg.training.trained_model_path)
        print(f"[INFO] Saved trained model in file {cfg.training.trained_model_path}")

    # Evaluate h5 best model on the validation set
    evaluate_h5_model(model_path=best_model_path, eval_ds=valid_ds,
                      class_names=class_names, output_dir=output_dir, name_ds="validation_set")

    if test_ds:
        # Evaluate h5 best model on the test set
        evaluate_h5_model(model_path=best_model_path, eval_ds=test_ds,
                          class_names=class_names, output_dir=output_dir, name_ds="test_set")

        # Record the whole hydra working directory to get all info
    mlflow.log_artifact(output_dir)

    return best_model_path
