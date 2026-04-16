# EfficientNet v2

## **Use case** : `Image classification`

# Model description


EfficientNet v2 family is one of the best topologies for image classification. It has been obtained through neural architecture search with a special care given to training time and number of parameters reduction.

This family of networks comprises various subtypes: B0 (224x224), B1 (240x240), B2 (260x260), B3 (300x300), S (384x384) ranked by depth and width increasing order.
There are also M, L, XL variants but too large to be executed efficiently on STM32N6.

All these networks are already available on https://www.tensorflow.org/api_docs/python/tf/keras/applications/ pre-trained on imagenet.


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

### Reference **NPU** memory footprint on food101 and imagenet dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-----------|---------------|----------|------------|-----------|--------------------|--------------------|---------------------|-----------------------|
| [efficientnetv2b0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b0_224_fft/efficientnetv2b0_224_fft_qdq_int8.onnx) | food101      | Int8     | 224x224x3  | STM32N6   | 722.75 |0.0| 6839.39             |     4.0.0   |
| [efficientnetv2b0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b0_224_fft/efficientnetv2b0_224_fft_qdq_w4_90.1%_w8_9.9%_a8_100%_acc_84.47.onnx) | food101      | Int8/Int4     | 224x224x3  | STM32N6   | 722.75 |0.0| 4237.52             |     4.0.0   |
| [efficientnetv2b1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b1_240_fft/efficientnetv2b1_240_fft_qdq_int8.onnx) | food101      | Int8     | 240x240x3  | STM32N6   | 1118.65 |0.0| 8089.27             |     4.0.0   |
| [efficientnetv2b1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b1_240_fft/efficientnetv2b1_240_fft_qdq_w4_91.8%_w8_8.2%_a8_100%_acc_85.71.onnx) | food101      | Int8/Int4     | 240x240x3  | STM32N6   | 1118.65 |0.0| 4995.39             |     4.0.0   |
| [efficientnetv2b2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b2_260_fft/efficientnetv2b2_260_fft_qdq_int8.onnx) | food101      | Int8     | 260x260x3  | STM32N6   | 1233.2 |0.0| 10328.52         |     4.0.0   |
| [efficientnetv2b2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b2_260_fft/efficientnetv2b2_260_fft_qdq_w4_81.26%_w8_18.74%_a8_100%_acc_87.24.onnx) | food101      | Int8/Int4     | 260x260x3  | STM32N6   | 1233.2 |0.0| 6865.39         |     4.0.0   |
| [efficientnetv2s_384_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2s_384_fft/efficientnetv2s_384_fft_qdq_int8.onnx) | food101 | Int8     | 384x384x3  | STM32N6   | 2471.94 | 1728 | 24262.34            | 4.0.0 |
| [efficientnetv2s_384_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2s_384_fft/efficientnetv2s_384_fft_qdq_w4_95.95%_w8_4.05%_a8_100%_acc_89.87.onnx) | food101 | Int8/Int4     | 384x384x3  | STM32N6   | 2471.94 | 1728 | 14836.94            | 4.0.0 |
| [efficientnetv2b0_224 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b0_224/efficientnetv2b0_224_qdq_int8.onnx) | imagenet | Int8     | 224x224x3  | STM32N6   | 722.75 | 0.0 | 7967.05           | 4.0.0 |
| [efficientnetv2b0_224 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b0_224/efficientnetv2b0_224_qdq_w4_65.43%_w8_34.57%_a8_100%_acc_73.38.onnx) | imagenet | Int8/Int4     | 224x224x3  | STM32N6   | 722.75 | 0.0 | 5710.05           | 4.0.0 |
| [efficientnetv2b1_240 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b1_240/efficientnetv2b1_240_qdq_int8.onnx) | imagenet | Int8     | 240x240x3  | STM32N6   | 1118.65 | 0.0 | 9216.92           | 4.0.0 |
| [efficientnetv2b1_240 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b1_240/efficientnetv2b1_240_qdq_w4_73.1%_w8_26.9%_a8_100%_acc_73.92.onnx) | imagenet | Int8/Int4     | 240x240x3  | STM32N6   | 1118.65 | 0.0 | 6342.67           | 4.0.0 |
| [efficientnetv2b2_260 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b2_260/efficientnetv2b2_260_qdq_int8.onnx) | imagenet | Int8     | 260x260x3  | STM32N6   | 1233.2 | 0.0 | 11568.55       | 4.0.0 |
| [efficientnetv2b2_260 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b2_260/efficientnetv2b2_260_qdq_w4_67.53%_w8_32.47%_a8_100%_acc_74.71.onnx) | imagenet | Int8/Int4     | 260x260x3  | STM32N6   | 2233.2 | 0.0 | 8273.17       | 4.0.0 |
| [efficientnetv2b3_300 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b3_300/efficientnetv2b3_300_qdq_int8.onnx) | imagenet | Int8     | 300x300x3  | STM32N6   | 2051.65 | 0.0 | 16510.05       | 4.0.0 |
| [efficientnetv2b3_300 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b3_300/efficientnetv2b3_300_qdq_w4_88.31%_w8_11.69%_a8_100%_acc_78.11.onnx) | imagenet | Int8/Int4     | 300x300x3  | STM32N6   | 2051.65 | 0.0 | 10376.74       | 4.0.0 |
| [efficientnetv2s_384 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2s_384/efficientnetv2s_384_qdq_int8.onnx) | imagenet |       Int8     | 384x384x3  | STM32N6   | 2768 | 1728 | 25390            | 4.0.0 |
| [efficientnetv2s_384 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2s_384/efficientnetv2s_384_qdq_w4_95.63%_w8_4.37%_a8_100%_acc_82.25.onnx) | imagenet |       Int8/Int4     | 384x384x3  | STM32N6   | 2768 | 1728 | 15458.97            | 4.0.0 |



