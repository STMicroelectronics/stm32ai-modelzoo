# STMicroelectronics – STM32 model zoo

Welcome to STM32 model zoo!


**🎉 We are excited to announce that the STM32 AI model zoo now includes comprehensive PyTorch support, joining TensorFlow and ONNX.
It now features a vast library of PyTorch models, all seamlessly integrated with our end-to-end workflows. Whether you want to train, evaluate, quantize, benchmark, or deploy, you’ll find everything you need – plus the flexibility to choose between PyTorch, TensorFlow, and ONNX. Dive into the expanded <a href="https://github.com/STMicroelectronics/stm32ai-modelzoo/">STM32 model zoo</a> and take your AI projects further than ever on STM32 devices.**

---

The STM32 AI model zoo is a collection of reference machine learning models that are optimized to run on STM32
microcontrollers.
Available on GitHub, this is a valuable resource for anyone looking to add AI capabilities to their STM32-based
projects.

- A large collection of application-oriented models ready for re-training
- Pre-trained models on reference datasets, available across several frameworks.

**Scripts to easily retrain, quantize, evaluate or benchmark any model from user datasets as well as application code examples automatically generated from user AI model can be found in the  [stm32ai-modelzoo-services GitHub](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)**


These models can be useful for quick deployment if you are interested in the categories that they were trained. We also provide training scripts to do transfer learning or to train your own model from scratch on your custom dataset.

Performance metrics on reference STM32 MCU, NPU, and MPU are provided for both float and quantized models.



## What's new in releases :

<details open><summary><b>4.1:</b></summary>

* Support of **STEdgeAI Core v4.0.0**.
* Updated **Audio Event Detection (AED)** to support deployment on **STM32U3**.
* Added support for the **YOLO26** model.
* Multiple bug fixes and overall quality improvements.

</details>

<details><summary><b>4.0:</b></summary>


* Major PyTorch support for Image Classification (IC) and Object Detection (OD)
* Support of **STEdgeAI Core v4.0.0**
* New training and evaluation scripts for PyTorch models
* Expanded model selection and improved documentation
* Unified workflow for TensorFlow and PyTorch
* Performance and usability improvements
* New use cases: **Face Detection (FD)**, **Arc Fault Detection (AFD)**, **Re-Identification (ReID)**
* New mixed precision models (Weights 4-bits, Activations 8-bits) for IC and OD use cases
* Support for Keras 3.8.0, TensorFlow 2.18.0, PyTorch 2.7.1, and ONNX 1.16.1
* Python software architecture rework
* Docker-based setup available, with a ready-to-use image including the full software stack.

</details>
<details><summary><b>3.2:</b></summary>

* Support for **STEdgeAI Core v2.2.0** (STM32Cube.AI v10.2.0).
* Support of **X-Linux-AI v6.1.0** support for MPU.
* New use cases added: **StyleTransfer** and **FastDepth**.
* New models added: **Face Detection**, available in the Object Detection use case, and **Face Landmarks**, available in the Pose Estimation use case.
* Architecture and codebase clean-up.
</details>

</details>
<details><summary><b>3.1:</b></summary>

* Included additional models support (yolov11n, st_yoloxn variants)
</details>
<details><summary><b>3.0:</b></summary>

