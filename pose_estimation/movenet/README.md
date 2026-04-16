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
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB)| External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|-------------------------|
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8.tflite)  | COCO-Person      | Int8     | 192x192x3  | STM32N6   |    914.88      |       0.0        |      2304.0       |     4.0.0   |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8.tflite)  | COCO-Person      | Int8     | 224x224x3  | STM32N6   |    1239.04     |       0.0        |      2304.0       |     4.0.0   |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8.tflite)  | COCO-Person      | Int8     | 256x256x3  | STM32N6   |    1607.68     |       0.0        |      2304.0       |     4.0.0   |


### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|-------------------------|
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8.tflite) | COCO-Person      | Int8     | 192x192x3  | STM32N6570-DK   |   NPU/MCU      |      22.17          |      45.1       |     4.0.0   |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8.tflite) | COCO-Person      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |      27.0          |      37.0       |     4.0.0   |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8.tflite) | COCO-Person      | Int8     | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |      34.16          |      29.2       |     4.0.0   |


### Reference **MPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)

| Model                                                                                                                                                                                                                          | Dataset                     | Format | Resolution | Quantization   | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------|--------|------------|----------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 192x192x3  | per-channel**  | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 55.81               | 2.87  | 97.13 | 0    | v6.1.0             | OpenVX                |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 224x224x3  | per-channel**  | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 79.41               | 2.41  | 97.59 | 0    | v6.1.0             | OpenVX                |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 256x256x3  | per-channel**  | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 68.42               | 3.32  | 96.68 | 0    | v6.1.0             | OpenVX                |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 192x192x3  | per-tensor     | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 8.20                | 82.06 | 17.94 | 0    | v6.1.0             | OpenVX                |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 224x224x3  | per-tensor     | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 11.63               | 83.75 | 16.25 | 0    | v6.1.0             | OpenVX                |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 256x256x3  | per-tensor     | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 13.10               | 81.39 | 18.61 | 0    | v6.1.0             | OpenVX                |
| [MoveNet Lightning](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_a100_192/movenet_singlepose_lightning_a100_192_int8.tflite)                                                          | custom_dataset_person_17kpts| Int8   | 192x192x3  | per-channel**  | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 63.80               | 6.58  | 93.42 | 0    | v6.1.0             | OpenVX                |
| [MoveNet Thunder](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_thunder_a100_256/movenet_singlepose_thunder_a100_256_int8.tflite)                                                                | custom_dataset_person_17kpts| Int8   | 256x256x3  | per-channel**  | STM32MP257F-EV1   | NPU/GPU          | 800 MHz   | 183.49              | 3.47  | 96.53 | 0    | v6.1.0             | OpenVX                |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 192x192x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 315.44              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 224x224x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 416.98              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 256x256x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 533.61              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 192x192x3  | per-tensor     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 424.77              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 224x224x3  | per-tensor     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 558.26              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 256x256x3  | per-tensor     | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 727.03              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MoveNet Lightning](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_a100_192/movenet_singlepose_lightning_a100_192_int8.tflite)                                                          | custom_dataset_person_17kpts| Int8   | 192x192x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 196.81              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MoveNet Thunder](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_thunder_a100_256/movenet_singlepose_thunder_a100_256_int8.tflite)                                                                | custom_dataset_person_17kpts| Int8   | 256x256x3  | per-channel    | STM32MP157F-DK2   | 2 CPU            | 800 MHz   | 766.38              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 192x192x3  | per-channel    | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 484.64              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 224x224x3  | per-channel    | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 651.62              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8.tflite)                                        | custom_coco_person_17kpts   | Int8   | 256x256x3  | per-channel    | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 844.89              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 192x192x3  | per-tensor     | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 578.72              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 224x224x3  | per-tensor     | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 772.76              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [ST MoveNet Lightning heatmaps per-tensor](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8_per_tensor.tflite)                  | custom_coco_person_17kpts   | Int8   | 256x256x3  | per-tensor     | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 1007.57             | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MoveNet Lightning](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_a100_192/movenet_singlepose_lightning_a100_192_int8.tflite)                                                          | custom_dataset_person_17kpts| Int8   | 192x192x3  | per-channel    | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 306.34              | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |
| [MoveNet Thunder](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_thunder_a100_256/movenet_singlepose_thunder_a100_256_int8.tflite)                                                                | custom_dataset_person_17kpts| Int8   | 256x256x3  | per-channel    | STM32MP135F-DK    | 1 CPU            | 1000 MHz  | 1131.30             | NA    | NA    | 100  | v6.1.0             | TensorFlowLite 2.18.0 |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

### OKS on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287


| Model | Format | Resolution | Training Dataset |       OKS      |
|-------|--------|------------|------------------|----------------|
| [ST MoveNet Lightning heatmaps per-channel](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8.tflite)  | Int8   | 192x192x3  | custom ST | 57.64 % |
| [ST MoveNet Lightning heatmaps per-channel](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8.tflite)  | Int8   | 224x224x3  | custom ST | 62.29 % |
| [ST MoveNet Lightning heatmaps per-channel](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8.tflite)  | Int8   | 256x256x3  | custom ST | 62.36 % |
| [ST MoveNet Lightning heatmaps per-tensor ](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8_per_tensor.tflite)  | Int8   | 192x192x3  | custom ST | 55.84 % |
| [ST MoveNet Lightning heatmaps per-tensor ](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8_per_tensor.tflite)  | Int8   | 224x224x3  | custom ST | 58.95 % |
| [ST MoveNet Lightning heatmaps per-tensor ](ST_pretrainedmodel_custom_dataset/custom_coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8_per_tensor.tflite)  | Int8   | 256x256x3  | custom ST | 60.73 % |
| [ST MoveNet Lightning heatmaps per-channel](ST_pretrainedmodel_public_dataset/coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8.tflite)  | Int8   | 192x192x3  | COCO | 55.34 % |
| [ST MoveNet Lightning heatmaps per-channel](ST_pretrainedmodel_public_dataset/coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8.tflite)  | Int8   | 224x224x3  | COCO | 59.02 % |
| [ST MoveNet Lightning heatmaps per-channel](ST_pretrainedmodel_public_dataset/coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8.tflite)  | Int8   | 256x256x3  | COCO | 61.99 % |
| [ST MoveNet Lightning heatmaps per-tensor ](ST_pretrainedmodel_public_dataset/coco_person_17kpts/st_movenet_lightning_a100_heatmaps_192/st_movenet_lightning_a100_heatmaps_192_int8_per_tensor.tflite)  | Int8   | 192x192x3  | COCO | 55.34 % |
| [ST MoveNet Lightning heatmaps per-tensor ](ST_pretrainedmodel_public_dataset/coco_person_17kpts/st_movenet_lightning_a100_heatmaps_224/st_movenet_lightning_a100_heatmaps_224_int8_per_tensor.tflite)  | Int8   | 224x224x3  | COCO | 58.50 % |
| [ST MoveNet Lightning heatmaps per-tensor ](ST_pretrainedmodel_public_dataset/coco_person_17kpts/st_movenet_lightning_a100_heatmaps_256/st_movenet_lightning_a100_heatmaps_256_int8_per_tensor.tflite)  | Int8   | 256x256x3  | COCO | 61.63 % |
| [MoveNet Lightning per-channel](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_a100_192/movenet_singlepose_lightning_a100_192_int8.tflite) | Int8   | 192x192x3  | custom Google | 54.12 % |
| [MoveNet Thunder per-channel](Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_thunder_a100_256/movenet_singlepose_thunder_a100_256_int8.tflite) | Int8   | 256x256x3  | custom Google | 64.43 % |


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
