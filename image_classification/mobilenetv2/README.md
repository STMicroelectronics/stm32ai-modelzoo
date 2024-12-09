# MobileNet v2

## **Use case** : `Image classification`

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
| STM32MP2 |[x]|[x]|
| STM32N6  |[x]|[x]|

# Performances

## Metrics

- Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
- `tfs` stands for "training from scratch", meaning that the model weights were randomly initialized before training.
- `tl` stands for "transfer learning", meaning that the model backbone weights were initialized from a pre-trained model, then only the last layer was unfrozen during the training.
- `fft` stands for "full fine-tuning", meaning that the full model weights were initialized from a transfer learning pre-trained model, and all the layers were unfrozen during the training.


### Reference **NPU** memory footprint on food-101 and ImageNet dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)  | food-101      | Int8     | 128x128x3  | STM32N6   | 240 | 0.0 | 715.67 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | food-101      | Int8     | 224x224x3  | STM32N6   | 980 | 0.0 | 730.7 |       10.0.0        |     2.0.0   |
|  [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_1.0_224_fft/mobilenet_v2_1.0_224_fft_int8.tflite) | food-101      | Int8     | 224x224x3  | STM32N6   | 2058 | 0.0 | 3110.05 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35 fft](ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)  | Person    | Int8     | 128x128x3  | STM32N6   | 240 | 0.0 | 589.45 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | ImageNet      | Int8     | 128x128x3  | STM32N6   | 240 | 0.0 | 1840.94 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6   | 980 | 0.0 | 1855.97 |       10.0.0        |     2.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6   | 2058 | 0.0 | 4235.31 |       10.0.0        |     2.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.4_224/mobilenet_v2_1.4_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6   | 2361 | 0.0 | 7315.69 |       10.0.0        |     2.0.0   |


### Reference **NPU**  inference time on food-101 and ImageNet dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | food-101      | Int8     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      | 3.33 | 300.30 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | food-101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 6.12 | 163.40 |       10.0.0        |     2.0.0   |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_1.0_224_fft/mobilenet_v2_1.0_224_fft_int8.tflite) | food-101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 18.08 | 55.32 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35 fft](ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)  | Person   | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 2.99 | 334.45 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite) | ImageNet      | Int8     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      | 6.35 | 157.48 |       10.0.0        |     2.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 9.14 | 109.40 |       10.0.0        |     2.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 21.08 | 47.44 |       10.0.0        |     2.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.4_224/mobilenet_v2_1.4_224_int8.tflite) | ImageNet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 35.34 | 28.30 |       10.0.0        |     2.0.0   |


### Reference **MCU** memory footprint based on Flowers and ImageNet dataset (see Accuracy for details on dataset)

| Model                                                                                                                                            | Dataset  | Format | Resolution  | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM  | Total Flash | STM32Cube.AI version |
|--------------------------------------------------------------------------------------------------------------------------------------------------|----------|--------|-------------|---------|----------------|-------------|---------------|------------|------------|-------------|----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)             | Flowers  | Int8   | 128x128x3   | STM32H7 | 237.32 KiB     | 30.14 KiB   | 406.86 KiB    | 108.29 KiB | 267.46 KiB | 515.15 KiB  | 10.0.0                |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite)             | Flowers  | Int8   | 224x224x3   | STM32H7 | 832.64 KiB     | 30.19 KiB   | 406.86 KiB    | 108.40 KiB | 862.83 KiB | 515.26 KiB  | 10.0.0                |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite)             | ImageNet  | Int8   | 128x128x3   | STM32H7 | 237.32 KiB     | 30.14 KiB   | 1654.5 KiB KiB    | 108.29 KiB | 267.46 KiB | 1762.79 KiB  | 10.0.0                |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite)             | ImageNet  | Int8   | 224x224x3   | STM32H7 | 832.64 KiB     | 30.19 KiB   | 1654.5 KiB    | 108.40 KiB | 862.83 KiB | 1762.9 KiB  | 10.0.0                |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite)             | ImageNet  | Int8   | 224x224x3   | STM32H7 | 1727.02 KiB     | 30.19 KiB   | 3458.97 KiB    | 157.37 KiB | 1757.21 KiB | 3616.34 KiB  | 10.0.0                |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.4_224/mobilenet_v2_1.4_224_int8.tflite)             | ImageNet  | Int8   | 224x224x3   | STM32H7 | 2332.2 KiB     | 30.19 KiB   | 6015.34 KiB    | 191.16 KiB | 2362.39 KiB | 6206.53 KiB  | 10.0.0                |

### Reference **MCU** inference time based on Flowers and ImageNet dataset (see Accuracy for details on dataset)

| Model                                                                                                                                            | Dataset  | Format | Resolution  | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|--------------------------------------------------------------------------------------------------------------------------------------------------|----------|--------|-------------|------------------|------------------|-------------|---------------------|-----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)             | Flowers  | Int8   | 128x128x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 94.34  ms          | 10.0.0                 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite)             | Flowers  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 290.75 ms           | 10.0.0                 |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite)             | ImageNet  | Int8   | 128x128x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 116.13  ms          | 10.0.0                 |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite)             | ImageNet  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 313.92 ms           | 10.0.0                 |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite)             | ImageNet  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 1106.64 ms           | 10.0.0                 |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.4_224/mobilenet_v2_1.4_224_int8.tflite)             | ImageNet  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 2010.66 ms           | 10.0.0                 |

