# MobileNet v1

## **Use case** : `Image classification`

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
| STM32MP2 |[x]|[x]|
| STM32N6  |[x]|[x]|

# Performances

## Metrics

- Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
- `tfs` stands for "training from scratch", meaning that the model weights were randomly initialized before training.
- `tl` stands for "transfer learning", meaning that the model backbone weights were initialized from a pre-trained model, then only the last layer was unfrozen during the training.
- `fft` stands for "full fine-tuning", meaning that the full model weights were initialized from a transfer learning pre-trained model, and all the layers were unfrozen during the training.

### Reference **NPU** memory footprint on food101 and imagenet dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|---------------|-------------------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6   | 392 |  0.0 | 240.88         |     4.0.0   |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6   | 588 | 0.0 | 864.99        |     4.0.0   |
| [MobileNet v1 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a100_224_fft/mobilenetv1_a100_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6   | 1568 | 0.0 | 3347.59       |      4.0.0   |
| [MobileNet v1 0.25](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a025_224/mobilenetv1_a025_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6   | 392 | 0.0 | 469.53       |       4.0.0   |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6   | 588 | 0.0 | 1318.38       |     4.0.0   |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_qdq_w4_38.8%_w8_61.2%_a8_100%_acc_60.87.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6   | 588 | 0.0 | 1067.95       |     4.0.0   |
| [MobileNet v1 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a100_224/mobilenetv1_a100_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6   | 1568 | 0.0 | 4250.49      |     4.0.0   |

### Reference **NPU**  inference time on food101 and imagenet dataset (see Accuracy for details on dataset)


| Model  | Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |   STEdgeAI Core version |
|--------|----------|--------|-------------|------------------|------------------|---------------------|-----------|-------------------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite) | food101 | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 2.37                | 421.94    |      4.0.0   |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | food101 | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 5.38                |  185.87   |     4.0.0   |
| [MobileNet v1 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a100_224_fft/mobilenetv1_a100_224_fft_int8.tflite) | food101 | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 16.36               |   61.12   |      4.0.0   |
| [MobileNet v1 0.25](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a025_224/mobilenetv1_a025_224_int8.tflite) | Imagenet | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 3.1               |  322.58    |      4.0.0   |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_int8.tflite) | Imagenet | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 6.67               |  149.92  |     4.0.0   |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_qdq_w4_38.8%_w8_61.2%_a8_100%_acc_60.87.onnx) | Imagenet | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 5.95               |  168.07  |     4.0.0   |
| [MobileNet v1 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a100_224/mobilenetv1_a100_224_int8.tflite) | Imagenet | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 18.81             |   53.16 |      4.0.0   |


### Reference **MCU** memory footprint based on Flowers dataset and imagenet dataset (see Accuracy for details on dataset)

| Model       | Dataset| Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |  STEdgeAI Core version |
|-------------|--------|--------|------------|---------|----------------|---------------|------------|-------------|-------------|-------------|------------------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite) |tf_flowers| Int8   | 224x224x3    | STM32H7 | 271.04 KiB     | 0.7 KiB      | 214.69 KiB    | 36.07 KiB  | 271.74 KiB   | 250.76 KiB  |      4.0.0   |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite)   | tf_flowers| Int8   | 224x224x3    | STM32H7 | 456.67 KiB     | 0.7 KiB      | 812.61 KiB    | 46.79 KiB  | 457.37 KiB   | 859.4 KiB  |      4.0.0   |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_fft/mobilenetv1_a025_96_fft_int8.tflite)   | tf_flowers | Int8   | 96x96x3    | STM32H7 | 63.04 KiB      | 0.7 KiB     | 214.69 KiB       | 36.03 KiB  | 63.74 KiB    | 250.72 KiB  |      4.0.0   |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_grayscale_tfs/mobilenetv1_a025_96_grayscale_tfs_int8.tflite)    | tf_flowers| Int8   | 96x96x1    | STM32H7 | 52.8 KiB      | 0.3 KiB     | 214.55 KiB    | 39.13 KiB  | 53.1 KiB | 253.68 KiB  |      4.0.0   |
| [MobileNet v1 0.25](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a025_224/mobilenetv1_a025_224_int8.tflite)  | Imagenet | Int8   | 224x224x3    | STM32H7 | 267.2 KiB     | 0.3 KiB      | 467.33 KiB    | 37.61 KiB  | 267.5 KiB   | 504.94 KiB  |      4.0.0   |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_int8.tflite)   | Imagenet | Int8   | 224x224x3    | STM32H7 | 431.07 KiB     | 0.3 KiB      | 1314 KiB    | 48.32 KiB  | 431.37 KiB   | 1362.32 KiB |      4.0.0   |
| [MobileNet v1 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a100_224/mobilenetv1_a100_224_int8.tflite)   | Imagenet | Int8   | 224x224x3    | STM32H7 | 899.78 KiB     | 0.3 KiB      | 4157.09 KiB    | 69.82 KiB | 900.08 KiB   | 4226.91 KiB  |      4.0.0   |


### Reference **MCU** inference time based on Flowers dataset and imagenet dataset (see Accuracy for details on dataset)


