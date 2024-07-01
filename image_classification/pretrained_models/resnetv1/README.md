# ResNet v1

## **Use case** : [Image classification](../README.md)

# Model description

ResNet models perform image classification - they take images as input and classify the major object in the image into a
set of pre-defined classes.  ResNet models provide very high accuracies with affordable model sizes. They are ideal for cases when high accuracy of classification is required.
ResNet models consist of residual blocks and came up to counter the effect of deteriorating accuracies with more layers due to network not learning the initial layers.
ResNet v1 uses post-activation for the residual blocks. The models below have 8 and 32 layers with ResNet v1 architecture.
(source: https://keras.io/api/applications/resnet/)
The model is quantized in int8 using tensorflow lite converter.

In addition, we introduce a new model family inspired from ResNet v1 which takes benefit from hybrid quantization.
Later on, they are named as ST ResNet 8 Hybrid v1 and ST ResNet 8 Hybrid v2.
By hybrid quantization, we mean that whenever it is possible, some network layers are quantized for weights and/or activations on less than 8 bits.
We used Larq library to define and train these models. In particular, in our topology some layers/activations are kept in 8 bits while others are in binary.
Please note that since this quantization is performed during training (Quantization Aware Training), these networks no longer need to be converted with tensorflow lite.
STM32Cube.AI is able to import them directly in .h5 format and to generate the corresponding optimized FW code.
Even if many layers are in binary, these models provide comparable accuracy to the full 8-bit ResNet v1 8 but have a significantly lower inference time.


## Network information

| Network Information     | Value                                                                   |
|-------------------------|-------------------------------------------------------------------------|
|  Framework              | TensorFlow Lite                                                         |
|  Quantization           | int8                                                                    |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/resnet |
|  Paper                  | https://arxiv.org/abs/1512.03385                                        |

The models are quantized using tensorflow lite converter.

## Network inputs / outputs

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
| STM32MP2 | [x]       | []        |

* Only for Cifar 100 models

# Performances

## Training

To train a ResNet v1 model with pretrained weights, from scratch or fine tune it on your own dataset, you need to configure
the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/README.md) under the src section.

As an example, [resnet_v1_8_32_tfs_config.yaml](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs_config.yaml) file is used to train this model on Cifar 10 dataset.

For ST ResNet 8 Hybrid v1 or ST ResNet 8 Hybrid v2 please use respectively [st_resnet_8_hybrid_v1_32_tfs_config.yaml](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v1_32_tfs/st_resnet_8_hybrid_v1_32_tfs_config.yaml)
or [st_resnet_8_hybrid_v2_32_tfs_config.yaml](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v2_32_tfs/st_resnet_8_hybrid_v2_32_tfs_config.yaml) instead.

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml)
file following the [tutorial](../../deployment/README.md) under the deployment section.

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **MCU** memory footprint based on Cifar 10 dataset (see Accuracy for details on dataset)

| Model                                                                                                                                 | Format | Resolution  | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM | Total Flash | STM32Cube.AI version  |
|---------------------------------------------------------------------------------------------------------------------------------------|--------|-------------|---------|----------------|-------------|---------------|------------|-----------|-------------|-----------------------|
| [ResNet v1 8 tfs](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs_int8.tflite)                      | Int8   | 32x32x3     | STM32H7 | 62.51 KiB      | 7.21 KiB    | 76.9 KiB      | 56.45 KiB  | 69.72 KiB | 133.35 KiB  | 9.1.0                 |
| [ST ResNet 8 Hybrid v1 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v1_32_tfs/st_resnet_8_hybrid_v1_32_tfs.h5) | Hybrid | 32x32x3     | STM32H7 | 77.84 KiB      | 18.38 KiB   | 85.79 KiB     | 61.75 KiB  | 96.22 KiB | 147.54 KiB  | 9.1.0                 |
| [ST ResNet 8 Hybrid v2 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v2_32_tfs/st_resnet_8_hybrid_v2_32_tfs.h5) | Hybrid | 32x32x3     | STM32H7 | 78.99 KiB      | 18.38 KiB   | 66.28 KiB     | 60.99 KiB  | 97.37 KiB | 127.27 KiB  | 9.1.0                 |

### Reference **MCU** inference time based on Cifar 10 dataset (see Accuracy for details on dataset)

| Model                            | Format | Resolution  | Board            | Execution Engine | Frequency    | Inference time (ms) | STM32Cube.AI version  |
|----------------------------------|--------|-------------|------------------|------------------|--------------|---------------------|-----------------------|
| [ResNet v1 8 tfs](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs_int8.tflite) | Int8   | 32x32x3     | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 28.67 ms            | 9.1.0                 |
| [ST ResNet 8 Hybrid v1 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v1_32_tfs/st_resnet_8_hybrid_v1_32_tfs.h5) | Hybrid | 32x32x3     | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 28.93 ms            | 9.1.0                 |
| [ST ResNet 8 Hybrid v2 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v2_32_tfs/st_resnet_8_hybrid_v2_32_tfs.h5) | Hybrid | 32x32x3     | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 25.2 ms            | 9.1.0                 |


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                                                                                                                                 |  Format  | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|---------------------------------------------------------------------------------------------------------------------------------------|----------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [ResNet v1 8 tfs](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs_int8.tflite)                      | Int8     | 32x32x3    |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 2.02 ms             | 12.26 | 87.74 | 0    |   v5.1.0           | OpenVX                |
| [ST ResNet 8 Hybrid v1 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v1_32_tfs/st_resnet_8_hybrid_v1_32_tfs.h5) | Hybrid   | 32x32x3    |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | TBD ms              | 0 | 0 | 0    |   v5.1.0           | OpenVX                |
| [ST ResNet 8 Hybrid v2 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v2_32_tfs/st_resnet_8_hybrid_v2_32_tfs.h5) | Hybrid   | 32x32x3    |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | TBD ms            | 0 | 0 | 0    |   v5.1.0           | OpenVX                |
| [ResNet v1 8 tfs](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs_int8.tflite)                      | Int8     | 32x32x3    |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 6.50 ms             | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| [ST ResNet 8 Hybrid v1 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v1_32_tfs/st_resnet_8_hybrid_v1_32_tfs.h5) | Hybrid   | 32x32x3    |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | TBD ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| [ST ResNet 8 Hybrid v2 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v2_32_tfs/st_resnet_8_hybrid_v2_32_tfs.h5) | Hybrid   | 32x32x3    |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | TBD ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| [ResNet v1 8 tfs](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs_int8.tflite)                      | Int8     | 32x32x3    |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 10.77 ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| [ST ResNet 8 Hybrid v1 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v1_32_tfs/st_resnet_8_hybrid_v1_32_tfs.h5) | Hybrid   | 32x32x3    |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | TBD ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| [ST ResNet 8 Hybrid v2 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v2_32_tfs/st_resnet_8_hybrid_v2_32_tfs.h5) | Hybrid   | 32x32x3    |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | TBD ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### Reference **MCU** memory footprint based on Cifar 100 dataset (see Accuracy for details on dataset)

| Model                                                                                                                | Format | Resolution  | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |
|----------------------------------------------------------------------------------------------------------------------|--------|-------------|---------|----------------|-------------|---------------|------------|-------------|-------------|
| [ResNet v1 32 tfs](./ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32_tfs/resnet_v1_32_32_tfs_int8.tflite) | Int8   | 32x32x3     | STM32H7 | 45.41 KiB      | 24.98 KiB   | 464.38 KiB    | 78.65 KiB  | 70.39 KiB   | 543.03 KiB  |


### Reference **MCU** inference time based on Cifar 100 dataset (see Accuracy for details on dataset)

| Model                                                                                                                | Format | Resolution | Board            | Execution Engine | Frequency    | Inference time (ms) |
|----------------------------------------------------------------------------------------------------------------------|--------|------------|------------------|------------------|--------------|---------------------|
| [ResNet v1 32 tfs](./ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32_tfs/resnet_v1_32_32_tfs_int8.tflite) | Int8   | 32x32x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 177.7 ms            |


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                                                                                                               |  Format  | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|---------------------------------------------------------------------------------------------------------------------|----------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
|[ResNet v1 32 tfs](./ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32_tfs/resnet_v1_32_32_tfs_int8.tflite) | Int8     | 32x32x3    |  per-channel  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 9.160 ms            | 14.75 | 85.25 | 0    |   v5.1.0           | OpenVX                |
|[ResNet v1 32 tfs](./ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32_tfs/resnet_v1_32_32_tfs_int8.tflite) | Int8     | 32x32x3    |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 34.78 ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
|[ResNet v1 32 tfs](./ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32_tfs/resnet_v1_32_32_tfs_int8.tflite) | Int8     | 32x32x3    |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 55.32 ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |


### Accuracy with Cifar10 dataset

Dataset details: [link](https://www.cs.toronto.edu/~kriz/cifar.html) ,
License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) , Quotation[[1]](#1) , Number of classes: 10, Number of
images: 60 000

| Model                                                                                                            | Format   | Resolution  | Top 1 Accuracy |
|------------------------------------------------------------------------------------------------------------------|----------|-------------|----------------|
| [ResNet v1 8 tfs](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs.h5)          | Float    | 32x32x3     | 87.01 %        |
| [ResNet v1 8 tfs](./ST_pretrainedmodel_public_dataset/cifar10/resnet_v1_8_32_tfs/resnet_v1_8_32_tfs_int8.tflite) | Int8     | 32x32x3     | 85.59 %        |
| [ST ResNet 8 Hybrid v1 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v1_32_tfs/st_resnet_8_hybrid_v1_32_tfs.h5)                                                                                        | Hybrid   | 32x32x3     | 86 %           |
| [ST ResNet 8 Hybrid v2 tfs](./ST_pretrainedmodel_public_dataset/cifar10/st_resnet_8_hybrid_v2_32_tfs/st_resnet_8_hybrid_v2_32_tfs.h5)                                                                                        | Hybrid   | 32x32x3     | 84.85 %        |


### Accuracy with Cifar100 dataset

Dataset details: [link](https://www.cs.toronto.edu/~kriz/cifar.html) ,
License [CC0 4.0](https://creativecommons.org/licenses/by/4.0/), Quotation[[2]](#2)  , Number of classes:100,
Number of images:  600 000

| Model                                                                                                                | Format  | Resolution | Top 1 Accuracy |
|----------------------------------------------------------------------------------------------------------------------|---------|------------|----------------|
| [ResNet v1 32 tfs](./ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32_tfs/resnet_v1_32_32_tfs.h5)          | Float   | 32x32x3    | 67.75 %        |
| [ResNet v1 32 tfs](./ST_pretrainedmodel_public_dataset/cifar100/resnet_v1_32_32_tfs/resnet_v1_32_32_tfs_int8.tflite) | Int8    | 32x32x3    | 66.58 %        |

## Retraining and code generation


Please refer to the yaml explanations: [here](../../src/README.md)


## Demos
### Integration in a simple example


Please refer to the generic guideline [here](../../deployment/README.md)

# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.
