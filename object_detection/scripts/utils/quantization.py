# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import pathlib

import cv2
import numpy as np
import tensorflow as tf
import tqdm
from hydra.core.hydra_config import HydraConfig


def TFLite_PTQ_quantizer(cfg, model, fake):
    def representative_data_gen():
        if fake is True:
            for _ in tqdm.tqdm(range(5)):
                data = np.random.rand(1, cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
                yield [data.astype(np.float32)]
        else:
            if cfg.quantization.quantization_dataset is not None:
                representative_ds_path = cfg.quantization.quantization_dataset
            else:

                if cfg.dataset.validation_path == None :

                    representative_ds_path = cfg.dataset.training_path

                    annotations = os.listdir(representative_ds_path)
                    nbannots = len(annotations)
                    all_annots = np.random.RandomState(seed=42).permutation(np.arange(nbannots))

                    validation_split = 0.2

                    train_split = all_annots[int(validation_split*nbannots):]
                    val_split = all_annots[:int(validation_split*nbannots)]

                    train_annotations,val_annotations = [annotations[i] for i in train_split],[annotations[i] for i in val_split]

                    list_of_files = train_annotations

                else:
                    representative_ds_path = cfg.dataset.training_path
                    list_of_files = os.listdir(representative_ds_path)


            for image_file in tqdm.tqdm(list_of_files):
                if image_file.endswith(".jpg"):
                    image = cv2.imread(os.path.join(representative_ds_path, image_file))
                    if len(image.shape) != 3:
                        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    resized_image = cv2.resize(image, (int(cfg.model.input_shape[0]), int(cfg.model.input_shape[0])), interpolation=cv2.INTER_LINEAR)
                    image_data = resized_image/cfg.pre_processing.rescaling.scale + cfg.pre_processing.rescaling.offset
                    img = image_data.astype(np.float32)
                    image_processed = np.expand_dims(img, 0)
                    yield [image_processed]
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    tflite_models_dir = pathlib.Path(os.path.join(HydraConfig.get().runtime.output_dir, "{}/".format(cfg.quantization.export_dir)))
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
