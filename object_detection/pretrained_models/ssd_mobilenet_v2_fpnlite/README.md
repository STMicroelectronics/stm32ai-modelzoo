# SSD MobileNet v2 FPN-lite quantized

## **Use case** : [Object detection](../../)

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
| STM32MP2 | [x]       | []          |

# Performances
## Training


To train a SSD_mobilenetv2_fpn-lite model with transfer learning or from scratch on your own dataset, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/training/README.md) under the training section.

As an example, [ssd_mobilenet_v2_fpnlite_035_192_config.yaml](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_config.yaml) file is used to train this model on the person dataset, you can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the training section to reproduce the results presented below

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference **MCU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3   | STM32H7 | 711.45 KiB      | 70.3 KiB       | 984.25 KiB     | 190.26 KiB    | 781.75 KiB   | 1174.51 KiB  | 9.1.0                 |              |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3   | STM32H7 | 956.82 KiB      | 70.3 KiB       | 1007.78 KiB    | 191.45 KiB    | 1027.12 KiB   | 1199.23 KiB  | 9.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3   | STM32H7 | 1238.29 KiB     | 70.3 KiB       | 1032.26 KiB    | 192.68 KiB    | 1308.59 KiB   | 1224.94 KiB  | 9.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3   | STM32H7 | 2541.27 KiB     | 70.3 KiB       | 1109.27 KiB    | 194.22 KiB    | 2611.73 KiB   | 1303.49 KiB  | 9.1.0                 |


### Reference **MCU** inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|-----------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 512.33 ms      | 9.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 675.63 ms     | 9.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 937.87 ms    | 9.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 2784.13 ms    | 9.1.0                 |


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
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8 | 192x192x3   | 40.73 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8 | 224x224x3   | 48.67 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8 | 256x256x3   | 55.56 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8 | 416x416x3   | 59.09 % |


\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH =0.001


### AP on COCO 80 classes dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP*       |
|-------|--------|------------|----------------|
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_256/ssd_mobilenet_v2_fpnlite_100_256_int8.tflite) | Int8   | 256x256x3  | 32.2 % |
| [SSD Mobilenet v2 1.0 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/ssd_mobilenet_v2_fpnlite_100_416/ssd_mobilenet_v2_fpnlite_100_416_int8.tflite) | Int8   | 416x416x3  | 32.3 % |

\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH =0.001

## Retraining and code generation


- Link to training script: [here](../../src/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../deployment/README.md)


## Demos
### Integration in simple example


coming soon.


# References


<a id="1">[1]</a>
Lin, T.Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., Dollár, P. and Zitnick, C.L., 2014. "Microsoft coco: Common objects in context". In Computer Vision–ECCV 2014: 13th European Conference, Zurich, Switzerland, September 6-12, 2014, Proceedings, Part V 13 (pp. 740-755). Springer International Publishing. [Online]. Available: https://cocodataset.org/#download.
