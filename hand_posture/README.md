# ST multi-zone Time-of-Flight sensors hand posture recognition STM32 model zoo


## Directory components:

* [getting_started](getting_started/README.md) contains the necessary files to run and demonstrate the usage of a hand posture model on STM32 board.
* [models](models/README.md) a collection of optimized pretrained models for different hand posture recognition use-cases.
* [scripts](scripts/README.md) contains tools to train, evaluate and deploy your model on your STM32 target.

## Guidelines

The hand posture use case is based on the ST VL53L5CX Time-of-Flight sensor.
The goal of this use case is to recognize static hand posture such as a like, dislike or love sign done with user hand in front of the sensor.

We are providing a complete workflow from data acquisition to model training, then deployment on an STM32 NUCLEO-F401RE board. To create your end-to-end embbeded application for the hand posture use-case, you simply need to follow these steps:

* Collect your custom dataset using ST datalogging tool [STSW-IMG035_EVK (Gesture EVK)](https://www.st.com/en/embedded-software/stsw-img035.html), by following this [tutorial](./scripts/training/README.md#create-your-st-tof-dataset).
* Train a model on your custom dataset using the training scripts provided [here](./scripts/training/README.md).
* Alternatively, you can start directly from one of our pretrained models found in the [models](./models/README.md) directory.
* Deploy the pretrained model with the [getting started](./getting_started/README.md) package using the deployment scripts provided [here](./scripts/deployment/README.md).
