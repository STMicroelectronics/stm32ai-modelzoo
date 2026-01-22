# MobileNet v2

## **Use case** : `Re-Identification`

# Model description


MobileNet v2 is very similar to the original MobileNet, except that it uses inverted residual blocks with bottlenecking features.

It has a drastically lower parameter count than the original MobileNet.

MobileNet models support any input size greater than 32 x 32, with larger image sizes offering better performance.
Alpha parameter: float, larger than zero, controls the width of the network. This is known as the width multiplier in the MobileNetV2 paper, but the name is kept for consistency with applications.

If alpha < 1.0, proportionally decreases the number of filters in each layer.

If alpha > 1.0, proportionally increases the number of filters in each layer.

If alpha = 1.0, default number of filters from the paper are used at each layer.

(source: https://keras.io/api/applications/mobilenet/)

The model is quantized in int8 using tensorflow lite converter.

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  MParams alpha=0.35      | 1.66 M          |
|  Quantization           | int8            |
|  Provenance             | https://www.tensorflow.org/api_docs/python/tf/keras/applications/mobilenet_v2 |
|  Paper                  | https://arxiv.org/pdf/1801.04381.pdf |

The models are quantized using tensorflow lite converter.


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
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a035_256_128_fft/mobilenetv2_a035_256_128_fft_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32N6   | 480 | 0.0 | 553.58      |     3.0.0   |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a100_256_128_fft/mobilenetv2_a100_256_128_fft_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32N6   | 1440  | 0.0 | 2786.52     |     3.0.0   |


### Reference **NPU**  inference time on DeepSportradar dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-----------| -----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a035_256_128_fft/mobilenetv2_a035_256_128_fft_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32N6570-DK       | NPU/MCU              | 4.15                 | 241       | 3.0.0                  |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a100_256_128_fft/mobilenetv2_a100_256_128_fft_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32N6570-DK       | NPU/MCU              | 13.37                | 74.8        | 3.0.0                  |


### Reference **MCU** memory footprint based on DeepSportradar dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash |  STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|---------------|-------------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a035_256_128_fft/mobilenetv2_a035_256_128_fft_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32H7   | 461.32 | 0.0 | 400.59      |     3.0.0   |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a100_256_128_fft/mobilenetv2_a100_256_128_fft_int8.tflite) | DeepSportradar      | Int8     | 256x128x3  | STM32H7   | 398.25   | 804.38 | 2205.06      |     3.0.0   |

### Reference **MCU** inference time on DeepSportradar dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-----------| -----------------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a035_256_128_fft/mobilenetv2_a035_256_128_fft_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32H747I-DISCO    | 1 CPU          | 190.3               | 5.3      |   3.0.0                |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a100_256_128_fft/mobilenetv2_a100_256_128_fft_int8.tflite) | DeepSportradar      | Int8   | 256x128x3  | STM32H747I-DISCO    | 1 CPU          |  729.45              | 1.37       |  3.0.0                |



### Performance with DeepSportradar ReID dataset


Dataset details: [link](https://github.com/DeepSportradar/player-reidentification-challenge) , License [Apache-2.0](https://github.com/DeepSportradar/player-reidentification-challenge?tab=Apache-2.0-1-ov-file#readme) , Number of identities: 486 (train: 436, test: 50), Number of images: 9529 (train: 8569, test_query: 50, test_gallery: 910)

| Model | Format | Resolution | mAP | rank-1 accuracy |rank-5 accuracy |rank-10 accuracy |
|-------|--------|------------|----------------|-----------------|----------------|-----------------|
| [MobileNet v2 0.35 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a035_256_128_fft/mobilenetv2_a035_256_128_fft_int8.tflite) | Int8 | 256x128    | 73.43 %         | 96.0 %          | 96.0 %       | 98.0 %          |
| [MobileNet v2 1.0 fft](./ST_pretrainedmodel_public_dataset/DeepSportradar/mobilenetv2_a100_256_128_fft/mobilenetv2_a100_256_128_fft_int8.tflite) | Int8 | 256x128    | 72.5 %         | 94.0 %          | 98.0 %       | 98.0 %          |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References

<a id="1">[1]</a>
The DeepSportradar Player Re-Identification Challenge (2023) [Online]. Available: https://github.com/DeepSportradar/player-reidentification-challenge.
