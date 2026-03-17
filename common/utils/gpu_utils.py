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


def set_gpu_memory_limit(gigabytes):
    """
     Sets the upper memory limit for the first GPU to the specified number of gigabytes.

     Args:
         gigabytes (int): The number of gigabytes to set as the upper memory limit.

     Raises:
         RuntimeError: If virtual devices have not been set before GPUs are initialized.

     Returns:
         None
     """
    # GPU memory usage configuration
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.set_logical_device_configuration(
                gpus[0],
                [tf.config.LogicalDeviceConfiguration(memory_limit=1024 * gigabytes)])
            logical_gpus = tf.config.list_logical_devices('GPU')
            print("{} physical GPUs, {} logical GPUs".format(len(gpus), len(logical_gpus)))
            print("[INFO] : Setting upper memory limit to {}GBytes on gpu[0]".format(gigabytes))
        except:
            raise RuntimeError("\nVirtual devices must be set before GPUs have been initialized.")


def inc_gpu_mode() -> None:
    """
    Increases the GPU memory allocation incrementally as needed.

    Returns:
        None
    """
    physical_gpus = tf.config.experimental.list_physical_devices('GPU')
    if not physical_gpus:
        return

    try:
        for gpu in physical_gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(f"Error setting memory growth: {e}")


def check_training_determinism(model: tf.keras.Model, sample_ds: tf.data.Dataset):
    """
    Check if there are operations that can rise exceptions during training.

    Args:
        model (tf.keras.Model): A keras model.
    
    Returns:
        valid_training (bool): True if the training raise no exception.
    """
    valid_training = True
    x_sample, y_sample = next(iter(sample_ds))

    try:
        with tf.GradientTape() as g:
            y = model(x_sample, training=True)
            loss = model.loss(y_sample, y)
        _ = g.gradient(loss, model.trainable_variables)
        
    except Exception as error:
        print(f"[WARN] {error}")
        valid_training = False

    return valid_training


def get_mem_consumption(batchsize,input_shape,model):
    """
    Calculate the memory consumption and time consumed for a given batch size,
    input shape, and model.

    Args:
        batchsize (int): The batch size for the input data.
        input_shape (tuple): The shape of the input data.
        model (tf.keras.Model): The model to calculate memory consumption and time for.

    Returns:
        tuple: A tuple containing the peak memory consumption (in GB).
    """
    img = np.random.rand(batchsize,*input_shape)
    labels_shape = model.output.shape
    label = np.random.rand(*labels_shape)
    tf.config.experimental.reset_memory_stats("GPU:0")
    t1 = time.time()
    with tf.GradientTape(watch_accessed_variables=False) as g:
        g.watch(model.trainable_variables)
        model_output = model(img, training=True)
        loss = model.loss(label, model_output)
    gradients = g.gradient(loss, model.trainable_variables)
    model.optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    t2 = time.time()
    info = tf.config.experimental.get_memory_info("GPU:0")
    tf.config.experimental.reset_memory_stats("GPU:0")
    time_consumed = t2 - t1
    return (info["peak"]/ 1024 / 1024 /1024, time_consumed)


def gpu_benchmark(gpu_limit,batch_size,input_shape,model):
    """
    Benchmark the memory consumption of a given model with a given batch size and input shape.

    Args:
        gpu_limit (float): The maximum amount of GPU memory (in GB) that can be used.
        batch_size (int): The batch size for the input data.
        input_shape (tuple): The shape of the input data.
        model (tf.keras.Model): The model to benchmark.

    Returns:
        bool: A boolean indicating whether an exception was raised during the benchmarking process.
    """
    S_E = False
    try:
        info = get_mem_consumption(batch_size,input_shape,model)
        memory_with_tf_overhead = info[0]
        if gpu_limit > memory_with_tf_overhead:
            print("[INFO] : Model memory requirement: {:.2f} GB".format(memory_with_tf_overhead))
    except Exception as e:
        S_E = True
    return S_E
