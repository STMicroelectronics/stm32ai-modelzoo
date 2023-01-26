# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import io
import os
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as k
import tqdm
from anchor_boxes_utils import bbox_iou
from hydra.core.hydra_config import HydraConfig
from object_det_metrics.lib.BoundingBox import BoundingBox
from object_det_metrics.lib.BoundingBoxes import BoundingBoxes
from object_det_metrics.lib.Evaluator import Evaluator
from object_det_metrics.lib.utils import BBFormat, BBType, CoordinatesType


def check(va):
    if va in ["inf", "-inf", "NaN", "nan"]:
        va = 0
    return va


def convert_predictions_to_R_BB(image, box, relative):
    height, width, _ = image.shape
    class_id = box[0]
    x_min = box[1]
    y_min = box[2]
    x_max = box[3]
    y_max = box[4]
    w = x_max - x_min
    h = y_max - y_min
    x_center = x_min + w/2
    y_center = y_min + h/2
    if relative is False:
        return [class_id, x_center, y_center, w, h]
    else:
        x_r = x_center/width
        y_r = y_center/height
        w_r = w/width
        h_r = h/height
        return [class_id, x_r, y_r, w_r, h_r]


def decode_predictions(predictions, normalize=True, org_img_height=None, org_img_width=None):
    '''
    Retrieve object bounding box coordinates from predicted offsets and anchor box coordinates
    Arguments:
        predictions: output of SSD-based human detection model, a tensor of [None, #boxes, 1+n_classes+4+4]
        normalize: coordinates are normalized or not, bool
        org_img_height: original image height, used if normalize=True, integer
        org_img_width: original image width, used if normalize=True, integer
    Returns:
        predictions_decoded_raw: object bounding boxes and categories, a tensor of [None, #boxes, 1+n_classes+4]
    '''
    predictions_decoded_raw = np.copy(predictions[:, :, :-4])
    # offsets are normalized with height and width of anchor boxes
    predictions_decoded_raw[:, :, [-4, -2]] *= np.expand_dims(predictions[:, :, -2] - predictions[:, :, -4], axis=-1)
    predictions_decoded_raw[:, :, [-3, -1]] *= np.expand_dims(predictions[:, :, -1] - predictions[:, :, -3], axis=-1)
    predictions_decoded_raw[:, :, -4:] += predictions[:, :, -4:]

    if normalize:
        predictions_decoded_raw[:, :, [-4, -2]] *= org_img_width
        predictions_decoded_raw[:, :, [-3, -1]] *= org_img_height

    return predictions_decoded_raw


def do_nms(preds_decoded, nms_thresh=0.45, confidence_thresh=0.5):
    '''
    Non-maximum suppression, removing overlapped bounding boxes based on IoU metric and keeping bounding boxes with the highest score
    Arguments:
        preds_decoded: return of decode_predictions function, a tensor of [None, #boxes, 1+n_classes+4]
        nms_thresh: IoU threshold to remove overlapped bounding boxes, a float between 0 and 1
        confidence_thresh: minimum score to keep bounding boxes, a float between 0 and 1
    Returns:
        final_preds: detection results after non-maximum suppression
    '''
    n_boxes = int(preds_decoded.shape[1])
    batch_size = int(preds_decoded.shape[0])
    n_classes_bg = int(preds_decoded.shape[2]) - 4

    final_preds = dict()

    for b_item in preds_decoded:  # loop for each batch item
        for c in range(1, n_classes_bg):  # loop for each object category
            single_class = b_item[:, [c, -4, -3, -2, -1]]  # retrieve predictions [score, xmin, ymin, xmax, ymax] for category c
            threshold_met = single_class[single_class[:, 0] > confidence_thresh]  # filter predictions with minimum confidence score threshold
            if threshold_met.shape[0] > 0:
                # sort confidence score in descending order
                sorted_indices = np.argsort([-elm[0] for elm in threshold_met])
                for i in range(len(sorted_indices)):  # loop for bounding boxes in order of highest score
                    index_i = sorted_indices[i]
                    if threshold_met[index_i, 0] == 0:  # verify if this box was processed
                        continue
                    box_i = threshold_met[index_i, -4:]  # get [xmin, ymin, xmax, ymax] of box_i
                    for j in range(i+1, len(sorted_indices)):
                        index_j = sorted_indices[j]
                        if threshold_met[index_j, 0] == 0:  # verify if this box was processed
                            continue
                        box_j = threshold_met[index_j, -4:]  # get [xmin, ymin, xmax, ymax] of box_j
                        if bbox_iou(box_i, box_j) >= nms_thresh:  # check if two boxes are overlapped based on IoU metric
                            threshold_met[index_j, 0] = 0  # if Yes, remove bounding box with smaller confidence score
                threshold_met = threshold_met[threshold_met[:, 0] > 0]
            final_preds[c] = threshold_met  # detection results after non-maximum suppression of object category c

    return final_preds


