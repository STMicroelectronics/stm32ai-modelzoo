# /*---------------------------------------------------------------------------------------------keras
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
from shutil import rmtree
from pathlib import Path
from tabulate import tabulate
from timeit import default_timer as timer
from datetime import timedelta
import tqdm
import onnx
import onnxruntime

import mlflow
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List, Optional

from models_utils import get_model_name_and_its_input_shape
from preprocess import load_and_preprocess_image
from postprocess import postprocess_predictions, corners_to_center_box_coords
from object_det_metrics.lib.BoundingBox import BoundingBox
from object_det_metrics.lib.BoundingBoxes import BoundingBoxes
from object_det_metrics.lib.Evaluator import Evaluator
from object_det_metrics.lib.utils import BBFormat, BBType, CoordinatesType
from metrics_utils import check, calculate_map
from logs_utils import log_to_file


def get_ground_truth_boxes(example_path, image_size=None, bounding_boxes=None):
    """
    Parse the *.txt file corresponding to an image file to get the ground truth
    boxes of the images. Then, add them to the set of bounding boxes of all 
    the images.
    The argument example_path is the path to the image path without the file
    extension. It is used as a unique ID to associate images and bounding boxes.
    """

    with open(Path(example_path + ".txt"), "r") as fh1:
        # Loop through each line in the text file
        for line in fh1:
            line = line.rstrip("\n")
            if not line.replace(' ', ''):
                continue
            # Split the line by spaces to get the class ID and bounding box coordinates
            split_line = line.split()

            # Create a BoundingBox object with the class ID and bounding box coordinates
            class_id, x, y, w, h = [float(check(split_line[i])) if i > 0 else int(split_line[i]) + 1 for i in range(5)]
            bb = BoundingBox(example_path,
                             class_id, x, y, w, h,
                             CoordinatesType.Relative,
                             image_size,
                             BBType.GroundTruth,
                             format=BBFormat.XYWH)
            bounding_boxes.addBoundingBox(bb)


def get_detection_boxes(predictions, example_path=None, image_size= None, bounding_boxes=None):
    """
    Extract the bounding boxes from the detections obtained for a given image. 
    Convert the coordinates of the boxes from (x_min,x_max, y_min, y_max)
    coordinates to (x_center, y_center, w, h) coordinates. Then, add the boxes
    to the set of bounding boxes of all the images.
    The argument example_path is the path to the image path without the file
    extension. It is used as a unique ID to associate images and bounding boxes.
    """
        
    for predicted_class, detection_boxes in predictions.items():
        for bbox in detection_boxes:
            score, xmi, ymi, xma, yma = bbox
            x, y, w, h = corners_to_center_box_coords(xmi, xma, ymi, yma, image_size=image_size, relative=True)

            bb = BoundingBox(example_path,
                             int(predicted_class),
                             check(x), check(y), check(w), check(h),
                             CoordinatesType.Relative,
                             image_size,
                             BBType.Detected,
                             check(score),
                             format=BBFormat.XYWH)
            bounding_boxes.addBoundingBox(bb)


def plot_precision_versus_recall(metrics_data, class_names, output_dir, input_shape, model_path_suffix):
    """
    Plot the precision versus recall curves. AP values are the areas under these curves.
    """
    # Create the directory where plots will be saved
    if model_path_suffix == '.h5':
        figs_dir = os.path.join(output_dir, f"float_model_ap_{input_shape[0]}")
    elif model_path_suffix == '.tflite':
        figs_dir = os.path.join(output_dir, f"quantized_model_ap_{input_shape[0]}")
    elif model_path_suffix == '.onnx':
        figs_dir = os.path.join(output_dir, f"onnx_model_ap_{input_shape[1]}")
    else:
        figs_dir = os.path.join(output_dir, f"model_ap_{input_shape[0]}")
    if os.path.exists(figs_dir):
        rmtree(figs_dir)
    os.mkdir(figs_dir)

    for class_metrics in metrics_data:
        # Get the name of the class
        class_name = class_names[class_metrics["class"]]

        # Plot the precision versus recall curve
        figure = plt.figure(figsize=(10, 10))
        plt.xlabel("recall")
        plt.ylabel("precision")
        plt.title("Precision versus recall curve for class {}, class AP = {:.2f}".format(
            class_name, float(class_metrics["AP"]) * 100))
        plt.plot(class_metrics["recall"], class_metrics["precision"])
        plt.grid()

        # Save the plot in the plots directory
        plt.savefig(f"{figs_dir}/{class_name}_AP.png")
        plt.close(figure)


