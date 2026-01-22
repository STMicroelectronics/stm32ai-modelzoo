# PeleeNet

## **Use case** : `Image classification`

# Model description



PeleeNet is a lightweight convolutional neural network architecture designed for **efficient real-time inference on mobile and edge devices**. It is built upon dense connectivity principles, similar to DenseNet, but optimized to significantly reduce computational cost while maintaining strong accuracy.

Unlike MobileNet, PeleeNet does **not rely on width multipliers or depthwise separable convolutions**. Instead, it uses **two-way dense blocks**, bottleneck layers, and efficient stem blocks to reduce memory access cost and improve speed on practical hardware.

The original paper demonstrates that PeleeNet achieves competitive accuracy compared to MobileNet while requiring **fewer parameters and lower latency**, especially on real devices.

(source: https://arxiv.org/abs/1804.06882)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~2.69 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/Robert-JunWang/PeleeNet |
| Paper              | https://arxiv.org/abs/1804.06882 |

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

- Measures are done with default STM32Edge.AI configuration with enabled input / output allocated option.
- All the models are trained from scratch on Imagenet dataset 

### Reference **NPU** memory footprint on Imagenet dataset (see Accuracy for details on dataset)

| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|--------------|--------------|---------------|----------------------|
| [peleenet_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/peleenet_pt_224/peleenet_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1421 | 0 | 2751.06 | 3.0.0 |


### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)


| Model  | Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |   STEdgeAI Core version |
|--------|----------|--------|-------------|------------------|------------------|---------------------|-----------|-------------------------|
| [peleenet_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/peleenet_pt_224/peleenet_pt_224_qdq_int8.onnx) | Imagenet | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 18.01                | 55.52    |      3.0.0   |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

|model    | Format | Resolution | Top 1 Accuracy |
|---------|--------|------------|----------------|
| [peleenet_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/peleenet_pt_224/peleenet_pt_224_qdq_int8.onnx)  | Int8 | 224x224x3 | 70.37% |  
| [peleenet_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/peleenet_pt_224/peleenet_pt_224.onnx)| Float | 224x224x3 | 70.57% |  

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: PeleeNet — https://github.com/Robert-JunWang/PeleeNet