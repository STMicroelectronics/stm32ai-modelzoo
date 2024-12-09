# Quantized Yamnet

## **Use case** : `AED`

# Model description

Yamnet is a very well-known audio classification model, pre-trained on Audioset and released by Google. The default model outputs embedding vectors of size 1024.

As the default Yamnet is a bit too large to fit on most microcontrollers (over 3M parameters), we provide in this model zoo a much downsized version of Yamnet which outputs embeddings of size 256.

We now also provide the original Yamnet (named Yamnet-1024 in this repo), with its original 3.2 million parameters, for use on the STM32N6.

Additionally, the default Yamnet provided by Google expects waveforms as input and has specific custom layers to perform conversion to mel-spectrogram and patch extraction.
These custom layers are not included in Yamnet-256 or Yamnet-1024, as STEDGEAI cannot convert them to C code, and more efficient implementations of these operations already exist on microcontrollers. 
Thus, Yamnet-256 and Yamnet-1024 expect mel-spectrogram patches of size 64x96, format (n_mels, n_frames)

The model is quantized in int8 using tensorflow lite converter for Yamnet-256, and ONNX quantizer for Yamnet-1024.

We provide Yamnet-256s for two different datasets : ESC-10, which is a small research dataset, and FSD50K, a large generalist dataset using the audioset ontology.
For FSD50K, the model is trained to detect a small subset of the classes included in the dataset. This subset is : Knock, Glass, Gunshots and gunfire, Crying and sobbing, Speech.

The inference time & footprints are very similar in both cases, with the FSD50K model being very slightly smaller and faster.

## Network information

Yamnet-256

| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Parameters Yamnet-256  | 130 K           |
|  Quantization           | int8            |
|  Provenance             | https://tfhub.dev/google/yamnet/1 |

Yamnet-1024

| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Parameters Yamnet-1024  | 3.2 M           |
|  Quantization           | int8            |
|  Provenance             | https://tfhub.dev/google/yamnet/1 |


## Network inputs / outputs


The network expects spectrogram patches of 96 frames and 64 mels, of shape (64, 96, 1).
Additionally, the original Yamnet converts waveforms to spectrograms by using an FFT and window size of 25 ms, a hop length of 10ms, and by clipping frequencies between 125 and 7500 Hz.

Yamnet-256 outputs embedding vectors of size 256. If you use the model zoo scripts to perform transfer learning, a classification head with the specified number of classes will automatically be added to the network.

Yamnet-1024 is the original yamnet without the TF preprocessing layers attached, and outputs embedding vectors of size 1024. If you use the model zoo scripts to perform transfer learning, a classification head with the specified number of classes will automatically be added to the network.


## Recommended platforms

For Yamnet-256
| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32U5  |[x]|[x]|
| STM32N6  |[x]|[x]|

For Yamnet-1024
| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32N6  |[x]|[x]|



# Performances

## Metrics

* Measures are done with default STEDGEAI configuration with enabled input / output allocated option.

* `tl` stands for "transfer learning", meaning that the model backbone weights were initialized from a pre-trained model, then only the last layer was unfrozen during the training.

### Reference **NPU** memory footprint based on ESC-10 dataset
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc10/yamnet_256_64x96_tl/yamnet_256_64x96_tl_int8.tflite)  | esc-10 | Int8 | 64x96x1 | STM32N6 |                                                144 | 0.0 | 176.59 | 10.0.0 | 2.0.0 |
| [Yamnet 1024](ST_pretrainedmodel_public_dataset/esc10/yamnet_1024_64x96_tl/yamnet_1024_64x96_tl_qdq_int8.onnx) | esc-10 | Int8 | 64x96x1 | STM32N6 |                                       144 | 0.0 | 3497.24 | 10.0.0 | 2.0.0 |

### Reference **NPU**  inference time  based on ESC-10 dataset
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc10/yamnet_256_64x96_tl/yamnet_256_64x96_tl_int8.tflite) | esc-10      | Int8     | 64x96x1  | STM32N6570-DK   |   NPU/MCU      |              1.07      |   934.58           |       10.0.0        |     2.0.0   |
| [Yamnet 1024](ST_pretrainedmodel_public_dataset/esc10/yamnet_1024_64x96_tl/yamnet_1024_64x96_tl_qdq_int8.onnx) | esc-10      | Int8     | 64x96x1  | STM32N6570-DK   |   NPU/MCU      |        9.88      |   101.21           |       10.0.0        |     2.0.0   |


### Reference **MCU** memory footprint based on ESC-10 dataset
| Model             | Format | Resolution | Series  | Activation RAM (kB) | Runtime RAM (kB) | Weights Flash (kB) | Code Flash (kB) | Total RAM (kB)  | Total Flash (kB) | STM32Cube.AI version  |
|-------------------|--------|------------|---------|----------------|-------------|---------------|------------|-------------|-------------|-----------------------|
|[Yamnet 256](ST_pretrainedmodel_public_dataset/esc10/yamnet_256_64x96_tl/yamnet_256_64x96_tl_int8.tflite) | Int8 | 64x96x1 | B-U585I-IOT02A    | 109.57               |   7.61        |   135.91           |   57.74   | 117.18 | 193.65 | 10.0.0 |
|[Yamnet 1024](ST_pretrainedmodel_public_dataset/esc10/yamnet_1024_64x96_tl/yamnet_1024_64x96_tl_qdq_int8.onnx) | Int8 | 64x96x1 | STM32N6 | 108.59               |   35.41        |   3162.66           |  334.30   | 144.0 | 3496.96 | 10.0.0 |

