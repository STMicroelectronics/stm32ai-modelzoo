# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
import os
from hydra.core.hydra_config import HydraConfig
import math

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
            alpha=0.00001
            step = min(epoch, decay_steps)
            cosine_decay = 0.5 * (1 + math.cos(math.pi * step / decay_steps))
            decayed = (1 - alpha) * cosine_decay + alpha
            return initial_learningrate * decayed
    return tf.keras.callbacks.LearningRateScheduler(scheduler)

def SchedulerConstant():
    def scheduler(epoch, lr):
            return lr
    return tf.keras.callbacks.LearningRateScheduler(scheduler)

# Define TensorBoard callback
class LRTensorBoard(tf.keras.callbacks.TensorBoard):

    def __init__(self, log_dir, **kwargs):
        super().__init__(log_dir, **kwargs)
        self.lr_writer = tf.summary.create_file_writer(self.log_dir + '/metrics')

    def on_epoch_end(self, epoch, logs=None):
        lr = getattr(self.model.optimizer, 'lr', None)
        with self.lr_writer.as_default():
            summary = tf.summary.scalar('learning_rate', lr, epoch)

        super().on_epoch_end(epoch, logs)

    def on_train_end(self, logs=None):
        super().on_train_end(logs)
        self.lr_writer.close()

def get_callbacks(cfg):
    callbacks=[]

    LR_list = ['ReduceLROnPlateau', 'Exponential', 'Cosine', 'Constant']
    # Learning rate scheduler callback selection
    if cfg.train_parameters.learning_rate_scheduler.lower() == 'ReduceLROnPlateau'.lower():
        callbacks.append(tf.keras.callbacks.ReduceLROnPlateau(monitor='val_accuracy', factor=0.1, patience=15, mode='max', min_lr=0.000001))
    elif cfg.train_parameters.learning_rate_scheduler.lower() == 'Exponential'.lower():
        callbacks.append(SchedulerExponential())
    elif cfg.train_parameters.learning_rate_scheduler.lower() == 'Cosine'.lower():
        callbacks.append(SchedulerCosine())
    elif cfg.train_parameters.learning_rate_scheduler.lower() == 'Constant'.lower():
        callbacks.append(SchedulerConstant())
    else:
        raise TypeError('{}  is not a valid Learning rate Scheduler, available options : {}'.format(cfg.train_parameters.learning_rate_scheduler, LR_list))


    # EarlyStopping callback
    callbacks.append(tf.keras.callbacks.EarlyStopping(monitor='val_accuracy',
                                                      mode='max',
                                                      patience=cfg.train_parameters.patience,
                                                      restore_best_weights=cfg.train_parameters.restore_best_weights,
                                                      verbose=2))

    # Checkpoints callback
    checkpoint_filepath = os.path.join(HydraConfig.get().runtime.output_dir,cfg.general.saved_models_dir+'/'+"best_model.h5")
    callbacks.append(tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_filepath,save_weights_only=False,monitor='val_accuracy',mode='max',save_best_only=True))

    # Tensorboard callback
    logdir = os.path.join(HydraConfig.get().runtime.output_dir,cfg.general.logs_dir)
    callbacks.append(LRTensorBoard(logdir))

    return callbacks