### Reference **NPU**  inference time on food101 and imagenet dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-----------|------------------------|
| [efficientnetv2b0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b0_224_fft/efficientnetv2b0_224_fft_qdq_int8.onnx) | food101      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 33.12               | 30.2     |           4.0.0   |
| [efficientnetv2b0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b0_224_fft/efficientnetv2b0_224_fft_qdq_w4_90.1%_w8_9.9%_a8_100%_acc_84.47.onnx) | food101      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 27.97               | 35.7     |           4.0.0   |
| [efficientnetv2b1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b1_240_fft/efficientnetv2b1_240_fft_qdq_int8.onnx) | food101      | Int8     | 240x240x3  | STM32N6570-DK   |   NPU/MCU      | 44.01               | 22.7      |        4.0.0   |
| [efficientnetv2b1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b1_240_fft/efficientnetv2b1_240_fft_qdq_w4_91.8%_w8_8.2%_a8_100%_acc_85.71.onnx) | food101      | Int8/Int4     | 240x240x3  | STM32N6570-DK   |   NPU/MCU      | 38.51               | 25.9     |         4.0.0   |
| [efficientnetv2b2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b2_260_fft/efficientnetv2b2_260_fft_qdq_int8.onnx) | food101      | Int8     | 260x260x3  | STM32N6570-DK   |   NPU/MCU      |     57.47          |   17.4    |        4.0.0   |
| [efficientnetv2b2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b2_260_fft/efficientnetv2b2_260_fft_qdq_w4_81.26%_w8_18.74%_a8_100%_acc_87.24.onnx) | food101      | Int8/Int4     | 260x260x3  | STM32N6570-DK   |   NPU/MCU      | 50.51              | 19.8          |     4.0.0   |
| [efficientnetv2s_384_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2s_384_fft/efficientnetv2s_384_fft_qdq_int8.onnx) | food101      | Int8     | 384x384x3  | STM32N6570-DK   | NPU/MCU |      706.3         | 1.4      |     4.0.0   |
| [efficientnetv2s_384_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2s_384_fft/efficientnetv2s_384_fft_qdq_w4_95.95%_w8_4.05%_a8_100%_acc_89.87.onnx) | food101      | Int8/Int4     | 384x384x3  | STM32N6570-DK   | NPU/MCU | 696.49              | 1.4      |     4.0.0   |
| [efficientnetv2b0_224 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b0_224/efficientnetv2b0_224_qdq_int8.onnx) | imagenet      | Int8     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      |  36.1              | 27.7     |     4.0.0   |
| [efficientnetv2b0_224 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b0_224/efficientnetv2b0_224_qdq_w4_65.43%_w8_34.57%_a8_100%_acc_73.38.onnx) | imagenet      | Int8/Int4     | 224x224x3  | STM32N6570-DK   |   NPU/MCU      | 30.52              | 32.7     |     4.0.0   |
| [efficientnetv2b1_240 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b1_240/efficientnetv2b1_240_qdq_int8.onnx) | imagenet      | Int8     | 240x240x3  | STM32N6570-DK   |   NPU/MCU      | 47.72            | 20.9     |       4.0.0   |
| [efficientnetv2b1_240 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b1_240/efficientnetv2b1_240_qdq_w4_73.1%_w8_26.9%_a8_100%_acc_73.92.onnx) | imagenet      | Int8/Int4     | 240x240x3  | STM32N6570-DK   |   NPU/MCU      | 41.26             |  24.2    |    4.0.0   |
| [efficientnetv2b2_260 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b2_260/efficientnetv2b2_260_qdq_int8.onnx) | imagenet      | Int8     | 260x260x3  | STM32N6570-DK   |   NPU/MCU      |     60.29         |   16.6    |     4.0.0   |
| [efficientnetv2b2_260 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b2_260/efficientnetv2b2_260_qdq_w4_67.53%_w8_32.47%_a8_100%_acc_74.71.onnx) | imagenet      | Int8/Int4     | 260x260x3  | STM32N6570-DK   |   NPU/MCU      |        50.94     |  19.6   |   4.0.0   |
| [efficientnetv2b3_300 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b3_300/efficientnetv2b3_300_qdq_int8.onnx) | imagenet      | Int8     | 300x300x3  | STM32N6570-DK   |   NPU/MCU      |        146.64     |   6.8   |     4.0.0   |
| [efficientnetv2b3_300 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b3_300/efficientnetv2b3_300_qdq_w4_88.31%_w8_11.69%_a8_100%_acc_78.11.onnx) | imagenet      | Int8/Int4     | 300x300x3  | STM32N6570-DK   |   NPU/MCU      |  142.46           |  7.0    |     4.0.0   |
| [efficientnetv2s_384 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2s_384/efficientnetv2s_384_qdq_int8.onnx) | imagenet      | Int8     | 384x384x3  | STM32N6570-DK   |   NPU/MCU      |     475.35         |  2.1    |     4.0.0   |
| [efficientnetv2s_384 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2s_384/efficientnetv2s_384_qdq_w4_95.63%_w8_4.37%_a8_100%_acc_82.25.onnx) | imagenet      | Int8/Int4     | 384x384x3  | STM32N6570-DK   |   NPU/MCU      |      463.91       |   2.2   |     4.0.0   |

