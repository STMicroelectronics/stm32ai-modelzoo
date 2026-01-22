# HardNet

## **Use case** : `Image classification`

# Model description


Harmonic DenseNet (HardNet) is a memory-efficient variant of DenseNet that optimizes for both **computational efficiency and memory access cost**. It introduces a harmonic pattern in the dense connections to reduce redundant feature computations.

HardNet features **harmonic dense connections** that reduce connection patterns to minimize memory bandwidth, while maintaining the benefits of DenseNet's feature reuse. The architecture combines **depthwise separable convolutions** with dense blocks for enhanced efficiency.

Designed for practical hardware deployment, HardNet provides DenseNet-like feature richness with lower memory cost on edge devices.

(source: https://arxiv.org/abs/1909.00948)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~3.43 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/PingoLH/Pytorch-HarDNet |
| Paper              | https://arxiv.org/abs/1909.00948 |

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
| [hardnet39ds_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/hardnet39ds_pt_224/hardnet39ds_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1476.12 | 0 | 3516.67 | 3.0.0 |



### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)
| Model | Dataset  | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|--------|------------|-------|-----------------|-------------------|---------------------|
| [hardnet39ds_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/hardnet39ds_pt_224/hardnet39ds_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 65.81 | 15.19 | 3.0.0  |



### Accuracy with Imagenet dataset

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [hardnet39ds_pt](./Public_pretrainedmodel_public_dataset/Imagenet/hardnet39ds_pt_224/hardnet39ds_pt_224.onnx) | Float | 224x224x3 | 74.38 % |
| [hardnet39ds_pt](./Public_pretrainedmodel_public_dataset/Imagenet/hardnet39ds_pt_224/hardnet39ds_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 73.61 % |


Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [hardnet39ds_pt](./Public_pretrainedmodel_public_dataset/Imagenet/hardnet39ds_pt_224/hardnet39ds_pt_224.onnx) | Float | 224x224x3 | 74.38 % |
| [hardnet39ds_pt](./Public_pretrainedmodel_public_dataset/Imagenet/hardnet39ds_pt_224/hardnet39ds_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 73.61 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: HarDNet — https://github.com/PingoLH/Pytorch-HarDNet
