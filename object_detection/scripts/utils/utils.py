# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import ssl

import mlflow
import tensorflow as tf
from munch import DefaultMunch
from omegaconf import OmegaConf
from tensorflow import keras

import os
import random

import load_models
import numpy as np
from anchor_boxes_utils import gen_anchors, get_sizes_ratios
from common_benchmark import *
from callbacks import *
from datasets import *
from datasets import generate, load_data, parse_data
from header_file_generator import *
from hydra.core.hydra_config import HydraConfig
from loss import ssd_focal_loss
from metrics_utils import calculate_float_map, calculate_quantized_map, relu6
from quantization import *
from tensorflow.keras.utils import get_custom_objects
ssl._create_default_https_context = ssl._create_unverified_context


# Set seeds
def setup_seed(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)  # tf cpu fix seed


def get_config(cfg):
    config_dict = OmegaConf.to_container(cfg)
    configs = DefaultMunch.fromDict(config_dict)
    return configs


def mlflow_ini(cfg):
    mlflow.set_tracking_uri(cfg.mlflow.uri)
    mlflow.set_experiment(cfg.general.project_name)
    mlflow.tensorflow.autolog(log_models=False)


def get_optimizer(cfg):

    if cfg.train_parameters.optimizer.lower() == "SGD".lower():
        optimizer = keras.optimizers.SGD(learning_rate=cfg.train_parameters.initial_learning)
    elif cfg.train_parameters.optimizer.lower() == "RMSprop".lower():
        optimizer = keras.optimizers.RMSprop(learning_rate=cfg.train_parameters.initial_learning)
    elif cfg.train_parameters.optimizer.lower() == "Adam".lower():
        optimizer = keras.optimizers.Adam(learning_rate=cfg.train_parameters.initial_learning, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
    else:
        optimizer = keras.optimizers.Adam(learning_rate=cfg.train_parameters.initial_learning)
    return optimizer


def inc_gpu_mode():
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        except RuntimeError as e:
            print(e)


def train(cfg):
    # Get SSD model and feature map sizes
    model, fmap_sizes = load_models.get_model(cfg)
    model.summary()

    # get loss
    loss = ssd_focal_loss()

    # get optimizer
    optimizer = get_optimizer(cfg)

    # get callbacks
    callbacks = get_callbacks(cfg)

    # compile the model
    model.compile(optimizer=optimizer, loss=loss)

    # Estimate the model footprints
    if cfg.quantization.quantize:
        print("[INFO] : Estimating the model footprints...")
        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            TFLite_PTQ_quantizer(cfg, model, fake=True)
            model_path = os.path.join(HydraConfig.get().runtime.output_dir, "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))
        else:
            raise TypeError("Quantizer and quantization type not supported yet!")
    else:
        model_path = os.path.join(HydraConfig.get().runtime.output_dir, "{}/{}".format(cfg.general.saved_models_dir, "best_model.h5"))
        model.save(model_path)

    # Evaluate model footprints with STM32Cube.AI
    if cfg.stm32ai.footprints_on_target:
        print("[INFO] : Establishing a connection to STM32Cube.AI Developer Cloud to launch the model benchmark on STM32 target...")
        try:
            output_analyze = Cloud_analyze(cfg, model_path)
            if output_analyze == 0:
                raise Exception("Connection failed, Offline benchmark will be launched.")
        except Exception as e:
            output_analyze = 0
            print("[FAIL] :", e)
            print("[INFO] : Offline benchmark launched...")
            benchmark_model(cfg, model_path)

    else:
        benchmark_model(cfg, model_path)

    # train the model
    tf.print("Loading Training ... ")
    train_annotations = parse_data(cfg.dataset.training_path)
    train_images_filename_list, train_gt_labels_list, num_train_samples = load_data(train_annotations)

    tf.print("Loading Validation ... ")
    if cfg.dataset.validation_path is not None:
        val_annotations = parse_data(cfg.dataset.validation_path)
        val_images_filename_list, val_gt_labels_list, num_val_samples = load_data(val_annotations)
    else:
        val_annotations = parse_data(cfg.dataset.training_path)
        val_images_filename_list, val_gt_labels_list, num_val_samples = load_data(val_annotations)

    n_epochs = cfg.train_parameters.training_epochs
    batch_size = cfg.train_parameters.batch_size
    steps_per_epoch = int(num_train_samples / batch_size)
    fmap_channels = 32
    n_classes = len(cfg.dataset.class_names)
    img_width = cfg.model.input_shape[0]
    img_height = cfg.model.input_shape[1]
    img_channels = cfg.model.input_shape[2]
    sizes_h, ratios_h = get_sizes_ratios(cfg)

    # Training data generator
    train_gen = generate(cfg, train_images_filename_list, train_gt_labels_list, batch_size, shuffle=True, augmentation=cfg.data_augmentation.augment,
                         fmap_sizes=fmap_sizes, img_width=img_width, img_height=img_height, sizes=sizes_h, ratios=ratios_h,
                         n_classes=n_classes)
    # Validation data generator
    # pos_iou_threshold should be >=0.5, neg_iou_limit<=0.5, usually 0.5 for both
    val_gen = generate(cfg, val_images_filename_list, val_gt_labels_list, batch_size, shuffle=False, augmentation=False,
                       fmap_sizes=fmap_sizes, img_width=img_width, img_height=img_height, sizes=sizes_h, ratios=ratios_h,
                       n_classes=n_classes)

    print("[INFO] : Starting training...")
    history = model.fit(train_gen,
                        steps_per_epoch=steps_per_epoch,
                        epochs=n_epochs,
                        validation_data=val_gen,
                        callbacks=callbacks,
                        validation_steps=int(num_val_samples / batch_size))

    # evaluate the float model on test set
    best_model = tf.keras.models.load_model(os.path.join(HydraConfig.get().runtime.output_dir, cfg.general.saved_models_dir+'/'+"best_model.h5"),
                                            custom_objects={'gen_anchors': gen_anchors, 'relu6': relu6, '_loss': loss})

    # generate Ap curves of the float model
    tf.print('[INFO] Evaluating the float model ...')
    mAP = calculate_float_map(cfg, best_model)
    mlflow.log_metric("float_model_mAP", mAP)

    # Quantize the model with training data
    if cfg.quantization.quantize:
        print("[INFO] : Quantizing the model ... This might take few minutes ...")

        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            TFLite_PTQ_quantizer(cfg, best_model, fake=False)
            quantized_model_path = os.path.join(HydraConfig.get(
            ).runtime.output_dir, "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))

            # Generating C model
            if cfg.stm32ai.footprints_on_target:
                try:
                    if output_analyze != 0:
                        output_benchmark = Cloud_benchmark(cfg, quantized_model_path, output_analyze)
                        if output_benchmark == 0:
                            raise Exception("Connection failed, generating C model using local STM32Cube.AI.")
                    else:
                        raise Exception("Connection failed, generating C model using local STM32Cube.AI.")
                except Exception as e:
                    print("[FAIL] :", e)
                    print("[INFO] : Offline C code generation launched...")
                    benchmark_model(cfg, quantized_model_path)
            else:
                benchmark_model(cfg, quantized_model_path)

            # Evaluate the quantized model
            if cfg.quantization.evaluate:
                tf.print('[INFO] Evaluating the quantized model ...')
                mAP = calculate_quantized_map(cfg, quantized_model_path)
                mlflow.log_metric("int_model_mAP", mAP)

        else:
            raise TypeError("Quantizer and quantization type not supported yet!")

        # Generate Config.h for C embedded application
        gen_h_user_file(cfg, quantized_model_path)

    # record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()
