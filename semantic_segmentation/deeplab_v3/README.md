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

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on Person PASCAL VOC 2012 + COCO 2017 segmentation dataset 21 classes and a derivative person dataset from it  (see Accuracy for details on dataset)

| Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version | STEdgeAI Core version |
|------------|---------------|----------|------------|-----------|--------------|--------------|---------------|----------------------|-----------------------|
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_256/deeplab_v3_mobilenetv2_05_16_256_asppv2_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 256x256x3 | STM32N6 | 2253.5 | 0.0 | 1001.25 | 10.0.0 | 2.0.0 | 
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_320/deeplab_v3_mobilenetv2_05_16_320_asppv2_qdq_int8.onnx) |person COCO 2017 + PASCAL VOC 2012 | Int8 | 320x320x3 | STM32N6 | 2446.0 | 0.0 | 1000.41 | 10.0.0 | 2.0.0 |
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_416/deeplab_v3_mobilenetv2_05_16_416_asppv2_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012  | Int8 | 416x416x3  | STM32N6 | 2743.5 | 2028.0 | 2721.19 | 10.0.0 | 2.0.0 |



### Reference **NPU**  inference time based on Person COCO  2017 + PASCAL VOC 2012  segmentation dataset 21 classes and a derivative person dataset from it  (see Accuracy for details on dataset)


| Model      | Dataset       | Format   | Resolution | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|------------|---------------|----------|------------|------------------|------------------|---------------------|-------------|----------------------|-------------------------|
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_256/deeplab_v3_mobilenetv2_05_16_256_asppv2_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 256x256x3 | STM32N6570-DK | NPU/MCU | 27.36 | 36.54 | 10.0.0 | 2.0.0 |
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_320/deeplab_v3_mobilenetv2_05_16_320_asppv2_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 320x320x3  | STM32N6570-DK | NPU/MCU | 44.99 | 22.22 | 10.0.0 | 2.0.0 |
| [DeepLabv3 MobileNetv2 ASPPv2](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_416/deeplab_v3_mobilenetv2_05_16_416_asppv2_qdq_int8.onnx) | person COCO 2017 + PASCAL VOC 2012 | Int8 | 416x416x3 | STM32N6570-DK | NPU/MCU | 191.91 | 5.21 | 10.0.0 | 2.0.0 |


