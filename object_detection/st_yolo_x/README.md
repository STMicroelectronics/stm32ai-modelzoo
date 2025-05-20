# ST Yolo X quantized

## **Use case** : `Object detection`

# Model description


ST Yolo X is a real-time object detection model targeted for real-time processing implemented in Tensorflow.
This is an optimized ST version of the well known yolo x, quantized in int8 format using tensorflow lite converter.

## Network information

| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             |   |
|  Paper                  |   |



## Network inputs / outputs

For an image resolution of NxM and NC classes

| Input Shape | Description |
| ----- | ----------- |
| (1, W, H, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
|   |    |


## Recommended Platforms

| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | [x]       | []          |
| STM32MP1 | [x]       | []          |
| STM32MP2 | [x]       | [x]         |
| STM32N6  | [x]       | [x]         |


# Performances

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB)| Weights Flash (KiB)| STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_192/st_yolo_x_nano_192_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 192x192x3  | STM32N6   |  324 | 0.0 | 1028.08  |  10.0.0 | 2.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6   |   624 | 0.0 | 1028.08 | 10.0.0 | 2.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.5_0.4_int8.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6   |       971.62 | 0.0 | 2547.17 | 10.0.0  | 2.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_320/st_yolo_x_nano_320_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 320x320x3  | STM32N6   |     968.5 | 0.0 | 1028.08 | 10.0.0 | 2.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_416/st_yolo_x_nano_416_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 416x416x3  | STM32N6 | 2640.62 | 0.0 | 1027.89 | 10.0.0 | 2.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_480/st_yolo_x_nano_480_1.0_0.25_3_int8.tflite) | COCO-Person      | Int8     | 480x480x3  | STM32N6 | 2418.75 | 0.0 | 1383.56 | 10.0.0 | 2.0.0 |

### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_192/st_yolo_x_nano_192_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 192x192x3  | STM32N6570-DK   |   NPU/MCU      |   5.99   |   166.94 |       10.0.0        |     2.0.0   |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |   8.5  |   117.65  |       10.0.0        |     2.0.0   |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.5_0.4_int8.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |     21.12     |    47.35    |       10.0.0        |     2.0.0   |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_320/st_yolo_x_nano_320_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 320x320x3  | STM32N6570-DK   |   NPU/MCU      |       11.59    |   86.29   |       10.0.0        |     2.0.0   |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_416/st_yolo_x_nano_416_0.33_0.25_int8.tflite) | COCO-Person      | Int8     | 416x416x3  | STM32N6570-DK   |   NPU/MCU      |    17.99  |    55.59   |       10.0.0        |     2.0.0   |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_480/st_yolo_x_nano_480_1.0_0.25_3_int8.tflite) | COCO-Person      | Int8     | 480x480x3  | STM32N6570-DK   |   NPU/MCU      |    32.4  |    30.8  |       10.0.0        |     2.0.0   |

### Reference **MCU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)

| Model             | Format | Resolution   | Series  | Activation RAM (KiB) | Runtime RAM (KiB)| Weights Flash (KiB)| Code Flash (KiB)| Total RAM   | Total Flash  | STM32Cube.AI version  |
|-------------------|--------|--------------|---------|----------------|-------------|---------------|------------|-------------|--------------|-----------------------|
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_192/st_yolo_x_nano_192_0.33_0.25_int8.tflite) |                                                        Int8 | 192x192x3 | STM32H7 | 162.42 | 64.05 | 891.18 |  166.19  |  226.47 | 1057.37 | 10.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.33_0.25_int8.tflite) |                                                          Int8 | 256x256x3 | STM32H7 | 284.92 | 64.05 | 891.18  | 166.21 | 348.97 |  1057.39 | 10.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.5_0.4_int8.tflite) |                                                                Int8   | 256x256x3    | STM32H7 |  463.9 |  83.8   |  2435.76 |  228.22| 547.7  |2663.98 | 10.0.0 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_320/st_yolo_x_nano_320_0.33_0.25_int8.tflite) |                                                            Int8   | 320x320x3    | STM32H7 | 442.42 |  64.05 |  891.18 |  166.25  |  506.47 | 1057.43 | 10.0.0 |


