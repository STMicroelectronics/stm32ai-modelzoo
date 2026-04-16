# Quantized miniresnet

## **Use case** : `AED`

# Model description

ResNets are well known image classification models, that use skip-connections between blocks of convolutional layers to address gradient vanishing and explosion problems.

However, they are also widely used in AED and Audio classification, by converting the audio to a mel-spectrogram, and passing that as input to the model.


MiniResNet is based on the ResNet implementation found in tensorflow, and is a resized version of a ResNet18 with a custom block function. These blocks are then assembled in stacks, and the user can specify the number of stacks desired, with more stacks resulting in a larger network.

A note on pooling : In some of our pretrained models, we do not use a pooling function at the end of the convolutional backbone, as is traditionally done. Because of the small number of convolutional blocks, the number of filters is low even for larger model sizes, leading to a low embedding size after pooling.
We found that in many cases we obtain a better performance / model size / inference time tradeoff by not performing any pooling. This makes the linear classification layer larger, but in cases with a relatively low number of classes, this remains cheaper than adding more convolutional blocks.

Naturally, you are able to set the type of pooling you wish to use when training a model, whether from scratch or using transfer learning.

The MiniResNet backbones provided in the model zoo are pretrained on [FSD50K](https://zenodo.org/records/4060432)


Source implementation : https://keras.io/api/applications/resnet/

Papers : [ResNet](https://arxiv.org/abs/1512.03385)

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Params 1 stack          | 135K            |
|  Params 2 stacks         | 450K            |
|  Quantization           | int8            |
|  Provenance             | https://keras.io/api/applications/resnet/ |

## Network inputs / outputs
The pre-trained networks expects patches of shape (64, 50, 1), with 64 mels and 50 frames per patch.

When training from scratch, you can specify whichever input shape you desire.

It outputs embedding vectors of size 2048 for the 2 stacks version, and 3548 for the 1 stack version. If you use the model zoo scripts to perform transfer learning or training from scratch, a classification head with the specified number of classes will automatically be added to the network.

## Recommended platforms

| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32U5  |[x]|[x]|


# Performances

## Metrics


* Measures are done with default STEdgeAI Core configuration with enabled input / output allocated option.

* For NUCLEO-U3C5ZI-Q footprints and inference time with HSP enabled, the amount of BRAM allocated to HSP is 4096 bytes.


### Reference MCU memory footprint based on ESC-10 dataset


| Model             | Format | Resolution | Series  | Activation RAM (KiB) | Runtime RAM (KiB)| Weights Flash (KiB) | Code Flash (KiB) | Total RAM (KiB) | Total Flash (KiB)| STEdgeAI Core version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A    | 59.89 | 1.08               |   123.6       |   32.36            | 60.97 | 155.96 | 4.0.0   |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A    | 59.89 |   	1.69      |   431.1           |   	36.81    | 61.58 | 467.91 | 4.0.0     | 
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (With HSP) | 60.62 | 1.38 | 123.6 | 15.0 | 62 | 138.6 | 4.0.0 |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (With HSP) | 58.73 | 1.99 | 431.1 | 19.21 | 60.72 | 450.31 | 4.0.0 |
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (Without HSP) | 70.44 | 1.08 | 123.6 | 32.4 | 71.52 | 156.0 | 4.0.0 |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (Without HSP) | 70.44 | 1.7 | 431.1 | 36.9 | 72.14 | 468.0 | 4.0.0 |


### Reference inference time based on ESC-10 dataset


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time (ms) | STEdgeAI Core version  |
|-------------------|--------|------------|------------------|------------------|-------------|-----------------|-----------------------|
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A | 1 CPU | 160 MHz | 91.45 | 4.0.0   |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A | 1 CPU | 160 MHz | 141.82 | 4.0.0   |
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (With HSP) | 1 CPU + HSP | 96 MHz | 38.34 | 4.0.0 |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (With HSP) | 1 CPU + HSP | 96 MHz | 55.41 | 4.0.0 |
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (Without HSP) | 1 CPU | 96 MHz | 152.56 | 4.0.0 |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl_int8.tflite) | int8 | 64x50x1 | NUCLEO-U3C5ZI-Q (Without HSP) | 1 CPU | 96 MHz | 236.91 | 4.0.0 |


### Accuracy with ESC-10 dataset

A note on clip-level accuracy : In a traditional AED data processing pipeline, audio is converted to a spectral representation (in this model zoo, mel-spectrograms), which is then cut into patches. Each patch is fed to the inference network, and a label vector is output for each patch. The labels on these patches are then aggregated based on which clip the patch belongs to, to form a single aggregate label vector for each clip. Accuracy is then computed on these aggregate label vectors.

The reason this metric is used instead of patch-level accuracy is because patch-level accuracy varies immensely depending on the specific manner used to cut spectrogram into patches, and also because clip-level accuracy is the metric most often reported in research papers.

| Model | Format | Resolution | Clip-level Accuracy |
|-------|--------|------------|----------------|
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl.keras) | float32 | 64x50x1 | 90.0% |
| [MiniResNet 1 stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s1_64x50_tl/miniresnetv1_s1_64x50_tl_int8.tflite) | int8 | 64x50x1 | 90.0% |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl.keras) | float32 | 64x50x1 | 92.5% |
| [MiniResNet 2 stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv1_s2_64x50_tl/miniresnetv1_s2_64x50_tl_int8.tflite) | int8 | 64x50x1 | 92.5% |

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