### Reference **MPU** inference time based on COCO  2017 + PASCAL VOC 2012  segmentation dataset 21 classes and a derivative person dataset from it  (see Accuracy for details on dataset)
| Model | Dataset     | Format | Resolution | Quantization   | Board| Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU   | %CPU | X-LINUX-AI version |Framework |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|--------|------------|----------------|-------------------|------------------|-----------|---------------------|-------|--------|------|--------------------|-----------------------|
| [DeepLabV3 per tensor (no ASPP)](https://www.st.com/en/embedded-software/x-linux-ai.html)                                                                                                                       | COCO 2017 + PASCAL VOC 2012   | Int8   | 257x257x3  | per-tensor     | STM32MP257F-DK2   | NPU/GPU          | 1500  MHz | 52.75           | 99.2 | 0.80  | 0 | v5.1.0             | OpenVX                |                |       |        |      | v5.1.0 
| [DeepLabV3 MobileNetv2 ASPPv1 per channel](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1_int8.tflite) | COCO 2017 + PASCAL VOC 2012   | Int8 (tflite)  | 512x512x3  | per-channel ** | STM32MP257F-DK2   | NPU/GPU          | 1500  MHz | 806.12            | 8.73| 91.27 | 0   | v5.1.0             | OpenVX                |
| [DeepLabV3 MobileNetv2 ASPPv1 mixed precision](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1_int8_f32.tflite) | COCO 2017 + PASCAL VOC 2012   | Int8 & float32 (tflite) | 512x512x3  | per-channel ** | STM32MP257F-DK2   | NPU/GPU          | 1500  MHz |  894.56  | 7.67 | 92.33 | 0  | v5.1.0             | OpenVX                |
| [DeepLabV3 MobileNetv2 ASPPv1 per channel](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1_qdq_int8.onnx) | COCO 2017 + PASCAL VOC 2012   | Int8 (onnx) | 512x512x3 | per-channel ** | STM32MP257F-DK2  | NPU/GPU  | 1500  MHz |  729.62 | 3.0 | 97.0 | 0  | v5.1.0| OpenVX |

- **DeepLabV3 per tensor**:
   This model, which does not include ASPP (Atrous Spatial Pyramid Pooling), was downloaded from the TensorFlow DeepLabV3 page on [Kaggle](https://www.kaggle.com/models/tensorflow/deeplabv3/).

- **The onnx DeepLabv3 MobileNetv2 ASPPv1 per channel**:
   The quantized TFLite model is derived from the DeepLabV3 float precision model. The ONNX quantized model is obtained by quantizing the DeepLabV3 float model using the [deeplab_v3_mobilenetv2_05_16_512_asppv1_onnx_config](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1_onnx_config.yaml) YAML file.

   **Note:** These results were obtained using the exact YAML files mentioned above and a specific quantization set containing 4 images from the PASCAL VOC dataset with the following IDs:
   - 2008_004804
   - 2010_005620
   - 2010_004290
   - 2008_000183

- **DeepLabV3 MobileNetv2 ASPPv1 mixed precision**:
   This model is a mixed precision version of the DeepLabV3 float precision. The backbone is fully quantized to 8 bits, while the ASPP head remains partially in float precision. Some layers were too sensitive to 8-bit quantization, resulting in unacceptable accuracy degradation. Therefore, we instructed TFLite not to quantize those specific layers.

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### Accuracy with COCO 2017 + PASCAL VOC 2012  

**Pascal VOC Dataset Details:**

- **Link:** [VOC 2012 Dataset](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/) 
- **License:** [Database Contents License (DbCL) v1.0](https://opendatacommons.org/licenses/dbcl/1-0/)
- **Number of Classes:** 21
- **Contents:** 
  - 1464 training images and masks
  - 1449 validation images and masks


**Please follow the [PASCAL VOC 2012 tutorial](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/main/semantic_segmentation/datasets) to have more training masks (about 10,582) and a `trainaug.txt` file containing the IDs of the new training masks.**


**COCO Dataset Details:**

- **Link:** [COCO 2017 Dataset](https://cocodataset.org/#home)
- **License:** [COCO License](https://cocodataset.org/#termsofuse)

Please note, that the following accuracies are obtained after training the model with the augmented Pascal VOC + COCO data and evaluated on Pascal VOC 2012 validation set (val.txt), and with a preprocessing resize with interpolation method 'bilinear'.
Moreover, IoU are averaged on all classes including background.

**Please use the [COCO 2017 PASCAL VOC 2012 tutorial](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/main/semantic_segmentation/datasets/coco_2017_pascal_voc_2012) to create COCO 2017 + PASCAL VOC 2012 dataset to do the needed filtering. Only images containing one or more classes from the 21 Pascal VOC dataset classes should be used. Additionally, the masks need to be converted to the Pascal VOC masks format.**

| Model Description | Resolution | Format  | Accuracy | Averaed IoU |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|------------|----------|--------------|
| [DeepLabV3 per tensor (no ASPP)](https://www.st.com/en/embedded-software/x-linux-ai.html) | 257x257x3 | Int8  (tflite)| 88.6% | 59.33% |
| [Deeplabv3 MobileNetv2 ASPPv1 float precision](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1.h5) | 512x512x3 | Float | 93.29% | 73.44% |
| [DeepLabv3 MobileNetv2 ASPPv1 per channel](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1_int8.tflite) | 512x512x3  | Int8  (tflite) | 91.3% | 67.32% |
| [DDeepLabv3 MobileNetv2 ASPPv1 mixed precision](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1_int8_f32.tflite) | 512x512x3  | Int8/Float (tflite)| 92.83% | 71.93% |
| [DeepLabv3 MobileNetv2 ASPPv1 per channel](./ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512/deeplab_v3_mobilenetv2_05_16_512_asppv1_qdq_int8.onnx) | 512x512x3 | Int8  (onnx) | 93.15%| 72.39% |


### Accuracy with Person COCO 2017 + PASCAL VOC 2012  

**Please use the [Person COCO 2017 PASCAL VOC 2012 tutorial](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/main/semantic_segmentation/datasets/n_class_coco_2017_pascal_voc_2012) to create Pesron COCO 2017 + PASCAL VOC 2012 dataset.**

| Models Description                                  |   Resolution        | Format        | Accuracy (%) | average IoU |
|--------------------------------------------|-----------|---------------|--------------|-------------|
| [Deeplabv3 MobileNetv2 ASPPv2 float precision](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_256/deeplab_v3_mobilenetv2_05_16_256_asppv2.h5)   |   256x256x3       | TensorFlow    |   94.65 %    |   76.96 %   |
| [DeepLabv3 MobileNetv2 ASPPv2 per channel](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_256/deeplab_v3_mobilenetv2_05_16_256_asppv2_qdq_int8.onnx)      |   256x256x    | ONNX          |    94.57 %   |   76.62 %   |
| [Deeplabv3 MobileNetv2 ASPPv2 float precision](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_320/deeplab_v3_mobilenetv2_05_16_320_asppv2.h5) |   320x320x3       | TensorFlow    |   95.16 %    |   79.04 %   |
| [DeepLabv3 MobileNetv2 ASPPv2 per channel](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_320/deeplab_v3_mobilenetv2_05_16_320_asppv2_qdq_int8.onnx)      |    320x320x3  | ONNX          |    94.98 %   |  78.35 %    |
| [Deeplabv3 MobileNetv2 ASPPv2 float precision](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_416/deeplab_v3_mobilenetv2_05_16_416_asppv2.h5) |   416x416x3     | TensorFlow    |   95.48 %    |   80.62 %   |
| [DeepLabv3 MobileNetv2 ASPPv2 per channel](./ST_pretrainedmodel_public_dataset/person_coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_416/deeplab_v3_mobilenetv2_05_16_416_asppv2_qdq_int8.onnx)       |   416x416x3       | ONNX          |   95.44 %    |   80.36 %   |


Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)
