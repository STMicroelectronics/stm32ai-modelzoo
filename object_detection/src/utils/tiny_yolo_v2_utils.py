# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os, sys, time
import numpy as np
import tensorflow as tf
import onnxruntime
from pathlib import Path
from munch import DefaultMunch
from hydra.core.hydra_config import HydraConfig
from tiny_yolo_v2_evaluate import evaluate_tiny_yolo_v2
from tiny_yolo_v2 import tiny_yolo_v2_body
from st_yolo_lc_v1 import st_yolo_lc_v1_body
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.layers import Input
from gpu_utils import gpu_benchmark

class CheckpointYoloCleanCallBack(Callback):
    """
    A Keras callback that replaces training checkpoints by inference checkpoints at the end of each epoch.
    """
    def __init__(self, class_names,anchors,model_input_shape,logs_dir, network_stride):
        """
        Initializes the callback.

        Parameters:
        - class_names: a list of strings representing the names of the classes that the model can detect.
        - anchors: a list of tuples representing the anchor boxes used in the model.
        - model_input_shape: an integer representing the input shape of the model.
        - logs_dir: a string representing the path and filename of the saved model. The file must be in .h5 format.
        """
        self.class_names = class_names
        self.anchors = anchors
        self.model_input_shape = model_input_shape
        self.logs_dir = logs_dir
        self.network_stride = network_stride

    def on_epoch_end(self, epoch, logs=None):
        _export_tiny_yolo_v2_model(self.class_names,self.anchors,self.model_input_shape,self.logs_dir,self.network_stride)


def _export_tiny_yolo_v2_model(class_names,anchors,model_input_shape,logs_dir,network_stride):
    """
    Export a trained Tiny YOLOv2 model to disk for inference.
    
    Parameters:
    - class_names: a list of strings representing the names of the classes that the model can detect.
    - anchors: a list of tuples representing the anchor boxes used in the model.
    - model_input_shape: an integer representing the input shape of the model.
    - logs_dir: a string representing the path and filename of the saved model. The file must be in .h5 format.
    """
    for models in os.listdir(logs_dir):
        model_path = os.path.join(logs_dir, models)        
        if os.path.isfile(model_path):
            assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'
            num_anchors = len(anchors)
            num_classes = len(class_names)
            w = model_input_shape
            input_tensor = Input(shape=(w, w, 3), name='image_input')
            if network_stride == 32 :
                inference_model = tiny_yolo_v2_body(input_tensor, num_anchors, num_classes)
            else:
                inference_model = st_yolo_lc_v1_body(input_tensor, num_anchors, num_classes)

            inference_model.load_weights(model_path, by_name=False)
            inference_model.save(model_path)

class YoloMapCallBack(Callback):
    """
    A Keras callback that calculates map for tiny_yolo_v2 model each n epochs.
    """
    def __init__(self, cfg, frq = None):
        """
        Initializes the callback.
        Args:
            cfg (dict): The configuration dictionary.
            frq (int): Frequency to calculate map.
        Returns:
            None
        """
        self.cfg = cfg
        self.output_dir = HydraConfig.get().runtime.output_dir
        self.saved_models_dir = self.cfg.general.saved_models_dir
        self.frq = frq

    def on_epoch_end(self, epoch, logs=None):
        try:
            if self.frq:
                if epoch % self.frq == 0:
                    evaluate_tiny_yolo_v2(self.cfg,model_path=os.path.join(self.output_dir, self.saved_models_dir, "best_model.h5"))
            else:
                evaluate_tiny_yolo_v2(self.cfg,model_path=os.path.join(self.output_dir, self.saved_models_dir, "best_model.h5"))
        except Exception as e:
            err = e

