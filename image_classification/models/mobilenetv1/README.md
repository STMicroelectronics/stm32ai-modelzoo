# MobileNet v1 quantized

## **Use case** : [Image classification](../../../image_classification/README.md)

# Model description


MobileNet is a well known architecture that can be used in multiple use cases.
Input size and width factor called `alpha` are parameters to be adapted to various use cases complexity. The `alpha` parameter is used to
increase or decrease the number of filters in each layer, allowing also to reduce the number of multiply-adds and then the inference time.

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


To train a  MobileNet v1 model with pretrained weights or from scratch on your own dataset, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [mobilenet_v1_0.5_224_config.yaml](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224_config.yaml) file is used to train this model on flowers dataset, you can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below.

## Deployment


To deploy your trained model, you need to configure the [user_config.yaml](../../scripts/deployment/user_config.yaml) file following the [tutorial](../../scripts/deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI (v7.3.0) configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 202.14 KiB     | ~21 KiB      | 214.69 KiB    | ~75 KiB       | 223.29 KiB   | 289.66 KiB  |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 404.28 KiB     | ~21 KiB       | 812.61 KiB    | ~89 KiB    | 425.43 KiB   | 901.05 KiB  |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96/mobilenet_v1_0.25_96_int8.tflite)   | Int8   | 96x96x3    | STM32H7 | 39.56 KiB      | ~20 KiB     | 219.84 KiB    | ~74 KiB    | 60.49 KiB    | 295.76 KiB  |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale/mobilenet_v1_0.25_96_grayscale_int8.tflite)   | Int8   | 96x96x1    | STM32H7 | 38.64 KiB      | ~20 KiB     | 214.55 KiB    | ~76 KiB    | 58.98 KiB | 290.97 KiB  |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) |
|-------------------|--------|------------|------------------|------------------|-----------|------------------|
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224_int8.tflite) | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 183.88 ms        |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 520.02 ms        |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96/mobilenet_v1_0.25_96_int8.tflite) | Int8   | 96x96x3    | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 35.48 ms         |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale/mobilenet_v1_0.25_96_grayscale_int8.tflite) | Int8   | 96x96x1    | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 37.64 ms            |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 71.77 ms **      |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 165.39 ms **     |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96/mobilenet_v1_0.25_96_int8.tflite) | Int8   | 96x96x3    | STM32MP157F-DK2 | 2 CPU            | 800 MHz   | 12.81 ms **      |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224.h5) | Float | 224x224x3    | 85.42 % |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224_int8.tflite) | Int8 | 224x224x3    | 83.24 % |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224.h5) | Float | 224x224x3    | 90.74 % |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224_int8.tflite) | Int8 | 224x224x3    | 89.51 % |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96/mobilenet_v1_0.25_96.h5)                    | Float  | 96x96x3      | 82.29 %       |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96/mobilenet_v1_0.25_96_int8.tflite)           | Int8   | 96x96x3      | 82.15  %       |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale/mobilenet_v1_0.25_96_grayscale.h5)          | Float  | 96x96x1      | 73.89 %        |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v1_0.25_96_grayscale/mobilenet_v1_0.25_96_grayscale_int8.tflite) | Int8   | 96x96x1    | 72.75 %       |



### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224.h5) | Float | 224x224x3    |  88.21 % |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224_int8.tflite) | Int8 | 224x224x3    | 86.22 % |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224.h5) | Float | 224x224x3    | 93.65 % |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/plant-village/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224_int8.tflite) | Int8 | 224x224x3    | 92.01 % |


### Accuracy with Food-101 dataset


Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) , License [-](), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224.h5) | Float | 224x224x3    | 41.58 % |
| [MobileNet v1 0.25](../mobilenetv1/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.25_224/mobilenet_v1_0.25_224_int8.tflite) | Int8 | 224x224x3    | 38.02 % |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224.h5) | Float | 224x224x3    | 50.8 % |
| [MobileNet v1 0.5](../mobilenetv1/ST_pretrainedmodel_public_dataset/food-101/mobilenet_v1_0.5_224/mobilenet_v1_0.5_224_int8.tflite) | Int8 | 224x224x3    | 48.5 % |



## Retraining and code generation


- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../scripts/deployment/README.md)


## Demos
### Integration in a simple example


Please refer to the generic guideline [here](../../scripts/deployment/README.md).



# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.