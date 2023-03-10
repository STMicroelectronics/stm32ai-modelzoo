# CNN2D_ST_HandPosture model

## **Use case** : [Hand posture recognition](../../../hand_posture/README.md)

# Model description

CNN2D_ST_HandPosture is a network topology designed by ST Teams to solve basic Hand Posture recognition use cases based on ST multi-zone Time-of-Flight sensor data. It is a convolutional neural network based model before feeding the data to the fully-connected (Dense) layer. It uses the distance and signal per spad 8x8 data. This is a very light model with very small foot prints in terms of FLASH and RAM as well as computational requirements.

We recommend to use input size (8 x 8 x 2) but this network can support greater input size.

The only input required to the model is the input shape and the number of outputs.

In this folder you will find multiple copies of the CNN2D_ST_HandPosture model pretrained on a ST custom dataset (*ST_VL53L5CX_handposture_dataset*).

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


To train a CNN2D_ST_HandPosture model, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [CNN2D_ST_HandPosture_8classes_config.yaml](../CNN2D_ST_HandPosture/ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes_config.yaml) file is used to train this model on ST_VL53L5CX_handposture_dataset dataset, you can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below. 

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../scripts/deployment/user_config.yaml) file following the [tutorial](../../scripts/deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI (v7.3.0) configuration with enabled input / output allocated option.


### Reference memory footprint based on ST_VL53L5CX_handposture_dataset (see Accuracy for details on dataset)


| Model             | Format | Input Shape | Series  | Activation RAM | Runtime RAM | Weights Flash | Code Flash | Total RAM   | Total Flash |
|:-----------------:|:------:|:-----------:|:-------:|:--------------:|:-----------:|:-------------:|:----------:|:-----------:|:-----------:|
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | STM32F4 | 1024 B     | 2.0 KiB       | 10.75 KiB    | 15.81 KiB       |  3.0 KiB   | 26.56 KiB  |



### Reference inference time based on ST_VL53L5CX_handposture_dataset (see Accuracy for details on dataset)


| Model             | Format | Resolution | Board            |   Frequency   | Inference time (ms) |
|:-----------------:|:------:|:----------:|:----------------:|:-------------:|:-------------------:|
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | STM32F401 | 84 MHz       |    1.520  ms       |


### Accuracy with ST_VL53L5CX_handposture_dataset


Dataset details: A custom dataset and not publically available, Number of classes: 8 [None, FlatHand, Like, Dislike, Fist, Love, BreakTime, CrossHands]. Training dataset number of frames:  3,031. Test dataset number of frames: 1146.


| Model | Format | Resolution | Accuracy |
|:-----------------:|:------:|:----------:|:----------------:|
| [CNN2D_ST_HandPosture](ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5) | FLOAT32   | 8 x 8 x 2    | 96.42 %    |



## Training and code generation


- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../scripts/deployment/README.md)


## Demos
### Integration in a simple example

Please refer to the generic guideline [here](../../scripts/deployment/README.md).



# References
