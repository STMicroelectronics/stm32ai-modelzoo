# Squeezenet v1.1 quantized

## **Use case** : [Image classification](../../../image_classification/README.md)

# Model description
SqueezeNet is a convolutional neural network that employs design strategies to reduce the number of parameters, notably with the use of fire modules that "squeeze" parameters using 1x1 convolutions.
SqueezeNet 1.1 has 2.4x less computation and slightly fewer parameters than SqueezeNet 1.0, without sacrificing accuracy.

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


# Performances
## Training


  To train a SqueezeNet v1.1 model with pretrained weights or from scratch on your own dataset, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [squeezenet_v1.1_128_config.yaml](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128/squeezenet_v1.1_128_config.yaml) file is used to train this model on flowers dataset.

## Deployment


To deploy your trained model, you need to configure the [user_config.yaml](../../scripts/deployment/user_config.yaml) file following the [tutorial](../../scripts/deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI (v7.3.0) configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on Flowers dataset (see Accuracy for details on dataset)


| Model                                                                                                                               | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM     | Total Flash |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------|----------------|-------------|--------------|------------|---------------|-------------|
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128/squeezenet_v1.1_128_int8.tflite) | Int8   | 128x128x3    | STM32H7 | 240.25 KiB     | ~18 KiB     | 716.70 KiB   | ~77  KiB   | ~261.13 KiB   | ~792.01 KiB |
| [SqueezeNet v1.1 ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224/squeezenet_v1.1_224_int8.tflite)  | Int8   | 224x224x3    | STM32H7 | 756.25 KiB     | ~ 18 KiB    | 716.71 KiB   | ~ 77 KiB   | ~775  KiB     | ~793 KiB    |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)


| Model                                                                                                                               | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|------------|------------------|---------------|-----------|---------------------|
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128/squeezenet_v1.1_128_int8.tflite) | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU | 400 MHz   | 277.3 ms            |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224/squeezenet_v1.1_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz   | 977.8 ms            |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224/squeezenet_v1.1_224_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz   | 224.2 ms **         |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model                                                                                                                               | Format | Resolution | Top 1 Accuracy |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|------------|--------------|
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224/squeezenet_v1.1_224.h5)          | Float  | 224x224x3    | 81.06 %      |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_224/squeezenet_v1.1_224_int8.tflite) | Int8   | 224x224x3    | 80.93 %      |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128/squeezenet_v1.1_128.h5)          | Float  | 128x128x3    | 79.02  %     |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/flowers/squeezenetv1.1_128/squeezenet_v1.1_128_int8.tflite) | Int8   | 128x128x3    | 77.93 %      |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=100' and ReduceLROnPlateau 'patience=80'.

### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) , License [-](), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000


| Model                                                                                                                                | Format | Resolution | Top 1 Accuracy |
|--------------------------------------------------------------------------------------------------------------------------------------|--------|------------|----------------|
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_128/squeezenet_v1.1_128.h5)          | Float  | 128x128x3    |  52.72 % |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_128/squeezenet_v1.1_128_int8.tflite) | Int8   | 128x128x3    | 52.18 % |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_224/squeezenet_v1.1_224.h5)          | Float  | 224x224x3    | 56.9 % |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/food-101/squeezenetv1.1_224/squeezenet_v1.1_224_int8.tflite) | Int8   | 224x224x3    | 56.43 % |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=100' and ReduceLROnPlateau 'patience=80'.


### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model                                                                                                                                     | Format | Resolution | Top 1 Accuracy |
|-------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------------|
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_224/squeezenet_v1.1_224.h5)          | Float  | 224x224x3    | 99.48 %       |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_224/squeezenet_v1.1_224_int8.tflite) | Int8   | 224x224x3    | 99.32 %       |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_128/squeezenet_v1.1_128.h5)          | Float  | 128x128x3    | 99.16 %       |
| [SqueezeNet v1.1  ](../squeezenetv1.1/ST_pretrainedmodel_public_dataset/plant-village/squeezenetv1.1_128/squeezenet_v1.1_128_int8.tflite) | Int8   | 128x128x3    | 99.04 %       |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=30' and ReduceLROnPlateau 'patience=20'.



## Retraining and code generation

- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../scripts/deployment/README.md)

## Demos

### Integration in simple example

Please refer to the generic guideline [here](../../scripts/deployment/README.md).


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.
