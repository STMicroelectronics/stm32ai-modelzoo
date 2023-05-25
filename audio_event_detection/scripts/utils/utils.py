# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/



import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import tensorflow as tf
import mlflow
import random
import os
import numpy as np
import load_models
from omegaconf import OmegaConf
from munch import DefaultMunch
from tensorflow import keras
from quantization import TFLite_PTQ_quantizer
from benchmark import evaluate_TFlite_quantized_model
from data_augment import get_data_augmentation
from datasets import _esc10_csv_to_tf_dataset, load_ESC_10, load_custom_esc_like_multiclass
from visualize import _compute_confusion_matrix, _plot_confusion_matrix
from common_visualize import vis_training_curves
from callbacks import get_callbacks
from preprocessing import preprocessing
from hydra.core.hydra_config import HydraConfig
from header_file_generator import gen_h_user_file
from evaluation import _aggregate_predictions, compute_accuracy_score

from sklearn.metrics import accuracy_score
from common_benchmark import analyze_footprints, Cloud_analyze, Cloud_benchmark, benchmark_model
from lookup_tables_generator import generate_mel_LUT_files


# Set seeds
def setup_seed(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)  
    np.random.seed(seed) 
    tf.random.set_seed(seed)  # tf cpu fix seed
    
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(1)

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
        optimizer = keras.optimizers.Adam(learning_rate=cfg.train_parameters.initial_learning)
    else:
        optimizer = keras.optimizers.Adam(learning_rate=cfg.train_parameters.initial_learning)
    return optimizer


def get_loss(cfg):
    num_classes = len(cfg.dataset.class_names)
    if cfg.model.multi_label:
        raise NotImplementedError("Multi-label classification not implemented yet, but will be in a future update.")
    elif num_classes > 2:
        loss = tf.keras.losses.CategoricalCrossentropy(from_logits=False)
    else:
        loss = tf.keras.losses.BinaryCrossentropy(from_logits=False)
    return loss


