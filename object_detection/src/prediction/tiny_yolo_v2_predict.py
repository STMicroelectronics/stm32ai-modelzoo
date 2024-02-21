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
import time
import math
import tqdm
import mlflow
import numpy as np
from pathlib import Path
import matplotlib
import tensorflow as tf
import tensorflow.keras.backend as K
from hydra.core.hydra_config import HydraConfig

sys.path.append(os.path.abspath('./postprocessing'))
from tiny_yolo_v2_postprocess import tiny_yolo_v2_decode, tiny_yolo_v2_nms


def check(va):
    if va in [float('inf'),'inf', float('-inf'),'-inf', "NaN", "nan"] or math.isnan(float(va)) or va != va:
        va = 0
    return va

def load_test_data(directory: str):
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

def float_inference(cfg, best_model):
    """
    Run inference on all images in directory.
    Args:
        cfg (config): The configuration file.
    Returns:
        None
    """        
    class_names = cfg.dataset.class_names
    anchors_list = cfg.postprocessing.yolo_anchors
    anchors = np.array(anchors_list).reshape(-1, 2)
    num_classes = len(class_names)
    input_shape = cfg.training.model.input_shape
    interpolation = cfg.preprocessing.resizing.interpolation
    if interpolation == 'bilinear':
        interpolation_type = cv2.INTER_LINEAR
    elif interpolation == 'nearest':
        interpolation_type = cv2.INTER_NEAREST
    else:
        raise ValueError("Invalid interpolation method. Supported methods are 'bilinear' and 'nearest'.")

    if cfg.dataset.test_path:
        test_set_path = cfg.dataset.test_path
        test_annotations =  load_test_data(test_set_path)
    else:
        print("no test set found")
    for image_file in test_annotations:
        if image_file.endswith(".jpg"):
            image = cv2.imread(os.path.join(test_set_path, image_file))
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape

            img_name = os.path.splitext(image_file)[0]
            resized_image = cv2.resize(image, (int(input_shape[0]), int(input_shape[0])), interpolation=interpolation_type)
            image_data = resized_image * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset
            image_processed = np.expand_dims(image_data, 0)
            predictions = best_model.predict_on_batch(image_processed)
            predictions_tensor = K.constant(predictions)
            predictions_output_shape = K.shape(predictions_tensor)
            input_tensor_shape = K.cast(predictions_output_shape[1:3] * 32, K.dtype(predictions_tensor))
            preds_decoded = tiny_yolo_v2_decode(predictions_tensor, anchors, num_classes, input_tensor_shape, calc_loss=False)
            input_image_shape = [height, width]
            boxes, scores, classes, my_boxes = tiny_yolo_v2_nms(yolo_outputs = preds_decoded,
                                                                image_shape = input_image_shape,
                                                                max_boxes=50,
                                                                score_threshold=float(cfg.postprocessing.confidence_thresh),
                                                                iou_threshold=float(cfg.postprocessing.NMS_thresh),
                                                                classes_ids=list(range(0, num_classes)))
            classes = classes.numpy()
            scores = scores.numpy()
            my_boxes = my_boxes.numpy()
            bbox_thick = int(0.6 * (height + width) / 600)
            for i, c in reversed(list(enumerate(classes))):
                box = my_boxes[i]
                score = scores[i]
                bbox_mess = '{}-{:.2f}'.format(class_names[int(c)],score)
                yyy, xxx, hhh, www = box
                x = xxx*width
                y = yyy*height
                w = www*width
                h = hhh*height
                x1 = int(x-w/2)
                y1 = int(y-h/2)
                x2 = int(x+w/2)
                y2 = int(y+h/2)
                cv2.rectangle(image,(x1,y1), (x2, y2),(0,255,0),2)
                result = "{} {:.2} {:.6} {:.6} {:.6} {:.6}\n".format(int(c),score,xxx,yyy,www,hhh)
                print(result)
                cv2.rectangle(image,(x1,y1), (x2, y2),(0,255,0),2)
                cv2.putText(image, bbox_mess, (x1,y1-2), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0), bbox_thick//2, lineType=cv2.LINE_AA)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow('image',image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            print("====================================================================")

