# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2024 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
import tqdm
import mlflow
import numpy as np
from pathlib import Path
import tensorflow as tf
import tensorflow.keras.backend as K
import onnx
import onnxruntime
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from typing import Optional

from postprocess import spe_postprocess, heatmaps_spe_postprocess, yolo_mpe_postprocess
from preprocess import apply_rescaling
from metrics import single_pose_oks, multi_pose_oks_mAP, compute_ap

import matplotlib.pyplot as plt

def evaluate(cfg: DictConfig = None, eval_ds: tf.data.Dataset = None,
             model_path_to_evaluate: Optional[str] = None,
             name_ds: Optional[str] = 'test_set') -> None:
    """
    Evaluates and benchmarks a TensorFlow Lite or Keras model, and generates a Config header file if specified.

    Args:
        cfg (config): The configuration file.
        eval_ds (tf.data.Dataset): The validation dataset.
        model_path_to_evaluate (str, optional): Model path to evaluate
        name_ds (str): The name of the chosen test_data to be mentioned in the prints and figures.

    Returns:
        None
    """
    output_dir = HydraConfig.get().runtime.output_dir
    # Pre-process test dataset
    eval_ds = apply_rescaling(dataset=eval_ds, scale=cfg.preprocessing.rescaling.scale,
                              offset=cfg.preprocessing.rescaling.offset)
    
    model_path  = model_path_to_evaluate if model_path_to_evaluate else cfg.general.model_path
    model_type  = cfg.general.model_type
    num_threads = cfg.general.num_threads_tflite

    try:
        file_extension = Path(model_path).suffix
        # Keras model
        if file_extension == '.h5':
            model = tf.keras.models.load_model(model_path)
        # TFlite model
        elif file_extension == '.tflite':
            interpreter_quant = tf.lite.Interpreter(model_path=model_path,num_threads=num_threads)
            interpreter_quant.allocate_tensors()
            input_details   = interpreter_quant.get_input_details()
            outputs_details = interpreter_quant.get_output_details()
            shape_to_resize = list(eval_ds.take(1).as_numpy_iterator())[0][0].shape
            interpreter_quant.resize_tensor_input(input_details[0]['index'], shape_to_resize)
            interpreter_quant.allocate_tensors()
        elif file_extension == '.onnx':
            sess = onnxruntime.InferenceSession(model_path)
            inputs  = sess.get_inputs()
            outputs = sess.get_outputs()
    except Exception:
        raise ValueError(f"Model accuracy evaluation failed\nReceived model path: {model_path}")


    metric = 0
    nb_batches = len(eval_ds)
    tp, conf, nb_gt, maskpad = None, None, None, None


    for images,labels in tqdm.tqdm(eval_ds, total=nb_batches):

        if Path(model_path).suffix == '.h5':
            predictions = model.predict_on_batch(images)
        if Path(model_path).suffix == '.tflite':

            image_processed = images.numpy()

            if input_details[0]['dtype'] == np.uint8:
                image_processed = (image_processed - cfg.preprocessing.rescaling.offset) / cfg.preprocessing.rescaling.scale
                image_processed = np.clip(np.round(image_processed), np.iinfo(input_details[0]['dtype']).min, np.iinfo(input_details[0]['dtype']).max)
            elif input_details[0]['dtype'] == np.int8:
                image_processed = (image_processed - cfg.preprocessing.rescaling.offset) / cfg.preprocessing.rescaling.scale
                image_processed -= 128
                image_processed = np.clip(np.round(image_processed), np.iinfo(input_details[0]['dtype']).min, np.iinfo(input_details[0]['dtype']).max)
            elif input_details[0]['dtype'] == np.float32:
                image_processed = image_processed
            else:
                print('[ERROR] : input dtype not recognized -> ',input_details[0]['dtype'])

            images = image_processed.astype(input_details[0]['dtype'])

            interpreter_quant.set_tensor(input_details[0]['index'], images)
            interpreter_quant.invoke()
            predictions = [interpreter_quant.get_tensor(outputs_details[j]["index"]) for j in range(len(outputs_details))][0]
        elif Path(model_path).suffix == '.onnx':
            t_images = tf.transpose(images,[0,3,1,2]).numpy()
            predictions = sess.run([o.name for o in outputs], {inputs[0].name: t_images.astype('float32')})[0]

        predictions = tf.cast(predictions,tf.float32)

        if model_type=='heatmaps_spe':
            poses = heatmaps_spe_postprocess(predictions)
            oks   = single_pose_oks(labels,poses)
            metric += tf.reduce_mean(oks)
        elif model_type=='spe':
            poses = spe_postprocess(predictions)
            oks   = single_pose_oks(labels,poses)
            metric += tf.reduce_mean(oks)
        elif model_type=='yolo_mpe':
            poses = yolo_mpe_postprocess(predictions,
                                         max_output_size=cfg.postprocessing.max_detection_boxes,
                                         iou_threshold=cfg.postprocessing.NMS_thresh,
                                         score_threshold=cfg.postprocessing.confidence_thresh)
            if Path(model_path).suffix == '.onnx':
                mask_s = tf.constant([images.shape[2]]*4 + [1.] + [images.shape[2],images.shape[2],1.]*17)
                poses /= mask_s[None,None]

            oks   = multi_pose_oks_mAP(labels,poses) # (batch*M,thresh), (batch*M,), (1,), (batch*M,)

            tdet_ind = tf.where(oks[1]>0)[:,0]    # (true_detections,)
            #print(tdet_ind)
            ttp      = tf.gather(oks[0],tdet_ind) # (true_detections,thresh)
            tconf    = tf.gather(oks[1],tdet_ind) # (true_detections,)
            tnb_gt   = oks[2]                     # (1,)
            tmaskpad = tf.gather(oks[3],tdet_ind) # (true_detections,)

            if tp==None:
                tp      = ttp
                conf    = tconf
                nb_gt   = tnb_gt
                maskpad = tmaskpad

            else:
                tp      = tf.concat([tp,ttp],0)
                conf    = tf.concat([conf,tconf],0)
                nb_gt  += tnb_gt
                maskpad = tf.concat([maskpad,tmaskpad],0)
        else:
            print('No post-processing found for the model type : '+model_type)

    if model_type in ['heatmaps_spe','spe']:
        metric /= nb_batches
        print("The mean OKS is : {:.2f}%".format(metric.numpy()*100))
        mlflow.log_metric("OKS", metric.numpy()*100) # logging the OKS in the stm32ai_main.log file
    elif model_type=='yolo_mpe':
        metric = compute_ap(tp, conf, nb_gt, maskpad, cfg.postprocessing.plot_metrics)
        print('mAP@0.5        -> {:.2f}%'.format(metric[0]*100))
        print('mAP@[0.5:0.95] -> {:.2f}%'.format(np.mean(metric)*100))
        mlflow.log_metric("mAP_0.5", metric[0]*100)              # logging the mAP@0.5 in the stm32ai_main.log file
        mlflow.log_metric("mAP_0.5_0.95", np.mean(metric)*100) # logging the mAP@[0.5:0.95] in the stm32ai_main.log file
    else:
        print('No metric found for the model type : '+model_type)

