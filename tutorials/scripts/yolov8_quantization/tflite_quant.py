# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
import logging
import warnings
import random
import hydra
import tqdm
import cv2
import pathlib

import tensorflow as tf
import numpy as np

from munch import DefaultMunch
from omegaconf import OmegaConf
from omegaconf import DictConfig

logger = tf.get_logger()
logger.setLevel(logging.ERROR)

warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Set seeds
def setup_seed(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)  # tf cpu fix seed

def get_config(cfg):
    config_dict = OmegaConf.to_container(cfg)
    configs = DefaultMunch.fromDict(config_dict)
    return configs

@hydra.main(version_base=None, config_path="", config_name="user_config_quant")
def main(cfg: DictConfig) -> None:

    def representative_data_gen():
        if cfg.quantization.fake is True:
            for _ in tqdm.tqdm(range(5)):
                data = np.random.rand(1, cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2])
                yield [data.astype(np.float32)]
        else:
            representative_ds_path = cfg.quantization.calib_dataset_path
            list_of_files = os.listdir(representative_ds_path)

            for image_file in tqdm.tqdm(list_of_files):
                if image_file.endswith(".jpg"):
                    image = cv2.imread(os.path.join(representative_ds_path, image_file))
                    if len(image.shape) != 3:
                        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    resized_image = cv2.resize(image, (int(cfg.model.input_shape[0]), int(cfg.model.input_shape[1])), interpolation=cv2.INTER_LINEAR)
                    image_data = resized_image/cfg.pre_processing.rescaling.scale + cfg.pre_processing.rescaling.offset
                    img = image_data.astype(np.float32)
                    image_processed = np.expand_dims(img, 0)
                    yield [image_processed]
                    
    # Initilize configuration
    configs = get_config(cfg)

    # Set all seeds
    setup_seed(42)
    
    name = cfg.model.name
    print(f'Quantization of {name}')
    uc = cfg.model.uc
    if cfg.quantization.fake == True:
        uc = 'fake'
    quant_tag = 'quant_pc'
    input_tag = 'f'
    output_tag = 'f'
    
    converter = tf.lite.TFLiteConverter.from_saved_model(cfg.model.model_path)
    
    tflite_models_dir = pathlib.Path(cfg.quantization.export_path)
    tflite_models_dir.mkdir(exist_ok=True, parents=True)

    # Quantize the model
    if cfg.quantization.quantization_input_type == 'int8':
        converter.inference_input_type = tf.int8
        input_tag = 'i'
    elif cfg.quantization.quantization_input_type == 'uint8':
        converter.inference_input_type = tf.uint8
        input_tag = 'u'
    else:
        pass
        
    if cfg.quantization.quantization_output_type == 'int8':
        converter.inference_output_type = tf.int8
        output_tag = 'i'
    elif cfg.quantization.quantization_output_type == 'uint8':
        converter.inference_output_type = tf.uint8
        output_tag = 'u'
    else:
        pass

    if cfg.quantization.quantization_type == 'per_tensor':
        converter._experimental_disable_per_channel = True
        quant_tag = 'quant_pt'
    
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen

    # Save the unquantized/float model:
    tflite_model_quantio = converter.convert()
    tflite_model_quantio_file = tflite_models_dir/f'{name}_{quant_tag}_{input_tag}{output_tag}_{uc}.tflite'
    tflite_model_quantio_file.write_bytes(tflite_model_quantio)
    
    print(f'Quantized model generated: {name}_{quant_tag}_{input_tag}{output_tag}_{uc}.tflite')

if __name__ == "__main__":

    main()
