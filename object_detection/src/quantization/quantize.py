# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from pathlib import Path
from glob import glob
import tqdm
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
import random
import numpy as np
import tensorflow as tf
from typing import List

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../preprocessing'))

from preprocess import load_and_preprocess_image
from models_mgt import get_model_name_and_its_input_shape


def tfite_ptq_quantizer(
            cfg: DictConfig,
            float_model: tf.keras.Model = None,
            image_shape: List = None,
            image_file_paths: List = None,
            num_fake_images: int = None):
    """
    Quantize a Keras model using TFlite

    Args:
        cfg (DictConfig): Entire configuration file.
        float_model (tf.keras.Model): The Keras float model to convert.
        input_shape (List): Input shape of the model.
        image_file_paths (List): Paths to the image files of the representative dataset to use.
                If the argument is not set, no dataset is available and fake data has to be used.
        num_fake_images: Number of random images to generate when using fake data.

    Returns:
        Quantized TFlite model
    """

    def representative_data_gen():
        cpp = cfg.preprocessing
        for path in tqdm.tqdm(image_file_paths):
            image = load_and_preprocess_image(
                            image_file_path=path,
                            image_size=image_shape[:2],
                            scale=cpp.rescaling.scale,
                            offset=cpp.rescaling.offset,
                            interpolation=cpp.resizing.interpolation,
                            color_mode=cpp.color_mode)
            image = np.expand_dims(image, axis=0)
            yield [image]


    def fake_data_gen():
        for _ in tqdm.tqdm(range(num_fake_images)):
            image = tf.random.uniform(image_shape, minval=0, maxval=256, dtype=tf.int8)
            image = tf.cast(image, tf.float32)
            
            # Rescale the image
            cpp = cfg.preprocessing.rescaling
            image = image * cpp.scale + cpp.offset

            image = tf.expand_dims(image, axis=0)
            yield [image.numpy()]


    converter = tf.lite.TFLiteConverter.from_keras_model(float_model)

    # Set the quantization type for the input images
    input_type = cfg.quantization.quantization_input_type
    if input_type == 'int8':
        converter.inference_input_type = tf.int8
    elif input_type == 'uint8':
        converter.inference_input_type = tf.uint8
    else:
        pass

    # Set the quantization type for the output images
    output_type = cfg.quantization.quantization_output_type
    if output_type == 'int8':
        converter.inference_output_type = tf.int8
    elif output_type == 'uint8':
        converter.inference_output_type = tf.uint8
    else:
        pass
    
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    if image_file_paths:
        converter.representative_dataset = representative_data_gen
    else:
        converter.representative_dataset = fake_data_gen

    quantized_model = converter.convert()
    return quantized_model


def quantize(cfg: DictConfig, model_path: str = None):

    if cfg.dataset.quantization_path:
        dataset_path = cfg.dataset.quantization_path
    elif cfg.dataset.training_path:
        dataset_path = cfg.dataset.training_path
    else:
        dataset_path = None

    if dataset_path:
        image_file_paths = glob(dataset_path + "/*.jpg")
        random.shuffle(image_file_paths)
        # Split the dataset if quantization_split is requested
        if cfg.dataset.quantization_split and cfg.dataset.quantization_split < 1.0:
            num_files = int(len(image_file_paths) * cfg.dataset.quantization_split)
            image_file_paths = image_file_paths[:num_files]
    else:
        image_file_paths = None

    # Display some info messages about the image data
    print("[INFO] Quantizing float model")
    if dataset_path:
        if cfg.dataset.quantization_split and cfg.dataset.quantization_split < 1.0:
            percentage_used = " {}% of".format(int(cfg.dataset.quantization_split * 100))
        else:
            percentage_used = ""
        num_files = len(image_file_paths)
        if cfg.dataset.quantization_path:
            print(f"[INFO] Using{percentage_used} the quantization set as representative data ({num_files} images)")
        elif cfg.dataset.training_path:
            print(f"[INFO] Using{percentage_used} the training set as representative data ({num_files} images)")
    else:
        print("[INFO] No quantization set or training set were provided, using fake image data")

    # Load the float model and get its input shape
    if not model_path:
        model_path = cfg.general.model_path
    _, model_input_shape = get_model_name_and_its_input_shape(model_path=model_path)
    float_model = tf.keras.models.load_model(model_path, compile=False)

    tflite_model = tfite_ptq_quantizer(cfg,
                                       float_model=float_model,
                                       image_shape=model_input_shape,
                                       image_file_paths=image_file_paths,
                                       num_fake_images=100)

    # Create the export directory if it does not exist
    export_dir = os.path.join(HydraConfig.get().runtime.output_dir, cfg.quantization.export_dir)
    os.makedirs(export_dir, exist_ok=True)

    # Save the TFlite model
    tflite_model_path = os.path.join(export_dir, "quantized_model.tflite")
    with open(tflite_model_path, "wb") as f:
        f.write(tflite_model)

    print("[INFO] Float model quantization complete")

    return tflite_model_path
