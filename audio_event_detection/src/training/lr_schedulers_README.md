### <a xid="appendix-c">Appendix C: learning rate schedulers

A number of callbacks are available that implement different learning rate decay functions. The ReduceLROnPlateau and LearningRateScheduler schedulers are Keras  schedulers, the others are provided with the Model Zoo.

To use one of these learning rate schedulers, simply add it to the list of callbacks in the 'training' section of your configuration file. The learning rate is updated at the beginning of each epoch.


#### <a xid="c-1">C.1 Plotting the learning rate before training

A script called *plot_learning_rate_schedule.py* is available in the *\<MODEL-ZOO-ROOT\>/image_classification/src/training* directory to plot the learning rate schedule before training. This script reads the 'training' section of your configuration file to get the number of training epochs, and the name and arguments of the learning rate scheduler in the 'callbacks' subsection. You can use it to plot the learning rate for the examples that are given in the sections below.

We encourage you to run this script. It does not require any extra work as it only needs your configuration file. It may save you a lot of time to choose a learning rate scheduler and tune its parameters.

Note that the script cannot be used with the Tensorflow `ReduceLROnPlateau` scheduler as the learning rate schedule is only available after training.


#### <a xid="c-2">C.2 Keras ReduceLROnPlateau scheduler

An example of usage of the Keras ReduceLROnPlateau learning rate scheduler is shown below.

```yaml
training:
   optimizer:
      Adam:
         learning_rate: 0.001
   callbacks:
      ReduceLROnPlateau:
         monitor: val_accuracy
         factor: 0.5
         patience: 20
         min_lr: 1e-7
         verbose: 0   # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

Refer to the Tensorflow documentation for more detail about the ReduceLROnPlateau callback.


#### <a xid="c-3">C.3 Keras LearningRateScheduler scheduler

An example of usage of the Tensorflow LearningRateScheduler scheduler is shown below.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LearningRateScheduler:   # The schedule is provided using a lambda function.
         schedule: |-
            lambda epoch, lr:
               (0.0005*epoch + 0.00001) if epoch < 20
               else (0.01 if epoch < 50
               else (lr / (1 + 0.0005 * epoch)
            ))
         verbose: 0   # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

In this example, the learning rate decay function includes 3 phases:
1. linear warmup from 0.00001 to 0.01 over the first 20 epochs
2. constant step at 0.01 for the next 30 epochs
3. time-based decay over the remaining epochs.

If you only want to implement a number of constant learning rate steps, there is no need to use the LearningRateScheduler callback. You can use the Model Zoo LRPiecewiseConstantDecay callback that is available for that purpose and is simpler to use.

Refer to the Tensorflow documentation for more detail about the LearningRateScheduler callback.


#### <a xid="c-4">C.4 LRLinearDecay scheduler

This callback applies a 2 phases decay function to the learning rate:
1. Hold phase: the learning rate is held constant at its initial value for a number of epochs.
2. Decay phase: the learning rate decays linearly over a number of epochs.

An example is shown below.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LRLinearDecay:
         initial_lr: 0.001   # Initial learning rate.
         hold_steps: 20      # Number of epochs to hold the learning rate constant at 'initial_lr' before starting to decay.
         decay_steps: 150    # Number of epochs to decay linearly over.
         end_lr: 1e-7        # End value of the learning rate.
         verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```


#### <a xid="c-5">C.5 LRExponentialDecay scheduler

This callback applies a 2 phases decay function to the learning rate:
1. Hold phase: the learning rate is held constant at its initial value for a number of epochs.
2. Decay phase: the learning rate decays following an exponential function.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LRExponentialDecay:
         initial_lr: 0.001  # Initial learning rate.
         hold_steps: 20     # Number of epochs to hold the learning rate constant at 'initial_lr' before starting to decay.
         decay_rate: 0.02   # A float, the decay rate of the exponential. Increasing the value causes the learning rate to decrease faster.
         min_lr: 1e-7       # minimum value of the learning rate.
         verbose: 0         # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

#### <a xid="c-6">C.6 LRStepDecay scheduler

