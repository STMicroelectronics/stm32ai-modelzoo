# OSNet

## **Use case** : `Re-Identification`

# Model description


OSNet is a lightweight convolutional neural network architecture designed specifically for person re-identification tasks. It introduces omni-scale feature learning, enabling the network to capture multi-scale information efficiently within a single residual block.

Key features of OSNet:
- Omni-scale feature learning for robust representation.
- Lightweight design with fewer parameters compared to traditional re-identification models.
- Suitable for deployment on resource-constrained devices.

For more details, see the OSNet paper: https://arxiv.org/abs/1905.00953

The model is quantized using ONNX quantization tools.

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  MParams alpha=0.25      | 0.197 M         |
|  Quantization           | int8            |
|  Provenance             | https://kaiyangzhou.github.io/deep-person-reid/index.html |
|  Paper                  | https://arxiv.org/abs/1905.0095 |

The models are quantized using TF Lite post-training quantization tools.


## Network inputs / outputs


For an image resolution of NxM and P classes

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, P) | Per-class confidence for P classes in FLOAT32|


## Recommended platforms


| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[x]|[]|
| STM32U5  |[x]|[]|
| STM32H7  |[x]|[x]|
| STM32MP1 |[x]|[x]|
| STM32MP2 |[x]|[x]|
| STM32N6  |[x]|[x]|

# Performances

## Metricss

- Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
- `tfs` stands for "training from scratch", meaning that the model weights were randomly initialized before training.
- `tl` stands for "transfer learning", meaning that the model backbone weights were initialized from a pre-trained model, then only the last layer was unfrozen during the training.
- `fft` stands for "full fine-tuning", meaning that the full model weights were initialized from a transfer learning pre-trained model, and all the layers were unfrozen during the training.


### Reference **NPU** memory footprint on DeepSportradar dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash |  STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|---------------|-------------------------|
| [OSNet 0.25 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a025_256_128_tfs/osnet_a025_256_128_tfs_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32N6   | 480 | 0 | 404.94      |     3.0.0   |
| [OSNet 1.0 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a100_256_128_tfs/osnet_a100_256_128_tfs_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32N6   | 1440 | 0 | 2375.33     |     3.0.0   |


### Reference **NPU**  inference time on DeepSportradar dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-----------| -----------------------|
| [OSNet 0.25 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a025_256_128_tfs/osnet_a025_256_128_tfs_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32N6570-DK       | NPU/MCU              | 3.53                 | 283.3       |    3.0.0                  |
| [OSNet 1.0 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a100_256_128_tfs/osnet_a100_256_128_tfs_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32N6570-DK       | NPU/MCU              | 13.44                | 74.4        |   3.0.0                  |


### Reference **MCU** memory footprint based on DeepSportradar dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|---------------|-------------------------|
| [OSNet 0.25 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a025_256_128_tfs/osnet_a025_256_128_tfs_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32H7   | 331.45 | 0 | 139.52      |     3.0.0   |
| [OSNet 1.0 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a100_256_128_tfs/osnet_a100_256_128_tfs_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32H7   | 396.01   | 1024.0 | 1892.75      |     3.0.0   |

### Reference **MCU** inference time on DeepSportradar dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-----------| -----------------------|
| [OSNet 0.25 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a025_256_128_tfs/osnet_a025_256_128_tfs_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32H747I-DISCO    | 1 CPU          | 495.13               | 2.02      |  3.0.0                |
| [OSNet 1.0 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a100_256_128_tfs/osnet_a100_256_128_tfs_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32H747I-DISCO    | 1 CPU          |  3894.82              | 0.26       |   3.0.0                |


### Performance with DeepSportradar ReID dataset


Dataset details: [link](https://github.com/DeepSportradar/player-reidentification-challenge) , License [Apache-2.0](https://github.com/DeepSportradar/player-reidentification-challenge?tab=Apache-2.0-1-ov-file#readme) , Number of identities: 486 (train: 436, test: 50), Number of images: 9529 (train: 8569, test_query: 50, test_gallery: 910)

| Model | Format | Resolution | mAP | rank-1 accuracy |rank-5 accuracy |rank-10 accuracy |
|-------|--------|------------|----------------|-----------------|----------------|-----------------|
| [OSNet 0.25 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a025_256_128_tfs/osnet_a025_256_128_tfs_int8.tflite) | Int8 | 256x128    | 70.27 %    | 92.0 %  | 96.0 %   | 96.0 %     |
| [OSNet 1.0 tfs](./ST_pretrainedmodel_public_dataset/DeepSportradar/osnet_a100_256_128_tfs/osnet_a100_256_128_tfs_int8.tflite) | Int8 | 256x128    | 73.84 %        | 90.0 %          | 98.0 %       | 98.0 %          |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References

<a id="1">[1]</a>
The DeepSportradar Player Re-Identification Challenge (2023) [Online]. Available: https://github.com/DeepSportradar/player-reidentification-challenge.
