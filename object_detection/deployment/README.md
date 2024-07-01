# Object detection STM32 model deployment

This tutorial shows how to deploy a pre-trained object detection model on an *STM32 board* using *STM32Cube.AI*.

## Table of contents

<details open><summary><a href="#1"><b>1. Before You Start</b></a></summary><a id="1"></a>

Please check out [STM32 model zoo](../README.md) for complete object detection information.

<ul><details open><summary><a href="#1-1">1.1 Hardware Setup</a></summary><a id="1-1"></a>

The [application code](../../stm32ai_application_code/object_detection/README.md) is running on a hardware setup made up of an STM32 microcontroller board connected to a camera module board. This version supports the following boards only:

- [STM32H747I-DISCO](https://www.st.com/en/product/stm32h747i-disco)
- [B-CAMS-OMV](https://www.st.com/en/product/b-cams-omv)

</details></ul>
<ul><details open><summary><a href="#1-2">1.2 Software requirements</a></summary><a id="1-2"></a>

You can use the [STM32 developer cloud](https://stm32ai-cs.st.com/home) to access the STM32Cube.AI functionalities without installing the software. This requires internet connection and making a free account. Or, alternatively, you can install [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) locally. In addition to this you will also need to install [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html) for building the embedded project.

For local installation :

- Download and install [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html).
- If opting for using [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) locally, download it then extract both `'.zip'` and `'.pack'` files.
The detailed instructions on installation are available in this [wiki article](https://wiki.st.com/stm32mcu/index.php?title=AI:How_to_install_STM32_model_zoo).

</details></ul>
<ul><details open><summary><a href="#1-3">1.3 Specifications</a></summary><a id="1-3"></a>

- `serie` : STM32H7
- `IDE` : GCC
- `resizing` : nearest
- Supports only 8-bits quantized TFlite model, i.e. `quantize` : True if model not quantized
- `quantization_input_type` : uint8
- `quantization_output_type` : float

</details></ul>
</details>
<details open><summary><a href="#2"><b>2. Configure the YAML File</b></a></summary><a id="2"></a>

To configure the deployment YAML, you can start from a minimalistic YAML example. If you want to deploy a model that is already quantized, you can use the [minimalistic deployment YAML example](../src/config_file_examples/deployment_config.yaml). If you want to quantize a model and then deploy it, you can use the [minimalistic quantization - deployment YAML example](../src/config_file_examples/chain_qd_config.yaml). Replace the fields according to your model. You can run a demo using a [pretrained model](../pretrained_models/README.md) from STM32 model zoo. Please refer to the YAML file provided alongside the TFlite model to fill the following sections.

As an example, we will show how to deploy the model [ssd_mobilenet_v2_fpnlite_035_192_int8.tflite](../pretrained_models/ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192) pretrained on COCO dataset using the necessary parameters provided in [ssd_mobilenet_v2_fpnlite_035_192_config.yaml](../pretrained_models/ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_config.yaml).

<ul><details open><summary><a href="#2-1">2.1 Setting the Model and the Operation Mode</a></summary><a id="2-1"></a>

Configure the **general** section in **[user_config.yaml](../src/user_config.yaml)** as the following:
```yaml
general:
  project_name: coco_person_detection
  model_type: ssd_mobilenet_v2_fpnlite
  model_path: ../pretrained_models/ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite
```

where:

- `project_name` - *String*, name of the project.
- `model_type` - *String*, model type is used to adapt the postprocessing to the model. There are three possible choices: `'st_ssd_mobilenet_v1'`, `'ssd_mobilenet_v2_fpnlite'`, `'tiny_yolo_v2'`, `'st_yolo_lc_v1'`.
- `model_path` - *Path* to pretained model. Please check out pretrained models from STM32 model zoo [here](../pretrained_models/README.md).

Configure the **operation_mode** section as follow:
```yaml
operation_mode: deployment
```
where:
- operation_mode - *String*, operation to be executed when the stm32ai_main.py script is launched. In the case of the deployment, the choices are: `'deployment'` if the model is already quantized, or `'chain_qd'` if the model is not quantized. 

</details></ul>
<ul><details open><summary><a href="#2-2">2.2 Dataset configuration</a></summary><a id="2-2"></a>

You need to specify some parameters related to the dataset and the preprocessing of the data in the **[user_config.yaml](../src/user_config.yaml)** which will be parsed into a header file used to run the C application.

<ul><details open><summary><a href="#2-2-1">2.2.1 Dataset info</a></summary><a id="2-2-1"></a>

Configure the **dataset** section in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
dataset:
  name: person_dataset
  class_names: [person]
```

where:
- `name` - Dataset name.
- `class_names` - A list containing the classes name.

</details></ul>
<ul><details open><summary><a href="#2-2-2">2.2.2 Preprocessing info</a></summary><a id="2-2-2"></a>

To run inference in the C application, we need to apply on the input data the same preprocessing used when training the model.

To do so, you need to specify the **preprocessing** configuration in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
preprocessing:
  resizing:
    aspect_ratio: fit
    interpolation: nearest
  color_mode: rgb
```

- `resizing` - **nearest**, only supported option for *application C code*.
- `aspect_ratio` - One of *fit*, *crop* or *padding*. If *crop*, resize the images without aspect ratio distortion by cropping the image as a square, if *padding*, add black borders above and below the image to make it as square, otherwise *fit*, aspect ratio may not be preserved.
- `color_mode` - One of "*grayscale*", "*rgb*" or "*bgr*".

</details></ul>
<ul><details open><summary><a href="#2-2-3">2.2.3 Post processing info</a></summary><a id="2-2-3"></a>

Apply post-processing by modifiying the post_processing parameters in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
postprocessing:
  confidence_thresh: 0.6
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.4
  max_detection_boxes: 10
```

- `confidence_thresh` - A *float* between 0.0 and 1.0, the score thresh to filter detections.
- `NMS_thresh` - A *float* between 0.0 and 1.0, NMS thresh to filter and reduce overlapped boxes.
- `IoU_eval_thresh` - A *float* between 0.0 and 1.0, Area of Overlap / Area of Union ratio above which two bounding boxes are detecting the same object.
- `max_detection_boxes` - An *int* to filter the number of bounding boxes.

</details></ul>
</details></ul>
<ul><details open><summary><a href="#2-3">2.3 Deployment parameters</a></summary><a id="2-3"></a>

To deploy the model in **STM32H747I-DISCO** board, we will use *STM32Cube.AI* to convert the model into optimized C code and *STM32CubeIDE* to build the C application and flash the board.

These steps will be done automatically by configuring the **tools** and **deployment** sections in the YAML file as the following:

```yaml
tools:
  stedgeai:
    version: 9.1.0
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe
deployment:
  c_project_path: ../../stm32ai_application_code/object_detection/
  IDE: GCC
  verbosity: 1
  hardware_setup:
    serie: STM32H7
    board: STM32H747I-DISCO
```

where:

- `tools/stedgeai`
  - `version` - Specify the **STM32Cube.AI** version used to benchmark the model, e.g. **8.0.1**.
  - `optimization` - *String*, define the optimization used to generate the C model, options: "*balanced*", "*time*", "*ram*".
  - `on_cloud` - *Boolean*, to use or not the [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home).
  - `path_to_stedgeai` - *Path* to stedgeai executable file to use local download, else **False**.
- `tools/path_to_cubeIDE` - *Path* to stm32cubeide executable file.
- `deployment`
  - `c_project_path` - *Path* to [application C code](../../stm32ai_application_code/object_detection/README.md) project.
  - `IDE` -**GCC**, only supported option for *Getting Started*.
  - `verbosity` - *0* or *1*. Mode 0 is silent, and mode 1 displays messages when building and flashing C application on STM32 target.
  - `hardware_setup/serie` - **STM32H7**, only supported option for now.
  - `hardware_setup/board` - **STM32H747I-DISCO**, only supported option for now.

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
<details open><summary><a href="#3"><b>3. Deploy pretrained model on STM32 board</b></a></summary><a id="3"></a>

First you need to connect the camera board to the *STM32H747I-DISCO* discovery board, then connect the discovery board to your computer using an usb cable.

The picture below shows how to connect the camera board to the *STM32H747I-DISCO* board using a flat flex cable:

![plot](./doc/img/hardware_setup.JPG)

If you chose to modify the [user_config.yaml](../src/user_config.yaml) you can deploy the model by running the following command from the **src/** folder to build and flash the application on your board::

```bash
python stm32ai_main.py 
```
If you chose to update the [deployment_config.yaml](../src/config_file_examples/deployment_config.yaml) and use it then run the following command from the **src/** folder to build and flash the application on your board: 

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_config.yaml
```

If you have a Keras model that has not been quantized and you want to quantize it before deploying it, you can use the `chain_qd` tool to quantize and deploy the model sequentially. To do this, update the [chain_qd_config.yaml](../src/config_file_examples/chain_qd_config.yaml) file and then run the following command from the `src/` folder to build and flash the application on your board:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_qd_config.yaml
```

When the application is running on the *STM32H747I-DISCO* discovery board, the LCD displays the following information:
- Data stream from camera board
- Bounding boxes with confidence score between 0 and 1 attached
probability
- The number of object detected
- The number of frames processed per second (FPS) by the model

![plot](./doc/img/output_application.JPG)

</details>
