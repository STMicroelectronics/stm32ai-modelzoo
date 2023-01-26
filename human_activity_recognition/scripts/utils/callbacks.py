# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import math
import os

import tensorflow as tf
from hydra.core.hydra_config import HydraConfig


def SchedulerExponential():
    def scheduler(epoch, lr):
        initial_learningrate = lr
        if epoch < 10:
            return initial_learningrate
        else:
            return initial_learningrate * tf.math.exp(-0.001 * epoch)
    return tf.keras.callbacks.LearningRateScheduler(scheduler)


def SchedulerCosine():
    def scheduler(epoch, lr):
        initial_learningrate = lr
        if epoch < 10:
            return initial_learningrate
        else:
            decay_steps = 1000
            alpha = 0.00001
            step = min(epoch, decay_steps)
            cosine_decay = 0.5 * (1 + math.cos(math.pi * step / decay_steps))
            decayed = (1 - alpha) * cosine_decay + alpha
            return initial_learningrate * decayed
    return tf.keras.callbacks.LearningRateScheduler(scheduler)


def SchedulerConstant():
    def scheduler(epoch, lr):
        return lr
    return tf.keras.callbacks.LearningRateScheduler(scheduler)


def get_callbacks(cfg):
    callbacks = []

    if cfg.tf_train_parameters.learning_rate_scheduler == 'ReduceLROnPlateau':
        callbacks.append(tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_accuracy', factor=0.1, patience=5, min_lr=0.000001))
    elif cfg.tf_train_parameters.learning_rate_scheduler == 'Exponential':
        callbacks.append(SchedulerExponential())
    elif cfg.tf_train_parameters.learning_rate_scheduler == 'Cosine':
        callbacks.append(SchedulerCosine())
    elif cfg.tf_train_parameters.learning_rate_scheduler == 'Constant':
        callbacks.append(SchedulerConstant())

    callbacks.append(tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy', patience=20, restore_best_weights=True, verbose=2))
    checkpoint_filepath = os.path.join(HydraConfig.get(
    ).runtime.output_dir, cfg.general.saved_models_dir+'/'+"best_model.h5")
    callbacks.append(tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_filepath,
                     save_weights_only=False, monitor='val_accuracy', mode='max', save_best_only=True))
    callbacks.append(tf.keras.callbacks.TensorBoard(log_dir=os.path.join(
        HydraConfig.get().runtime.output_dir, cfg.general.logs_dir)))

    return callbacks
