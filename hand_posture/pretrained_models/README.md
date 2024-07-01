# Overview of ST multi-zone Time-of-Flight sensors hand posture recognition STM32 model zoo

The STM32 model zoo includes several models for hand posture recognition use cases pre-trained on custom datasets. Under each model directory, you can find the following model categories:

- `ST_pretrainedmodel_custom_dataset` contains different hand posture models trained on ST custom datasets using our [training scripts](../src/config_file_examples/training_config.yaml). 

<a name="ic_models"></a>
## Hand posture recognition models

The table below summarizes the performance of the models, as well as their memory footprints generated using STM32Cube.AI for deployment purposes.

By default, the results are provided for float models.

Below sections contain detailed information on models memory usage and accuracies (click on the arrows to expand):
<details><summary>ST CNN2D Handposture</summary>

| Models                                   | Implementation | Dataset                         | Input Resolution | Top 1 Accuracy (%) | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version  | Source                                                                                                                         |
|------------------------------------------|----------------|---------------------------------|------------------|--------------------|--------------|----------------------|---------------------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------|
| CNN2D_ST_HandPosture VL53L8CX 8 postures | TensorFlow     | ST_VL53L8CX_handposture_dataset | 8x8x2            | 99.43%             | 0.009        | 1.07                  | 10.75               | 9.1.0                 | [link](CNN2D_ST_HandPosture/ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5)|
| CNN2D_ST_HandPosture VL53L5CX 8 postures | TensorFlow     | ST_VL53L5CX_handposture_dataset | 8x8x2            | 97.17%             | 0.009        | 1.07                  | 10.75               | 9.1.0                 | [link](CNN2D_ST_HandPosture/ST_pretrainedmodel_custom_dataset/ST_VL53L5CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5)|

</details>

You can get inference time information for each models following links below:
- [CNN2D_ST_HandPosture](./CNN2D_ST_HandPosture/README.md)