### Reference **MPU** inference time based on Flowers and ImageNet dataset (see Accuracy for details on dataset)
| Model                                                                                                                                            | Dataset  | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|--------------------------------------------------------------------------------------------------------------------------------------------------|----------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8_per_tensor.tflite) | ImageNet | Int8   | 224x224x3  |  per-tensor   | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 11.92 ms            | 92.74 | 7.26  |0     | v5.1.0             | OpenVX                |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite)                       | ImageNet | Int8   | 224x224x3  |  per-channel **  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 76.29 ms            | 3.13  | 96.87 |0     | v5.1.0             | OpenVX                |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite)             | Flowers  | Int8   | 224x224x3  |  per-channel **  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 25.51 ms            | 4.37  | 95.63 |0     | v5.1.0             | OpenVX                |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)             | Flowers  | Int8   | 128x128x3  |  per-channel **  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 9.14  ms            | 12.06 | 87.94 |0     | v5.1.0             | OpenVX                |
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8_per_tensor.tflite) | ImageNet | Int8   | 224x224x3  |  per-tensor   | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 332.9 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite)                       | ImageNet | Int8   | 128x128x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 194.1 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite)             | Flowers  | Int8   | 224x224x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 54.52 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)             | Flowers  | Int8   | 128x128x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 17.16 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8_per_tensor.tflite) | ImageNet | Int8   | 224x224x3  |  per-tensor   | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 415.7 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite)                       | ImageNet | Int8   | 128x128x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 308.80 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite)             | Flowers  | Int8   | 224x224x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 54.85  ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite)             | Flowers  | Int8   | 128x128x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 27.17  ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**
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

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs.h5) | Float | 128x128x3    | 64.22 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs_int8.tflite) | Int8 | 128x128x3    | 63.41 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl.h5) | Float | 128x128x3    | 44.74 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl_int8.tflite) | Int8 | 128x128x3    | 42.01 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft.h5) | Float | 128x128x3    | 64.22 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8 | 128x128x3    | 63.41 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs.h5) | Float | 224x224x3    | 72.31 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tfs/mobilenet_v2_0.35_224_tfs_int8.tflite) | Int8 | 224x224x3    | 72.05 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl.h5) | Float | 224x224x3    | 49.01 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_tl/mobilenet_v2_0.35_224_tl_int8.tflite) | Int8 | 224x224x3    | 47.26 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft.h5) | Float | 224x224x3    | 73.76 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_0.35_224_fft/mobilenet_v2_0.35_224_fft_int8.tflite) | Int8 | 224x224x3    | 73.16 % |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_1.0_224_fft/mobilenet_v2_1.0_224_fft.h5) | Float | 224x224x3    | 77.77 % |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food-101/mobilenet_v2_1.0_224_fft/mobilenet_v2_1.0_224_fft_int8.tflite) | Int8 | 224x224x3    | 77.09 % |


### Accuracy with person dataset

The person dataset is derived from COCO-2014 and created using the script here (link). The dataset folder has 2 sub-folders — person and notperson containing images of the respective types
Dataset details: [link](https://cocodataset.org/) , License [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Quotation[[3]](#3)  , Number of classes: 2 , Number of images: 84810

| Model      | Format | Resolution | Top 1 Accuracy |
|------------|--------|-----------|----------------|
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs.h5)                                    | Float  | 128x128x3   | 92.56 % |
| [MobileNet v2 0.35 tfs](./ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tfs/mobilenet_v2_0.35_128_tfs_int8.tflite)                           | Int8   | 128x128x3   | 92.44 % |
| [MobileNet v2 0.35 tl ](./ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl.h5)         | Float  | 128x128x3   | 92.28 % |
| [MobileNet v2 0.35 tl](./ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_tl/mobilenet_v2_0.35_128_tl_int8.tflite) | Int8   | 128x128x3   | 91.63 % |
| [MobileNet v2 0.35 fft ](./ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft.h5)         | Float  | 128x128x3   | 95.37 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/person/mobilenet_v2_0.35_128_fft/mobilenet_v2_0.35_128_fft_int8.tflite) | Int8   | 128x128x3   | 94.95 % |


### Accuracy with ImageNet

Dataset details: [link](https://www.image-net.org), Quotation[[4]](#4).
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model    | Format | Resolution | Top 1 Accuracy |
|----------|--------|------------|----------------|
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128.h5)                                | Float  | 128x128x3  | 46.96 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128_int8.tflite)                       | Int8   | 128x128x3  | 43.94 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224.h5)                                | Float  | 224x224x3  | 56.44 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_0.35_224/mobilenet_v2_0.35_224_int8.tflite)                       | Int8   | 224x224x3  | 54.7 %        |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224.h5)                                | Float  | 224x224x3  | 68.87 %        |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8.tflite)                       | Int8   | 224x224x3  | 67.97 %        |
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224_int8_per_tensor.tflite) | Int8   | 224x224x3  | 64.53 %        |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.4_224/mobilenet_v2_1.4_224.h5)                                | Float  | 224x224x3  | 71.97 %        |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/ImageNet/mobilenet_v2_1.4_224/mobilenet_v2_1.4_224_int8.tflite)                       | Int8   | 224x224x3  | 71.46 %        |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.

<a id="4">[4]</a>
Olga Russakovsky*, Jia Deng*, Hao Su, Jonathan Krause, Sanjeev Satheesh, Sean Ma, Zhiheng Huang, Andrej Karpathy, Aditya Khosla, Michael Bernstein, Alexander C. Berg and Li Fei-Fei.
(* = equal contribution) ImageNet Large Scale Visual Recognition Challenge.