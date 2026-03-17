# Object Detection STM32N6 Model Deployment

This tutorial demonstrates how to deploy a pre-trained object detection model built with quantized tflite or ONNX QDQ on an STM32N6 board using STEdgeAI.

## Table of contents

- [1. Before you start](#1-before-you-start)
  - [1.1 Hardware Setup](#11-hardware-setup)
  - [1.2 Software requirements](#12-software-requirements)
- [2. Configuration file](#2-configuration-file)
  - [2.1 Setting the Model and the Operation Mode](#21-setting-the-model-and-the-operation-mode)
  - [2.2 Dataset configuration](#22-dataset-configuration)
    - [2.2.1 Dataset info](#221-dataset-info)
    - [2.2.2 Preprocessing info](#222-preprocessing-info)
    - [2.2.3 Post processing info](#223-post-processing-info)
  - [2.3 Deployment parameters](#23-deployment-parameters)
  - [2.4 Hydra and MLflow settings](#24-hydra-and-mlflow-settings)
- [3. Deployment](#3-deployment)
  - [3.0 Boot modes](#30-boot-modes)
  - [3.1 STM32N6570-DK](#31-stm32n6570-dk)
  - [3.2 NUCLEO-N657X0-Q](#32-nucleo-n657x0-q)

## 1. Before you start

### 1.1 Hardware Setup

The [STM32N6 application code](../../application_code/object_detection/STM32N6/README.md) submodule:

```bash
 git submodule update --init application_code/object_detection/STM32N6
```
This application code runs with either:

- [STM32N6570-DK](https://www.st.com/en/evaluation-tools/stm32n6570-dk.html) discovery board
- [NUCLEO-N657X0-Q](https://www.st.com/en/evaluation-tools/nucleo-n657x0-q.html) nucleo board

- And one of the following camera modules:
  - MB1854 IMX335 camera module (provided with STM32N6570-DK board)
  - [STEVAL-55G1MBI](https://www.st.com/en/evaluation-tools/steval-55g1mbi.html)
  - [STEVAL-66GYMAI1](https://www.st.com/en/evaluation-tools/steval-66gymai.html)
__Note__: Camera detected automatically by the firmware, no config required.

- Optional screen for nucleo board:
  - [X-NUCLEO-GFX01M2](https://www.st.com/en/evaluation-tools/x-nucleo-gfx01m2.html)

### 1.2 Software requirements

1. [STEdgeAI Core](https://www.st.com/en/development-tools/stedgeai-core.html) to generate network C code from tflite/onnx model.
2. [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html) to build the embedded project.

## 2. Configuration file

To deploy your model, you need to fill a YAML configuration file with your tools and model info, and then launch `stm32ai_main.py`.

As an example, we will show how to deploy [st_yoloxn_d033_w025_416_int8.tflite](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/st_yoloxn/ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite) pre-trained on the COCO 2017 person dataset using the necessary parameters provided in [st_yoloxn_d033_w025_416_config.yaml](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/st_yoloxn/ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_config.yaml). To get this model, clone the [ModelZoo repo](https://github.com/STMicroelectronics/stm32ai-modelzoo/) in the same folder you cloned the [STM32 ModelZoo services repo](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/).

To configure the deployment, edit [`../config_file_examples/deployment_n6_st_yoloxn_config.yaml`](../config_file_examples/deployment_n6_st_yoloxn_config.yaml).

### 2.1 Setting the model and the operation Mode

```yaml
general:
  project_name: coco_person_detection

model:
  model_type: st_yoloxn # \'yolov2t', 'yolov4', 'yolov4t', 'st_yololcv1', 'st_yoloxn', 'yolov8n', 'yolov11n'
  # path to a `.tflite` or `.onnx` file.
  model_path: ../../../stm32ai-modelzoo/blob/master/object_detection/st_yoloxn/ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite
```

Configure the __operation_mode__ section as follow:

```yaml
operation_mode: deployment
```

### 2.2 Dataset configuration

#### 2.2.1 Dataset info

Configure the __dataset__ section in the YAML file as follows:

```yaml
dataset:
  dataset_name: coco
  class_names: [person]
```

#### 2.2.2 Preprocessing info

```yaml
preprocessing:
  resizing:
    interpolation: bilinear
    aspect_ratio: crop
  color_mode: rgb # rgb, bgr
```

- `aspect_ratio`:
  - `crop`: Crop both pipes to nn input aspect ratio; Original aspect ratio kept
  - `fit`: Resize both pipe to NN input aspect ratio; Original aspect ratio not kept
  - `full_screen` Resize camera image to NN input size and display a maximized image. See [Aspect Ratio Mode](../../application_code/object_detection/STM32N6/Doc/Build-Options.md#aspect-ratio-mode).
- `color_mode`:
  - `rgb`
  - `bgr`

#### 2.2.3 Post processing info

The --use case--- models usually have a post processing to be applied to filter the model output and show final results on an image.
Post processing parameters can be configured.

```yaml
postprocessing:
  confidence_thresh: 0.5
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  yolo_anchors: # Only applicable for YoloV2
  max_detection_boxes: 10
```

- `confidence_thresh` A *float* between 0.0 and 1.0, the score thresh to filter detections.
- `NMS_thresh` A *float* between 0.0 and 1.0, NMS thresh to filter and reduce overlapped boxes.
- `yolo_anchors`: List of anchors. Only used with Yolov2
- `max_detection_boxes` An *int* to filter the number of bounding boxes. __Warning__: The higher the number, the more memory is used. Our models are validated with 10 boxes.

### 2.3 Deployment parameters

To deploy the model in __STM32N6570-DK__ board, you will use:

1. *STEdgeAI* to convert the model into optimized C code
2. *STM32CubeIDE* to build the C application and flash the board.

These steps will be done automatically by configuring the __tools__ and __deployment__ sections in the YAML file as the following:

```yaml
tools:
  stedgeai:
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/ST/STEdgeAI/<x.y>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

deployment:
  c_project_path: ../application_code/object_detection/STM32N6/
  IDE: GCC
  verbosity: 1
  hardware_setup:
    serie: STM32N6
    board: STM32N6570-DK # NUCLEO-N657X0-Q or STM32N6570-DK
    output: "UVCL" # default image output interface; "UVCL" (USB display) or "SPI" (X-NUCLEO-GFX01M2). Used only with NUCLEO-N657X0-Q
```

- `tools/stedgeai`
  - `optimization` *String*, define the optimization used to generate the C model, options: "*balanced*", "*time*", "*ram*".
  - `on_cloud` *Boolean*, True/False.
  - `path_to_stedgeai` *Path* to stedgeai executable file to use local download, else __False__.
- `tools/path_to_cubeIDE` *Path* to stm32cubeide executable file.
- `deployment`
  - `c_project_path` *Path* to [application C code](../../application_code/object_detection/STM32N6/README.md) project.
  - `IDE` __GCC__, only supported option for *stm32ai application code*.
  - `verbosity` *0* or *1*. Mode 0 is silent, and mode 1 displays messages when building and flashing C application on STM32 target.
  - `serie` __STM32N6__
  - `board` __STM32N6570-DK or NUCLEO-N657X0-Q__, see the [README](../../application_code/object_detection/STM32N6/README.md) for more details.
  - `output` __"SPI"__ to use X-NUCLEO-GFX01M2. __"UVCL"__ to use USB/UVC host as display. Only used for __NUCLEO-N657X0-Q__.

### 2.4 Hydra and MLflow settings

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used to specify the name of the directory where experiment directories are saved. This pattern allows creating a new experiment directory for each run.

```yaml
hydra:
  run:
    dir: ./tf/src/experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown below:

```yaml
mlflow:
  uri: ./tf/src/experiments_outputs/mlruns
```

## 3. Deployment

### 3.0 Boot modes

The STM32N6 does not have any internal flash. To retain your firmware after a reboot, you must program it in the external flash. Alternatively, you can load your firmware directly from SRAM (dev mode). However, in dev mode if you turn off the board, your program will be lost.

__Boot modes:__

- Dev mode (STM32N6570-DK: both boot switches to the right, NUCLEO-N657X0-Q: BOOT0 JP1 in position 1, BOOT1 JP2 in position 2): used to load the firmware from debug session in RAM, or program firmware in external flash
- Boot from flash (STM32N6570-DK: both boot switches to the left, NUCLEO-N657X0-Q: BOOT0 JP1 in position 1, BOOT1 JP2 in position 1): used to boot the firmware in external flash

### 3.1 STM32N6570-DK

__1.__ Connect the CSI camera module to the *STM32N6570-DK* discovery board with a flat cable.

![plot](./img/STM32N6570-DK_Camera.JPG)

__2.__ Connect the discovery board from the STLINK-V3EC USB-C port to your computer using an __USB-C to USB-C cable__.

__Warning__: using USB-A to USB-C cable may not work because of possible lack of power delivery.

![plot](./img/STM32N6570-DK_USB.JPG)

__3.__ Set to [dev mode](#30-boot-modes) and disconnect/reconnect the power cable of your board.

__4.__ Once [`deployment_n6_st_yoloxn_config.yaml`](../config_file_examples/deployment_n6_st_yoloxn_config.yaml) filled, launch:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_n6_st_yoloxn_config.yaml
```

__5.__ Once the application deployment complete, set to [boot from flash mode](#30-boot-modes) and disconnect/reconnect the power cable of your board.

__6.__ When the application is running on the *STM32N6570-DK* board, the LCD displays the following information:

- Data stream from camera board
- The inference time
- Bounding boxes with confidence score between 0 and 1
- The number of detected object

### 3.2 NUCLEO-N657X0-Q

__1.__ Connect the CSI camera module to the *NUCLEO-N657X0-Q* nucleo board with a flat cable.

__2.__ Connect the nucleo board from the STLINK-V3EC USB-C port to your computer using an __USB-C to USB-C cable__.

__Warning__: using USB-A to USB-C cable may not work because of possible lack of power delivery.

![plot](./img/NUCLEO-N657X0-Q.png)

__3.__ Set to [dev mode](#30-boot-modes) and disconnect/reconnect the power cable of your board.

__4.__ Once [`deployment_n6_st_yoloxn_config.yaml`](../config_file_examples/deployment_n6_st_yoloxn_config.yaml) filled, launch:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name deployment_n6_st_yoloxn_config.yaml
```

__5.__ Once the application deployment complete, set to [boot from flash mode](#30-boot-modes) and disconnect/reconnect the power cable of your board.

__6.__ When the application is running on the *NUCLEO-N657X0-Q* board, the LCD displays the following information:

- Data stream from camera board
- The inference time
- Bounding boxes with confidence score between 0 and 1
- The number of detected object

__Note__:
If you have a Keras model that has not been quantized and you want to quantize it before deploying it, you can use the `chain_qd` tool to quantize and deploy the model sequentially. To do this, update the [chain_qd_config.yaml](../config_file_examples/chain_qd_config.yaml) file and then run the following command from the UC folder to build and flash the application on your board:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_qd_config.yaml
```
