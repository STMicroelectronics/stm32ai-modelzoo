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

import matplotlib.pyplot
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
import onnx
import onnxruntime
from hydra.core.hydra_config import HydraConfig

from models_utils import get_model_name_and_its_input_shape
from postprocess import postprocess_predictions
from tiny_yolo_v2_postprocess import tiny_yolo_v2_decode, tiny_yolo_v2_nms


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

def predict(cfg):
    """
    Run inference on all the images within the test set.

    Args:
        cfg (config): The configuration file.
    Returns:
        None.
    """

    output_dir = HydraConfig.get().runtime.output_dir
    model_path = cfg.general.model_path
    model_type = cfg.general.model_type
    class_names = cfg.dataset.class_names
    num_classes = len(class_names)
    if model_type in ['st_yolo_lc_v1','tiny_yolo_v2']:
        anchors = cfg.postprocessing.yolo_anchors
        anchors = np.array(anchors).reshape(-1, 2)
    _, input_shape = get_model_name_and_its_input_shape(model_path)
    
    # Keras model
    if Path(model_path).suffix == '.h5':
        best_model = tf.keras.models.load_model(model_path)
    # TFlite model
    elif Path(model_path).suffix == '.tflite':
        interpreter_quant = tf.lite.Interpreter(model_path=model_path)
        interpreter_quant.allocate_tensors()
        input_details = interpreter_quant.get_input_details()[0]
        outputs_details = interpreter_quant.get_output_details()
        input_index_quant = interpreter_quant.get_input_details()[0]["index"]
    elif Path(model_path).suffix == '.onnx':
        input_shape = input_shape[1:]
        sess = onnxruntime.InferenceSession(model_path)
        inputs  = sess.get_inputs()
        outputs = sess.get_outputs()

    interpolation = cfg.preprocessing.resizing.interpolation
    if interpolation == 'bilinear':
        interpolation_type = cv2.INTER_LINEAR
    elif interpolation == 'nearest':
        interpolation_type = cv2.INTER_NEAREST
    else:
        raise ValueError("Invalid interpolation method. Supported methods are 'bilinear' and 'nearest'.")

    if cfg.prediction.test_files_path:
        test_set_path = cfg.prediction.test_files_path
        test_annotations =  load_test_data(test_set_path)
    else:
        print("no test set found")

    prediction_result_dir = f'{cfg.output_dir}/predictions/'
    os.makedirs(prediction_result_dir, exist_ok=True)
    for image_file in test_annotations:
        if image_file.endswith(".jpg"):
            print(f"================ Running prediction on : {os.path.basename(image_file)} ========================")
            image = cv2.imread(os.path.join(test_set_path, image_file))
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            img_name = os.path.splitext(image_file)[0]
            resized_image = cv2.resize(image, (int(input_shape[0]), int(input_shape[0])), interpolation=interpolation_type)
            image_data = resized_image * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset
            input_image_shape = [height, width]

            if Path(model_path).suffix == '.tflite':
                image_processed = (image_data / input_details['quantization'][0]) + input_details['quantization'][1]
                image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
                image_processed = image_processed.astype(input_details['dtype'])
                image_data = image_processed

            image_processed = np.expand_dims(image_data, 0)

            if Path(model_path).suffix == '.h5':
                predictions = best_model.predict_on_batch(image_processed)

            if Path(model_path).suffix == '.tflite':
                interpreter_quant.set_tensor(input_index_quant, image_processed)
                interpreter_quant.invoke()
                predictions = [interpreter_quant.get_tensor(outputs_details[j]["index"]) for j in range(len(outputs_details))]
            elif Path(model_path).suffix == '.onnx':
                image_processed = np.transpose(image_processed,[0,3,1,2])
                predictions = sess.run([o.name for o in outputs], {inputs[0].name: image_processed.astype('float32')})
            
            if model_type in ['st_ssd_mobilenet_v1','ssd_mobilenet_v2_fpnlite']:
                preds_decoded = postprocess_predictions(predictions=predictions, image_size = [width,height], nms_thresh = cfg.postprocessing.NMS_thresh, confidence_thresh = cfg.postprocessing.confidence_thresh)
                for c in preds_decoded:
                    for bb in preds_decoded[c]:
                        bbox_thick = int(0.6 * (height + width) / 600)
                        x1 = int(bb[1])
                        y1 = int(bb[2])
                        x2 = int(bb[3])
                        y2 = int(bb[4])
                        cv2.rectangle(image,(x1,y1), (x2, y2),(0,255,0),2)
                        cv2.putText(image, '{}-{:.2f}'.format(class_names[c-1],bb[0]), (x1,y1-2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), bbox_thick//2, lineType=cv2.LINE_AA)

            elif model_type in ['st_yolo_lc_v1','tiny_yolo_v2']:
                if Path(model_path).suffix == '.h5':
                    predictions_tensor = K.constant(predictions)
                elif Path(model_path).suffix in ['.tflite','.onnx']:
                    predictions_tensor = K.constant(predictions[0])
                
                predictions_output_shape = K.shape(predictions_tensor)
                input_tensor_shape = K.cast(predictions_output_shape[1:3] * cfg.postprocessing.network_stride, K.dtype(predictions_tensor))
                preds_decoded = tiny_yolo_v2_decode(predictions_tensor, anchors, num_classes, input_tensor_shape, calc_loss=False)
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
            # writing prediction result to the output dir
            pred_res_filename = f'{prediction_result_dir}/{os.path.basename(img_name)}.png'
            cv2.imwrite(pred_res_filename,image)
            if cfg.general.display_figures:
                cv2.imshow('image',image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()