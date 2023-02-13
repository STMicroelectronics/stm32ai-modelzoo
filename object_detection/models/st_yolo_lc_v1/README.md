# ST Yolo LC v1 quantized

## **Use case** : [Object detection](../../../object_detection/README.md)

# Model description


ST Yolo LC v1 is a real-time object detection model targeted for real-time processing implemented in Tensorflow.

The model is quantized in int8 format using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             | ST |
|  Paper                  | - |

The models are quantized using tensorflow lite converter.


## Network inputs / outputs


For an image resolution of NxM and NC classes

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

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
| STM32MP1 | [x]       | [x]          |


# Performances
## Training


To train ST_Yolo_LC_v1 model using transfer learning or from scratch on your own dataset, please get in touch with us.


## Deployment


coming soon.


## Metrics


Measures are done with default STM32Cube.AI (v7.3.0) configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|
| ST Yolo LC v1 | Int8   | 192x192x3    | STM32H7 | 157.44 KiB     | ~9 KiB      | 276.73 KiB    | ~55 KiB       | ~167 KiB   | ~332 KiB  |
| ST Yolo LC v1 | Int8   | 224x224x3    | STM32H7 | 210.69 KiB     | ~9 KiB       | 276.73 KiB    | ~55 KiB    | ~220 KiB   | ~332 KiB  |
| ST Yolo LC v1 | Int8   | 256x256x3   | STM32H7 | 271.94 KiB     | ~9 KiB       | 276.73 KiB    | ~55 KiB    | ~281 KiB   | ~332 KiB  |


### Reference inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|
| ST Yolo LC v1     | Int8   | 192x192x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 192.8 ms            |
| ST Yolo LC v1     | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 263.1 ms            |
| ST Yolo LC v1     | Int8   | 256x256x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 343.4 ms            |
| ST Yolo LC v1     | Int8   | 192x192x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz     | 50.9 ms **          |
| ST Yolo LC v1     | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz     | 69.7 ms **          |
| ST Yolo LC v1     | Int8   | 256x256x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz     | 88.1 ms **          |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### AP on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP       |
|-------|--------|------------|----------------|
| ST Yolo LC v1 | Int8 | 192x192x3   | 39.92 % |
| ST Yolo LC v1 | Int8 | 224x224x3   | 42.75 % |
| ST Yolo LC v1 | Int8 | 256x256x3   | 45.09 % |


## Retraining and code generation


- Please get in touch with us for more details.


## Demos
### Integration in simple example


coming soon.


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