### Reference inference time based on ESC-10 dataset
| Model             | Format | Resolution | Board            | Execution Engine | Frequency    | Inference time  | STM32Cube.AI version  |
|-------------------|--------|------------|------------------|------------------|--------------|-----------------|-----------------------|
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc10/yamnet_256_64x96_tl/yamnet_256_64x96_tl_int8.tflite) | Int8 | 64x96x1 | B-U585I-IOT02A | 1 CPU | 160 MHz | 281.95 ms | 10.0.0    
|[Yamnet 1024](ST_pretrainedmodel_public_dataset/esc10/yamnet_1024_64x96_tl/yamnet_1024_64x96_tl_qdq_int8.onnx) | Int8 | 64x96x1 | STM32N6 | 1 CPU + 1 NPU | 800MhZ/1000MhZ | 11.949 ms | 10.0.0


### Accuracy with ESC-10 dataset

A note on clip-level accuracy : In a traditional AED data processing pipeline, audio is converted to a spectral representation (in this model zoo, mel-spectrograms), which is then cut into patches. Each patch is fed to the inference network, and a label vector is output for each patch. The labels on these patches are then aggregated based on which clip the patch belongs to, to form a single aggregate label vector for each clip. Accuracy is then computed on these aggregate label vectors.

The reason this metric is used instead of patch-level accuracy is because patch-level accuracy varies immensely depending on the specific manner used to cut spectrogram into patches, and also because clip-level accuracy is the metric most often reported in research papers.

| Model | Format | Resolution | Clip-level Accuracy |
|-------|--------|------------|----------------|
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc10/yamnet_256_64x96_tl/yamnet_256_64x96_tl.h5) | float32 | 64x96x1 | 94.9% |
| [Yamnet 256](ST_pretrainedmodel_public_dataset/esc10/yamnet_256_64x96_tl/yamnet_256_64x96_tl_int8.tflite) | int8 | 64x96x1 | 94.9% |
| [Yamnet 1024](ST_pretrainedmodel_public_dataset/esc10/yamnet_1024_64x96_tl/yamnet_1024_64x96_tl.h5) | float32 | 64x96x1 | 100.0% |
| [Yamnet 1024](ST_pretrainedmodel_public_dataset/esc10/yamnet_1024_64x96_tl/yamnet_1024_64x96_tl_qdq_int8.onnx) | int8 | 64x96x1 | 100.0% |



### Accuracy with FSD50K dataset - Domestic AED use case
In this use case, the model is trained to detect a small subset of the classes included in the dataset. This subset is : Knock, Glass, Gunshots and gunfire, Crying and sobbing, Speech.

A note on clip-level accuracy : In a traditional AED data processing pipeline, audio is converted to a spectral representation (in this model zoo, mel-spectrograms), which is then cut into patches. Each patch is fed to the inference network, and a label vector is output for each patch. The labels on these patches are then aggregated based on which clip the patch belongs to, to form a single aggregate label vector for each clip. Accuracy is then computed on these aggregate label vectors.

The reason this metric is used instead of patch-level accuracy is because patch-level accuracy varies immensely depending on the specific manner used to cut spectrogram into patches, and also because clip-level accuracy is the metric most often reported in research papers.

**IMPORTANT NOTE** : The accuracy for the model with the "unknown class" added is significantly lower when performing inference on PC. This is because this additional class regroups a lot (appromiatively 194 in this specific case) of other classes, and thus drags performance down a bit.

However, contrary to what the numbers might suggest online performance on device is much improved in practice by this addition, in this specific case.

Note that accuracy with unknown class is lower. This is normal
| Model | Format | Resolution | Clip-level Accuracy |
|-------|--------|------------|----------------|
| [Yamnet 256 without unknown class](ST_pretrainedmodel_public_dataset/fsd50k/yamnet_256_64x96_tl/without_unknown_class/yamnet_256_64x96_tl.h5) | float32 | 64x96x1 | 86.0% |
| [Yamnet 256 without unknown class](ST_pretrainedmodel_public_dataset/fsd50k/yamnet_256_64x96_tl/without_unknown_class/yamnet_256_64x96_tl_int8.tflite) | float32 | 64x96x1 | 87.0% |
| [Yamnet 256 with unknown class](ST_pretrainedmodel_public_dataset/fsd50k/yamnet_256_64x96_tl/with_unknown_class/yamnet_256_64x96_tl.h5) | float32 | 64x96x1 | 73.0% |
| [Yamnet 256 with unknown class](ST_pretrainedmodel_public_dataset/fsd50k/yamnet_256_64x96_tl/with_unknown_class/yamnet_256_64x96_tl_int8.tflite) | int8 | 64x96x1 | 73.9% |

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