def tflite_inference(cfg, tflite_model):
    """
    Run inference on all images in directory.
    Args:
        cfg (config): The configuration file.
    Returns:
        None
    """        
    class_names = cfg.dataset.class_names
    anchors_list = cfg.postprocessing.yolo_anchors
    anchors = np.array(anchors_list).reshape(-1, 2)
    num_classes = len(class_names)
    input_shape = cfg.training.model.input_shape
    interpolation = cfg.preprocessing.resizing.interpolation
    if interpolation == 'bilinear':
        interpolation_type = cv2.INTER_LINEAR
    elif interpolation == 'nearest':
        interpolation_type = cv2.INTER_NEAREST
    else:
        raise ValueError("Invalid interpolation method. Supported methods are 'bilinear' and 'nearest'.")
    
    interpreter_quant = tf.lite.Interpreter(model_path=tflite_model)
    interpreter_quant.allocate_tensors()
    input_details = interpreter_quant.get_input_details()[0]
    input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]
    if cfg.dataset.test_path:
        test_set_path = cfg.dataset.test_path
        test_annotations =  load_test_data(test_set_path)
    else:
        print("no test set found")

    for image_file in test_annotations:
        if image_file.endswith(".jpg"):
            image = cv2.imread(os.path.join(test_set_path, image_file))
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            img_name = os.path.splitext(image_file)[0]
            resized_image = cv2.resize(image, (int(input_shape[0]), int(input_shape[0])), interpolation=interpolation_type)
            img = resized_image * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset
            image_processed = (img / input_details['quantization'][0]) + input_details['quantization'][1]
            image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
            image_processed = image_processed.astype(input_details['dtype'])
            image_processed = np.expand_dims(image_processed, 0)

            interpreter_quant.set_tensor(input_index_quant, image_processed)
            interpreter_quant.invoke()
            predictions = interpreter_quant.get_tensor(output_index_quant)

            predictions_tensor = K.constant(predictions)
            predictions_output_shape = K.shape(predictions_tensor)
            input_tensor_shape = K.cast(predictions_output_shape[1:3] * 32, K.dtype(predictions_tensor))
            preds_decoded = tiny_yolo_v2_decode(predictions_tensor, anchors, num_classes, input_tensor_shape, calc_loss=False)
            input_image_shape = [height, width]
            boxes, scores, classes, my_boxes = tiny_yolo_v2_nms(yolo_outputs = preds_decoded,
                                                                image_shape = input_image_shape,
                                                                max_boxes=50,
                                                                score_threshold=float(cfg.postprocessing.confidence_thresh),
                                                                iou_threshold=float(cfg.postprocessing.NMS_thresh),
                                                                classes_ids=list(range(0, num_classes)))
            classes = classes.numpy()
            scores = scores.numpy()
            my_boxes = my_boxes.numpy()
            bbox_thick = int(0.6 * (height + width) / 600)
            for i, c in reversed(list(enumerate(classes))):
                box = my_boxes[i]
                score = scores[i]
                bbox_mess = '{}-{:.2f}'.format(class_names[int(c)],score)
                yyy, xxx, hhh, www = box
                x = xxx*width
                y = yyy*height
                w = www*width
                h = hhh*height
                x1 = int(x-w/2)
                y1 = int(y-h/2)
                x2 = int(x+w/2)
                y2 = int(y+h/2)
                cv2.rectangle(image,(x1,y1), (x2, y2),(0,255,0),2)
                result = "{} {:.2} {:.6} {:.6} {:.6} {:.6}\n".format(int(c),score,xxx,yyy,www,hhh)
                print(result)
                cv2.rectangle(image,(x1,y1), (x2, y2),(0,255,0),2)
                cv2.putText(image, bbox_mess, (x1,y1-2), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0), bbox_thick//2, lineType=cv2.LINE_AA)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow('image',image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            print("====================================================================")


def predict_tiny_yolo_v2(cfg):
    """
    Run inference on all the images within the test set.

    Args:
        cfg (config): The configuration file.
    Returns:
        None.
    """
    output_dir = HydraConfig.get().runtime.output_dir
    class_names = cfg.dataset.class_names
    model_path = cfg.general.model_path
    # Keras model
    if Path(model_path).suffix == '.h5':
        model = tf.keras.models.load_model(model_path)
        float_inference(cfg, model)
    # TFlite model
    if Path(model_path).suffix == '.tflite':
        tflite_inference(cfg, model_path)