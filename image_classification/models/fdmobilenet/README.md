# Fd-MobileNet quantized

## **Use case** : [Image classification](../README.md)

# Model description
Fd-MobileNet stands for Fast-downsampling MobileNet. It was initially introduced in this [paper](https://arxiv.org/pdf/1802.03750.pdf).
This family of networks, inspired from Mobilenet, provides a good accuracy on various image classification tasks for very limited computational budgets.
Thus it is an interesting solution for deep learning at the edge.
As stated by the authors, the key idea is to apply a fast downsampling strategy to MobileNet framework with only half the layers of the original MobileNet. This design remarkably reduces the computational cost as well as the inference time.

The hyperparameter 'alpha' controls the width of the network, also denoted as width multiplier. It proportionally adjusts each layer width.
Authorized values for 'alpha' are 0.25, 0.5, 0.75, 1.0.
The model is quantized in int8 using Tensorflow Lite converter.

Performances of a ST custom model derived from Fd-MobileNet is also proposed below.

## Network information
| Network Information     | Value                                |
|-------------------------|--------------------------------------|
|  Framework              | TensorFlow Lite                      |
|  Params alpha=0.25      | 125477                               |
|  Quantization           | int8                                 |
|  Paper                  | https://arxiv.org/pdf/1802.03750.pdf |

The models are quantized using tensorflow lite converter.

## Network inputs / outputs
For an image resolution of NxM and P classes and 0.25 alpha parameter :

| Input Shape   | Description                                              |
|---------------|----------------------------------------------------------|
| (1, N, M, 3)  | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape  | Description                                              |
|---------------|----------------------------------------------------------|
| (1, P)        | Per-class confidence for P classes                       |


## Recommended platform
| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | [x]       | []          |
| STM32U5  | [x]       | []          |
| STM32H7  | [x]       | [x]         |
| STM32MP1 | [x]       | []          |

---
# Performances
## Training
To train a FdMobileNet 0.25 model from scratch on your own dataset, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [fdmobilenet_0.25_224_config.yaml](./ST_pretrainedmodel_public_dataset/flowers/fdmobilenet_0.25_224/fdmobilenet_0.25_224_config.yaml) file is used to train this model on flowers dataset, you can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below.

## Deployment
To deploy your trained model, you need to configure the [user_config.yaml](../../scripts/deployment/user_config.yaml) file following the [tutorial](../../scripts/deployment/README.md) under the deployment section.

## Metrics
Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference MCU memory footprints based on Flowers dataset (see Accuracy for details on dataset)
| Model             | Format | Resolution   | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM | Total Flash |
|-------------------|--------|--------------|---------|----------------|-------------|---------------|------------|-----------|-------------|
| FdMobileNet 0.25  | Int8   | 224x224x3    | STM32H7 | 152 KiB        | 16 KiB      | 129 KiB       | 61 KiB     | 168 KiB   | 190 KiB     |
| ST FdMobileNet v1 | Int8   | 224x224x3    | STM32H7 | 207 KiB        | 16 KiB      | 145 KiB       | 63 KiB     | 223 KiB   | 208 KiB     |
| FdMobileNet 0.25  | Int8   | 128x128x3    | STM32H7 | 51 KiB         | 16 KiB      | 129 KiB       | 61 KiB     | 67 KiB    | 190 KiB     |
| ST FdMobileNet v1 | Int8   | 128x128x3    | STM32H7 | 71 KiB         | 16 KiB      | 145 KiB       | 63 KiB     | 87 KiB    | 208 KiB     |


### Reference inference time based on Flowers dataset (see Accuracy for details on dataset)
| Model             | Format | Resolution   | Board            | Execution Engine | Frequency     | Inference time (ms) |
|-------------------|--------|--------------|------------------|------------------|---------------|---------------------|
| FdMobileNet 0.25  | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 63.19 ms            |
| ST FdMobileNet v1 | Int8   | 224x224x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 117.3 ms            |
| FdMobileNet 0.25  | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 21.97 ms            |
| ST FdMobileNet v1 | Int8   | 128x128x3    | STM32H747I-DISCO | 1 CPU            | 400 MHz       | 39.5 ms             |
| FdMobileNet 0.25  | Int8   | 224x224x3    | STM32H769I-DISCO | 1 CPU            | 216 MHz       | 112.4 ms            |
| ST FdMobileNet v1 | Int8   | 224x224x3    | STM32H769I-DISCO | 1 CPU            | 216 MHz       | 204.3 ms            |
| FdMobileNet 0.25  | Int8   | 128x128x3    | STM32H769I-DISCO | 1 CPU            | 216 MHz       | 39.47 ms            |
| ST FdMobileNet v1 | Int8   | 128x128x3    | STM32H769I-DISCO | 1 CPU            | 216 MHz       | 69.49 ms            |
| FdMobileNet 0.25  | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 23.55 ms **         |
| ST FdMobileNet v1 | Int8   | 224x224x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 39.48 ms **         |
| FdMobileNet 0.25  | Int8   | 128x128x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 8.53 ms **          |
| ST FdMobileNet v1 | Int8   | 128x128x3    | STM32MP157F-DK2  | 2 CPU            | 800 MHz       | 13.42 ms **         |

** The results on STM32MP157F-DK2 are obtained using TensorFlowLite 2.11.0

### Accuracy with Flowers dataset
Dataset details: http://download.tensorflow.org/example_images/flower_photos.tgz , License CC - BY 2.0
Number of classes: 5, 3670 files

| Model             | Format | Resolution   | Top 1 Accuracy |
|-------------------|--------|--------------|----------------|
| FdMobileNet 0.25  | Float  | 224x224x3    | 0.8719         |
| FdMobileNet 0.25  | Int8   | 224x224x3    | 0.8597         |
| ST FdMobileNet v1 | Float  | 224x224x3    | 0.8719         |
| ST FdMobileNet v1 | Int8   | 224x224x3    | 0.8692         |
| FdMobileNet 0.25  | Float  | 128x128x3    | 0.8433         |
| FdMobileNet 0.25  | Int8   | 128x128x3    | 0.842          |
| ST FdMobileNet v1 | Float  | 128x128x3    | 0.8501         |
| ST FdMobileNet v1 | Int8   | 128x128x3    | 0.8474         |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=200' and ReduceLROnPlateau 'factor=0.5', 'patience=60'.

### Accuracy with Plant dataset
Dataset details: https://data.mendeley.com/datasets/tywbtsjrjv/1 , License CC0 1.0
Number of classes: 39, number of files: 55448

| Model             | Format | Resolution   | Top 1 Accuracy |
|-------------------|--------|--------------|----------------|
| FdMobileNet 0.25  | Float  | 224x224x3    | 0.9981         |
| FdMobileNet 0.25  | Int8   | 224x224x3    | 0.9959         |
| ST FdMobileNet v1 | Float  | 224x224x3    | 0.9983         |
| ST FdMobileNet v1 | Int8   | 224x224x3    | 0.9979         |
| FdMobileNet 0.25  | Float  | 128x128x3    | 0.9961         |
| FdMobileNet 0.25  | Int8   | 128x128x3    | 0.9835         |
| ST FdMobileNet v1 | Float  | 128x128x3    | 0.9967         |
| ST FdMobileNet v1 | Int8   | 128x128x3    | 0.9608         |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=200' and ReduceLROnPlateau 'factor=0.5', 'patience=40'.

### Accuracy with Food-101 dataset
Dataset details: https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/,
Number of classes: 101, number of files: 101000

| Model             | Format | Resolution   | Top 1 Accuracy |
|-------------------|--------|--------------|----------------|
| FdMobileNet 0.25  | Float  | 224x224x3    | 0.5761         |
| FdMobileNet 0.25  | Int8   | 224x224x3    | 0.5636         |
| ST FdMobileNet v1 | Float  | 224x224x3    | 0.6477         |
| ST FdMobileNet v1 | Int8   | 224x224x3    | 0.636          |
| FdMobileNet 0.25  | Float  | 128x128x3    | 0.4597         |
| FdMobileNet 0.25  | Int8   | 128x128x3    | 0.4476         |
| ST FdMobileNet v1 | Float  | 128x128x3    | 0.5318         |
| ST FdMobileNet v1 | Int8   | 128x128x3    | 0.5248         |

Please note that these accuracies are obtained after fine-tuning ReduceLROnPlateau and EarlyStopping parameters in [callbacks.py](../../scripts/utils/callbacks.py).
In particular, EarlyStopping 'patience=100' and ReduceLROnPlateau 'factor=0.5', 'patience=20'.

## Retraining and code generation

- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../scripts/deployment/README.md)

## Demos
### Integration in a simple example

Please refer to the generic guideline [here](../../scripts/deployment/README.md).


# References

<a id="1">[1]</a>
"Tf_flowers : tensorflow datasets," TensorFlow. [Online]. Available: https://www.tensorflow.org/datasets/catalog/tf_flowers.

<a id="2">[2]</a>
J, ARUN PANDIAN; GOPAL, GEETHARAMANI (2019), "Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network", Mendeley Data, V1, doi: 10.17632/tywbtsjrjv.1

<a id="3">[3]</a>
L. Bossard, M. Guillaumin, and L. Van Gool, "Food-101 -- Mining Discriminative Components with Random Forests." European Conference on Computer Vision, 2014.
