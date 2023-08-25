# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import pathlib
import json
import numpy as np
import tensorflow as tf
from hydra.core.hydra_config import HydraConfig
import tqdm


def TFLite_PTQ_quantizer(cfg, model, train_ds, fake):
	def representative_data_gen():
		if fake:
			fake_data_size = [1] + cfg.model.input_shape
			for _ in tqdm.tqdm(range(5)):
				data = np.random.random_sample(size=(fake_data_size))
				if cfg.model.expand_last_dim:
					data = np.expand_dims(data, axis=-1)
				yield [data.astype(np.float32)]
		else:
			for images, labels in tqdm.tqdm(train_ds, total=len(train_ds)):
				for image in images:
					image = tf.cast(image, dtype=tf.float32)
					image = np.expand_dims(image, axis=0)
					yield [image]

	converter = tf.lite.TFLiteConverter.from_keras_model(model)

	tflite_models_dir = pathlib.Path(os.path.join(HydraConfig.get().runtime.output_dir,"{}/".format(cfg.quantization.export_dir)))
	tflite_models_dir.mkdir(exist_ok=True, parents=True)

	if cfg.quantization.quantization_input_type=='int8':
		converter.inference_input_type = tf.int8
	elif cfg.quantization.quantization_input_type=='uint8':
		converter.inference_input_type = tf.uint8
	else:
		pass

	if cfg.quantization.quantization_output_type=='int8':
		converter.inference_output_type = tf.int8
	elif cfg.quantization.quantization_output_type=='uint8':
		converter.inference_output_type = tf.uint8
	else:
		pass

	converter.optimizations = [tf.lite.Optimize.DEFAULT]
	converter.representative_dataset = representative_data_gen


	tflite_model_quantio = converter.convert()
	tflite_model_quantio_file = tflite_models_dir/"quantized_model.tflite"
	tflite_model_quantio_file.write_bytes(tflite_model_quantio)
