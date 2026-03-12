# PreResNet

## **Use case** : `Image classification`

# Model description


Pre-activation ResNet (PreResNet) is a variant of ResNet that places batch normalization and activation before convolutions. This simple change **improves both training dynamics and final accuracy**.

PreResNet employs a **pre-activation design** with BN-ReLU-Conv order instead of Conv-BN-ReLU, enabling cleaner **identity mappings** for improved information flow through residual connections. The improved gradient flow during training results from **full pre-activation** applied to both main path and shortcut connections.

The architecture is well-suited for deep learning research, transfer learning with pre-activation benefits, and applications where training dynamics matter.

(source: https://arxiv.org/abs/1603.05027)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~3.75 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/KaimingHe/resnet-1k-layers |
| Paper              | https://arxiv.org/abs/1603.05027 |

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
| [preresnet18_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/preresnet18_a025_pt_224/preresnet18_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1323 | 0 | 3843.64 | 3.0.0 |


### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)
| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [preresnet18_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/preresnet18_a025_pt_224/preresnet18_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 14.35 | 69.69 | 3.0.0  |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [preresnet18_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/preresnet18_a025_pt_224/preresnet18_a025_pt_224.onnx) | Float | 224x224x3 | 60.99 % |
| [preresnet18_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/preresnet18_a025_pt_224/preresnet18_a025_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 59.79 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: PreResNet — https://github.com/KaimingHe/resnet-1k-layers
