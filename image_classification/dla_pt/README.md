# DLA (Deep Layer Aggregation)

## **Use case** : `Image classification`

# Model description


Deep Layer Aggregation (DLA) networks introduce iterative and hierarchical structures for aggregating features across layers. DLA extends standard architectures by merging features from different depths and resolutions, enabling **richer semantic and spatial information flow**.

DLA employs **Hierarchical Deep Aggregation (HDA)** to merge feature hierarchies combining features from different depths, and **Iterative Deep Aggregation (IDA)** to progressively refine resolution and semantic information. The dense connections enable gradient flow and feature reuse across the network.

DLA is particularly well-suited for applications requiring multi-scale feature representation, such as semantic segmentation and object detection.

(source: https://arxiv.org/abs/1707.06484)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~1.04–1.25 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/ucbdrive/dla |
| Paper              | https://arxiv.org/abs/1707.06484 |

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
| [dla46xc_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/dla46xc_pt_224/dla46xc_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2361 | 6272 | 1036.41 | 3.0.0 |
| [dla46c_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/dla46c_pt_224/dla46c_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2361 | 6272 | 1266.66 | 3.0.0 |
| [dla60xc_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/dla60xc_pt_224/dla60xc_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2361 | 6272 | 1278.52 | 3.0.0 |



### Reference **NPU**  inference time on Imagenet dataset (see Accuracy for details on dataset)
| Model | Dataset  | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|--------|------------|-------|-----------------|-------------------|---------------------|
| [dla46c_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/dla46c_pt_224/dla46c_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 184.23 | 5.43 | 3.0.0  |
| [dla46xc_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/dla46xc_pt_224/dla46xc_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 186.36 | 5.37 | 3.0.0  |
| [dla60xc_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/dla60xc_pt_224/dla60xc_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 187.54 | 5.33 | 3.0.0  |




### Accuracy with Imagenet dataset

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [dla46c_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46c_pt_224/dla46c_pt_224.onnx) | Float | 224x224x3 | 65.03 % |
| [dla46c_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46c_pt_224/dla46c_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 64.43 % |
| [dla46xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46xc_pt_224/dla46xc_pt_224.onnx) | Float | 224x224x3 | 66.50 % |
| [dla46xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46xc_pt_224/dla46xc_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 66.06 % |
| [dla60xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla60xc_pt_224/dla60xc_pt_224.onnx) | Float | 224x224x3 | 68.30 % |
| [dla60xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla60xc_pt_224/dla60xc_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 67.73 % |


Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [dla46c_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46c_pt_224/dla46c_pt_224.onnx) | Float | 224x224x3 | 65.03 % |
| [dla46c_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46c_pt_224/dla46c_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 64.43 % |
| [dla46xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46xc_pt_224/dla46xc_pt_224.onnx) | Float | 224x224x3 | 66.50 % |
| [dla46xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla46xc_pt_224/dla46xc_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 66.06 % |
| [dla60xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla60xc_pt_224/dla60xc_pt_224.onnx) | Float | 224x224x3 | 68.30 % |
| [dla60xc_pt](./Public_pretrainedmodel_public_dataset/Imagenet/dla60xc_pt_224/dla60xc_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 67.73 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: Deep Layer Aggregation — https://github.com/ucbdrive/dla
