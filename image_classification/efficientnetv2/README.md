# EfficientNet v2

## **Use case** : `Image classification`

# Model description


EfficientNet v2 family is one of the best topologies for image classification. It has been obtained through neural architecture search with a special care given to training time 
and number of parameters reduction.

This family of networks comprises various subtypes: B0 (224x224), B1 (240x240), B2 (260x260), B3 (300x300), S (384x384) ranked by depth and width increasing order.
There are also M, L, XL variants but too large to be executed efficiently on STM32N6.

All these networks are already available on https://www.tensorflow.org/api_docs/python/tf/keras/applications/ pre-trained on ImageNet.


## Network information


| Network Information | Value                                                                            |
|---------------------|----------------------------------------------------------------------------------|
| Framework           | TensorFlow Lite/ONNX quantizer                                                   |
| MParams type=B0     | 7.1 M                                                                            |
| Quantization        | int8                                                                             |
| Provenance          | https://www.tensorflow.org/api_docs/python/tf/keras/applications/efficientnet_v2 |
| Paper               | https://arxiv.org/pdf/2104.00298                                                 |

The models are quantized using tensorflow lite converter or ONNX quantizer.


## Network inputs / outputs


For an image resolution of NxM and P classes

| Input Shape   | Description                                                         |
|---------------|---------------------------------------------------------------------|
| (1, N, M, 3)  | Single NxM RGB image with UINT8 values between 0 and 255 for tflite |
| (1, 3, N, M)  | Single NxM RGB image with INT8 values between -128 and 127 for ONNX |

| Output Shape | Description                                              |
| ----- |----------------------------------------------------------|
| (1, P) | Per-class confidence for P classes in FLOAT32 for tflite |
| (1, P) | Per-class confidence for P classes in FLOAT32 for ONNX   |


## Recommended platforms


| Platform  | Supported | Recommended |
|-----------|-----------|-------------|
| STM32L0   |[]| []          |
| STM32L4   |[]| []          |
| STM32U5   |[]| []          |
| STM32H7   |[]| []          |
| STM32MP1  |[x]| [x]         |
| STM32MP2  |[x]| [x]         |
| STM32N6   |[x]| [x]         |


# Performances

## Metrics

* Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
* `fft` stands for "full fine-tuning", meaning that the full model weights were initialized from a transfer learning pre-trained model, and all the layers were unfrozen during the training.

### Reference **NPU** memory footprint on food-101 and ImageNet dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [efficientnet_v2B0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B0_224_fft/efficientnet_v2B0_224_fft_qdq_int8.onnx) | food-101      | Int8     | 224x224x3  | STM32N6   | 1834.44 |0.0| 7553.77 |       10.0.0        |     2.0.0   |
| [efficientnet_v2B1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B1_240_fft/efficientnet_v2B1_240_fft_qdq_int8.onnx) | food-101      | Int8     | 240x240x3  | STM32N6   | 2589.97 |0.0| 8924.78 |       10.0.0        |     2.0.0   |
| [efficientnet_v2B2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B2_260_fft/efficientnet_v2B2_260_fft_qdq_int8.onnx) | food-101      | Int8     | 260x260x3  | STM32N6   | 2629.56 |528.12| 11212.75|       10.0.0        |     2.0.0   |
| [efficientnet_v2S_384_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2S_384_fft/efficientnet_v2S_384_fft_qdq_int8.onnx) | food-101 | Int8     | 384x384x3  | STM32N6   | 2700 | 6912 | 25756.92 | 10.0.0 | 2.0.0 |
| [efficientnet_v2B0_224 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B0_224/efficientnet_v2B0_224_qdq_int8.onnx) | ImageNet | Int8     | 224x224x3  | STM32N6   | 1834.44 | 0.0 | 8680.39 | 10.0.0 | 2.0.0 |
| [efficientnet_v2B1_240 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B1_240/efficientnet_v2B1_240_qdq_int8.onnx) | ImageNet | Int8     | 240x240x3  | STM32N6   | 2589.97 | 0.0 | 10051.7 | 10.0.0 | 2.0.0 |
| [efficientnet_v2B2_260 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B2_260/efficientnet_v2B2_260_qdq_int8.onnx) | ImageNet | Int8     | 260x260x3  | STM32N6   | 2629.56 | 528.12 | 12451.77 | 10.0.0 | 2.0.0 |
| [efficientnet_v2S_384 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2S_384/efficientnet_v2S_384_qdq_int8.onnx) | ImageNet |       Int8     | 384x384x3  | STM32N6   | 2700 | 6912 | 26884.47 | 10.0.0 | 2.0.0 |


