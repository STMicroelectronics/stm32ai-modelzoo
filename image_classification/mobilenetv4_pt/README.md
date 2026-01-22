# MobileNet V4

## **Use case** : `Image classification`

# Model description


MobileNetV4 represents the latest evolution in the MobileNet family, introducing **Universal Inverted Bottleneck (UIB) blocks** that unify various efficient convolution designs. It achieves state-of-the-art accuracy-efficiency trade-offs on mobile hardware.

The architecture features a **flexible UIB block design** accommodating various operations, optimized through **Neural Architecture Search** for multiple hardware platforms. It includes **Mobile MQA Attention** as an efficient attention mechanism for mobile deployment, providing enhanced feature extraction with improved capacity per FLOP.

MobileNetV4 is ideal for state-of-the-art mobile vision applications requiring the latest architectural improvements, though it shows quantization sensitivity (~10% drop) that should be considered for INT8 deployment.

(source: https://arxiv.org/abs/2404.10518)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~3.67 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/huggingface/pytorch-image-models |
| Paper              | https://arxiv.org/abs/2404.10518 |

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
- All the models are trained from scratch on imagenet dataset 

### Reference **NPU** memory footprint on Imagenet dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|--------------|--------------|---------------|----------------------|
| [mobilenetv4small_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv4small_pt_224/mobilenetv4small_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 539 | 0 | 3760.53 | 3.0.0 |



### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [mobilenetv4small_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv4small_pt_224/mobilenetv4small_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 13.74 | 72.78 | 3.0.0  |




### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [mobilenetv4small_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv4small_pt_224/mobilenetv4small_pt_224.onnx) | Float | 224x224x3 | 74.33 % |
| [mobilenetv4small_pt](./Public_pretrainedmodel_public_dataset/Imagenet/mobilenetv4small_pt_224/mobilenetv4small_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 64.24 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: MobileNetV4 — https://arxiv.org/abs/2404.10518
