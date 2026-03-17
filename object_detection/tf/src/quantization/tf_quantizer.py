#  *---------------------------------------------------------------------------------------------*/
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

# Import necessary libraries
import pathlib
import numpy as np
import tensorflow as tf
import tqdm
import os
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig

# Import utility functions and modules
from common.optimization import model_formatting_ptq_per_tensor

class TFLitePTQQuantizer:
    """
    A class to handle TensorFlow Lite Post-Training Quantization (PTQ).

    Args:
        cfg (DictConfig): Configuration object for quantization.
        model (tf.keras.Model): The TensorFlow model to quantize.
        dataloaders (dict): Dictionary containing datasets for quantization and testing.
    """
    def __init__(self, cfg: DictConfig = None, model: object = None, 
                 dataloaders: dict = None):
        self.cfg = cfg
        self.model = model
        self.quantization_ds = dataloaders['quantization']
        self.output_dir = HydraConfig.get().runtime.output_dir
        self.export_dir = cfg.quantization.export_dir
        self.quantized_model = None

    def _representative_data_gen(self, input_shape):
        """
        Generates representative data for quantization.

        Args:
            input_shape (tuple): Shape of the model input.

        Yields:
            List[np.ndarray]: Representative data samples.
        """
        # Get the scale and the offset parameters:
        scale  = self.cfg.preprocessing.rescaling.scale
        offset = self.cfg.preprocessing.rescaling.offset
        if not self.quantization_ds:
            # If no dataset is provided, generate random data
            print("[WARNING] No representative images were provided. Quantization will be performed using fake data.")
            for _ in tqdm.tqdm(range(5)):
                image = tf.random.uniform((1,) + input_shape, minval=0, maxval=256, dtype=tf.int32)
                image = tf.cast(image, tf.float32)
                image = scale * image + offset
                yield [image]
        else:
            # Use the provided dataset for representative data
            for images,_ in tqdm.tqdm(self.quantization_ds, total=len(self.quantization_ds)):
                for image in images:
                    image = tf.cast(image, dtype=tf.float32)
                    image = tf.expand_dims(image, 0) # Add batch dimension
                    yield [image]

    def _run_quantization(self):
        """
        Runs the quantization process and saves the quantized model.
        """
        
        # Get the input shape of the model
        input_shape = tuple(self.model.input.shape[1:])
        # Create a TFLite converter from the Keras model
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)

        # Set input and output quantization types
        q_input = self.cfg.quantization.quantization_input_type
        q_output = self.cfg.quantization.quantization_output_type
        if q_input == 'int8':
            converter.inference_input_type = tf.int8
        elif q_input == 'uint8':
            converter.inference_input_type = tf.uint8
        if q_output == 'int8':
            converter.inference_output_type = tf.int8
        elif q_output == 'uint8':
            converter.inference_output_type = tf.uint8

        # Enable default optimizations and set the representative dataset
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = lambda: self._representative_data_gen(input_shape)

        # Set quantization granularity (per-tensor or per-channel)
        if self.cfg.quantization.granularity == 'per_tensor':
            converter._experimental_disable_per_channel = True

        # Convert the model to TFLite format
        tflite_model_quantized = converter.convert()

        # Save the quantized model to the specified directory
        tflite_models_dir = pathlib.Path(os.path.join(self.output_dir, f"{self.export_dir}/"))
        tflite_models_dir.mkdir(exist_ok=True, parents=True)
        tflite_model_path = tflite_models_dir / "quantized_model.tflite"
        tflite_model_path.write_bytes(tflite_model_quantized)

        # Load the quantized model as a TFLite Interpreter
        interpreter = tf.lite.Interpreter(model_path=str(tflite_model_path))
        interpreter.allocate_tensors()
        setattr(interpreter, 'model_path', str(tflite_model_path)) # Add model path as an attribute
        self.quantized_model = interpreter

    def _prepare_quantization(self):
        """
        Prepares the model for quantization by applying optimizations if necessary.
        """
        # Ensure the model is a TensorFlow Keras model
        if not isinstance(self.model, tf.keras.Model):
            raise ValueError(f"Unsupported model format: {type(self.model)}. ")
        
        quantization_granularity = self.cfg.quantization.granularity
        quantization_optimize = self.cfg.quantization.optimize
        print(f'[INFO] : Quantization granularity : {quantization_granularity}')
        
        # Apply optimizations for per-tensor quantization if specified
        if quantization_granularity == 'per_tensor' and quantization_optimize:
            print("[INFO] : Optimizing the model for improved per_tensor quantization...")
            self.model = model_formatting_ptq_per_tensor(model_origin=self.model)
            models_dir = pathlib.Path(os.path.join(self.output_dir, f"{self.export_dir}/"))
            models_dir.mkdir(exist_ok=True, parents=True)
            model_path = models_dir / "optimized_model.keras"
            self.model.save(model_path)

    def quantize(self):
        """
        Executes the quantization process.

        Returns:
            tf.lite.Interpreter: The quantized TFLite model as an Interpreter object.
        """
        print("[INFO] : Quantizing the model ... This might take few minutes ...")
        self._prepare_quantization()  # Prepare the model for quantization
        self._run_quantization()      # Run the quantization process
        print('[INFO] : Quantization complete.')
        return self.quantized_model   # Return the quantized model