def calculate_float_map(model: tf.keras.Model = None,
                        image_file_paths: List[str] = None,
                        input_shape: tuple = None,
                        scale: float = None,
                        offset: float = None,
                        interpolation: str = None,
                        color_mode: str = None,
                        nms_thresh: float = 0.5,
                        confidence_thresh: float = 0.5,
                        iou_threshold: float = 0.5):
    """
    Calculates the AP per class and mAP for a given float model and set of image files.

    Args:
        model (tf.keras.Model): The Keras model to evaluate.
        image_file_paths (str): Paths to the images files of the dataset.
        input_shape (tuple): Input shape of the model.
        scale (float): Image rescaling scale.
        offset (float): Image rescaling offset.
        interpolation (str): Interpolation method to use for resizing images.
        color_mode (str): Color mode ('grayscale', 'rgb' or 'rgba').
        nms_thresh (float, optional): Threshold for non-maximum suppression. Defaults to 0.5.
        confidence_thresh (float, optional): confidence threshold for filtering detections. Defaults to 0.5.
        iou_threshold (float, optional): IoU threshold for AP evaluation. Defaults to 0.5.

    Returns:
        A list of dictionaries:
            There is one dictionary for each class with the following keys:
            ['class', 'precision', 'recall', 'AP', 'interpolated precision', 'interpolated recall', 
             'total positives', 'total TP', 'total FP']
    """
    
    image_size = input_shape[:2]

    # Ground truth and detection boxes for all images
    bounding_boxes = BoundingBoxes()

    for img_path in tqdm.tqdm(image_file_paths):

        # The path to the image file path without the extension is used 
        # to associate an image with its ground truth and detection boxes
        example_path = os.path.splitext(img_path)[0]

        # Read, resize and rescale the image
        image = load_and_preprocess_image(
                            image_file_path=img_path,
                            image_size=image_size,
                            scale=scale,
                            offset=offset,
                            interpolation=interpolation,
                            color_mode=color_mode)
        image = np.expand_dims(image, axis=0)

        # Make predictions for the current image
        raw_predictions = model.predict_on_batch(image)

        predictions = postprocess_predictions(
                                raw_predictions,
                                image_size=image_size,
                                nms_thresh=nms_thresh,
                                confidence_thresh=confidence_thresh)

        # Add ground boxes and detection boxes to the set of bounding boxes
        get_ground_truth_boxes(example_path, image_size=image_size,
                               bounding_boxes=bounding_boxes)
        get_detection_boxes(predictions, example_path=example_path, image_size=image_size,
                            bounding_boxes=bounding_boxes)

    # Calculate the mAP
    evaluator = Evaluator()
    metrics_data = evaluator.GetPascalVOCMetrics(bounding_boxes, IOUThreshold=iou_threshold)

    return metrics_data


