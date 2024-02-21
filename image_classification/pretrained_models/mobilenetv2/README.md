# MobileNet v2

## **Use case** : [Image classification](../README.md)

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

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  MParams alpha=0.35      | 1.66 M          |
|  Quantization           | int8            |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/mobilenet_v2 |
|  Paper                  | https://arxiv.org/pdf/1801.04381.pdf |

The models are quantized using tensorflow lite converter.


## Network inputs / outputs


For an image resolution of NxM and P classes

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, P) | Per-class confidence for P classes in FLOAT32|


## Recommended platforms


| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[x]|[]|
| STM32U5  |[x]|[]|
| STM32H7  |[x]|[x]|
| STM32MP1 |[x]|[x]|


# Performances
## Training


To train a MobileNet v2 model with pretrained weights, from scratch or finetune it on your own dataset, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../README.md) under the src  section.

As an example, [mobilenet_v2_0.35_224_tfs_config.yaml](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs_config.yaml) file is used to train this model from scratch on flowers dataset. You can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the src section to reproduce the results presented below.

## Deployment

To deploy your trained model, you need to configure the same [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md).


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8   | 128x128x3    | STM32H7 | 225.17 KiB     | 32.83 KiB       | 406.86 KiB    | 115.14 KiB       | 258 KiB   | 522 KiB  | 8.1.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 686.5 KiB     | 32.88 KiB       | 406.86 KiB    | 115.26 KiB    | 719.38 KiB   | 522.12 KiB  | 8.1.0    |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|-----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8   | 128x128x3   | STM32H747I-DISCO | 1 CPU | 400 MHz       | 101.11  ms      | 8.1.0                 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU | 400 MHz       | 363.82 ms       | 8.1.0                |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8   | 128x128x3   | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 47.57  ms **    | X-LINUX-AI v5.0.0     |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | Int8   | 224x224x3   | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 141.92 ms **    | X-LINUX-AI v5.0.0     |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs.h5) | Float | 128x128x3    | 87.06 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs_int8.tflite) | Int8 | 128x128x3    | 87.47 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl.h5) | Float | 128x128x3    | 88.15 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl_int8.tflite) | Int8 | 128x128x3    | 88.01 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft.h5) | Float | 128x128x3    | 91.83 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8 | 128x128x3    | 91.01 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs.h5) | Float | 224x224x3    | 88.69 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs_int8.tflite) | Int8 | 224x224x3    | 88.83 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl.h5) | Float | 224x224x3    | 88.96 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl_int8.tflite) | Int8 | 224x224x3    | 88.01 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft.h5) | Float | 224x224x3    | 93.6 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | Int8 | 224x224x3    | 92.78 % |


### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs.h5) | Float | 128x128x3    | 99.86 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs_int8.tflite) | Int8 | 128x128x3    | 99.83 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl.h5) | Float | 128x128x3    | 93.51 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl_int8.tflite) | Int8 | 128x128x3    | 92.33 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft.h5) | Float | 128x128x3    | 99.77 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8 | 128x128x3    | 99.48 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs.h5) | Float | 224x224x3    | 99.86 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs_int8.tflite) | Int8 | 224x224x3    | 99.81 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl.h5) | Float | 224x224x3    | 93.62 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl_int8.tflite) | Int8 | 224x224x3    | 92.8 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft.h5) | Float | 224x224x3    | 99.95 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | Int8 | 224x224x3    | 99.68 % |


### Accuracy with Food-101 dataset


Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) , License [-](), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs.h5) | Float | 128x128x3    | 62.15 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs_int8.tflite) | Int8 | 128x128x3    | 61.31 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl.h5) | Float | 128x128x3    | 44.74 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl_int8.tflite) | Int8 | 128x128x3    | 42.01 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft.h5) | Float | 128x128x3    | 63.78 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8 | 128x128x3    | 62.28 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs.h5) | Float | 224x224x3    | 72.31 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs_int8.tflite) | Int8 | 224x224x3    | 72.05 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl.h5) | Float | 224x224x3    | 49.01 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl_int8.tflite) | Int8 | 224x224x3    | 47.26 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft.h5) | Float | 224x224x3    | 74.14 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | Int8 | 224x224x3    | 73.3 % |

### Accuracy with person dataset


The person dataset is derived from COCO-2014 and created using the script here (link). The dataset folder has 2 sub-folders — person and notperson containing images of the respective types
Dataset details: [link](https://cocodataset.org/) , License [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Quotation[[3]](#3)  , Number of classes: 2 , Number of images: 84810


| Model                                                                                                                                                          | Format | Resolution | Top 1 Accuracy |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|-----------|----------------|
| [MobileNet v2 0.35 tfs](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs.h5)                                    | Float  | 128x128x3   | 92.56 % |
| [MobileNet v2 0.35 tfs](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs_int8.tflite)                           | Int8   | 128x128x3   | 92.44 % |
| [MobileNet v2 0.35 tl ](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl.h5)         | Float  | 128x128x3   | 92.28 % |
| [MobileNet v2 0.35 tl](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl_int8.tflite) | Int8   | 128x128x3   | 91.63 % |
| [MobileNet v2 0.35 fft ](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft.h5)         | Float  | 128x128x3   | 95.37 % |
| [MobileNet v2 0.35 fft](../mobilenetv2/ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8   | 128x128x3   | 94.95 % |


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