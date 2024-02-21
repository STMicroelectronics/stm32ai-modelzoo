# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
from timeit import default_timer as timer
from datetime import timedelta
from typing import Dict, List, Optional
from pathlib import Path
import mlflow
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf

from utils import model_summary, check_training_determinism, get_loss, log_to_file, log_last_epoch_history
from models_mgt import get_model
from data_augmentation import get_data_augmentation
from data_augmentation_layers_audio import VolumeAugment, SpecAugment
import lr_schedulers
from evaluate import evaluate_h5_model
from visualizer import vis_training_curves


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
            raise ValueError("\nThe model includes a dropout layer.\nPlease use the 'training.dropout' "
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
    (same directory as best_augmented_model.h5 and best_model.h5).

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

            if name in lr_scheduler_names + ["ReduceLROnPlateau", "LearningRateScheduler"]:
                num_lr_schedulers += 1

    # Check that there is only one scheduler
    if num_lr_schedulers > 1:
        raise ValueError(f"\nFound more than one learning rate scheduler{message}")

    # Add the Keras callback that saves the best model obtained so far
    callback = tf.keras.callbacks.ModelCheckpoint(
                        filepath=os.path.join(output_dir, saved_models_dir, "best_augmented_model.h5"),
                        save_best_only=True,
                        save_weights_only=False,
                        monitor="val_accuracy",
                        mode="max")
    callback_list.append(callback)

    # Add the Keras callback that saves the model at the end of the epoch
    callback = tf.keras.callbacks.ModelCheckpoint(
                        filepath=os.path.join(output_dir, saved_models_dir, "last_augmented_model.h5"),
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
    callback = tf.keras.callbacks.CSVLogger(os.path.join(output_dir, logs_dir, "metrics", "train_metrics.csv"))
    callback_list.append(callback)

    return callback_list


def load_model_to_train(cfg, model_path=None, num_classes=None) -> tf.keras.Model:
    """
    This function loads the model to train, which can be either a:
    - model from the zoo (Yamnet, miniresnet, etc).
    - .h5 model
    These 2 different cases are mutually exclusive.

    Arguments:
        cfg (DictConfig): a dictionary containing the configuration file.
        model_path (str): a path to a .h5 file provided using the 
                          'general.model_path' attribute.

    Return:
        tf.keras.Model: a keras model.
    """
    
    if cfg.training.model:
        # Model from the zoo
        model = get_model(
            cfg=cfg.training.model,
            num_classes=num_classes,
            dropout=cfg.training.dropout,
            fine_tune=cfg.training.fine_tune,
            use_garbage_class=cfg.dataset.use_garbage_class,
            multi_label=cfg.dataset.multi_label,
            pretrained_weights=cfg.training.model.pretrained_weights,
            kernel_regularizer=None,
            activity_regularizer=None,
            patch_length=cfg.feature_extraction.patch_length,
            n_mels=cfg.feature_extraction.n_mels,
            section="training.model")
        input_shape = cfg.training.model.input_shape

    elif model_path:
        # User model (h5 file)
        model = tf.keras.models.load_model(model_path)
        input_shape = tuple(model.input.shape[1:])

    elif cfg.training.resume_training_from:
        # Model saved during a previous training 
        model = tf.keras.models.load_model(
                        cfg.training.resume_training_from,
                        custom_objects={
                                    'VolumeAugment': VolumeAugment,
                                    'SpecAugment' : SpecAugment
                                       })
        input_shape = tuple(model.input.shape[1:])

    else:
        raise RuntimeError("\nInternal error: should have model, model_path or resume_training_from")

    return model, input_shape

def train(cfg: DictConfig = None, train_ds: tf.data.Dataset = None,
          valid_ds: tf.data.Dataset = None, val_clip_labels: np.ndarray = None,
          test_ds: Optional[tf.data.Dataset] = None, test_clip_labels: np.ndarray = None) -> str:
    """
    Trains the model with the given configuration and datasets.

    Args:
        cfg (DictConfig): The entire configuration file dictionary.
        train_ds (tf.data.Dataset): The training dataset.
        valid_ds (tf.data.Dataset): The validation dataset.
        val_clip_labels : np.ndarray, Clip labels associated to the validation dataset
        test_ds (Optional,tf.data.Dataset): The test dataset.
        test_clip_labels : Optional, np.ndarray, Clip labels associated to the test dataset

    Returns:
        best_model_path : str, path to the best trained model
    """

    output_dir = HydraConfig.get().runtime.output_dir
    saved_models_dir = cfg.general.saved_models_dir
    class_names = cfg.dataset.class_names
    num_classes = len(class_names)

    model, _ = load_model_to_train(cfg, model_path=cfg.general.model_path, num_classes=num_classes)

    if cfg.training.model:
        cfm = cfg.training.model
        print(f"[INFO] Using `{cfm.name}` model")
        log_to_file(output_dir, (f"Model name : {cfm.name}"))
        if cfm.pretrained_weights:
            print(f"[INFO] Initialized model with pretrained weights")
            log_to_file(output_dir,(f"Used ST-provided pretrained weights"))
        elif cfm.pretrained_model_path:
            print(f"[INFO] Initialized model with weights from model file {cfm.pretrained_model_path}")
            log_to_file(output_dir, (f"Weights from model file : {cfm.pretrained_model_path}"))
        else:
            print("[INFO] No pretrained weights were loaded, training from randomly initialized weights.")
    elif cfg.training.resume_training_from:
        print(f"[INFO] Resuming training from model file {cfg.training.resume_training_from}")
        log_to_file(output_dir, (f"Model file : {cfg.training.resume_training_from}"))
    elif cfg.general.model_path:
        print(f"[INFO] Loaded model file {cfg.general.model_path}")
        log_to_file(output_dir ,(f"Model file : {cfg.general.model_path}"))
    if cfg.dataset.name: 
        log_to_file(output_dir, f"Dataset : {cfg.dataset.name}")

    # Set frozen layers
    # NOTE : This will be added at a later point.
    # Too much of a constantly changing mess for now.
    # if not cfg.training.resume_training_from:
    #     # Set frozen layers
    #     if not cfg.training.frozen_layers or cfg.training.frozen_layers == "None":
    #         model.trainable = True
    #     else:
    #         set_frozen_layers(model, frozen_layers=cfg.training.frozen_layers)

    # Set dropout rate
    # Technically it gets set twice here for models from the zoo, but we
    # need to keep this for user-provided model files.
    # This block shouldn't get triggered if dropout=0
    if "dropout" in cfg.training and cfg.training.dropout:
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

    if cfg.training.trained_model_path:
        # Check that the directory where the model must be saved exists.
        dir_name = os.path.dirname(cfg.training.trained_model_path)
        if not dir_name:
            dir_name = Path("./")
        if not os.path.isdir(dir_name):
            raise ValueError(
                "\nUnable to find directory {}\nPlease check the 'training.trained_model_path' "
                "attribute in your configuration file.".format(dir_name))

    # Initialize the augmented model that includes
    model_layers = []

    if not cfg.training.resume_training_from:
        # Append eventual data augmentation layers to the model
        if cfg.data_augmentation:
            data_augmentation_layers = get_data_augmentation(cfg=cfg.data_augmentation,
                                                            db_scale=cfg.feature_extraction.to_db)
            model_layers.extend(data_augmentation_layers)
        # Add the actual model to the model
        model_layers.append(model)

        augmented_model = tf.keras.Sequential(model_layers, name="augmented_model")

    else: # If we're resuming training we don't need to reappend the data augmentation layers.
        augmented_model = model


    # Compile the model with data augmentation layers added
    augmented_model.compile(loss=get_loss(multi_label=cfg.dataset.multi_label),
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

        if not check_training_determinism(augmented_model, sample_ds):
            print("[WARNING]: Some operations cannot be run deterministically. Setting deterministic_ops to False.")
            tf.config.experimental.enable_op_determinism.__globals__["_pywrap_determinism"].enable(False)

    # Train the model
    print("Starting training...")
    start_time = timer()
    try:
        history = augmented_model.fit(train_ds,
                                      validation_data=valid_ds,
                                      epochs=cfg.training.epochs,
                                      callbacks=callbacks)
    except Exception as e: 
        print('\n[INFO] :Training interrupted')
        print(f'Exception raised : {e}')  
    #save the last epoch history in the log file
    last_epoch=log_last_epoch_history(cfg, output_dir)
    end_time = timer()
    fit_run_time = int(end_time - start_time)
    average_time_per_epoch = round(fit_run_time / (int(last_epoch) + 1),2)
    print("Training runtime: " + str(timedelta(seconds=fit_run_time)))
    log_to_file(output_dir, (f"Training runtime : {fit_run_time} s\n" + f"Average time per epoch : {average_time_per_epoch} s"))          

    # Visualize training curves
    vis_training_curves(history=history, output_dir=output_dir)

    # Load the checkpoint model (best model obtained)
    models_dir = os.path.join(output_dir, saved_models_dir)
    checkpoint_filepath = Path(models_dir) / "best_augmented_model.h5"

    checkpoint_model = tf.keras.models.load_model(
        checkpoint_filepath,
        custom_objects={
            'VolumeAugment': VolumeAugment,
            'SpecAugment' : SpecAugment
        })

    # Get the checkpoint model w/o preprocessing layers
    print("[DEBUG] Summary of checkpoint model")
    model_summary(checkpoint_model)
    best_model = checkpoint_model.layers[-1]
    best_model.compile(loss=get_loss(multi_label=cfg.dataset.multi_label),
                       metrics=['accuracy'])
    best_model_path = Path(output_dir) / saved_models_dir / "best_model.h5"
    best_model.save(best_model_path)
    print("[DEBUG] Summary of best model")
    model_summary(best_model)

    # Save a copy of the best model if requested

    if cfg.training.trained_model_path:
        best_model.save(cfg.training.trained_model_path)
        print("[INFO] Saved trained model in file {}".format(cfg.training.trained_model_path))


    # Evaluate h5 best model on the validation set
    # It seems we aren't doing anything with the returned accuracies in image_classification either
    # So I just don't bother retrieving them.
    _, _ = evaluate_h5_model(model_path=best_model_path,
                             eval_ds=valid_ds,
                             class_names=class_names,
                             clip_labels=val_clip_labels,
                             output_dir=output_dir,
                             name_ds="validation_set",
                             multi_label=cfg.dataset.multi_label)

    if test_ds:
        # Evaluate h5 best model on the test set
        _, _ = evaluate_h5_model(model_path=best_model_path,
                                 eval_ds=test_ds,
                                 class_names=class_names,
                                 clip_labels=test_clip_labels,
                                 output_dir=output_dir,
                                 name_ds="test_set",
                                 multi_label=cfg.dataset.multi_label)

        # Record the whole hydra working directory to get all info
    mlflow.log_artifact(output_dir)
    return best_model_path
