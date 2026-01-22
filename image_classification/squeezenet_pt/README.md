# SqueezeNet

## **Use case** : `Image classification`

# Model description


SqueezeNet is a pioneering compact architecture that achieves **AlexNet-level accuracy with 50x fewer parameters**. It introduced the "Fire module" combining squeeze and expand operations.

The architecture features **Fire Modules** with squeeze (1x1) followed by expand (1x1 + 3x3) layers, employing **delayed downsampling** to maintain larger activation maps longer. It uses **no fully connected layers**, relying on global average pooling, resulting in an **extremely compact** model (<0.5MB original size).

SqueezeNet is ideal for extremely constrained deployment scenarios, model compression research, and applications where model size is critical.

(source: https://arxiv.org/abs/1602.07360)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~1.24 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/DeepScale/SqueezeNet |
| Paper              | https://arxiv.org/abs/1602.07360 |

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
| [squeezenetv10_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/squeezenetv10_pt_224/squeezenetv10_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2278.12 | 6683.06 | 1266.61 | 3.0.0 |


### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [squeezenetv10_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/squeezenetv10_pt_224/squeezenetv10_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 121.20 | 8.25 | 3.0.0  |


### Accuracy with Imagenet dataset

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [squeezenetv10_pt](./Public_pretrainedmodel_public_dataset/Imagenet/squeezenetv10_pt_224/squeezenetv10_pt_224.onnx) | Float | 224x224x3 | 62.11 % |
| [squeezenetv10_pt](./Public_pretrainedmodel_public_dataset/Imagenet/squeezenetv10_pt_224/squeezenetv10_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 58.43 % |


| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [squeezenetv10_pt](./Public_pretrainedmodel_public_dataset/Imagenet/squeezenetv10_pt_224/squeezenetv10_pt_224.onnx) | Float | 224x224x3 | 62.11 % |
| [squeezenetv10_pt](./Public_pretrainedmodel_public_dataset/Imagenet/squeezenetv10_pt_224/squeezenetv10_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 58.43 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: SqueezeNet — https://github.com/DeepScale/SqueezeNet
