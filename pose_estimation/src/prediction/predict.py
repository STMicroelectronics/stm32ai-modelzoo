# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2024 STMicroelectronics.
#  * All rights reserved.
#  *
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
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow.keras.backend as K
import onnx
import onnxruntime
from hydra.core.hydra_config import HydraConfig

from models_utils import get_model_name_and_its_input_shape
from postprocess import spe_postprocess, heatmaps_spe_postprocess, yolo_mpe_postprocess


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

    kpts_nbr = cfg.dataset.keypoints

    prediction_result_dir = f'{cfg.output_dir}/predictions/'
    os.makedirs(prediction_result_dir, exist_ok=True)

    for image_file in test_annotations:
        if image_file.endswith(".jpg"):
            
            print('Inference on image : ',image_file)

            image = cv2.imread(os.path.join(test_set_path, image_file))
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            img_name = os.path.splitext(image_file)[0]
            resized_image = cv2.resize(image, (int(input_shape[0]), int(input_shape[0])), interpolation=interpolation_type)
            image_processed = resized_image * cfg.preprocessing.rescaling.scale + cfg.preprocessing.rescaling.offset
            input_image_shape = [height, width]

            if Path(model_path).suffix == '.tflite':

                if input_details['dtype'] == np.uint8:
                    image_processed = (image_processed - cfg.preprocessing.rescaling.offset) / cfg.preprocessing.rescaling.scale
                    image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
                elif input_details['dtype'] == np.int8:
                    image_processed = (image_processed - cfg.preprocessing.rescaling.offset) / cfg.preprocessing.rescaling.scale
                    image_processed -= 128
                    image_processed = np.clip(np.round(image_processed), np.iinfo(input_details['dtype']).min, np.iinfo(input_details['dtype']).max)
                elif input_details['dtype'] == np.float32:
                    image_processed = image_processed
                else:
                    print('[ERROR] : input dtype not recognized -> ',input_details['dtype'])

                image_processed = image_processed.astype(input_details['dtype'])

            image_processed = np.expand_dims(image_processed, 0)

            if Path(model_path).suffix == '.h5':
                predictions = best_model.predict_on_batch(image_processed)

            if Path(model_path).suffix == '.tflite':
                interpreter_quant.set_tensor(input_index_quant, image_processed)
                interpreter_quant.invoke()
                predictions = [interpreter_quant.get_tensor(outputs_details[j]["index"]) for j in range(len(outputs_details))]
                # Add the support for quantized outputs, with retreival of scale & zero_point
            elif Path(model_path).suffix == '.onnx':
                image_processed = np.transpose(image_processed,[0,3,1,2])
                predictions = sess.run([o.name for o in outputs], {inputs[0].name: image_processed.astype('float32')})


            if Path(model_path).suffix == '.h5':
                predictions_tensor = predictions
            elif Path(model_path).suffix in ['.tflite','.onnx']:
                if len(predictions)==1:
                    predictions_tensor = predictions[0]
                else:
                    predictions_tensor = predictions

            print(predictions_tensor[0,:,0])
            print(predictions_tensor.shape)

            if model_type=='heatmaps_spe':
                poses = heatmaps_spe_postprocess(predictions_tensor)[0]
            elif model_type=='spe':
                poses = spe_postprocess(predictions_tensor)[0]
            elif model_type=='yolo_mpe':
                poses = yolo_mpe_postprocess(predictions_tensor,
                                             max_output_size = cfg.postprocessing.max_detection_boxes,
                                             iou_threshold   = cfg.postprocessing.NMS_thresh,
                                             score_threshold = cfg.postprocessing.confidence_thresh)[0]
            else:
                print('No post-processing found for the model type : '+model_type)

            if kpts_nbr == 17:
                skeleton_connections = [[0,1],[0,2],[1,3],[2,4],[3,5],[4,6],[5,7],[6,8],[7,9],[8,10],[5,6],[5,11],[6,12],[11,12],[11,13],[12,14],[13,15],[14,16]]
            elif kpts_nbr == 13:
                skeleton_connections = [[0,1],[0,2],[1,2],[1,3],[2,4],[3,5],[4,6],[1,7],[2,8],[7,9],[8,10],[9,11],[10,12],[7,8]]
            else:
                skeleton_connections = []
                print('Skeleton for this number of keypoints is not supported -> use 17 or 13')

            threshSkeleton = cfg.postprocessing.kpts_conf_thresh

            for p in poses:
                if model_type in ['heatmaps_spe','spe']:
                    xx, yy, pp = p[0::3],p[1::3],p[2::3]
                elif model_type=='yolo_mpe':
                    bbox_thick = int(0.6 * (height + width) / 600)
                    x,y,w,h,conf = p[:5]
                    xx, yy, pp = p[5::3],p[5+1::3],p[5+2::3]
                    if Path(model_path).suffix == '.onnx':
                        x  /= input_shape[0]
                        y  /= input_shape[0]
                        w  /= input_shape[0]
                        h  /= input_shape[0]
                        xx /= input_shape[0]
                        yy /= input_shape[0]
                    x1 = int((x - w/2)*width)
                    x2 = int((x + w/2)*width)
                    y1 = int((y - h/2)*height)
                    y2 = int((y + h/2)*height)

                if not tf.reduce_all(tf.constant(pp)==0):
                    for i in range(0,len(xx)):
                        if float(pp[i])>threshSkeleton:
                            cv2.circle(image,(int(xx[i]*width),int(yy[i]*height)),radius=5,color=(0, 0, 255), thickness=-1)
                        else:
                            cv2.circle(image,(int(xx[i]*width),int(yy[i]*height)),radius=5,color=(255, 0, 0), thickness=-1)
                    for k,l in skeleton_connections:
                        if float(pp[k])>threshSkeleton and float(pp[l])>threshSkeleton: 
                            cv2.line(image,(int(xx[k]*width),int(yy[k]*height)),(int(xx[l]*width),int(yy[l]*height)),(0, 255, 0))
                if model_type=='yolo_mpe':
                    cv2.rectangle(image,(x1,y1), (x2, y2),(255, 0, 255),1)
                    cv2.putText(image, '{}-{:.2f}'.format('person',conf), (x1,y1-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), bbox_thick//2, lineType=cv2.LINE_AA)

            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # writing prediction result to the output dir
            pred_res_filename = f'{prediction_result_dir}/{os.path.basename(img_name)}.png'
            cv2.imwrite(pred_res_filename,image)
            if cfg.general.display_figures:
                cv2.imshow('image',image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()