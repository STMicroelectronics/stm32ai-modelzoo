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
from typing import Tuple, List, Dict, Optional

import mlflow
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf

from utils import model_summary, check_training_determinism, log_to_file, log_last_epoch_history
from preprocess import apply_rescaling
from models_mgt import get_model
from data_augmentation_layer import DataAugmentationLayer
import data_augmentation
import lr_schedulers
from evaluate import evaluate_h5_model
from visualizer import vis_training_curves

import logging
logging.getLogger('tensorflow').setLevel(logging.WARNING)

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


def load_model_to_train(cfg, model_path=None, num_classes=None) -> tf.keras.Model:
    """
    This function loads the model to train, which can be either a:
    - model from the zoo (MobileNet, FD-MobileNet, etc).
    - .h5 model
    - .h5 model with preprocessing layers included if the training
      is being resumed.
    These 3 different cases are mutually exclusive.

    Arguments:
        cfg (DictConfig): a dictionary containing the 'training' section 
                          of the configuration file.
        model_path (str): a path to a .h5 file provided using the 
                          'general.model_path' attribute.

    Return:
        tf.keras.Model: a keras model.
    """
    
    if cfg.model:
        # Model from the zoo
        model = get_model(
            cfg=cfg.model,
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
        model = tf.keras.models.load_model(
                        cfg.resume_training_from,
                        custom_objects={
                            'DataAugmentationLayer': DataAugmentationLayer})
        input_shape = tuple(model.input.shape[1:])

        # Check that the model includes the preprocessing layers
        expected = False
        if len(model.layers) == 2:
            if model.layers[0].__class__.__name__ == "Rescaling":
                expected = True
        elif len(model.layers) == 3:
            if model.layers[0].__class__.__name__ == "Rescaling" and \
               model.layers[1].__class__.__name__ == "DataAugmentationLayer":
                expected = True
        if not expected:
            raise RuntimeError("\nThe model does not include preprocessing layers (rescaling, data augmentation).\n"
                               f"Received model path: {cfg.resume_training_from}\nTraining can only be resumed from "
                               "the 'best_augmented_model.h5' or 'last_augmented_model.h5' model files\nsaved in "
                               "the 'saved_models_dir' directory during a previous training run.")
    else:
        raise RuntimeError("\nInternal error: should have model, model_path or resume_training_from")

    return model, input_shape


def set_frozen_layers(model: tf.keras.Model, frozen_layers: str = None) -> None:
    """
    This function freezes (makes non-trainable) the layers that are 
    specified by the `frozen_layers` attribute. If `frozen_layers` is `None`,
    then all layers in the model are made trainable.
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
        frozen_layers (str): the indices of the layers to freeze. If `None`, all layers are made trainable.

    Returns:
        None
    """
    if frozen_layers == 'None':
        # Train the whole model
        model.trainable = True
        return
    
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


def add_preprocessing_layers(
                model: tf.keras.Model,
                input_shape: Tuple = None, 
                scale: float = None,
                offset: float = None,
                data_augmentation: Dict = None,
                batches_per_epoch: float = None):
    """
    This function adds the rescaling and data augmentation preprocessing layers.

    Arguments:
        model (tf.keras.Model): the model preprocessing layers will be added to.
        input_shape (Tuple): input shape of the model.
        scale (float): scale to use for rescaling the images.
        offset (float): offset to use for rescaling the images.
        data_augmentation (Dict): dictionary containing the data augmentation functions.
        batches_per_epoch: number of training batches per epoch.
        
    Returns:
        None
    """

    model_layers = []
    model_layers.append(tf.keras.Input(shape=input_shape))

    # Add the rescaling layer
    model_layers.append(tf.keras.layers.Rescaling(scale, offset))

    # If data augmentation is used, add the custom .
    if data_augmentation:
        # Add the data augmentation layer
        pixels_range = (offset, scale * 255 + offset)
        model_layers.append(
            DataAugmentationLayer(
                data_augmentation_fn=data_augmentation.function_name,
                config=data_augmentation.config,
                pixels_range=pixels_range,
                batches_per_epoch=batches_per_epoch
            )
        )
    model_layers.append(model)
    augmented_model = tf.keras.Sequential(model_layers, name="augmented_model")

    return augmented_model


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


def get_loss(num_classes: int) -> tf.keras.losses:
    """
    Returns the appropriate loss function based on the number of classes in the dataset.

    Args:
        num_classes (int): The number of classes in the dataset.

    Returns:
        tf.keras.losses: The appropriate loss function based on the number of classes in the dataset.
    """
    # We use the sparse version of the categorical crossentropy because
    # this is what we use to load the dataset.
    if num_classes > 2:
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
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

    output_dir = HydraConfig.get().runtime.output_dir
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

    # Load the model to train
    model, input_shape = load_model_to_train(cfg.training, model_path=cfg.general.model_path, num_classes=num_classes)

    # Info messages about the model that was loaded
    if cfg.training.model:
        cfm = cfg.training.model
        print(f"[INFO] Using `{cfm.name}` model")
        log_to_file(cfg.output_dir, (f"Model name : {cfm.name}"))
        if cfm.pretrained_weights:
            print(f"[INFO] Initialized model with '{cfm.pretrained_weights}' pretrained weights")
            log_to_file(cfg.output_dir,(f"Pretrained weights : {cfm.pretrained_weights}"))
        elif cfm.pretrained_model_path:
            print(f"[INFO] Initialized model with weights from model file {cfm.pretrained_model_path}")
            log_to_file(cfg.output_dir, (f"Weights from model file : {cfm.pretrained_model_path}"))
        else:
            print("[INFO] No pretrained weights were loaded, training from randomly initialized weights.")

    elif cfg.training.resume_training_from:
        print(f"[INFO] Resuming training from model file {cfg.training.resume_training_from}")
        log_to_file(cfg.output_dir, (f"Model file : {cfg.training.resume_training_from}"))
    elif cfg.general.model_path:
        print(f"[INFO] Loaded model file {cfg.general.model_path}")
        log_to_file(cfg.output_dir ,(f"Model file : {cfg.general.model_path}"))
    if cfg.dataset.name: 
        log_to_file(output_dir, f"Dataset : {cfg.dataset.name}")

    if not cfg.training.resume_training_from:
        model.trainable = True
        if cfg.training.frozen_layers:
            set_frozen_layers(model, frozen_layers=cfg.training.frozen_layers)
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

    if not cfg.training.resume_training_from:
        # Add the preprocessing layers to the model
        augmented_model = add_preprocessing_layers(model,
                                input_shape=input_shape,
                                scale=cfg.preprocessing.rescaling.scale,
                                offset=cfg.preprocessing.rescaling.offset,
                                data_augmentation=cfg.data_augmentation,
                                batches_per_epoch=len(train_ds))
        # Compile the augmented model
        augmented_model.compile(loss=get_loss(num_classes=num_classes),
                                metrics=['accuracy'],
                                optimizer=get_optimizer(cfg=cfg.training.optimizer))
    else:
        # The preprocessing layers are already included.
        # We don't compile the model otherwise we would 
        # loose the loss and optimizer states.
        augmented_model = model

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
    except: 
        print('\n[INFO] Training interrupted')  
    #save the last epoch history in the log file
    last_epoch=log_last_epoch_history(cfg, output_dir)
    end_time = timer()
    
    #calculate and log the runtime in the log file
    fit_run_time = int(end_time - start_time)
    average_time_per_epoch = round(fit_run_time / (int(last_epoch) + 1),2)
    print("Training runtime: " + str(timedelta(seconds=fit_run_time))) 
    log_to_file(cfg.output_dir, (f"Training runtime : {fit_run_time} s\n" + f"Average time per epoch : {average_time_per_epoch} s"))          

    # Visualize training curves
    vis_training_curves(history=history, output_dir=output_dir)

    # Load the checkpoint model (best model obtained)
    models_dir = os.path.join(output_dir, saved_models_dir)
    checkpoint_filepath = os.path.join(models_dir, "best_augmented_model.h5")

    checkpoint_model = tf.keras.models.load_model(
        checkpoint_filepath,
        custom_objects={
            'DataAugmentationLayer': DataAugmentationLayer
        })
 
    # Get the checkpoint model w/o preprocessing layers
    best_model = checkpoint_model.layers[-1]
    best_model.compile(loss=get_loss(num_classes), metrics=['accuracy'])
    best_model_path = os.path.join(output_dir,
                                   "{}/{}".format(saved_models_dir, "best_model.h5"))
    best_model.save(best_model_path)

    # Save a copy of the best model if requested
    if cfg.training.trained_model_path:
        best_model.save(cfg.training.trained_model_path)
        print("[INFO] Saved trained model in file {}".format(cfg.training.trained_model_path))

    # Pre-process validation dataset
    valid_ds = apply_rescaling(dataset=valid_ds, scale=cfg.preprocessing.rescaling.scale,
                               offset=cfg.preprocessing.rescaling.offset)

    # Evaluate h5 best model on the validation set
    evaluate_h5_model(model_path=best_model_path, eval_ds=valid_ds,
                     class_names=class_names, output_dir=output_dir, name_ds="validation_set")

    if test_ds:
        # Pre-process test dataset
        test_ds = apply_rescaling(dataset=test_ds, scale=cfg.preprocessing.rescaling.scale,
                                  offset=cfg.preprocessing.rescaling.offset)

        # Evaluate h5 best model on the test set
        best_model_test_acc = evaluate_h5_model(model_path=best_model_path, eval_ds=test_ds,
                                                class_names=class_names, output_dir=output_dir, name_ds="test_set")

    # Record the whole hydra working directory to get all info
    mlflow.log_artifact(output_dir)

    return best_model_path
