# MobileNet v2 quantized

## **Use case** : [Image Classification](../../../image_classification/README.md)

# Model description


MobileNet v2 is very similar to the original MobileNet, except that it uses inverted residual blocks with bottlenecking features.

It has a drastically lower parameter count than the original MobileNet.

MobileNet models support any input size greater than 32 x 32, with larger image sizes offering better performance.
Alpha parameter: float, larger than zero, controls the width of the network. This is known as the width multiplier in the MobileNetV2 paper, but the name is kept for consistency with applications.

If alpha < 1.0, proportionally decreases the number of filters in each layer.

If alpha > 1.0, proportionally increases the number of filters in each layer.

If alpha = 1.0, default number of filters from the paper are used at each layer.

(source: https://keras.io/api/applications/mobilenet/)

The model is quantized in int8 using tensorflow lite converter.

## Network Information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  MParams alpha=0.35      | 1.66 M          |
|  Quantization           | int8            |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/mobilenet_v2 |
|  Paper                  | https://arxiv.org/pdf/1801.04381.pdf |

The models are quantized using tensorflow lite converter.


## Network Inputs / Outputs


For an image resolution of NxM and P classes

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, P) | Per-class confidence for P classes in FLOAT32|


## Recommended Platforms


| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[x]|[]|
| STM32U5  |[x]|[]|
| STM32H7  |[x]|[x]|
| STM32MP1 |[x]|[x]|


# Performances
## Training


To train a MobileNet v2 model with pretrained weights or from scratch on your own dataset, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [mobilenet_v2_0.35_224_config.yaml](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_config.yaml) file is used to train this model on flowers dataset, you can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below.

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../scripts/deployment/user_config.yaml) file following the [tutorial](../../scripts/deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI (v7.3.0) configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | Int8   | 128x128    | STM32H7 | 224.5 KiB     | ~37 KiB       | 406.86 KiB    | ~123 KiB       | 261.92 KiB   | 529.2 KiB  |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | Int8   | 224x224    | STM32H7 | 686.5 KiB     | ~37 KiB       | 406.86 KiB    | ~123 KiB    | 723.92 KiB   | 529.36 KiB  |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | Int8   | 128x128   | STM32H747I-DISCO | 1 CPU | 400 MHz       | 110.27  ms      |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | Int8   | 224x224   | STM32H747I-DISCO | 1 CPU | 400 MHz       | 392.92 ms       |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | Int8   | 128x128   | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 47.57  ms **    |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | Int8   | 224x224   | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 141.92 ms **    |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128.h5) | Float | 128x128    | 86.78 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | Int8 | 128x128    | 86.38 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224.h5) | Float | 224x224    | 89.78 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | Int8 | 224x224    | 89.37 % |


### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128.h5) | Float | 128x128    | 91.75 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | Int8 | 128x128    | 91.35 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224.h5) | Float | 224x224    | 92.12 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | Int8 | 224x224    | 91.62 % |


### Accuracy with Food-101 dataset


Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) , License [-](), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128.h5) | Float | 128x128    | 43.43 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | Int8 | 128x128    | 41.58 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224.h5) | Float | 224x224    | 49.35 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | Int8 | 224x224    | 48.67 % |

### Accuracy with person dataset


The person dataset is derived from COCO-2014 and created using the script here (link). The dataset folder has 2 sub-folders — person and notperson containing images of the respective types
Dataset details: [link](https://cocodataset.org/) , License [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Quotation[[3]](#3)  , Number of classes: 2 , Number of images: 84810


| Model                                                                                                                                                          | Format | Resolution | Top 1 Accuracy |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|-----------|----------------|
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128.h5)                                    | Float  | 128x128   | 91.45 % |
| [MobileNet v2 0.35](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite)                           | Int8   | 128x128   | 91.05 % |
| [MobileNet v2 0.35 training from scratch ](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128.h5)         | Float  | 128x128   | 86.27 % |
| [MobileNet v2 0.35 training from scratch](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_int8.tflite) | Int8   | 128x128   | 86.22 % |


## Retraining and code generation


- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../scripts/deployment/README.md)


## Demos
### Integration in a simple example


Please refer to the generic guideline [here](../../scripts/deployment/README.md).



# References

<a id="1">[1]</a>
“Tf_flowers : tensorflow datasets,” TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), “Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network”, Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
@inproceedings{bossard14,
  title = {Food-101 -- Mining Discriminative Components with Random Forests},
  author = {Bossard, Lukas and Guillaumin, Matthieu and Van Gool, Luc},
  booktitle = {European Conference on Computer Vision},
  year = {2014}
}