def relu6(x):
    return k.relu(x, max_value=6.0)


def calculate_float_map(cfg, best_model):
    ap_folder = os.path.join(HydraConfig.get().runtime.output_dir, "float_model_ap_{}".format(int(cfg.model.input_shape[0])))
    if os.path.exists(ap_folder):
        print("folder already exist")
    else:
        os.system("mkdir {}".format(ap_folder))
    tf.print('[INFO] Starting calculating map')
    m_Start = time.time()
    class_names = ["background"] + cfg.dataset.class_names
    ap_classes = []
    ap_classes_names = []
    all_bbs = BoundingBoxes()

    if cfg.dataset.test_path is not None:
        test_set_path = cfg.dataset.test_path
    else:
        test_set_path = cfg.dataset.validation_path

    for image_file in tqdm.tqdm(os.listdir(test_set_path)):
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
                idClass, x, y, w, h = int(int(splitLine[0])+1), float(check(splitLine[1])), float(check(splitLine[2])), float(check(splitLine[3])), float(check(splitLine[4]))
                bb = BoundingBox(img_name, idClass, x, y, w, h, CoordinatesType.Relative, (width, height), BBType.GroundTruth, format=BBFormat.XYWH)
                all_bbs.addBoundingBox(bb)
            fh1.close()

            resized_image = cv2.resize(image, (int(cfg.model.input_shape[0]), int(cfg.model.input_shape[0])), interpolation=cv2.INTER_LINEAR)
            image_data = resized_image/cfg.pre_processing.rescaling.scale + cfg.pre_processing.rescaling.offset
            image_processed = np.expand_dims(image_data, 0)
            predictions = best_model.predict_on_batch(image_processed)
            preds_decoded = decode_predictions(predictions, normalize=True, org_img_height=height, org_img_width=width)
            final_preds = do_nms(preds_decoded, nms_thresh=float(cfg.post_processing.NMS_thresh), confidence_thresh=float(cfg.post_processing.confidence_thresh))

            for _category, predictions in final_preds.items():
                predicted_class = _category
                for prediction in predictions:
                    score, xmi, ymi, xma, yma = prediction
                    pred_list = [predicted_class, xmi, ymi, xma, yma]
                    r_pred_list = convert_predictions_to_R_BB(image, pred_list, True)
                    idClass, conf, x, y, w, h = int(r_pred_list[0]), float(check(score)), float(check(r_pred_list[1])), float(check(r_pred_list[2])), float(check(r_pred_list[3])), float(check(r_pred_list[4]))
                    bb = BoundingBox(img_name, idClass, x, y, w, h, CoordinatesType.Relative, (width, height), BBType.Detected, conf, format=BBFormat.XYWH)
                    all_bbs.addBoundingBox(bb)

    evaluator = Evaluator()
    tmp_result = evaluator.GetPascalVOCMetrics(all_bbs, IOUThreshold=float(cfg.post_processing.IoU_eval_thresh))
    for class_metrics in tmp_result:
        classID = class_names[int(class_metrics["class"])]
        figure = plt.figure(figsize=(10, 10))
        plt.xlabel('recall')
        plt.ylabel('precision')
        plt.title('AP for class %s on db %s' % (str(classID), cfg.dataset.name))
        precision = class_metrics['precision']
        recall = class_metrics['recall']
        ap = class_metrics['AP']
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
    tf.print("[INFO] Evaluation took {:.4} minutes".format(elapsed))
    return round((mAP/len(ap_classes)), 2)


