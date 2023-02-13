# SSD MobileNet v1 quantized

## **Use case** : [Object detection](../../)

# Model description


The mobilenet-ssd model is a Single-Shot multibox Detection (SSD) network intended to perform object detection.
Mobilenet-ssd is using MobileNet as a backbone which is a general architecture that can be used for multiple use cases.
Depending on the use case, it can use different input layer size and
different width factors. This allows different width models to reduce
the number of multiply-adds and thereby reduce inference cost on mobile devices.

The model is quantized in int8 using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/mobilenet |
|  Paper                  | https://arxiv.org/abs/1704.04861, https://arxiv.org/abs/1512.02325 |

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


To train a SSD mobilenetv1 model with transfer learning or from scratch on your own dataset, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [ssd_mobilenet_v1_025_192_config.yaml](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_192/ssd_mobilenet_v1_025_192_config.yaml) file is used to train this model on the person dataset, you can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below

## Deployment


coming soon.


## Metrics


Measures are done with default STM32Cube.AI (v7.3.0) configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_192/ssd_mobilenet_v1_025_192_int8.tflite) | Int8   | 192x192x3    | STM32H7 | 195.6 KiB     | ~38 KiB      | 438.28 KiB    | ~113 KiB       | 234 KiB   | 551 KiB  |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_224/ssd_mobilenet_v1_025_224_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 333.25 KiB     | ~43 KiB       | 595.66 KiB    | ~127 KiB    | 378 KiB   | 723 KiB  |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_256/ssd_mobilenet_v1_025_256_int8.tflite) | Int8   | 256x256x3   | STM32H7 | 347.3 KiB     | ~43 KiB       | 595.66 KiB    | ~125 KiB    | 391 KiB   | 721 KiB  |


### Reference inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_192/ssd_mobilenet_v1_025_192_int8.tflite) | Int8   | 192x192x3    | STM32H747I-DISCO | 1 CPU | 400 MHz       | 173.1 ms       |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_224/ssd_mobilenet_v1_025_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz       | 254.9 ms       |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_256/ssd_mobilenet_v1_025_256_int8.tflite) | Int8   | 256x256x3    | STM32H747I-DISCO | 1 CPU | 400 MHz       | 310 ms           |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_192/ssd_mobilenet_v1_025_192_int8.tflite) | Int8   | 192x192x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 69.8 ms **     |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_224/ssd_mobilenet_v1_025_224_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 99.9 ms **     |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_256/ssd_mobilenet_v1_025_256_int8.tflite) | Int8   | 256x256x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 163.8 ms **    |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### AP on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP*       |
|-------|--------|------------|----------------|
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_192/ssd_mobilenet_v1_025_192_int8.tflite) | Int8 | 192x192x3   | 33.84 % |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_224/ssd_mobilenet_v1_025_224_int8.tflite) | Int8 | 224x224x3   | 43.86 % |
| [SSD Mobilenet v1 0.25](../ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_256/ssd_mobilenet_v1_025_256_int8.tflite) | Int8 | 256x256x3   | 47.03 % |

\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH =0.001

## Retraining and code generation


- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here]()


## Demos
### Integration in simple example


coming soon.


# References


<a id="1">[1]</a>
Lin, T.Y., Maire, M., Belongie, S., Hays, J., Perona, P., Ramanan, D., Dollár, P. and Zitnick, C.L., 2014. "Microsoft coco: Common objects in context". In Computer Vision–ECCV 2014: 13th European Conference, Zurich, Switzerland, September 6-12, 2014, Proceedings, Part V 13 (pp. 740-755). Springer International Publishing. [Online]. Available: https://cocodataset.org/#download.
