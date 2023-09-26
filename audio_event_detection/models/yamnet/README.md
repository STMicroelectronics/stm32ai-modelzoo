# Quantized Yamnet-256

## **Use case** : [AED](../../../audio_event_detection/README.md)

# Model description

Yamnet is a very well-known audio classification model, pre-trained on Audioset and released by Google. The default model outputs embedding vectors of size 1024.

As the default Yamnet is a bit too large to fit on most microcontrollers (over 3M parameters), we provide in this model zoo a much downsized version of Yamnet which outputs embeddings of size 256.

Additionally, the default Yamnet provided by Google expects waveforms as input and has specific custom layers to perform conversion to mel-spectrogram and patch extraction.
These custom layers are not included in Yamnet-256, as STM32Cube.AI cannot convert them to C code, and more efficient implementations of these operations already exist on microcontrollers. 
Thus, Yamnet-256 expects mel-spectrogram patches of size 64x96, format (n_mels, n_frames)

The model is quantized in int8 using tensorflow lite converter.

We provide Yamnet-256s for two different datasets : ESC-10, which is a small research dataset, and FSD50K, a large generalist dataset using the audioset ontology.
For FSD50K, the model is trained to detect a small subset of the classes included in the dataset. This subset is : Knock, Glass, Gunshots and gunfire, Crying and sobbing, Speech.

The inference time & footprints are very similar in both cases, with the FSD50K model being very slightly smaller and faster.

## Network information


| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Parameters Yamnet-256  | 130 K           |
|  Quantization           | int8            |
|  Provenance             | https://tfhub.dev/google/yamnet/1 |

## Network inputs / outputs


The network expects spectrogram patches of 96 frames and 64 mels, of shape (64, 96, 1).
Additionally, the original Yamnet converts waveforms to spectrograms by using an FFT and window size of 25 ms, a hop length of 10ms, and by clipping frequencies between 125 and 7500 Hz.

It outputs embedding vectors of size 256. If you use the train.py script to perform transfer learning, a classification head with the specified number of classes will automatically be added to the network.


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

**NOTE** : Yamnet can only be used with transfer learning or fine tuning, as it is simply a MobileNet with pretrained weights, not using the pretrained weights wouldn't make it much of a Yamnet anymore.

To train a Yamnet model with pretrained weights you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [yamnet_256_64x96_config.yaml](ST_pretrainedmodel_public_dataset/esc_10/yamnet_256_64x96/yamnet_256_64x96_config.yaml) file is used to train Yamnet-256 on the ESC10 dataset. You can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below.
## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference MCU memory footprint based on ESC-10 dataset


| Model             | Format | Resolution | Series  | Activation RAM (kB) | Runtime RAM (kB) | Weights Flash (kB) | Code Flash (kB) | Total RAM (kB)  | Total Flash (kB) | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
|[Yamnet 256](ST_pretrainedmodel_public_dataset/esc_10/yamnet_256_64x96/yamnet_256_64x96_int8.tflite) | int8 | 64x96x1 | B-U585I-IOT02A    | 109.5               |   8.3        |   135.9           |   52.6     | 117.9 | 188.5 | 7.3.0                 |

### Reference inference time based on ESC-10 dataset


| Model             | Format | Resolution | Board            | Execution Engine | Frequency    | Inference time  | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|--------------|-----------------|-----------------------|
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc_10/yamnet_256_64x96/yamnet_256_64x96_int8.tflite) | int8 | 64x96x1 | B-U585I-IOT02A | 1 CPU | 160 MHz | 321 ms | 7.3.0                 |


### Accuracy with ESC-10 dataset

A note on clip-level accuracy : In a traditional AED data processing pipeline, audio is converted to a spectral representation (in this model zoo, mel-spectrograms), which is then cut into patches. Each patch is fed to the inference network, and a label vector is output for each patch. The labels on these patches are then aggregated based on which clip the patch belongs to, to form a single aggregate label vector for each clip. Accuracy is then computed on these aggregate label vectors.

The reason this metric is used instead of patch-level accuracy is because patch-level accuracy varies immensely depending on the specific manner used to cut spectrogram into patches, and also because clip-level accuracy is the metric most often reported in research papers.

| Model | Format | Resolution | Clip-level Accuracy |
|-------|--------|------------|----------------|
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc_10/yamnet_256_64x96/yamnet_256_64x96.h5) | float32 | 64x96x1 | 94.6% |
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc_10/yamnet_256_64x96/yamnet_256_64x96_int8.tflite) | int8 | 64x96x1 | 94.6% |


### Accuracy with FSD50K dataset - Domestic AED use case
In this use case, the model is trained to detect a small subset of the classes included in the dataset. This subset is : Knock, Glass, Gunshots and gunfire, Crying and sobbing, Speech.

A note on clip-level accuracy : In a traditional AED data processing pipeline, audio is converted to a spectral representation (in this model zoo, mel-spectrograms), which is then cut into patches. Each patch is fed to the inference network, and a label vector is output for each patch. The labels on these patches are then aggregated based on which clip the patch belongs to, to form a single aggregate label vector for each clip. Accuracy is then computed on these aggregate label vectors.

The reason this metric is used instead of patch-level accuracy is because patch-level accuracy varies immensely depending on the specific manner used to cut spectrogram into patches, and also because clip-level accuracy is the metric most often reported in research papers.

**IMPORTANT NOTE** : The accuracy for the model with the "unknown class" added is significantly lower when performing inference on PC. This is because this additional class regroups a lot (appromiatively 194 in this specific case) of other classes, and thus drags performance down a bit.

However, contrary to what the numbers might suggest online performance on device is much improved in practice by this addition, in this specific case.

Note that accuracy with unknown class is lower. This is normal
| Model | Format | Resolution | Clip-level Accuracy |
|-------|--------|------------|----------------|
| [Yamnet 256 without unknown class](ST_pretrainedmodel_public_dataset\fsd50k\yamnet_256_64x96\without_unknown_class\yamnet_256_64x96.h5) | float32 | 64x96x1 | 86.0% |
| [Yamnet 256 without unknown class](ST_pretrainedmodel_public_dataset\fsd50k\yamnet_256_64x96\without_unknown_class\yamnet_256_64x96_int8.tflite) | float32 | 64x96x1 | 87.0% |
| [Yamnet 256 with unknown class](ST_pretrainedmodel_public_dataset\fsd50k\yamnet_256_64x96\with_unknown_class\yamnet_256_64x96.h5) | float32 | 64x96x1 | 73.0% |
| [Yamnet 256 with unknown class](ST_pretrainedmodel_public_dataset\fsd50k\yamnet_256_64x96\with_unknown_class\yamnet_256_64x96_int8.tflite) | int8 | 64x96x1 | 73.9% |

## Retraining and code generation


- Link to training script: [here](../../../audio_event_detection/scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here]()


## Demos
### Integration in simple example


Please refer to the generic guideline [here](../../../audio_event_detection/scripts/deployment/README.md).
Specificities: - . 