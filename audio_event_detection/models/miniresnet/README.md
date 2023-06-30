# Quantized miniresnet

## **Use case** : [AED](../../../audio_event_detection/README.md)

# Model description

ResNets are well known image classification models, that use skip-connections between blocks of convolutional layers to address gradient vanishing and explosion problems.

However, they are also widely used in AED and Audio classification, by converting the audio to a mel-spectrogram, and passing that as input to the model.


MiniResNet is based on the ResNetv2 implementation found in tensorflow, and is a resized version of a ResNet18 with a custom block function. These blocks are then assembled in stacks, and the user can specify the number of stacks desired, with more stacks resulting in a larger network.

A note on pooling : In some of our pretrained models, we do not use a pooling function at the end of the convolutional backbone, as is traditionally done. Because of the small number of convolutional blocks, the number of filters is low even for larger model sizes, leading to a low embedding size after pooling.
We found that in many cases we obtain a better performance / model size / inference time tradeoff by not performing any pooling. This makes the linear classification layer larger, but in cases with a relatively low number of classes, this remains cheaper than adding more convolutional blocks.

Naturally, you are able to set the type of pooling you wish to use when training a model from scratch.


Source implementation : https://keras.io/api/applications/resnet/

Papers : [ResNet](https://arxiv.org/abs/1512.03385)

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Params 1stack         | 135K            |
|  Params 2stacks        | 450K            |
|  Quantization           | int8            |
|  Provenance             | https://keras.io/api/applications/resnet/ |

## Network inputs / outputs
The pre-trained networks expects patches of shape (64, 50, 1), with 64 mels and 50 frames per patch.

When training from scratch, you can specify whichever input shape you desire.

It outputs embedding vectors of size 2048 for the 2 stacks version, and 3548 for the 1 stack version. If you use the train.py script to perform transfer learning or training from scratch, a classification head with the specified number of classes will automatically be added to the network.

## Recommended platforms

| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[x]|[]|
| STM32U5  |[x]|[x]|
| STM32H7  |[x]|[]|
| STM32MP1 |[x]|[]|

# Performances

## Training 

To train a miniresnet model with pretrained weights or from scratch on your own dataset, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [miniresnet_2stacks_64x50_config.yaml](ST_pretrainedmodel_public_dataset/esc10/miniresnet_2stacks_64x50/miniresnet_2stacks_64x50_config.yaml) file is used to train the 2 stacks variant of this model on the ESC10 dataset. You can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below. 


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on ESC-10 dataset


| Model             | Format | Resolution | Series  | Activation RAM (kB) | Runtime RAM (kB) | Weights Flash (kB) | Code Flash (kB) | Total RAM (kB)  | Total Flash (kB) | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [MiniResNet 1stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_1stacks_64x50/miniresnet_1stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A    | 59.6 | 6.3               |   127.8        |   48.8            | 66.0 | 176.7 | 7.3.0                 |
| [MiniResNet 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_2stacks_64x50/miniresnet_2stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A    | 59.6 |   10.1      |   451.8           |   58.0      | 69.7 | 509.9 | 7.3.0                 | 


### Reference inference time based on ESC-10 dataset


| Model             | Format | Resolution | Board            | Execution Engine | Frequency   | Inference time  | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|-------------|-----------------|-----------------------|
| [MiniResNet 1stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_1stacks_64x50/miniresnet_1stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A | 1 CPU | 160 MHz | 179 ms | 7.3.0                 |
| [MiniResNet 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_2stacks_64x50/miniresnet_2stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A | 1 CPU | 160 MHz | 303 ms | 7.3.0                 |


### Accuracy with ESC-10 dataset

A note on clip-level accuracy : In a traditional AED data processing pipeline, audio is converted to a spectral representation (in this model zoo, mel-spectrograms), which is then cut into patches. Each patch is fed to the inference network, and a label vector is output for each patch. The labels on these patches are then aggregated based on which clip the patch belongs to, to form a single aggregate label vector for each clip. Accuracy is then computed on these aggregate label vectors.

The reason this metric is used instead of patch-level accuracy is because patch-level accuracy varies immensely depending on the specific manner used to cut spectrogram into patches, and also because clip-level accuracy is the metric most often reported in research papers.

| Model | Format | Resolution | Clip-level Accuracy |
|-------|--------|------------|----------------|
| [MiniResNet 1stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_1stacks_64x50/miniresnet_1stacks_64x50.h5) | float32 | 64x50x1 | 91.1% |
| [MiniResNet 1stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_1stacks_64x50/miniresnet_1stacks_64x50_int8.tflite) | int8 | 64x50x1 | 91.1% |
| [MiniResNet 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_2stacks_64x50/miniresnet_2stacks_64x50.h5) | float32 | 64x50x1 | 93.6% |
| [MiniResNet 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnet_2stacks_64x50/miniresnet_2stacks_64x50_int8.tflite) | int8 | 64x50x1 | 93.6% |


## Retraining and code generation


- Link to training script: [here](../../../audio_event_detection/scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here]()


## Demos
### Integration in simple example


Please refer to the generic guideline [here](../../../audio_event_detection/scripts/deployment/README.md).
Specificities: - . 