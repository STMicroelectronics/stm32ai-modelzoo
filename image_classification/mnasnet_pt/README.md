# MnasNet

## **Use case** : `Image classification`

# Model description


Mobile Neural Architecture Search Network (MnasNet) is designed using **automated neural architecture search (NAS)** specifically targeting mobile devices. It optimizes for both accuracy and real-device latency simultaneously.

MnasNet employs **multi-objective optimization** to balance accuracy with latency on target devices, using **inverted residual blocks** similar to MobileNetV2 but with NAS-optimized configurations. The **factorized hierarchical search space** enables diverse and efficient architectures.

The architecture is well-suited for mobile and embedded vision applications, particularly in scenarios requiring optimized accuracy-latency trade-offs.

(source: https://arxiv.org/abs/1807.11626)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~2.27 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet |
| Paper              | https://arxiv.org/abs/1807.11626 |

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
| [mnasnet_d050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mnasnet_d050_pt_224/mnasnet_d050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 612.5 | 0 | 2319.53 | 4.0.0 |

### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)
| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [mnasnet_d050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mnasnet_d050_pt_224/mnasnet_d050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 11.21 | 89.21 | 4.0.0  |




### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [mnasnet_d050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mnasnet_d050_pt_224/mnasnet_d050_pt_224.onnx) | Float | 224x224x3 | 67.50 % |
| [mnasnet_d050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mnasnet_d050_pt_224/mnasnet_d050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 59.99 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: MnasNet — https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet
