# EfficientNet

## **Use case** : [Image classification](../README.md)

# Model description
EfficientNet was initially introduced in this [paper](https://arxiv.org/pdf/1905.11946.pdf).
The authors proposed a method that uniformly scales all dimensions depth/width/resolution using a so-called compound coefficient.
Using neural architecture search, the authors created the EfficientNet topology and starting from B0, derived a few variants B1...B7 ordered by increasing complexity.
Its main building blocks are a mobile inverted bottleneck MBConv (Sandler et al., 2018; Tan et al., 2019) and a squeeze-and-excitation optimization (Hu et al., 2018).

EfficientNet provides state-of-the art accuracy on ImageNet and CIFAR for example while being much smaller and faster
than its comparable (ResNet, DenseNet, Inception...).
However, for STM32 platforms, B0 is already too large. That's why, we internally derived a custom version tailored for STM32
and modified it to be quantization-friendly (not discussed in the initial paper). This custom model is then quantized in int8 using Tensorflow Lite converter.
In the following, the resulting model is called ST EfficientNet LC v1 (LC standing for Low Complexity).

ST EfficientNet LC v1 was obtained after fine-tuning of the original topology. Our goal was to reach around 500 kBytes for RAM and weights.
For achieving this, we decided to replace original 'swish' by a simple 'relu6', and search for good expansion factor, depth
and width coefficients. Of course, many models could meet the requirement. We selected the one which was better performing on food-101 dataset.
We made several attempts to quantize the EfficientNet topology, and discover some issues when quantizing activations.
The problem was fixed mainly by adding a clipping lambda layer before the sigmoid.

## Network information
| Network Information | Value                                 |
|---------------------|---------------------------------------|
| Framework           | TensorFlow Lite                       |
| Params              | 517540                                |
| Quantization        | int8                                  |
| Paper               | https://arxiv.org/pdf/1905.11946.pdf  |

The models are quantized using tensorflow lite converter.

## Network inputs / outputs
For an image resolution of NxM and P classes :

| Input Shape   | Description                                              |
|---------------|----------------------------------------------------------|
| (1, N, M, 3)  | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape  | Description                                              |
|---------------|----------------------------------------------------------|
| (1, P)        | Per-class confidence for P classes                       |


## Recommended platform
| Platform | Supported | Recommended   |
|----------|-----------|---------------|
| STM32L0  | []        | []            |
| STM32L4  | []        | []            |
| STM32U5  | [x]       | []            |
| STM32H7  | [x]       | [x]           |
| STM32MP1 | [x]       | [x]           |
| STM32MP2 | [x]       | []            |

---
# Performances
## Training
To train a ST EfficientNet LC v1 model from scratch on your own dataset, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/README.md) under the src section.

As an example, [st_efficientnet_lc_v1_224_config_tfs.yaml](./ST_pretrainedmodel_public_dataset/flowers/st_efficientnet_lc_v1_224_tfs/st_efficientnet_lc_v1_224_tfs_config.yaml) file is used to train this model on flowers dataset,
you can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the src section to reproduce the results presented below.

## Deployment
To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md) under the deployment section.

## Metrics
Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **MCU** memory footprints based on Flowers dataset (see Accuracy for details on dataset)
| Model                     | Format | Resolution   | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM  | Total Flash | STM32Cube.AI version |
|---------------------------|--------|--------------|---------|----------------|-------------|---------------|------------|------------|-------------|----------------------|
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | STM32H7 | 430.78 KiB     | 58.19 KiB    | 505.41 KiB    | 158.4 KiB | 488.97 KiB | 663.81 KiB  | 9.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | STM32H7 | 166.78 KiB     | 57.86 KiB    | 505.41 KiB    | 157.68 KiB| 224.64 KiB | 663.09 KiB  | 9.1.0                |


### Reference **MCU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                     | Format | Resolution | Board             | Execution Engine | Frequency | Inference time (ms) | STM32Cube.AI version |
|---------------------------|--------|------------|-------------------|------------------|-----------|---------------------|----------------------|
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 439.91 ms            | 9.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 145.51 ms            | 9.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  | STM32F769I-DISCO  | 1 CPU            | 216 MHz   | 871.7 ms            | 9.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  | STM32F769I-DISCO  | 1 CPU            | 216 MHz   | 259.5 ms            | 9.1.0                |


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                     | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|---------------------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 36.75 ms            | 16.89 | 83.11 | 0    |   v5.1.0           | OpenVX                |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 14.67 ms            | 32.55 | 67.45 | 0    |   v5.1.0           | OpenVX                |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 140.6 ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 47.50 ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 198.7 ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 63.84 ms            | NA    | NA    | 100  |   v5.1.0           | TensorFlowLite 2.11.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### Accuracy with Flowers dataset
Dataset details: http://download.tensorflow.org/example_images/flower_photos.tgz , License CC - BY 2.0
Number of classes: 5, 3670 files

| Model                     | Format | Resolution | Top 1 Accuracy (%) |
|---------------------------|--------|------------|--------------------|
| ST EfficientNet LC v1 tfs | Float  | 224x224x3  | 90.19              |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  | 89.92              |
| ST EfficientNet LC v1 tfs | Float  | 128x128x3  | 87.19              |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  | 86.78              |


### Accuracy with Plant dataset
Dataset details: https://data.mendeley.com/datasets/tywbtsjrjv/1 , License CC0 1.0
Number of classes: 39, number of files: 55448

| Model                     | Format | Resolution | Top 1 Accuracy (%) |
|---------------------------|--------|------------|--------------------|
| ST EfficientNet LC v1 tfs | Float  | 224x224x3  | 99.86              |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  | 99.78              |
| ST EfficientNet LC v1 tfs | Float  | 128x128x3  | 99.76              |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  | 99.63              |


### Accuracy with Food-101 dataset
Dataset details: https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/,
Number of classes: 101, number of files: 101000

| Model                     | Format | Resolution | Top 1 Accuracy (%) |
|---------------------------|--------|------------|--------------------|
| ST EfficientNet LC v1 tfs | Float  | 224x224x3  | 73.78              |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3  | 73.1               |
| ST EfficientNet LC v1 tfs | Float  | 128x128x3  | 64.02              |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3  | 62.71              |


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
