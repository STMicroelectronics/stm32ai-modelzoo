# Quantized miniresnetv2

## **Use case** : [AED](../../../audio_event_detection/README.md)

# Model description

ResNets are well known image classification models, that use skip-connections between blocks of convolutional layers to address gradient vanishing and explosion problems.

However, they are also widely used in AED and Audio classification, by converting the audio to a mel-spectrogram, and passing that as input to the model.

ResNetv2 changes the order of the skip-connections and ReLU activations in the ordinary ResNet architecture, with the main benefit being faster convergence during training.

miniresnetv2v2 is based on the ResNetv2 implementation found in tensorflow, and is a resized version of a ResNet18v2 with a custom block function. These blocks are then assembled in stacks, and the user can specify the number of stacks desired, with more stacks resulting in a larger network.

A note on pooling : In some of our pretrained models, we do not use a pooling function at the end of the convolutional backbone, as is traditionally done. Because of the small number of convolutional blocks, the number of filters is low even for larger model sizes, leading to a low embedding size after pooling.
We found that in many cases we obtain a better performance / model size / inference time tradeoff by not performing any pooling. This makes the linear classification layer larger, but in cases with a relatively low number of classes, this remains cheaper than adding more convolutional blocks.

Naturally, you are able to set the type of pooling you wish to use when training a model from scratch.

Source implementation : https://keras.io/api/applications/resnet/

Papers : [ResNet](https://arxiv.org/abs/1512.03385)
         [ResNetv2](https://arxiv.org/abs/1603.05027)

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Params 1stack          | 125K            |
|  Params 2stacks         | 440K            |
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
To train a miniresnetv2 model with pretrained weights or from scratch on your own dataset, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [miniresnetv2_2stacks_64x50_config.yaml](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_2stacks_64x50/miniresnetv2_2stacks_64x50_config.yaml) file is used to train the 2 stacks variant of this model on the ESC10 dataset. You can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below. 

## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on ESC-10 dataset


| Model             | Format | Resolution | Series  | Activation RAM (kB) | Runtime RAM (kB) | Weights Flash (kB) | Code Flash (kB) | Total RAM (kB)  | Total Flash (kB) | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
| [miniresnet v2 1stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_1stacks_64x50/miniresnetv2_1stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A    | 59.6               |   7.4       |   123.9            |   53.6      | 67.1 | 177.5 | 7.3.0                 |
| [miniresnet v2 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_2stacks_64x50/miniresnetv2_2stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A    | 59.6                |   11.9        |   432.0            |   63.2      | 71.5 | 495.2 | 7.3.0                 |


### Reference inference time based on ESC-10 dataset


| Model             | Format | Resolution | Board            | Execution Engine |  Frequency   | Inference time (ms) | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|--------------|-------|-----------------------|
| [miniresnet v2 1stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_1stacks_64x50/miniresnetv2_1stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A |  1 CPU | 160 | 186 | 7.3.0                 |
| [miniresnet v2 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_2stacks_64x50/miniresnetv2_2stacks_64x50_int8.tflite) | int8 | 64x50x1 | B-U585I-IOT02A |  1 CPU | 160 | 315 | 7.3.0                 |


### Accuracy with ESC-10 dataset

A note on clip-level accuracy : In a traditional AED data processing pipeline, audio is converted to a spectral representation (in this model zoo, mel-spectrograms), which is then cut into patches. Each patch is fed to the inference network, and a label vector is output for each patch. The labels on these patches are then aggregated based on which clip the patch belongs to, to form a single aggregate label vector for each clip. Accuracy is then computed on these aggregate label vectors.

The reason this metric is used instead of patch-level accuracy is because patch-level accuracy varies immensely depending on the specific manner used to cut spectrogram into patches, and also because clip-level accuracy is the metric most often reported in research papers.

| Model | Format | Resolution | Clip-level Accuracy |
|-------|--------|------------|----------------|
| [miniresnet v2 1stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_1stacks_64x50/miniresnetv2_1stacks_64x50.h5) | float32 | 64x50x1 | 89.9% |
| [miniresnet v2 1stack ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_1stacks_64x50/miniresnetv2_1stacks_64x50_int8.tflite) | int8 | 64x50x1 | 91.1% |
| [miniresnet v2 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_2stacks_64x50/miniresnetv2_2stacks_64x50.h5) | float32 | 64x50x1 | 93.6% |
| [miniresnet v2 2stacks ](ST_pretrainedmodel_public_dataset/esc10/miniresnetv2_2stacks_64x50/miniresnetv2_2stacks_64x50_int8.tflite) | int8 | 64x50x1 | 93.6% |



## Retraining and code generation


- Link to training script: [here](../../../audio_event_detection/scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here]()


## Demos
### Integration in simple example


Please refer to the generic guideline [here](../../../audio_event_detection/scripts/deployment/README.md).
Specificities: - . 