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

## Metricss

- Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
- `tfs` stands for "training from scratch", meaning that the model weights were randomly initialized before training.
- `tl` stands for "transfer learning", meaning that the model backbone weights were initialized from a pre-trained model, then only the last layer was unfrozen during the training.
- `fft` stands for "full fine-tuning", meaning that the full model weights were initialized from a transfer learning pre-trained model, and all the layers were unfrozen during the training.


### Reference **NPU** memory footprint on food101 and imagenet dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB)| Weights Flash (KiB)| STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|---------------|-------------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite)  | food101      | Int8     | 128x128x3  | STM32N6   | 240 | 0.0 | 530.59        |     4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_qdq_w4_53.32%_w8_46.68%_a8_100%_acc_64.61.onnx)  | food101      | Int8/Int4     | 128x128x3  | STM32N6   | 240 | 0.0 | 396.44        |     4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6   | 931 | 0.0 | 557.44        |     4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_qdq_w4_53.32%_w8_46.68%_a8_100%_acc_74.86.onnx) | food101      | Int8/Int4     | 224x224x3  | STM32N6   | 1127 | 0.0 | 423.28      |     4.0.0   |
|  [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a100_224_fft/mobilenetv2_a100_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6   | 2058 | 0.0 | 2686.42       |     4.0.0   |
|  [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a100_224_fft/mobilenetv2_a100_224_fft_qdq_w4_30.91%_w8_69.09%_a8_100%_acc_80.06.onnx) | food101      | Int8/Int4     | 224x224x3  | STM32N6   | 2058 | 0.0 | 2336.39       |     4.0.0   |
| [MobileNet v2 0.35 fft](ST_pretrainedmodel_public_dataset/coco_person/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite)  | Person    | Int8     | 128x128x3  | STM32N6   | 240 | 0.0 | 404.55        |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_int8.tflite) | imagenet      | Int8     | 128x128x3  | STM32N6   | 240 | 0.0 | 1656.28       |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_qdq_w4_85.64%_w8_14.36%_a8_100%_acc_43.53.onnx) | imagenet      | Int8/Int4     | 128x128x3  | STM32N6   | 240 | 0.0 | 962.22       |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6   | 931 | 0.0 | 1683.13      |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_qdq_w4_85.64%_w8_14.36%_a8_100%_acc_56.25.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6   | 1127 | 0.0 | 989.06      |     4.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6   | 2058 | 0.0 | 3812.11       |     4.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_qdq_w4_48.7%_w8_51.3%_a8_100%_acc_69.54.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6   | 2058 | 0.0 | 2988.05       |     4.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6   | 2361 | 0.0 | 6746.7       |     4.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_qdq_w4_42.82%_w8_57.18%_a8_100%_acc_73.12.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6   | 2361 | 0.0 | 5480.25       |     4.0.0   |


### Reference **NPU**  inference time on food101 and imagenet dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |   STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-----------|-------------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite) | food101      | Int8     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      | 2.82               | 354.6     |     4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_qdq_w4_53.32%_w8_46.68%_a8_100%_acc_64.61.onnx) | food101      | Int8/Int4     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      | 2.65                | 377.36     |     4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 5.67                | 176.36    |     4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_qdq_w4_53.32%_w8_46.68%_a8_100%_acc_74.86.onnx) | food101      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 5.43               | 184.16    |     4.0.0   |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a100_224_fft/mobilenetv2_a100_224_fft_int8.tflite) | food101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 17.44               | 57.34     |     4.0.0   |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a100_224_fft/mobilenetv2_a100_224_fft_qdq_w4_30.91%_w8_69.09%_a8_100%_acc_80.06.onnx) | food101      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 16.43             | 60.86    |     4.0.0   |
| [MobileNet v2 0.35 fft](ST_pretrainedmodel_public_dataset/coco_person/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite)  | Person   | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 2.47                | 404.86    |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_int8.tflite) | imagenet      | Int8     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      | 5.83               |   171.53  |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_qdq_w4_85.64%_w8_14.36%_a8_100%_acc_43.53.onnx) | imagenet      | Int8/Int4     | 128x128x3  | STM32N6570-DK   |   NPU/MCU      | 4.05               | 246.91   |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 8.68               | 115.2     |     4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_qdq_w4_85.64%_w8_14.36%_a8_100%_acc_56.25.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 6.83              | 146.4    |     4.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 20.45               | 48.9    |     4.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_qdq_w4_48.7%_w8_51.3%_a8_100%_acc_69.54.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 18.21               | 54.91     |     4.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_int8.tflite) | imagenet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 34.74               | 28.79     |     4.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_qdq_w4_42.82%_w8_57.18%_a8_100%_acc_73.12.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 31.94               | 31.3     |     4.0.0   |


