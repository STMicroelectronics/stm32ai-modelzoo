# STMicroelectronics – STM32 model zoo

Welcome to STM32 model zoo!

The STM32 AI model zoo is a collection of reference machine learning models that are optimized to run on STM32
microcontrollers.
Available on GitHub, this is a valuable resource for anyone looking to add AI capabilities to their STM32-based
projects.

- A large collection of application-oriented models ready for re-training
- Scripts to easily retrain any model from user datasets
- Pre-trained models on reference datasets
- Application code examples automatically generated from user AI model

These models can be useful for quick deployment if you are interested in the categories that they were trained. We also
provide training scripts to do transfer learning or to train your own model from scratch on your custom dataset.

The performances on reference STM32 MCU and MPU are provided for float and quantized models.

This project is organized by application, for each application you will have a step by step guide that will indicate how
to train and deploy the models.

## What's new in releases 2.x:
<details><summary><b>2.0:</b></summary>

* An aligned and `uniform architecture` for all the use case
* A modular design to run different operation modes (training, benchmarking, evaluation, deployment, quantization) independently or with an option of chaining multiple modes in a single launch.
* A simple and `single entry point` to the code : a .yaml configuration file to configure all the needed services.
* Support of the `Bring Your Own Model (BYOM)` feature to allow the user (re-)training his own model. Example is provided [here](./image_classification/src/training/README.md#51-training-your-own-model), chapter 5.1.
* Support of the `Bring Your Own Data (BYOD)` feature to allow the user finetuning some pretrained models with his own datasets. Example is provided [here](./image_classification/src/training/README.md#23-dataset-specification), chapter 2.3.
</details>
<details open><summary><b>2.1:</b></summary>

* Included additional models compatible with the [STM32MP257F-EV1](https://www.st.com/en/evaluation-tools/stm32mp257f-ev1) board.
* Added support for per-tensor quantization.
* Integrated support for `ONNX model` quantization and evaluation.
* Included support for `STEdgeAI` (STM32Cube.AI v9.1.0 and subsequent versions).
* Expanded use case support to include `Pose Estimation` and `Semantic Segmentation`.
* Standardized logging information for a unified experience.
</details>

<div align="center" style="margin-top: 80px; padding: 20px 0;">
    <p align="center">
        <a href="https://www.python.org/downloads/" target="_blank"><img src="https://img.shields.io/badge/python-3.10-blue" /></a>
        <a href="https://www.tensorflow.org/install/pip" target="_blank"><img src="https://img.shields.io/badge/TensorFlow-2.8.3-FF6F00?style=flat&logo=tensorflow&logoColor=#FF6F00&link=https://www.tensorflow.org/install/pip"/></a>
        <a href="https://stm32ai-cs.st.com/home"><img src="https://img.shields.io/badge/STM32Cube.AI-Developer%20Cloud-FFD700?style=flat&logo=stmicroelectronics&logoColor=white"/></a>  
    </p>
</div>

## Available use-cases
>[!TIP]
> For all use-cases below, quick and easy examples are provided and can be executed for a fast ramp up (click on use cases links below)

<details open><summary><b>Image classification (IC)</b></summary>

[Image Classification use case](image_classification)
| Models             | Input Resolutions | Supported Services    | Suitable Targets for deployment |
|--------------------|------------------|-----------------------|-------------------|
| [MobileNet v1 0.25](image_classification/pretrained_models/mobilenetv1/README.md)   | 96x96x1<br> 96x96x3<br> 224x224x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [MobileNet v1 0.5](image_classification/pretrained_models/mobilenetv1/README.md)   | 224x224x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   | 
| [MobileNet v2 0.35](image_classification/pretrained_models/mobilenetv2/README.md)   | 128x128x3<br>  224x224x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [MobileNet v2 1.0](image_classification/pretrained_models/mobilenetv2/README.md)   |  224x224x3     | Full IC Services      |  [STM32MP257F-EV1](./X-LINUX-AI_application_code/image_classification/STM32MP2/README.md)<br>   |
| [ResNet8 v1](image_classification/pretrained_models/resnetv1/README.md)   | 32x32x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [ST ResNet8](image_classification/pretrained_models/resnetv1/README.md)   | 32x32x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [ResNet32 v1](image_classification/pretrained_models/resnetv1/README.md)   | 32x32x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [SqueezeNet v1.1](image_classification/pretrained_models/squeezenetv1.1/README.md)   | 128x128x3<br>  224x224x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [FD MobileNet 0.25](image_classification/pretrained_models/fdmobilenet/README.md)   | 128x128x3<br>  224x224x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [ST FD MobileNet](image_classification/pretrained_models/fdmobilenet/README.md)   | 128x128x3<br>  224x224x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [ST EfficientNet](image_classification/pretrained_models/efficientnet/README.md)   | 128x128x3<br>  224x224x3     | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |
| [Mnist](image_classification/pretrained_models/st_mnist/README.md)   | 28x28x1<br>      | Full IC Services      | [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board<br>   |

[Full IC Services](image_classification/README.md) : training, evaluation, quantization, benchmarking, prediction, deployment

</details>

<details open><summary><b>Object Detection (OD)</b></summary>

[Object Detection use case](object_detection)
| Models             | Input Resolutions | Supported Services    | Targets for deployment |
|--------------------|------------------|-----------------------|-------------------|
| [ST SSD MobileNet v1 0.25](object_detection/pretrained_models/st_ssd_mobilenet_v1/README.md)   |  192x192x3<br> 224x224x3<br> 256x256x3<br>  | Full OD Services      | [STM32H747I-DISCO](stm32ai_application_code/object_detection/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br>    |
| [SSD MobileNet v2 fpn lite 0.35](object_detection/pretrained_models/ssd_mobilenet_v2_fpnlite/README.md)   |  192x192x3<br> 224x224x3<br> 256x256x3<br> 416x416x3   | Full OD Services      | [STM32H747I-DISCO](stm32ai_application_code/object_detection/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br> or <br>[STM32MP257F-EV1](./X-LINUX-AI_application_code/object_detection/STM32MP2/README.md) <br>    |
| [SSD MobileNet v2 fpn lite 1.0](object_detection/pretrained_models/ssd_mobilenet_v2_fpnlite/README.md)   |  256x256x3<br> 416x416x3   | Full OD Services      |  [STM32MP257F-EV1](./X-LINUX-AI_application_code/object_detection/STM32MP2/README.md)   |
| [ST Yolo LC v1](object_detection/pretrained_models/st_yolo_lc_v1/README.md)   |  192x192x3<br> 224x224x3<br> 256x256x3<br>  | Full OD Services      | [STM32H747I-DISCO](stm32ai_application_code/object_detection/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br>    |
| [Tiny Yolo v2](object_detection/pretrained_models/tiny_yolo_v2/README.md)   |  224x224x3<br> 416x416x3<br>  | Full OD Services      | [STM32H747I-DISCO](stm32ai_application_code/object_detection/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board<br>    |

[Full OD Services](object_detection/README.md) : training, evaluation, quantization, benchmarking, prediction, deployment

</details>

<details open><summary><b>Pose Estimation (PE)</b></summary>

[Pose Estimation use case](pose_estimation)
| Models             | Input Resolutions | Supported Services    | Targets for deployment |
|--------------------|------------------|-----------------------|-------------------|
| [Yolo v8 n pose](pose_estimation/pretrained_models/yolov8n_pose/README.md)   |  256x256x3<br>  | Evaluation / Benchmarking / Prediction / Deployment      | [STM32MP257F-EV1](./X-LINUX-AI_application_code/pose_estimation/STM32MP2/README.md) <br>  |
| [MoveNet 17 kps](pose_estimation/pretrained_models/movenet/README.md)   |  192x192x3<br> 224x224x3<br> 256x256x3<br>   | Evaluation / Quantization / Benchmarking / Prediction      | N/A <br>|
| [ST MoveNet 13 kps](pose_estimation/pretrained_models/movenet/README.md)   |  192x192x3<br>   | Evaluation / Quantization / Benchmarking / Prediction      | N/A <br>|

</details>

<details open><summary><b>Segmentation (Seg)</b></summary>

[Segmentation use case](./semantic_segmentation/)
| Models             | Input Resolutions | Supported Services    | Targets for deployment |
|--------------------|------------------|-----------------------|-------------------|
| [DeepLab v3](./semantic_segmentation/pretrained_models/deeplab_v3/README.md)   |  512x512x3<br>  | Full Seg Services     | [STM32MP257F-EV1](./X-LINUX-AI_application_code/semantic_segmentation/STM32MP2/README.md) <br>  |

[Full Seg Services](./semantic_segmentation/README.md) : training, evaluation, quantization, benchmarking, prediction, deployment

</details>

<details open><summary><b>Human Activity Recognition (HAR)</b></summary>

[Human Activity Recognition use case](human_activity_recognition)
| Models             | Input Resolutions | Supported Services    | Targets for deployment |
|--------------------|------------------|-----------------------|-------------------|
| [gmp](human_activity_recognition/pretrained_models/gmp/README.md)   |  24x3x1<br> 48x3x1<br>  | training / Evaluation / Benchmarking / Deployment      | [B-U585I-IOT02A](./stm32ai_application_code/sensing_thread_x/) using ThreadX RTOS<br>    |
| [ign](human_activity_recognition/pretrained_models/ign/README.md)   |  24x3x1<br> 48x3x1<br>  | training / Evaluation / Benchmarking / Deployment      | [B-U585I-IOT02A](./stm32ai_application_code/sensing_thread_x/) using ThreadX RTOS<br>    |

</details>

<details open><summary><b>Audio Event Detection (AED)</b></summary>

[Audio Event Detection use case](audio_event_detection)
| Models             | Input Resolutions | Supported Services    | Targets for deployment |
|--------------------|------------------|-----------------------|-------------------|
| [miniresnet](audio_event_detection/pretrained_models/miniresnet/README.md)   |  64x50x1<br>  | Full AED Services      | [B-U585I-IOT02A](stm32ai_application_code) using RTOS, ThreadX or FreeRTOS<br>    |
| [miniresnet v2](audio_event_detection/pretrained_models/miniresnetv2/README.md)   |  64x50x1<br>  | Full AED Services      | [B-U585I-IOT02A](stm32ai_application_code) using RTOS, ThreadX or FreeRTOS<br>    |
| [yamnet 256](audio_event_detection/pretrained_models/yamnet/README.md)   |  64x96x1<br>  | Full AED Services      | [B-U585I-IOT02A](stm32ai_application_code) using RTOS, ThreadX or FreeRTOS<br>    |

[Full AED Services](audio_event_detection/README.md) : training, evaluation, quantization, benchmarking, prediction, deployment

</details>

<details open><summary><b>Hand Posture Recognition (HPR)</b></summary>

[Hand Posture Recognition use case](hand_posture)
| Models             | Input Resolutions | Supported Services    | Targets for deployment |
|--------------------|------------------|-----------------------|-------------------|
| [ST CNN 2D Hand Posture](hand_posture/pretrained_models/CNN2D_ST_HandPosture/README.md)   |  64x50x1<br>  | training / Evaluation / Benchmarking / Deployment       | [NUCLEO-F401RE](stm32ai_application_code/hand_posture) with X-NUCLEO-53LxA1 Time-of-Flight Nucleo expansion board<br>    |


## Available tutorials and utilities

* [stm32ai_model_zoo_colab.ipynb](tutorials/notebooks/stm32ai_model_zoo_colab.ipynb): a Jupyter notebook that can be
  easily deployed on Colab to exercise STM32 model zoo training scripts.
* [stm32ai_devcloud.ipynb](tutorials/notebooks/stm32ai_devcloud.ipynb): a Jupyter notebook that shows how to
  access to the STM32Cube.AI Developer Cloud through [ST Python APIs](common/stm32ai_dc) (based on REST API) instead of
  using the web application https://stm32ai-cs.st.com.
* [stm32ai_quantize_onnx_benchmark.ipynb](tutorials/notebooks/stm32ai_quantize_onnx_benchmark.ipynb):
  a Jupyter notebook that shows how to quantize ONNX format models with fake or real data by using ONNX runtime and
  benchmark it by using the STM32Cube.AI Developer Cloud.
* [STM32 Developer Cloud examples](tutorials/scripts/stm32ai_dc_examples): a collection of Python scripts that you can
  use in order to get started with STM32Cube.AI Developer Cloud [ST Python APIs](common/stm32ai_dc).
* [Tutorial video](https://youtu.be/yuSVz3x9LzE): discover how to create an AI application for image classification
  using the STM32 model zoo.
* [stm32ai-tao](https://github.com/STMicroelectronics/stm32ai-tao): this GitHub repository provides Python scripts and
  Jupyter notebooks to manage a complete life cycle of a model from training, to compression, optimization and
  benchmarking using **NVIDIA TAO Toolkit** and STM32Cube.AI Developer Cloud.
* [stm32ai-nota](https://github.com/STMicroelectronics/stm32ai-nota): this GitHub repository contains Jupyter notebooks that demonstrate how to use **NetsPresso** to prune pre-trained deep learning models from the model zoo and fine-tune, quantize and benchmark them by using STM32Cube.AI Developer Cloud for your specific use case. 

## Before you start
For more in depth guide on installing and setting up the model zoo and its requirement on your PC, specially in the
cases when you are running behind the proxy in corporate setup, follow the detailed wiki article
on [How to install STM32 model zoo](https://wiki.st.com/stm32mcu/index.php?title=AI:How_to_install_STM32_model_zoo).

* Create an account on myST and then sign in to [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) to be
  able access the service.
* Or, install [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) locally by following the
  instructions provided in
  the [user manual](https://www.st.com/resource/en/user_manual/um2526-getting-started-with-xcubeai-expansion-package-for-artificial-intelligence-ai-stmicroelectronics.pdf)
  in **section 2**, and get the path to `stm32ai` executable.
    * Alternatively, download latest version of [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html)
      for your OS, extract the package and get the path to `stm32ai` executable.
* If you don't have python already installed, you can download and install it
  from [here](https://www.python.org/downloads/), a **Python Version == 3.10.x** is required to be able to run the the code 
* (For Windows systems make sure to check the **Add python.exe to PATH** option during the installation process).
* If using GPU make sure to install the GPU driver. For NVIDIA GPUs please refer
  to https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html to install CUDA and CUDNN. On Windows, it is
  not recommended to use WSL to get the best GPU training acceleration. If using conda, see below for installation.

* Clone this repository using the following command:

```
git clone https://github.com/STMicroelectronics/stm32ai-modelzoo.git
```

* Create a python virtual environment for the project:
    ```
    cd stm32ai-modelzoo
    python -m venv st_zoo
    ```
  Activate your virtual environment
  On Windows run:
    ```
    st_zoo\Scripts\activate.bat
    ```
  On Unix or MacOS, run:
    ```
    source st_zoo/bin/activate
    ```
* Or create a conda virtual environment for the project:
    ```
    cd stm32ai-modelzoo
    conda create -n st_zoo
    ```
  Activate your virtual environment:
    ```
    conda activate st_zoo
    ```
  Install python 3.10:
    ```
    conda install -c conda-forge python=3.10
    ```
  If using NVIDIA GPU, install cudatoolkit and cudnn and add to conda path:
    ```
    conda install -c conda-forge cudatoolkit=11.8 cudnn
    ```
  Add cudatoolkit and cudnn to path permanently:
    ```
    mkdir -p $CONDA_PREFIX/etc/conda/activate.d
    echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    ```
* Then install all the necessary python packages, the [requirement file](requirements.txt) contains it all.

```
pip install -r requirements.txt
```

## Jump start with Colab

In [tutorials/notebooks](tutorials/notebooks/README.md) you will find a jupyter notebook that can be easily deployed on
Colab to exercise STM32 model zoo training scripts.


> [!IMPORTANT]
> In this project, we are using **TensorFLow version 2.8.3** following unresolved issues with newest versions of TensorFlow, see [more](https://github.com/tensorflow/tensorflow/issues/56242).

>[!CAUTION]
> If there are some white spaces in the paths (for Python, STM32CubeIDE, or, STM32Cube.AI local installation) this can result in errors. So avoid having paths with white spaces in them.

>[!TIP]
> In this project we are using the `mlflow` library to log the results of different runs. Depending on which version of Windows OS are you using or where you place the project the output log files might have a very long path which might result in an error at the time of logging the results. As by default, Windows uses a path length limitation (MAX_PATH) of 256 characters: Naming Files, Paths, and Namespaces. To avoid this potential error, create (or edit) a variable named `LongPathsEnabled` in **Registry Editor** under **Computer/HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Control/FileSystem/** and assign it a value of `1`. This will change the maximum length allowed for the file length on Windows machines and will avoid any errors resulting due to this. For more details have a look at this [link](https://knowledge.autodesk.com/support/autocad/learn-explore/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html). Note that using GIT, line below may help solving long path issue : 
```bash
git config --system core.longpaths true
```
