# ResNet50 v2

## **Use case** : `Image classification`

# Model description


ResNets family is a well known architecture that uses skip connections to enable stronger gradients in much deeper networks. This variant has 50 layers.

The model is quantized in int8 using tensorflow lite converter. A mixed precision version is also provided using onnx-runtime and our own quantization scripts.

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


### Reference **NPU** memory footprint on food101 and imagenet dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|--------------|--------------|----------------------|-------------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_int8.tflite)  | food101      | Int8     | 224x224x3  | STM32N6   | 2308.06 | 3136     | 23833.67  |     3.0.0   |
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_qdq_w4_91.4%_w8_8.6%_a8_100%_acc_80.17.onnx)  | food101      | Int8/Int4     | 224x224x3  | STM32N6   | 2308.06 | 2352     | 13268.39  |     3.0.0   |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_int8.tflite) | imagenet | Int8   | 224x224x3  | STM32N6   | 2308.06 | 3136.0  | 25633.61    |     3.0.0   |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_qdq_w4_35.98%_w8_64.02%_a8_100%_acc_67.45.onnx) | imagenet | Int8/Int4   | 224x224x3  | STM32N6   | 2308.06 | 2352  | 21154.53    |     3.0.0   |

### Reference **NPU**  inference time on food101 and imagenet dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-----------|-------------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 238.49       | 4.19      |     3.0.0   |
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_qdq_w4_91.4%_w8_8.6%_a8_100%_acc_80.17.onnx) | food101      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 267.33       | 3.74      |     3.0.0   |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |    243.04    |      4.11     |     3.0.0   |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_qdq_w4_35.98%_w8_64.02%_a8_100%_acc_67.45.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |    286.06    |      3.5     |     3.0.0   |


### Reference **MCU** memory footprint based on Food-101 and imagenet dataset (see Accuracy for details on dataset)

| Model     | Dataset |  Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash     | STEdgeAI Core version  |
|-----------|---------------------------------------------------------------------------------------------------------------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-----------------|-----------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_int8.tflite) | food101 | Int8   | 224x224x3    | STM32H7 | 1816.2 KiB     | 14.56 KiB   | 23240.96 KiB    | 169.12 KiB | 1830.76 KiB  | 23410.08 KiB | 3.0.0  |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_int8.tflite)    | imagenet | Int8   | 224x224x3    | STM32H7 | 2142.07 KiB     | 41.03 KiB   | 25042.47 KiB    | 225.32 KiB | 2183.1 KiB | 25267.79 KiB    | 3.0.0 |


### Reference **MCU** inference time based on Food-101 and imagenet dataset (see Accuracy for details on dataset)


| Model             | Dataset | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) | STEdgeAI Core version  |
|-------------------|-----|---|------------|------------------|------------------|-----------|---------------------|-----------------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_int8.tflite) | food101 |  Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 11314.82        | 3.0.0                 |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_int8.tflite) | imagenet | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz   |  11370.07       | 3.0.0                 |



### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[1]](#1)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft.keras) | Float | 224x224x3    | 82.2 % |
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_int8.tflite) | Int8 | 224x224x3    | 81.03 % |
| [ResNet50 v2 fft](./ST_pretrainedmodel_public_dataset/food101/resnet50v2_224_fft/resnet50v2_224_fft_qdq_w4_91.4%_w8_8.6%_a8_100%_acc_80.17.onnx) | Int8/Int4 | 224x224x3 | 80.17 % |

### Accuracy with imagenet dataset

Dataset details: [link](https://www.image-net.org), Quotation[[4]](#4).
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

|model    | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|----------------|
| [ResNet50 v2 ](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224.keras) | Float | 224x224x3    | 68.73 % |
| [ResNet50 v2 ](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_int8.tflite) | Int8 | 224x224x3    | 67.99 % |
| [ResNet50 v2](./Public_pretrainedmodel_public_dataset/imagenet/resnet50v2_224/resnet50v2_224_qdq_w4_35.98%_w8_64.02%_a8_100%_acc_67.45.onnx) | Int8/Int4 | 224x224x3 | 67.45 % |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.