### Reference **MCU** memory footprint based on Flowers and imagenet dataset (see Accuracy for details on dataset)

| Model  | Dataset  | Format | Resolution  | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STEdgeAI Core version |
|--------|----------|--------|-------------|---------|-------------|---------------|------------|-------------|-------------|----------------|-----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite) | Flowers  | Int8   | 128x128x3   | STM32H7 | 237.32 KiB     | 3.77 KiB   | 406.86 KiB    | 64.3 KiB  | 241.09 KiB  | 471.16 KiB  |    4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite)             | Flowers  | Int8   | 224x224x3   | STM32H7 | 699.32 KiB     | 3.77 KiB    | 406.86 KiB    | 64.69 KiB | 703.09 KiB  | 471.55 KiB  |    4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_int8.tflite)             | imagenet  | Int8   | 128x128x3   | STM32H7 | 237.32 KiB     | 3.36 KiB   | 1654.5 KiB KiB    | 65.25 KiB | 240.68 KiB  | 1719.75 KiB |    4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_int8.tflite)             | imagenet  | Int8   | 224x224x3   | STM32H7 | 699.32 KiB     | 3.36 KiB   | 1654.5 KiB    | 65.68 KiB | 702.68 KiB  | 1720.18 KiB  |    4.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite)             | imagenet  | Int8   | 224x224x3   | STM32H7 | 1433.13 KiB     | 3.36 KiB   | 3458.97 KiB    | 104.92 KiB | 1436.49 KiB | 3563.89 KiB |    4.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_int8.tflite)             | imagenet  | Int8   | 224x224x3   | STM32H7 | 2143.27 KiB     | 3.36 KiB   | 6015.34 KiB    | 132.17 KiB | 2146.63 KiB | 6147.51 KiB |    4.0.0   |

### Reference **MCU** inference time based on Flowers and imagenet dataset (see Accuracy for details on dataset)

| Model                           | Dataset  | Format | Resolution  | Board            | Execution Engine | Frequency   | Inference time (ms) | STEdgeAI Core version |
|---------------------------------|----------|--------|-------------|------------------|------------------|-------------|---------------------|-----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite)             | Flowers  | Int8   | 128x128x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 96.75 ms           |    4.0.0   |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite)             | Flowers  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 298.62 ms           |    4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_int8.tflite)             | imagenet  | Int8   | 128x128x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 113.43 ms          |    4.0.0   |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_int8.tflite)             | imagenet  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 321.76 ms           |    4.0.0   |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite)             | imagenet  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 1118.27 ms          |    4.0.0   |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_int8.tflite)             | imagenet  | Int8   | 224x224x3   | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 	2035.56 ms |    4.0.0   |

### Reference **MPU** inference time based on Flowers and imagenet dataset (see Accuracy for details on dataset)

| Model                                                                                                                                            | Dataset  | Format | Resolution | Quantization   | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|--------------------------------------------------------------------------------------------------------------------------------------------------|----------|--------|------------|----------------|-------------------|------------------|-----------|---------------------|------|-------|------|--------------------|-----------------------|
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8_per_tensor.tflite) | imagenet | Int8   | 224x224x3  | per-tensor     | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 12.15               | 81.71| 18.29 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite)                       | imagenet | Int8   | 224x224x3  | per-channel ** | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 75.91               | 2.77 | 97.23 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite)            | Flowers  | Int8   | 224x224x3  | per-channel ** | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 25.30               | 3.89 | 96.11 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite)            | Flowers  | Int8   | 128x128x3  | per-channel ** | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 8.97                | 11.73| 88.27 | 0    | v6.1.0             | OpenVX                |
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8_per_tensor.tflite) | imagenet | Int8   | 224x224x3  | per-tensor     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 346.87              | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite)                       | imagenet | Int8   | 224x224x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 206.64              | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite)            | Flowers  | Int8   | 224x224x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 51.33               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite)            | Flowers  | Int8   | 128x128x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 16.27               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8_per_tensor.tflite) | imagenet | Int8   | 224x224x3  | per-tensor     | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 434.12              | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite)                       | imagenet | Int8   | 224x224x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 316.76              | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite)            | Flowers  | Int8   | 224x224x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 81.91               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite)            | Flowers  | Int8   | 128x128x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 25.75               | NA   | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

### Accuracy with Flowers dataset


