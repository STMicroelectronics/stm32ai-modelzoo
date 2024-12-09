# Squeezenet v1.1

## **Use case** : `Image classification`

# Model description
SqueezeNet is a convolutional neural network that uses design strategies to reduce the number of parameters, particularly with the use of fire modules that "squeeze" parameters using 1x1 convolutions.
SqueezeNet 1.1 has 2.4x less computation and slightly fewer parameters than SqueezeNet 1.0, without sacrifying accuracy.

The model is quantized in int8 using tensorflow lite converter.


## Network information


| Network Information | Value                                  |
|---------------------|----------------------------------------|
| Framework           | TensorFlow Lite                        |
| MParams             | 725,061                                |
| Quantization        | int8                                   |
| Provenance          | https://github.com/forresti/SqueezeNet |
| Paper               | https://arxiv.org/pdf/1602.07360.pdf   |

The models are quantized using tensorflow lite converter.


## Network inputs / outputs


For an image resolution of NxM and P classes

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, P) | Per-class confidence for P classes in FLOAT32|


## Recommended Platforms


| Platform | Supported | Optimized |
|----------|-----------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[x]|[]|
| STM32U5  |[x]|[]|
| STM32H7  |[x]|[x]|
| STM32MP1 |[x]|[]|
| STM32MP2 |[x]|[]|
| STM32N6  |[x]|[]|

# Performances

## Metrics

- Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
- `tfs` stands for "training from scratch", meaning that the model weights were randomly initialized before training.


### Reference **NPU** memory footprint on food-101 dataset (see Accuracy for details on dataset)
|Model      |  Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STM32Cube.AI version | STEdgeAI Core version |
|----------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite)  |  Int8     | 128x128x3  | STM32N6   | 270.28 | 0.0 | 772.16 |       10.0.0        |     2.0.0   |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite)  | Int8     | 224x224x3  | STM32N6   | 858.23 | 0.0 | 772.16 |       10.0.0        |     2.0.0   |

### Reference **NPU**  inference time on food-101 dataset (see Accuracy for details on dataset)
| Model  |  Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) |  Int8     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      |3.74|267.38|       10.0.0        |     2.0.0   |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite)  |  Int8     |  224x224x3  | STM32N6570-DK   |   NPU/MCU      |7.75|129.03|       10.0.0        |     2.0.0   |


### Reference **MCU** memory footprint based on Flowers dataset (see Accuracy for details on dataset)
| Model                                                                                                                               | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM     | Total Flash | STM32Cube.AI version  |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------|----------------|-------------|--------------|------------|---------------|-------------|-----------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8   | 128x128x3    | STM32H7 | 271.84 KiB     | 16.47 KiB     | 716.71 KiB   | 78.24 KiB   | 288.31 KiB   | 789.55 KiB | 10.0.0                 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite)  | Int8   | 224x224x3    | STM32H7 | 816.86 KiB     | 16.51 KiB    | 716.71 KiB   | 71.42 KiB   | 833.37  KiB     | 788.13 KiB    | 10.0.0                 |


### Reference **MCU** inference time based on Flowers dataset (see Accuracy for details on dataset)


| Model                                                                                                                               | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) | STM32Cube.AI version  |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|------------|------------------|---------------|-----------|---------------------|-----------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU | 400 MHz   | 216.67 ms            | 10.0.0                 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz   | 693.3 ms            | 10.0.0                 |


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model                                                                                                                         |  Format  | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|-------------------------------------------------------------------------------------------------------------------------------|----------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8     | 128x128x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 9.72  ms            | 8.45  | 91.55 | 0    | v5.1.0             | OpenVX                |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite) | Int8     | 224x224x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 31.11 ms            | 8.23  | 91.77 | 0    | v5.1.0             | OpenVX                |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8     | 128x128x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 44.92 ms            | NA    | NA    | 100  | v5.1.0             | TensorFlowLite 2.11.0 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite) | Int8     | 224x224x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 147.80 ms           | NA    | NA    | 100  | v5.1.0             | TensorFlowLite 2.11.0 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8     | 128x128x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 70.16 ms            | NA    | NA    | 100  | v5.1.0             | TensorFlowLite 2.11.0 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite) | Int8     | 224x224x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 234.80 ms           | NA    | NA    | 100  | v5.1.0             | TensorFlowLite 2.11.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model   | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|--------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs.h5)          | Float  | 224x224x3    | 85.29 %      |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite) | Int8   | 224x224x3    | 83.24 %      |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs.h5)          | Float  | 128x128x3    | 80.93  %     |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8   | 128x128x3    | 80.93 %      |


### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[3]](# 3)  , Number of classes: 101 , Number of images:  101 000


| Model   | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|----------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs.h5)          | Float  | 224x224x3    | 67.15 % |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite) | Int8   | 224x224x3    | 66.71 % |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs.h5)          | Float  | 128x128x3    |  58.55 % |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8   | 128x128x3    | 58.51 % |


### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model   | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|---------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs.h5)          | Float  | 224x224x3    | 99.88 %       |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_224_tfs/squeezenetv1.1_224_tfs_int8.tflite) | Int8   | 224x224x3    | 99.74 %       |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs.h5)          | Float  | 128x128x3    | 99.77 %       |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_128_tfs/squeezenetv1.1_128_tfs_int8.tflite) | Int8   | 128x128x3    | 99.69 %       |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.
