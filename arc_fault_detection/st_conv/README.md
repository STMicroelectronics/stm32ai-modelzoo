# st_conv models


## **Use case**: `Arc fault detection`

# Model description

The st_conv model is a compact per‑channel CNN for arc fault detection (normal vs arc). It processes each channel independently using Conv2D kernels of size (1, k), where k is the temporal kernel length, so there is no cross‑channel mixing. The resulting feature maps are reshaped and passed through two small dense layers (16 and 8 units) with batch normalization, ReLU, and dropout. A final dense layer with softmax activation produces per‑channel class probabilities.

Two model families are provided:
* Single‑channel: input (1 × 512 × 1), output (1 × 2)
* Multi‑channel: input (4 × 512 × 1), output (4 × 2)

The domain is selected during preprocessing, not by the network itself. Time‑domain inputs consist of raw 512‑sample windows obtained by downsampling the original dataset, which uses 1024‑sample windows. Frequency‑domain inputs are obtained by applying an FFT to a 1024‑sample window and retaining the first 512 bins, exploiting spectrum symmetry. In both cases, the resulting data are normalized. We provide both time‑ and frequency‑domain examples for each of the families mentioned above.

The 1‑channel time‑domain variant is provided as a standard [Keras model (.keras)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_1channel_512/st_conv_time_1channel_512.keras) and as an [INT8‑quantized TensorFlow Lite model (.tflite)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_1channel_512/st_conv_time_1channel_512_int8.tflite). The 1‑channel frequency‑domain variant is provided as a standard [Keras model (.keras)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_1channel_512/st_conv_freq_1channel_512.keras) and as an [INT8‑quantized TensorFlow Lite model (.tflite)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_1channel_512/st_conv_freq_1channel_512_int8.tflite). The 4‑channel time‑domain variant is provided as a standard [Keras model (.keras)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_4channels_512/st_conv_time_4channels_512.keras) and as an [INT8‑quantized TensorFlow Lite model (.tflite)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_4channels_512/st_conv_time_4channels_512_int8.tflite). The 4‑channel frequency‑domain variant is provided as a standard [Keras model (.keras)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_4channels_512/st_conv_freq_4channels_512.keras) and as an [INT8‑quantized TensorFlow Lite model (.tflite)](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_4channels_512/st_conv_freq_4channels_512_int8.tflite).


## Network information

| Network Information | Value |
|---------------------|-------|
| Framework | TensorFlow Lite |
| Params | 50,450 (for all variants)|
| Quantization | int8 |

## Network inputs / outputs

The models expect inputs of shape (1, 512, 1) or (4, 512, 1) and output per-channel class probabilities for normal vs arc.

| Input shape | Description |
|:-----------:|:------------|
| (1, 512, 1) | 1‑channel window of 512 samples for the single‑channel models. |
| (4, 512, 1) | 4‑channel window of 512 samples for the 4‑channel models. |

| Output shape | Description |
|:------------:|:------------|
| (1, 2) | Per-class scores for [normal, arc] for the 1‑channel models. |
| (4, 2) | Per-class scores for [normal, arc] for the 4‑channel models. |

## Recommended platforms

| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32U5 | [x] | [x] |
| STM32N6 | [x] | [] |


# Performances

## Metrics

* Measurements are taken with default STEdgeAI Core configuration with enabled input / output allocated option.

### Reference MCU memory footprint based on afd_test_bench dataset