def train(cfg):
    #get model
    model = load_models.get_model(cfg)
    print("[INFO] Model summary")
    model.summary()

    #get loss
    loss = get_loss(cfg)

    #get optimizer
    optimizer = get_optimizer(cfg)

    #get callbacks
    callbacks = get_callbacks(cfg)

    #get data augmentation
    data_augmentation,augment = get_data_augmentation(cfg)

    #get pre_processing
    #pre_process = preprocessing(cfg)
    _, _ = preprocessing(cfg)


    #get datasets

    if cfg.dataset.name.lower()=="esc10" :
        train_ds, valid_ds, test_ds, clip_labels = load_ESC_10(cfg)
    elif cfg.dataset.name.lower()=="custom" and not cfg.model.multi_label:
        train_ds, valid_ds, test_ds, clip_labels = load_custom_esc_like_multiclass(cfg)
    elif cfg.dataset.name.lower()=="custom" and cfg.model.multi_label:
        raise NotImplementedError("Multilabel support not implemented yet !")
    else:
        raise NotImplementedError("Please choose a valid dataset ('esc10' or 'custom')")

    # Apply Data aug
    if augment:
        augmented_model = tf.keras.models.Sequential([data_augmentation, model])
        augmented_model._name = "Augmented_model"
    else:
        augmented_model = model
        augmented_model._name = "Model"

    if cfg.model.expand_last_dim:
        augmented_model.build((None, cfg.model.input_shape[0], cfg.model.input_shape[1], 1))
    else:
        augmented_model.build((None, cfg.model.input_shape[0], cfg.model.input_shape[1]))
    
    print("[INFO] Augmented model summary")
    augmented_model.summary()

    # Compile the model
    augmented_model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    
    print("[INFO] Model sucessfully compiled")


    if cfg.quantization.quantize:
        print("[INFO] : Estimating the model footprints...")
        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            TFLite_PTQ_quantizer(cfg, model, train_ds=None, fake=True)
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

    
    #train the model
    print("[INFO] : Starting training...")
    history = augmented_model.fit(train_ds, validation_data=valid_ds, callbacks = callbacks, 
    epochs=cfg.train_parameters.training_epochs)

    # Visualize training curves
    vis_training_curves(history,cfg)
    
    
    #evaluate the float model on test set

    
    # Load best trained model w/o data augmentation layers
    best_model = augmented_model.layers[-1]
    best_model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    best_model.save(
        os.path.join(HydraConfig.get().runtime.output_dir, cfg.general.saved_models_dir + '/' + "best_model.h5"))

    X_test, y_test = test_ds[0], test_ds[1]

    test_preds = best_model.predict(X_test)
    aggregated_preds = _aggregate_predictions(preds=test_preds,
                                              clip_labels=clip_labels,
                                              is_multilabel=cfg.model.multi_label,
                                              is_truth=False)
    aggregated_truth = _aggregate_predictions(preds=y_test,
                                              clip_labels=clip_labels,
                                              is_multilabel=cfg.model.multi_label,
                                              is_truth=True)

    

    # generate the confusion matrix for the float model
    patch_level_accuracy = compute_accuracy_score(y_test, test_preds,
                                                  is_multilabel=cfg.model.multi_label)
    print("[INFO] : Patch-level accuracy on test set : {}".format(patch_level_accuracy))
    clip_level_accuracy = compute_accuracy_score(aggregated_truth, aggregated_preds,
                                                  is_multilabel=cfg.model.multi_label)
    print("[INFO] : Clip-level accuracy on test set : {}".format(clip_level_accuracy))

    # Log accuracies in MLFLOW
    mlflow.log_metric("float_patch_test_acc", patch_level_accuracy)
    mlflow.log_metric("float_clip_test_acc", clip_level_accuracy)


    patch_level_confusion_matrix = _compute_confusion_matrix(y_test, test_preds,
                                                               is_multilabel=cfg.model.multi_label)
    clip_level_confusion_matrix = _compute_confusion_matrix(aggregated_truth, aggregated_preds,
                                                              is_multilabel=cfg.model.multi_label)

    _plot_confusion_matrix(patch_level_confusion_matrix,
                           class_names=cfg.dataset.class_names,
                           title="Patch-level CM",
                           test_accuracy=patch_level_accuracy)

    _plot_confusion_matrix(clip_level_confusion_matrix,
                           class_names=cfg.dataset.class_names,
                           title="Clip-level CM",
                           test_accuracy=clip_level_accuracy)
    
    #quantize the model with training data
    if cfg.quantization.quantize:
        print("[INFO] : Quantizing the model ... This might take few minutes ...")

        if cfg.data_augmentation.VolumeAugment:
            print("Applying Volume augmentation to quantization dataset")
            map_fn = lambda x, y : (data_augmentation(x), y)
            train_ds = train_ds.map(map_fn)

        if cfg.quantization.quantizer == "TFlite_converter" and cfg.quantization.quantization_type == "PTQ":
            TFLite_PTQ_quantizer(cfg, best_model, train_ds, fake=False)
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

            #evaluate the quantized model
            if cfg.quantization.evaluate ==True:
                q_patch_level_acc, q_clip_level_acc = evaluate_TFlite_quantized_model(quantized_model_path,X_test, y_test, clip_labels, cfg)
                mlflow.log_metric("int_patch_test_acc", q_patch_level_acc)
                mlflow.log_metric("int_clip_test_acc", q_clip_level_acc)

        else:
            raise TypeError("Quantizer and quantization type not supported yet!")

        # Generate Config.h for C embedded application
        print("Generating C header file for Getting Started...")
        gen_h_user_file(cfg)
        print("Done")
        # Generate LUT files
        print("Generating C look-up tables files for Getting Started...")
        generate_mel_LUT_files(cfg)
        print("Done")


    #record the whole hydra working directory to get all infos
    mlflow.log_artifact(HydraConfig.get().runtime.output_dir)
    mlflow.end_run()

