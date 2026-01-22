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


### Reference **NPU** memory footprint on food101 dataset (see Accuracy for details on dataset)
|Model      |  Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STEdgeAI Core version |
|----------|--------|-------------|------------------|------------------|---------------------|---------------|-------------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite)  |  Int8     | 128x128x3  | STM32N6   | 240.25 | 0.0 | 753.38        |     3.0.0   |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite)  | Int8     | 224x224x3  | STM32N6   | 803.52 | 0.0 | 753.38        |     3.0.0   |

### Reference **NPU**  inference time on food101 dataset (see Accuracy for details on dataset)
| Model  |  Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|--------|-------------|------------------|------------------|---------------------|-----------|-------------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) |  Int8     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      | 3.82                | 261.78     |     3.0.0   |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite)  |  Int8     |  224x224x3  | STM32N6570-DK   |   NPU/MCU      | 7.97                 | 125.47    |     3.0.0   |


### Reference **MCU** memory footprint based on Flowers dataset (see Accuracy for details on dataset)
| Model                                                                                                                               | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STEdgeAI Core version  |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------|----------------|-------------|--------------|------------|-------------|-------------|-----------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3    | STM32H7 | 271.84 KiB     | 3.72 KiB   | 716.71 KiB   | 45.79 KiB  | 275.56 KiB  | 762.5 KiB  | 3.0.0                 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite)  | Int8   | 224x224x3    | STM32H7 | 829.09 KiB     | 3.72 KiB   | 716.71 KiB   | 45.85 KiB   | 832.81  KiB | 762.56 KiB  | 3.0.0                 |


### Reference **MCU** inference time based on Flowers dataset (see Accuracy for details on dataset)


| Model                                                                                                                               | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) | STEdgeAI Core version  |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|------------|------------------|---------------|-----------|---------------------|-----------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU | 400 MHz   | 218.97 ms           | 3.0.0                 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz   | 704.22 ms           | 3.0.0                 |


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)

| Model                                                                                                                         | Format | Resolution | Quantization   | Board           | Execution Engine | Frequency | Inference time (ms) | %NPU | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|-------------------------------------------------------------------------------------------------------------------------------|--------|------------|----------------|-----------------|------------------|-----------|---------------------|------|-------|------|--------------------|-----------------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3  | per-channel**  | STM32MP257F-DK2 | NPU/GPU          | 800 MHz   | 9.41                | 9.70 | 90.30 | 0    | v6.1.0             | OpenVX                |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite) | Int8   | 224x224x3  | per-channel**  | STM32MP257F-DK2 | NPU/GPU          | 800 MHz   | 30.93               | 8.45 | 91.55 | 0    | v6.1.0             | OpenVX                |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3  | per-channel    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 45.27               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite) | Int8   | 224x224x3  | per-channel    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 145.33              | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3  | per-channel    | STM32MP135F-DK2 | 1 CPU            | 1000 MHz  | 71.93               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite) | Int8   | 224x224x3  | per-channel    | STM32MP135F-DK2 | 1 CPU            | 1000 MHz  | 235.63              | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model   | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|--------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_128_tfs/squeezenetv11_128_tfs.keras)          | Float  | 128x128x3    | 80.93  %     |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3    | 80.93 %      |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_224_tfs/squeezenetv11_224_tfs.keras)          | Float  | 224x224x3    | 85.29 %      |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/tf_flowers/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite) | Int8   | 224x224x3    | 83.24 %      |

### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[3]](# 3)  , Number of classes: 101 , Number of images:  101 000


| Model   | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|----------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_128_tfs/squeezenetv11_128_tfs.keras)          | Float  | 128x128x3    | 60.28 % |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3    | 60.17 % |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_224_tfs/squeezenetv11_224_tfs.keras)          | Float  | 224x224x3    | 68.08 % |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/food101/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite) | Int8   | 224x224x3    | 67.3 % |


### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model   | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|---------------|
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/squeezenetv11_128_tfs/squeezenetv11_128_tfs.keras)          | Float  | 128x128x3    | 99.77 %       |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/squeezenetv11_128_tfs/squeezenetv11_128_tfs_int8.tflite) | Int8   | 128x128x3    | 99.69 %       |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/squeezenetv11_224_tfs/squeezenetv11_224_tfs.keras)          | Float  | 224x224x3    | 99.88 %       |
| [SqueezeNet v1.1 tfs ](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/squeezenetv11_224_tfs/squeezenetv11_224_tfs_int8.tflite) | Int8   | 224x224x3    | 99.74 %       |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.
