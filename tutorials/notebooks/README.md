# STM32 model zoo notebooks

This directory contains notebook examples to run STM32 model zoo. These notebooks should be downloaded, then uploaded **Jupyter** or **Colab**.

* [stm32ai_model_zoo_colab.ipynb](./stm32ai_model_zoo_colab.ipynb) shows how to train an image classification model on a custom or public dataset using our [scripts](../../image_classification/src/training/README.md).
* [stm32ai_devcloud.ipynb](./stm32ai_devcloud.ipynb) shows how to access to the STM32Cube.AI Developer Cloud through ST Python APIs (based on REST API) instead of using the web application *https://stm32ai-cs.st.com*.

* [stm32ai_quantize_onnx_benchmark.ipynb](./stm32ai_quantize_onnx_benchmark.ipynb) shows how to quantize ONNX format models with fake or real data by using ONNX runtime and benchmark it by using the [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com).
Other notebooks to fulfill model zoo features are available:

* [imageclassification_deploy.ipynb](../../image_classification/deployment/imageclassification_deploy.ipynb) allows to:

1. Select the STM32 board
2. Choose the Image Classification model
3. Build the associated C project
4. Flash the binary file to the STM32 board