* Included additional models compatible with the [STM32N6570-DK](https://www.st.com/en/evaluation-tools/stm32n6570-dk) board.
* Expanded models in all use cases.
* Expanded use case support to include **Instance Segmentation** and **Speech Enhancement**.
* Added `Pytorch` support through the speech enhancement Use Case.
* Model Zoo hosted on <a href="#Hugging Face">Hugging Face</a>
</details>
<details><summary><b>2.1:</b></summary>

* Included additional models compatible with the [STM32MP257F-EV1](https://www.st.com/en/evaluation-tools/stm32mp257f-ev1) board.
* Expanded use case support to include **Pose Estimation** and **Semantic Segmentation**.
</details>
<details><summary><b>2.0:</b></summary>

* An aligned and **uniform architecture** for all the use case
</details>


## Find below a summary of available use cases
| Use Case             | Quick definition  | Suitable Targets for deployment |  Smart example  |
|--------------------|------------------|-----------------|------------ |
| [Image Classification](./image_classification/README.md)   | Classifies the content of an image within a predefined set of classes.     | [STM32H747I-DISCO](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/image_classification/STM32H7/README.md) <br> [NUCLEO-H743ZI2](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/image_classification/STM32H7/README.md) <br>  [STM32MP257F-EV1](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/image_classification/STM32MP-LINUX/STM32MP2/README.md) <br> [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_ic.JPG) |
| [Object Detection](./object_detection/README.md)   | Detects, locates and estimates the occurences probability of predefined objects from input images.     | [STM32H747I-DISCO](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/object_detection/STM32H7/README.md) <br>  [STM32MP257F-EV1](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/object_detection/STM32MP-LINUX/STM32MP2/README.md) <br> [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_od.JPG) |
| [Face Detection](./face_detection/README.md)   | Detects, locates and estimates the occurences probability of predefined faces and keypoints from input images.     | [STM32H747I-DISCO](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/face_detection/STM32H7/README.md) <br>   [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_FD.png) |
| [Pose Estimation](./pose_estimation/README.md)   | Detects key points on some specific objects (people, hand, face, ...).     | [STM32MP257F-EV1](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/pose_estimation/STM32MP-LINUX/STM32MP2/README.md) <br> [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_pe.JPG) |
| [Semantic Segmentation](./semantic_segmentation/README.md)   | Associates a label to every pixel in an image to recognize a collection of pixels that form distinct categories.     | [STM32MP257F-EV1](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/STM32MP-LINUX/STM32MP2/README.md) <br> [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_semseg.JPG) |
| [Instance Segmentation](./instance_segmentation/README.md)   | Associates a label to every pixel in an image to recognize a collection of pixels that form distinct categories or instances of each category.     |  [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_instseg.JPG) |
| [Depth Estimation](./depth_estimation/README.md)   | Predict the distance to objects from an image as a pixel-wise depth map.     |  [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br>  | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_de.JPG) |
| [Neural Style Transfer](./neural_style_transfer/README.md)   | applies the artistic style of one image to the content of another image.     |  [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br>  | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_nst.JPG) |
| [Audio Event Detection](./audio_event_detection/README.md)   | Detection of a specific audio events.     | [B-U585I-IOT02A ](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/sensing/STM32U5/README.md) <br> [B-U585I-IOT02A](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/sensing/STM32U5/README.md) <br> [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_aed.JPG) |
| [Speech Enhancement](./speech_enhancement/README.md)   | Enhancement of the audio perception in a noisy environment.     |  [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_se.JPG) |
| [Human Activity Recognition](./human_activity_recognition/README.md)   | Recognizes various activities like walking, running, ...     |  [B-U585I-IOT02A](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/sensing/STM32U5/README.md) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_har.JPG) |
| [Hand Posture Recognition](./hand_posture/README.md)   | Recognizes a set of hand postures using Time of Flight (ToF) sensor     |  [NUCLEO-F401RE](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/hand_posture/STM32F4/README.md) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_hpr.JPG) |
| [Arc Fault Detection](./arc_fault_detection/README.md)   | Detects electrical arc faults from current signals.     |  [B-U585I-IOT02A](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/blob/main/application_code/sensing/STM32U5/README.md) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_afd.JPG) |
| [Re-Identification](./re_identification/README.md)   | Reidentifies a person or object across different images or video frames.     | [STM32N6570-DK](https://www.st.com/en/development-tools/stm32n6-ai.html) <br> | <div align="center" style="width:480px; margin: left;">![plot](./doc/img/output_application_reid.JPG)
</div>


## <a id="Hugging Face">Hugging Face host</a>
The Model Zoo Dashboard is hosted in a Docker environment under the [STMicroelectronics Organization](https://huggingface.co/STMicroelectronics). This dashboard is developed using Dash Plotly and Flask, and it operates within a Docker container.
It can also run locally if Docker is installed on your system. The dashboard provides the following features:

•	Training: Train machine learning models.
•	Evaluation: Evaluate the performance of models.
•	Benchmarking: Benchmark your model using ST Edge AI Developer Cloud
•	Visualization: Visualize model performance and metrics.
•	User Configuration Update: Update and modify user configurations directly from the dashboard.
•	Output Download: Download model results and outputs.

You can also find our models on Hugging Face under the [STMicroelectronics Organization](https://huggingface.co/STMicroelectronics). Each model from the STM32AI Model Zoo is represented by a model card on Hugging Face, providing all the necessary information about the model and linking to dedicated scripts.


## Before you start
The model zoo repo is using the `git lfs`, so the users need to install and set up the `git lfs` before cloning the repo. This can be done by following the instructions below.


- **On Ubuntu:**
    ```sh
    sudo apt-get install git-lfs
    ```

- **On Windows:**
    Download the Git LFS extension [here](https://git-lfs.github.com/).

Once downloaded and installed, set up Git LFS for your user account by running the following command:

```sh
git lfs install
```
You should see the message `Git LFS initialized.` if the command runs successfully.

**NOTE:** If you do not see the message `Git LFS initialized.`, visit the [GitHub documentation page](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage) for more details and support.

### Clone the Repository
In order to use the config files examples from the modelzoo-services, without the need to change the model_path, it is needed to clone the modelzoo below in the same folder as the modelzoo services.

```sh
git clone https://github.com/STMicroelectronics/stm32ai-modelzoo.git
```


