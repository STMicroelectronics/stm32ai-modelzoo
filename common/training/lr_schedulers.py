# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

"""
References:
----------
Some of the callbacks in this package were inspired by the optimizer
schedules of Tensorflow:

    Various learning rate schedule functions
    The Tensorflow Authors
    Copyright (c) 2015

This includes LRCosineDecayRestarts, LRPolynomialDecayRestarts and LRPiecewiseConstantDecay.

Link to the source code:
    https://github.com/keras-team/keras/blob/v2.12.0/keras/optimizers/schedules/learning_rate_schedule.py#L577-L670

"""

import os
import sys
import math
import tensorflow as tf
#from tensorflow.keras import backend
from keras.src import backend
import numpy as np

      
def _check_scheduler_arguments(args, arg_names, scheduler_name):      
    for i in range(len(args)):
        if args[i] is None:
            raise ValueError(
                f"\nLearning rate scheduler `{scheduler_name}`: "
                f"missing argument `{arg_names[i]}`")

def get_scheduler_names():
    """
    This function returns the names of the learning rate schedulers
    available in this package (this does not include the Tensorflow
    LearningRateScheduler callback). All the schedulers are Keras
    custom callbacks.
    If a new scheduler is made available, it must be addedv to this list.
    """
    return ["LRLinearDecay", "LRExponentialDecay", "LRStepDecay",
            "LRCosineDecay", "LRWarmupCosineDecay", "LRCosineDecayRestarts",
            "LRPolynomialDecay", "LRPolynomialDecayRestarts",
            "LRPiecewiseConstantDecay"]

def generic_on_epoch_begin(self, epoch, logs=None):
    """
    This function is a generic implementation for the on_epoch_begin method of all LR schedulers.
    """
    if not hasattr(self.model.optimizer, "learning_rate"):
        raise ValueError('\nOptimizer must have a "learning_rate" attribute.')
    try:  # new API
        learning_rate = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )
        learning_rate = self.schedule(epoch, learning_rate)
    except TypeError:  # Support for old API for backward compatibility
        learning_rate = self.schedule(epoch)
    if not isinstance(learning_rate, (float, np.float32, np.float64)):
        raise ValueError(
            "The output of the `schedule` function should be a float. "
            f"Got: {learning_rate}"
        )
    self.model.optimizer.learning_rate = learning_rate
    if self.verbose > 0:
        print("\nEpoch {}: {} setting "
              "learning rate to {:.4e}.".format(epoch + 1, self.name, learning_rate))


