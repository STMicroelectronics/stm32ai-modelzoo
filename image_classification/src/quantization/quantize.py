# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import pathlib
import numpy as np
import tensorflow as tf
import tqdm
import sys
import os
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../evaluation'))
sys.path.append(os.path.abspath('../preprocessing'))
sys.path.append(os.path.abspath('../../common'))
from preprocess import apply_rescaling
from typing import Optional
from models_mgt import get_model_name_and_its_input_shape


def tflite_ptq_quantizer(model: tf.keras.Model = None, quantization_ds: tf.data.Dataset = None, fake: bool = False,
                         output_dir: str = None, export_dir: Optional[str] = None, input_shape: tuple = None,
                         quantization_input_type: str = None, quantization_output_type: str = None,
                         quantization_split: str = None, quantization_path: str = None) -> None:
    """
    Perform post-training quantization on a TensorFlow Lite model.

    Args:
        model (tf.keras.Model): The TensorFlow model to be quantized.
        quantization_ds (tf.data.Dataset): The quantization dataset if it's provided by the user else the training dataset. Defaults to None
        fake (bool): Whether to use fake data for representative dataset generation.
        output_dir (str): Path to the output directory. Defaults to None.
        export_dir (str): Name of the export directory. Defaults to None.
        input_shape (tuple: The input shape of the model. Defaults to None.
        quantization_input_type (str): The quantization type for the input. Defaults to None.
        quantization_output_type (str): The quantization type for the output. Defaults to None.
        quantization_path (str): the quantization dataset path if it's provided by the user.  Defaults to None.
        quantization_split (str): The Fraction of the data to use for the quantization

    Returns:
        None
    """

    def representative_data_gen():
        """
        Generate representative data for post-training quantization.

        Yields:
            List[tf.Tensor]: A list of TensorFlow tensors representing the input data.
        """
        if fake:
            for _ in tqdm.tqdm(range(5)):
                data = np.random.rand(1, input_shape[0], input_shape[1], input_shape[2])
                yield [data.astype(np.float32)]

        else:
            if not quantization_split or quantization_path:
                print("[INFO] : Quantizing by using the provided dataset fully...")
                for images, labels in tqdm.tqdm(quantization_ds, total=len(quantization_ds)):
                    for image in images:
                        image = tf.cast(image, dtype=tf.float32)
                        image = tf.expand_dims(image, 0)
                        yield [image]
            else:
                print(f'[INFO] : Quantizing by using {quantization_split * 100} % of the provided dataset...')
                quantization_ds_size = len(quantization_ds)
                splited_ds = quantization_ds.take(int(quantization_ds_size * float(quantization_split)))
                for images, labels in tqdm.tqdm(splited_ds, total=len(splited_ds)):
                    for image in images:
                        image = tf.cast(image, dtype=tf.float32)
                        image = tf.expand_dims(image, 0)
                        yield [image]

    # Create the TFLite converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Create the output directory
    tflite_models_dir = pathlib.Path(os.path.join(output_dir, "{}/".format(export_dir)))
    tflite_models_dir.mkdir(exist_ok=True, parents=True)

    # Set the quantization types for the input and output
    if quantization_input_type == 'int8':
        converter.inference_input_type = tf.int8
    elif quantization_input_type == 'uint8':
        converter.inference_input_type = tf.uint8
    else:
        pass
    if quantization_output_type == 'int8':
        converter.inference_output_type = tf.int8
    elif quantization_output_type == 'uint8':
        converter.inference_output_type = tf.uint8
    else:
        pass

    # Set the optimizations and representative dataset generator
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen

    # Convert the model to a quantized TFLite model
    tflite_model_quantized = converter.convert()
    tflite_model_quantized_file = tflite_models_dir / "quantized_model.tflite"
    tflite_model_quantized_file.write_bytes(tflite_model_quantized)


def quantize(cfg: DictConfig = None, quantization_ds: Optional[tf.data.Dataset] = None, fake: Optional[bool] = False,
             float_model_path: Optional[str] = None) -> str:
    """
    Quantize the TensorFlow model with training data.

    Args:
        cfg (DictConfig): The configuration dictionary. Defaults to None.
        quantization_ds (tf.data.Dataset): The quantization dataset if it's provided by the user else the training dataset. Defaults to None.
        fake (bool, optional): Whether to use fake data for representative dataset generation. Defaults to False.
        float_model_path (str, optional): Model path to quantize

    Returns:
        quantized model path (str)
    """
    '''
    if float_model_path:
        model_path = float_model_path
        model_name, input_shape = get_model_name_and_its_input_shape(model_path=model_path)
    else:
        model_path = cfg.general.model_path
        input_shape = cfg.general.model.input_shape
    '''

    model_path = float_model_path if float_model_path else cfg.general.model_path
    _, input_shape = get_model_name_and_its_input_shape(model_path=model_path)
   
    float_model = tf.keras.models.load_model(model_path)
    output_dir = HydraConfig.get().runtime.output_dir
    export_dir = cfg.quantization.export_dir
    print("[INFO] : Quantizing the model ... This might take few minutes ...")
    if cfg['quantization']['quantizer'] == "TFlite_converter" and cfg['quantization'][
        'quantization_type'] == "PTQ":
        if fake:
            tflite_ptq_quantizer(model=float_model, fake=fake, output_dir=output_dir,
                                 export_dir=export_dir, input_shape=input_shape,
                                 quantization_input_type=cfg.quantization.quantization_input_type,
                                 quantization_output_type=cfg.quantization.quantization_output_type)
        else:
            # Quantize the model with training data
            quantization_split = cfg.dataset.quantization_split
            quantization_path = cfg.dataset.quantization_path
            quantization_ds = apply_rescaling(dataset=quantization_ds, scale=cfg.preprocessing.rescaling.scale,
                                              offset=cfg.preprocessing.rescaling.offset)
            tflite_ptq_quantizer(model=float_model, quantization_ds=quantization_ds, output_dir=output_dir,
                                 export_dir=export_dir, input_shape=input_shape,
                                 quantization_input_type=cfg.quantization.quantization_input_type,
                                 quantization_output_type=cfg.quantization.quantization_output_type,
                                 quantization_split=quantization_split, quantization_path=quantization_path)
        quantized_model_path = os.path.join(output_dir, export_dir, "quantized_model.tflite")
        return quantized_model_path
    else:
        raise TypeError("Quantizer and quantization type not supported yet!")
