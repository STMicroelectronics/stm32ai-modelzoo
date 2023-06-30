# SVC HAR model

## **Use case** : [Human activity recognition](../../../human_activity_recognition/)

# Model description

SVC are support vector classifiers for multiclass classification. These models are based on support vector machines and can be made using the sklearn framework. Just like a neural network these models can also do the human activity recognition  on the accelerometer data. In STM32Cube.AI we support the generation and deployment of these models saved as .onnx format.

For SVC models provided in this model zoo, the input is vectorized window of (wl x 3) matrix, where wl is window lenght and 3 is the number of axes (x, y and z). As a preprocessing we apply rotate and suppress the gravity filter. Then to reduce the foot print of these models we perform the dimensionality reduction using TSVD before fitting the SVC. The reason being SVC saves the representative samples of the data called support vectors which help to seperate the boundries of different classes.

The naming of the models svc_wl_24_pct_10 means that the data is windowed as 24 samples each, pct_10 means, only 10 percent data from the training data is used to optimized the model hyper-parameters and doing the training. We strongly recomment to use 10 percent or less data because using more data will increase the size of the model with very littel gain in the accuracy.

The only input required to the model building is the percentage of the optimization data controlled by `svc_train_parameters.opt_data_keep`, `model.model_type.name` and `model.input_shape` in the [user_config.yaml](../../scripts/training/user_config.yaml) file.

