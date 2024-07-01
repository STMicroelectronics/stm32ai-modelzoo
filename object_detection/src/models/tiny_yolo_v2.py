# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import os
import sys
import numpy as np
import tensorflow as tf
from pathlib import Path#change
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model

from common_training import set_frozen_layers, set_dropout_rate, get_optimizer
from tensorflow.keras.layers import Input, Lambda
from tiny_yolo_v2_loss import tiny_yolo_v2_loss
from st_yolo_lc_v1 import st_yolo_lc_v1_body

def DarknetConv2D_BN_Leaky(filters: int, x: layers.Input) -> layers.Input:
    """
    Darknet Convolution2D followed by CustomBatchNormalization and LeakyReLU.
    
    Args:
    - filters: An integer representing the number of filters in the convolution layer.
    - x: A tensor representing the input to the layer.
    
    Returns:
    - A tensor representing the output of the layer.
    """
    x = layers.Conv2D(filters, (3, 3), strides=(1,1), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('leaky_relu')(x)
    return x


def tiny_yolo_v2_body(inputs: layers.Input, num_anchors: int, num_classes: int) -> keras.Model:
    """
    Builds a Tiny YOLOv2 model architecture using the DarknetConv2D_BN_Leaky layer.

    Args:
    - inputs: a tensor representing the input to the model
    - num_anchors: an integer representing the number of anchors used in the model
    - num_classes: an integer representing the number of classes to be predicted by the model

    Returns:
    - a keras Model object representing the Tiny YOLOv2 model architecture
    """
    len_anchor = 5 + num_classes
    len_detection_vector = len_anchor * num_anchors

    x = DarknetConv2D_BN_Leaky(16,inputs)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = DarknetConv2D_BN_Leaky(32,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = DarknetConv2D_BN_Leaky(64,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = DarknetConv2D_BN_Leaky(128,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = DarknetConv2D_BN_Leaky(256,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)

    x = DarknetConv2D_BN_Leaky(512,x)
    x = layers.MaxPooling2D(pool_size=(2, 2), strides=(1, 1), padding='same')(x)

    x = DarknetConv2D_BN_Leaky(1024,x)

    x = DarknetConv2D_BN_Leaky(512,x)

    x = layers.Conv2D(len_detection_vector, (1, 1), strides=1, padding='same', use_bias=False)(x)
    outputs = layers.BatchNormalization(name='predict_conv')(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="tiny_yolo_v2")
    return model

def tiny_yolo_v2_transfer_learning_model(transfer_learning_model, weights_path):
    """
    Update transfer learning model with weights from given path.

    Args:
        transfer_learning_model (tf.keras.Model): Transfer learning model to update.
        weights_path (str): Path to weights.

    Returns:
        transfer_learning_model (tf.keras.Model): Updated transfer learning model.
    """
    old_model = tf.keras.models.load_model(weights_path)
    for i,l in enumerate(old_model.layers[:-1]):
        transfer_learning_model.layers[i].set_weights(l.get_weights())
        #transfer_learning_model.layers[i].trainable =False    
    return transfer_learning_model

def get_tiny_yolo_v2_train_model(anchors, num_classes, weights_path=None, frozen_layers=None,network_stride = 16):
    """
    Create the training model for YOLOv2.

    Args:
        anchors: A list of anchor boxes as floats.
        num_classes: An integer representing the number of classes.
        weights_path: A string representing the path to the pre-trained weights file. Default is None.

    Returns:
        A Keras Model object representing the YOLOv2 training model.
    """
    num_anchors = len(anchors)
    y_true_input = Input(shape=(None, None, num_anchors, 6))
    input_tensor = Input(shape=(None, None, 3), batch_size=None, name='image_input')
    if network_stride == 32 :
        model_body = tiny_yolo_v2_body(input_tensor, num_anchors, num_classes)
    else:
        model_body = st_yolo_lc_v1_body(input_tensor, num_anchors, num_classes)

    if weights_path:
        model_body = tiny_yolo_v2_transfer_learning_model(model_body, weights_path)

    if frozen_layers:
        set_frozen_layers(model_body, frozen_layers=frozen_layers)

    model_loss, _, _, _ = Lambda(tiny_yolo_v2_loss, name='tiny_yolo_v2_loss',arguments={'anchors': anchors, 'num_classes': num_classes, 'network_stride': network_stride})([model_body.output, y_true_input])

    model = Model([model_body.input, y_true_input], model_loss)

    return model

def tiny_yolo_v2_model(cfg):
    """
    Create a YOLOv2 model for resuming training from a saved checkpoint.

    Args:
        cfg (DictConfig): The configuration object.
    Returns:
        A Keras Model object representing the YOLOv2 model.
    """
    classes = cfg.dataset.class_names
    num_classes = len(classes)
    anchors_list = cfg.postprocessing.yolo_anchors
    anchors = np.array(anchors_list).reshape(-1, 2)
    frozen_layers = cfg.training.frozen_layers
    network_stride = cfg.postprocessing.network_stride

    if cfg.training.model.pretrained_weights:
        print("[INFO] : Training Initialized with : coco weights")
        if cfg.training.model.pretrained_weights == "coco" and cfg.general.model_type == "tiny_yolo_v2":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(os.path.dirname(current_dir))
            weights_dir = os.path.join(parent_dir, "pretrained_models/tiny_yolo_v2/Public_pretrainedmodel_public_dataset/coco_2017/tiny_yolo_v2_416")
            pretrained_weights = os.path.join(weights_dir, "tiny_yolo_v2_416.h5")
        else:
            pretrained_weights = cfg.training.model.pretrained_weights
            
        model = get_tiny_yolo_v2_train_model(anchors, num_classes, weights_path = pretrained_weights, frozen_layers = frozen_layers, network_stride = network_stride)
    elif cfg.general.model_path and Path(cfg.general.model_path).suffix == '.h5':
        print("[INFO] : Training Initialized with : {}".format(cfg.general.model_path))
        model = get_tiny_yolo_v2_train_model(anchors, num_classes, frozen_layers = frozen_layers, network_stride = network_stride)
        model_path = cfg.general.model_path
        old_model = tf.keras.models.load_model(model_path)
        model.set_weights(old_model.get_weights())   
    else:
        model = get_tiny_yolo_v2_train_model(anchors, num_classes, frozen_layers = frozen_layers, network_stride = network_stride)
    return model