def calculate_quantized_map(cfg, quantized_model_path):
    tf.print('[INFO] Starting calculating map')
    m_Start = time.time()

    ap_folder = os.path.join(HydraConfig.get().runtime.output_dir, "quantized_model_ap_{}".format(int(cfg.model.input_shape[0])))
    if os.path.exists(ap_folder):
        print("folder already exist")
    else:
        os.system("mkdir {}".format(ap_folder))

    interpreter_quant = tf.lite.Interpreter(model_path=quantized_model_path)
    interpreter_quant.allocate_tensors()
    input_details = interpreter_quant.get_input_details()[0]
    input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    output_index_quant = interpreter_quant.get_output_details()[0]["index"]
    class_names = ["background"] + cfg.dataset.class_names

    m_Start = time.time()

    ap_classes = []
    ap_classes_names = []
    all_bbs = BoundingBoxes()

    if cfg.dataset.test_path is not None:
        test_set_path = cfg.dataset.test_path
    else:
        test_set_path = cfg.dataset.validation_path

    for image_file in tqdm.tqdm(os.listdir(test_set_path)):
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
                idClass, x, y, w, h = int(int(splitLine[0])+1), float(check(splitLine[1])), float(check(splitLine[2])), float(check(splitLine[3])), float(check(splitLine[4]))
                bb = BoundingBox(img_name, idClass, x, y, w, h, CoordinatesType.Relative, (width, height), BBType.GroundTruth, format=BBFormat.XYWH)
                all_bbs.addBoundingBox(bb)
            fh1.close()
            resized_image = cv2.resize(image, (int(cfg.model.input_shape[0]), int(cfg.model.input_shape[0])), interpolation=cv2.INTER_LINEAR)
            image_data = resized_image/cfg.pre_processing.rescaling.scale + cfg.pre_processing.rescaling.offset
            img = image_data.astype(np.float32)
            image_processed = (img / input_details['quantization'][0]) + input_details['quantization'][1]
            image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
            image_processed = image_processed.astype(input_details['dtype'])
            image_processed = tf.expand_dims(image_processed, 0)
            interpreter_quant.set_tensor(input_index_quant, image_processed)
            interpreter_quant.invoke()
            predictions = interpreter_quant.get_tensor(output_index_quant)
            preds_decoded = decode_predictions(predictions, normalize=True, org_img_height=height, org_img_width=width)
            final_preds = do_nms(preds_decoded, nms_thresh=float(cfg.post_processing.NMS_thresh), confidence_thresh=float(cfg.post_processing.confidence_thresh))

            for _category, predictions in final_preds.items():
                predicted_class = _category
                for prediction in predictions:
                    score, xmi, ymi, xma, yma = prediction
                    pred_list = [predicted_class, xmi, ymi, xma, yma]
                    r_pred_list = convert_predictions_to_R_BB(image, pred_list, True)
                    idClass, conf, x, y, w, h = int(r_pred_list[0]), float(check(score)), float(check(r_pred_list[1])), float(check(r_pred_list[2])), float(check(r_pred_list[3])), float(check(r_pred_list[4]))
                    bb = BoundingBox(img_name, idClass, x, y, w, h, CoordinatesType.Relative, (width, height), BBType.Detected, conf, format=BBFormat.XYWH)
                    all_bbs.addBoundingBox(bb)

    evaluator = Evaluator()
    tmp_result = evaluator.GetPascalVOCMetrics(all_bbs, IOUThreshold=float(cfg.post_processing.IoU_eval_thresh))
    for class_metrics in tmp_result:
        classID = class_names[int(class_metrics["class"])]
        figure = plt.figure(figsize=(10, 10))
        plt.xlabel('recall')
        plt.ylabel('precision')
        plt.title('AP for class %s on db %s' % (str(classID), cfg.dataset.name))
        precision = class_metrics['precision']
        recall = class_metrics['recall']
        ap = class_metrics['AP']
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
    tf.print("[RESULTS] Quantized model mAP = {:.2f} % ".format(round((mAP/len(ap_classes)), 2)))
    tf.print("[INFO] Evaluation took {:.4} minutes".format(elapsed))
    return round((mAP/len(ap_classes)), 2)
