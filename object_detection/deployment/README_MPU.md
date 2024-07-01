# Object detection STM32MPU Model Deployment

This tutorial demonstrates how to deploy a pre-trained object detection model built with TensorFlow Lite (.tflite) or (.ONNX) on an STM32MPU board using X-LINUX-AI.

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Before You Start</b></a></summary><a id="1"></a>
<ul><details open><summary><a href="#1-1">1.1 Hardware Setup</a></summary><a id="1-1"></a>

The [X-LINUX-AI application code](../../X-LINUX-AI_application_code/object_detection/README.md) runs on a hardware setup consisting of an STM32 microprocessor board connected to a camera module board or a USB camera. This version supports the following boards only:

- [STM32MP135F-DK](https://www.st.com/en/evaluation-tools/stm32mp135f-dk) discovery board
- [MB1897]  GC2145 GalaxyCore camera module
- [STM32MP157F-DK2](https://www.st.com/en/evaluation-tools/stm32mp157f-dk2) discovery boards
- [USB camera] no built-in camera
- [STM32MP257F-EV1](https://www.st.com/en/evaluation-tools/stm32mp257f-ev1) discovery board
- [MB1864B]  Sony IMX335 5Mpx camera module

</details></ul>
<ul><details open><summary><a href="#1-2">1.2 Software Requirements</a></summary><a id="1-2"></a>

[X-LINUX-AI](https://www.st.com/en/embedded-software/x-linux-ai.html) expansion package for OpenSTLinux version `v5.1.0` is required on the target board to be able to use the following object detection deployment application.

To install X-LINUX-AI on your target device please follow the dedicated wiki page :

- X-LINUX-AI expansion package : https://wiki.st.com/stm32mpu/wiki/Category:X-LINUX-AI_expansion_package

To facilitate the deployment and avoid tools installation the MPU deployment is based on [ST Edge AI developer cloud](https://stedgeai-dc.st.com/home) to access the ST Edge AI functionalities without installing the software. This requires internet connection and making a free account.

You can use the deployment service by using a model zoo pre-trained model from the [STM32 model zoo](../pretrained_models/README.md) or your own object detection model. Please refer to the YAML file [deployment_mpu_config.yaml](../src/config_file_examples/deployment_mpu_config.yaml), which is a ready YAML file with all the necessary sections ready to be filled, or you can update the [user_config.yaml](../src/user_config.yaml) to use it.

As an example, we will show how to deploy the model [ssd_mobilenet_v2_fpnlite_10_256_int8_pt.tflite](../pretrained_models/ssd_mobilenet_v2_fpnlite/Public_pretrainedmodel_public_dataset/coco_2017/ssd_mobilenet_v2_fpnlite_10_256/ssd_mobilenet_v2_fpnlite_10_256_int8_pt.tflite) pre-trained on the Coco 2017 (80 classes)dataset using the necessary parameters provided in [ssd_mobilenet_v2_fpnlite_10_256_config.yaml](../pretrained_models/ssd_mobilenet_v2_fpnlite/Public_pretrainedmodel_public_dataset/coco_2017/ssd_mobilenet_v2_fpnlite_10_256/ssd_mobilenet_v2_fpnlite_10_256_config.yaml).

</details></ul>
</details>
<details open><summary><a href="#2"><b>2. Yaml Configuration</b></a></summary><a id="2"></a>

<ul><details open><summary><a href="#2-1">2.1 Setting the Model and the Operation Mode</a></summary><a id="2-1"></a>

The first section of the configuration file is the `general` section that provides information about your project and the path to the model you want to deploy. The `operation_mode` attribute should be set to `deployment` as follows:

```yaml
general:
   model_path: ../pretrained_models/ssd_mobilenet_v2_fpnlite/Public_pretrainedmodel_public_dataset/coco_2017/ssd_mobilenet_v2_fpnlite_10_256/ssd_mobilenet_v2_fpnlite_10_256_int8_pt.tflite
   model_type: ssd_mobilenet_v2_fpnlite
operation_mode: deployment
```

In the `general` section, users must provide the path to their model file using the `model_path` attribute. This can be either a Keras model file with a `.h5` filename extension (float model), a TensorFlow Lite model file with a `.tflite` filename extension (quantized model), or an ONNX model with a `.onnx` filename extension.
In this example, the path to the MobileNet V2 model is provided in the `model_path` parameter. Please check out the [STM32 model zoo](../pretrained_models/README.md) for more object detection models.

You must copy the `preprocessing` section to your own configuration file, to ensure you have the correct preprocessing parameters.

</details></ul>
<ul><details open><summary><a href="#2-2">2.2 Dataset Configuration</a></summary><a id="2-2"></a>
<ul><details open><summary><a href="#2-2-1">2.2.1 Dataset info</a></summary><a id="2-2-1"></a>

Configure the **dataset** section in the YAML file as follows:

The `class_names` attribute specifies the classes that the model is trained on. This information could be provided in the YAML file directly, or in the case of MPU if the `label_file_path` is not provided in deployment section the `class_names` can be automatically recovered.

It avoid to list 80 classes for the example of Coco 2017 dataset used for this model.

</details></ul>
<ul><details open><summary><a href="#2-2-2">2.2.2 Preprocessing info</a></summary><a id="2-2-2"></a>

To run inference in the python application, we need to apply on the input data the same preprocessing used when training the model.

To do so, you need to specify the **preprocessing** configuration in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
preprocessing:
  resizing:
    interpolation: bilinear
    aspect_ratio: fit
  color_mode: rgb
```

- `resizing` - **bilinear**, only supported option for *application python code*.
- `aspect_ratio` - **fit**, only supported for now. With *fit* aspect ratio may not be preserved.
- `color_mode` -  **rgb**, only supported for now.

</details></ul>
</details></ul>
<ul><details open><summary><a href="#2-3">2.3 Deployment parameters</a></summary><a id="2-3"></a>

To deploy the model in **STM32MPU** boards, you can use either TensorFlow Lite or ONNX models on MP1, the computation will be done
on CPU. For MP2 the TensorFlow Lite or ONNX model will be automatically converted to NBG model using *STM32 developer cloud* functionalities.

The application code and the model will be deployed on the board through SSH.

These steps will be done automatically by configuring the **tools** and **deployment** sections in the YAML file as the following:

```yaml
tools:
   stedgeai:
      version: 9.1.0
      optimization: balanced
      on_cloud: True
      path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
   path_to_cubeIDE: C:/ST/STM32CubeIDE_1.15.0/STM32CubeIDE/stm32cubeide.exe

deployment:
   c_project_path: ../../X-LINUX-AI_application_code/object_detection/
   label_file_path: ../../X-LINUX-AI_application_code/object_detection/Resources/labels_coco_dataset_80.txt
   board_deploy_path: /usr/local/object-detection
   verbosity: 1
   hardware_setup:
      serie: STM32MP2
      board: STM32MP257F-EV1
      ip_address: X.X.X.X
```

where:
- `on_cloud` - *Bool* enable usage of STM32 developer cloud
- `c_project_path` - *Path* to [X-LINUX-AI application code](../../X-LINUX-AI_application_code/object_detection/README.md) project.
- `label_file_path` - *Path* to Dataset labels file path.
- `board_deploy_path` - *Path* to the on target application deployment directory
- `serie` - **STM32MP2** or **STM32MP1**, only supported options for *X-LINUX-AI application code*.
- `board` - **STM32MP257F-EV1** or **STM32MP157F-DK2** or **STM32MP135F-DK**, see the [README](../../X-LINUX-AI_application_code/object_detection/README.md) for more details.
- `ip_address` - *String* IP address of the board used for deployment

</details></ul>
<ul><details open><summary><a href="#2-4">2.4 Hydra and MLflow settings</a></summary><a id="2-4"></a>

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment directories. With the YAML code below, every time you run the Model Zoo, an experiment directory is created that contains all the directories and files created during the run. The names of experiment directories are all unique as they are based on the date and time of the run.

```yaml
hydra:
   run:
      dir: ./experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown below:

```yaml
mlflow:
   uri: ./experiments_outputs/mlruns
```

</details></ul>
</details>
<details open><summary><a href="#3"><b>3. Deploy pretrained model on STM32MPU board</b></a></summary><a id="3"></a>

First you need to connect the camera board or USB camera to the *STM32MPU* board, then connect the board to your network using ethernet cable or WIFI and recover the board IP using netdata tool on the on the home screen.

If you chose to modify the [user_config.yaml](../src/user_config.yaml) you can deploy the model by running the following command from the **src/** folder to deploy the application on your board::

```bash
python stm32ai_main.py
```
If you chose to update the [deployment_config.yaml](../src/config_file_examples/deployment_mpu_config.yaml) and use it then run the following command from the **src/** folder to build and flash the application on your board::

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_mpu_config.yaml
```

If you have a Keras model that has not been quantized and you want to quantize it before deploying it, you can use the `chain_qd` tool to quantize and deploy the model sequentially. To do this, update the [chain_qd_config.yaml](../src/config_file_examples/chain_qd_config.yaml) file and then run the following command from the `src/` folder to build and flash the application on your board:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_qd_config.yaml
```

When the application is running on the *STM32MPU* board, the LCD displays the following information:
- Data stream from camera board
- Bounding boxes with confidence score between 0 and 1 attached
probability and attached classes
- The number of frames processed per second (FPS) by the model

![plot](./doc/img/output_mpu_application.JPG)

</details>