| Model      | Dataset       | Format | Resolution | Board            | Execution Engine | Frequency | Inference time (ms) | STEdgeAI Core version |
|------------|------|--------|------------|------------------|------------------|-----------|---------------------|------------------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite) | tf_flowers | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 166.12 ms            |     4.0.0   |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | tf_flowers | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 478.26 ms           |     4.0.0   |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_fft/mobilenetv1_a025_96_fft_int8.tflite) | tf_flowers| Int8   | 96x96x3    | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 30.74 ms            |     4.0.0   |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_grayscale_tfs/mobilenetv1_a025_96_grayscale_tfs_int8.tflite) | tf_flowers| Int8   | 96x96x1    | STM32H747I-DISCO  | 1 CPU            | 400 MHz   | 29.01 ms            |     4.0.0   |
| [MobileNet v1 0.25](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a025_224/mobilenetv1_a025_224_int8.tflite) | Imagenet| Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 180.87 ms           |     4.0.0   |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_int8.tflite) | Imagenet| Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 504.08 ms           |     4.0.0   |
| [MobileNet v1 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a100_224/mobilenetv1_a100_224_int8.tflite) | Imagenet| Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz   | 1651.05 ms          |     4.0.0   |


### Reference **MPU** inference time based on Flowers dataset (see Accuracy for details on dataset)

| Model                 | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|-----------------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|------|-------|------|--------------------|-----------------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite)  | Int8   | 224x224x3  | per-channel** | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 14.06               | 7.47 | 92.53 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | Int8   | 224x224x3  | per-channel** | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 32.37               | 3.84 | 96.16 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_fft/mobilenetv1_a025_96_fft_int8.tflite)  | Int8   | 96x96x3   | per-channel** | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 3.62                | 18.33| 81.67 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_grayscale_tfs/mobilenetv1_a025_96_grayscale_tfs_int8.tflite) | Int8   | 96x96x1   | per-channel** | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 3.72                | 14.97| 85.03 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite)  | Int8   | 224x224x3  | per-channel   | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 31.70               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | Int8   | 224x224x3  | per-channel   | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 89.23               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_fft/mobilenetv1_a025_96_fft_int8.tflite)  | Int8   | 96x96x3   | per-channel   | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 5.99                | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_grayscale_tfs/mobilenetv1_a025_96_grayscale_tfs_int8.tflite) | Int8   | 96x96x1   | per-channel   | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 5.94                | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite)  | Int8   | 224x224x3  | per-channel   | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 49.86               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | Int8   | 224x224x3  | per-channel   | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 142.62              | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_fft/mobilenetv1_a025_96_fft_int8.tflite)  | Int8   | 96x96x3   | per-channel   | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 9.18                | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_grayscale_tfs/mobilenetv1_a025_96_grayscale_tfs_int8.tflite) | Int8   | 96x96x1   | per-channel   | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 9.24                | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft.keras) | Float | 224x224x3    | 93.05 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite) | Int8 | 224x224x3    | 92.1 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft.keras) | Float | 224x224x3    | 95.1 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | Int8 | 224x224x3    | 94.41 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_fft/mobilenetv1_a025_96_fft.keras)      | Float  | 96x96x3      | 87.47 %   |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_fft/mobilenetv1_a025_96_fft_int8.tflite)   | Int8   | 96x96x3    | 87.06  % |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_grayscale_tfs/mobilenetv1_a025_96_grayscale_tfs.keras) | Float | 96x96x1 | 74.93 % |
| [MobileNet v1 0.25 tfs](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv1_a025_96_grayscale_tfs/mobilenetv1_a025_96_grayscale_tfs_int8.tflite) | Int8 | 96x96x1 | 74.93 % |



### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft.keras) | Float | 224x224x3    | 99.95 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite) | Int8 | 224x224x3    | 99.82 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft.keras) | Float | 224x224x3    | 99.94 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | Int8 | 224x224x3    | 99.85 % |


### Accuracy with Food-101 dataset


Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft.keras) | Float | 224x224x3    | 75.75 % |
| [MobileNet v1 0.25 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a025_224_fft/mobilenetv1_a025_224_fft_int8.tflite) | Int8 | 224x224x3    | 73.24 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft.keras) | Float | 224x224x3    | 82.06 % |
| [MobileNet v1 0.5 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a050_224_fft/mobilenetv1_a050_224_fft_int8.tflite) | Int8 | 224x224x3    | 80.64 % |
| [MobileNet v1 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a100_224_fft/mobilenetv1_a100_224_fft.keras) | Float | 224x224x3    | 84.57 % |
| [MobileNet v1 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv1_a100_224_fft/mobilenetv1_a100_224_fft_int8.tflite) | Int8 | 224x224x3    | 83.07 % |


### Accuracy with imagenet dataset

Dataset details: [link](https://www.image-net.org), Quotation[[4]](#4).
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

|model    | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|----------------|
| [MobileNet v1 0.25](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a025_224/mobilenetv1_a025_224.keras)                                | Float  | 224x224x3  | 50.5 %        |
| [MobileNet v1 0.25](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a025_224/mobilenetv1_a025_224_int8.tflite)                       | Int8   | 224x224x3  | 47.94 %        |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224.keras)                                | Float  | 224x224x3  | 64.02 %       |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_int8.tflite)                       | Int8   | 224x224x3  | 62.25 %       |
| [MobileNet v1 0.5](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a050_224/mobilenetv1_a050_224_qdq_w4_38.8%_w8_61.2%_a8_100%_acc_60.87.onnx) | Int8/Int4 | 224x224x3 | 60.87 %  |
| [MobileNet v1 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a100_224/mobilenetv1_a100_224.keras)                                | Float  | 224x224x3  | 70.92 %       |
| [MobileNet v1 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv1_a100_224/mobilenetv1_a100_224_int8.tflite)                       | Int8   | 224x224x3  | 69.64 %       |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.