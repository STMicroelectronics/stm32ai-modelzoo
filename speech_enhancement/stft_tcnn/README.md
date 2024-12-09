# STFT-TCNN

## **Use case** : `speech enhancement`

# Model description

The TCNN is a time-domain speech enhancement temporal convolutional model proposed in 2019 by Pandey and Wang in the paper [TCNN: TEMPORAL CONVOLUTIONAL NEURAL NETWORK FOR REAL-TIME SPEECH ENHANCEMENT IN THE TIME DOMAIN](https://ieeexplore.ieee.org/document/8683634).


Unfortunately, time-domain models do not perform well when quantized to 8-bit integer precision.
Therefore, we made several modifications to the model, in order to make it work in the frequency domain.
Mainly, we removed the convolutional encoder and decoder described in the paper, keeping only the main TCN part of the model, and instead substituted the encoder/decoder pair with STFT pre-processing, and inverse STFT post-processing.


This means that the model takes as input magnitude spectrogram frames, and outputs a mask of the same dimension.
Inference is then performed by applying this output mask to the complex spectrogram corresponding to the input, and performing inverse STFT on the masked complex spectrogram to retrieve the corresponding time domain denoised signal.

## Network information

STFT-TCNN

| Network Information     |  Value          |
|-------------------------|-----------------|
|  Framework              | ONNX QDQ |
|  Parameters | 1.594 M          |
|  Quantization           | int8            |

## Network inputs / outputs


The model expects input of shape (batch, n_fft // 2 + 1, sequence_length), where batch and sequence_length are axes with dynamic length. 
The models provided here were pretrained with n_fft = 512, and so the input shape becomes (batch, 257, sequence_length)

We provide float and int8 quantized ONNX versions of the model, as well as a Pytorch state dict.

We also provide the original .yaml config file used to train the model. For details on which exact parameters were used to train it, please refer to the attached config file.

**IMPORTANT :** Since STEdgeAI does not allow deployment of models with a dynamic input shape on ST boards, we also provide a version of the model with static input shape, usually (1, 257, 40). If using the default configuration that includes 5 lookahead and lookback frames, this means the model will perform once inference every 30 frames.

**For evaluation, use the model with dynamic input shape, and for deployment, use the model with static input shape !**

## Recommended platforms

| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32N6  |[x]|[x]|



# Performances

## Metrics
Measures are done with default STEDGEAI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM | External RAM | Weights Flash | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [STFT-TCNN Medium](ST_pretrainedmodel_public_dataset/valentini/stft_tcnn_medium_sigmoid_257x40_qdq_int8.onnx)  | valentini     | Int8     | 257x40  | STM32N6   |     100.09    |   0.0              |    1626.86         |       10.0.0        |     2.0.0   |

### Reference **NPU**  inference time

**IMPORTANT NOTE :** In the current version of ST Edge AI, some convolutional layers of this model are still mapped to software which slows down the inference time, though we still end up with plenty of room to spare to run the model in real time. This issue will be fixed in the next STEdgeAI release.

The figures listed in this table correspond to the version of ST Edge AI with this issue (i.e. the slowed down version), so you will not experience unexpected inference times.

You can expect significant improvements once this issue is resolved.


| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [STFT-TCNN medium](ST_pretrainedmodel_public_dataset/valentini/stft_tcnn_medium_sigmoid_257x40_qdq_int8.onnx) | valentini     | Int8     | 257x40  | STM32N6570-DK   |   NPU/MCU      |       53.76         |    18.6      |       10.0.0        |     2.0.0   |


### Metrics on the Valentini dataset

We report five metrics : 
- [PESQ (Perceptual Evaluation of Speech Quality)](https://en.wikipedia.org/wiki/Perceptual_Evaluation_of_Speech_Quality)
- [STOI (Short-Time Objective Intelligibility)](https://ieeexplore.ieee.org/document/5495701)
- MSE between the clean and denoised waveforms
- [SNR (Signal-to-Noise Ratio)](https://en.wikipedia.org/wiki/Signal-to-noise_ratio) between the clean and denoised waveforms
- Scale-invariant SNR


| Model | Format | Resolution | PESQ | STOI | SNR | SI-SNR | Waveform MSE |
|-------|--------|------------|------|------|-----|--------|--------------|
| [STFT-TCNN Medium](ST_pretrainedmodel_public_dataset/valentini/stft_tcnn_medium_sigmoid_257xsl_float.onnx) | float32 | 257x? | 2.480 | 0.931 | 18.190 | 18.104 | 1.136e-4 |
| [STFT-TCNN Medium](ST_pretrainedmodel_public_dataset/valentini/stft_tcnn_medium_sigmoid_257xsl_qdq_int8.onnx) | int8 | 257x? | 2.372 | 0.932 | 18.190 | 18.100 | 1.109e-4 |

### Limitations

The models provided here typically have trouble denoising speech at SNRs beyond what they were trained on. In the Valentini dataset, the lowest SNR in the training set is 0 dB. Therefore, the model tends to struggle to denoise speech at negative SNRs.

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


