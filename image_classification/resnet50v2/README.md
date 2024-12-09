# ResNet50 v2

## **Use case** : `Image classification`

# Model description


ResNets family is a well known architecture that uses skip connections to enable stronger gradients in much deeper networks. This variant has 50 layers.

The model is quantized in int8 using tensorflow lite converter.

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  MParams                | 25.6 M          |
|  Quantization           | int8            |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/ResNet50V2 |
|  Paper                  | https://arxiv.org/abs/1603.05027 |

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
| STM32L4  |[]|[]|
| STM32U5  |[]|[]|
| STM32H7  |[x]|[]|
| STM32MP1 |[x]|[]|
| STM32MP2 |[x]|[x]|
| STM32N6 |[x]|[x]|

# Performances

## Metrics

- Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
- `tfs` stands for "training from scratch", meaning that the model weights were randomly initialized before training.
- `tl` stands for "transfer learning", meaning that the model backbone weights were initialized from a pre-trained model, then only the last layer was unfrozen during the training.
- `fft` stands for "full fine-tuning", meaning that the full model weights were initialized from a transfer learning pre-trained model, and all the layers were unfrozen during the training.


### Reference **NPU** memory footprint on food-101 and ImageNet dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food-101/resnet50_v2_224_fft/resnet50_v2_224_fft_int8.tflite)  | food-101      | Int8     | 224x224x3  | STM32N6   |         |                |             |       10.0.0        |     2.0.0   |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/ImageNet/resnet50_v2_224/resnet50_v2_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6   |         |                |             |       10.0.0        |     2.0.0   |

### Reference **NPU**  inference time on food-101 and ImageNet dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food-101/resnet50_v2_224_fft/resnet50_v2_224_fft_int8.tflite) | food-101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |                |             |       10.0.0        |     2.0.0   |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/ImageNet/resnet50_v2_224/resnet50_v2_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |                |             |       10.0.0        |     2.0.0   |


### Reference **MCU** memory footprint based on Food-101 and ImageNet dataset (see Accuracy for details on dataset)

| Model     | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STM32Cube.AI version  |
|--------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food-101/resnet50_v2_224_fft/resnet50_v2_224_fft_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 2142.07 KiB     | 41.02 KiB      | 23240.96 KiB    | 226.05 KiB  | 2183.09 KiB   | 23467.01 KiB  | 10.0.0  |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/ImageNet/resnet50_v2_224/resnet50_v2_224_int8.tflite)    | Int8   | 224x224x3    | STM32H7 | 2142.07 KiB     | 41.02 KiB      | 25042.47 KiB    | 226.05 KiB  | 2183.09 KiB   | 25268.52 KiB  | 10.0.0 |


### Reference **MCU** inference time based on Food-101 and ImageNet dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-----------|------------------|-----------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food-101/resnet50_v2_224_fft/resnet50_v2_224_fft_int8.tflite) | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 11354.82 ms        | 10.0.0                 |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/ImageNet/resnet50_v2_224/resnet50_v2_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 11368.81 ms        | 10.0.0                 |



### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[1]](#1)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food-101/resnet50_v2_224_fft/resnet50_v2_224_fft.h5) | Float | 224x224x3    | 71.53 % |
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food-101/resnet50_v2_224_fft/resnet50_v2_224_fft_int8.tflite) | Int8 | 224x224x3    | 70.07 % |


### Accuracy with ImageNet dataset

Dataset details: [link](https://www.image-net.org), Quotation[[4]](#4).
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

|model    | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|----------------|
| [ResNet50 v2 ](./Public_pretrainedmodel_public_dataset/ImageNet/resnet50_v2_224/resnet50_v2_224.h5) | Float | 224x224x3    | 66.38 % |
| [ResNet50 v2 ](./Public_pretrainedmodel_public_dataset/ImageNet/resnet50_v2_224/resnet50_v2_224_int8.tflite) | Int8 | 224x224x3    | 65.99 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.