# ST YOLO LC V1 quantized

## **Use case** : [Object detection](../../../object_detection/README.md)

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


# Performances
## Training


To train a st_yolo_lc_v1 model with transfer learning or from scratch on your own dataset, you need to configure the
[user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../README.md) under the training section.
As an example, [st_yolo_lc_v1_224_config.yaml](./ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_lc_v1_224/st_yolo_lc_v1_224_config.yaml) file is used to train this model on the person dataset, you can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the training section to reproduce the results presented below

## Deployment


To deploy your trained model, you need to configure the same [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README.md).


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference **MCU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash      | Total RAM    | Total Flash | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|-----------------|--------------|-------------|-----------------------|
| st_yolo_lc_v1     | Int8   | 192x192x3  | STM32H7 | 166.29 KiB     | 8.09 KiB    | 276.73 KiB    | 53.51 KiB      | 174.38 KiB    | 330.23 KiB  | 9.1.0         |
| st_yolo_lc_v1     | Int8   | 224x224x3  | STM32H7 | 217.29 KiB     | 8.09 KiB    | 276.73 KiB    | 53.51 KiB      | 225.38 KiB    | 330.24 KiB  | 9.1.0           |
| st_yolo_lc_v1     | Int8   | 256x256x3  | STM32H7 | 278.29 KiB     | 8.09 KiB    | 276.73 KiB    | 53.51 KiB      | 286.38 KiB    | 330.23 KiB  | 9.1.0           |


### Reference **MCU** inference time based on COCO Person dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-------------|---------------------|-----------------------|
| st_yolo_lc_v1     | Int8   | 192x192x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 179.35 ms         | 9.1.0                 |
| st_yolo_lc_v1     | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 244.7 ms          | 9.1.0                 |
| st_yolo_lc_v1     | Int8   | 256x256x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz     | 321.23 ms         | 9.1.0                 |


### Reference **MPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)

| Model         | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|---------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| st_yolo_lc_v1 | Int8   | 192x192x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 12.00 ms            | 2.62  | 97.38 |0     | v5.1.0             | OpenVX                |
| st_yolo_lc_v1 | Int8   | 224x224x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 17.92 ms            | 2.43  | 97.57 |0     | v5.1.0             | OpenVX                |
| st_yolo_lc_v1 | Int8   | 256x256x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 14.43 ms            | 3.20  | 96.80 |0     | v5.1.0             | OpenVX                |
| st_yolo_lc_v1 | Int8   | 192x192x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 32.84 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| st_yolo_lc_v1 | Int8   | 224x224x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 45.13 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| st_yolo_lc_v1 | Int8   | 256x256x3  |  per-channel  | STM32MP157F-DK2   | 2 CPU            | 800  MHz  | 59.38 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| st_yolo_lc_v1 | Int8   | 192x192x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 52.64 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| st_yolo_lc_v1 | Int8   | 224x224x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 71.26 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |
| st_yolo_lc_v1 | Int8   | 256x256x3  |  per-channel  | STM32MP135F-DK2   | 1 CPU            | 1000 MHz  | 93.50 ms            | NA    | NA    |100   | v5.1.0             | TensorFlowLite 2.11.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### AP on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Format | Resolution |       AP       |
|-------|--------|------------|----------------|
| st_yolo_lc_v1 | Int8 | 192x192x3   | 31.61 % |
| st_yolo_lc_v1 | Int8 | 224x224x3   | 36.80 % |
| st_yolo_lc_v1 | Int8 | 256x256x3   | 40.58 % |

\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH =0.001
## Retraining and code generation


Please refer to the yaml explanations: [here](../../src/README.md)


## Demos
### Integration in a simple example


Please refer to the generic guideline [here](../../deployment/README.md)



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
