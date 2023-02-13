# Human activity recognition STM32 model zoo

This directory contains scripts and tools for training, evaluating and deploying human activity recognition (HAR) models using **TensorFlow**, **Sklearn** & **STM32Cube.AI**.

## Training
Under [training](training/README.md) you can find a step by step guide plus the necessary scripts and tools to train, quantize and evaluate your image classification models using WISDM dataset. Note that the dataset is not provided in the modelzoo and has to be downloaded by the user himself.

## Evaluate
Under [evaluate](evaluate/README.md) you can find a step by step guide plus the necessary scripts and tools to benchmark your model using STM32Cube.AI through our STM32Cube.AI Developer Cloud Services or from the local downloaded CLI, as well as support for quantizing and evaluating your pretrained `IGN`, `SVC`, and `Custom` models is also provided if dataset are provided.

## Deployment
Under [deployment](deployment/README.md) you can find a step by step guide plus the necessary scripts and tools to quantize your own pre-trained human activity recognition (HAR) models, evaluate it and then deploy it on your STM32 board using STM32Cube.AI.

You can also use a pretrained model from our `human activity recognition model zoo`, and deploy it for your tests. Refer [here](../models/README.md) for all the available pretrained models.