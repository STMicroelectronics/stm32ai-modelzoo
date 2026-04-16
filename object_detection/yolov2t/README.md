# Tiny Yolo v2 quantized

## **Use case** : `Object detection`

# Model description


Tiny Yolo v2 is a real-time object detection model targeted for real-time processing implemented in Tensorflow.

The model is quantized in int8 format using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             | https://github.com/AlexeyAB/darknet
|  Paper                  | https://pjreddie.com/media/files/papers/YOLO9000.pdf |

The models are quantized using tensorflow lite converter.


## Network inputs / outputs


For an image resolution of NxM and NC classes

| Input Shape | Description |
| ----- | ----------- |
| (1, W, H, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, WxH, NAx(5+NC)) | FLOAT values Where WXH is the resolution of the output grid cell, NA is the number of anchors and NC is the number of classes|


## Recommended Platforms


| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | [x]       | []         |
| STM32MP1 | [x]       | [x]          |
| STM32MP2 | [x]       | [x]          |
| STM32N6  | [x]       | [x]          |

# Performances

## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                            | Dataset     | Format   | Resolution   | Series   |   Internal RAM (KiB) |   External RAM (KiB) |   Weights Flash (KiB) | STEdgeAI Core version   |
|------------------------------------------------------------------------------------------------------------------|-------------|----------|--------------|----------|----------------------|----------------------|-----------------------|-------------------------|
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | COCO-Person | Int8     | 224x224x3    | STM32N6  |               343    |                    0 |               10568.87 | 4.0.0                   |
| [yolov2t](ST_pretrainedmodel_custom_dataset/st_person/yolov2t_224/yolov2t_224_int8.tflite)        | ST-Person   | Int8     | 224x224x3    | STM32N6  |               343    |                    0 |               10856.87 | 4.0.0                   |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | COCO-Person | Int8     | 416x416x3    | STM32N6  |              1690    |                    0 |               10884.56 | 4.0.0                   |

### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                            | Dataset     | Format   | Resolution   | Board         | Execution Engine   |   Inference time (ms) |   Inf / sec | STEdgeAI Core version   |
|------------------------------------------------------------------------------------------------------------------|-------------|----------|--------------|---------------|--------------------|-----------------------|-------------|-------------------------|
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | COCO-Person | Int8     | 224x224x3    | STM32N6570-DK | NPU/MCU            |                 30.68 |       32.59 | 4.0.0                   |
| [yolov2t](ST_pretrainedmodel_custom_dataset/st_person/yolov2t_224/yolov2t_224_int8.tflite)        | ST-Person   | Int8     | 224x224x3    | STM32N6570-DK | NPU/MCU            |                 30.38 |       32.65 | 4.0.0                   |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | COCO-Person | Int8     | 416x416x3    | STM32N6570-DK | NPU/MCU            |                 50.26 |       19.80 | 4.0.0                   |

### Reference **MCU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)

| Model                                                                                                            | Format   | Resolution   | Series   | Activation RAM   | Runtime RAM   | Weights Flash   | Code Flash   | Total RAM   | Total Flash   | STEdgeAI Core version   |
|------------------------------------------------------------------------------------------------------------------|----------|--------------|----------|------------------|---------------|-----------------|--------------|-------------|---------------|------------------------|
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_192/yolov2t_192_int8.tflite) | Int8     | 192x192x3    | STM32H7  | 220.6 KiB        | 7.98 KiB      | 10775.98 KiB    | 55.85 KiB    | 228.58 KiB  | 10816.05 KiB  | 4.0.0                 |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | Int8     | 224x224x3    | STM32H7  | 249.35           | 7.98 KiB      | 10775.98        | 55.24        | 253.93      | 10816.05      | 4.0.0                 |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | Int8     | 416x416x3    | STM32H7  | 1263.07          | 8.03 KiB      | 10775.98        | 55.29        | 1271.10     | 10816.05      | 4.0.0                 |

### Reference **MCU** inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model                                                                                                            | Format   | Resolution   | Board            | Execution Engine   | Frequency   | Inference time (ms)   | STEdgeAI Core version   |
|------------------------------------------------------------------------------------------------------------------|----------|--------------|------------------|--------------------|-------------|-----------------------|------------------------|
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_192/yolov2t_192_int8.tflite) | Int8     | 192x192x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     | 3006.3 ms             | 4.0.0                 |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | Int8     | 224x224x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     | 2550.46               | 4.0.0                 |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | Int8     | 416x416x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     | 10123.1              | 4.0.0                 |

### Reference **MPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)

| Model                                                                                     | Format | Resolution | Quantization   | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|-------------------------------------------------------------------------------------------|--------|------------|----------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | Int8   | 224x224x3  | per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 8.27                | 96.57 | 3.43  | 0    | v6.1.0             | OpenVX                |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | Int8   | 416x416x3  | per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 14.62               | 96.42 | 3.58  | 0    | v6.1.0             | OpenVX                |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | Int8   | 224x224x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 698.54              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | Int8   | 416x416x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 2161.35             | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | Int8   | 224x224x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 1037.84             | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | Int8   | 416x416x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 3581.99             | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

### AP on COCO Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP       |
|-------|--------|------------|----------------|
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_192/yolov2t_192_int8.tflite) | Int8 | 192x192x3   | 26.29 % |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_192/yolov2t_192.keras) | Float | 192x192x3   | 27.50 % |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224_int8.tflite) | Int8 | 224x224x3   | 28.4 % |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_224/yolov2t_224.keras) | Float | 224x224x3   | 30.85 % |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416_int8.tflite) | Int8 | 416x416x3   | 41.93 % |
| [yolov2t](ST_pretrainedmodel_public_dataset/coco_2017_person/yolov2t_416/yolov2t_416.keras) | Float | 416x416x3   | 43.41 % |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on ST Person dataset
This model has been trained using a STMicroelectronics proprietary dataset which is not provided as part of the STM32 model zoo. The ST person dataset has been built by aggregating several public datasets and by applying data augmentation on these public datasets. If users wish to retrain this model it has to be done using another dataset selected by the user.

| Model | Format | Resolution |       AP       |
|-------|--------|------------|----------------|
| [yolov2t](ST_pretrainedmodel_custom_dataset/st_person/yolov2t_224/yolov2t_224_int8.tflite) | Int8 | 224x224x3   |  28.5 % |


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
