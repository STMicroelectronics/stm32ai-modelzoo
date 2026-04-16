# Fd-MobileNet

## **Use case** : `Image classification`

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
| STM32H7  | [x]       | [x]         |
| STM32MP1 | [x]       | [x]         |
| STM32MP2 | [x]       | []          |
| STM32N6  | [x]       | []          |

---
# Performances

## Metrics

* Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
* `tfs` stands for "training from scratch", meaning that the model weights are randomly initialized before the training and all layers are actually trained.

### Reference **NPU** memory footprint on food101 dataset (see Accuracy for details on dataset)
|Model      |  Format   | Resolution | Series    | Internal RAM (KiB)| External RAM (KiB)| Weights Flash (KiB) | STEdgeAI Core version |
|----------|--------|-------------|------------------|------------------|---------------------|---------------------|----------------------|
| [FdMobileNet 0.25 tfs](ST_pretrainedmodel_public_dataset/food101/fdmobilenet_a025_224_tfs/fdmobilenet_a025_224_tfs_int8.tflite)  |  Int8     | 224x224x3  | STM32N6   | 294 |0.0| 148.34           | 4.0.0 |
| [ST FdMobileNet v1 tfs](ST_pretrainedmodel_public_dataset/food101/st_fdmobilenetv1_224_tfs/st_fdmobilenetv1_224_tfs_int8.tflite)  | Int8     | 224x224x3  | STM32N6   | 343 | 0.0 | 167.2              | 4.0.0 |
| [FdMobileNet 0.25 tfs](ST_pretrainedmodel_public_dataset/food101/fdmobilenet_a025_128_tfs/fdmobilenet_a025_128_tfs_int8.tflite)  | Int8     | 128x128x3  | STM32N6   | 96 | 0.0 | 146.66              | 4.0.0 |
| [ST FdMobileNet v1 tfs](ST_pretrainedmodel_public_dataset/food101/st_fdmobilenetv1_128_tfs/st_fdmobilenetv1_128_tfs_int8.tflite)   | Int8     | 128x128x3  | STM32N6   | 112 | 0.0 | 163.83              | 4.0.0 |


### Reference **NPU**  inference time on food101 dataset (see Accuracy for details on dataset)
| Model  |  Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   |  STEdgeAI Core version |
|--------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|
| [FdMobileNet 0.25 tfs](ST_pretrainedmodel_public_dataset/food101/fdmobilenet_a025_224_tfs/fdmobilenet_a025_224_tfs_int8.tflite)  |  Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 1.29 | 775.19 |     4.0.0   |
| [ST FdMobileNet v1 tfs](ST_pretrainedmodel_public_dataset/food101/st_fdmobilenetv1_224_tfs/st_fdmobilenetv1_224_tfs_int8.tflite)   |  Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 1.67 | 598.8 |     4.0.0   |
| [FdMobileNet 0.25 tfs](ST_pretrainedmodel_public_dataset/food101/fdmobilenet_a025_128_tfs/fdmobilenet_a025_128_tfs_int8.tflite)  |  Int8     |  128x128x3  | STM32N6570-DK   |   NPU/MCU      | 0.75 | 1333.33 |     4.0.0   |
| [ST FdMobileNet v1 tfs](ST_pretrainedmodel_public_dataset/food101/st_fdmobilenetv1_128_tfs/st_fdmobilenetv1_128_tfs_int8.tflite)   |  Int8     |  128x128x3  | STM32N6570-DK   |   NPU/MCU      | 0.9 | 1111.11 |      4.0.0   |


### Reference **MCU** memory footprints based on Flowers dataset (see Accuracy for details on dataset)
| Model                 | Format | Resolution   | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM  | Total Flash | STEdgeAI Core version |
|-----------------------|--------|--------------|---------|----------------|-------------|---------------|------------|------------|-------------|-----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | STM32H7 | 157.03 KiB     | 0.3 KiB     | 128.32 KiB    | 29.99 KiB  | 157.33 KiB | 158.31 KiB  | 4.0.0                 |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32H7 | 211.64 KiB     | 0.3 KiB     | 144.93 KiB    | 31.18 KiB  | 211.94 KiB | 176.11 KiB  | 4.0.0                 |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | STM32H7 | 56.16 KiB      | 0.3 KiB     | 128.32 KiB    | 29.95 KiB  | 56.46 KiB  | 158.27 KiB  | 4.0.0                 |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32H7 | 74.23 KiB      | 0.3 KiB     | 144.93 KiB    | 31.13 KiB  | 74.53 KiB  | 176.06 KiB  | 4.0.0                 |


### Reference **MCU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                 | Format | Resolution   | Board            | Execution Engine | Frequency     | Inference time (ms) | STEdgeAI Core version |
|-----------------------|--------|--------------|------------------|------------------|---------------|---------------------|-----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 54.38 ms            | 4.0.0                 |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 103.5 ms            | 4.0.0                 |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 18.03 ms            | 4.0.0                 | 
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 32.66 ms            | 4.0.0                 | 
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz       | 170.2 ms            | 4.0.0                 | 
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz       | 53.73 ms            | 4.0.0                 | 


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)

| Model                 | Format | Resolution | Quantization    | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|-----------------------|--------|------------|-----------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3  | per-channel**   | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 6.48                | 15.25 | 84.75 | 0    | v6.1.0             | OpenVX                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3  | per-channel**   | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 7.82                | 16.29 | 83.71 | 0    | v6.1.0             | OpenVX                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3  | per-channel**   | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 2.01                | 18.25 | 81.75 | 0    | v6.1.0             | OpenVX                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3  | per-channel**   | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 2.78                | 13.80 | 86.20 | 0    | v6.1.0             | OpenVX                |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3  | per-channel     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 24.96               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3  | per-channel     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 43.05               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3  | per-channel     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 8.96                | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3  | per-channel     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 14.19               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3  | per-channel     | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 34.86               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3  | per-channel     | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 63.78               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3  | per-channel     | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 11.86               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3  | per-channel     | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 20.34               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

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
| FdMobileNet 0.25 tfs  | Float  | 224x224x3    | 63.03                |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | 62.11                |
| ST FdMobileNet v1 tfs | Float  | 224x224x3    | 69.31                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | 68.73                |
| FdMobileNet 0.25 tfs  | Float  | 128x128x3    | 51.12                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | 50.26                |
| ST FdMobileNet v1 tfs | Float  | 128x128x3    | 59.07                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | 58.15                |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.
