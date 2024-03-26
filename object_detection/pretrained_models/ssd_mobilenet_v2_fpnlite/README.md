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
| STM32MP1 | [x]       | [x]          |


# Performances
## Training


To train a SSD_mobilenetv2_fpn-lite model with transfer learning or from scratch on your own dataset, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/training/README.md) under the training section.

As an example, [ssd_mobilenet_v2_fpnlite_035_192_config.yaml](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_config.yaml) file is used to train this model on the person dataset, you can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the training section to reproduce the results presented below

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3   | STM32H7 | 565.25 KiB      | 75.79 KiB       | 984.25 KiB     | 203.23 KiB    | 641.04 KiB   | 1187.48 KiB  | 8.1.0                 |              |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3   | STM32H7 | 769.12 KiB      | 76.02 KiB       | 1059.17 KiB    | 207.28 KiB    | 845.14 KiB   | 1266.45 KiB  | 8.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3   | STM32H7 | 1003.73 KiB     | 76.02 KiB       | 1065.32 KiB    | 207.13 KiB    | 1079.75 KiB   | 1272.45 KiB  | 8.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3   | STM32H7 | 2673.27 KiB     | 75.97 KiB       | 1109.27 KiB    | 205.71 KiB    | 2749.24 KiB   | 1314.98 KiB  | 8.1.0                 |


### Reference inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|-----------------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 646.4 ms      | 8.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 902.24 ms     | 8.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 1187.92 ms    | 8.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3    | STM32H747I-DISCO | 1 CPU | 400 MHz      | 3184.82 ms    | 8.1.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8   | 192x192x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz      | 196.579 ms **    | X-LINUX-AI v5.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz      | 266.396 ms **    | X-LINUX-AI v5.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8   | 256x256x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz      | 347.193 ms **    | X-LINUX-AI v5.0.0                 |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8   | 416x416x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz      | 898.08  ms **    | X-LINUX-AI v5.0.0                 |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### AP on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP*       |
|-------|--------|------------|----------------|
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite) | Int8 | 192x192x3   | 40.73 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite) | Int8 | 224x224x3   | 48.67 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite) | Int8 | 256x256x3   | 55.56 % |
| [SSD Mobilenet v2 0.35 FPN-lite](ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite) | Int8 | 416x416x3   | 59.09 % |

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
