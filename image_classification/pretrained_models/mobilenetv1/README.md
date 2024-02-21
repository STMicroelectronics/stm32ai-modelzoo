# MobileNet v1

## **Use case** : [Image classification](../README.md)

# Model description


MobileNet is a well known architecture that can be used in multiple use cases.
Input size and width factor called `alpha` are parameters to be adapted to various use cases complexity. The `alpha` parameter is used to increase or decrease the number of filters in each layer, allowing also to reduce the number of multiply-adds and then the inference time.

The original paper demonstrates the performance of MobileNet models using `alpha` values of 1.0, 0.75, 0.5 and 0.25.

(source: https://keras.io/api/applications/mobilenet/)

The model is quantized in int8 using tensorflow lite converter.

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  MParams alpha=1.0      | 1.3 M           |
|  Quantization           | int8            |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/mobilenet |
|  Paper                  | https://arxiv.org/abs/1704.04861 |

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


To train a  MobileNet v1 model with pretrained weights, from scratch or fine tuning on your own dataset, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/README.md) under the src section.

As an example, [mobilenet_v1_0.5_224_tfs_config.yaml](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_tfs/mobilenet_v1_0.5_224_tfs_config.yaml) file is used to train this model from scratch on flowers dataset. You can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the src section to reproduce the results presented below.

## Deployment


To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md).


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 202.33 KiB     | 18.44 KiB      | 214.69 KiB    | 73.79 KiB  | 220.69 KiB   | 288.48 KiB  | 8.1.0  |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 404.66 KiB     | 18.48 KiB    | 812.61 KiB    | 89.36 KiB    | 423.14 KiB   | 899.97 KiB  | 8.1.0 |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_fft/mobilenet_v1_0.25_96_fft_int8.tflite)   | Int8   | 96x96x3    | STM32H7 | 50.2 KiB      | 18.44 KiB     | 214.69 KiB    | 73.88 KiB    | 68.64 KiB    | 288.57 KiB  | 8.1.0                 |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale_tfs/mobilenet_v1_0.25_96_grayscale_tfs_int8.tflite)   | Int8   | 96x96x1    | STM32H7 | 41.21 KiB      | 18.36 KiB     | 214.55 KiB    | 75.95 KiB    | 59.57 KiB | 290.5 KiB  | 8.1.0                 |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-----------|------------------|-----------------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft_int8.tflite) | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 181.47 ms        | 8.1.0                 |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 525.07 ms        | 8.1.0                 |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_fft/mobilenet_v1_0.25_96_fft_int8.tflite) | Int8   | 96x96x3    | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 32.18 ms         | 8.1.0                 |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale_tfs/mobilenet_v1_0.25_96_grayscale_tfs_int8.tflite) | Int8   | 96x96x1    | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 30.99 ms            | 8.1.0                 |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 71.77 ms **      | X-LINUX-AI v5.0.0       |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 165.39 ms **     | X-LINUX-AI v5.0.0       |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_fft/mobilenet_v1_0.25_96_fft_int8.tflite) | Int8   | 96x96x3    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 12.81 ms **      | X-LINUX-AI v5.0.0       |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_tfs/mobilenet_v1_0.25_224_tfs.h5) | Float | 224x224x3    | 88.83 % |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_tfs/mobilenet_v1_0.25_224_tfs_int8.tflite) | Int8 | 224x224x3    | 89.37 % |
| [MobileNet v1 0.25 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_tl/mobilenet_v1_0.25_224_tl.h5) | Float | 224x224x3    | 85.83 % |
| [MobileNet v1 0.25 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_tl/mobilenet_v1_0.25_224_tl_int8.tflite) | Int8 | 224x224x3    | 83.24 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft.h5) | Float | 224x224x3    | 93.05 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft_int8.tflite) | Int8 | 224x224x3    | 92.1 % |
| [MobileNet v1 0.5 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_tfs/mobilenet_v1_0.5_224_tfs.h5) | Float | 224x224x3    | 92.1 % |
| [MobileNet v1 0.5 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_tfs/mobilenet_v1_0.5_224_tfs_int8.tflite) | Int8 | 224x224x3    | 91.55 % |
| [MobileNet v1 0.5 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_tl/mobilenet_v1_0.5_224_tl.h5) | Float | 224x224x3    | 88.56 % |
| [MobileNet v1 0.5 tl](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_tl/mobilenet_v1_0.5_224_tl_int8.tflite) | Int8 | 224x224x3    | 87.74 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft.h5) | Float | 224x224x3    | 95.1 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft_int8.tflite) | Int8 | 224x224x3    | 94.41 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_fft/mobilenet_v1_0.25_96_fft.h5)      | Float  | 96x96x3      | 87.47 %   |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_fft/mobilenet_v1_0.25_96_fft_int8.tflite)   | Int8   | 96x96x3    | 87.06  % |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale_tfs/mobilenet_v1_0.25_96_grayscale_tfs.h5) | Float | 96x96x1 | 74.93 % |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale_tfs/mobilenet_v1_0.25_96_grayscale_tfs_int8.tflite) | Int8 | 96x96x1 | 74.93 % |



### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224_tfs/mobilenet_v1_0.25_224_tfs.h5) | Float | 224x224x3    | 99.92 % |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224_tfs/mobilenet_v1_0.25_224_tfs_int8.tflite) | Int8 | 224x224x3    | 99.92 % |
| [MobileNet v1 0.25 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224_tl/mobilenet_v1_0.25_224_tl.h5) | Float | 224x224x3    | 85.38 % |
| [MobileNet v1 0.25 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224_tl/mobilenet_v1_0.25_224_tl_int8.tflite) | Int8 | 224x224x3    | 83.7 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft.h5) | Float | 224x224x3    | 99.95 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft_int8.tflite) | Int8 | 224x224x3    | 99.82 % |
| [MobileNet v1 0.5 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224_tfs/mobilenet_v1_0.5_224_tfs.h5) | Float | 224x224x3    | 99.9 % |
| [MobileNet v1 0.5 tfs](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224_tfs/mobilenet_v1_0.5_224_tfs_int8.tflite) | Int8 | 224x224x3    | 99.83 % |
| [MobileNet v1 0.5 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224_tl/mobilenet_v1_0.5_224_tl.h5) | Float | 224x224x3    | 93.05 % |
| [MobileNet v1 0.5 tl](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224_tl/mobilenet_v1_0.5_224_tl_int8.tflite) | Int8 | 224x224x3    | 92.7 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft.h5) | Float | 224x224x3    | 99.94 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft_int8.tflite) | Int8 | 224x224x3    | 99.85 % |


### Accuracy with Food-101 dataset


Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) , License [-](), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224_tfs/mobilenet_v1_0.25_224_tfs.h5) | Float | 224x224x3    | 72.16 % |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224_tfs/mobilenet_v1_0.25_224_tfs_int8.tflite) | Int8 | 224x224x3    | 71.13 % |
| [MobileNet v1 0.25 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224_tl/mobilenet_v1_0.25_224_tl.h5) | Float | 224x224x3    | 43.21 % |
| [MobileNet v1 0.25 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224_tl/mobilenet_v1_0.25_224_tl_int8.tflite) | Int8 | 224x224x3    | 39.89 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft.h5) | Float | 224x224x3    | 72.37 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224_fft/mobilenet_v1_0.25_224_fft_int8.tflite) | Int8 | 224x224x3    | 70.67 % |
| [MobileNet v1 0.5 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224_tfs/mobilenet_v1_0.5_224_tfs.h5) | Float | 224x224x3    | 76.97 % |
| [MobileNet v1 0.5 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224_tfs/mobilenet_v1_0.5_224_tfs_int8.tflite) | Int8 | 224x224x3    | 76.37 % |
| [MobileNet v1 0.5 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224_tl/mobilenet_v1_0.5_224_tl.h5) | Float | 224x224x3    | 48.78 % |
| [MobileNet v1 0.5 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224_tl/mobilenet_v1_0.5_224_tl_int8.tflite) | Int8 | 224x224x3    | 45.89 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft.h5) | Float | 224x224x3    | 77.01 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224_fft/mobilenet_v1_0.5_224_fft_int8.tflite) | Int8 | 224x224x3    | 75.99 % |



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