In this folder you will find multiple copies of the SVC model pretrained on a public dataset ([WISDM](https://www.cis.fordham.edu/wisdm/dataset.php)) and a custom dataset collected by ST (mobility_v1). The pretrained model saved as `.onnx` format using `skl2onnx` library and can be deployed or benchmarked using STM32Cube.AI.

## Network information


| Network Information     |  Value          |
|:-----------------------:|:---------------:|
|  Framework              | sklearn, skl2onnx  |

The models are quantized using post training quantization with tensorflow lite converter.


## Model inputs / outputs


For an input resolution of wl x 3 x 1 and P classes

| Input Shape | Description |
| :----:| :-----------: |
| (1, 1, 1, 72) | Single ( 1, 1, 1, wl x 3 ) vector of accelerometer values, `wl` is window lenght, for 3 axes in FLOAT32.|

| Output Shape | Description |
| :----:| :-----------: |
| (1, P) | Per-class confidence for P classes in FLOAT32|
| (1,1,1,1) | class index for the selected class in INT32|


## Recommended platforms


| Platform | Supported | Recommended |
|:----------:|:-----------:|:-----------:|
| STM32L4  |    [x]    |    [x]    |
| STM32U5  |    [x]    |    []     |


# Performances
## Training


To train an SVC model, you need to configure the [user_config.yaml](../../scripts/training/user_config.yaml) file following the [tutorial](../../scripts/training/README.md) under the training section.

As an example, [svc_wl_24_pct_5_config.yaml](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_5/svc_wl_24_pct_5_config.yaml) file is used to train this model on WISDM dataset, using 5 % of training data for optimization, you can copy its content in the [user_config.yaml](../../scripts/training/user_config.yaml) file provided under the training section to reproduce the results presented below. Note that using a higher values for  `svc_train_parameters.opt_data_keep` might result in better result but will increase the size of the model also considerably.

## Deployment

To deploy your trained model, you need to configure the [user_config.yaml](../../scripts/deployment/user_config.yaml) file following the [tutorial](../../scripts/deployment/README.md) under the deployment section.


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference memory footprint and inference time for the two datasets (see Accuracy for details on dataset)

The memory footprints, and the inference times for the various pretrained SVC models for two datasets are provided in the table below. For the inference times please note that these are computed on the **'B-U585I-IOT02A'** running at frequency value of 160 MHz.

| Model                                                                                                   | dataset    |  Format | Input Shape     | Series  |Activation RAM (KiB)|Runtime RAM (KiB)|Weights Flash (KiB)|Code Flash (KiB)|Total RAM (KiB)|Total Flash (KiB)|Inference Time (ms)|STM32Cube.AI version |
|:-------------------------------------------------------------------------------------------------------:|:----------:|:-------:|:---------------:|:-------:|:------------------:|:---------------:|:-----------------:|:--------------:|:-------------:|:---------------:|:-----------------:|:-------------------:|
| [SVC wl 24 pct 5](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx)       | WISDM      | FLOAT32 | 1 x 1 x 1 x 72  | STM32U5 | 4.25               | 1.74            | 97.17             | 16.82          |  5.99         | 113.99          | 2.546              | 8.1.0              |
| [SVC wl 24 pct 10](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_10/svc_wl_24_pct_10.onnx)    | WISDM      | FLOAT32 | 1 x 1 x 1 x 72  | STM32U5 | 7.36               | 1.74            | 168.68            | 16.80          |  9.10         | 185.49          | 4.604              | 8.1.0              |
| [SVC wl 48 pct 5](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx)       | WISDM      | FLOAT32 | 1 x 1 x 1 x 144 | STM32U5 | 2.8                | 1.74            | 69.37             | 16.79          |  4.54         | 86.16           | 1.724              | 8.1.0              |
| [SVC wl 48 pct 10](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_10/svc_wl_48_pct_10.onnx)    | WISDM      | FLOAT32 | 1 x 1 x 1 x 144 | STM32U5 | 4.62               | 1.74            | 111.42            | 16.80          |  6.37         | 128.22          | 2.851              | 8.1.0              |
| [SVC wl 24 pct 2](./ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_24_pct_2/svc_wl_24_pct_2.onnx) | mobility_v1| FLOAT32 | 1 x 1 x 1 x 72  | STM32U5 | 2.29               | 1.74            | 60.83             | 16.79          |  4.03         | 77.61           | 1.424              | 8.1.0              |
| [SVC wl 24 pct 5](./ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx) | mobility_v1| FLOAT32 | 1 x 1 x 1 x 72  | STM32U5 | 4.46               | 1.74            | 119.37            | 16.80          |  6.20         | 136.16          | 2.861              | 8.1.0              |
| [SVC wl 48 pct 2](./ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_48_pct_2/svc_wl_48_pct_2.onnx) | mobility_v1| FLOAT32 | 1 x 1 x 1 x 144 | STM32U5 | 1.28               | 1.74            | 40.26             | 16.79          |  3.0é         | 57.05           | 0.852              | 8.1.0              |
| [SVC wl 48 pct 5](./ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx) | mobility_v1| FLOAT32 | 1 x 1 x 1 x 144 | STM32U5 | 2.66               | 1.74            | 77.70             | 16.79          |  4.4&         | 94.09           | 1.748              | 8.1.0              |



### Accuracy with mobility_v1 dataset


Dataset details: A custom dataset and not publically available, Number of classes: 5 [Stationary, Walking, Jogging, Biking, Driving]. **(We kept only 4, [Stationary, Walking, Jogging, Biking]) and removed Driving**, Number of input frames:  81,151 (for wl = 24), and 40,575 for (wl = 48).

| Model                                                                                         |  Format  | Resolution       |   Accuracy    |
|:---------------------------------------------------------------------------------------------:|:--------:|:----------------:|:-------------:|
| [SVC wl 24 pct 2](ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_24_pct_2/svc_wl_24_pct_2.onnx) | FLOAT32  | 1 x 1 x 1 x 72   | 88.41         |
| [SVC wl 24 pct 5](ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx) | FLOAT32  | 1 x 1 x 1 x 72   | 89.94         |
| [SVC wl 48 pct 2](ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_48_pct_2/svc_wl_48_pct_2.onnx) | FLOAT32  | 1 x 1 x 1 x 144  | 84.28         |
| [SVC wl 48 pct 5](ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx) | FLOAT32  | 1 x 1 x 1 x 144  | 87.81         |


Confusion matrix for [SVC wl 24 pct 5](ST_pretrainedmodel_custom_dataset/mobility_v1/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx) for mobility_v1 dataset is given below.

![plot](../../scripts/training/doc/img/mobility_v1/svc_wl_24_pct_5_confusion_matrix.png)

### Accuracy with WISDM dataset


Dataset details: [link](([WISDM]("https://www.cis.fordham.edu/wisdm/dataset.php"))) , License [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) , Quotation[[1]](#1) , **Number of classes: 4 (we are combining [Upstairs and Downstairs into Stairs] and [Standing and Sitting into Stationary])**, Number of samples: 45,579 (at wl = 24), and 22,880 (at wl = 48).

| Model                                                                                                |  Format  | Resolution       |   Accuracy    |
|:----------------------------------------------------------------------------------------------------:|:--------:|:----------------:|:-------------:|
| [SVC wl 24 pct 2](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_5/svc_wl_24_pct_5.onnx)    | FLOAT32  | 1 x 1 x 1 x 72   | 81.14         |
| [SVC wl 24 pct 10](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_24_pct_10/svc_wl_24_pct_10.onnx) | FLOAT32  | 1 x 1 x 1 x 72   | 82.72         |
| [SVC wl 48 pct 5](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_5/svc_wl_48_pct_5.onnx)    | FLOAT32  | 1 x 1 x 1 x 144  | 78.36         |
| [SVC wl 48 pct 10](./ST_pretrainedmodel_public_dataset/WISDM/svc_wl_48_pct_10/svc_wl_48_pct_10.onnx) | FLOAT32  | 1 x 1 x 1 x 144  | 81.73         |


## Training and code generation


- Link to training script: [here](../../scripts/training/README.md)
- Link to STM32Cube.AI generation script: [here](../../scripts/deployment/README.md)


## Demos
### Integration in a simple example

Please refer to the generic guideline [here](../../scripts/deployment/README.md).



# References

<a id="1">[1]</a>
“WISDM : Human activity recognition datasets". [Online]. Available: "https://www.cis.fordham.edu/wisdm/dataset.php".