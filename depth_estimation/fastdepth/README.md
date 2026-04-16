# FastDepth

## **Use case** : `Depth Estimation`

# Model description

FastDepth is a lightweight encoder-decoder network designed for real-time monocular depth estimation, optimized for edge devices. This implementation is based on model number 146 from [PINTO's model zoo](https://github.com/PINTO0309/PINTO_model_zoo), which builds upon a MobileNetV1 based feature extractor and a fast decoder.

Although the original training dataset is not explicitly provided, it is most likely **NYU Depth V2**, a standard benchmark dataset for indoor depth estimation.

## Network information


| Network Information     | Value                                                          |
|-------------------------|----------------------------------------------------------------|
|  Framework              | TensorFlowLite                      |
|  Quantization           | int8                                |
|  Provenance             | PINTO Model Zoo #146                |
|  Paper                  | [Link to Paper](https://arxiv.org/pdf/1903.03273)|

The models are quantized using tensorflow lite converter.


## Network inputs / outputs

| Input Shape  | Description                                         |
|--------------|-----------------------------------------------------|
| (1, H, W, 3) | Single RGB image (int8)     |

| Output Shape  | Description                                     |
|---------------|-------------------------------------------------|
| (1, H, W, 1)  | Single-channel depth prediction (int8)|


## Recommended platforms


| Platform | Supported | Recommended |
|----------|--------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[]|[]|
| STM32U5  |[]|[]|
| STM32H7  |[]|[]|
| STM32MP1 |[]|[]|
| STM32MP2 |[x]|[x]|
| STM32N6  |[x]|[x]|


# Performances

## Metrics

Measures are done with default STEdgeAI Core version configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint 

| Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|------------|---------------|----------|------------|-----------|--------------|--------------|---------------|-----------------------|
| [Fast Depth](Public_pretrainedmodel_public_dataset/nyu_depthv2/fastdepth_224/fastdepth_224_int8.tflite) | NYU depth v2 | Int8 | 224x224x3 | STM32N6 | 2728.5 | 0 | 1347.97 | 4.0.0 |
| [Fast Depth](Public_pretrainedmodel_public_dataset/nyu_depthv2/fastdepth_256/fastdepth_256_int8.tflite) | NYU depth v2 | Int8 | 256x256x3 | STM32N6 | 2688 | 1024 | 1354.09 | 4.0.0 |
| [Fast Depth](Public_pretrainedmodel_public_dataset/nyu_depthv2/fastdepth_320/fastdepth_320_int8.tflite) | NYU depth v2 | Int8 | 320x320x3 | STM32N6 | 2800 | 2800 | 1376.78 | 4.0.0 |


### Reference **NPU**  inference time 


| Model      | Dataset       | Format   | Resolution | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STEdgeAI Core version |
|------------|---------------|----------|------------|------------------|------------------|---------------------|-------------|-------------------------|
| [Fast Depth](Public_pretrainedmodel_public_dataset/nyu_depthv2/fastdepth_224/fastdepth_224_int8.tflite) | NYU depth v2    | Int8   | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |      24.49      |   40.83    |     4.0.0   |
| [Fast Depth](Public_pretrainedmodel_public_dataset/nyu_depthv2/fastdepth_256/fastdepth_256_int8.tflite) | NYU depth v2    | Int8   | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |     75.01    |   13.33   |     4.0.0   |
| [Fast Depth](Public_pretrainedmodel_public_dataset/nyu_depthv2/fastdepth_320/fastdepth_320_int8.tflite) | NYU depth v2    | Int8   | 320x320x3  | STM32N6570-DK   |   NPU/MCU      |     477.93    |   2.09   |     4.0.0   |



Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)
