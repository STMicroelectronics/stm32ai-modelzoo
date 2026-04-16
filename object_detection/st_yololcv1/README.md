# ST YOLO LC V1 quantized

## **Use case** : `Object detection`

# Model description


ST Yolo LC v1 is a real-time object detection model targeted for real-time processing implemented in Tensorflow.

The model is quantized in int8 format using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
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
| STM32H7  | [x]       | [x]         |
| STM32MP1 | [x]       | [x]         |
| STM32MP2 | [x]       | []          |
| STM32N6  | [x]       | []          |

# Performances

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                               | Dataset     | Format      | Resolution   | Series   |   Internal RAM (KiB) |   External RAM (KiB) |   Weights Flash (KiB) | STEdgeAI Core version   |
|---------------------------------------------------------------------------------------------------------------------|-------------|-------------|--------------|----------|----------------------|----------------------|-----------------------|-------------------------|
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_192/st_yololcv1_192_int8.tflite)       | COCO-Person | Int8        | 192x192x3    | STM32N6  |                 252  |                    0 |                269.44 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_224/st_yololcv1_224_int8.tflite)       | COCO-Person | Int8        | 224x224x3    | STM32N6  |                 343  |                    0 |                276.19 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_256/st_yololcv1_256_int8.tflite)       | COCO-Person | Int8        | 256x256x3    | STM32N6  |                 576  |                    0 |                276.19 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_192/st_yololcv1_192_qdq_w4_74.3%_w8_25.7%_a8_100%_map_33.94.onnx)  | COCO-Person | W4A8  | 192x192x3    | STM32N6  |                 252  |                    0 |                169.42 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_224/st_yololcv1_224_qdq_w4_50.53%_w8_49.47%_a8_100%_map_34.99.onnx) | COCO-Person | W4A8  | 224x224x3    | STM32N6  |                 343  |                    0 |                208.17 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_256/st_yololcv1_256_qdq_w4_50.53%_w8_49.47%_a8_100%_map_36.87.onnx) | COCO-Person | W4A8  | 256x256x3    | STM32N6  |                 576  |                    0 |                208.19 | 4.0.0                   |


### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                               | Dataset     | Format      | Resolution   | Board         | Execution Engine   |   Inference time (ms) |   Inf / sec | STEdgeAI Core version   |
|---------------------------------------------------------------------------------------------------------------------|-------------|-------------|--------------|---------------|--------------------|-----------------------|-------------|-------------------------|
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_192/st_yololcv1_192_int8.tflite)       | COCO-Person | Int8        | 192x192x3    | STM32N6570-DK | NPU/MCU            |                  1.90 |      526.32 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_224/st_yololcv1_224_int8.tflite)       | COCO-Person | Int8        | 224x224x3    | STM32N6570-DK | NPU/MCU            |                  2.26 |      442.48 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_256/st_yololcv1_256_int8.tflite)       | COCO-Person | Int8        | 256x256x3    | STM32N6570-DK | NPU/MCU            |                  2.90 |      344.83 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_192/st_yololcv1_192_qdq_w4_74.3%_w8_25.7%_a8_100%_map_33.94.onnx)  | COCO-Person | W4A8  | 192x192x3    | STM32N6570-DK | NPU/MCU            |                  1.85 |      540.54 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_224/st_yololcv1_224_qdq_w4_50.53%_w8_49.47%_a8_100%_map_34.99.onnx) | COCO-Person | W4A8  | 224x224x3    | STM32N6570-DK | NPU/MCU            |                  2.26 |      442.48 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_256/st_yololcv1_256_qdq_w4_50.53%_w8_49.47%_a8_100%_map_36.87.onnx) | COCO-Person | W4A8  | 256x256x3    | STM32N6570-DK | NPU/MCU            |                  2.82 |      354.61 | 4.0.0                   |


### Reference **MCU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                               | Format   | Resolution   | Series   |   Activation RAM (KiB) |   Runtime RAM (KiB) |   Weights Flash (KiB) |   Code Flash (KiB) |   Total RAM (KiB) |   Total Flash (KiB) | STEdgeAI Core version   |
|---------------------------------------------------------------------------------------------------------------------|----------|--------------|----------|------------------------|---------------------|-----------------------|--------------------|--------------------|----------------------|-------------------------|
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_192/st_yololcv1_192_int8.tflite)       | Int8     | 192x192x3    | STM32H7  |                 166.29 |                0    |                276.73 |             31.15 |             166.29 |               307.88 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_224/st_yololcv1_224_int8.tflite)       | Int8     | 224x224x3    | STM32H7  |                 217.29 |                0    |                276.73 |             31.16 |             217.29 |               307.89 | 4.0.0                   |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_256/st_yololcv1_256_int8.tflite)       | Int8     | 256x256x3    | STM32H7  |                 278.29 |                0    |                276.73 |             31.16 |             278.29 |               307.89 | 4.0.0                   |


### Reference **MCU** inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                               | Format   | Resolution   | Board            | Execution Engine   | Frequency   |   Inference time (ms) | STEdgeAI Core version   |
|---------------------------------------------------------------------------------------------------------------------|----------|--------------|------------------|--------------------|-------------|-----------------------|------------------------|
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_192/st_yololcv1_192_int8.tflite)       | Int8     | 192x192x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                 179.33 | 4.0.0                 |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_224/st_yololcv1_224_int8.tflite)       | Int8     | 224x224x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                 245.14 | 4.0.0                 |
| [st_yololcv1](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yololcv1_256/st_yololcv1_256_int8.tflite)       | Int8     | 256x256x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                 321.35 | 4.0.0                 |

### Reference **MPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)

| Model      | Format | Resolution | Quantization   | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|-----------|--------|------------|----------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| st_yololcv1 | Int8   | 192x192x3  | per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 5.26                | 93.66 | 6.34  | 0    | v6.1.0             | OpenVX                |
| st_yololcv1 | Int8   | 224x224x3  | per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 4.90                | 93.55 | 6.45  | 0    | v6.1.0             | OpenVX                |
| st_yololcv1 | Int8   | 256x256x3  | per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800 MHz   | 6.43                | 94.18 | 5.82  | 0    | v6.1.0             | OpenVX                |
| st_yololcv1 | Int8   | 192x192x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 51.42               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| st_yololcv1 | Int8   | 224x224x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 72.44               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| st_yololcv1 | Int8   | 256x256x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 88.55               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| st_yololcv1 | Int8   | 192x192x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 79.26               | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| st_yololcv1 | Int8   | 224x224x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 106.30              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| st_yololcv1 | Int8   | 256x256x3  | per-channel    | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 140.87              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

### AP on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution | AP |
|-------|--------|------------|----|
| st_yololcv1 | Int8 | 192x192x3 |  34.7% |
| st_yololcv1 | Float | 192x192x3 | 34.9 % |
| st_yololcv1 | w4w8 | 192x192x3 | 33.94 % |
| st_yololcv1 | Int8 | 224x224x3 | 35.5 % |
| st_yololcv1 | Float | 224x224x3 | 35.8 % |
| st_yololcv1 | w4w8 | 224x224x3 | 34.99 % |
| st_yololcv1 | Int8 | 256x256x3 | 37.2 % |
| st_yololcv1 | Float | 256x256x3 | 37.3 % |
| st_yololcv1 | w4w8 | 256x256x3 | 36.87 % |

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