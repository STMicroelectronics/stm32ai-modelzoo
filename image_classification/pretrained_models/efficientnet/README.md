# EfficientNet 

## **Use case** : [Image classification](../README.md)

# Model description
EfficientNet is a family of convolutional networks initially introduced in this [paper](https://arxiv.org/pdf/1905.11946.pdf).
The authors proposed a method that uniformly scales all dimensions depth/width/resolution using a so-called compound coefficient.
Using neural architecture search, the authors created the EfficientNet topology and starting from B0, derived a few variants B1...B7 ordered by increasing complexity.
Its main building blocks are a mobile inverted bottleneck MBConv (Sandler et al., 2018; Tan et al., 2019) and a squeeze-and-excitation optimization (Hu et al., 2018).

EfficientNet provides state-of-the art accuracy on ImageNet and CIFAR for example while being much smaller and faster
than its comparable (ResNet, DenseNet, Inception...). However, for STM32 platforms, B0 is already too large.
That's why, we internally derived a custom version tailored for STM32 and modified it to be quantization-friendly (not discussed in the initial paper).
This custom model is then quantized in int8 using Tensorflow Lite converter.

Performances of the ST custom Efficient Net is also summarized below.

## Network information
| Network Information     | Value                                |
|-------------------------|--------------------------------------|
|  Framework              | TensorFlow Lite                      |
|  Params                 | 517540                               |
|  Quantization           | int8                                 |
|  Paper                  | https://arxiv.org/pdf/1905.11946.pdf |

The model is quantized using tensorflow lite converter.

## Network inputs / outputs
For an image resolution of NxM and P classes:

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

---
# Performances
## Training
Please, Contact Edge.ai@st.com.

## Deployment
Please, Contact Edge.ai@st.com.

## Metrics
Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference MCU memory footprints based on Flowers dataset (see Accuracy for details on dataset)
| Model                     | Format | Resolution   | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM  | Total Flash | STM32Cube.AI version |
|---------------------------|--------|--------------|---------|----------------|-------------|---------------|------------|------------|-------------|----------------------|
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | STM32H7 | 393.17 KiB     | 61.4 KiB    | 505.41 KiB    | 166.45 KiB | 454.57 KiB | 671.86 KiB  | 8.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | STM32H7 | 129.17 KiB     | 61.48 KiB   | 505.41 KiB    | 166.43 KiB | 190.65 KiB | 671.84 KiB  | 8.1.0                |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                     | Format | Resolution   | Board            | Execution Engine | Frequency    | Inference time (ms) | STM32Cube.AI version |
|---------------------------|--------|--------------|------------------|------------------|--------------|---------------------|----------------------|
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 476.5 ms            | 8.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz      | 158.3 ms            | 8.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz      | 848.5 ms            | 8.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | STM32F769I-DISCO | 1 CPU            | 216 MHz      | 285.7 ms            | 8.1.0                |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz      | 138.1 ms **         | X-LINUX-AI v5.0.0    |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz      | 46.8 ms **          | X-LINUX-AI v5.0.0    |


** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Flowers dataset
Dataset details: http://download.tensorflow.org/example_images/flower_photos.tgz , License CC - BY 2.0
Number of classes: 5, 3670 files

| Model                     | Format | Resolution   | Top 1 Accuracy (%) |
|---------------------------|--------|--------------|--------------------|
| ST EfficientNet LC v1 tfs | Float  | 224x224x3    | 90.19              |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | 89.92              |
| ST EfficientNet LC v1 tfs | Float  | 128x128x3    | 87.19              |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | 86.78              |


### Accuracy with Plant dataset
Dataset details: https://data.mendeley.com/datasets/tywbtsjrjv/1 , License CC0 1.0
Number of classes: 39, number of files: 55448

| Model                     | Format | Resolution   | Top 1 Accuracy (%) |
|---------------------------|--------|--------------|--------------------|
| ST EfficientNet LC v1 tfs | Float  | 224x224x3    | 99.86              |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | 99.78              |
| ST EfficientNet LC v1 tfs | Float  | 128x128x3    | 99.76              |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | 99.63              |


### Accuracy with Food-101 dataset
Dataset details: https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/,
Number of classes: 101, number of files: 101000

| Model                     | Format | Resolution   | Top 1 Accuracy (%) |
|---------------------------|--------|--------------|--------------------|
| ST EfficientNet LC v1 tfs | Float  | 224x224x3    | 73.78              |
| ST EfficientNet LC v1 tfs | Int8   | 224x224x3    | 73.1               |
| ST EfficientNet LC v1 tfs | Float  | 128x128x3    | 64.02              |
| ST EfficientNet LC v1 tfs | Int8   | 128x128x3    | 62.71              |


## Retraining and code generation
Please, Contact Edge.ai@st.com.

## Demos
### Integration in a simple example
Please, Contact Edge.ai@st.com.


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.