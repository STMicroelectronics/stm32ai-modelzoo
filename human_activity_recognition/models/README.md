# Overview of human activity recognition STM32 model zoo


The STM32 model zoo includes several models for the human activity recognition (HAR) use case pre-trained on custom and public datasets. Under each model directory, you can find the following model categories:

- `ST_pretrainedmodel_custom_dataset` contains different human activity recognition models trained on ST custom datasets using our [training scripts](../scripts/training/README.md). 
- `ST_pretrainedmodel_public_dataset` contains different human activity recognition models trained on various public datasets following the [training section](../scripts/training/README.md).




<a name="ic_models"></a>
## Human activity recognition STM32 models

The table below summarizes the performance of the models, as well as their memory footprints generated using STM32Cube.AI for deployment purposes.

By default, the results are provided for quantized Int8 models.


| Models              | Implementation  | Dataset           |  Accuracy (%)   | MACCs (M)   | Activation RAM (KiB)   | Weights Flash (KiB)   | STM32Cube.AI version  | Source
|--------------------|:----------------:|:-----------------:|:---------------:|:-----------:|:----------------------:|:---------------------:|:---------------------:|:--------
| IGN wl 24 \*       | TensorFlow       | mobility_v1       |   95.51         |   0.014    |   2.81                  |       11.97          | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_24/ign_wl_24.h5)
| IGN wl 24          | TensorFlow       | mobility_v1       |   95.19         |   0.014    |   1.63                  |       3.11           | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_24/ign_wl_24_int8.tflite)
| IGN wl 48 \*       | TensorFlow       | mobility_v1       |   96.06         |   0.052    |   9.84                  |       38.97          | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_48/ign_wl_48.h5)
| IGN wl 48          | TensorFlow       | mobility_v1       |   96.07         |   0.050    |   2.33                  |       9.86           | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_48/ign_wl_48_int8.tflite)
| GMP wl 24 \*       | TensorFlow       | mobility_v1       |   94.21         |   0.067    |   4.03                  |       5.70           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_custom_dataset/mobility_v1/gmp_wl_24/gmp_wl_24.h5)
| GMP wl 24          | TensorFlow       | mobility_v1       |   94.18         |   0.067    |   4.73                  |       1.53           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_custom_dataset/mobility_v1/gmp_wl_24/gmp_wl_24_int8.tflite)
| GMP wl 48 \*       | TensorFlow       | mobility_v1       |   93.84         |   0.166     |  8.81               |       5.70           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_custom_dataset/mobility_v1/gmp_wl_48/gmp_wl_48.h5)
| GMP wl 48          | TensorFlow       | mobility_v1       |   94.14         |   0.167     |   6.98                |       1.53           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_custom_dataset/mobility_v1/gmp_wl_48/gmp_wl_48_int8.tflite)
| SVC wl 24 pct 2 \* | sklearn          | mobility_v1       |   88.41         |   0.125     |   2.29                |       60.83          | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_24_pct_2/svc_wl_24_pct_2.onnx)
| SVC wl 24 pct 5 \* | sklearn          | mobility_v1       |   89.94         |   0.258     |   4.46                |       119.37         | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx)
| SVC wl 48 pct 2 \* | sklearn          | mobility_v1       |   84.28         |   0.064     |   1.28                |       40.26           | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_48_pct_2/svc_wl_48_pct_2.onnx)
| SVC wl 48 pct 5 \* | sklearn          | mobility_v1       |   87.81         |   0.149     |   2.66                |       77.70          | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx)
| IGN wl 24 \*       | TensorFlow       | WISDM             |   86.38         |   0.014     |   2.81                |       11.97          | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_24/ign_wl_24.h5)
| IGN wl 24          | TensorFlow       | WISDM             |   85.62         |   0.014     |   1.63                |       3.11           | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_24/ign_wl_24_int8.tflite)
| IGN wl 48 \*       | TensorFlow       | WISDM             |   85.04         |   0.052     |   9.84                 |       38.97          | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_48/ign_wl_48.h5)
| IGN wl 48          | TensorFlow       | WISDM             |   85.01         |   0.050     |   2.33                |       9.86           | 8.1.0                 |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_48/ign_wl_48_int8.tflite)
| GMP wl 24 \*       | TensorFlow       | WISDM             |   77.95         |   0.067     |   4.03                |       5.70           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_24/gmp_wl_24.h5)
| GMP wl 24          | TensorFlow       | WISDM             |   76.53         |   0.067     |   4.73                |       1.53           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_24/gmp_wl_24_int8.tflite)
| GMP wl 48 \*       | TensorFlow       | WISDM             |   76.68         |   0.166     |   8.81               |       5.70           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_48/gmp_wl_48.h5)
| GMP wl 48          | TensorFlow       | WISDM             |   76.57         |   0.167     |   6.98                |       1.53           | 8.1.0                 |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_48/gmp_wl_48_int8.tflite)
| SVC wl 24 pct 5 \* | sklearn          | WISDM             |   81.14         |   0.205     |   4.25                 |       97.17           | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx)
| SVC wl 24 pct 10 \*| sklearn          | WISDM             |   82.72         |   0.364     |   7.36                |       168.68         | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_10/svc_wl_24_pct_10.onnx)
| SVC wl 48 pct 5 \* | sklearn          | WISDM             |   78.36         |   0.132     |   2.8               |       69.37          | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx)
| SVC wl 48 pct 10 \*| sklearn          | WISDM             |   81.73         |   0.226     |   4.62                |       111.42        | 8.1.0                 |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_10/svc_wl_48_pct_10.onnx)


\* Float32 model results
