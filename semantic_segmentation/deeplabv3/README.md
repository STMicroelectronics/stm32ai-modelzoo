# DeepLab v3

## **Use case** : `Semantic Segmentation`

# Model description

DeepLabv3 was specified in "Rethinking Atrous Convolution for Semantic Image Segmentation" paper by Google.
It is composed by a backbone (encoder) that can be a Mobilenet V2 (width parameter alpha) or a ResNet-50 or 101 for example followed by an ASPP (Atrous Spatial Pyramid Pooling) as described in the paper.

ASPP applies on encoder outputs several parallel dilated convolutions with various dilation rates. This technique helps capturing longer range context without increasing too much the number of parameters.
The multi-scale design of the ASPP has proved to be receptive at the same time to details and greater contextual information.

So far, we have only considered Mobilenet V2 encoder.

## Network information


| Network Information     | Value                                                          |
|-------------------------|----------------------------------------------------------------|
|  Framework              | TensorFlow Lite                                                |
|  Quantization           | int8                                                           |
|  Provenance             | https://www.tensorflow.org/lite/examples/segmentation/overview |
|  Paper                  | https://arxiv.org/pdf/1706.05587                               |

The models are quantized using tensorflow lite converter.


## Network inputs / outputs


For an image resolution of NxM and P classes

| Input Shape  | Description |
|--------------| ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape  | Description                                      |
|---------------|--------------------------------------------------|
| (1, N, M, 21) | Per-class confidence for P=21 classes in FLOAT32 |


## Recommended platforms


| Platform | Supported | Recommended |
|----------|--------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[]|[]|
| STM32U5  |[]|[]|
| STM32H7  |[]|[]|
| STM32MP1 |[]|[]|
| STM32MP2 |[x]|[x]|
| STM32N6  |[x]|[x]|


# Performances

## Metrics

Measures are done with default STEdgeAI Core version configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on Person PASCAL VOC 2012 + COCO 2017 segmentation dataset 21 classes and a derivative person dataset from it  (see Accuracy for details on dataset)

| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|--------------------|--------------------|---------------------|----------------------|
 [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_256/st_deeplabv3_mnv2_a050_s16_asppv2_256_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 256x256x3 | STM32N6 | 1869.88 | 0.0    | 882.33  | 3.0.0 |
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_320/st_deeplabv3_mnv2_a050_s16_asppv2_320_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 320x320x3 | STM32N6 | 2421    | 0.0    | 893.3   | 3.0.0 |
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_416/st_deeplabv3_mnv2_a050_s16_asppv2_416_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 416x416x3 | STM32N6 | 2802.28 | 2028.0 | 894.14  | 3.0.0 |



### Reference **NPU**  inference time based on Person COCO  2017 + PASCAL VOC 2012  segmentation dataset 21 classes and a derivative person dataset from it  (see Accuracy for details on dataset)


| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|---------------------|-----------|----------------------
 [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_256/st_deeplabv3_mnv2_a050_s16_asppv2_256_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 256x256x3 | STM32N6570-DK | NPU/MCU | 26.62 | 37.55 | 3.0.0 |
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_320/st_deeplabv3_mnv2_a050_s16_asppv2_320_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 320x320x3 | STM32N6570-DK | NPU/MCU | 40.83 | 24.49 | 3.0.0 |
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_416/st_deeplabv3_mnv2_a050_s16_asppv2_416_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 416x416x3 | STM32N6570-DK | NPU/MCU | 227.02 | 4.41 | 3.0.0 |




### Accuracy with Person COCO 2017 + PASCAL VOC 2012

**Please use the [Person COCO 2017 PASCAL VOC 2012 tutorial](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/main/semantic_segmentation/datasets/n_class_coco_2017_pascal_voc_2012) to create Pesron COCO 2017 + PASCAL VOC 2012 dataset.**

| Models Description                                  |   Resolution        | Format        | Accuracy (%) | average IoU |
|--------------------------------------------|-----------|---------------|--------------|-------------|
| [Deeplabv3 MobileNetv2 ASPPv2 float precision](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_256/st_deeplabv3_mnv2_a050_s16_asppv2_256.keras)   |   256x256x3       | TensorFlow    |   94.46 %    |   76.58 %   |
| [DeepLabv3 MobileNetv2 ASPPv2 per channel](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_256/st_deeplabv3_mnv2_a050_s16_asppv2_256_qdq_int8.onnx)      |   256x256x3    | ONNX          |    94.42 %   |   76.25 %   |
| [Deeplabv3 MobileNetv2 ASPPv2 float precision](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_320/st_deeplabv3_mnv2_a050_s16_asppv2_320.keras) |   320x320x3       | TensorFlow    |   94.8 %    |   77.87 %   |
| [DeepLabv3 MobileNetv2 ASPPv2 per channel](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_320/st_deeplabv3_mnv2_a050_s16_asppv2_320_qdq_int8.onnx)      |    320x320x3  | ONNX          |    94.71 %   |  77.45 %    |
| [Deeplabv3 MobileNetv2 ASPPv2 float precision](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_416/st_deeplabv3_mnv2_a050_s16_asppv2_416.keras) |   416x416x3     | TensorFlow    |   95.25 %    |   79.9 %   |
| [DeepLabv3 MobileNetv2 ASPPv2 per channel](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/st_deeplabv3_mnv2_a050_s16_asppv2_416/st_deeplabv3_mnv2_a050_s16_asppv2_416_qdq_int8.onnx)       |   416x416x3       | ONNX          |   95.1 %    |   79.18 %   |

**The ASPPv2 is an improved version of the Atrous Spatial Pyramid Pooling (ASPP) module. In ASPPv2, the standard atrous (dilated) convolutions are replaced by separable depthwise dilated convolutions. This change reduces computational complexity and model size, while still capturing multi-scale context efficiently. Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)**