def calculate_quantized_map(model_path: str = None,
                            image_file_paths: List[str] = None,
                            input_shape: tuple = None,
                            scale: float = None,
                            offset: float = None,
                            interpolation: str = None,
                            color_mode: str = None,
                            nms_thresh: float = 0.5,
                            confidence_thresh: float = 0.5,
                            iou_threshold: float = 0.5,
                            num_threads: Optional[int] = 1):
    """
    Calculates the AP per class and mAP for a given quantize model and set of image files.

    Args:
        model_path (str): Path to the TFlite model file.
        image_file_paths (List[str]): Paths to the image files of the dataset.
        input_shape (tuple): Input shape of the model.
        scale (float): Image rescaling scale.
        offset (float): Image rescaling offset.
        interpolation (str): Interpolation method to use for resizing images.
        color_mode (str): Color mode ('graysacle', 'rgb' or 'rgba').
        nms_thresh (float, optional): Threshold for non-maximum suppression. Defaults to 0.5.
        confidence_thresh (float, optional): confidence threshold for filtering detections. Defaults to 0.5.
        iou_threshold (float, optional): IoU threshold for AP evaluation. Defaults to 0.5.
        num_threads (int): number of threads for tflite interpreter

    Returns:
        A list of dictionaries:
            There is one dictionary for each class with the following keys:
            ['class', 'precision', 'recall', 'AP', 'interpolated precision', 'interpolated recall', 
             'total positives', 'total TP', 'total FP']
    """

    image_size = input_shape[:2]

    # All ground truth and detection boxes
    bounding_boxes = BoundingBoxes()

    interpreter = tf.lite.Interpreter(model_path, num_threads=num_threads)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    input_index = interpreter.get_input_details()[0]["index"]
    output_index = interpreter.get_output_details()

    for img_path in tqdm.tqdm(image_file_paths):
        # The path to the image file without the extension is used 
        # to associate an image with its ground truth and detection boxes
        example_path = os.path.splitext(img_path)[0]

        # Read, resize and rescale the image
        image = load_and_preprocess_image(
                        image_file_path=img_path,
                        image_size=image_size,
                        scale=scale,
                        offset=offset,
                        interpolation=interpolation,
                        color_mode=color_mode)
        image = np.expand_dims(image, axis=0)

        # 8-bit quantization approximates floating point values
        # using the following formula:
        #     float_value = (int8_value - zero_points) * scale
        # so to get the int8 values:
        #     int8_value = float_value/scale + zero_points
        tf_scale = input_details['quantization'][0]
        tf_zero_points = input_details['quantization'][1]
        image = np.round(image / tf_scale + tf_zero_points)

        # Convert the image data type to the model input data type
        # and clip to the min/max values of this data type
        input_dtype = input_details['dtype']
        image = image.astype(dtype=input_dtype)
        image = np.clip(image, np.iinfo(input_dtype).min, np.iinfo(input_dtype).max)                 

        # Make a prediction for the image to get detection boxes
        interpreter.set_tensor(input_index, image)
        interpreter.invoke()

        predicted_scores = interpreter.get_tensor(output_index[0]["index"])
        predicted_boxes = interpreter.get_tensor(output_index[1]["index"])
        predicted_anchors = interpreter.get_tensor(output_index[2]["index"])

        raw_predictions = [predicted_scores, predicted_boxes, predicted_anchors]
        predictions = postprocess_predictions(
                                raw_predictions,
                                image_size=image_size,
                                nms_thresh=nms_thresh,
                                confidence_thresh=confidence_thresh)

        # Add the ground boxes and detection boxes to the set of detection boxes
        get_ground_truth_boxes(example_path, image_size=image_size, bounding_boxes=bounding_boxes)
        get_detection_boxes(predictions, example_path=example_path, image_size=image_size, bounding_boxes=bounding_boxes)

    evaluator = Evaluator()
    metrics_data = evaluator.GetPascalVOCMetrics(bounding_boxes, IOUThreshold=float(iou_threshold))

    return metrics_data