This callback applies a staircase decay function with an exponential trend to the learning rate.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LRStepDecay:
         initial_lr: 0.001   # Initial learning rate.
         step_size: 30       # The number of epochs to hold the learning rate constant between two drops.
         decay_rate: 0.4     # The decay rate of the exponential. Decreasing the value of `decay_rate`
                             # causes the learning rate to decrease faster.
         min_lr: 1e-7        # Minimum value of the learning rate.
         verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

         initial_lr: 0.001    # Initial learning rate.
         step_size: 30      # The number of epochs to hold the learning rate constant between two drops.
         decay_rate: 0.4   # The decay rate of the exponential. Decreasing the value of `decay_rate` causes the learning rate to decrease faster.
         min_lr: 1e-7     # Minimum value of the learning rate.
         verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.


#### <a xid="c-7">C.7 LRCosineDecay scheduler

This callback applies a 3 phases decay function to the learning rate:
1. Hold phase: the learning rate is held constant at its initial value.
3. Cosine decay phase: the learning rate decays over a number of epochs
following a cosine function until it reaches its target value.
4. On target phase: the leaning rate is held constant at its target value for any number of subsequent epochs.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LRCosineDecay:
         initial_lr: 0.001   # Initial learning rate.
         hold_steps: 20      # The number of epochs to hold the learning rate constant between two drops.
         decay_steps: 180    # the number of steps to decay over following a cosine function
         end_lr: 1e-7        # The learning rate value reached at the end of the cosine decay phase. 
                             # The learning rate is held constant at this value for any subsequent epochs.
         verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

If `hold_steps` is set to 0, there is no hold phase and the learning rate immediately starts decaying from `initial_lr`.

If `hold_steps` + `decay_steps` is equal to the total number of epochs, the cosine decay ends at the last epoch of the training with the learning rate reaching `end_lr`. There is no on-target constant learning rate phase in this case.


#### <a xid="c-8">C.8 LRWarmupCosineDecay scheduler

This callback applies a 4 phases decay function to the learning rate:
1. Warmup phase: the learning rate increases linearly from an initial value over a number of epochs until it reaches its maximum value.
2. Hold phase: the learning rate is held constant at its maximum value for a number of epochs.
3. Cosine decay phase: the learning rate decays over a number of epochs following a cosine function until it reaches its target value.
4. On target phase: the leaning rate is held constant at its target value for any number of subsequent epochs.

```yaml
training:
   epochs: 400
   optimizer: Adam
   callbacks:
      LRWarmupCosineDecay:
         initial_lr: 1e-6   # Initial learning rate.
         warmup_steps: 30   # the number of epochs to increase the learning rate linearly over.
         max_lr: 0.001      # The maximum value of the learning rate reached at the end of the linear increase phase
         hold_steps: 50     # the number of epochs to hold the learning rate constant at `max_lr` before starting to decay
         decay_steps: 320   # the number of steps to decay over following a cosine function.
         end_lr: 1e-6       # the learning rate value reached at the end of the cosine decay phase. The learning rate
                            # is held constant at this value for any subsequent epochs.
         verbose: 0         # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

About the arguments:
- If `warmup_steps` is set to 0, there is no warmup phase and the learning rate starts at `max_lr` (the `initial_lr` argument does not apply in this case and should not be used).
- If `hold_steps` is set to 0, there is no hold phase and the learning rate immediately starts decaying after reaching `max_lr`.
- If `warmup_steps` + `hold_steps` + `decay_steps` is equal to the total number of epochs, the cosine decay ends at the last epoch of the training with the learning rate reaching `end_lr`. There is no on-target constant learning rate phase in this case.
- If `warmup_steps` and `hold_steps` are both equal to 0, the callback implements the same cosine decay function as the LRCosineDecay callback.


#### <a xid="c-9">C.9 LRCosineDecayRestarts scheduler

This callback applies a cosine decay function with restarts to the learning rate.

At the beginning of the training, the learning rate decays from an initial value following a cosine function. After a number of epochs, the first restart occurs, i.e. the learning rate restarts from an initial value. Then, it decays following a cosine function until the second restart occurs, etc. A restart followed by a cosine decay is referred to as a "period". Periods get longer and longer and the initial learning rate of each period gets smaller and smaller as the training progresses.

Reference paper:
[Loshchilov & Hutter, ICLR2016](https://arxiv.org/abs/1608.03983), SGDR: Stochastic Gradient Descent with Warm Restarts.

```yaml
training:
   epochs: 350
   optimizer: Adam
   callbacks:
      LRCosineDecayRestarts:
         initial_lr: 0.001      # Initial learning rate.
         first_decay_steps: 50  # An integer, the number of epochs to decay over in the first period. 
                                # The numbers of epochs of the subsequent periods are a function of `first_decay_steps` and `t_mul`
         end_lr: 1e-6           # The value of the learning rate reached at the end of each period
         t_mul: 2               # A positive integer, used to derive the number of epochs of each period.
         m_mul: 0.8             # A float smaller than or equal to 1.0, used to derive the initial learning rate of the i-th period.

         verbose: 0             # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

