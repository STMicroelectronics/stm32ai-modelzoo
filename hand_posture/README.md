# ST multi-zone Time-of-Flight sensors hand posture recognition STM32 model zoo


## Directory components:
* [datasets](datasets/README.md) placeholder for the Hand Posture ToF datasets.
* [deployment](deployment/README.md) contains the necessary files for the deployment service.
* [pretrained_models](pretrained_models/README.md) a collection of optimized pretrained models
* [src](src/README.md) contains tools to train, evaluate and benchmark your model on your STM32 target.

## Quick & easy examples:
The `operation_mode` top-level attribute specifies the operations or the service you want to execute.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below.

All .yaml configuration examples are located in [config_file_examples](./src/config_file_examples/) folder.

| operation_mode attribute | Operations                                                             |
|:---------------------------|:-----------------------------------------------------------------------|
| `training`| Train a model from the model zoo or your own model                     |
| `evaluation` | Evaluate the accuracy of a float model on a test or validation dataset |
| `benchmarking` | Benchmark a float model on an STM32 board                              |
| `deployment`   | Deploy a model on an STM32 board                                       |

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific services:
   - [training](./src/training/README.md)
   - [evaluation](./src/evaluation/README.md)
   - [benchmarking](./src/benchmarking/README.md)
   - [deployment](./deployment/README.md)

## Guidelines
The hand posture use case is based on the ST multi-zone Time-of-Flight sensors: [VL53L5CX](https://www.st.com/en/imaging-and-photonics-solutions/vl53l5cx.html), and [VL53L8CX](https://www.st.com/en/imaging-and-photonics-solutions/vl53l8cx.html).
The goal of this use case is to recognize static hand posture such as a like, dislike or love sign done with user hand in front of the sensor.

We are providing a complete workflow from data acquisition to model training, then deployment on an STM32 NUCLEO-F401RE board. To create your end-to-end embedded application for the hand posture use-case, you simply need to follow these steps:

* Collect your custom dataset using ST datalogging tool [STSW-IMG035_EVK (Gesture EVK)](https://www.st.com/en/embedded-software/stsw-img035.html), by following this [tutorial](./datasets/README.md).
* Train a model on your custom dataset using the training scripts provided [here](src/README.md).
* Alternatively, you can start directly from one of our pretrained models found in the [models](pretrained_models/README.md) directory.
* Deploy the pretrained model with the [deployment service](deployment/README.md).
