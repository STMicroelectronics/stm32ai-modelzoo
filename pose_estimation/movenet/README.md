# MoveNet quantized

## **Use case** : `Pose estimation`

# Model description


MoveNet is a single pose estimation model targeted for real-time processing implemented in Tensorflow.

The model is quantized in int8 format using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             | https://www.kaggle.com/models/google/movenet
|  Paper                  | https://storage.googleapis.com/movenet/MoveNet.SinglePose%20Model%20Card.pdf |


## Networks inputs / outputs

With an image resolution of NxM with K keypoints to detect :

- For heatmaps models

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, W, H, K) | FLOAT values Where WXH is the resolution of the output heatmaps and K is the number of keypoints|

- For the other models

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, Kx3) | FLOAT values Where Kx3 are the (x,y,conf) values of each keypoints |


## Recommended Platforms


| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | []        | []          |
| STM32MP1 | [x]       | []          |
| STM32MP2 | [x]       | [x]         |
| STM32N6  | [x]       | [x]         |

# Performances

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB)| External RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_public_dataset/custom_dataset_person_13kpts/st_movenet_lightning_heatmaps_192/st_movenet_lightning_heatmaps_192_int8_pc.tflite)  | COCO-Person      | Int8     | 192x192x3  | STM32N6   |    1674     |       0.0        |      3036.17       |       10.0.0        |     2.0.0   |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_192/movenet_lightning_heatmaps_192_int8_pc.tflite)  | COCO-Person      | Int8     | 192x192x3  | STM32N6   |    1674     |       0.0        |       3036.41    |       10.0.0        |     2.0.0   |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_224/movenet_lightning_heatmaps_224_int8_pc.tflite)  | COCO-Person      | Int8     | 224x224x3  | STM32N6   |   2058      |       0.0        |     3088.56        |       10.0.0        |     2.0.0   |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_256/movenet_lightning_heatmaps_256_int8_pc.tflite)  | COCO-Person      | Int8     | 256x256x3  | STM32N6   |   2360      |       0.0        |      3141.36       |       10.0.0        |     2.0.0   |


### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_public_dataset/custom_dataset_person_13kpts/st_movenet_lightning_heatmaps_192/st_movenet_lightning_heatmaps_192_int8_pc.tflite) | COCO-Person      | Int8     | 192x192x3  | STM32N6570-DK   |   NPU/MCU      |      18.44          |      54.23       |       10.0.0        |     2.0.0   |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_192/movenet_lightning_heatmaps_192_int8_pc.tflite) | COCO-Person      | Int8     | 192x192x3  | STM32N6570-DK   |   NPU/MCU      |      18.49          |      54.08       |       10.0.0        |     2.0.0   |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_224/movenet_lightning_heatmaps_224_int8_pc.tflite) | COCO-Person      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |      22.33          |      44.78       |       10.0.0        |     2.0.0   |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_256/movenet_lightning_heatmaps_256_int8_pc.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |      27.01          |      37.03       |       10.0.0        |     2.0.0   |


### Reference **MPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model         | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_public_dataset/custom_dataset_person_13kpts/st_movenet_lightning_heatmaps_192/st_movenet_lightning_heatmaps_192_int8_pc.tflite) | Int8   | 192x192x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 58.02 ms            | 3.75  | 96.25 |0     | v5.0.0             | OpenVX                |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_public_dataset/custom_dataset_person_13kpts/st_movenet_lightning_heatmaps_192/st_movenet_lightning_heatmaps_192_int8_pt.tflite) | Int8   | 192x192x3  |  per-tensor     | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  |  7.93 ms            | 84.89 | 15.11 |0     | v5.0.0             | OpenVX                |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_192/movenet_lightning_heatmaps_192_int8_pc.tflite)      | Int8   | 192x192x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 58.17 ms            | 3.80  | 96.20 |0     | v5.0.0             | OpenVX                |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_192/movenet_lightning_heatmaps_192_int8_pt.tflite)      | Int8   | 192x192x3  |  per-tensor     | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  |  8.00 ms            | 86.48 | 13.52 |0     | v5.0.0             | OpenVX                |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_224/movenet_lightning_heatmaps_224_int8_pc.tflite)      | Int8   | 224x224x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 81.65 ms            | 2.77  | 97.23 |0     | v5.0.0             | OpenVX                |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_224/movenet_lightning_heatmaps_224_int8_pt.tflite)      | Int8   | 224x224x3  |  per-tensor     | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 11.55 ms            | 87.04 | 12.96 |0     | v5.0.0             | OpenVX                |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_256/movenet_lightning_heatmaps_256_int8_pc.tflite)      | Int8   | 256x256x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 70.57 ms            | 3.74  | 96.26 |0     | v5.0.0             | OpenVX                |
| [MoveNet Lightning heatmaps](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_256/movenet_lightning_heatmaps_256_int8_pc.tflite)      | Int8   | 256x256x3  |  per-tensor     | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 12.90 ms            | 86.33 | 13.67 |0     | v5.0.0             | OpenVX                |
| [MoveNet Lightning](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_192/movenet_singlepose_lightning_192_int8.tflite)                         | Int8   | 192x192x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 66.97 ms            | 6.72  | 93.28 |0     | v5.0.0             | OpenVX    
| [MoveNet Thunder](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_thunder_256/movenet_singlepose_thunder_256_int8.tflite)                               | Int8   | 256x256x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 187.1 ms            | 3.96  | 96.04 |0     | v5.0.0             | OpenVX                |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### OKS on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287


| Model | Format | Resolution |       OKS      |
|-------|--------|------------|----------------|
| [ST MoveNet Lightning heatmaps per-channel](ST_pretrainedmodel_public_dataset/custom_dataset_person_13kpts/st_movenet_lightning_heatmaps_192/st_movenet_lightning_heatmaps_192_int8_pc.tflite) | Int8   | 192x192x3  | *52.1 % |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_public_dataset/custom_dataset_person_13kpts/st_movenet_lightning_heatmaps_192/st_movenet_lightning_heatmaps_192_int8_pt.tflite)  | Int8   | 192x192x3  | *39.31 % |
| [MoveNet Lightning heatmaps per-channel](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_192/movenet_lightning_heatmaps_192_int8_pc.tflite)      | Int8   | 192x192x3  | 54.01 %  |
| [MoveNet Lightning heatmaps per-tensor](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_192/movenet_lightning_heatmaps_192_int8_pt.tflite)       | Int8   | 192x192x3  | 48.49 %  |
| [MoveNet Lightning heatmaps per-channel](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_224/movenet_lightning_heatmaps_224_int8_pc.tflite)      | Int8   | 224x224x3  | 57.07 %  |
| [MoveNet Lightning heatmaps per-tensor](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_224/movenet_lightning_heatmaps_224_int8_pt.tflite)       | Int8   | 224x224x3  | 50.93 %  |
| [MoveNet Lightning heatmaps per-channel](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_256/movenet_lightning_heatmaps_256_int8_pc.tflite)      | Int8   | 256x256x3  | 58.58 %  |
| [MoveNet Lightning heatmaps per-tensor](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_256/movenet_lightning_heatmaps_256_int8_pt.tflite)       | Int8   | 256x256x3  | 52.86 %  |
| [MoveNet Lightning](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_192/movenet_singlepose_lightning_192_int8.tflite)                         | Int8   | 192x192x3  | 54.12%   |
| [MoveNet Thunder](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_thunder_256/movenet_singlepose_thunder_256_int8.tflite)                               | Int8   | 256x256x3  | 64.43%   |


\* keypoints = 13

## Integration in a simple example and other services support:

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
