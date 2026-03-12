# ShuffleNet V2

## **Use case** : `Image classification`

# Model description


ShuffleNet V2 is designed following **practical guidelines for efficient CNN architecture design**. It uses channel shuffle operations and a split-concat structure for efficient feature reuse with minimal memory access cost.

The architecture features **channel shuffle** operations to enable information flow between channel groups, with a **split-concat architecture** for efficient feature processing. Designed based on **practical guidelines** using direct speed measurement rather than FLOPs, the architecture makes choices that **minimize memory access cost**.

ShuffleNet V2 is well-suited for mobile applications with strict efficiency requirements, real-time video processing, and multi-model deployment scenarios.

(source: https://arxiv.org/abs/1807.11164)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~1.34–2.21 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/megvii-model/ShuffleNet-Series |
| Paper              | https://arxiv.org/abs/1807.11164 |

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
| [shufflenetv2_x050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x050_pt_224/shufflenetv2_x050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 441 | 0 | 1369.07 | 3.0.0 |
| [shufflenetv2b_x050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x050_pt_224/shufflenetv2b_x050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 441 | 0 | 1369.07 | 3.0.0 |
| [shufflenetv2_x100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x100_pt_224/shufflenetv2_x100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 459.38 | 0 | 2262.45 | 3.0.0 |
| [shufflenetv2b_x100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x100_pt_224/shufflenetv2b_x100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 459.38 | 0 | 2263.57 | 3.0.0 |


### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [shufflenetv2_x050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x050_pt_224/shufflenetv2_x050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 8.35 | 119.76 | 3.0.0  |
| [shufflenetv2_x100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x100_pt_224/shufflenetv2_x100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 32.43 | 30.84 | 3.0.0  |
| [shufflenetv2b_x050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x050_pt_224/shufflenetv2b_x050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 8.39 | 119.19 | 3.0.0  |
| [shufflenetv2b_x100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x100_pt_224/shufflenetv2b_x100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 32.65 | 30.63 | 3.0.0  |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [shufflenetv2_x050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x050_pt_224/shufflenetv2_x050_pt_224.onnx) | Float | 224x224x3 | 60.63 % |
| [shufflenetv2_x050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x050_pt_224/shufflenetv2_x050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 59.69 % |
| [shufflenetv2_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x100_pt_224/shufflenetv2_x100_pt_224.onnx) | Float | 224x224x3 | 69.29 % |
| [shufflenetv2_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2_x100_pt_224/shufflenetv2_x100_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 68.65 % |
| [shufflenetv2b_x050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x050_pt_224/shufflenetv2b_x050_pt_224.onnx) | Float | 224x224x3 | 60.90 % |
| [shufflenetv2b_x050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x050_pt_224/shufflenetv2b_x050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 59.62 % |
| [shufflenetv2b_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x100_pt_224/shufflenetv2b_x100_pt_224.onnx) | Float | 224x224x3 | 70.40 % |
| [shufflenetv2b_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/shufflenetv2b_x100_pt_224/shufflenetv2b_x100_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 69.59 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: ShuffleNet V2 — https://github.com/megvii-model/ShuffleNet-Series
