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


<div align="center" style="margin-top: 80px; padding: 20px 0;">
    <p align="center">
        <a href="https://www.python.org/downloads/" target="_blank"><img src="https://img.shields.io/badge/python-3.9%20%7C%203.10-blue" /></a>
        <a href="https://www.tensorflow.org/install/pip" target="_blank"><img src="https://img.shields.io/badge/TensorFlow-2.8.3-FF6F00?style=flat&logo=tensorflow&logoColor=#FF6F00&link=https://www.tensorflow.org/install/pip"/></a>
        <a href="https://stm32ai-cs.st.com/home"><img src="https://img.shields.io/badge/STM32Cube.AI-Developer%20Cloud-FFD700?style=flat&logo=stmicroelectronics&logoColor=white"/></a>  
    </p>
</div>

## Available use-cases

* [Image classification](image_classification)
    * Models: EfficientNet, MobileNet v1, MobileNet v2, Resnet v1 including with hybrid quantization, 
      SqueezeNet v1.1, STMNIST.
    * Deployment: getting started application
        * On [STM32H747I-DISCO](stm32ai_application_code/image_classification/Application/STM32H747I-DISCO) with
          B-CAMS-OMV camera daughter board.
        * On [NUCLEO-H743ZI2](stm32ai_application_code/image_classification/Application/NUCLEO-H743ZI2) with B-CAMS-OMV
          camera daughter board, webcam or Arducam Mega 5MP as input and USB display or SPI display as output.
* [Object detection](object_detection)
    * Models:  ST SSD MobileNet v1, Tiny YOLO v2, SSD MobileNet v2 fpn lite, ST Yolo LC v1.
    * Deployment: getting started application
        * On [STM32H747I-DISCO](stm32ai_application_code/object_detection/Application/STM32H747I-DISCO) with B-CAMS-OMV
          camera daughter board.
* [Human activity recognition (HAR)](human_activity_recognition/)
    * Models: CNN IGN, and CNN GMP for different settings.
    * Deployment: getting started application
        * On [B-U585I-IOT02A](./stm32ai_application_code/sensing_thread_x/) using ThreadX RTOS.
* [Audio event detection (AED)](audio_event_detection)
    * Models: Yamnet, MiniResnet, MiniResnet v2.
    * Deployment: getting started application
        * On [B-U585I-IOT02A](stm32ai_application_code) using RTOS, ThreadX or FreeRTOS.
* [Hand posture recognition](hand_posture)
    * The hand posture use case is based on the ST multi-zone Time-of-Flight sensors: VL53L5CX, VL53L7CX, VL53L8CX. The
      goal of this use case is to recognize static hand posture such as a like, dislike or love sign done with user hand
      in front of the sensor. We are providing a complete workflow from data acquisition to model training, then
      deployment on an STM32 NUCLEO-F401RE board.
    * Model: ST CNN 2D Hand Posture.
    * Deployment: getting started application
        * On [NUCLEO-F401RE](stm32ai_application_code/hand_posture) with X-NUCLEO-53LxA1 Time-of-Flight Nucleo expansion
          board

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

## Before you start

* Create an account on myST and then sign in to [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) to be
  able access the service.
* Or, install [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) locally by following the
  instructions provided in
  the [user manual](https://www.st.com/resource/en/user_manual/um2526-getting-started-with-xcubeai-expansion-package-for-artificial-intelligence-ai-stmicroelectronics.pdf)
  in **section 2**, and get the path to `stm32ai` executable.
    * Alternatively, download latest version of [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html)
      for your OS, extract the package and get the path to `stm32ai` executable.
* If you don't have python already installed, you can download and install it
  from [here](https://www.python.org/downloads/), a **3.9 <= Python Version <= 3.10.x** is required to be able to use
  TensorFlow later on, we recommand using **Python v3.10**. (For Windows systems make sure to check the **Add python.exe
  to PATH** option during the installation process).
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

For more in depth guide on installing and setting up the model zoo and its requirement on your PC, specially in the
cases when you are running behind the proxy in corporate setup, follow the detailed wiki article
on [How to install STM32 model zoo](https://wiki.st.com/stm32mcu/index.php?title=AI:How_to_install_STM32_model_zoo).

## Jump start with Colab

In [tutorials/notebooks](tutorials/notebooks/README.md) you will find a jupyter notebook that can be easily deployed on
Colab to exercise STM32 model zoo training scripts.

## Notes

In this project, we are using **TensorFLow version 2.8.3** following unresolved issues with newest versions of
TensorFlow, see [more](https://github.com/tensorflow/tensorflow/issues/56242).

**Warnings** :

* In this project we are using the `mlflow` library to log the results of different runs. Depending on which version of
  Windows OS are you using or where you place the project the output log files might have a very long path which might
  result in an error at the time of logging the results. As by default, Windows uses a path length limitation (MAX_PATH)
  of 256 characters: Naming Files, Paths, and Namespaces. To avoid this potential error, create (or edit) a variable
  named `LongPathsEnabled` in **Registry Editor**
  under `Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\` and assign it a value of `1`. This
  will change the maximum length allowed for the file length on Windows machines and will avoid any errors resulting due
  to this. For more details have a look at
  this [link](https://knowledge.autodesk.com/support/autocad/learn-explore/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html)
  .
* If there are some white spaces in the paths (for Python, STM32CubeIDE, or, STM32Cube.AI local installation) this can
  result in errors. So avoid having paths with white spaces in them.
