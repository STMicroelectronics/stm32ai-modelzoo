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
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow.keras.backend as K
from hydra.core.hydra_config import HydraConfig
from typing import Optional

from object_det_metrics.lib.BoundingBox import BoundingBox
from object_det_metrics.lib.BoundingBoxes import BoundingBoxes
from object_det_metrics.lib.Evaluator import Evaluator
from object_det_metrics.lib.utils import BBFormat, BBType, CoordinatesType
from tiny_yolo_v2_postprocess import tiny_yolo_v2_decode, tiny_yolo_v2_nms
from typing import Optional


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

def calculate_float_map(cfg, best_model):
    """
    Calculates the mean average precision (mAP) for the given model on the test set.

    Args:
        cfg (config): The configuration file.
        best_model (tf.keras.Model): The model to evaluate.
    Returns:
        float: The mAP value.
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

    ap_folder = os.path.join(HydraConfig.get().runtime.output_dir, "float_model_ap_{}".format(int(input_shape[0])))
    if os.path.exists(ap_folder):
        print("folder already exist")
    else:
        os.system("mkdir {}".format(ap_folder))
    tf.print('[INFO] : Starting calculating map')
    m_Start = time.time()
    ap_classes = []
    ap_classes_names = []
    all_bbs = BoundingBoxes()

    if cfg.dataset.test_path:
        test_set_path = cfg.dataset.test_path
        test_annotations =  load_test_data(test_set_path)
    elif cfg.dataset.test_path == None and cfg.dataset.validation_path:
        test_set_path = cfg.dataset.validation_path
        test_annotations = load_test_data(test_set_path)
    elif cfg.dataset.test_path == None and cfg.dataset.validation_path == None and cfg.dataset.training_path:
        test_set_path = cfg.dataset.training_path
        train_set = load_test_data(cfg.dataset.training_path)
        num_val = int(len(train_set)*cfg.dataset.validation_split)
        num_train = len(train_set) - num_val
        test_annotations = train_set[num_train:]
    else:
        print("no dataset is found")
    for image_file in tqdm.tqdm(test_annotations):
        if image_file.endswith(".jpg"):
            image = cv2.imread(os.path.join(test_set_path, image_file))
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape

            img_name = os.path.splitext(image_file)[0]
            gt = os.path.join(test_set_path, (img_name+'.txt'))
            fh1 = open(gt, "r")
            for line in fh1:
                line = line.replace("\n", "")
                if line.replace(' ', '') == '':
                    continue
                splitLine = line.split(" ")
                idClass, x, y, w, h = int(splitLine[0]), float(check(splitLine[1])), float(check(splitLine[2])), float(check(splitLine[3])), float(check(splitLine[4]))
                bb = BoundingBox(img_name, idClass, x, y, w, h, CoordinatesType.Relative, (width, height), BBType.GroundTruth, format=BBFormat.XYWH)
                all_bbs.addBoundingBox(bb)
            fh1.close()

            resized_image = cv2.resize(image, (int(input_shape[0]), int(input_shape[0])), interpolation=interpolation_type)
            image_data = resized_image * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset
            image_processed = np.expand_dims(image_data, 0)
            predictions = best_model.predict_on_batch(image_processed)
            predictions_tensor = K.constant(predictions)
            predictions_output_shape = K.shape(predictions_tensor)
            input_tensor_shape = K.cast(predictions_output_shape[1:3] * cfg.postprocessing.network_stride, K.dtype(predictions_tensor))
            preds_decoded = tiny_yolo_v2_decode(predictions_tensor, anchors, num_classes, input_tensor_shape, calc_loss=False)
            input_image_shape = [height, width]
            boxes, scores, classes, my_boxes = tiny_yolo_v2_nms(yolo_outputs = preds_decoded,
                                                                image_shape = input_image_shape,
                                                                max_boxes=int(cfg.postprocessing.max_detection_boxes),
                                                                score_threshold=float(cfg.postprocessing.confidence_thresh),
                                                                iou_threshold=float(cfg.postprocessing.NMS_thresh),
                                                                classes_ids=list(range(0, num_classes)))
            classes = classes.numpy()
            scores = scores.numpy()
            my_boxes = my_boxes.numpy()
            for i, c in reversed(list(enumerate(classes))):
                predicted_class = c
                box = my_boxes[i]
                score = scores[i]
                yyy, xxx, hhh, www = box
                idClass,conf,x,y,w,h = int(predicted_class),float(check(score)),float(check(xxx)),float(check(yyy)),float(check(www)),float(check(hhh))
                bb = BoundingBox(img_name,idClass,x,y,w,h,CoordinatesType.Relative, (width,height), BBType.Detected,conf, format=BBFormat.XYWH)
                all_bbs.addBoundingBox(bb)

    evaluator = Evaluator()
    tmp_result = evaluator.GetPascalVOCMetrics(all_bbs, IOUThreshold=float(cfg.postprocessing.IoU_eval_thresh))
    for class_metrics in tmp_result:
        classID = class_names[int(class_metrics["class"])]
        figure = plt.figure(figsize=(10, 10))
        plt.xlabel('recall')
        plt.ylabel('precision')
        plt.title('AP for class %s on db %s' % (str(classID), cfg.dataset.name))
        precision = class_metrics['precision']
        recall = class_metrics['recall']
        ap = float(check(class_metrics['AP']))
        plt.plot(recall, precision, label=str(classID)+" AP " + "{:.2f}".format(ap*100)+"%")
        plt.legend(shadow=True, prop={'size': 8})
        plt.grid()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.savefig('{}/{}_AP.png'.format(ap_folder, str(classID)))
        plt.close(figure)
        buf.seek(0)
        ap_classes.append(ap)
        ap_classes_names.append(str(classID))

    m_End = time.time()
    elapsed = (m_End - m_Start) / 60.0
    mAP = 0
    for rank, av_p in enumerate(ap_classes):
        tf.print("[RESULTS] AP for class {} = {:.2f} % ".format(ap_classes_names[rank], av_p*100))
        mAP = av_p*100 + mAP
    tf.print("[RESULTS] mAP = {:.2f} % ".format(round((mAP/len(ap_classes)), 2)))
    tf.print("[INFO] : Evaluation took {:.4} minutes".format(elapsed))
    return round((mAP/len(ap_classes)), 2)


def calculate_quantized_map(cfg, tflite_model, num_threads: Optional[int] = 1):
    """
    Calculates the mean average precision (mAP) for the given model on the test set.

    Args:
        cfg (config): The configuration file.
        tflite_model (tf.keras.Model): The model to evaluate.
        num_threads: Optional[int]: number of threads for the tflite interpreter
    Returns:
        float: The mAP value.
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

    ap_folder = os.path.join(HydraConfig.get().runtime.output_dir, "quantized_model_ap_{}".format(int(input_shape[0])))
    if os.path.exists(ap_folder):
        print("folder already exist")
    else:
        os.system("mkdir {}".format(ap_folder))
    
    interpreter_quant = tf.lite.Interpreter(model_path=tflite_model, num_threads=num_threads)
    interpreter_quant.allocate_tensors()
    input_details = interpreter_quant.get_input_details()[0]
    input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]

    tf.print('[INFO] : Starting calculating map')
    m_Start = time.time()
    ap_classes = []
    ap_classes_names = []
    all_bbs = BoundingBoxes()

    if cfg.dataset.test_path:
        test_set_path = cfg.dataset.test_path
        test_annotations =  load_test_data(test_set_path)
    elif cfg.dataset.test_path == None and cfg.dataset.validation_path:
        test_set_path = cfg.dataset.validation_path
        test_annotations = load_test_data(test_set_path)
    elif cfg.dataset.test_path == None and cfg.dataset.validation_path == None and cfg.dataset.training_path:
        test_set_path = cfg.dataset.training_path
        train_set = load_test_data(cfg.dataset.training_path)
        num_val = int(len(train_set)*cfg.dataset.validation_split)
        num_train = len(train_set) - num_val
        test_annotations = train_set[num_train:]
    else:
        print("no dataset is found")
    for image_file in tqdm.tqdm(test_annotations):
        if image_file.endswith(".jpg"):
            image = cv2.imread(os.path.join(test_set_path, image_file))
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape

            img_name = os.path.splitext(image_file)[0]
            gt = os.path.join(test_set_path, (img_name+'.txt'))
            fh1 = open(gt, "r")
            for line in fh1:
                line = line.replace("\n", "")
                if line.replace(' ', '') == '':
                    continue
                splitLine = line.split(" ")
                idClass, x, y, w, h = int(splitLine[0]), float(check(splitLine[1])), float(check(splitLine[2])), float(check(splitLine[3])), float(check(splitLine[4]))
                bb = BoundingBox(img_name, idClass, x, y, w, h, CoordinatesType.Relative, (width, height), BBType.GroundTruth, format=BBFormat.XYWH)
                all_bbs.addBoundingBox(bb)
            fh1.close()

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
            input_tensor_shape = K.cast(predictions_output_shape[1:3] * cfg.postprocessing.network_stride, K.dtype(predictions_tensor))
            preds_decoded = tiny_yolo_v2_decode(predictions_tensor, anchors, num_classes, input_tensor_shape, calc_loss=False)
            input_image_shape = [height, width]
            boxes, scores, classes, my_boxes = tiny_yolo_v2_nms(yolo_outputs = preds_decoded,
                                                                image_shape = input_image_shape,
                                                                max_boxes=int(cfg.postprocessing.max_detection_boxes),
                                                                score_threshold=float(cfg.postprocessing.confidence_thresh),
                                                                iou_threshold=float(cfg.postprocessing.NMS_thresh),
                                                                classes_ids=list(range(0, num_classes)))
            classes = classes.numpy()
            scores = scores.numpy()
            my_boxes = my_boxes.numpy()
            for i, c in reversed(list(enumerate(classes))):
                predicted_class = c
                box = my_boxes[i]
                score = scores[i]
                yyy, xxx, hhh, www = box
                idClass,conf,x,y,w,h = int(predicted_class),float(check(score)),float(check(xxx)),float(check(yyy)),float(check(www)),float(check(hhh))
                bb = BoundingBox(img_name,idClass,x,y,w,h,CoordinatesType.Relative, (width,height), BBType.Detected,conf, format=BBFormat.XYWH)
                all_bbs.addBoundingBox(bb)

    evaluator = Evaluator()
    tmp_result = evaluator.GetPascalVOCMetrics(all_bbs, IOUThreshold=float(cfg.postprocessing.IoU_eval_thresh))
    for class_metrics in tmp_result:
        classID = class_names[int(class_metrics["class"])]
        figure = plt.figure(figsize=(10, 10))
        plt.xlabel('recall')
        plt.ylabel('precision')
        plt.title('AP for class %s on db %s' % (str(classID), cfg.dataset.name))
        precision = class_metrics['precision']
        recall = class_metrics['recall']
        ap = float(check(class_metrics['AP']))
        plt.plot(recall, precision, label=str(classID)+" AP " + "{:.2f}".format(ap*100)+"%")
        plt.legend(shadow=True, prop={'size': 8})
        plt.grid()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.savefig('{}/{}_AP.png'.format(ap_folder, str(classID)))
        plt.close(figure)
        buf.seek(0)
        ap_classes.append(ap)
        ap_classes_names.append(str(classID))

    m_End = time.time()
    elapsed = (m_End - m_Start) / 60.0
    mAP = 0
    for rank, av_p in enumerate(ap_classes):
        tf.print("[RESULTS] AP for class {} = {:.2f} % ".format(ap_classes_names[rank], av_p*100))
        mAP = av_p*100 + mAP
    tf.print("[RESULTS] mAP = {:.2f} % ".format(round((mAP/len(ap_classes)), 2)))
    tf.print("[INFO] : Evaluation took {:.4} minutes".format(elapsed))
    return round((mAP/len(ap_classes)), 2)

def evaluate_tiny_yolo_v2(cfg, valid_ds= None, test_ds = None, model_path = None) -> None:
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

    output_dir = HydraConfig.get().runtime.output_dir
    class_names = cfg.dataset.class_names

    if model_path:
        model_path = model_path
    else:
        model_path = cfg.general.model_path

    # Keras model
    if Path(model_path).suffix == '.h5':
        # Load the model
        model = tf.keras.models.load_model(model_path)
        print("[INFO] : Evaluating the float model...")
        mAP = calculate_float_map(cfg, model)
        mlflow.log_metric("float_model_mAP", mAP)
    # TFlite model
    if Path(model_path).suffix == '.tflite':
        # Evaluate quantized TensorFlow Lite model
        print("[INFO] : Evaluating the TFlite model...")
        mAP = calculate_quantized_map(cfg, model_path, num_threads=cfg.general.num_threads_tflite)
        mlflow.log_metric("int_model_mAP", mAP)