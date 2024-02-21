# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import sys
import os
from pathlib import Path
from hydra.core.hydra_config import HydraConfig
from munch import DefaultMunch
from omegaconf import DictConfig
import numpy as np
import tensorflow as tf
from typing import List, Dict, Generator
import lr_schedulers

sys.path.append(os.path.abspath('../utils'))
sys.path.append(os.path.abspath('../evaluation'))
sys.path.append(os.path.abspath('../../../common'))

from train_utils import *
from utils import model_summary
from load_models import get_model
from train_utils import LRTensorBoard, set_frozen_layers, get_optimizer, get_callbacks
from evaluate import evaluate
from loss import ssd_focal_loss


def train(cfg: DictConfig = None,
          train_ds: Dict = None, valid_ds: Dict = None, test_ds: Dict = None,
          train_gen: Generator = None, valid_gen: Generator = None) -> str:
    """
    Trains the model with the given configuration and datasets.

    If no test set is provided, the validation set is used instead
    to calculate the mAP.

    Args:
        cfg (DictConfig): configuration dictionary.
        train_ds (Dict): training dataset.
        valid_ds (Dict): validation dataset.
        test_ds (Dict): test dataset (optional).
        train_gen (generator): training generator.
        valid_gen (generator): validation generator.

    Returns:
        str: The trained model path.
    """

    output_dir = HydraConfig.get().runtime.output_dir
    saved_models_dir = cfg.general.saved_models_dir

    num_train_samples = len(train_ds["train_images_filename_ds"])
    num_valid_samples = len(valid_ds["val_images_filename_ds"])

    print("Dataset stats:")
    print("  classes:", len(cfg.dataset.class_names))
    print("  training samples:", num_train_samples)
    print("  validation samples:", num_valid_samples)
    if test_ds:
        print("  Test samples:", len(test_ds["test_images_filename_ds"]))
    else:
        print("  Test samples: None")
    
    batch_size = cfg.training.batch_size
    epochs = cfg.training.epochs

    saved_models_path = os.path.join(output_dir, saved_models_dir)

    os.mkdir(saved_models_path)

    if cfg.general.model_path:
        if cfg.general.model_path[-15:] == 'best_weights.h5': # resume training from
            print("[INFO] Resuming training from weights ...")
            inference_model, training_model, _ = get_model(cfg, class_names=cfg.dataset.class_names)
            training_model.load_weights(cfg.general.model_path)

        else: # bring your own model
            print("[INFO] Importation of the model ...")
            inference_model = tf.keras.models.load_model(cfg.general.model_path, compile=False)
            tmoutput        = tf.keras.layers.Concatenate(axis=2, name='predictions')(inference_model.outputs)
            training_model  = tf.keras.models.Model(inputs=inference_model.input,outputs=tmoutput)

    elif cfg.training.model:
        inference_model, training_model, _ = get_model(cfg, class_names=cfg.dataset.class_names)

        # Save the inference model and the fmap sizes.
        # We will need it when resuming a training.
        #inference_model.save(os.path.join(saved_models_path, "inference_model.h5"))


   # Freeze layers if requested
    training_model.trainable = True
    if cfg.training.frozen_layers and cfg.training.frozen_layers != "None":
        set_frozen_layers(training_model, frozen_layers=cfg.training.frozen_layers)

    else:
        print('[ERROR] Cannot execute training : yaml file missing model_path or training.model informations')
        # We are resuming the training.
        #print("[INFO] Resuming training from", cfg.training.resume_training_from)
        # models_dir = os.path.join(cfg.training.resume_training_from, cfg.general.saved_models_dir)
        # inference_model = tf.keras.models.load_model(os.path.join(models_dir, "inference_model.h5"), compile=False)
        # training_model = tf.keras.models.load_model(os.path.join(models_dir, "last_train_model.h5"), compile=False)

    model_summary(training_model)

    # Compile the training model
    training_model.compile(optimizer=get_optimizer(cfg.training.optimizer), loss=ssd_focal_loss())

    callbacks = get_callbacks(callbacks_dict=cfg.training.callbacks,
                              model_type=cfg.general.model_type,
                              output_dir=output_dir,
                              saved_models_dir=saved_models_dir,
                              logs_dir=cfg.general.logs_dir)

    # Train the model
    print("[INFO] Starting training...")
    training_model.fit(train_gen,
                       steps_per_epoch=int(num_train_samples / batch_size),
                       epochs=epochs,
                       validation_data=valid_gen,
                       callbacks=callbacks,
                       validation_steps=int(num_valid_samples / batch_size))


    best_weights_path = Path(output_dir, saved_models_dir, "best_weights.h5")

    best_model_path   = Path(output_dir, saved_models_dir, "best_model.h5")

    inference_model.load_weights(best_weights_path)

    inference_model.save(best_model_path)

    os.remove(best_weights_path)

    evaluate(cfg, valid_ds=valid_ds, test_ds=test_ds, model_path=best_model_path)

    return best_model_path
