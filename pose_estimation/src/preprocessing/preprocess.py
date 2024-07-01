# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2024 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

from omegaconf import DictConfig
import numpy as np
import tensorflow as tf
from typing import Tuple
import sys
import os

from models_utils import get_model_name_and_its_input_shape
from data_loader import load_dataset


def preprocess(cfg: DictConfig = None) -> Tuple:
    """
    Preprocesses the data based on the provided configuration.

    Args:
        cfg (DictConfig): Configuration object containing the settings.

    Returns:
        Tuple: A tuple containing the following:
            - data_augmentation (object): Data augmentation object.
            - augment (bool): Flag indicating whether data augmentation is enabled.
            - pre_process (object): Preprocessing object.
            - train_ds (object): Training dataset.
            - valid_ds (object): Validation dataset.
    """

    # Get the model input shape
    if cfg.general.model_path:
        _, input_shape = get_model_name_and_its_input_shape(cfg.general.model_path)
    else:
        # We are running a training using the 'training' section of the config file.
        if cfg.training.model:
            input_shape = cfg.training.model.input_shape
        else:
            _, input_shape = get_model_name_and_its_input_shape(cfg.training.resume_training_from)

    interpolation = cfg.preprocessing.resizing.interpolation
    aspect_ratio = cfg.preprocessing.resizing.aspect_ratio

    # Set a default value to 32 for the 'evaluation' mode
    # in case a 'training' section is not available
    batch_size = cfg.training.batch_size if cfg.training else 32

    train_ds, valid_ds, quantization_ds, test_ds = load_dataset(
        dataset_name=cfg.dataset.name,
        training_path=cfg.dataset.training_path,
        validation_path=cfg.dataset.validation_path,
        quantization_path=cfg.dataset.quantization_path,
        test_path=cfg.dataset.test_path,
        validation_split=cfg.dataset.validation_split,
        nbr_keypoints=cfg.dataset.keypoints,
        image_size= input_shape[1:] if cfg.general.model_path and cfg.general.model_path.split('.')[-1]=='onnx' else input_shape[:2],
        interpolation=interpolation,
        aspect_ratio=aspect_ratio,
        color_mode=cfg.preprocessing.color_mode,
        batch_size=batch_size,
        seed=cfg.dataset.seed)
                 
    return train_ds, valid_ds, quantization_ds, test_ds


def apply_rescaling(dataset: tf.data.Dataset = None, scale: float = None, offset: float = None):
    """
    Applies rescaling to a dataset using a tf.keras.Sequential model.

    Args:
        dataset (tf.data.Dataset): The dataset to be rescaled.
        scale (float): The scaling factor.
        offset (float): The offset factor.

    Returns:
        The rescaled dataset.
    """
    # Define the rescaling model
    rescaling = tf.keras.Sequential([
        tf.keras.layers.Rescaling(scale, offset)
    ])

    # Apply the rescaling to the dataset
    rescaled_dataset = dataset.map(lambda x, y: (rescaling(x), y))

    return rescaled_dataset


def apply_normalization(dataset: tf.data.Dataset = None, mean: float = None, variance: float = None):
    """
    Applies normalization to a dataset using a tf.keras.Sequential model.

    Args:
        dataset (tf.data.Dataset): The dataset to be rescaled.
        mean (float): The mean of the three channels.
        variance (float): The vairance of the three channels.

    Returns:
        The rescaled dataset.
    """
    # Define the rescaling model
    normalization = tf.keras.Sequential([
        tf.keras.layers.Normalization(mean=mean, variance=variance)
    ])

    # Apply the rescaling to the dataset
    normalized_dataset = dataset.map(lambda x, y: (normalization(x), y))

    return normalized_dataset


def apply_rescaling_on_image(image: tf.Tensor = None, scale: float = None, offset: float = None) -> tf.Tensor:
    """
    Applies rescaling to an image using a tf.keras.Sequential model.

    Args:
        image (tf.Tensor): The image to be rescaled.
        scale (float): The scaling factor.
        offset (float): The offset factor.

    Returns:
        The rescaled image.
    """
    # Define the rescaling model
    rescaling = tf.keras.Sequential([
        tf.keras.layers.Rescaling(scale, offset)
    ])

    # Apply the rescaling to the image
    rescaled_image = rescaling(image)

    return rescaled_image


def preprocess_input(image: np.ndarray, input_details: dict) -> tf.Tensor:
    """
    Preprocesses an input image according to input details.

    Args:
        image: Input image as a NumPy array.
        input_details: Dictionary containing input details, including quantization and dtype.

    Returns:
        Preprocessed image as a TensorFlow tensor.

    """

    image = tf.image.resize(image, (input_details['shape'][1], input_details['shape'][2]))
    # Get the dimensions
    if input_details['dtype'] in [np.uint8, np.int8]:
        image_processed = (image / input_details['quantization'][0]) + input_details['quantization'][1]
        image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min,
                                  np.iinfo(input_details['dtype']).max)

    else:
        image_processed = image
    image_processed = tf.cast(image_processed, dtype=input_details['dtype'])
    image_processed = tf.expand_dims(image_processed, 0)
    return image_processed


def postprocess_output(output: np.ndarray, output_details: dict) -> np.ndarray:
    """
    Postprocesses the model output to obtain the predicted label.

    Args:
        output (np.ndarray): The output tensor from the model.
        output_details: Dictionary containing output details, including quantization and dtype.

    Returns:
        np.ndarray: The predicted label.
    """
    if output_details['dtype'] in [np.uint8, np.int8]:
        # Convert the output data to float32 data type and perform the inverse quantization operation
        predicted_label = (output - output_details['quantization'][1]) * output_details['quantization'][0]
    if output.shape[1] > 1:
        predicted_label = np.argmax(output, axis=1)
    else:
        predicted_label = np.where(output < 0.5, 0, 1)
    return predicted_label
