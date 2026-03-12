# RegNet

## **Use case** : `Image classification`

# Model description


RegNet introduces a **design space paradigm** for neural networks. Rather than designing individual architectures, RegNet defines a design space of possible networks characterized by a few parameters, enabling systematic exploration of network designs.

The architecture uses **quantized linear parameterization** where networks are defined by simple equations, with systematic variation of **width and depth patterns**. RegNet employs **group convolutions** for efficiency, following a **design space exploration** methodology for finding optimal configurations.

RegNet is well-suited for research on neural network design principles, applications requiring systematic architecture selection, and scalable deployments with consistent design principles.

(source: https://arxiv.org/abs/2003.13678)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~2.55 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/facebookresearch/pycls |
| Paper              | https://arxiv.org/abs/2003.13678 |

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
|------|---------|--------|------------|--------|--------------|--------------|---------------|----------------------|
| [regnetx002_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/regnetx002_pt_224/regnetx002_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1192.84 | 0 | 2606.72 | 3.0.0 |

### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)
| Model  | Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |   STEdgeAI Core version |
|--------|----------|--------|-------------|------------------|------------------|---------------------|-----------|-------------------------|
| [regnetx002_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/regnetx002_pt_224/regnetx002_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 9.96 | 100.40 | 3.0.0  |

### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [regnetx002_pt](./Public_pretrainedmodel_public_dataset/Imagenet/regnetx002_pt_224/regnetx002_pt_224.onnx) | Float | 224x224x3 | 70.72 % |
| [regnetx002_pt](./Public_pretrainedmodel_public_dataset/Imagenet/regnetx002_pt_224/regnetx002_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 68.95 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: RegNet — https://github.com/facebookresearch/pycls