The `t_mul` argument is used to derive the number of epochs of each period. The number of epochs of the i-th period is equal to "`t_mul`**(i - 1) * `first_decay_steps`". For example, if `first_decay_steps` is equal to 50 and `t_mul` is equal to 2, the numbers of epochs of the periods are 50, 100, 200, 450, etc.

The `m_mul` argument is used to derive the initial learning rate of the i-th period. If LR(i - 1) is the initial learning rate of period i-1, the initial learning rate of period i is equal to "LR(i-1) * `m_mul`". For example, if `initial_lr` is equal to 0.01 and `m_mul` is equal to 0.7, the initial learning rates of the restarts are 0.007, 0.0049, 0.0512, 0.00343, etc. if `m_mul` is equal to 1.0, the initial learning rate is the same for all the restarts.


#### <a xid="c-10">C.10 LRPolynomialDecay scheduler

This callback applies a polynomial decay function to the learning rate, given a provided initial learning rate. See the `schedule` method of the callback.

```yaml
training:
   epochs: 300
   optimizer: Adam
   callbacks:
      LRPolynomialDecay:
         initial_lr: 0.001   # Initial learning rate.
         hold_steps: 30      # number of epochs to hold the learning rate constant at `initial_lr` before starting to decay
         decay_steps: 270    # The decay rate of the exponential. Decreasing the value of `decay_rate` causes the learning rate to decrease faster.
         end_lr: 1e-7        # end learning rate.
         verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```


#### <a xid="c-11">C.11 LRPolynomialDecayRestarts scheduler

This callback applies a polynomial decay function to the learning rate, given a provided initial learning rate. See the `schedule` method of the callback. If the `power` argument is set to 1.0, the learning rate decreases linearly.

```yaml
training:
   epochs: 400
   optimizer: Adam
   callbacks:
      LRPolynomialDecayRestarts:
         initial_lr: 0.001   # Initial learning rate.
         hold_steps: 30      # the number of epochs to hold the learning rate constant at `initial_lr` before starting to decay.
         decay_steps: 120    # see `schedule` function
         end_lr: 1e-7        # Minimum value of the learning rate.
         power: 0.5          # The power of the polynomial
         verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

With the settings of the example above, the learning rate restarts from 0.00001 at epochs 130, 230 and 330.


#### <a xid="c-12">C.12 LRPiecewiseConstantDecay scheduler

The PiecewiseConstantDecay scheduler applies a piecewise constant decay function (a number of constant value steps) to the learning rate. See the `schedule` method of the callback.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LRPiecewiseConstantDecay:
         boundaries: [30, 70, 150]              # The list of epochs when the learning rate starts a new constant step.
         values: [0.01, 0.005, 0.001, 0.0001]   # The number of epochs to hold the learning rate constant between two drops.
         verbose: 0                             # verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

The `boundaries` argument is a list of integers with strictly increasing values that provide the epoch numbers  when the learning rate starts a new constant step.
The `values` argument is a list of floats that specifies the value of the learning rate for each interval defined by the `boundaries` argument. It should have one more element than `boundaries`, the last element being the learning rate value for any remaining epoch after the last epoch specified in `boundaries` (the last element).

In the example above, the learning rate is 0.01 for the first 30 epochs, 0.005 for the next 40 epochs, 0.001 for the next 80 epochs, and 0.0001 for any
subsequent epoch.