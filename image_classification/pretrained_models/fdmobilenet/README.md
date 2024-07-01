# Fd-MobileNet

## **Use case** : [Image classification](../README.md)

# Model description
Fd-MobileNet stands for Fast-downsampling MobileNet. It was initially introduced in this [paper](https://arxiv.org/pdf/1802.03750.pdf).
This family of networks, inspired from Mobilenet, provides a good accuracy on various image classification tasks for very limited computational budgets.
Thus it is an interesting solution for deep learning at the edge.
As stated by the authors, the key idea is to apply a fast downsampling strategy to MobileNet framework with only half the layers of the original MobileNet. This design remarkably reduces the computational cost as well as the inference time.

The hyperparameter 'alpha' controls the width of the network, also denoted as width multiplier. It proportionally adjusts each layer width.
Authorized values for 'alpha' are 0.25, 0.5, 0.75, 1.0.
The model is quantized in int8 using Tensorflow Lite converter.

Performances of a ST custom model derived from Fd-MobileNet is also proposed below. It is named ST FdMobileNet v1.
It is inspired from original FdMobilenet. Instead of having one unique 'alpha' dimensioning the width of the network, we
use a list of 'alpha' values in order to give more or less importance to each of the individual sub-blocks.
It is slightly more complex than FdMobilenet 0.25 due to higher number of channels for some sub-blocks but provides
better accuracies. We believe it is a good compromise between size, complexity and accuracy for this family of networks.

## Network information
| Network Information     | Value                                |
|-------------------------|--------------------------------------|
|  Framework              | TensorFlow Lite                      |
|  Params alpha=0.25      | 125477                               |
|  Quantization           | int8                                 |
|  Paper                  | https://arxiv.org/pdf/1802.03750.pdf |

The models are quantized using tensorflow lite converter.

## Network inputs / outputs
For an image resolution of NxM and P classes and 0.25 alpha parameter :

| Input Shape   | Description                                              |
|---------------|----------------------------------------------------------|
| (1, N, M, 3)  | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape  | Description                                              |
|---------------|----------------------------------------------------------|
| (1, P)        | Per-class confidence for P classes                       |


## Recommended platform
| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | [x]       | []          |
| STM32U5  | [x]       | []          |
| STM32MP1 | [x]       | [x]         |
| STM32MP2 | [x]       | []          |

---
# Performances
## Training
To train a FdMobileNet 0.25 model from scratch on your own dataset, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/README.md) under the src section.

As an example, [fdmobilenet_0.25_224_config_tfs.yaml](./ST_pretrainedmodel_public_dataset/flowers/fdmobilenet_0.25_224_tfs/fdmobilenet_0.25_224_tfs_config.yaml) file is used to train this model on flowers dataset, you can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the src section to reproduce the results presented below.
For ST FdMobileNet v1, just consider [st_fdmobilenet_v1_224_tfs_config.yaml](./ST_pretrainedmodel_public_dataset/flowers/st_fdmobilenet_v1_224_tfs/st_fdmobilenet_v1_224_tfs_config.yaml) instead.

## Deployment
To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md) under the deployment section.

## Metrics
Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **MCU** memory footprints based on Flowers dataset (see Accuracy for details on dataset)
| Model                 | Format | Resolution   | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM  | Total Flash | STM32Cube.AI version |
|-----------------------|--------|--------------|---------|----------------|-------------|---------------|------------|------------|-------------|----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | STM32H7 | 157.03 KiB     | 14.25 KiB   | 128.32 KiB    | 58.66 KiB  | 171.28 KiB  | 186.98 KiB  | 9.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32H7 | 211.64 KiB     | 14.25 KiB   | 144.93 KiB    | 60.17 KiB  | 225.89 KiB | 205.1 KiB    | 9.1.0                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | STM32H7 | 56.16 KiB      | 14.2 KiB    | 128.32 KiB    | 58.16 KiB  | 70.36 KiB  | 186.95 KiB   | 9.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32H7 | 74.23 KiB      | 14.2 KiB    | 144.93 KiB    | 60.12 KiB  | 88.43 KiB  | 205.05 KiB   | 9.1.0                |


### Reference **MCU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                 | Format | Resolution   | Board            | Execution Engine | Frequency     | Inference time (ms) | STM32Cube.AI version |
|-----------------------|--------|--------------|------------------|------------------|---------------|---------------------|----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 53.52 ms            | 9.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 102 ms              | 9.1.0                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 17.73 ms            | 9.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 32.14 ms            | 9.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz       | 176.5 ms            | 9.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz       | 59.29 ms            | 9.1.0                |


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                 | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|-----------------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 6.60  ms            | 12.28 | 87.72 |  0   | v5.1.0             | OpenVX                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 7.84  ms            | 10.82 | 89.19 |  0   | v5.1.0             | OpenVX                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 2.17  ms            | 15.66 | 84.34 |  0   | v5.1.0             | OpenVX                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 2.85  ms            | 12.75 | 87.25 |  0   | v5.1.0             | OpenVX                |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 22.76 ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 33.93 ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 8.08  ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 13.16 ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 33.50 ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 61.00 ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 10.86 ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 19.43 ms            | NA    | NA    |  100 | v5.1.0             | TensorFlowLite 2.11.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### Accuracy with Flowers dataset
Dataset details: http://download.tensorflow.org/example_images/flower_photos.tgz , License CC - BY 2.0
Number of classes: 5, 3670 files

| Model                 | Format | Resolution   | Top 1 Accuracy (%)   |
|-----------------------|--------|--------------|----------------------|
| FdMobileNet 0.25 tfs  | Float  | 224x224x3    | 86.92                |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | 87.06                |
| ST FdMobileNet v1 tfs | Float  | 224x224x3    | 89.51                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | 88.83                |
| FdMobileNet 0.25 tfs  | Float  | 128x128x3    | 84.6                 |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | 84.2                 |
| ST FdMobileNet v1 tfs | Float  | 128x128x3    | 87.87                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | 87.6                 |


### Accuracy with Plant dataset
Dataset details: https://data.mendeley.com/datasets/tywbtsjrjv/1 , License CC0 1.0
Number of classes: 39, number of files: 55448

| Model                 | Format | Resolution   | Top 1 Accuracy (%)   |
|-----------------------|--------|--------------|----------------------|
| FdMobileNet 0.25 tfs  | Float  | 224x224x3    | 99.9                 |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | 99.8                 |
| ST FdMobileNet v1 tfs | Float  | 224x224x3    | 99.59                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | 99.4                 |
| FdMobileNet 0.25 tfs  | Float  | 128x128x3    | 99.05                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | 98.55                |
| ST FdMobileNet v1 tfs | Float  | 128x128x3    | 99.58                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | 99.8                 |


### Accuracy with Food-101 dataset
Dataset details: https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/,
Number of classes: 101, number of files: 101000

| Model                 | Format | Resolution   | Top 1 Accuracy (%)   |
|-----------------------|--------|--------------|----------------------|
| FdMobileNet 0.25 tfs  | Float  | 224x224x3    | 59.9                 |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | 58                   |
| ST FdMobileNet v1 tfs | Float  | 224x224x3    | 65.41                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | 63.67                |
| FdMobileNet 0.25 tfs  | Float  | 128x128x3    | 45.53                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | 44.63                |
| ST FdMobileNet v1 tfs | Float  | 128x128x3    | 54.5                 |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | 53.46                |


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