def calculate_model_map(model_path: str = None,
                        image_file_paths: List[str] = None,
                        input_shape: tuple = None,
                        scale: float = None,
                        offset: float = None,
                        interpolation: str = None,
                        color_mode: str = None,
                        nms_thresh: float = 0.5,
                        confidence_thresh: float = 0.5,
                        iou_threshold: float = 0.5,
                        num_threads: Optional[int] = 1):
    """
    Calculates the AP per class and mAP for a given model and set of image files.

    Args:
        model_path (str): Path to the model file.
        image_file_paths (List[str]): Paths to the image files of the dataset.
        input_shape (tuple): Input shape of the model.
        scale (float): Image rescaling scale.
        offset (float): Image rescaling offset.
        interpolation (str): Interpolation method to use for resizing images.
        color_mode (str): Color mode ('graysacle', 'rgb' or 'rgba').
        nms_thresh (float, optional): Threshold for non-maximum suppression. Defaults to 0.5.
        confidence_thresh (float, optional): confidence threshold for filtering detections. Defaults to 0.5.
        iou_threshold (float, optional): IoU threshold for AP evaluation. Defaults to 0.5.

    Returns:
        A list of dictionaries:
            There is one dictionary for each class with the following keys:
            ['class', 'precision', 'recall', 'AP', 'interpolated precision', 'interpolated recall', 
             'total positives', 'total TP', 'total FP']
    """

    image_size = input_shape[:2]
    try:
        file_extension = Path(model_path).suffix
    except Exception:
        raise ValueError(f"Model accuracy evaluation failed\nReceived model path: {model_path}")

    # All ground truth and detection boxes
    bounding_boxes = BoundingBoxes()

    if file_extension == '.tflite':
        image_size = input_shape[:2]
        interpreter = tf.lite.Interpreter(model_path, num_threads=num_threads)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()[0]
        input_index = interpreter.get_input_details()[0]["index"]
        output_index = interpreter.get_output_details()

    elif file_extension == '.onnx':
        image_size = input_shape[1:]
        sess = onnxruntime.InferenceSession(model_path)
        inputs  = sess.get_inputs()
        outputs = sess.get_outputs()

    elif file_extension == '.h5':
        image_size = input_shape[:2]
        model = tf.keras.models.load_model(model_path,compile=False)


    for img_path in tqdm.tqdm(image_file_paths):
        # The path to the image file without the extension is used 
        # to associate an image with its ground truth and detection boxes
        example_path = os.path.splitext(img_path)[0]

        # Read, resize and rescale the image
        image = load_and_preprocess_image(
                        image_file_path=img_path,
                        image_size=image_size,
                        scale=scale,
                        offset=offset,
                        interpolation=interpolation,
                        color_mode=color_mode)
        image = np.expand_dims(image, axis=0)

        if file_extension == '.tflite':
            # 8-bit quantization approximates floating point values
            # using the following formula:
            #     float_value = (int8_value - zero_points) * scale
            # so to get the int8 values:
            #     int8_value = float_value/scale + zero_points
            tf_scale = input_details['quantization'][0]
            tf_zero_points = input_details['quantization'][1]
            image = np.round(image / tf_scale + tf_zero_points)

            # Convert the image data type to the model input data type
            # and clip to the min/max values of this data type
            input_dtype = input_details['dtype']
            image = image.astype(dtype=input_dtype)
            image = np.clip(image, np.iinfo(input_dtype).min, np.iinfo(input_dtype).max)

            # Make a prediction for the image to get detection boxes
            interpreter.set_tensor(input_index, image)
            interpreter.invoke()

            predicted_scores = interpreter.get_tensor(output_index[0]["index"])
            predicted_boxes = interpreter.get_tensor(output_index[1]["index"])
            predicted_anchors = interpreter.get_tensor(output_index[2]["index"])

            raw_predictions = [predicted_scores, predicted_boxes, predicted_anchors]

        elif file_extension == '.onnx': # if onnx -> the inputs/outputs are channel first

            image = np.transpose(image,[0,3,1,2])
            raw_predictions = sess.run([o.name for o in outputs], {inputs[0].name: image})

        elif file_extension == '.h5':

            raw_predictions = model.predict_on_batch(image)

        predictions = postprocess_predictions(
                                raw_predictions,
                                image_size=image_size,
                                nms_thresh=nms_thresh,
                                confidence_thresh=confidence_thresh)

        # Add the ground boxes and detection boxes to the set of detection boxes
        get_ground_truth_boxes(example_path, image_size=image_size, bounding_boxes=bounding_boxes)
        get_detection_boxes(predictions, example_path=example_path, image_size=image_size, bounding_boxes=bounding_boxes)

    evaluator = Evaluator()
    metrics_data = evaluator.GetPascalVOCMetrics(bounding_boxes, IOUThreshold=float(iou_threshold))

    return metrics_data