class LRLinearDecay(tf.keras.callbacks.Callback):
    """
    This callback applies a 2 phases decay function to the learning rate:
    1. Hold phase: the learning rate is held constant at its initial value
       for a number of epochs.
    2. Decay phase: the learning rate decays linearly over a number of epochs.

    The learning rate is updated at the beginning of each epoch.

    Arguments:
        initial_lr:
            A float, the initial learning rate.
        hold_steps:
            An integer, the number of epochs to hold the learning rate
            constant at `initial_lr` before starting to decay.
        decay_steps:
            An integer, the number of steps to decay linearly over.
        end_lr:
            A float, the end value of the learning rate.
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    Example usage:
        epochs = 250
        lr_scheduler = LRLinearDecay(
                            initial_lr=0.01,
                            hold_steps=40,
                            decay_steps=160
                            end_lr=0.00001)
    """

    def __init__(self,
                 initial_lr=None,
                 hold_steps=None,
                 decay_steps=None,
                 end_lr=None,
                 verbose=0):
        super().__init__()
        self.name = "LRLinearDecay"
        _check_scheduler_arguments(
                    [initial_lr, hold_steps, decay_steps, end_lr],
                    ["initial_lr", "hold_steps", "decay_steps", "end_lr"],
                    self.name)  
        self.initial_lr = initial_lr
        self.hold_steps = hold_steps
        self.decay_steps = decay_steps
        self.end_lr = end_lr
        self.verbose = verbose

    def schedule(self, epoch, lr=None):
        if epoch < self.hold_steps - 1:
            lr = self.initial_lr
        elif epoch >= self.hold_steps + self.decay_steps:
            lr = self.end_lr
        else:
            epoch = epoch - self.hold_steps + 1
            lr = ((self.end_lr - self.initial_lr) / self.decay_steps) * epoch + self.initial_lr
        return lr

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRExponentialDecay(tf.keras.callbacks.Callback):
    """
    This callback applies a 2 phases decay function to the learning rate:
    1. Hold phase: the learning rate is held constant at its initial value
       for a number of epochs.
    2. Decay phase: the learning rate decays following an exponential
       function.

    The learning rate is updated at the beginning of each epoch.

    Arguments:
        initial_lr:
            A float, the initial learning rate.
        hold_steps:
            An integer, the number of epochs to hold the learning rate
            constant at `initial_lr` before starting to decay.
        decay_rate:
            A float, the decay rate of the exponential. Increasing the value
            of `decay_rate` causes the learning rate to decrease faster.
        min_lr:
            A float, minimum value of the learning rate.
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    Example usage:
        epochs = 200
        lr_scheduler = LRExponentialDecay(
                            initial_lr=0.01,
                            hold_steps=20,
                            decay_rate=0.02,
                            min_lr=0.0001)
    """

    def __init__(self,
                 initial_lr=None,
                 hold_steps=None,
                 decay_rate=None,
                 min_lr=0.0,
                 verbose=0):
        super().__init__()
        self.name = "LRExponentialDecay"
        _check_scheduler_arguments(
                    [initial_lr, hold_steps, decay_rate, min_lr],
                    ["initial_lr", "hold_steps", "decay_rate", "min_lr"],
                    self.name)
        self.initial_lr = initial_lr
        self.hold_steps = hold_steps
        self.decay_rate = decay_rate
        self.min_lr = min_lr
        self.verbose = verbose

    def schedule(self, epoch, lr=None):
        if epoch < self.hold_steps - 1:
            lr = self.initial_lr
        else:
            epoch = epoch - self.hold_steps + 1
            lr = self.initial_lr * math.exp(-self.decay_rate * epoch)
            if lr < self.min_lr:
                lr = self.min_lr
        return lr

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRStepDecay(tf.keras.callbacks.Callback):
    """
    This callback applies a staircase decay function with an exponential
    trend to the learning rate.

    The learning rate is updated at the beginning of each epoch.

    Arguments:
        initial_lr:
            A float, the initial learning rate.
        step_size:
            A positive integer, the number of epochs to hold the learning
            rate constant between two drops.
        decay_rate:
            A float, the decay rate of the exponential. Decreasing the value
            of `decay_rate` causes the learning rate to decrease faster.
        min_lr:
            A float, the minimum value of the learning rate.
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    Example usage:
        epochs = 300
        lr_scheduler = LRStepDecay(
                            initial_lr=0.01,
                            step_size=30,
                            decay_rate=0.7,
                            min_lr=0.0001)
    """

    def __init__(self, initial_lr=None, step_size=None, decay_rate=None, min_lr=0.0, verbose=0):
        super().__init__()
        self.name = "LRStepDecay"
        _check_scheduler_arguments(
                [initial_lr, step_size, decay_rate, min_lr],
                ["initial_lr", "step_size", "decay_rate", "min_lr"],
                self.name)
        self.initial_lr = initial_lr
        self.step_size = step_size
        self.decay_rate = decay_rate
        self.min_lr = min_lr
        self.verbose = verbose

    def schedule(self, epoch, lr=None):
        exp = math.floor((1 + epoch) / self.step_size)
        lr = self.initial_lr * (self.decay_rate ** exp)
        if lr < self.min_lr:
            lr = self.min_lr
        return lr

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRCosineDecay(tf.keras.callbacks.Callback):
    """
    This callback applies a 3 phases decay function to the learning rate:
    1. Hold phase: the learning rate is held constant at its initial value.
    3. Cosine decay phase: the learning rate decays over a number of epochs
    following a cosine function until it reaches its target value.
    4. On target phase: the leaning rate is held constant at its target
    value for any number of subsequent epochs.

    The learning rate is updated at the beginning of each epoch.

    Arguments:
        initial_lr:
            A float, the initial value of the learning rate.
        hold_steps:
            An integer, the number of epochs to hold the learning rate
            constant at `initial_lr` before starting to decay.
        decay_steps:
            An integer, the number of steps to decay over following
            a cosine function.
        end_lr:
            A float, the learning rate value reached at the end of the
            cosine decay phase. The learning rate is held constant at
            this value for any subsequent epochs.
        verbose:
            A boolean. If set to `True`, the updated learning rate value
            is printed at the beginning of each epoch.

    About the arguments:
        - If `hold_steps` is set to 0, there is no hold phase and the learning
          rate immediately starts decaying from `initial_lr`.
        - If `hold_steps` + `decay_steps` is equal to the total number of epochs,
          the cosine decay ends at the last epoch of the training with the learning
          rate reaching `end_lr`. There is no on-target constant learning rate
          phase in this case.

    Example usage:
        epochs = 250
        lr_scheduler = LRCosineDecay(
                            initial_lr=0.01,
                            hold_steps=30,
                            decay_steps=180,
                            end_lr=0.00001)
    """

    def __init__(self, initial_lr=None, hold_steps=None, decay_steps=None, end_lr=None, verbose=0):
        super().__init__()
        self.name = "LRCosineDecay"
        _check_scheduler_arguments(
                    [initial_lr, hold_steps, decay_steps, end_lr],
                    ["initial_lr", "hold_steps", "decay_steps", "end_lr"],
                    self.name)
        self.initial_lr = initial_lr
        self.hold_steps = hold_steps
        self.decay_steps = decay_steps
        self.end_lr = end_lr
        self.verbose = verbose

    def schedule(self, epoch, lr=None):
        if epoch < self.hold_steps:
            # Hold phase, the learning rate is held constant at initial_lr.
            lr = self.initial_lr
        else:
            # The learning rate decays following a cosine function
            # until it reaches end_lr.
            epoch = epoch - self.hold_steps + 1
            completed_fraction = min(epoch, self.decay_steps) / self.decay_steps
            cosine_decayed = 0.5 * (1.0 + math.cos(math.pi * completed_fraction))
            alpha = self.end_lr / self.initial_lr
            decayed = (1 - alpha) * cosine_decayed + alpha
            lr = self.initial_lr * decayed
        return lr

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRWarmupCosineDecay(tf.keras.callbacks.Callback):
    """
    This callback applies a 4 phases decay function to the learning rate:
    1. Warmup phase: the learning rate increases linearly from an initial
    value over a number of epochs until it reaches its maximum value.
    2. Hold phase: the learning rate is held constant at its maximum value
    for a number of epochs.
    3. Cosine decay phase: the learning rate decays over a number of epochs
    following a cosine function until it reaches its target value.
    4. On target phase: the leaning rate is held constant at its target
    value for any number of subsequent epochs.

    The learning rate is updated at the beginning of each epoch.

    Arguments:
        initial_lr:
            A float, the initial value of the learning rate.
        warmup_steps:
            An integer, the number of epochs to increase the learning
            rate linearly over.
        max_lr:
            A float, the maximum value of the learning rate reached
            at the end of the linear increase phase.
        hold_steps:
            An integer, the number of epochs to hold the learning rate
            constant at `max_lr` before starting to decay.
        decay_steps:
            An integer, the number of steps to decay over following
            a cosine function.
        end_lr:
            A float, the learning rate value reached at the end of the
            cosine decay phase. The learning rate is held constant at
            this value for any subsequent epochs.
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    About the arguments:
        - If `warmup_steps` is set to 0, there is no warmup phase and the
          learning rate starts at `max_lr` (the `initial_lr` argument
          does not apply in this case and should not be used).
        - If `hold_steps` is set to 0, there is no hold phase and the learning
          rate immediately starts decaying after reaching `max_lr`.
        - If `warmup_steps` + `hold_steps` + `decay_steps` is equal to the
          total number of epochs, the cosine decay ends at the last epoch
          of the training with the learning rate reaching `end_lr`.
          There is no on-target constant learning rate phase in this case.
        - If `warmup_steps` and `hold_steps` are both equal to 0, the callback
          implements the same cosine decay function as the LRCosineDecay
          callback.

    Example usage:
        epochs = 400
        lr_scheduler = LRWarmupCosineDecay(
                            initial_lr=0.00001,
                            warmup_steps=30,
                            max_lr=0.01,
                            hold_steps=50,
                            decay_steps=280,
                            end_lr=0.00001)

    """

    def __init__(self,
                 initial_lr=None,
                 warmup_steps=None,
                 max_lr=None,
                 hold_steps=None,
                 decay_steps=None,
                 end_lr=None,
                 verbose=0):
        super().__init__()
        self.name = "LRWarmupCosineDecay"
        _check_scheduler_arguments(
                    [initial_lr, warmup_steps, max_lr, hold_steps, decay_steps, end_lr],
                    ["initial_lr", "warmup_steps", "max_lr", "hold_steps", "decay_steps", "end_lr"],
                    self.name)
        self.initial_lr = initial_lr
        self.warmup_steps = warmup_steps
        self.max_lr = max_lr
        self.hold_steps = hold_steps
        self.decay_steps = decay_steps
        self.end_lr = end_lr
        self.verbose = verbose
                          
    def schedule(self, epoch, lr=None):
        if epoch < self.warmup_steps - 1:
            # Warmup phase, the learning rate increases
            # linearly between initial_lr and maximum_lr.
            lr = ((self.max_lr - self.initial_lr) / self.warmup_steps) * epoch + self.initial_lr
        elif epoch < self.warmup_steps + self.hold_steps:
            # Hold phase, the learning rate is held constant at maximum_lr.
            lr = self.max_lr
        else:
            # The learning rate decays following a cosine function
            # until it reaches end_lr.
            epoch = epoch - self.warmup_steps - self.hold_steps
            completed_fraction = min(epoch, self.decay_steps) / self.decay_steps
            cosine_decayed = 0.5 * (1.0 + math.cos(math.pi * completed_fraction))
            alpha = self.end_lr / self.max_lr
            decayed = (1 - alpha) * cosine_decayed + alpha
            lr = self.max_lr * decayed
        return lr

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs=None)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
#        logs["lr"] = backend.get_value(self.model.optimizer.learning_rate)
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRCosineDecayRestarts(tf.keras.callbacks.Callback):
    """
    This callback applies a cosine decay function with restarts to
    the learning rate.

    At the beginning of the training, the learning rate decays from
    an initial value following a cosine function. After a number of
    epochs, the first restart occurs, i.e. the learning rate restarts
    from an initial value. Then, it decays following a cosine function
    until the second restart occurs, etc.
    A restart followed by a cosine decay is referred to as a "period".
    Periods get longer and longer and the initial learning rate of
    each period gets smaller and smaller as the training progresses.

    The learning rate is updated at the beginning of each epoch.

    Reference paper:
       [Loshchilov & Hutter, ICLR2016](https://arxiv.org/abs/1608.03983),
       SGDR: Stochastic Gradient Descent with Warm Restarts.

    Arguments:
        initial_lr:
            A float, the initial learning rate of the first period.
        first_decay_steps:
            An integer, the number of epochs to decay over in the first
            period. The numbers of epochs of the subsequent periods are
            a function of `first_decay_steps` and `t_mul`.
        end_lr:
            A float, the value of the learning rate reached at the end
            of each period.
        t_mul:
            A positive integer, used to derive the number of epochs of each
            period. The number of epochs of the i-th period is equal to
                `t_mul`**(i - 1) * `first_decay_steps`
            For example, if `first_decay_steps` is equal to 50 and `t_mul`
            is equal to 2, the numbers of epochs of the periods are 50,
            100, 200, 450, etc.
        m_mul:
            A float smaller than or equal to 1.0, used to derive the initial
            learning rate of the i-th period. If LR(i - 1) is the initial
            learning rate of period i-1, the initial learning rate of
            period i is equal to LR(i-1) * `m_mul`.
            For example, if `initial_lr` is equal to 0.01 and `m_mul` is
            equal to 0.7, the initial learning rates of the restarts
            are 0.007, 0.0049, 0.0512, 0.00343, etc.
            if `m_mul` is equal to 1.0, the initial learning rate is the
            same for all the restarts.
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    Example usage:
        epochs = 350
        lr_scheduler = LRCosineDecayRestarts(
                            initial_lr=0.01,
                            first_decay_steps=50,
                            end_lr=0.0001,
                            t_mul=2,
                            m_mul=0.8)

        With these settings, the learning rate restarts from 0.008 at epoch 50
        and from 0.0064 at epoch 150.
    """

    def __init__(self, initial_lr=None, first_decay_steps=None, end_lr=None, t_mul=2, m_mul=1.0, verbose=0):
        super().__init__()
        self.name = "LRCosineDecayRestarts"
        _check_scheduler_arguments(
                    [initial_lr, first_decay_steps, end_lr, t_mul, m_mul],
                    ["initial_lr", "first_decay_steps", "end_lr", "t_mul", "m_mul"],
                    self.name)
        self.initial_lr = initial_lr
        self.first_decay_steps = first_decay_steps
        self.end_lr = end_lr
        self.t_mul = t_mul
        self.m_mul = m_mul
        self.verbose = verbose

    def schedule(self, epoch, lr=None):

        def compute_step(completed_fraction, geometric=False):
            if geometric:
                i_restart = math.floor(
                    math.log(1.0 - completed_fraction * (1.0 - self.t_mul)) / math.log(self.t_mul)
                )
                sum_r = (1.0 - self.t_mul ** i_restart) / (1.0 - self.t_mul)
                completed_fraction = (completed_fraction - sum_r) / self.t_mul ** i_restart

            else:
                i_restart = math.floor(completed_fraction)
                completed_fraction -= i_restart
            return i_restart, completed_fraction

        completed_fraction = epoch / self.first_decay_steps
        if self.t_mul == 1:
            i_restart, completed_fraction = compute_step(completed_fraction, geometric=False)
        else:
            i_restart, completed_fraction = compute_step(completed_fraction, geometric=True)

        m_fac = self.m_mul ** i_restart
        cosine_decayed = 0.5 * m_fac * (1.0 + math.cos(math.pi * completed_fraction))
        alpha = self.end_lr / self.initial_lr
        decayed = (1 - alpha) * cosine_decayed + alpha
        return self.initial_lr * decayed

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs=None)
                  

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRPolynomialDecay(tf.keras.callbacks.Callback):
    """
    This callback applies a polynomial decay function to the learning rate,
    given a provided initial learning rate. See the `schedule` method of
    the callback.

    The learning rate is updated at the beginning of each epoch.

    If the `power` argument is set to 1.0, the learning rate decreases
    linearly.

    Arguments:
        initial_lr:
            A float, the initial learning rate.
        hold_steps:
            An integer, the number of epochs to hold the learning rate
            constant at `initial_lr` before starting to decay.
        decay_steps:
            A positive, see `schedule` function.
        end_lr:
            A float, end learning rate.
        power:
            The power of the polynomial.
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    Example usage:
        epochs = 300
        lr_scheduler = LRPolynomialDecay(
                            initial_lr=0.01,
                            hold_steps=30,
                            decay_steps=230,
                            end_lr=0.0001,
                            power=0.5)
    """

    def __init__(self, initial_lr=None, hold_steps=None, decay_steps=None, end_lr=None, power=0.5, verbose=0):
        super().__init__()
        self.name = "LRPolynomialDecay"
        _check_scheduler_arguments(
                    [initial_lr, hold_steps, decay_steps, end_lr, power],
                    ["initial_lr", "hold_steps", "decay_steps", "end_lr", "power"],
                    self.name)
        self.initial_lr = initial_lr
        self.hold_steps = hold_steps
        self.decay_steps = decay_steps
        self.end_lr = end_lr
        self.power = power
        self.verbose = verbose

    def schedule(self, epoch, lr=None):
        if epoch < self.hold_steps - 1:
            lr = self.initial_lr
        else:
            epoch = epoch - self.hold_steps + 1
            p = min(epoch, self.decay_steps) / self.decay_steps
            lr = (self.initial_lr - self.end_lr) * math.pow(1 - p, self.power) + self.end_lr
        return lr

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs=None)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRPolynomialDecayRestarts(tf.keras.callbacks.Callback):
    """
    This callback applies a polynomial decay function to the learning rate,
    given a provided initial learning rate. See the `schedule` method of
    the callback.
    If the `power` argument is set to 1.0, the learning rate decreases
    linearly.

    The learning rate is updated at the beginning of each epoch.

    Arguments:
        initial_lr:
            A float, the initial learning rate.
        hold_steps:
            An integer, the number of epochs to hold the learning rate
            constant at `initial_lr` before starting to decay.
        decay_steps:
            A positive, see `schedule` function.
        end_lr:
            A float, minimal end learning rate.
        power:
            The power of the polynomial.
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    Example usage:
        epochs = 400
        lr_scheduler = LRPolynomialDecayRestarts(
                            initial_lr=0.01,
                            hold_steps=30,
                            decay_steps=100,
                            end_lr=0.0001,
                            power=0.4)
        With these settings, the learning rate restarts from 0.00001
        at epochs 130, 230 and 330.
    """

    def __init__(self, initial_lr=None, hold_steps=None, decay_steps=None, end_lr=None, power=0.7, verbose=0):
        super().__init__()
        self.name = "LRPolynomialDecayRestarts"
        _check_scheduler_arguments(
                    [initial_lr, hold_steps, decay_steps, end_lr, power],
                    ["initial_lr", "hold_steps", "decay_steps", "end_lr", "power"],
                    self.name)
        self.initial_lr = initial_lr
        self.hold_steps = hold_steps
        self.decay_steps = decay_steps
        self.end_lr = end_lr
        self.power = power
        self.verbose = verbose

    def schedule(self, epoch, lr=None):
        if epoch < self.hold_steps - 1:
            lr = self.initial_lr
        else:
            epoch = epoch - self.hold_steps + 1
            p = epoch / (self.decay_steps * math.ceil(epoch / self.decay_steps)) if epoch > 0 else 0.0
            lr = (self.initial_lr - self.end_lr) * math.pow(1 - p, self.power) + self.end_lr
        return lr

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs=None)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )


class LRPiecewiseConstantDecay(tf.keras.callbacks.Callback):
    """
    This callback applies a piecewise constant decay function (a number of
    constant value steps) to the learning rate. See the `schedule` method
    of the callback.

    The learning rate is updated at the beginning of each epoch.

    Arguments:
        boundaries:
            A list of integers with strictly increasing values, the epochs
            when the learning rate starts a new constant step.
        values:
            A list of floats, specifies the value of the learning rate for
            each interval defined by `boundaries`. It should have one more
            element than `boundaries`, the last element being the learning
            rate value for any remaining epoch after the last epoch
            specified in `boundaries` (the last element).
        verbose:
            A boolean. If set to `True`, the learning rate value is printed
            at the beginning of each epoch.

    Example usage:
        Use a learning rate that is 0.01 for the first 30 epochs, 0.005 for
        the next 40 epochs, 0.001 for the next 80 epochs, and 0.0001 for any
        additional epoch.

        lr_scheduler = LRPiecewiseConstantDecay(
                            boundaries=[30, 70, 150]
                            values=[0.01, 0.005, 0.001, 0.0001])

    """

    def __init__(self, boundaries=None, values=None, verbose=0):
        super().__init__()
        self.name = "LRPiecewiseConstantDecay"
        _check_scheduler_arguments([boundaries, values], ["boundaries", "values"], self.name)
        if len(boundaries) != len(values) - 1:
            raise ValueError(
                "The length of boundaries should be 1 less than the length of "
                "values, got boundaries={} and values={}".format(boundaries, values))
        self.boundaries = boundaries
        self.values = values
        self.verbose = verbose

    def schedule(self, epoch, lr=None):
        for i, bound in enumerate(self.boundaries + [sys.maxsize]):
            if bound > epoch:
                return self.values[i]

    def on_epoch_begin(self, epoch, logs=None):
        generic_on_epoch_begin(self, epoch, logs=None)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs["lr"] = float(
            backend.convert_to_numpy(self.model.optimizer.learning_rate)
        )

