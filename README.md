# STMicroelectronics – STM32 model zoo

Welcome to STM32 model zoo!

The STM32 AI model zoo is a collection of reference machine learning models that are optimized to run on STM32 microcontrollers.
Available on GitHub, this is a valuable resource for anyone looking to add AI capabilities to their STM32-based projects.

- A large collection of application-oriented models ready for re-training
- Scripts to easily retrain any model from user datasets
- Pre-trained models on reference datasets
- Application code examples automatically generated from user AI model

These models can be useful for quick deployment if you are interested in the categories that they were trained. We also provide training scripts to do transfer learning or to train your own model from scratch on your custom dataset.

The performances on reference STM32 MCU and MPU are provided for float and quantized models.

This project is organized by application, for each application you will have a step by step guide that will indicate how to train and deploy the models.

## Available use-cases

* [Image classification](image_classification)
    * Models: EfficientNet, MobileNet v1, MobileNet v2, Resnet v1 including with hybrid quantization, SqueezeNet v1.0, SqueezeNet v1.1, STMNIST.
    * Deployment: getting started application
        * On [STM32H747I-DISCO](image_classification/getting_started/Application/STM32H747I-DISCO) with B-CAMS-OMV camera daughter board.
        * On [NUCLEO-H743ZI2](image_classification/getting_started/Application/NUCLEO-H743ZI2) with B-CAMS-OMV camera daughter board and USB display output.
* [Object detection](object_detection)
    * Models: SSD MobileNet v1, ST Yolo LC v1.
    * Deployment: getting started application
        * On [STM32H747I-DISCO](object_detection/getting_started) with B-CAMS-OMV camera daughter board.
* [Human activity recognition (HAR)](human_activity_recognition/)
    * Models: CNN IGN, CNN GMP, SVC (Support Vector Classifier).
    *  Deployment: getting started application
        * On [B-U585I-IOT02A](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/main/human_activity_recognition/getting_started) using ThreadX RTOS.
* [Audio event detection (AED)](audio_event_detection)
    * Models: Yamnet, MiniResnet, MiniResnet v2.
    *  Deployment: getting started application
        * On [B-U585I-IOT02A](audio_event_detection/getting_started) using RTOS, ThreadX or FreeRTOS.
* [Hand posture recognition](hand_posture)
    * The hand posture use case is based on the ST multi-zone Time-of-Flight sensors: VL53L5CX, VL53L7CX, VL53L8CX. The goal of this use case is to recognize static hand posture such as a like, dislike or love sign done with user hand in front of the sensor. We are providing a complete workflow from data acquisition to model training, then deployment on an STM32 NUCLEO-F401RE board.
    * Model: ST CNN 2D Hand Posture.
    * Deployment: getting started application
        * On [NUCLEO-F401RE](hand_posture/getting_started) with X-NUCLEO-53LxA1 Time-of-Flight Nucleo expansion board

## Available tutorials and utilities
* [STM32AI_Model_Zoo_Colab.ipynb](tutorials/notebooks/ONNX_model_quantization.ipynb): a Jupyter notebook that can be easily deployed on Colab to exercise STM32 model zoo training scripts.
* [STM32CubeAI_DevCloud.ipynb](tutorials/notebooks/STM32CubeAI_DevCloud.ipynb): a Jupyter notebook that shows how to access to the STM32Cube.AI Developer Cloud through [ST Python APIs](common/stm32ai_dc) (based on REST API) instead of using the web application https://stm32ai-cs.st.com.
* [ONNX_model_quantization.ipynb](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/main/tutorials/notebooks/ONNX_model_quantization.ipynb): a Jupyter notebook that shows how to quantize ONNX format models with fake or real data by using ONNX runtime and benchmark it by using the STM32Cube.AI Developer Cloud.
* [STM32 Developer Cloud examples](tutorials/scripts/stm32ai_dc_examples): a collection of Python scripts that you can use in order to get started with STM32Cube.AI Developer Cloud [ST Python APIs](common/stm32ai_dc).
* [Tutorial video](https://youtu.be/yuSVz3x9LzE): discover how to create an AI application for image classification using the STM32 model zoo.

## Before you start

* Create an account on myST and then sign in to [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) to be able access the service.
* Or, download latest version of [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) for your OS, extract the package and get the path to `stm32ai` executable.
* If you don't have python already installed, you can download and install it from [here](https://www.python.org/downloads/), a **Python Version <= 3.10** is required to be able to use TensorFlow later on, we recommand using **Python v3.9 or v3.10**. (For Windows systems make sure to check the **Add python.exe to PATH** option during the installation process).
* If using GPU make sure to install the GPU driver. For NVIDIA GPUs please refer to https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html to install CUDA and CUDNN. On Windows, it is not recommended to use WSL to get the best GPU training acceleration. If using conda, see below for installation.

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
    conda install -c conda-forge pyhton=3.10
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

In [tutorials/notebooks](tutorials/notebooks/README.md) you will find a jupyter notebook that can be easily deployed on Colab to exercise STM32 model zoo training scripts.

## Notes

In this project, we are using **TensorFLow version 2.8.3** following unresolved issues with newest versions of TensorFlow, see [more](https://github.com/tensorflow/tensorflow/issues/56242).

**Warning** : In this project we are using the `mlflow` library to log the results of different runs. Depending on which version of Windows OS are you using or where you place the project the output log files might have a very long path which might result in an error at the time of logging the results. As by default, Windows uses a path length limitation (MAX_PATH) of 256 characters: Naming Files, Paths, and Namespaces. To avoid this potential error, create (or edit) a variable named `LongPathsEnabled` in **Registry Editor** under `Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\` and assign it a value of `1`. This will change the maximum length allowed for the file length on Windows machines and will avoid any errors resulting due to this. For more details have a look at this [link](https://knowledge.autodesk.com/support/autocad/learn-explore/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html).
