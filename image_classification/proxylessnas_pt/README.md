# ProxylessNAS

## **Use case** : `Image classification`

# Model description



ProxylessNAS enables **direct neural architecture search on target hardware**, eliminating the "proxy" task typically used in NAS. It learns specialized architectures optimized for specific devices without costly re-training.

The architecture employs **direct hardware targeting** by searching directly on target hardware metrics, using **path-level binarization** as an efficient search method with binary architecture parameters. **Latency regularization** incorporates actual latency into the search objective, resulting in **hardware-specific architectures** optimized for different hardware platforms.

ProxylessNAS achieves high accuracy (74.25% Top-1) with good quantization stability (0.60% drop), making it ideal for applications requiring hardware-optimized architectures with strict latency requirements.

(source: https://arxiv.org/abs/1812.00332)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~4.13 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/mit-han-lab/proxylessnas |
| Paper              | https://arxiv.org/abs/1812.00332 |

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
| [proxylessnas_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/proxylessnas_pt_224/proxylessnas_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1372 | 0 | 4233.20 | 3.0.0 |


### Reference **NPU**  inference time on food101 and imagenet dataset (see Accuracy for details on dataset)
| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [proxylessnas_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/proxylessnas_pt_224/proxylessnas_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 27.65 | 36.17 | 3.0.0  |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [proxylessnas_pt](./Public_pretrainedmodel_public_dataset/Imagenet/proxylessnas_pt_224/proxylessnas_pt_224.onnx) | Float | 224x224x3 | 74.85 % |
| [proxylessnas_pt](./Public_pretrainedmodel_public_dataset/Imagenet/proxylessnas_pt_224/proxylessnas_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 74.25 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: ProxylessNAS — https://github.com/MIT-HAN-LAB/ProxylessNAS