### Reference **MCU** inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model            | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|------------------|--------|------------|------------------|------------------|-------------|---------------------|-----------------------|
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_192/st_yolo_x_nano_192_0.33_0.25_int8.tflite) | Int8   | 192x192x3  | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 352.4      | 10.0.0                 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.33_0.25_int8.tflite) | Int8   | 256x256x3  | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 619.92   | 10.0.0                 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.5_0.4_int8.tflite) | Int8   | 256x256x3  | STM32H747I-DISCO | 1 CPU            | 400 MHz     |  1696.59   | 10.0.0                 |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_320/st_yolo_x_nano_320_0.33_0.25_int8.tflite) | Int8   | 320x320x3  | STM32H747I-DISCO | 1 CPU            | 400 MHz     |  988.86  | 10.0.0                 |



### AP on COCO Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution | Depth Multiplier | Width Multiplier | Anchors | AP |
|-------|--------|------------|------------------|------------------|---------|----|
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_192/st_yolo_x_nano_192_0.33_0.25_int8.tflite) | Int8 | 192x192x3 | 0.33 | 0.25 | 1 | 36.1 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_192/st_yolo_x_nano_192_0.33_0.25.h5) | Float | 192x192x3 | 0.33 | 0.25 | 1 | 36.1 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.33_0.25_int8.tflite) | Int8 | 256x256x3 | 0.33 | 0.25 | 1 | 44.2 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.33_0.25.h5) | Float | 256x256x3 | 0.33 | 0.25 | 1 | 44.1 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.5_0.4_int8.tflite) | Int8 | 256x256x3 | 0.5 | 0.4 | 1 | 50.1 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_256/st_yolo_x_nano_256_0.5_0.4.h5) | Float | 256x256x3 | 0.5 | 0.4 | 1 | 50.0 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_320/st_yolo_x_nano_320_0.33_0.25_int8.tflite) | Int8 | 320x320x3 | 0.33 | 0.25 | 1 | 48.8 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_320/st_yolo_x_nano_320_0.33_0.25.h5) | Float | 320x320x3 | 0.33 | 0.25 | 1 | 48.5 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_416/st_yolo_x_nano_416_0.33_0.25_int8.tflite) | Int8 | 416x416x3 | 0.33 | 0.25 | 1 | 54.0 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_416/st_yolo_x_nano_416_0.33_0.25.h5) | Float | 416x416x3 | 0.33 | 0.25 | 1 | 54.5 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_480/st_yolo_x_nano_480_1.0_0.25_3_int8.tflite) | Int8 | 480x480x3 | 1.0 | 0.25 | 3 | 61.4 % |
| [st_yolo_x_nano](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_x_nano_480/st_yolo_x_nano_480_1.0_0.25_3.h5) | Float | 480x480x3 | 1.0 | 0.25 | 3 | 62.1 % |


\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References


<a id="1">[1]</a>
“Microsoft COCO: Common Objects in Context”. [Online]. Available: https://cocodataset.org/#download.
@article{DBLP:journals/corr/LinMBHPRDZ14,
  author    = {Tsung{-}Yi Lin and
               Michael Maire and
               Serge J. Belongie and
               Lubomir D. Bourdev and
               Ross B. Girshick and
               James Hays and
               Pietro Perona and
               Deva Ramanan and
               Piotr Doll{'{a} }r and
               C. Lawrence Zitnick},
  title     = {Microsoft {COCO:} Common Objects in Context},
  journal   = {CoRR},
  volume    = {abs/1405.0312},
  year      = {2014},
  url       = {http://arxiv.org/abs/1405.0312},
  archivePrefix = {arXiv},
  eprint    = {1405.0312},
  timestamp = {Mon, 13 Aug 2018 16:48:13 +0200},
  biburl    = {https://dblp.org/rec/bib/journals/corr/LinMBHPRDZ14},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
