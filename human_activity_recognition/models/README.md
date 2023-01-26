# Overview of STMicroelectronics HAR Model Zoo


In the table below we provide a summary report of the Human Activity Recognition (HAR) models pre-trained on public or custom datasets.

The table below summarizes the performance of these models, as well as their memory footprints generated using STM32Cube.AI (v7.3.0) for deployment purposes.

By default, the results are provided for quantized Int8 models.

<a name="ic_models"></a>
## Human Activity Recognition (HAR) models


| Model              | Implementation   | Dataset   |  Accuracy (%)   | MACCs (M)   | Activation RAM (KiB)   | Weights Flash (KiB)   | Source
|--------------------|:----------------:|:---------:|:---------------:|:-----------:|:----------------------:|:---------------------:|:--------
| IGN wl 24 \*       | TensorFlow       | AST       |   95.51         |   0.0144    |   1.969                |       11.969          |    [link](./ign/ST_pretrainedmodel_custom_dataset/AST/ign_wl_24/ign_wl_24.h5)
| IGN wl 24          | TensorFlow       | AST       |   95.19         |   0.0139    |   1.539                |       3.109           |    [link](./ign/ST_pretrainedmodel_custom_dataset/AST/ign_wl_24/ign_wl_24_int8.tflite)
| IGN wl 48 \*       | TensorFlow       | AST       |   96.06         |   0.0524    |   4.500                |       38.968          |    [link](./ign/ST_pretrainedmodel_custom_dataset/AST/ign_wl_48/ign_wl_48.h5)
| IGN wl 48          | TensorFlow       | AST       |   96.07         |   0.0503    |   2.332                |       9.859           |    [link](./ign/ST_pretrainedmodel_custom_dataset/AST/ign_wl_48/ign_wl_48_int8.tflite)
| GMP wl 24 \*       | TensorFlow       | AST       |   94.21         |   0.0673    |   6.812                |       5.711           |    [link](./gmp/ST_pretrainedmodel_custom_dataset/AST/gmp_wl_24/gmp_wl_24.h5)
| GMP wl 24          | TensorFlow       | AST       |   94.18         |   0.0673    |   4.671                |       1.531           |    [link](./gmp/ST_pretrainedmodel_custom_dataset/AST/gmp_wl_24/gmp_wl_24_int8.tflite)
| GMP wl 48 \*       | TensorFlow       | AST       |   93.84         |   0.166     |   15.812               |       5.710           |    [link](./gmp/ST_pretrainedmodel_custom_dataset/AST/gmp_wl_48/gmp_wl_48.h5)
| GMP wl 48          | TensorFlow       | AST       |   94.14         |   0.166     |   6.922                |       1.531           |    [link](./gmp/ST_pretrainedmodel_custom_dataset/AST/gmp_wl_48/gmp_wl_48_int8.tflite)
| SVC wl 24 pct 2 \* | sklearn          | AST       |   88.41         |   0.124     |   2.289                |       60.828          |    [link](./svc/ST_pretrainedmodel_custom_dataset/AST/svc_wl_24_pct_2/svc_wl_24_pct_2.onnx)
| SVC wl 24 pct 5 \* | sklearn          | AST       |   89.94         |   0.2578    |   4.457                |       119.367         |    [link](./svc/ST_pretrainedmodel_custom_dataset/AST/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx)
| SVC wl 48 pct 2 \* | sklearn          | AST       |   84.28         |   0.0641    |   1.277                |       40261           |    [link](./svc/ST_pretrainedmodel_custom_dataset/AST/svc_wl_48_pct_2/svc_wl_48_pct_2.onnx)
| SVC wl 48 pct 5 \* | sklearn          | AST       |   87.81         |   0.1493    |   2.664                |       77.703          |    [link](./svc/ST_pretrainedmodel_custom_dataset/AST/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx)
| IGN wl 24 \*       | TensorFlow       | WISDM     |   86.38         |   0.144     |   1.968                |       11.968          |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_24/ign_wl_24.h5)
| IGN wl 24          | TensorFlow       | WISDM     |   85.62         |   0.0139    |   1.539                |       3.109           |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_24/ign_wl_24_int8.tflite)
| IGN wl 48 \*       | TensorFlow       | WISDM     |   85.04         |   0.0524    |   4.5                  |       38.968          |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_48/ign_wl_48.h5)
| IGN wl 48          | TensorFlow       | WISDM     |   85.01         |   0.0503    |   2.332                |       9.589           |    [link](./ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_48/ign_wl_48_int8.tflite)
| GMP wl 24 \*       | TensorFlow       | WISDM     |   77.95          |   0.0673    |   6.812                |       5.711           |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_24/gmp_wl_24.h5)
| GMP wl 24          | TensorFlow       | WISDM     |   76.53         |   0.0673    |   4.671                |       1.531           |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_24/gmp_wl_24_int8.tflite)
| GMP wl 48 \*       | TensorFlow       | WISDM     |   76.68         |   0.166     |   15.812               |       5.711           |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_48/gmp_wl_48.h5)
| GMP wl 48          | TensorFlow       | WISDM     |   76.57         |   0.166     |   6.922                |       1.531           |    [link](./gmp/ST_pretrainedmodel_public_dataset/WISDM/gmp_wl_48/gmp_wl_48_int8.tflite)
| SVC wl 24 pct 5 \* | sklearn          | WISDM     |   81.14         |   0.205    |   4.25               |       97.16         |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx)
| SVC wl 24 pct 10 \*| sklearn          | WISDM     |   82.72         |   0.3624    |   7.359               |       168.683         |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_10/svc_wl_24_pct_10.onnx)
| SVC wl 48 pct 5 \* | sklearn          | WISDM     |   78.36         |   0.1172    |   2.5078               |       62.718          |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx)
| SVC wl 48 pct 10 \*| sklearn          | WISDM     |   81.73         |   0.22148   |   4.542                |       109.5312        |    [link](./svc/ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_10/svc_wl_48_pct_10.onnx)


 <font size="2"> \* Float32 model results</font>
