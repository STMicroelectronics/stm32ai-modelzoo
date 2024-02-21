# Overview of human activity recognition STM32 model zoo


The STM32 model zoo includes several models for the human activity recognition (HAR) use case pre-trained on custom and public datasets. Under each model directory, you can find the following model categories:

- `ST_pretrainedmodel_custom_dataset` directory contains different human activity recognition models trained on ST custom datasets. 
- `ST_pretrainedmodel_public_dataset` directory contains different human activity recognition models trained on public datasets.




<a name="har_models"></a>
## Human activity recognition STM32 models

The table below summarizes the performance of the models, as well as their memory footprints generated using STM32Cube.AI v8.1.0, for deployment purposes.

By default all the results are for the FLOAT32 resolution (all the inputs, outputs, activations and weights are of FLOAT32 type).
| Models        | Implementation   | Dataset           |  Accuracy (%)   | MACCs (M)   | Activation RAM (KiB)    | Weights Flash (KiB)   | Source
|---------------|:----------------:|:-----------------:|:---------------:|:-----------:|:-----------------------:|:---------------------:|:--------
| IGN wl 24     | TensorFlow       | mobility_v1       |   94.64         |   0.014     |   2.81                  |       11.97           |    [link](./ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_24/ign_wl_24.h5)
| IGN wl 48     | TensorFlow       | mobility_v1       |   95.01         |   0.052     |   9.84                  |       38.97           |    [link](./ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_48/ign_wl_48.h5)
| GMP wl 24     | TensorFlow       | mobility_v1       |   94.08         |   0.067     |   4.03                  |       5.70            |     [link](./gmp/ST_pretrainedmodel_custom_dataset/mobility_v1/gmp_wl_24/gmp_wl_24.h5)
| GMP wl 48     | TensorFlow       | mobility_v1       |   93.23         |   0.166     |   8.81                  |       5.70            |    [link](./gmp/ST_pretrainedmodel_custom_dataset/mobility_v1/gmp_wl_48/gmp_wl_48.h5)
| IGN wl 24     | TensorFlow       | WISDM             |   91.70         |   0.014     |   2.81                  |       11.97           |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_24/ign_wl_24.h5)
| IGN wl 48     | TensorFlow       | WISDM             |   93.67         |   0.052     |   9.84                  |       38.97           |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_48/ign_wl_48.h5)
| GMP wl 24     | TensorFlow       | WISDM             |   84.49         |   0.067     |   4.03                  |       5.70            |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_24/gmp_wl_24.h5)
| GMP wl 48     | TensorFlow       | WISDM             |   87.05         |   0.166     |   8.81                  |       5.70            |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_48/gmp_wl_48.h5)


