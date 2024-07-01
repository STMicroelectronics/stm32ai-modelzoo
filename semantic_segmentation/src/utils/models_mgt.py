#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import os
from typing import Optional, List, Union
import tensorflow as tf
from omegaconf import DictConfig


from models_utils import transfer_pretrained_weights, check_attribute_value, check_model_support
from cfg_utils import check_attributes
from deeplabv3 import get_deeplab_v3
from custom_model import get_custom_model


def check_mobilenet(cfg: DictConfig = None, section: str = None, message: str = None):
    """
    Utility function that checks the attributes and pretrained weights
    of MobileNet-V1 and MobileNet-V2 models.
    """
    check_attributes(cfg, expected=["name", "version", "alpha", "input_shape", "output_stride"],
                     optional=["pretrained_weights", "pretrained_model_path"], section=section)
    if cfg.pretrained_weights and cfg.pretrained_model_path:
        raise ValueError("\nThe `pretrained_weights` and `pretrained_model_path` attributes "
                         "are mutually exclusive.{}".format(message))
    if cfg.pretrained_weights:
        if cfg.pretrained_weights == "None":
            cfg.pretrained_weights = None
        check_attribute_value(cfg.pretrained_weights, values=[None, "imagenet"], name="pretrained_weights",
                              message=message)


def get_model(cfg: DictConfig = None) -> tf.keras.Model:
    """
    Returns a Keras model object based on the specified configuration and parameters.

    Args:
        cfg (DictConfig): A dictionary containing the full configuration parameters.
        num_classes (int): The number of classes for the model.
        dropout (float): The dropout rate for the model.

    Returns:
        tf.keras.Model: A Keras model object based on the specified configuration and parameters.
    """
    # Define the supported models and their versions
    supported_models = {'deeplab_v3': None,
                        'custom': None}
    section = "general"
    message = "\nPlease check the '{}' section of your configuration file.".format(section)

    # Check if the specified model is supported
    model_type = cfg.general.model_type
    num_classes = len(cfg.dataset.class_names)

    if model_type:
        check_model_support(model_type, version=None, supported_models=supported_models, message=message)
    
    backbone_model = cfg.training.model.name
    backbone_version = cfg.training.model.version
    backbone_model_alpha = cfg.training.model.alpha
    backbone_model_pretrained_weights = cfg.training.model.pretrained_weights
    output_stride = cfg.training.model.output_stride

    dropout_rate = cfg.training.dropout
    input_shape = cfg.training.model.input_shape

    if cfg.training.model.pretrained_model_path:
        raise ValueError("\nPretrained model usage is not yet enabled for segmentation.")

    if model_type == 'deeplab_v3':
        if backbone_model == "mobilenet" and backbone_version == "v2":
            section = "training.model"
            check_mobilenet(cfg.training.model, section=section, message=message)

            model = get_deeplab_v3(input_shape=input_shape, backbone=backbone_model, version=backbone_version,
                                   alpha=backbone_model_alpha, dropout=dropout_rate,pretrained_weights=backbone_model_pretrained_weights, 
                                   num_classes=num_classes, output_stride=output_stride)
        else:
            raise ValueError("\nThe only backbone supported so far is Mobilenet v2. Please update the config yaml "
                             "file accordingly.")
    # If the model is a custom model
    if model_type == "custom":
        section = "training.model"
        check_attributes(cfg.training.model, expected=["input_shape"], optional=["name", "pretrained_model_path"],
                         section=section)
        model = get_custom_model(num_classes=num_classes, input_shape=input_shape, dropout=dropout_rate)

    return model
        

def load_model_for_training(cfg: DictConfig) -> tuple:
    """"
    Loads a model for training.
    
    The model to train can be:
    - a model from the Model Zoo
    - a user model (BYOM)
    - a model previously trained during a training that was interrupted.
    
    When a training is run, the following files are saved in the saved_models
    directory:
        base_model.h5:
            Model saved before the training started. Weights are random.
        best_weights.h5:
            Best weights obtained since the beginning of the training.
        last_weights.h5:
            Weights saved at the end of the last epoch.
    
    To resume a training, the last weights are loaded into the base model.
    """
    
    # Bring your own model
    if cfg.general.model_path:
        print("[INFO] Loading model file:", cfg.general.model_path)
        model = tf.keras.models.load_model(cfg.general.model_path, compile=False)
        input_shape = tuple(model.input.shape[1:])

    # Resume a previously interrupted training
    elif cfg.training.resume_training_from:
        resume_dir = os.path.join(cfg.training.resume_training_from, cfg.general.saved_models_dir)
        if not os.path.isdir(resume_dir):
            raise FileNotFoundError(f"\nCould not find directory {resume_dir}\n"
                                    f"Unable to resume training.")
        print(f"[INFO] Resuming training from directory {cfg.training.resume_training_from}")
        model_path = os.path.join(resume_dir, "base_model.h5")
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"\nCould not find model file {model_path}\n"
                                    f"Unable to resume training from directory {resume_dir}")
        last_weights_path = os.path.join(resume_dir, "last_weights.h5")
        if not os.path.isfile(last_weights_path):
            raise FileNotFoundError(f"\nCould not find model weights file {last_weights_path}\n"
                                    f"Unable to resume training from directory {resume_dir}")
        
        model = tf.keras.models.load_model(model_path, compile=False)
        model.load_weights(last_weights_path)
        input_shape = tuple(model.input.shape[1:])

    # Train a model from the Model Zoo
    else:
        model = get_model(cfg)
        input_shape = cfg.training.model.input_shape

    return model, input_shape

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

