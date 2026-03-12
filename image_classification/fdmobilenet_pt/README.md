# FDMobileNet

## **Use case** : `Image classification`

# Model description


Fast-Downsampling MobileNet (FDMobileNet) is an optimized variant of MobileNet designed for **extremely fast inference**. It achieves speed improvements through aggressive early spatial reduction while maintaining reasonable accuracy.

FDMobileNet employs a **fast downsampling strategy** that reduces spatial dimensions early in the network to minimize computation. It retains **depthwise separable convolutions** inherited from MobileNet for parameter efficiency, and uses a **width multiplier (Alpha)** to scale the number of channels (a025 = 0.25x, a050 = 0.5x, a075 = 0.75x).

Among the fastest models in the model zoo, FDMobileNet is ideal for ultra-low-latency real-time applications and battery-powered devices with strict power constraints.

(source: https://arxiv.org/abs/1802.03750)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~0.37–1.77 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/qinzheng93/FD-MobileNet |
| Paper              | https://arxiv.org/abs/1802.03750 |

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
| [fdmobilenet_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a025_pt_224/fdmobilenet_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 294 | 0 | 377.03 | 3.0.0 |
| [fdmobilenet_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a050_pt_224/fdmobilenet_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 343 | 0 | 973.39 | 3.0.0 |
| [fdmobilenet_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a075_pt_224/fdmobilenet_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 441 | 0 | 1813.66 | 3.0.0 |



### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)
| Model | Dataset  | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|--------|------------|-------|-----------------|-------------------|---------------------|
| [fdmobilenet_a025_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a025_pt_224/fdmobilenet_a025_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 1.88 | 531.91 | 3.0.0  |
| [fdmobilenet_a050_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a050_pt_224/fdmobilenet_a050_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 4.07 | 245.70 | 3.0.0  |
| [fdmobilenet_a075_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a075_pt_224/fdmobilenet_a075_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 6.83 | 146.41 | 3.0.0  |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [fdmobilenet_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a025_pt_224/fdmobilenet_a025_pt_224.onnx) | Float | 224x224x3 | 45.37 % |
| [fdmobilenet_a025_pt](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a025_pt_224/fdmobilenet_a025_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 29.73 % |
| [fdmobilenet_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a050_pt_224/fdmobilenet_a050_pt_224.onnx) | Float | 224x224x3 | 58.04 % |
| [fdmobilenet_a050_pt](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a050_pt_224/fdmobilenet_a050_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 41.58 % |
| [fdmobilenet_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a075_pt_224/fdmobilenet_a075_pt_224.onnx) | Float | 224x224x3 | 62.10 % |
| [fdmobilenet_a075_pt](./Public_pretrainedmodel_public_dataset/Imagenet/fdmobilenet_a075_pt_224/fdmobilenet_a075_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 60.29 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: FD-MobileNet — https://arxiv.org/abs/1802.03750