def check_cfg_attributes(cfg):
    """
    Checks that all the expected attributes are present in the configuration dictionary and that
    there are no unknown attributes.

    Args:
        cfg (dict): The configuration dictionary.
    Returns:
        None
    """
    if cfg.general.model_path and Path(cfg.general.model_path).suffix == '.h5':
        model_path = cfg.general.model_path
        old_model = tf.keras.models.load_model(model_path)
        input_shape = old_model.layers[0].input_shape
        if cfg.training:
            cfg.training.model = DefaultMunch()
        else:
            cfg.training = DefaultMunch()
            cfg.training.model = DefaultMunch()
        cfg.training.model.input_shape = input_shape[0][1:]
    elif cfg.general.model_path and Path(cfg.general.model_path).suffix == '.tflite':
        model_path = cfg.general.model_path
        interpreter_quant = tf.lite.Interpreter(model_path=model_path)
        input_details = interpreter_quant.get_input_details()[0]
        input_shape = input_details['shape']
        if cfg.training:
            cfg.training.model = DefaultMunch()
        else:
            cfg.training = DefaultMunch()
            cfg.training.model = DefaultMunch()
        cfg.training.model.input_shape = input_shape[1:]
    elif cfg.general.model_path and Path(cfg.general.model_path).suffix == '.onnx':
        sess = onnxruntime.InferenceSession(cfg.general.model_path)
        inputs  = sess.get_inputs()
        ish = inputs[0].shape
        input_shape = [ish[2],ish[3],ish[1]]
        if cfg.training:
            cfg.training.model = DefaultMunch()
        else:
            cfg.training = DefaultMunch()
            cfg.training.model = DefaultMunch()
        cfg.training.model.input_shape = input_shape
    elif not cfg.general.model_path:
        cfg.training.model.input_shape = cfg.training.model.input_shape
    if cfg.operation_mode not in ['quantization' ,'benchmarking']:
        cfg.postprocessing.yolo_anchors = [x * cfg.training.model.input_shape[0] for x in cfg.postprocessing.yolo_anchors]

        if cfg.general.model_type == "tiny_yolo_v2":
            cfg.postprocessing.network_stride = 32
        elif cfg.general.model_type == "st_yolo_lc_v1":
            cfg.postprocessing.network_stride = 16

def set_multi_scale_max_resolution(cfg):
    """
    Set the maximum input size for multi-scale data augmentation based on the available GPU memory.

    Args:
        cfg (Config): The configuration object containing the necessary parameters.

    Returns:
        None
    """
    gpu_limit = cfg.general.gpu_memory_limit
    min_input_size = cfg.training.model.input_shape[0]
    batch_size  = cfg.training.batch_size
    anchors_list = cfg.postprocessing.yolo_anchors
    anchors = np.array(anchors_list).reshape(-1, 2)
    num_anchors = len(anchors)
    classes = cfg.dataset.class_names
    num_classes = len(classes)
    channels = cfg.training.model.input_shape[2]
    network_stride = cfg.postprocessing.network_stride

    sizes = list(range(min_input_size, 609, cfg.postprocessing.network_stride))
    sizes = sorted(sizes, reverse=True)
    for im_sz in sizes:
        input_shape= (im_sz,im_sz,channels)
        input_tensor = Input(shape=input_shape, batch_size=batch_size, name='image_input')
        if network_stride == 32 :
            model = tiny_yolo_v2_body(input_tensor, num_anchors, num_classes)
        else:
            model = st_yolo_lc_v1_body(input_tensor, num_anchors, num_classes)
        model.compile(loss=tf.keras.losses.mean_squared_error, optimizer=tf.keras.optimizers.Adam(learning_rate=0.01))
        print("[INFO] : Setting max input size to {} for multi scale data augmentation".format(im_sz))
        size_error = gpu_benchmark(gpu_limit, batch_size,input_shape,model)
        if size_error:
            print("[WRN] : Not enough GPU memory!!")
        else:
            sizes_list = list(range(min_input_size, (im_sz+1), cfg.postprocessing.network_stride))
            cfg.data_augmentation.multi_scale_list = [(x, x) for x in sizes_list]
            break
