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


To train a SSD mobilenetv1 model with transfer learning or from scratch on your own dataset, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/training/README.md) under the training section.

As an example, [st_ssd_mobilenet_v1_025_192_config.yaml](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_192/st_ssd_mobilenet_v1_025_192_config.yaml) file is used to train this model on the person dataset, you can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the training section to reproduce the results presented below

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_192/st_ssd_mobilenet_v1_025_192_int8.tflite) | Int8   | 192x192x3    | STM32H7 | 249.54 KiB     | 33.76 KiB      | 438.28 KiB    | 108.23 KiB       | 283.3 KiB   | 546.51 KiB  | 8.1.0                 |              |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_224/st_ssd_mobilenet_v1_025_224_int8.tflite) | Int8   | 224x224x3    | STM32H7 | 366.15 KiB     | 38.97 KiB      | 595.66 KiB    | 119.7 KiB       | 405.12 KiB   | 715.36 KiB  | 8.1.0                 |              |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_256/st_ssd_mobilenet_v1_025_256_int8.tflite) | Int8   | 256x256x3    | STM32H7 | 439.34 KiB     | 38.3 KiB       | 595.66 KiB    | 118.87 KiB    | 477.64 KiB   | 714.53 KiB  | 8.1.0                 |


### Reference inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|-----------------------|
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_192/st_ssd_mobilenet_v1_025_192_int8.tflite) | Int8   | 192x192x3    | STM32H747I-DISCO | 1 CPU | 400 MHz       | 169.13 ms      | 8.1.0                 |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_224/st_ssd_mobilenet_v1_025_224_int8.tflite) | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU | 400 MHz       | 241.95 ms      | 8.1.0                 |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_256/st_ssd_mobilenet_v1_025_256_int8.tflite) | Int8   | 256x256x3    | STM32H747I-DISCO | 1 CPU | 400 MHz       | 295.52 ms      | 8.1.0                 |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_192/st_ssd_mobilenet_v1_025_192_int8.tflite) | Int8   | 192x192x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 69.5 ms **     | X-LINUX-AI v5.0.0                 |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_224/st_ssd_mobilenet_v1_025_224_int8.tflite) | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 103.1 ms **    | X-LINUX-AI v5.0.0                 |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_256/st_ssd_mobilenet_v1_025_256_int8.tflite) | Int8   | 256x256x3    | STM32MP157F-DK2  | 2 CPU | 800 MHz       | 121.6 ms **    | X-LINUX-AI v5.0.0                 |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### AP on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP*       |
|-------|--------|------------|----------------|
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_192/st_ssd_mobilenet_v1_025_192_int8.tflite) | Int8 | 192x192x3   | 33.70 % |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_224/st_ssd_mobilenet_v1_025_224_int8.tflite) | Int8 | 224x224x3   | 44.45 % |
| [ST SSD Mobilenet v1 0.25](ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_256/st_ssd_mobilenet_v1_025_256_int8.tflite) | Int8 | 256x256x3   | 46.26 % |

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
