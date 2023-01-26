# STMicroelectronics Object Detection ZOO

This directory contains scripts and tools for training, evaluating and deploying object detection models using **TensorFlow** & **STM32Cube.AI**.

## Training
Under [training](training/README.md) you can find a step by step guide plus the necessary scripts and tools to train, quantize and evaluate your object detection models after providing your own dataset.

## Evaluate
Under [evaluate](evaluate/README.md) you can find a step by step guide plus the necessary scripts and tools to benchmark your model using STM32Cube.AI through our Developer Cloud Services or from the local download, as well as support for quantizing and evaluating your model performances if datasets are provided.

## Deployment
Under [deployment](deployment/README.md) you can find a step by step guide plus the necessary scripts and tools to quantize your own pre-trained object detection model, evaluate it and then deploy it on your STM32 board using STM32Cube.AI.

You can also use a pretrained model from our `Object Detection model zoo`, check out the available models [here](../models/README.md).