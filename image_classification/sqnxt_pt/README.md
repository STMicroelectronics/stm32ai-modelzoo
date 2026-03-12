# SqueezeNext

## **Use case** : `Image classification`

# Model description



SqueezeNext is the successor to SqueezeNet, offering **improved accuracy through skip connections, bottleneck modules, and separable convolutions**. It is specifically designed for hardware efficiency.

The architecture employs a **two-stage bottleneck** with 1x1 squeeze followed by 1x1-3x3 expand patterns, with **skip connections** added for improved gradient flow. **Separable convolutions** further reduce computational cost, and the **hardware-aware design** is optimized for specific hardware platforms.

SqueezeNext is ideal for applications requiring SqueezeNet-style compactness with better accuracy, and hardware platforms with specific optimization targets.

(source: https://arxiv.org/abs/1803.10615)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~0.68–3.17 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/amirgholami/SqueezeNext |
| Paper              | https://arxiv.org/abs/1803.10615 |

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
| [sqnxt23_x100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x100_pt_224/sqnxt23_x100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2086.45 | 3025 | 693.67 | 3.0.0 |
| [sqnxt23_x150_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x150_pt_224/sqnxt23_x150_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2087.48 | 6806.25 | 1453.99 | 3.0.0 |
| [sqnxt23_x200_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x200_pt_224/sqnxt23_x200_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2275.52 | 9075 | 2493.33 | 3.0.0 |
| [sqnxt23v5_x150_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x150_pt_224/sqnxt23v5_x150_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2087.48 | 6806.25 | 1879.24 | 3.0.0 |
| [sqnxt23v5_x200_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x200_pt_224/sqnxt23v5_x200_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2275.52 | 9075 | 3249.45 | 3.0.0 |


### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [sqnxt23_x100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x100_pt_224/sqnxt23_x100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 87.07 | 11.49 | 3.0.0  |
| [sqnxt23_x150_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x150_pt_224/sqnxt23_x150_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 127.46 | 7.85 | 3.0.0  |
| [sqnxt23_x200_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x200_pt_224/sqnxt23_x200_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 182.12 | 5.49 | 3.0.0  |
| [sqnxt23v5_x100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x100_pt_224/sqnxt23v5_x100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 86.37 | 11.58 | 3.0.0  |
| [sqnxt23v5_x150_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x150_pt_224/sqnxt23v5_x150_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 126.91 | 7.88 | 3.0.0  |
| [sqnxt23v5_x200_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x200_pt_224/sqnxt23v5_x200_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 181.01 | 5.52 | 3.0.0  |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [sqnxt23_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x100_pt_224/sqnxt23_x100_pt_224.onnx) | Float | 224x224x3 | 58.18 % |
| [sqnxt23_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x100_pt_224/sqnxt23_x100_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 57.86 % |
| [sqnxt23_x150_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x150_pt_224/sqnxt23_x150_pt_224.onnx) | Float | 224x224x3 | 66.17 % |
| [sqnxt23_x150_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x150_pt_224/sqnxt23_x150_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 65.48 % |
| [sqnxt23_x200_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x200_pt_224/sqnxt23_x200_pt_224.onnx) | Float | 224x224x3 | 70.56 % |
| [sqnxt23_x200_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23_x200_pt_224/sqnxt23_x200_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 70.25 % |
| [sqnxt23v5_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x100_pt_224/sqnxt23v5_x100_pt_224.onnx) | Float | 224x224x3 | 59.85 % |
| [sqnxt23v5_x100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x100_pt_224/sqnxt23v5_x100_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 59.57 % |
| [sqnxt23v5_x150_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x150_pt_224/sqnxt23v5_x150_pt_224.onnx) | Float | 224x224x3 | 67.32 % |
| [sqnxt23v5_x150_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x150_pt_224/sqnxt23v5_x150_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 66.78 % |
| [sqnxt23v5_x200_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x200_pt_224/sqnxt23v5_x200_pt_224.onnx) | Float | 224x224x3 | 71.42 % |
| [sqnxt23v5_x200_pt](./Public_pretrainedmodel_public_dataset/Imagenet/sqnxt23v5_x200_pt_224/sqnxt23v5_x200_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 71.02 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: SqueezeNext — https://github.com/amirgholami/SqueezeNext
