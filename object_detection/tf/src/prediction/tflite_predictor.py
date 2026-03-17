# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

# Import necessary libraries
import os
import sys
from pathlib import Path
from omegaconf import DictConfig
from tabulate import tabulate
import numpy as np
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt
from hydra.core.hydra_config import HydraConfig

# Suppress warnings and TensorFlow logs for cleaner output
import warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import utility functions for AI runner and ONNX prediction
from common.utils import ai_runner_interp, ai_interp_input_quant, ai_interp_outputs_dequant
from common.data_augmentation import remap_pixel_values_range
from object_detection.tf.src.postprocessing  import get_nmsed_detections
from object_detection.tf.src.utils import ai_runner_invoke, bbox_normalized_to_abs_coords, plot_bounding_boxes
from object_detection.tf.src.models import model_family


class TFLiteQuantizedModelPredictor:
    """
    A class to handle predictions using a TFLite quantized model. This class includes methods for:
    - Loading and preprocessing images
    - Running inference on the TFLite model
    - Annotating and saving prediction results
    - Displaying results in a tabular format
    """
    def __init__(self, cfg, model, dataloaders):
        """
        Initialize the predictor with configuration, model, and dataloaders.

        Args:
            cfg: Configuration object containing settings for the predictor.
            model: The TFLite model to use for predictions.
            dataloaders: A dictionary containing the prediction dataset.
        """
        self.cfg = cfg
        self.model = model
        self.predict_ds = dataloaders['predict']
        self.class_names = cfg.dataset.class_names
        self.prediction_result_dir = os.path.join(cfg.output_dir, 'predictions')
        os.makedirs(self.prediction_result_dir, exist_ok=True)
        self.results_table = []
        self.target = getattr(cfg.prediction, 'target', 'host') if hasattr(cfg, 'prediction') else 'host'
        self.model_name = os.path.basename(model.model_path)
        self.display_figures = cfg.general.display_figures

        # Initialize the TFLite interpreter for the quantized model
        self.interpreter_quant = tf.lite.Interpreter(model_path=model.model_path)
        self.interpreter_quant.allocate_tensors()
        self.input_details = self.interpreter_quant.get_input_details()[0]
        self.input_index_quant = self.input_details["index"]
        self.output_details = self.interpreter_quant.get_output_details()[0]
        self.output_index_quant = self.output_details["index"]

        # Initialize the AI runner interpreter for edge devices
        self.ai_runner_interpreter = ai_runner_interp(self.target, self.model_name)

    def _view_image_and_boxes(self, image, img_path, boxes=None, classes=None, scores=None, class_names=None):
        """
        Display image and bounding boxes, optionally cropping and saving detected regions.

        Args:
            cfg: Configuration object.
            image: Image array.
            img_path: Path to the image file.
            boxes: Bounding boxes.
            classes: Class indices.
            scores: Detection scores.
            class_names: List of class names.
        """
        # Convert TF tensors to numpy
        image = np.array(image, dtype=np.float32)
        boxes = np.array(boxes, dtype=np.int32)
        classes = np.array(classes, dtype=np.int32)

        file_name_with_extension = os.path.basename(img_path.numpy().decode('utf-8'))
        file_name, _ = os.path.splitext(file_name_with_extension)
        output_dir = "{}/{}".format(HydraConfig.get().runtime.output_dir,"predictions")
        os.makedirs(output_dir, exist_ok=True)

        # Calculate dimensions for the displayed image
        image_width, image_height = np.shape(image)[:2]
        display_size = 7
        if image_width >= image_height:
            x_size = display_size
            y_size = round((image_width / image_height) * display_size)
        else:
            x_size = round((image_height / image_width) * display_size)
            y_size = display_size

        # Display the image and the bounding boxes
        fig, ax = plt.subplots(figsize=(x_size, y_size))
        if self.cfg.preprocessing.color_mode.lower() == 'bgr':
            image = image[...,::-1]
        ax.imshow(image)
        plot_bounding_boxes(ax, boxes, classes, scores, class_names)
        # turning off the grid
        plt.grid(visible=False)
        plt.axis('off')
        plt.savefig('{}/{}_predict.jpg'.format(output_dir,file_name))
        if self.cfg.general.display_figures:
            plt.show()
        plt.close()
        # Crop and save predicted boxes
        if model_family(self.cfg.model.model_type) in ["face_detect_front"]:
            self._crop_and_save(img_path, image, boxes, file_name, output_dir, stretch_percents = self.cfg.postprocessing.crop_stretch_percents)

    def _crop_and_save(self, image_path, image_array, boxes, base_filename, output_dir, stretch_percents=None):
        """
        Crop and save images with independent stretching for each coordinate.

        Args:
            image_path: Path to the original image.
            image_array: The resized or processed image array (used for coordinate normalization).
            boxes: List of bounding boxes (xmin, ymin, xmax, ymax) relative to image_array.
            base_filename: Base filename for saving crops.
            output_dir: Directory to save cropped images.
            stretch_percents: List of 4 floats (stretch_xmin%, stretch_ymin%, stretch_xmax%, stretch_ymax%)
                            representing the stretch percentage for each coordinate.
                            If None, defaults to (0, 0, 0, 0) (no stretch).
        """
        if stretch_percents is None:
            stretch_percents = [0, 0, 0, 0]

        original_image = cv2.imread(image_path.numpy().decode('utf-8'))
        if original_image is None:
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        h_array, w_array = image_array.shape[:2]
        h_orig, w_orig = original_image.shape[:2]

        # Create a subfolder for this image inside the output directory
        image_folder = os.path.join(output_dir, base_filename)
        os.makedirs(image_folder, exist_ok=True)

        for i, box in enumerate(boxes):
            xmin, ymin, xmax, ymax = box

            # Normalize coordinates based on image_array size
            xmin_norm = xmin / w_array
            ymin_norm = ymin / h_array
            xmax_norm = xmax / w_array
            ymax_norm = ymax / h_array

            # Scale normalized coordinates to original image size
            xmin_scaled = int(xmin_norm * w_orig)
            ymin_scaled = int(ymin_norm * h_orig)
            xmax_scaled = int(xmax_norm * w_orig)
            ymax_scaled = int(ymax_norm * h_orig)

            # Calculate width and height of the box
            box_width = xmax_scaled - xmin_scaled
            box_height = ymax_scaled - ymin_scaled

            # Unpack stretch percentages for each coordinate
            stretch_xmin_percent, stretch_ymin_percent, stretch_xmax_percent, stretch_ymax_percent = stretch_percents

            # Calculate stretch amounts for each coordinate
            stretch_xmin = int(box_width * (stretch_xmin_percent / 100))
            stretch_ymin = int(box_height * (stretch_ymin_percent / 100))
            stretch_xmax = int(box_width * (stretch_xmax_percent / 100))
            stretch_ymax = int(box_height * (stretch_ymax_percent / 100))

            # Apply stretching by adjusting each coordinate independently
            xmin_stretched = max(0, xmin_scaled - stretch_xmin)
            ymin_stretched = max(0, ymin_scaled - stretch_ymin)
            xmax_stretched = min(w_orig - 1, xmax_scaled + stretch_xmax)
            ymax_stretched = min(h_orig - 1, ymax_scaled + stretch_ymax)

            # Check if coordinates are valid after stretching
            if xmax_stretched <= xmin_stretched or ymax_stretched <= ymin_stretched:
                # Skipping invalid box
                continue

            cropped_bgr = original_image[ymin_stretched:ymax_stretched, xmin_stretched:xmax_stretched]

            if cropped_bgr.size == 0:
                # Skipping empty crop for box
                continue

            # Convert BGR to RGB for displaying with matplotlib
            cropped_rgb = cv2.cvtColor(cropped_bgr, cv2.COLOR_BGR2RGB)

            # Show the cropped image using matplotlib
            if self.cfg.general.display_figures:
                plt.figure(figsize=(4, 4))
                plt.imshow(cropped_rgb)
                plt.title(f"Crop {i}")
                plt.axis('off')
                plt.show()

            # Save the cropped image inside the image-specific folder
            output_filename = os.path.join(image_folder, f"{base_filename}_crop_{i}.jpg")
            cv2.imwrite(output_filename, cropped_bgr)

    def predict(self):
        """
        Run inference using a loaded TFLite Interpreter object.
        """
        input_details = self.interpreter_quant.get_input_details()[0]
        batch_size = 1
        input_shape = tuple(input_details['shape'][1:])
        image_size = input_shape[:2]

        output_details = self.interpreter_quant.get_output_details()

        cpr = self.cfg.preprocessing.rescaling
        pixels_range = (cpr.offset, 255 * cpr.scale + cpr.offset)

        for images, image_paths in self.predict_ds:
            batch_size = tf.shape(images)[0]

            # Allocate input tensor to predict the batch of images
            input_index = input_details['index']
            tensor_shape = (batch_size,) + input_shape
            self.interpreter_quant.resize_tensor_input(input_index, tensor_shape)
            self.interpreter_quant.allocate_tensors()

            input_dtype = input_details['dtype']
            is_float = np.issubdtype(input_dtype, np.floating)

            if is_float:
                predict_images = images
            else:
                # Rescale the image using the model's coefficients
                scale = input_details['quantization'][0]
                zero_points = input_details['quantization'][1]
                predict_images = images / scale + zero_points

            # Convert the image data type to the model input data type
            predict_images = tf.cast(predict_images, input_dtype)
            # and clip to the min/max values of this data type
            if is_float:
                min_val = np.finfo(input_dtype).min
                max_val = np.finfo(input_dtype).max
            else:
                min_val = np.iinfo(input_dtype).min
                max_val = np.iinfo(input_dtype).max

            predict_images = tf.clip_by_value(predict_images, min_val, max_val)

            if self.target == 'host':
                # Predict the images
                self.interpreter_quant.set_tensor(input_index, predict_images)
                self.interpreter_quant.invoke()
            elif self.target in ['stedgeai_host', 'stedgeai_n6', 'stedgeai_h7p']:
                data        = ai_interp_input_quant(self.ai_runner_interpreter,images.numpy(),'.tflite')
                predictions = ai_runner_invoke(data,self.ai_runner_interpreter)
                predictions = ai_interp_outputs_dequant(self.ai_runner_interpreter,predictions)

            if model_family(self.cfg.model.model_type) in ["face_detect_front"]:
                predictions = []
                if self.target == 'host':
                    # face_detect_model_front
                    predictions_r = (self.interpreter_quant.get_tensor(output_details[0]['index']),
                                self.interpreter_quant.get_tensor(output_details[1]['index']),
                                self.interpreter_quant.get_tensor(output_details[2]['index']),
                                self.interpreter_quant.get_tensor(output_details[3]['index']))
                    for i, pred in enumerate(predictions_r):
                        is_float = np.issubdtype(pred.dtype, np.floating)
                        if not is_float:
                            scale, zero_point = output_details[i]['quantization']
                            out_deq = (pred.astype(np.float32) - zero_point) * scale
                            predictions.append(out_deq)
                        else:
                            predictions.append(pred)
            elif model_family(self.cfg.model.model_type) in ["ssd", "st_yoloxn"]:
                if self.target == 'host':
                    # Model outputs are scores, boxes and anchors.
                    predictions = (self.interpreter_quant.get_tensor(output_details[0]['index']),
                                self.interpreter_quant.get_tensor(output_details[1]['index']),
                                self.interpreter_quant.get_tensor(output_details[2]['index']))
            else:
                if self.target == 'host':
                    predictions = self.interpreter_quant.get_tensor(output_details[0]['index'])
                elif self.target in ['stedgeai_host', 'stedgeai_n6', 'stedgeai_h7p']:
                    predictions = predictions[0]

            # The TFLITE version of yolov8 has channel-first outputs
            if model_family(self.cfg.model.model_type) in ["yolov8n"]:
                predictions = tf.transpose(predictions, perm=[0, 2, 1])

            # Decode and NMS the predictions
            boxes, scores, classes = get_nmsed_detections(self.cfg, predictions, image_size)

            # Display images and boxes
            images = remap_pixel_values_range(images, pixels_range, (0, 1))
            boxes = bbox_normalized_to_abs_coords(boxes, image_size=image_size)
            for i in range(batch_size):
                self._view_image_and_boxes(images[i],
                                        image_paths[i],
                                        boxes[i],
                                        classes[i],
                                        scores[i],
                                        class_names=self.cfg.dataset.class_names)