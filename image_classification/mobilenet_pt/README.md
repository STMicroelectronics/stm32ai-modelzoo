# MobileNet V1

## **Use case** : `Image classification`

# Model description


The original MobileNet architecture pioneered the use of **depthwise separable convolutions** for efficient mobile vision. It dramatically reduces computation and model size while maintaining competitive accuracy.

MobileNet factorizes standard convolutions into **depthwise and pointwise operations**, dramatically reducing computational cost. The architecture supports a **width multiplier (Alpha)** to scale channel dimensions (a025 = 0.25x, a050 = 0.5x, a075 = 0.75x), and uses **linear bottleneck** for efficient channel expansion and compression.

Resolution multipliers can further scale input resolution for additional efficiency, making MobileNet ideal for real-time mobile applications and resource-constrained embedded systems.

(source: https://arxiv.org/abs/1704.04861)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~0.46–2.55 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/tensorflow/models/tree/master/research/slim/nets/mobilenet |
| Paper              | https://arxiv.org/abs/1704.04861 |

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
| [mobilenet_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a025_pt_224/mobilenet_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 392 | 0 | 469.45 | 4.0.0 |
| [mobilenet_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a050_pt_224/mobilenet_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 588 | 0 | 1318.3 | 4.0.0 |
| [mobilenet_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a075_pt_224/mobilenet_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1323 | 0 | 2612.79 | 4.0.0 |
| [mobilenetb_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a025_pt_224/mobilenetb_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 392 | 0 | 469.3 | 4.0.0 |
| [mobilenetb_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a050_pt_224/mobilenetb_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 588 | 0 | 1317.91 | 4.0.0 |
| [mobilenetb_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a075_pt_224/mobilenetb_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1323 | 0 | 2602.29 | 4.0.0 |


### Reference **NPU**  inference time and imagenet dataset (see Accuracy for details on dataset)

| Model  | Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|--------|---------|--------|--------|-------------|-----------------|-----------------|-------------------|----------------------|
| [mobilenet_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a025_pt_224/mobilenet_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224x224x3 | STM32N6570-DK | NPU/MCU | 2.98 | 335.57 | 4.0.0  |
| [mobilenet_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a050_pt_224/mobilenet_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224x224x3 | STM32N6570-DK | NPU/MCU | 6.55 | 152.67 | 4.0.0  |
| [mobilenet_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a075_pt_224/mobilenet_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224x224x3 | STM32N6570-DK | NPU/MCU | 11.73 | 85.25 | 4.0.0  |
| [mobilenetb_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a025_pt_224/mobilenetb_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224x224x3 | STM32N6570-DK | NPU/MCU | 2.89 | 345.90 | 4.0.0  |
| [mobilenetb_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a050_pt_224/mobilenetb_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224x224x3 | STM32N6570-DK | NPU/MCU | 6.65 | 150.38 | 4.0.0  |
| [mobilenetb_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a075_pt_224/mobilenetb_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224x224x3 | STM32N6570-DK | NPU/MCU | 11.70 | 85.47 | 4.0.0  |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [mobilenet_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a025_pt_224/mobilenet_a025_pt_224.onnx) | Float | 224x224x3 | 54.81 % |
| [mobilenet_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a025_pt_224/mobilenet_a025_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 50.55 % |
| [mobilenet_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a050_pt_224/mobilenet_a050_pt_224.onnx) | Float | 224x224x3 | 66.60 % |
| [mobilenet_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a050_pt_224/mobilenet_a050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 64.37 % |
| [mobilenet_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a075_pt_224/mobilenet_a075_pt_224.onnx) | Float | 224x224x3 | 71.01 % |
| [mobilenet_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenet_a075_pt_224/mobilenet_a075_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 69.91 % |
| [mobilenetb_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a025_pt_224/mobilenetb_a025_pt_224.onnx) | Float | 224x224x3 | 55.53 % |
| [mobilenetb_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a025_pt_224/mobilenetb_a025_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 53.81 % |
| [mobilenetb_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a050_pt_224/mobilenetb_a050_pt_224.onnx) | Float | 224x224x3 | 67.44 % |
| [mobilenetb_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a050_pt_224/mobilenetb_a050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 65.96 % |
| [mobilenetb_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a075_pt_224/mobilenetb_a075_pt_224.onnx) | Float | 224x224x3 | 71.46 % |
| [mobilenetb_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetb_a075_pt_224/mobilenetb_a075_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 69.72 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: MobileNets — https://github.com/tensorflow/models/blob/master/research/slim/nets/mobilenet_v1.md
