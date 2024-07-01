# __Image classification getting started - STM32MP1x__

The purpose of this package is to enable image classification application on a STM32MPU board.

### __Directory contents__

This repository is structured as follows:

| Directory                                                              | Content                                                   |
|:---------------------------------------------------------------------- |:--------------------------------------------------------- |
| Application                                                            | Python application script + launch script                 |
| Resources                                                              | All the resources necessary for the application           |
| Optimized_models                                                       | *Place holder* for optimized model from Developer Cloud |
| STM32MP1                                                               | Specific resources for STM32MP1x family + Readme |
| STM32MP2                                                               | Specific resources for STM32MP2x family + Readme |
| LICENSE.md                                                             | Application License file                          |

## __Before you start__

### __Hardware and Software environment__

In order to run this image classification application examples you need to have the following hardware:

- [STM32MP157F-DK2](https://www.st.com/en/evaluation-tools/stm32mp157f-dk2) discovery board
- [USB camera] no built-in camera

![STM32MP157F-DK2](../_htmresc/STM32MP157F-DK2.png)

or

- [STM32MP135F-DK](https://www.st.com/en/evaluation-tools/stm32mp135f-dk) discovery board
- [MB1897]  GC2145 GalaxyCore camera module

![STM32MP135F-DK](../_htmresc/STM32MP135F-DK.png)

Only these hardwares are supported for now

On software side, this getting started needs [X-LINUX-AI](https://www.st.com/en/embedded-software/x-linux-ai.html) expansion package for OpenSTLinux version `v5.1.0`.

![X-LINUX-AI](../_htmresc/X-LINUX-AI-logo.png)

All the information needed to install X-LINUX-AI on your board is available in the following wiki page:

- X-LINUX-AI expansion package : https://wiki.st.com/stm32mpu/wiki/Category:X-LINUX-AI_expansion_package


## __Deployment__

For STM32MPU, application code example is provided as python script to facilitate and accelerate the deployment on the target.

### __Deploy application code__

You should use the deploy.py script to automatically deploy the program on the target (if the hardware is connected to the network).

The [deployment script](../../../image_classification/deployment/README.md) of the model zoo is used to directly populate the target with all the needed files, resources and NN model. The script use
the IP address provided in the configuration yaml file. The application source code is available `Application\` directory and can be modified easily.

## __Getting started deep dive__

The purpose of this package is to enable image classification application on a STM32MPU board.

### __Processing workflow__

The software executes an image classification on each image captured by the camera. The framerate depends on each step of the processing workflow.


![processing Workflow schema](../_htmresc/algoProcessing.drawio.svg)

Captured_image: image from the camera

Network_Preprocess - 3 steps:
   -  ImageResize: rescale the image to fit the resolution needed by the network
   -  PixelFormatConversion: convert image format (usually RGB565) to fit the network color channels (RGB888 or Grayscale)
   -  PixelValueConversion: convert to pixel type used by the network (uint8 or int8)

HxWxC: Height, Width and Number of color channels, format defined by the neural network

Network_Inference: call tflite/onnx network

Network_Postprocess: Apply post-processing operations on NN model raw outputs to be able to display inference results on the display

### __Application workflow__

The image classification application can be divided into four main parts :

- Data acquisition and preprocessing which is built with Gstreamer library
- Neural Network inference based on TFLite runtime or ONNX Runtime libraries depending on the model used.
- Neural Network post processing which is handled by common numerical computing tools like Numpy
- Graphical user interface : built with GTK3+ and Cairo libraries

### __Image processing__

The frame captured by the camera is in a standard video format. As the neural network needs to receive a square-shaped image as input, for now only one solutions is provided to reshape the captured frame before running the inference
- ASPECT_RATIO_FIT: the frame is compacted to fit into a square with a side equal to the height of the captured frame. The aspect ratio is modified.

![ASPECT_RATIO_FIT](../_htmresc/ASPECT_RATIO_FIT.png)

By default the interpolation type used for resizing the input image is simple bilinear interpolation

## __Limitations__

- Supports only X-LINUX-AI latest version v5.1.0.