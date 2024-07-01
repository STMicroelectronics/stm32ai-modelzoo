# Benchmarking of Hand Posture model

The Hand Posture Model Benchmarking service is a powerful tool that enables users to evaluate the performance of their Hand Posture models built with Keras (.h5). 
With this service, users can easily upload their model and configure the settings to benchmark it and generate various metrics, including memory footprints and inference time. This can be achieved by utilizing the [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) to benchmark on different STM32 target devices or by using [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html)  to estimate the memory footprints.

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Configure the yaml file</b></a></summary><a id="1"></a>

To use this service and achieve your goals, you can use the [user_config.yaml](../user_config.yaml) or directly update the [benchmarking_config.yaml](../config_file_examples/benchmarking_config.yaml) file and use it. This file provides an example of how to configure the benchmarking service to meet your specific needs.

Alternatively, you can follow the tutorial below, which shows how to benchmark your pre-trained Hand Posture model using our evaluation service.

<ul><details open><summary><a href="#1-1">1.1 Setting the model and the operation mode</a></summary><a id="1-1"></a>

As mentioned previously, all the sections of the YAML file must be set in accordance with this **[README.md](../config_file_examples/benchmarking_config.yaml)**.
In particular, `operation_mode` should be set to evaluation and the `benchmarking` section should be filled as in the following example: 

```yaml
general:
   model_path: ../pretrained_models/CNN2D_ST_HandPosture/ST_pretrainedmodel_custom_dataset/ST_VL53L8CX_handposture_dataset/CNN2D_ST_HandPosture_8classes/CNN2D_ST_HandPosture_8classes.h5

operation_mode: benchmarking
```

In this example, the path to the CNN2D_ST_HandPosture_8classes model (for VL53L8CX sensor) is provided in the `model_path` parameter.

</details></ul>
<ul><details open><summary><a href="#1-2">1.2 Set benchmarking tools and parameters</a></summary><a id="1-2"></a>

The [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) allows you to benchmark your model and estimate its footprints and inference time for different STM32 target devices. To use this feature, set the `on_cloud` attribute to True. Alternatively, you can use [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) to benchmark your model and estimate its footprints for STM32 target devices locally. To do this, make sure to add the path to the `stedgeai` executable under the `path_to_stedgeai` attribute and set the `on_cloud` attribute to False.

The `version` attribute to specify the **STM32Cube.AI** version used to benchmark the model, e.g. **9.1.0** and the `optimization` defines the optimization used to generate the C model, options: "balanced", "time", "ram".

The `board` attribute is used to provide the name of the STM32 board to benchmark the model on. The available boards are 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32F469I-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-H743ZI2', 'STM32H747I-DISCO', 'STM32H735G-DK', 'STM32F769I-DISCO', 'NUCLEO-G474RE', 'NUCLEO-F401RE' and 'STM32F746G-DISCO'.

```yaml
tools:
  stedgeai:
    version: 9.1.0
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_1.15.0/STM32CubeIDE/stm32cubeide.exe

benchmarking:
   board: NUCLEO-F401RE     # Name of the STM32 board to benchmark the model on
```

</details></ul>
</details>
<details open><summary><a href="#2"><b>2. Benchmark your model</b></a></summary><a id="2"></a>

If you chose to modify the [user_config.yaml](../user_config.yaml) you can evaluate the model by running the following command from the **src/** folder:

```bash
python stm32ai_main.py
```
If you chose to update the [benchmarking_config.yaml](../config_file_examples/benchmarking_config.yaml) and use it then run the following command from the **src/** folder: 

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name benchmarking_config.yaml
```
Note that you can provide YAML attributes as arguments in the command, as shown below:

```bash
python stm32ai_main.py operation_mode='benchmarking'
```

</details>
<details open><summary><a href="#3"><b>3. Visualizing the Benchmarking Results</b></a></summary><a id="3"></a>

To view the detailed benchmarking results, you can access the log file `stm32ai_main.log` located in the directory `experiments_outputs/<date-and-time>`. Additionally, you can navigate to the `experiments_outputs` directory and use the MLflow Webapp to view the metrics saved for each trial or launch. To access the MLflow Webapp, run the following command:

```bash
mlflow ui
``` 

This will open a browser window where you can view the metrics and results of your benchmarking trials.

</details>