def segmentation_loss(logits: tf.Tensor, labels: tf.Tensor, num_classes: int = 21, ignore_label: 
                      int = 255, loss_weights: Optional[Union[List[float], tf.Tensor]] = None) -> tf.Tensor:
    """
    Calculate the weighted softmax cross-entropy loss for segmentation tasks.

    Args:
        logits (tf.Tensor): The raw output of the network, which represents the
                            prediction for each pixel.
        labels (tf.Tensor): The ground truth labels for each pixel.
        num_classes (int, optional): The number of classes in the segmentation task.
                                     Defaults to 21.
        ignore_label (int, optional): The label that should be ignored in the loss
                                      computation. Defaults to 255.
        loss_weights (list or tf.Tensor, optional): Weights for each class that are
                                                    applied to the loss. The default
                                                    is None, which creates a list of
                                                    weights with 0.5 for the background
                                                    class and 1.0 for all other classes.

    Returns:
        tf.Tensor: The computed loss as a scalar tensor.
    """
    # If no specific loss weights are provided, initialize them with default values.
    if loss_weights is None:
        if num_classes == 21:
            loss_weights = [0.5] + [1.0] * (num_classes - 1)
        else:
            loss_weights = [1.0] * (num_classes - 1)

    with tf.name_scope('seg_loss'):
        # Flatten logits and labels tensors for processing.
        logits = tf.reshape(logits, [-1, num_classes])
        labels = tf.reshape(labels, [-1])

        # Create a mask to exclude the ignored label from the loss computation.
        not_ignored_mask = tf.not_equal(labels, ignore_label)
        labels = tf.boolean_mask(labels, not_ignored_mask)
        logits = tf.boolean_mask(logits, not_ignored_mask)

        # Cast labels to an integer type for further processing.
        labels = tf.cast(labels, tf.int32)

        # Apply class weights if provided.
        if isinstance(loss_weights, list) or isinstance(loss_weights, tf.Tensor):
            class_weights = tf.constant(loss_weights, dtype=tf.float32)
            weights = tf.gather(class_weights, labels)
        else:
            weights = loss_weights
        
        # Convert labels to one-hot encoding for compatibility with softmax cross entropy.
        labels_one_hot = tf.one_hot(labels, depth=num_classes)

        # Compute the softmax cross entropy loss for each pixel.
        pixel_losses = tf.nn.softmax_cross_entropy_with_logits(labels=labels_one_hot, logits=logits)
        weighted_pixel_losses = pixel_losses * weights
        total_loss = tf.reduce_sum(weighted_pixel_losses)

        # Calculate the number of pixels that contribute to the loss (excluding ignored ones).
        num_positive = tf.reduce_sum(tf.cast(not_ignored_mask, tf.float32))

        # Normalize the loss by the number of contributing pixels to get the final loss value.
        loss = total_loss / (num_positive + 1e-5)

        return loss


def get_custom_loss(num_classes: int = 21) -> tf.keras.losses.Loss:
    """
    Creates a custom loss function for a segmentation model with predefined parameters.

    Args:
        num_classes (int, optional): The number of classes in the segmentation task.
                                     Defaults to 21.
        ignore_label (int, optional): The label that should be ignored in the loss
                                      computation. Defaults to 255.
        loss_weights (Optional[Union[List[float], tf.Tensor]], optional): Weights for each class that are
                                                    applied to the loss. The default
                                                    is None, which creates a list of
                                                    weights with 0.5 for the background
                                                    class and 1.0 for all other classes.

    Returns:
        tf.keras.losses.Loss: A custom loss function that can be used in training a model.
    """
    def custom_loss(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
        """
        The custom loss function that will be used during model training.

        Args:
            y_true (tf.Tensor): The ground truth labels for each pixel.
            y_pred (tf.Tensor): The predicted labels for each pixel.

        Returns:
            tf.Tensor: The computed loss as a scalar tensor.
        """
        # Call the segmentation_loss function with the predefined parameters.
        return segmentation_loss(logits=y_pred, labels=y_true, num_classes=num_classes)

    return custom_loss