| Model | Format | Resolution | Series | Activation RAM (KiB) | Runtime RAM (KiB) | Weights Flash (KiB) | Code Flash (KiB) | Total RAM (KiB) | Total Flash (KiB) | STEdgeAI Core version |
|-------|--------|------------|--------|----------------------|-------------------|---------------------|------------------|-----------------|-------------------|----------------------|
| [st_conv_time_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_1channel_512/st_conv_time_1channel_512_int8.tflite) | int8 | 1x512x1 | B-U585I-IOT02A | 9.17 | 1.3 | 49.23 | 14.85 | 10.47 | 64.08 | 4.0.0 |
| [st_conv_freq_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_1channel_512/st_conv_freq_1channel_512_int8.tflite) | int8 | 1x512x1 | B-U585I-IOT02A | 9.17 | 1.3 | 49.23 | 14.86 | 10.47 | 64.09 | 4.0.0 |
| [st_conv_time_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_4channels_512/st_conv_time_4channels_512_int8.tflite) | int8 | 4x512x1 | B-U585I-IOT02A | 24.17 | 0 | 49.23 | 16.74 | 24.17 | 65.97 | 4.0.0 |
| [st_conv_freq_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_4channels_512/st_conv_freq_4channels_512_int8.tflite) | int8 | 4x512x1 | B-U585I-IOT02A | 24.17 | 0 | 49.23 | 16.74 | 24.17 | 65.97 | 4.0.0 |


### Reference inference time based on afd_test_bench dataset

| Model | Format | Resolution | Board | Execution Engine | Frequency | Inference time (ms) | STEdgeAI Core version |
|-------|--------|------------|-------|------------------|-----------|---------------------|----------------------|
| [st_conv_time_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_1channel_512/st_conv_time_1channel_512_int8.tflite) | int8 | 1x512x1 | B-U585I-IOT02A | 1 CPU | 160 | 8.92 | 4.0.0 |
| [st_conv_freq_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_1channel_512/st_conv_freq_1channel_512_int8.tflite) | int8 | 1x512x1 | B-U585I-IOT02A | 1 CPU | 160 | 8.91 | 4.0.0 |
| [st_conv_time_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_4channels_512/st_conv_time_4channels_512_int8.tflite) | int8 | 4x512x1 | B-U585I-IOT02A | 1 CPU | 160 | 40.07 | 4.0.0 |
| [st_conv_freq_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_4channels_512/st_conv_freq_4channels_512_int8.tflite) | int8 | 4x512x1 | B-U585I-IOT02A | 1 CPU | 160 | 40.09 | 4.0.0 |


### Accuracy with afd_test_bench dataset

The afd_test_bench dataset was generated by ST on a controlled test bench for an arc vs. normal operating condition classification task. It contains 7000 waveforms, each of length 1024 samples, acquired at a sampling frequency of 125 kHz. Each line in the CSV files corresponds to a single waveform and is followed by its binary class label, where 1 = arc and 0 = normal operation. The dataset is split into 5000 samples for training, 1000 for validation, and 1000 for testing. An additional 40 samples, composed of 20 arcs followed by 20 normal samples, are available for prediction/inference purposes. All CSV files are named to reflect their specific role and are packaged into a single archive, `afd_test_bench.zip`, available in the ['stm32ai-modelzoo-services'](https://github.com/STMicroelectronics/stm32ai-modelzoo-services) under the arc_fault_detection use case.

| Model | Format | Resolution | Accuracy |
|-------|--------|------------|----------|
| [st_conv_time_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_1channel_512/st_conv_time_1channel_512.keras) | float32 | 1x512x1 | 100% |
| [st_conv_time_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_1channel_512/st_conv_time_1channel_512_int8.tflite) | int8 | 1x512x1 | 100% |
| [st_conv_freq_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_1channel_512/st_conv_freq_1channel_512.keras) | float32 | 1x512x1 | 100% |
| [st_conv_freq_1channel_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_1channel_512/st_conv_freq_1channel_512_int8.tflite) | int8 | 1x512x1 | 100% |
| [st_conv_time_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_4channels_512/st_conv_time_4channels_512.keras) | float32 | 4x512x1 | 100% |
| [st_conv_time_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_time_4channels_512/st_conv_time_4channels_512_int8.tflite) | int8 | 4x512x1 | 100% |
| [st_conv_freq_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_4channels_512/st_conv_freq_4channels_512.keras) | float32 | 4x512x1 | 100% |
| [st_conv_freq_4channels_512](ST_pretrainedmodel_custom_dataset/afd_test_bench_dataset/st_conv_freq_4channels_512/st_conv_freq_4channels_512_int8.tflite) | int8 | 4x512x1 | 100% |


## Retraining and integration in a simple example

Please refer to the stm32ai-modelzoo-services GitHub repository [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services).
