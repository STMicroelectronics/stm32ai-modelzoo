# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from pathlib import Path
from omegaconf import DictConfig
from tabulate import tabulate
import numpy as np
import tensorflow as tf

import warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../preprocessing'))
from models_mgt import get_model_name_and_its_input_shape
from preprocess import preprocess_input


def predict(cfg: DictConfig = None) -> None:
    """
    Predicts a class for all the images that are inside a given directory.
    The model used for the predictions can be either a .h5 or .tflite file.

    Args:
        cfg (dict): A dictionary containing the entire configuration file.

    Returns:
        None
    
    Errors:
        The directory containing the images cannot be found.
        The directory does not contain any file.
        An image file can't be loaded.
    """
    
    model_path = cfg.general.model_path
    class_names = cfg.dataset.class_names
    test_images_dir = cfg.prediction.test_images_path
    cpp = cfg.preprocessing
    
    _, model_input_shape = get_model_name_and_its_input_shape(model_path)
    
    print("[INFO] Making predictions using:")
    print("  model:", model_path)
    print("  images directory:", test_images_dir)

    # Load the test images
    image_filenames = []
    images = []
    channels = 1 if cpp.color_mode == "grayscale" else 3
    for fn in os.listdir(test_images_dir):
        im_path = os.path.join(test_images_dir, fn)
        # Skip subdirectories if any
        if os.path.isdir(im_path): continue
        image_filenames.append(fn)
        # Load the image
        try:
            data = tf.io.read_file(im_path)
            img = tf.image.decode_image(data, channels=channels)
        except:
            raise ValueError(f"\nUnable to load image file {im_path}\n"
                             "Supported image file formats are BMP, GIF, JPEG and PNG.")
        # Resize the image            
        width, height = model_input_shape[0:2]
        if cpp.resizing.aspect_ratio == "fit":
            img = tf.image.resize(img, [height, width], method=cpp.resizing.interpolation, preserve_aspect_ratio=False)
        else:
            img = tf.image.resize_with_crop_or_pad(img, height, width)

        # Rescale the image
        img = cpp.rescaling.scale * tf.cast(img, tf.float32) + cpp.rescaling.offset     
        images.append(img)

    if not images:
        raise ValueError("Unable to make predictions, could not find any image file in the "
                         f"images directory.\nReceived directory path {test_images_dir}")

    results_table = []
    file_extension = Path(model_path).suffix
    if file_extension == ".h5":
        # Load the .h5 model
        model = tf.keras.models.load_model(model_path)

        for i in range(len(images)):
            img = tf.expand_dims(images[i], 0)
            scores = model.predict(img)

            # Find the label with the highest score
            scores = np.squeeze(scores)
            max_score_index = np.argmax(scores)
            prediction_score = 100 * scores[max_score_index]
            predicted_label = class_names[max_score_index]

            # Add result to the table
            results_table.append([predicted_label, "{:.1f}".format(prediction_score), image_filenames[i]])

    elif file_extension == ".tflite":
        # Load the Tflite model and allocate tensors
        interpreter_quant = tf.lite.Interpreter(model_path=model_path)
        interpreter_quant.allocate_tensors()
        input_details = interpreter_quant.get_input_details()[0]
        input_index_quant = input_details["index"]
        output_index_quant = interpreter_quant.get_output_details()[0]["index"]

        for i in range(len(images)):
            image_processed = preprocess_input(images[i], input_details)
            interpreter_quant.set_tensor(input_index_quant, image_processed)
            interpreter_quant.invoke()
            scores = interpreter_quant.get_tensor(output_index_quant)

            # Find the label with the highest score
            scores = np.squeeze(scores)
            max_score_index = np.argmax(scores)
            prediction_score = 100 * scores[max_score_index]
            predicted_label = class_names[max_score_index]

            # Add result to the table
            results_table.append([predicted_label, "{:.1f}".format(prediction_score), image_filenames[i]])

    else:
        raise TypeError(f"Unknown or unsupported model type. Received path {model_path}")

    # Display the results table
    print(tabulate(results_table, headers=["Prediction", "Score", "Image file"]))
