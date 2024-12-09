# SSD MobileNet v2 FPN-lite quantized

## **Use case** : `Object detection`

# Model description


The mobilenet-ssd model is a Single-Shot multibox Detection (SSD) network intended to perform object detection.
Mobilenet-ssd is using MobileNetV2 as a backbone which is a general architecture that can be used for multiple use cases.
Depending on the use case, it can use different input layer size and
different width factors. This allows different width models to reduce
the number of multiply-adds and thereby reduce inference cost on mobile devices.

The model is quantized in int8 using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/mobilenet_v2 |
|  Paper                  | https://arxiv.org/abs/1801.04381, https://arxiv.org/abs/1512.02325 |

The models are quantized using tensorflow lite converter.


## Network inputs / outputs


For an image resolution of NxM and NC classes

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, NA, 8 + NC) | FLOAT values Where NA is thge number of anchors and NC is the number of classes|


## Recommended Platforms


| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | [x]       | [x]         |
| STM32MP1 | [x]       | [x]         |
| STM32MP2 | [x]       | [x]         |
| STM32N6  | [x]       | [x]         |

# Performances

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB)  | Weights Flash (KiB)  | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite)  | COCO-Person      | Int8     | 192x192x3  | STM32N6   |   606.49      |      0.0          |   1580.53          |       10.0.0        |     2.0.0   |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | COCO-Person      | Int8     | 224x224x3  | STM32N6   |     1314.67   |        0.0          |    1607.41	         |       10.0.0        |     2.0.0   |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6   |      1959.06   |        0.0         |     1637.02        |       10.0.0        |     2.0.0   |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | COCO-Person      | Int8     | 416x416x3  | STM32N6   |     4570.03    |        0.0          |     1837.8        |       10.0.0        |     2.0.0   |

### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | COCO-Person      | Int8     | 192x192x3  | STM32N6570-DK   |   NPU/MCU      |      14.37          |  69.57           |       10.0.0        |     2.0.0   |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | COCO-Person      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |        18.15        |  55.10           |       10.0.0        |     2.0.0   |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |         21.73       |     46.03        |       10.0.0        |     2.0.0   |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | COCO-Person      | Int8     | 416x416x3  | STM32N6570-DK   |   NPU/MCU      |      114.12          |     8.76        |       10.0.0        |     2.0.0   |

### Reference **MCU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)


| Model | Format | Resolution | Series  | Activation RAM (KiB)  | Runtime RAM (KiB)  | Weights Flash (KiB)  | Code Flash (KiB)  | Total RAM (KiB) | Total Flash (KiB) | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3   | STM32H7 |  521.210.0.0        |  70.26       |  1098.76  |  192.69    |  591.46     |  1291.45 | 10.0.0                 |              |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3   | STM32H7 |  956.82       |  70.3        |  1120.63  |  192.84    |  1027.12    |  1313.47 | 10.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3   | STM32H7 |  1238.29      |  70.3        |  1145.24    |  192.81  |  1308.59 | 1338.05  | 10.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3   | STM32H7 |  2869.05      |  70.3        |  1321.02    |  193.23  |  2939.35    | 1514.25 | 10.0.0                 |


### Reference **MCU** inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|-----------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 511.16 ms      | 10.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 673.19 ms     | 10.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 898.32 ms    | 10.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 2684.93 ms    | 10.0.0                 |


### Reference **MPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)

| Model                                                                                                                                                              | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 35.08 ms            | 6.20  | 93.80 |0     | v5.1.0             | OpenVX                |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 48.92 ms            | 6.19  | 93.81 |0     | v5.1.0             | OpenVX                |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 40.66 ms            | 7.07  | 92.93 |0     | v5.1.0             | OpenVX                |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 110.4 ms            | 4.47  | 95.53 |0     | v5.1.0             | OpenVX                |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 193.70 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 263.60 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 339.40 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 894.00 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 287.40 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 383.40 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 498.90 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 1348.00  ms         | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |


### Reference **MPU** inference time based on COCO 80 classes dataset (see Accuracy for details on dataset)

| Model                                                                                                                                                              | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_256/ssd_mobilenet_v2_fpnlite_100_256_int8.tflite) | Int8   | 256x256x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 100.90 ms            | 8.86  | 91.14 |0     | v5.1.0             | OpenVX                |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_416/ssd_mobilenet_v2_fpnlite_100_416_int8.tflite) | Int8   | 416x416x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 280.00 ms            | 8.68  | 91.32 |0     | v5.1.0             | OpenVX                |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_256/ssd_mobilenet_v2_fpnlite_100_256_int8.tflite) | Int8   | 256x256x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 742.90 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_416/ssd_mobilenet_v2_fpnlite_100_416_int8.tflite) | Int8   | 416x416x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  |  2000 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_256/ssd_mobilenet_v2_fpnlite_100_256_int8.tflite) | Int8   | 256x256x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 1112.00 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_416/ssd_mobilenet_v2_fpnlite_100_416_int8.tflite) | Int8   | 416x416x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  |  2986 ms           | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |



** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### AP on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP*       |
|-------|--------|------------|----------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8 | 192x192x3   | 40.7 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192.h5) | Float | 192x192x3   | 40.8 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8 | 224x224x3   | 51.1 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224.h5) | Float | 224x224x3   | 51.7 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8 | 256x256x3   | 58.3 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256.h5) | Float | 256x256x3   | 58.8 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8 | 416x416x3   | 61.9 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416.h5) | Float | 416x416x3   | 62.6 % |


\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH =0.001


### AP on COCO 80 classes dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP*       |
|-------|--------|------------|----------------|
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_256/ssd_mobilenet_v2_fpnlite_100_256_int8.tflite) | Int8   | 256x256x3  | 32.2 % |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_256/ssd_mobilenet_v2_fpnlite_100_256.h5) | Float   | 256x256x3  |  32.6 % |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_416/ssd_mobilenet_v2_fpnlite_100_416_int8.tflite) | Int8   | 416x416x3  | 32.3 % |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_416/ssd_mobilenet_v2_fpnlite_100_416.h5) | Float   | 416x416x3  |  34.8 % |

\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH =0.001

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References


<a id="1">[1]</a>
Lin, T.Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., Dollár, P. and Zitnick, C.L., 2014. "Microsoft coco: Common objects in context". In Computer Vision–ECCV 2014: 13th European Conference, Zurich, Switzerland, September 6-12, 2014, Proceedings, Part V 13 (pp. 740-755). Springer International Publishing. [Online]. Available: https://cocodataset.org/#download.
