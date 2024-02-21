# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import io
import sys
import os
import cv2
import tqdm
import pathlib
import numpy as np
import tensorflow as tf
from hydra.core.hydra_config import HydraConfig

def load_quantization_data(directory: str):
    """
    Parse the training data and return a list of paths to annotation files.
    
    Args:
    - directory: A string representing the path to test set directory.
    
    Returns:
    - A list of strings representing the paths to test images.
    """
    annotation_lines = []
    path = directory+'/'
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            new_path = path+file
            annotation_lines.append(new_path)
    return annotation_lines

def tfite_ptq_quantizer(cfg, model, quantization_ds, output_dir, export_dir, fake):
    """
    Converts a Keras model to a TensorFlow Lite model with post-training quantization.

    Args:
        cfg (DictConfig): The configuration dictionary. Defaults to None.
        model: The Keras model to convert.
        quantization_ds:  the quantization dataset
        output_dir (str): Path to the output directory. Defaults to None.
        export_dir: The directory to export the TensorFlow Lite model to (default: 'tflite_models').
        fake: Whether to generate fake data instead of using the dataset (default: False).
    Returns:
        None.
    """
    input_shape = cfg.training.model.input_shape
    interpolation = cfg.preprocessing.resizing.interpolation
    if interpolation == 'bilinear':
        interpolation_type = cv2.INTER_LINEAR
    elif interpolation == 'nearest':
        interpolation_type = cv2.INTER_NEAREST
    else:
        raise ValueError("Invalid interpolation method. Supported methods are 'bilinear' and 'nearest'.")
    
    def representative_data_gen():
        if fake is True:
            for _ in tqdm.tqdm(range(5)):
                data = np.random.rand(1, int(input_shape[0]), int(input_shape[1]), 3)
                yield [data.astype(np.float32)]
        else:
            for image_file in tqdm.tqdm(quantization_ds):
                if image_file.endswith(".jpg"):
                    image = cv2.imread(image_file)
                    if len(image.shape) != 3:
                        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    resized_image = cv2.resize(image, (int(input_shape[0]), int(input_shape[0])), interpolation=interpolation_type)
                    image_data = resized_image * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset
                    img = image_data.astype(np.float32)
                    image_processed = np.expand_dims(img, 0)
                    yield [image_processed]
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    tflite_models_dir = pathlib.Path(output_dir, "{}/".format(export_dir))
    tflite_models_dir.mkdir(exist_ok=True, parents=True)

    if cfg.quantization.quantization_input_type == 'int8':
        converter.inference_input_type = tf.int8
    elif cfg.quantization.quantization_input_type == 'uint8':
        converter.inference_input_type = tf.uint8
    else:
        pass

    if cfg.quantization.quantization_output_type == 'int8':
        converter.inference_output_type = tf.int8
    elif cfg.quantization.quantization_output_type == 'uint8':
        converter.inference_output_type = tf.uint8
    else:
        pass

    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen

    tflite_model_quantio = converter.convert()
    tflite_model_quantio_file = tflite_models_dir/"quantized_model.tflite"
    tflite_model_quantio_file.write_bytes(tflite_model_quantio)

def quantize_tiny_yolo_v2(cfg = None, quantization_ds = None, fake = False, model_path = None) :
    """
    Quantize the TensorFlow model with training data.

    Args:
        cfg (DictConfig): The configuration dictionary. Defaults to None.
        quantization_ds (tf.data.Dataset): The quantization dataset if it's provided by the user else the training dataset. Defaults to None.
        fake (bool, optional): Whether to use fake data for representative dataset generation. Defaults to False.
        model_path (str, optional): Model path to quantize

    Returns:
        quantized model path (str)
    """

    if model_path:
        model_path = model_path
    else:
        model_path = cfg.general.model_path

    float_model =  tf.keras.models.load_model(model_path)
    
    output_dir = HydraConfig.get().runtime.output_dir
    export_dir = cfg.quantization.export_dir
    quantization_split = cfg.dataset.quantization_split
    quantization_path = cfg.dataset.quantization_path
    training_path = cfg.dataset.training_path
    fake = False
    if quantization_path and not quantization_split:
        print("[INFO] : Quantizing using the provided dataset ...")
        quantization_ds = load_quantization_data(quantization_path)
    elif quantization_path and quantization_split:
        print(f'[INFO] : Quantizing using {quantization_split * 100} % of the provided dataset...')
        quantization_set = load_quantization_data(quantization_path)
        num_subset = int(len(quantization_set)*quantization_split)
        num_set = len(quantization_set) - num_subset
        quantization_ds = quantization_set[num_set:]
    elif not quantization_path and quantization_split and training_path:
        print(f'[INFO] : Quantizing using {quantization_split * 100} % of the training set...')
        quantization_set = load_quantization_data(training_path)
        num_subset = int(len(quantization_set)*quantization_split)
        num_set = len(quantization_set) - num_subset
        quantization_ds = quantization_set[num_set:]
    elif not quantization_path and not quantization_split and training_path:
        print("[INFO] : Quantizing using the training dataset ...")
        quantization_ds = load_quantization_data(training_path)
    else:
        print('[INFO] : Neither quantization dataset or training set are provided! Using fake data to quantize the model. '
              'The model performances will not be accurate.')
        fake = True

    print("[INFO] : Quantizing the model ... This might take few minutes ...")

    if cfg['quantization']['quantizer'] == "TFlite_converter" and cfg['quantization']['quantization_type'] == "PTQ":
        tfite_ptq_quantizer(cfg, model=float_model, quantization_ds= quantization_ds,output_dir=output_dir, export_dir=export_dir,fake=fake)
        quantized_model_path = os.path.join(output_dir, export_dir, "quantized_model.tflite")

        return quantized_model_path
    else:
        raise TypeError("Quantizer and quantization type not supported yet!")