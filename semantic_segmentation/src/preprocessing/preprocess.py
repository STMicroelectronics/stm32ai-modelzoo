# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf
from PIL import Image
import os
import sys
from typing import Tuple

from data_loader import load_dataset
from models_utils import get_model_name_and_its_input_shape


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

    image_size = (input_shape[1:] if cfg.general.model_path and cfg.general.model_path.split('.')[-1] == 'onnx' 
                  else input_shape[:2])

    train_ds, valid_ds, quantization_ds, test_ds = load_dataset(cfg=cfg, image_size=image_size)

    return train_ds, valid_ds, quantization_ds, test_ds


def preprocess_image(img: np.ndarray = None, height: int = None, width: int = None, aspect_ratio: str = None,
                     interpolation: str = None, scale: float = None, offset: int = None,
                     perform_scaling: bool = True) -> tf.Tensor:

    """
    Predicts a class for all the images that are inside a given directory.
    The model used for the predictions can be either a .h5 or .tflite file.

    Args:
        img (np.ndarray): image to be prepared
        height (int): height in pixels
        width (int): width in pixels
        aspect_ratio (str): "fit' or "crop"
        interpolation (str): resizing interpolation method
        scale (float): rescaling pixels value
        offset (int): offset value on pixels
        perform_scaling (bool): whether to rescale or not the image

    Returns:
        img_processed (tf.Tensor): the prepared image

    """

    if aspect_ratio == "fit":
        img = tf.image.resize(img, [height, width], method=interpolation, preserve_aspect_ratio=False)
    else:
        img = tf.image.resize_with_crop_or_pad(img, height, width)

    # Rescale the image
    if perform_scaling:
        img_processed = scale * tf.cast(img, tf.float32) + offset
    else:
        img_processed = img

    return img_processed


def preprocess_input(image: np.ndarray, input_details: dict) -> tf.Tensor:
    """
    Preprocesses an input image according to input details.

    Args:
        image: Input image as a NumPy array.
        input_details: Dictionary containing input details, including quantization and dtype.

    Returns:
        Preprocessed image as a TensorFlow tensor.

    """

    # Get the dimensions
    if input_details is not None:
        if input_details['dtype'] in [np.uint8, np.int8]:
            image_processed = (image / input_details['quantization'][0]) + input_details['quantization'][1]
            image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min,
                                      np.iinfo(input_details['dtype']).max)
        else:
            image_processed = image
        image_processed = tf.cast(image_processed, dtype=input_details['dtype'])
    else:
        image_processed = image

    image_processed = tf.expand_dims(image_processed, 0)

    return image_processed


def postprocess_output_values(output: np.ndarray, output_details: dict) -> np.ndarray:
    """
    Postprocesses the model output to obtain the predicted label.

    Args:
        output (np.ndarray): The output tensor from the model.
        output_details: Dictionary containing output details, including quantization and dtype.

    Returns:
        np.ndarray: The predicted label.
    """
    if output_details is not None:
        if output_details['dtype'] in [np.uint8, np.int8]:
            # Convert the output data to float32 data type and perform the inverse quantization operation
            predicted_label = (output - output_details['quantization'][1]) * output_details['quantization'][0]
        else:
            predicted_label = output
    else:
        predicted_label = output

    return predicted_label