### Reference **NPU**  inference time on food-101 and ImageNet dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [efficientnet_v2B0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B0_224_fft/efficientnet_v2B0_224_fft_qdq_int8.onnx) | food-101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 54.32 | 18.41 |       10.0.0        |     2.0.0   |
| [efficientnet_v2B1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B1_240_fft/efficientnet_v2B1_240_fft_qdq_int8.onnx) | food-101      | Int8     | 240x240x3  | STM32N6570-DK   |   NPU/MCU      | 73.89 | 13.53 |       10.0.0        |     2.0.0   |
| [efficientnet_v2B2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B2_260_fft/efficientnet_v2B2_260_fft_qdq_int8.onnx) | food-101      | Int8     | 260x260x3  | STM32N6570-DK   |   NPU/MCU      | 146.01 | 6.85 |       10.0.0        |     2.0.0   |
| [efficientnet_v2S_384_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2S_384_fft/efficientnet_v2S_384_fft_qdq_int8.onnx) | food-101      | Int8     | 384x384x3  | STM32N6570-DK   | NPU/MCU | 842 | 1.19 |       10.0.0        |     2.0.0   |
| [efficientnet_v2B0_224 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B0_224/efficientnet_v2B0_224_qdq_int8.onnx) | ImageNet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 57.5 | 17.39 |       10.0.0        |     2.0.0   |
| [efficientnet_v2B1_240 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B1_240/efficientnet_v2B1_240_qdq_int8.onnx) | ImageNet      | Int8     | 240x240x3  | STM32N6570-DK   |   NPU/MCU      |	77.25 | 12.94 |       10.0.0        |     2.0.0   |
| [efficientnet_v2B2_260 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B2_260/efficientnet_v2B2_260_qdq_int8.onnx) | ImageNet      | Int8     | 260x260x3  | STM32N6570-DK   |   NPU/MCU      | 148.78 | 6.72 |       10.0.0        |     2.0.0   |
| [efficientnet_v2S_384 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2S_384/efficientnet_v2S_384_qdq_int8.onnx) | ImageNet      | Int8     | 384x384x3  | STM32N6570-DK   |   NPU/MCU      | 809.73 | 1.23 |       10.0.0        |     2.0.0   |

* The deployment of all the models listed in the table is supported, except for the efficientnet_v2S_384 model, for which support is coming soon.
### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model                                                                                                                                            | Format | Resolution | Top 1 Accuracy |
|--------------------------------------------------------------------------------------------------------------------------------------------------|--------|-----------|----------------|
| [efficientnet_v2B0_224_fft](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B0_224_fft/efficientnet_v2B0_224_fft.h5)                 | Float  | 224x224x3 | 81.35 %        |
| [efficientnet_v2B0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B0_224_fft/efficientnet_v2B0_224_fft_qdq_int8.onnx) | Int8   | 224x224x3 | 81.1 %        |
| [efficientnet_v2B1_240_fft](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B1_240_fft/efficientnet_v2B1_240_fft.h5)                 | Float  | 240x240x3 | 83.23 %        |
| [efficientnet_v2B1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B1_240_fft/efficientnet_v2B1_240_fft_qdq_int8.onnx) | Int8   | 240x240x3 | 82.95 %        |
| [efficientnet_v2B2_260_fft](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B2_260_fft/efficientnet_v2B2_260_fft.h5)                 | Float  | 260x260x3 | 84.37 %        |
| [efficientnet_v2B2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2B2_260_fft/efficientnet_v2B2_260_fft_qdq_int8.onnx) | Int8   | 260x260x3 | 84.04 %        |
| [efficientnet_v2S_384_fft](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2S_384_fft/efficientnet_v2S_384_fft.h5)                    | Float  | 384x384x3 | 88.16 %        |
| [efficientnet_v2S_384_fft onnx](./ST_pretrainedmodel_public_dataset/food-101/efficientnet_v2S_384_fft/efficientnet_v2S_384_fft_qdq_int8.onnx)    | Int8   | 384x384x3 | 87.34 %        |


### Accuracy with ImageNet

Dataset details: [link](https://www.image-net.org), Quotation[[4]](#4).
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 10000 labelled images of the validation set.

| Model                                                                                                                                    | Format | Resolution | Top 1 Accuracy |
|------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|----------------|
| [efficientnet_v2B0_224](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B0_224/efficientnet_v2B0_224.h5)                 | Float  | 224x224x3  | 73.94 %        |
| [efficientnet_v2B0_224 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B0_224/efficientnet_v2B0_224_qdq_int8.onnx) | Int8   | 224x224x3  | 72.21 %        |
| [efficientnet_v2B1_240](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B1_240/efficientnet_v2B1_240.h5)                 | Float  | 240x240x3  | 76.14 %        |
| [efficientnet_v2B1_240 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B1_240/efficientnet_v2B1_240_qdq_int8.onnx) | Int8   | 240x240x3  | 75.5 %        |
| [efficientnet_v2B2_260](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B2_260/efficientnet_v2B2_260.h5)                 | Float  | 260x260x3  | 76.58 %        |
| [efficientnet_v2B2_260 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2B2_260/efficientnet_v2B2_260_qdq_int8.onnx) | Int8   | 260x260x3  | 76.26 %        |
| [efficientnet_v2S_384](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2S_384/efficientnet_v2S_384.h5)                    | Float  | 384x384x3  | 83.52 %        |
| [efficientnet_v2S_384 onnx](./Public_pretrainedmodel_public_dataset/ImageNet/efficientnet_v2S_384/efficientnet_v2S_384_qdq_int8.onnx)    | Int8   | 384x384x3  | 83.07 %        |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.

<a id="4">[4]</a>
Olga Russakovsky*, Jia Deng*, Hao Su, Jonathan Krause, Sanjeev Satheesh, Sean Ma, Zhiheng Huang, Andrej Karpathy, Aditya Khosla, Michael Bernstein, Alexander C. Berg and Li Fei-Fei.
(* = equal contribution) ImageNet Large Scale Visual Recognition Challenge.
