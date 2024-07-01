# CNN2D_ST_HandPosture model

## **Use case** : [Hand posture recognition](../../../hand_posture/README.md)

# Model description

CNN2D_ST_HandPosture is a network topology designed by ST Teams to solve basic Hand Posture recognition use cases based on ST multi-zone Time-of-Flight sensor data. It is a convolutional neural network based model before feeding the data to the fully-connected (Dense) layer. It uses the distance and signal per spad 8x8 data. This is a very light model with very small foot prints in terms of FLASH and RAM as well as computational requirements.

We recommend to use input size (8 x 8 x 2) but this network can support greater input size.

The only input required to the model is the input shape and the number of outputs.

In this folder you will find multiple copies of the CNN2D_ST_HandPosture model pretrained on a [ST custom datasets](../../datasets/README.md).

## Network information (for 8 hand postures)


| Network Information     |  Value          |
|:-----------------------:|:---------------:|
|  Framework              | TensorFlow      |
|  Params                 | 2,752           |


## Network inputs / outputs


For an Time of Flight frame resolution of 8x8 and P classes

| Input Shape | Description |
| :----:| :-----------: |
| (N, 8, 8, 2) | Batch ( 8 x 8 x 2 ) matrix of Time of Flight values (distance, signal per spad) for a 8x8 frame in FLOAT32.|

| Output Shape | Description |
| :----:| :-----------: |
| (N, P) | Batch of per-class confidence for P classes in FLOAT32|


## Recommended platforms


| Platform | Supported | Recommended |
|:--------:|:---------:|:-----------:|
| STM32F4  |    [x]    |      [x]    |
| STM32L4  |    [x]    |      [x]    |
| STM32U5  |    [x]    |      []     |


# Performances
## Training


To train a CNN2D_ST_HandPosture model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/README.md) under the training section.

As an example, [CNN2D_ST_HandPosture_8classes_config.yaml](../CNN2D_ST_HandPosture/ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes_config.yaml) file is used to train this model on [ST_VL53L8CX_handposture_dataset dataset](../../datasets/), you can copy its content in the [user_config.yaml](../../src/user_config.yaml) file provided under the training section to reproduce the results presented below. 

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../src/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference memory footprint based on ST_VL53LxCX_handposture_dataset (see Accuracy for details on dataset)


| Model             | Format | Input Shape | Series  | Activation RAM (KiB) | Runtime RAM (KiB) | Weights Flash (KiB) | Code Flash (KiB) | Total RAM (KiB)   | Total Flash (KiB) | STM32Cube.AI version  |
|:-----------------:|:------:|:-----------:|:-------:|:--------------:|:-----------:|:-------------:|:----------:|:-----------:|:-----------:|:---------------------:|
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | STM32F4 | 1.07     | 2.08       | 10.75    | 14.37       |  3.15    | 25.12  | 9.1.0                 |
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | STM32F4 | 1.07      | 2.08        | 10.75     | 14.37        |  3.15    | 25.12   | 9.1.0                 |


### Reference inference time based on ST_VL53LxCX_handposture_dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            |   Frequency   | Inference time (ms) | STM32Cube.AI version  |
|:-----------------:|:------:|:----------:|:----------------:|:-------------:|:-------------------:|:---------------------:|
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | STM32F401 | 84 MHz       |    1.54  ms       | 9.1.0                 |
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | STM32F401 | 84 MHz       |    1.53  ms       | 9.1.0                 |

### Accuracy with ST_VL53LxCX_handposture_dataset


Dataset details: A ST custom dataset: [ST_VL53LxCX_handposture_dataset dataset](../../datasets/README.md), Number of classes: 8 [None, FlatHand, Like, Dislike, Fist, Love, BreakTime, CrossHands]. Training dataset number of frames:  3,031. Test dataset number of frames: 1146.


| Model | Format | Resolution | Accuracy |
|:-----------------:|:------:|:----------:|:----------------:|
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | 99.43 %    |
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | 97.17 %    |


## Training and code generation

*Training* and *deployment* can be performed by configuring the operation mode in the [user_config.yaml](../../src/user_config.yaml) file to `training` or `deployment`, and then launching [src/stm32ai_main.py](../../src/stm32ai_main.py) scripts.


## Demos
### Integration in a simple example

Please refer to the generic guideline [here](../../src/README.md).
