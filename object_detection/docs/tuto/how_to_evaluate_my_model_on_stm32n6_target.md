# How to evaluate my model on STM32N6 target?

The evaluation of a model consists in running several inferences on a representative test set in order to get a quality metric of the model, like the accuracy, the mAP, the OKS or any other depending on the UC. This evaluation can be done on :
   - "host" using TensorFlow or ONNX Run Times and executed on the host machine.
   - "stedgeai_host" using a DLL containing emulated STM32 kernels implementation and executed on the host machine
   - "stedgeai_n6" using a generic test application and executed on the STM32N6 target


## Environment setup:
The evaluation on the target requires installation and configuration of ST Edge AI Core you can find here :
- [STEdgeAI Core](https://www.st.com/en/development-tools/stedgeai-core.html)
- [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)

A few configurations are required, please find below an example following a standard installation of STEdgeAI_Core v2.x.

- The 'C:/ST/STEdgeAI_Core/2.x/scripts/N6_scripts/config_n6.json' file should be updated to configure the N6 loader.
```json
{
	// The 2lines below are _only used if you call n6_loader.py ALONE (memdump is optional and will be the parent dir of network.c by default)
	"network.c": "C:/ST/STEdgeAI_Core/2.0/script/N6_scripts/st_ai_output/network.c",
	//"memdump_path": "C:/Users/foobar/CODE/stm.ai/stm32ai_output",
	// Location of the "validation" project  + build config name to be built (if applicable)
	// If using the provided project, valid build_conf names are "N6-DK" (CR5 boards), "N6-DK-legacy" (older-than-CR5-boards); "N6-Nucleo" can also be used for IAR project.
	"project_path": "C:/ST/STEdgeAI_Core/2.0/Projects/STM32N6570-DK/Applications/NPU_Validation",
	"project_build_conf": "N6-DK",
	// Skip programming weights to earn time (but lose accuracy) -- useful for performance tests
	"skip_external_flash_programming": false,
	"skip_ram_data_programming": false
}
```
- The 'C:/ST/STEdgeAI_Core/2.x/scripts/N6_scripts/config.json' file should be updated to indicate the paths to find the external tools.
```json
{
	// Set Compiler_type to either gcc or iar
	"compiler_type": "iar",
	// Set Compiler_binary_path to your bin/ directory where IAR or GCC can be found
	//     If "Compiler_type" == gcc, then gdb_server_path shall point to where ST-LINK_gdbserver.exe can be found
	"gdb_server_path": "C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.stlink-gdb-server.win32_2.2.0.202409170845/tools/bin/",
	"gcc_binary_path": "C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.12.3.rel1.win32_1.1.0.202410251130/tools/bin/",
	"iar_binary_path": "C:/Program Files/IAR Systems/Embedded Workbench 9.1/common/bin/",
	// Full path to arm-none-eabi-objcopy.exe
	"objcopy_binary_path": "C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.12.3.rel1.win32_1.1.0.202410251130/tools/bin/arm-none-eabi-objcopy.exe",
	// Cube Programmer binary path
	"cubeProgrammerCLI_binary_path": "C:/Program Files/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe",
	"cubeide_path":"C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE"
}
```
Please refer to [stedge ai core getting started on how to evaluate a model on STM32N6 board](https://stedgeai-dc.st.com/assets/embedded-docs/stneuralart_getting_started.html#ref_tools_config_n6l_json) for more information on how it works and on the setup.


## Before launching the stm32ai_eval_on_target.py script:
The script to be used for the evaluation on target is taking as parameter a configuration file. The one to use and to adapt is [evaluation_n6_config.yaml](../../config_file_examples/evaluation_n6_config.yaml) in config_file_examples folder.
It is using a standard configuration file used for evaluation, with a few more parameters to define.
Below are the main parameters to set.
* The `model_path` in the model section : path to the model you want to evaluate.
* The `operation_mode` must be set to `evaluation`

In the evaluation section:
* `profile` : This relates to the user_neuralart.json file that contains various profiles the memory mapping and the compiler options. This is for advanced users and `profile_O3` is very good to start with. More information in [this article](https://stedgeai-dc.st.com/assets/embedded-docs/stneuralart_neural_art_compiler.html#ref_built_in_tool_profiles).
* `input_type` : This is the input type provided by the pipeline, before entering the model. In this use case, this can be set to uint8 as this is the expected camera pipeline output format.
* `output_type` : This is the output type expected for the post processing, after model execution. This can be set to int8 here.
* `input_chpos` : This refers to the input data layout (NHWC vs NCHW). As the camera pipeline present data channel last, for standard .tflite and .onnx models (no transpose at the start of the model), this should be set to chlast.
* `output_chpos` : This refers to the output data layout (NHWC vs NCHW). Here as well, for consistency this should be set to chlast.
* `target` : This is to set the type of evaluation (host, STM32 emulated on host, or on STM32N6 HW)

In the dataset section:
* The `test_path` must be set to the dataset folder used for the evaluation

The `preprocessing` and `postprocessing` sections must be set as usual to align the preprocessing with the same configuration used during the model training.

Please refer to the online documentation on the [I/O data type or layout changes](https://stedgeai-dc.st.com/assets/embedded-docs/how_to_change_io_data_type_format.html) for more information.
In the Tools section:
* `path_to_stedgeai` : This the path of the stedgeai core executable

In the Tools section:
* `path_to_stedgeai` : This the path of the stedgeai core executable

```yaml
model:
   model_path:  ../../stm32ai-modelzoo/object_detection/st_yoloxn/ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_192/st_yoloxn_d033_w025_192_int8.tflite
   model_type: st_yoloxn

operation_mode: evaluation

evaluation:
  profile: profile_O3
  input_type: uint8     # int8 / uint8 / float32
  output_type: int8     # int8 / uint8 / float32
  input_chpos: chlast   # chlast / chfirst
  output_chpos: chlast  # chlast / chfirst
  target: host # host, stedgeai_host, stedgeai_n6

dataset:
  dataset_name: coco
  class_names: [person]
  test_path: ./datasets/coco_2017_person/test


preprocessing:
  rescaling: { scale: 1/127.5, offset: -1 }
  resizing:
    aspect_ratio: fit
    interpolation: nearest
  color_mode: rgb

postprocessing:
  confidence_thresh: 0.001
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  plot_metrics: True   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 100

tools:
   stedgeai:
      path_to_stedgeai: C:/ST/STEdgeAI_Core/2.1/Utilities/windows/stedgeai.exe

mlflow:
   uri: ./tf/src/experiments_outputs/mlruns

hydra:
   run:
      dir: ./tf/src/experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```


## Run the script:
Edit the evaluation_n6_config.yaml as explained above then open a CMD (make sure to be in the application folder containing the stm32ai_main.py script), and run the command:

```powershell
python stm32ai_main.py --config-path ./config_file_examples --config-name evaluation_n6_config.yaml
```
You can also use any .yaml file using command below:
```powershell
python stm32ai_main.py --config-path=path_to_the_folder_of_the_yaml --config-name=name_of_your_yaml_file
```

## Script outcome:
Close to the end of the log, you will see mAP results for the evaluation of your model, based on the dataset you used.
Please remember that evaluation on target may take time mainly because of data transfers between the host and the target, so a appropriate number of samples should be used for this task. Not less than 100 for a representative statistics and no more than 1000 for a reasonable evaluation time sounds a good tradeoff.

