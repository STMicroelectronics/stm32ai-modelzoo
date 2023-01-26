# STMicroelectronics – STM32 Model Zoo

Welcome to STM32 Model Zoo!

This project provides a collection of pre-trained models that you can easily pass through STM32Cube.AI and deploy  on your STM32 board.

These models can be useful for quick deployment if you are interested in the categories that they were trained. We also provide training scripts to do transfer learning or to train your own model from scratch on your custom dataset.

This project is organized by application, for each application you will have a step by step guide that will indicate how to train and deploy the models.

## Available Use-Cases

* [Image Classification](image_classification/README.md)
* [Object Detection](object_detection/README.md)
* [Human Activity Recognition (HAR)](human_activity_recognition/README.md)
* [Audio Event Detection (AED)](audio_event_detection/README.md)


## Before You Start

- Create an account on [ST Developer Cloud](https://stm32ai-cs.st.com/home) to be able to use the provided Developer Cloud Services of `STM32Cube.AI`.
- Or, Download latest version of [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) for your OS, extract the package and get the path to `stm32ai` executable.
- If you don't have python already installed, you can download the latest version and install it from [here](https://www.python.org/downloads/) (For Windows systems make sure to check the **Add python.exe to PATH** option during the installation process).
- Clone this repository using the following command:
```
git clone https://github.com/STMicroelectronics/stm32ai-modelzoo.git
```
- Create a virtual environment for the project, you should have a **Python Version <= 3.10** to be able to use TensorFlow:
```
cd stm32ai-modelzoo
python -m venv st_zoo
```
- Activate your virtual environment, on Windows run:
 ```
st_zoo\Scripts\activate.bat
```
On Unix or MacOS, run:
 ```
source st_zoo/bin/activate
```
- Install all the necessary python packages, the [requirement file](requirements.txt) contains it all.
```
pip install -r requirements.txt
```

## Jump Start with Colab

In [utilities/notebooks](utilities/notebooks/README.md) you will find a Jupyter Notebook that can be easily deployed on Colab to exercise ST Model Zoo training scripts.


**PS**: In this project, we are using **TensorFLow version 2.8.3** following unresolved issues with newest versions of TensorFlow, see [more](https://github.com/tensorflow/tensorflow/issues/56242).

**Warning** : In this project we are using the mlflow library to log the results of different runs. Depending on which version of Windows OS are you using or where you place the project the output log files might have a very long path which might result in an error at the time of logging the results. As by default, Windows uses a path length limitation (MAX_PATH) of 256 characters: Naming Files, Paths, and Namespaces. To avoid this potential error, create (or edit) a variable named `LongPathsEnabled` in **Registry Editor** under `Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem\` and assign it a value of `1`. This will change the maximum length allowed for the file length on Windows machines and will avoid any errors resulting due to this. For more details have a look at this [link](https://knowledge.autodesk.com/support/autocad/learn-explore/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html).