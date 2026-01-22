# st_cnn2d_handposture model

## **Use case** : `Hand posture recognition`

# Model description

CNN2D_ST_HandPosture is a network topology designed by ST Teams to solve basic Hand Posture recognition use cases based on ST multi-zone Time-of-Flight sensor data. It is a convolutional neural network based model before feeding the data to the fully-connected (Dense) layer. It uses the distance and signal per spad 8x8 data. This is a very light model with very small foot prints in terms of FLASH and RAM as well as computational requirements.

We recommend to use input size (8 x 8 x 2) but this network can support greater input size.

The only input required to the model is the input shape and the number of outputs.

In this folder you will find multiple copies of the CNN2D_ST_HandPosture model pretrained on a ST custom datasets - Please refer to th [stm32ai-modelzoo-services](https://github.com/STMicroelectronics/stm32ai-modelzoo-services) GitHub for more informations

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

## Metrics

Measures are done with default STEdge AI Dev Cloud configuration with enabled input / output allocated option.


### Reference memory footprint based on ST_VL53LxCX_handposture_dataset (see Accuracy for details on dataset)

| Model                                                                                                                                                    | Format | Input Shape  | Series  | Activation RAM (KiB) | Runtime RAM (KiB) | Weights Flash (KiB) | Code Flash (KiB) | Total RAM (KiB)   | Total Flash (KiB) | STEdge AI Core version  |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:------:|:-----------:|:-------:|:--------------:|:-----------:|:-------------:|:----------:|:-----------:|:-----------:|:---------------------:|
| [st_cnn2d_handposture](./ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/st_cnn2d_handposture_8classes/st_cnn2d_handposture_8classes.keras) | FLOAT32   | 8 x 8 x 2    | STM32F4 | 1.63     | 0.28       | 10.75    | 6.16       |  1.91    | 16.19  | 3.0.0                 |


### Reference inference time based on ST_VL53LxCX_handposture_dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            |   Frequency   | Inference time (ms) | STEdge AI Core version  |
|:-----------------:|:------:|:----------:|:----------------:|:-------------:|:-------------------:|:---------------------:|
| [st_cnn2d_handposture](./ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/st_cnn2d_handposture_8classes/st_cnn2d_handposture_8classes.keras) | FLOAT32   | 8 x 8 x 2    | STM32F401 | 84 MHz       |    1.46  ms       | 3.0.0                 |

### Accuracy with ST_VL53LxCX_handposture_dataset

Number of classes: 8 [None, FlatHand, Like, Dislike, Fist, Love, BreakTime, CrossHands]. Training dataset number of frames:  3,031. Test dataset number of frames: 1146.


| Model                                                                                                                                                    | Dataset                         |Format     | Resolution | Accuracy (%) |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------:|:-------------------------------:|:---------:|:----------:|:------------:|
| [st_cnn2d_handposture](./ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/st_cnn2d_handposture_8classes/st_cnn2d_handposture_8classes.keras) | ST_VL53L8CX_handposture_dataset | FLOAT32   | 8 x 8 x 2  | 98.47        |
| [st_cnn2d_handposture](./ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/st_cnn2d_handposture_8classes/st_cnn2d_handposture_8classes.keras) | ST_VL53L5CX_handposture_dataset | FLOAT32   | 8 x 8 x 2  | 99.21        |


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)

