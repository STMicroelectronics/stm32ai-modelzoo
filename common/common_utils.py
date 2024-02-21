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

def benchmark(gpu_limit,batch_size,input_shape,model):
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