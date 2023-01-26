# ResNet v1  quantized

## **Use case** : [Image Classification](../../../image_classification/README.md)

# Model description

ResNet models perform image classification - they take images as input and classify the major object in the image into a
set of pre-defined classes.  ResNet models provide very high accuracies with affordable model sizes. They are ideal for cases when high accuracy of classification
is required.
ResNet models consists of residual blocks and came up to counter the effect of deteriorating accuracies with more layers due to network not learning the initial layers.
ResNet v1 uses post-activation for the residual blocks. the models below have 8 and 32 layers with ResNet v1 architecture.
(source: https://keras.io/api/applications/resnet/)
The model is quantized in int8 using tensorflow lite converter.

In addition, we introduce a new model family inspired from ResNet v1 which takes benefit from hybrid quantization.
By hybrid quantization, we mean that whenever it is possible, some network layers are quantized for weights and/or activations on less than 8 bits.
These networks no longer need to be converted with tensorflow lite. They are quantized during training (Quantization Aware Training).
CubeAI is able to import them directly and to generate the corresponding FW code.  


## Network Information

| Network Information     | Value                                                                   |
|-------------------------|-------------------------------------------------------------------------|
|  Framework              | TensorFlow Lite                                                         |                                                         |
|  Quantization           | int8                                                                    |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/resnet |
|  Paper                  | https://arxiv.org/abs/1512.03385                                        |

The models are quantized using tensorflow lite converter.

## Network Inputs / Outputs

For an image resolution of NxM and P classes

| Input Shape    | Description                                                 |
|----------------|-------------------------------------------------------------|
| (1, N, M, 3)   | Single NxM RGB image with UINT8 values between 0 and 255    |

| Output Shape   | Description                                                 |
|----------------|-------------------------------------------------------------|
| (1, P)         | Per-class confidence for P classes in FLOAT32               |

## Recommended Platforms

| Platform | Supported | Optimized |
|----------|-----------|-----------|
| STM32L0  | []        | []        |  
| STM32L4  | [x]       | []        |
| STM32U5  | [x]       | []        |
| STM32H7  | [x]       | [x]       |
| STM32MP1 | [x]       | [x]*      |

* Only for Cifar 100 models

# Performances

## Training

To train a ResNet v1 model with pretrained weights or from scratch on your own dataset, you need to configure
the [user_config.yaml](../../scripts/training/user_config.yaml) file following
the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [resnet_v1_8_config.yaml](../resnetv1/ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32/resnet_v1_8_32_config.yaml)
file is used to train this model on Cifar 10 dataset.

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../scripts/deployment/user_config.yaml)
file following the [tutorial](../../scripts/deployment/README.md) under the deployment section.

## Metrics

Measures are done with default STM32Cube.AI (v7.3.0) configuration with enabled input / output allocated option.

### Reference MCU memory footprint based on Cifar 10 dataset (see Accuracy for details on dataset)

| Model                                                                                                          | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM | Total Flash |
|----------------------------------------------------------------------------------------------------------------|--------|------------|---------|----------------|-------------|---------------|------------|-----------|-------------|
| [ResNet v1 8](../resnetv1/ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32/resnet_v1_8_32_int8.tflite) | Int8   | 32x32      | STM32H7 | 55.28 KiB      | ~8 KiB      | 76.9 KiB      | ~46 KiB    | ~64 KiB   | 123 KiB     |
| ST ResNet 8 Hybrid v1                                                                                          | Hybrid | 32x32      | STM32H7 | 72 KiB         | ~20 KiB     | 66.28 KiB     | ~75 KiB    | ~92 KiB   | 141 KiB     |
| ST ResNet 8 Hybrid v2                                                                                          | Hybrid | 32x32      | STM32H7 | 72 KiB         | ~20 KiB     | 85.8 KiB      | ~75 KiB    | ~92 KiB   | 161 KiB     |
| ST ResNet 8 Hybrid v3                                                                                          | Hybrid | 32x32      | STM32H7 | 72 KiB         | ~20 KiB     | 66.28 KiB     | ~75 KiB    | ~92 KiB   | 141 KiB     |

### Reference inference time based on Cifar 10 dataset (see Accuracy for details on dataset)

