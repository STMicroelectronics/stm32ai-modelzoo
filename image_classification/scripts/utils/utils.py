# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
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

ssl._create_default_https_context = ssl._create_unverified_context
import os
import random

import numpy as np
from hydra.core.hydra_config import HydraConfig

import load_models
from benchmark import *
from common_benchmark import *
from callbacks import *
from data_augment import *
from datasets import *
from header_file_generator import *
from quantization import *
from visualize import *
from common_visualize import *


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
    mlflow.set_tag("mlflow.runName", HydraConfig.get().runtime.output_dir.split(os.sep)[-1])
    mlflow.tensorflow.autolog(log_models=False)


def get_optimizer(cfg):
    if cfg.train_parameters.optimizer.lower() == "SGD".lower():
        optimizer = keras.optimizers.SGD(learning_rate=cfg.train_parameters.initial_learning)
    elif cfg.train_parameters.optimizer.lower() == "RMSprop".lower():
        optimizer = keras.optimizers.RMSprop(learning_rate=cfg.train_parameters.initial_learning)
    elif cfg.train_parameters.optimizer.lower() == "Adam".lower():
        optimizer = keras.optimizers.Adam(learning_rate=cfg.train_parameters.initial_learning)
    else:
        optimizer = keras.optimizers.Adam(learning_rate=cfg.train_parameters.initial_learning)
    return optimizer


def get_loss(cfg):
    num_classes = len(cfg.dataset.class_names)
    if num_classes > 2:
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)
    return loss


def train(cfg):
    # Get model
    model = load_models.get_model(cfg)
    model.summary()

    # Get loss
    loss = get_loss(cfg)

    # Get optimizer
    optimizer = get_optimizer(cfg)

    # Get callbacks
    callbacks = get_callbacks(cfg)

    # Get data augmentation
    data_augmentation, augment = get_data_augmentation(cfg)

    # Get pre_processing
    pre_process = preprocessing(cfg)

    # Get datasets
    if cfg.dataset.name.lower() == "cifar10":
        train_ds, valid_ds = load_CIFAR_10(cfg)
    elif cfg.dataset.name.lower() == "cifar100":
        train_ds, valid_ds = load_CIFAR_100(cfg)
    elif cfg.dataset.name.lower() == "emnist_byclass":
        train_ds, valid_ds = load_EMNIST_Byclass(cfg)
    else:
        if cfg.dataset.validation_path is None:
            train_ds, valid_ds = get_train_val_ds(cfg)

        else:
            train_ds = get_ds(cfg.dataset.training_path, cfg, shuffle=True)
            valid_ds = get_ds(cfg.dataset.validation_path, cfg)

    # Create augmented model with data_augmentation + preprocessing layers + model
    if augment:
        augmented_model = tf.keras.models.Sequential([data_augmentation, pre_process, model])
    else:
        augmented_model = tf.keras.models.Sequential([pre_process, model])
    augmented_model._name = "Augmented_model"
    augmented_model.build((None, cfg.model.input_shape[0], cfg.model.input_shape[1], cfg.model.input_shape[2]))
    augmented_model.summary()

    # Compile the model
    augmented_model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])

    # Estimate the model footprints
    if cfg.quantization.quantize:
        print("[INFO] : Estimating the model footprints...")
        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            TFLite_PTQ_quantizer(cfg, model, train_ds=None, fake=True)
            model_path = os.path.join(HydraConfig.get().runtime.output_dir,
                                      "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))
        else:
            raise TypeError("Quantizer and quantization type not supported yet!")
    else:
        model_path = os.path.join(HydraConfig.get().runtime.output_dir,
                                  "{}/{}".format(cfg.general.saved_models_dir, "best_model.h5"))
        model.save(model_path)

    # Evaluate model footprints with STM32Cube.AI
    if cfg.stm32ai.footprints_on_target:
        print("[INFO] : Establishing a connection to STM32Cube.AI Developer Cloud to launch the model benchmark on STM32 target...")
        try:
            output_analyze = Cloud_analyze(cfg, model_path)
            if output_analyze == 0:
                raise Exception(
                    "Connection failed, using local STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
        except Exception as e:
            output_analyze = 0
            print("[FAIL] :", e)
            print("[INFO] : Offline benchmark launched...")
            benchmark_model(cfg, model_path)

    else:
        benchmark_model(cfg, model_path)

    # Train the model
    print("[INFO] : Starting training...")
    history = augmented_model.fit(train_ds, validation_data=valid_ds, callbacks=callbacks,
                                  epochs=cfg.train_parameters.training_epochs)
    # Visualize training curves
    vis_training_curves(history, cfg)

    # Evaluate the float model on test set
    if cfg.dataset.test_path is None:
        test_ds = valid_ds
    else:
        test_ds = get_ds(cfg.dataset.test_path, cfg)
    test_dataset = test_ds.map(lambda x, y: (pre_process(x), y))

    # Load best trained model w/o preprocessing layers
    best_model = augmented_model.layers[-1]
    best_model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    best_model.save(
        os.path.join(HydraConfig.get().runtime.output_dir, cfg.general.saved_models_dir + '/' + "best_model.h5"))

    # Generate the confusion matrix for the float model
    training_confusion_matrix(test_dataset, best_model, cfg.dataset.class_names)

    # Quantize the model with training data
    if cfg.quantization.quantize:
        print("[INFO] : Quantizing the model ... This might take few minutes ...")

        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            train_ds = train_ds.map(lambda x, y: (pre_process(x), y))
            TFLite_PTQ_quantizer(cfg, best_model, train_ds, fake=False)
            quantized_model_path = os.path.join(HydraConfig.get(
            ).runtime.output_dir, "{}/{}".format(cfg.quantization.export_dir, "quantized_model.tflite"))

            # Generating C model
            if cfg.stm32ai.footprints_on_target:
                try:
                    if output_analyze != 0:
                        output_benchmark = Cloud_benchmark(cfg, quantized_model_path, output_analyze)
                        if output_benchmark == 0:
                            raise Exception(
                                "Connection failed, using local STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
                    else:
                        raise Exception(
                            "Connection failed, using local STM32Cube.AI. Link to download https://www.st.com/en/embedded-software/x-cube-ai.html")
                except Exception as e:
                    print("[FAIL] :", e)
                    print("[INFO] : Offline benchmark launched...")
                    benchmark_model(cfg, quantized_model_path)
            else:
                benchmark_model(cfg, quantized_model_path)

            # Evaluate the quantized model
            if cfg.quantization.evaluate:
                q_acc = evaluate_TFlite_quantized_model(quantized_model_path, test_dataset, cfg)
                mlflow.log_metric("int_test_acc", q_acc)

        else:
            raise TypeError("Quantizer and quantization type not supported yet!")

        # Generate Config.h for C embedded application
        gen_h_user_file(cfg, quantized_model_path)

    # Record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()
