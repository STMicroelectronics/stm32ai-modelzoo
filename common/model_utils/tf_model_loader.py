# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025-2026 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import tensorflow as tf
import onnxruntime

def load_model_from_path(cfg, model_path):
    """
    Loads a model from the given file path.

    Supported formats:
    - Keras (.h5, .keras): Returns a compiled Keras model.
    - TFLite (.tflite): Returns a TensorFlow Lite Interpreter.
    - ONNX (.onnx): Returns an ONNX Runtime InferenceSession.

    Args:
        model_path (str): Path to the model file.

    Returns:
        model object: Loaded model (Keras model, TFLite Interpreter, or ONNX InferenceSession) with 'model_path' and 'input_shape' attributes.

    Raises:
        ValueError: If the file format is not supported.
    """
    file_extension = str(model_path).split('.')[-1]
    model = None
    input_shape = None
    if cfg.training:
        resume_training_from = getattr(cfg.model, 'resume_training_from', None)
    else:
        resume_training_from = None
    if file_extension in ['h5', 'keras']:
        if resume_training_from:
            model = tf.keras.models.load_model(model_path, compile=True)
        else:
            model = tf.keras.models.load_model(model_path, compile=False)
        input_shape = (tuple(model.inputs[0].shape))[1:]
    elif file_extension == 'tflite':
        num_threads = getattr(cfg.general, 'num_threads_tflite', 1)
        model = tf.lite.Interpreter(model_path, num_threads=num_threads)
        model.allocate_tensors()
        input_details = model.get_input_details()
        input_shape = tuple(input_details[0]['shape'])
#        setattr(model, 'input_shape', input_shape)
    elif file_extension == 'onnx':
        model = onnxruntime.InferenceSession(model_path)
        input_shape = tuple(model.get_inputs()[0].shape)
#        setattr(model, 'input_shape', input_shape)
    else:
        raise ValueError(f"Unsupported model file format: {file_extension}. Supported formats are: h5, keras, tflite, onnx.")
    setattr(model, 'model_path', model_path)
    cfg.model.input_shape = input_shape
    return model