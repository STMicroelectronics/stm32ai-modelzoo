# Overview of ST multi-zone Time-of-Flight sensors hand posture recognition STM32 model zoo

The STM32 model zoo includes several models for hand posture recognition use cases pre-trained on custom datasets. Under each model directory, you can find the following model categories:

- `ST_pretrainedmodel_custom_dataset` contains different hand posture models trained on ST custom datasets using our [training scripts](../scripts/training/README.md). 

<a name="ic_models"></a>
## Hand posture recognition models

The table below summarizes the performance of the models, as well as their memory footprints generated using STM32Cube.AI (v7.3.0) for deployment purposes.

By default, the results are provided for float models.

| Models                          | Implementation | Dataset                         | Input Resolution | Top 1 Accuracy (%) | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | Source                                                                                                                         |
|---------------------------------|----------------|---------------------------------|------------------|--------------------|--------------|----------------------|---------------------|--------------------------------------------------------------------------------------------------------------------------------|
| CNN2D_ST_HandPosture 8 postures | TensorFlow     | ST_VL53L5CX_handposture_dataset | 8x8x2            | 96.42%             | 0.009        | 1.0                  | 10.75               | [link](CNN2D_ST_HandPosture/ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5)|