Dataset details: [link](http://download.tensorflow.org/example_images/flower_photos.tgz) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , Number of classes: 5, Number of images: 3 670

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft.keras) | Float | 128x128x3    | 91.83 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite) | Int8 | 128x128x3    | 91.01 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft.keras) | Float | 224x224x3    | 93.6 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/tf_flowers/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite) | Int8 | 224x224x3    | 92.78 % |


### Accuracy with Plant-village dataset


Dataset details: [link](https://data.mendeley.com/datasets/tywbtsjrjv/1) , License [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), Quotation[[2]](#2)  , Number of classes: 39, Number of images:  61 486

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft.keras) | Float | 128x128x3    | 99.77 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite) | Int8 | 128x128x3    | 99.48 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft.keras) | Float | 224x224x3    | 99.95 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/plant_leaf_diseases/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite) | Int8 | 224x224x3    | 99.68 % |


### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft.keras) | Float | 128x128x3    | 65.88 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite) | Int8 | 128x128x3    | 65 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_qdq_w4_53.32%_w8_46.68%_a8_100%_acc_64.61.onnx) | Int8/Int4 | 128x128x3    | 64.61 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft.keras) | Float | 224x224x3    | 76.47 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_int8.tflite) | Int8 | 224x224x3    | 75.4 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a035_224_fft/mobilenetv2_a035_224_fft_qdq_w4_53.32%_w8_46.68%_a8_100%_acc_74.86.onnx) | Int8/Int4 | 224x224x3    | 74.86 % |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a100_224_fft/mobilenetv2_a100_224_fft.keras) | Float | 224x224x3    | 82.13 % |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a100_224_fft/mobilenetv2_a100_224_fft_int8.tflite) | Int8 | 224x224x3    | 81.6 % |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/food101/mobilenetv2_a100_224_fft/mobilenetv2_a100_224_fft_qdq_w4_30.91%_w8_69.09%_a8_100%_acc_80.06.onnx) | Int8/Int4 | 224x224x3    | 80.06 % |


### Accuracy with coco_person dataset

The coco_person dataset is derived from COCO-2014 and created using the script here (link). The dataset folder has 2 sub-folders — person and not person containing images of the respective types
Dataset details: [link](https://cocodataset.org/) , License [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Quotation[[3]](#3)  , Number of classes: 2 , Number of images: 84810

| Model      | Format | Resolution | Top 1 Accuracy |
|------------|--------|-----------|----------------|
| [MobileNet v2 0.35 fft ](./ST_pretrainedmodel_public_dataset/coco_person/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft.keras)         | Float  | 128x128x3   | 95.37 % |
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/coco_person/mobilenetv2_a035_128_fft/mobilenetv2_a035_128_fft_int8.tflite) | Int8   | 128x128x3   | 94.95 % |


### Accuracy with imagenet

Dataset details: [link](https://www.image-net.org), Quotation[[4]](#4).
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model    | Format | Resolution | Top 1 Accuracy |
|----------|--------|------------|----------------|
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128.keras)                                | Float  | 128x128x3  | 46.96 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_int8.tflite)                       | Int8   | 128x128x3  | 43.94 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_128/mobilenetv2_a035_128_qdq_w4_85.64%_w8_14.36%_a8_100%_acc_43.53.onnx)   | Int8/Int4   | 128x128x3  | 43.53 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224.keras)                                | Float  | 224x224x3  | 58.13 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_int8.tflite)                       | Int8   | 224x224x3  | 56.77 %        |
| [MobileNet v2 0.35](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a035_224/mobilenetv2_a035_224_qdq_w4_85.64%_w8_14.36%_a8_100%_acc_56.25.onnx)  | Int8/Int4   | 224x224x3  | 56.25 %        |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224.keras)                                | Float  | 224x224x3  | 70.37 %        |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8.tflite)                       | Int8   | 224x224x3  | 69.75 %        |
| [MobileNet v2 1.0](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_qdq_w4_48.7%_w8_51.3%_a8_100%_acc_69.54.onnx)  | Int8/Int4   | 224x224x3  | 69.54 %        |
| [MobileNet v2 1.0_per_tensor](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a100_224/mobilenetv2_a100_224_int8_per_tensor.tflite) | Int8   | 224x224x3  | 65.84 %        |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224.keras)                                | Float  | 224x224x3  | 73.74 %        |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_int8.tflite)                       | Int8   | 224x224x3  | 73.45 %        |
| [MobileNet v2 1.4](./Public_pretrainedmodel_public_dataset/imagenet/mobilenetv2_a140_224/mobilenetv2_a140_224_qdq_w4_42.82%_w8_57.18%_a8_100%_acc_73.12.onnx)  | Int8/Int4   | 224x224x3  | 73.12 %        |


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
(* = equal contribution) imagenet Large Scale Visual Recognition Challenge.