| Model                                                                                                          | Format | Resolution | Board            | Execution Engine | Frequency    | Inference time (ms) |
|----------------------------------------------------------------------------------------------------------------|--------|------------|------------------|------------------|--------------|---------------------|
| [ResNet v1 8](../resnetv1/ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32/resnet_v1_8_32_int8.tflite) | Int8   | 32x32      | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 37.91 ms            |
| [ResNet v1 8](../resnetv1/ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32/resnet_v1_8_32_int8.tflite) | Int8   | 32x32      | STM32MP157F-DK2  | 2 CPU            | 800 MHz      | 10.97 ms **         |
| ST ResNet 8 Hybrid v1                                                                                          | Hybrid | 32x32      | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 36.48 ms            |
| ST ResNet 8 Hybrid v2                                                                                          | Hybrid | 32x32      | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 32.81 ms            |
| ST ResNet 8 Hybrid v3                                                                                          | Hybrid | 32x32      | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 28.71 ms            |


** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Reference MCU memory footprint based on Cifar 100 dataset (see Accuracy for details on dataset)

| Model                                                                                                              | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |
|--------------------------------------------------------------------------------------------------------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|
| [ResNet v1 32](../resnetv1/ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32/resnet_v1_32_32_int8.tflite) | Int8   | 32x32      | STM32H7 | 55.28 KiB      | ~28 KiB     | 464.38 KiB    | ~78 KiB    | ~84 KiB     | ~ 542 KiB   |


### Reference inference time based on Cifar 100 dataset (see Accuracy for details on dataset)

| Model                                                                                                              | Format | Resolution | Board            | Execution Engine | Frequency    | Inference time (ms) |
|--------------------------------------------------------------------------------------------------------------------|--------|------------|------------------|------------------|--------------|---------------------|
| [ResNet v1 32](../resnetv1/ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32/resnet_v1_32_32_int8.tflite) | Int8   | 32x32      | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 192 ms              |
| [ResNet v1 32](../resnetv1/ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32/resnet_v1_32_32_int8.tflite) | Int8   | 32x32      | STM32MP157F-DK2  | 2 CPU            | 800 MHz      | 55.36 ms **         |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Cifar10 dataset

Dataset details: [link](https://www.cs.toronto.edu/~kriz/cifar.html) ,
License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) , Quotation[[1]](#1) , Number of classes: 10, Number of
images: 60 000

| Model                                                                                                          | Format   | Resolution | Top 1 Accuracy |
|----------------------------------------------------------------------------------------------------------------|----------|------------|----------------|
| [ResNet v1 8](../resnetv1/ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32/resnet_v1_8_32.h5)          | Float    | 32x32      | 85.63 %        |
| [ResNet v1 8](../resnetv1/ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32/resnet_v1_8_32_int8.tflite) | Int8     | 32x32      | 84.95 %        |
| ST ResNet 8 Hybrid v1                                                                                          | Hybrid   | 32x32      | 85.89 %        |
| ST ResNet 8 Hybrid v2                                                                                          | Hybrid   | 32x32      | 85.24%         |
| ST ResNet 8 Hybrid v3                                                                                          | Hybrid   | 32x32      | 84.37%         |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=200' and ReduceLROnPlateau 'factor=0.75', 'patience=50'.

### Accuracy with Cifar100 dataset

Dataset details: [link](https://www.cs.toronto.edu/~kriz/cifar.html) ,
License [CC0 4.0](https://creativecommons.org/licenses/by/4.0/), Quotation[[2]](#2)  , Number of classes:100,
Number of images:  600 000

| Model                                                                                                             | Format  | Resolution | Top 1 Accuracy |
|-------------------------------------------------------------------------------------------------------------------|---------|------------|----------------|
| [ResNet v1 32](../resnetv1/ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32/resnet_v1_32_32.h5)          | Float   | 32x32      | 66.3%          |
| [ResNet v1 32](../resnetv1/ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32/resnet_v1_32_32_int8.tflite) | Int8    | 32x32      | 65.47%         |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=200' and ReduceLROnPlateau 'patience=50'.
## Retraining and code generation

- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../scripts/deployment/README.md)

## Demos

### Integration in simple example

Please refer to the generic guideline [here](../../scripts/deployment/README.md).

# References

<a id="1">[1]</a>
“Tf_flowers : tensorflow datasets,” TensorFlow. [Online].
Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), “Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep
Convolutional Neural Network”, Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
@inproceedings{bossard14,
title = {Food-101 -- Mining Discriminative Components with Random Forests},
author = {Bossard, Lukas and Guillaumin, Matthieu and Van Gool, Luc},
booktitle = {European Conference on Computer Vision},
year = {2014}
}
