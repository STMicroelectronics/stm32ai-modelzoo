# SEMnasNet

## **Use case** : `Image classification`

# Model description


SEMnasNet combines the MnasNet architecture with **Squeeze-and-Excitation (SE) blocks**, adding channel attention mechanisms to the NAS-derived architecture for improved accuracy.

The architecture builds on MnasNet's **NAS-derived efficient design** and adds **Squeeze-and-Excitation blocks** for channel attention and feature recalibration. **Adaptive feature weighting** emphasizes informative channels, with SE blocks boosting accuracy with minimal overhead.

SEMnasNet achieves the **highest accuracy** in the model zoo (75.38% Top-1) with excellent quantization stability (0.37% drop), making it the best choice for accuracy-critical applications.

(source: https://arxiv.org/abs/1807.11626, https://arxiv.org/abs/1709.01507)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~4.04 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/huggingface/pytorch-image-models |
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
| [semnasnet100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/semnasnet100_pt_224/semnasnet100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2058 | 0 | 4133.38 | 3.0.0 |

### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [semnasnet100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/semnasnet100_pt_224/semnasnet100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 37.63 | 26.57 | 3.0.0  |

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [semnasnet100_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/semnasnet100_pt_224/semnasnet100_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 37.63 | 26.57 | 3.0.0  |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [semnasnet100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/semnasnet100_pt_224/semnasnet100_pt_224.onnx) | Float | 224x224x3 | 75.75 % |
| [semnasnet100_pt](./Public_pretrainedmodel_public_dataset/Imagenet/semnasnet100_pt_224/semnasnet100_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 75.38 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model (MnasNet)**: MnasNet — https://arxiv.org/abs/1807.11626

<a id="3">[3]</a> - **Model (SE-Net)**: Squeeze-and-Excitation Networks — https://arxiv.org/abs/1709.01507
