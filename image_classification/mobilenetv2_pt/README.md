# MobileNet V2

## **Use case** : `Image classification`

# Model description


MobileNetV2 improves upon V1 with **inverted residual blocks and linear bottlenecks**. It features skip connections between thin bottleneck layers, improving gradient flow and enabling deeper, more accurate networks.

The architecture uses **inverted residuals** that expand channels before depthwise convolution and then compress, with **linear bottlenecks** that remove non-linearity in narrow layers to preserve information. **Skip connections** between bottleneck layers improve gradient flow, typically with a 6x expansion ratio.

MobileNetV2 offers the best overall accuracy-efficiency trade-off with excellent quantization stability (typically <1% accuracy drop), making it ideal for production mobile applications, object detection backbones, and semantic segmentation networks.

(source: https://arxiv.org/abs/1801.04381)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~1.49–3.72 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/tensorflow/models/tree/master/research/slim/nets/mobilenet |
| Paper              | https://arxiv.org/abs/1801.04381 |

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
| STM32L4  |[]|[]|
| STM32U5  |[]|[]|
| STM32H7  |[]|[]|
| STM32MP1 |[]|[]|
| STM32MP2 |[]|[]|
| STM32N6  |[x]|[x]|

# Performances

## Metrics

- Measures are done with default STEdgeAI Core configuration with enabled input / output allocated option.
- All the models are trained from scratch on Imagenet dataset 

### Reference **NPU** memory footprint on Imagenet dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|--------------|--------------|---------------|----------------------|
| [mobilenetv2_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a025_pt_224/mobilenetv2_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 392 | 0 | 1522.31 | 4.0.0 |
| [mobilenetv2b_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a025_pt_224/mobilenetv2b_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 392 | 0 | 1522.25 | 4.0.0 |
| [mobilenetv2_w035_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_w035_pt_224/mobilenetv2_w035_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 931 | 0 | 1685.00 | 4.0.0 |
| [mobilenetv2_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a050_pt_224/mobilenetv2_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1274 | 0 | 1972.03 | 4.0.0 |
| [mobilenetv2b_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a050_pt_224/mobilenetv2b_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1065.75 | 0 | 1965.86 | 4.0.0 |
| [mobilenetv2_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a075_pt_224/mobilenetv2_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1653.75 | 0 | 2737.58 | 4.0.0 |
| [mobilenetv2b_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a075_pt_224/mobilenetv2b_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1653.75 | 0 | 2737.02 | 4.0.0 |
| [mobilenetv2_a100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a100_pt_224/mobilenetv2_a100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2058 | 0 | 3813.97 | 4.0.0 |
| [mobilenetv2b_a100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a100_pt_224/mobilenetv2b_a100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2058 | 0 | 3812.52 | 4.0.0 |


### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [mobilenetv2_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a025_pt_224/mobilenetv2_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 6.50 | 153.85 | 4.0.0  |
| [mobilenetv2_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a050_pt_224/mobilenetv2_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 10.08 | 99.21 | 4.0.0  |
| [mobilenetv2_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a075_pt_224/mobilenetv2_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 15.17 | 65.88 | 4.0.0  |
| [mobilenetv2_a100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a100_pt_224/mobilenetv2_a100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 20.35 | 49.14 | 4.0.0  |
| [mobilenetv2_w035_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_w035_pt_224/mobilenetv2_w035_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 8.58 | 116.55 | 4.0.0  |
| [mobilenetv2b_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a025_pt_224/mobilenetv2b_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 6.29 | 158.98 | 4.0.0  |
| [mobilenetv2b_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a050_pt_224/mobilenetv2b_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 9.79 | 102.14 | 4.0.0  |
| [mobilenetv2b_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a075_pt_224/mobilenetv2b_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 14.56 | 68.68 | 4.0.0  |
| [mobilenetv2b_a100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a100_pt_224/mobilenetv2b_a100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 20.39 | 49.04 | 4.0.0  |




### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [mobilenetv2_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a025_pt_224/mobilenetv2_a025_pt_224.onnx) | Float | 224x224x3 | 52.29 % |
| [mobilenetv2_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a025_pt_224/mobilenetv2_a025_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 51.51 % |
| [mobilenetv2_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a050_pt_224/mobilenetv2_a050_pt_224.onnx) | Float | 224x224x3 | 66.20 % |
| [mobilenetv2_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a050_pt_224/mobilenetv2_a050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 65.31 % |
| [mobilenetv2_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a075_pt_224/mobilenetv2_a075_pt_224.onnx) | Float | 224x224x3 | 70.78 % |
| [mobilenetv2_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a075_pt_224/mobilenetv2_a075_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 70.33 % |
| [mobilenetv2_a100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a100_pt_224/mobilenetv2_a100_pt_224.onnx) | Float | 224x224x3 | 73.17 % |
| [mobilenetv2_a100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_a100_pt_224/mobilenetv2_a100_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 72.76 % |
| [mobilenetv2_w035_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_w035_pt_224/mobilenetv2_w035_pt_224.onnx) | Float | 224x224x3 | 61.02 % |
| [mobilenetv2_w035_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2_w035_pt_224/mobilenetv2_w035_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 60.09 % |
| [mobilenetv2b_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a025_pt_224/mobilenetv2b_a025_pt_224.onnx) | Float | 224x224x3 | 53.53 % |
| [mobilenetv2b_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a025_pt_224/mobilenetv2b_a025_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 52.55 % |
| [mobilenetv2b_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a050_pt_224/mobilenetv2b_a050_pt_224.onnx) | Float | 224x224x3 | 66.30 % |
| [mobilenetv2b_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a050_pt_224/mobilenetv2b_a050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 65.67 % |
| [mobilenetv2b_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a075_pt_224/mobilenetv2b_a075_pt_224.onnx) | Float | 224x224x3 | 70.41 % |
| [mobilenetv2b_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a075_pt_224/mobilenetv2b_a075_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 70.20 % |
| [mobilenetv2b_a100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a100_pt_224/mobilenetv2b_a100_pt_224.onnx) | Float | 224x224x3 | 73.33 % |
| [mobilenetv2b_a100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv2b_a100_pt_224/mobilenetv2b_a100_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 72.89 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: MobileNetV2 — https://github.com/tensorflow/models/tree/master/research/slim/nets/mobilenet
