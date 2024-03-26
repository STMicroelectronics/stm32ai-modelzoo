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
| STM32H7  | [x]       | [x]         |
| STM32MP1 | [x]       | []          |

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

### Reference MCU memory footprints based on Flowers dataset (see Accuracy for details on dataset)
| Model                 | Format | Resolution   | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM  | Total Flash | STM32Cube.AI version |
|-----------------------|--------|--------------|---------|----------------|-------------|---------------|------------|------------|-------------|----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | STM32H7 | 152.05 KiB     | 14.25 KiB   | 128.32 KiB    | 61.71 KiB  | 166.3 KiB  | 190.03 KiB  | 8.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32H7 | 206.88 KiB     | 14.25 KiB   | 144.93 KiB    | 63.19 KiB  | 221.13 KiB | 208.12 KiB  | 8.1.0                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | STM32H7 | 51.18 KiB      | 14.2 KiB    | 128.32 KiB    | 61.71 KiB  | 65.38 KiB  | 190.03 KiB  | 8.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32H7 | 70.75 KiB      | 14.2 KiB    | 144.93 KiB    | 63.2 KiB   | 84.95 KiB  | 208.13 KiB  | 8.1.0                |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                 | Format | Resolution   | Board            | Execution Engine | Frequency     | Inference time (ms) | STM32Cube.AI version |
|-----------------------|--------|--------------|------------------|------------------|---------------|---------------------|----------------------|
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 59.96 ms            | 8.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 112.77 ms           | 8.1.0                |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 19.91 ms            | 8.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 35.74 ms            | 8.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz       | 196.13 ms           | 8.1.0                |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz       | 65.72 ms            | 8.1.0                |
| FdMobileNet 0.25 tfs  | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 23.55 ms **         | X-LINUX-AI v5.0.0    |
| ST FdMobileNet v1 tfs | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 39.48 ms **         | X-LINUX-AI v5.0.0    |
| FdMobileNet 0.25 tfs  | Int8   | 128x128x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 8.53 ms **          | X-LINUX-AI v5.0.0    |
| ST FdMobileNet v1 tfs | Int8   | 128x128x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 13.42 ms **         | X-LINUX-AI v5.0.0    |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0


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
