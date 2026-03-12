# ST ResNet

## **Use case** : `Image classification`

# Model description


ST ResNet is STMicroelectronics' custom ResNet family **specifically designed and optimized for STM32 deployment**. It offers a range of sizes from "pico" to "tiny" with ReLU activations, providing a progressive accuracy-efficiency trade-off tailored for embedded vision applications.

The architecture is **STM32-optimized** and designed specifically for STM32 NPU deployment, with **progressive sizing** from Pico → Nano → Micro → Milli → Tiny (increasing capacity). It uses **ReLU activation** for quantization friendliness and a **balanced design** optimized for both accuracy and inference speed on target hardware.

ST ResNet models are the **recommended choice** for production STM32 deployments, with all variants running on internal RAM only and well-characterized performance on STM32 hardware.

(source: https://arxiv.org/abs/2601.05364, https://arxiv.org/abs/2511.11716)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~0.59–3.97 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/STMicroelectronics/stm32ai-modelzoo |
| Paper              | https://arxiv.org/abs/2601.05364 |

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
| [st_resnetpico_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetpico_actrelu_pt_224/st_resnetpico_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 784 | 0 | 607.27 | 3.0.0 |
| [st_resnetnano_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetnano_actrelu_pt_224/st_resnetnano_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 759.5 | 0 | 992.04 | 3.0.0 |
| [st_resnetmicro_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmicro_actrelu_pt_224/st_resnetmicro_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 882 | 0 | 1534.12 | 3.0.0 |
| [st_resnetmilli_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmilli_actrelu_pt_224/st_resnetmilli_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 1421 | 0 | 3059.81 | 3.0.0 |
| [st_resnettiny_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnettiny_actrelu_pt_224/st_resnettiny_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 2205 | 0 | 4060.57 | 3.0.0 |


### Reference **NPU**  inference time on  imagenet dataset (see Accuracy for details on dataset)

| Model  |  Dataset  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|---------|--------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [st_resnetpico_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetpico_actrelu_pt_224/st_resnetpico_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 7.54 | 132.63 | 3.0.0  |
| [st_resnetnano_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetnano_actrelu_pt_224/st_resnetnano_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 9.46 | 105.71 | 3.0.0  |
| [st_resnetmicro_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmicro_actrelu_pt_224/st_resnetmicro_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 13.83 | 72.31 | 3.0.0  |
| [st_resnetmilli_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmilli_actrelu_pt_224/st_resnetmilli_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 17.59 | 56.85 | 3.0.0  |
| [st_resnettiny_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnettiny_actrelu_pt_224/st_resnettiny_actrelu_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 24.10 | 41.49 | 3.0.0  |

| Model  |  Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|--------|-------------|------------------|------------------|---------------------|-----------|----------------------|-------------------------|
| [st_resnetpico_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetpico_actrelu_pt_224/st_resnetpico_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 7.54 | 132.63 | 10.2.0 | 2.2.0 |
| [st_resnetnano_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetnano_actrelu_pt_224/st_resnetnano_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 9.46 | 105.71 | 10.2.0 | 2.2.0 |
| [st_resnetmicro_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmicro_actrelu_pt_224/st_resnetmicro_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 13.83 | 72.31 | 10.2.0 | 2.2.0 |
| [st_resnetmilli_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmilli_actrelu_pt_224/st_resnetmilli_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 17.59 | 56.85 | 10.2.0 | 2.2.0 |
| [st_resnettiny_actrelu_pt_224](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnettiny_actrelu_pt_224/st_resnettiny_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 24.10 | 41.49 | 10.2.0 | 2.2.0 |


### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| Model | Format | Resolution | Top 1 Accuracy |
|-------|--------|------------|----------------|
| [st_resnetmicro_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmicro_actrelu_pt_224/st_resnetmicro_actrelu_pt_224.onnx) | Float | 224×224×3 | 66.43 % |
| [st_resnetmicro_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmicro_actrelu_pt_224/st_resnetmicro_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | 65.62 % |
| [st_resnetmilli_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmilli_actrelu_pt_224/st_resnetmilli_actrelu_pt_224.onnx) | Float | 224×224×3 | 71.10 % |
| [st_resnetmilli_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetmilli_actrelu_pt_224/st_resnetmilli_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | 70.45 % |
| [st_resnetnano_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetnano_actrelu_pt_224/st_resnetnano_actrelu_pt_224.onnx) | Float | 224×224×3 | 59.32 % |
| [st_resnetnano_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetnano_actrelu_pt_224/st_resnetnano_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | 58.25 % |
| [st_resnetpico_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetpico_actrelu_pt_224/st_resnetpico_actrelu_pt_224.onnx) | Float | 224×224×3 | 49.42 % |
| [st_resnetpico_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnetpico_actrelu_pt_224/st_resnetpico_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | 46.98 % |
| [st_resnettiny_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnettiny_actrelu_pt_224/st_resnettiny_actrelu_pt_224.onnx) | Float | 224×224×3 | 72.07 % |
| [st_resnettiny_actrelu_pt](./ST_pretrainedmodel_public_dataset/Imagenet/st_resnettiny_actrelu_pt_224/st_resnettiny_actrelu_pt_224_qdq_int8.onnx) | Int8 | 224×224×3 | 71.40 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: STRESNET & STYOLO — https://arxiv.org/abs/2601.05364

<a id="3">[3]</a> - **Model**: CompressNAS — https://arxiv.org/abs/2511.11716