### Accuracy with Food-101 dataset

Dataset details: [link](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/), Quotation[[3]](#3)  , Number of classes: 101 , Number of images:  101 000

| Model                                                                                                                                            | Format | Resolution | Top 1 Accuracy |
|--------------------------------------------------------------------------------------------------------------------------------------------------|--------|-----------|----------------|
| [efficientnetv2b0_224_fft](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b0_224_fft/efficientnetv2b0_224_fft.keras)              | Float  | 224x224x3 | 86.59 %        |
| [efficientnetv2b0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b0_224_fft/efficientnetv2b0_224_fft_qdq_int8.onnx) | Int8   | 224x224x3 | 85.98 %        |
| [efficientnetv2b0_224_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b0_224_fft/efficientnetv2b0_224_fft_qdq_w4_90.1%_w8_9.9%_a8_100%_acc_84.47.onnx)| Int8/Int4 | 224x224x3 | 84.47 % |
| [efficientnetv2b1_240_fft](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b1_240_fft/efficientnetv2b1_240_fft.keras)              | Float  | 240x240x3 | 87.71 %        |
| [efficientnetv2b1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b1_240_fft/efficientnetv2b1_240_fft_qdq_int8.onnx) | Int8   | 240x240x3 | 87.09 %        |
| [efficientnetv2b1_240_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b1_240_fft/efficientnetv2b1_240_fft_qdq_w4_91.8%_w8_8.2%_a8_100%_acc_85.71.onnx) | Int8/Int4 | 240x240x3 | 85.71 % |
| [efficientnetv2b2_260_fft](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b2_260_fft/efficientnetv2b2_260_fft.keras)              | Float  | 260x260x3 | 88.67 %        |
| [efficientnetv2b2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b2_260_fft/efficientnetv2b2_260_fft_qdq_int8.onnx) | Int8   | 260x260x3 | 88.44 %        |
| [efficientnetv2b2_260_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2b2_260_fft/efficientnetv2b2_260_fft_qdq_w4_81.26%_w8_18.74%_a8_100%_acc_87.24.onnx) | Int8/Int4 | 260x260x3 | 87.24 % |
| [efficientnetv2s_384_fft](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2s_384_fft/efficientnetv2s_384_fft.keras)                 | Float  | 384x384x3 | 91.69 %        |
| [efficientnetv2s_384_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2s_384_fft/efficientnetv2s_384_fft_qdq_int8.onnx)    | Int8   | 384x384x3 | 91.34 %        |
| [efficientnetv2s_384_fft onnx](./ST_pretrainedmodel_public_dataset/food101/efficientnetv2s_384_fft/efficientnetv2s_384_fft_qdq_w4_95.95%_w8_4.05%_a8_100%_acc_89.87.onnx) | Int8/Int4 | 384x384x3 | 89.87 % | 


### Accuracy with imagenet

Dataset details: [link](https://www.image-net.org), Quotation[[4]](#4).
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 10000 labelled images of the validation set.

| Model                                                                                                                                    | Format | Resolution | Top 1 Accuracy |
|------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|----------------|
| [efficientnetv2b0_224](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b0_224/efficientnetv2b0_224.keras)                 | Float  | 224x224x3  |   75.18 %      |
| [efficientnetv2b0_224 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b0_224/efficientnetv2b0_224_qdq_int8.onnx)    | Int8   | 224x224x3  |   73.75 %      |
| [efficientnetv2b0_224 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b0_224/efficientnetv2b0_224_qdq_w4_65.43%_w8_34.57%_a8_100%_acc_73.38.onnx) | Int8/Int4  | 224x224x3  |    73.38 %     |
| [efficientnetv2b1_240](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b1_240/efficientnetv2b1_240.keras)                 | Float  | 240x240x3  |   76.14 %      |
| [efficientnetv2b1_240 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b1_240/efficientnetv2b1_240_qdq_int8.onnx)    | Int8   | 240x240x3  |   75.19 %      |
| [efficientnetv2b1_240 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b1_240/efficientnetv2b1_240_qdq_w4_73.1%_w8_26.9%_a8_100%_acc_73.92.onnx)  | Int8/Int4   | 240x240x3  |    73.92 %   |
| [efficientnetv2b2_260](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b2_260/efficientnetv2b2_260.keras)                 | Float  | 260x260x3  |   76.58 %      |
| [efficientnetv2b2_260 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b2_260/efficientnetv2b2_260_qdq_int8.onnx)    | Int8   | 260x260x3  |   76.14 %      |
|[efficientnetv2b2_260 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b2_260/efficientnetv2b2_260_qdq_w4_67.53%_w8_32.47%_a8_100%_acc_74.71.onnx) | Int8/Int4   | 260x260x3  |   74.71 %    |
| [efficientnetv2b3_300](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b3_300/efficientnetv2b3_300.keras)                 | Float  | 300x300x3  |    79.18 %     |
| [efficientnetv2b3_300 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b3_300/efficientnetv2b3_300_qdq_int8.onnx)    | Int8   | 300x300x3  |    79.05 %     |
| [efficientnetv2b3_300 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2b3_300/efficientnetv2b3_300_qdq_w4_88.31%_w8_11.69%_a8_100%_acc_78.11.onnx) | Int8/Int4 | 300x300x3 |  78.11 %   |
| [efficientnetv2s_384](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2s_384/efficientnetv2s_384.keras)                    | Float  | 384x384x3  |  83.52 %   |
| [efficientnetv2s_384 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2s_384/efficientnetv2s_384_qdq_int8.onnx)       | Int8   | 384x384x3  |    83.07 % |
| [efficientnetv2s_384 onnx](./Public_pretrainedmodel_public_dataset/imagenet/efficientnetv2s_384/efficientnetv2s_384_qdq_w4_95.63%_w8_4.37%_a8_100%_acc_82.25.onnx)     | Int8/Int4   | 384x384x3  |   82.25 %    |



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
(* = equal contribution) imagenet Large Scale Visual Recognition Challenge.