def evaluate(cfg: DictConfig = None,
             valid_ds: Dict = None, test_ds: Dict = None,
             model_path: str = None) -> None:
    """
    Evaluates the AP of each class and mAP for a Keras model (float)
    or a TFlite model (quantized)

    If there is no test dataset, the validation dataset is used instead.

    Args:
        cfg (config): The configuration file.
        valid_ds (Dict): validation dataset (dictionary containing the paths to the image files).
        test_ds (Dict): test dataset (dictionary containing the paths to the image files).
        model_path (str, optional): path to the model file to evaluate.

    Returns:
        map (float): Average AP over all classes.
    """

    # Start runtime timer
    start_time = timer()

    if test_ds:
        used_dataset = "test"
        image_file_paths = test_ds['test_images_filename_ds']
    else:
        used_dataset = "validation"
        image_file_paths = valid_ds['val_images_filename_ds']

    model_path = model_path if model_path else cfg.general.model_path
    _, input_shape = get_model_name_and_its_input_shape(model_path)

    pre = cfg.preprocessing
    post = cfg.postprocessing

    print(f"[INFO] : Calculating mAP using the {used_dataset} set")

    metrics_data = calculate_model_map(model_path=model_path,
                      image_file_paths=image_file_paths,
                      input_shape=input_shape,
                      scale=pre.rescaling.scale,
                      offset=pre.rescaling.offset,
                      interpolation=pre.resizing.interpolation,
                      color_mode=pre.color_mode,
                      nms_thresh=post.NMS_thresh,
                      confidence_thresh=post.confidence_thresh,
                      iou_threshold=post.IoU_eval_thresh,
                      num_threads=cfg.general.num_threads_tflite)

    # if Path(model_path).suffix == '.h5':
    #     model = tf.keras.models.load_model(model_path,
    #                                        compile=False)
    #     print(f"[INFO] Calculating mAP of float model using the {used_dataset} set")
    #     metrics_data = calculate_float_map(model=model,
    #                               image_file_paths=image_file_paths,
    #                               input_shape=input_shape,
    #                               scale=pre.rescaling.scale,
    #                               offset=pre.rescaling.offset,
    #                               interpolation=pre.resizing.interpolation,
    #                               color_mode=pre.color_mode,
    #                               nms_thresh=post.NMS_thresh,
    #                               confidence_thresh=post.confidence_thresh,
    #                               iou_threshold=post.IoU_eval_thresh)

    # elif Path(model_path).suffix == '.tflite':
    #     print(f"[INFO] Calculating mAP of quantized model using the {used_dataset} set")
    #     metrics_data = calculate_quantized_map(model_path=model_path,
    #                                   image_file_paths=image_file_paths,
    #                                   input_shape=input_shape,
    #                                   scale=pre.rescaling.scale,
    #                                   offset=pre.rescaling.offset,
    #                                   interpolation=pre.resizing.interpolation,
    #                                   color_mode=pre.color_mode,
    #                                   nms_thresh=post.NMS_thresh,
    #                                   confidence_thresh=post.confidence_thresh,
    #                                   iou_threshold=post.IoU_eval_thresh)

    # else:
    #     raise RuntimeError("Internal error: unsupported model file extension")

    # Get the AP results from the evaluator output and calculate the mAP
    class_names = ["background"] + cfg.dataset.class_names    
    ap_classes_names = [class_names[cm["class"]] for cm in metrics_data]
    ap_classes = [float(cm["AP"]) for cm in metrics_data]
    map = calculate_map(ap_classes=ap_classes, ap_classes_names=ap_classes_names)

    # Display AP per class and mAP
    table = [[ap_classes_names[i], ap_classes[i]*100] for i in range(len(ap_classes_names))]
    print(tabulate(table, headers=["Class", "AP %"]))

    if Path(model_path).suffix == '.h5':
        print("Float model average AP over classes (mAP): {:.2f}".format(map))
        mlflow.log_metric("float_model_mAP", map)
        # logging the mAP in the stm32ai_main.log file
        log_to_file(HydraConfig.get().runtime.output_dir,  f"Float model {used_dataset} dataset:")
        log_to_file(HydraConfig.get().runtime.output_dir, f"float_model_mAP : {map}")
    else:
        print("Quantized model average AP over classes (mAP): {:.2f}".format(map))
        mlflow.log_metric("int_model_mAP", map)# logging the mAP in the stm32ai_main.log file
        log_to_file(HydraConfig.get().runtime.output_dir,  f"Quantized model {used_dataset} dataset:")
        log_to_file(HydraConfig.get().runtime.output_dir, f"Quantized_model_mAP : {map}")

    end_time = timer()

    if cfg.postprocessing.plot_metrics:
        print("Plotting precision versus recall curves")
        output_dir = HydraConfig.get().runtime.output_dir
        model_path_suffix = Path(model_path).suffix
        plot_precision_versus_recall(metrics_data, class_names, output_dir, input_shape, model_path_suffix)

    run_time = int(end_time - start_time)
    print("Evaluation runtime:", str(timedelta(seconds=run_time)))

    return map
