# Benchmarking of Human Activity Recognition (HAR) models

The benchmarking functionality of the Human Activity Recognition models enable users to evaluate the performance of their pretrained Keras (.h5) models.  With this service, the users can easily configure the settings of STM32Cube.AI to benchmark the .h5 models and generate various metrics, including memory footprints (RAM and FLASH) and inference time. The provided scripts can perform benchmarking by utilizing the [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) to benchmark on different STM32 target devices or by using [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html)  to estimate the memory footprints. Or, alternatively locally installed STM32Cube.AI CLI application can be used for estimating the memory foot prints (RAM and FLASH).

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Configure the yaml file</b></a></summary><a id="1"></a> 

To use this service and achieve your goals, you can use the [user_config.yaml](../user_config.yaml) or directly update the [benchmarking_config.yaml](../config_file_examples/benchmarking_config.yaml) file and use it. This file provides an example of how to configure the benchmarking service to meet your specific needs.

Alternatively, you can follow the tutorial below, which shows how to benchmark your pretrained Human Activity Recognition model using our benchmarking service.

<ul><details open><summary><a href="#1-1">1.1 Setting the model and the operation mode</a></summary><a id="1-1"></a>

As mentioned previously, the users can either use the minimalistic example [configuration file for the benchmarking](../config_file_examples/benchmarking_config.yaml) file or alternatively follow the steps below to modify the all the sections of the [user_config.yaml](../user_config.yaml) main YAML file. 

The first thing to be configured is the `general.model_path` in general section to point to the keras model that has to be benchmarked.

```yaml
general:
  project_name: human_activity_recognition # optional, if not provided <human_activity_recognition> is used
  model_path:  ../pretrained_models/ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_24/ign_wl_24.h5
              # could be a pretrained (.h5) model from the ../pretrained_models or any model user trained. 
```

Further, the most important part is to set the `operation_mode` variable, which should be set to `benchmarking`: 

```yaml
operation_mode: benchmarking
```

</details></ul>
<ul><details open><summary><a href="#1-2">1.2 Set benchmarking tools and parameters</a></summary><a id="1-2"></a>

The [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) allows you to benchmark your model and estimate its footprints and inference time for different STM32 target boards. To do this the user will need an internet connection and a free account on [st.com](https://www.st.com). Also, the user needs to, set the `on_cloud` attribute to `True`. Alternatively, you can use locally installed CLI of [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) to benchmark your model and estimate its footprints for STM32 target devices locally (no inference time with this option). To do this, make sure to provide the path to the `stedgeai` executable under the `path_to_stedgeai` attribute and set the `on_cloud` attribute to `False`.

The `version` attribute to specify the **STM32Cube.AI** version used to benchmark the model, e.g. `9.0.0` or `9.1.0` and the `optimization` defines the optimization used to generate the C-model, available choices are: 
- balanced (default option, uses a balanced approach for optimizing the RAM and inference time)
- time (optimizes for the best inference time and can result in a bigger RAM consumption)
- ram (optimizes for the best RAM size and can result in a longer inference time)

The `board` attribute is used to provide the name of the STM32 board to benchmark the model. Various choices are available. 
After the configuration of these parameters the sections of configuration file should like below:
```yaml
tools:
  stedgeai:
    version: 9.1.0
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
                     # replace the paths with your path of STM32Cube.AI and STM32CubeIDE
  path_to_cubeIDE: C:/ST/STM32CubeIDE_1.15.0/STM32CubeIDE/stm32cubeide.exe

benchmarking:
   board: NUCLEO-F401RE     # Name of the STM32 board to benchmark the model on
          # available choices
          # [STM32H747I-DISCO, STM32H7B3I-DK, STM32F469I-DISCO, B-U585I-IOT02A,
          # STM32L4R9I-DISCO, NUCLEO-H743ZI2, STM32H747I-DISCO, STM32H735G-DK,
          # STM32F769I-DISCO, NUCLEO-G474RE, NUCLEO-F401RE, STM32F746G-DISCO]

```

</details></ul>
</details>
<details open><summary><a href="#2"><b>2. benchmark your model</b></a></summary><a id="2"></a>

If you chose to modify the [user_config.yaml](../user_config.yaml) you can benchmark the model by running the following command from the **src/** folder after the file is modified:

```bash
python stm32ai_main.py
```
If you chose to update the [benchmarking_config.yaml](../config_file_examples/benchmarking_config.yaml) and use it then run the following command from the **src/** folder: 

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name benchmarking_config.yaml
```
Note that you can also over-write the parameters directly in the CLI by using a provided YAML file. An example of over-writing the `operation_mode` and `model_path` is given below:

```bash
python stm32ai_main.py operation_mode='benchmarking' general.model_path='../pretrained_models/ign/ST_pretrainedmodel_custom_dataset/mobility_v1/ign_wl_24/ign_wl_24.h5'
```

</details>
<details open><summary><a href="#3"><b>3. Visualizing the Benchmarking Results</b></a></summary><a id="3"></a>

The results of the benchmark are printed in the terminal. However you can also access the results later for the previously ran benchmarks either by manually viewing them or by using `mflow`. To view the detailed benchmarking results, you can access the log file `stm32ai_main.log` located in the directory `experiments_outputs/<launch-date-and-time>`. Additionally, you can navigate to the `experiments_outputs` directory and use the MLflow Webapp to view the metrics saved for each trial or launch. To access the MLflow Webapp, run the following command:

```bash
mlflow ui
``` 

This will open a browser window where you can view the metrics and results of your different experiments ran before.

</details>
