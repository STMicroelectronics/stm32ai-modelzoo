# How to check the accuracy of my model after quantization?

The quantization process optimizes the model for efficient deployment on embedded devices by reducing its memory usage (Flash/RAM) and accelerating its inference time, with minimal degradation in model accuracy. With ST Model Zoo, you can easily check the accuracy of your model, quantize your model and compare this accuracy after quantization. You can also simply do one of these actions alone.

## Operation modes:

Depending on what you want to do, you can use the operation modes below:
- evaluate:
    - To evaluate a model, quantized or not (.h5, .tflite or QDQ onnx)
- Chain_eqe:
    - To evaluate a model, quantize it and evaluate it again after quantization for comparison.
- Chain_eqeb:
    - To also add a benchmark of the quantized model.

For any details regarding the parameters of the config file, you can look here:
- [Evaluation documentation](../README_EVALUATION.md)
- [Quantization documentation](../README_QUANTIZATION.md)
- [Benchmark documentation](../README_OVERVIEW.md)


## User_config.yaml:

The way ST Model Zoo works is that you edit the user_config.yaml available for each use case and run the stm32ai_main.py python script. 

The most important parts here are to define:
- The path to the model used and its type
- The operation mode
- The data paths and classes
- The other optional or operation mode related parts

It is highly recommended to use real data for the quantization.

```yaml
# user_config.yaml

model:
  model_path: ../../../stm32ai-modelzoo/blob/master/object_detection/st_yoloxn/ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite
  model_type: st_yoloxn
operation_mode: chain_eqeb

# dataset in YOLO Darknet format
# look at the tutorial about the dataset for more information
dataset:
   format: tfs
   dataset_name: coco
   class_names: [<your-classes-used-during-training>]
   test_path: <test-set-root-directory>  
   # Needed if quantization in operation mode
   quantization_path: <quantization-set-root-directory> # you can use your training dataset
   
# Optionnal
preprocessing:
   rescaling:
      scale: 1/127.5
      offset: -1
   resizing:
      aspect_ratio: fit
      interpolation: nearest
   color_mode: rgb

# Optionnal
postprocessing:
  confidence_thresh: 0.001
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  plot_metrics: True   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 100

# Needed if quantization in operation mode
quantization:
   quantizer: TFlite_converter
   quantization_type: PTQ
   quantization_input_type: uint8
   quantization_output_type: float

# Needed if quantization in operation mode
tools:
   stedgeai:
      optimization: balanced
      on_cloud: True
      path_to_stedgeai: C:/ST/STEdgeAI/<x.y>/Utilities/windows/stedgeai.exe
   path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

# Needed if benchmarking in operation mode
benchmarking:
   board: STM32H747I-DISCO

mlflow:
   uri: ./tf/src/experiments_outputs/mlruns

hydra:
   run:
      dir: ./tf/src/experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

You can look at user_config.yaml example [here](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/main/object_detection/config_file_examples) for other operation modes.

## Run the script:

Edit the user_config.yaml then open a CMD (make sure to be in the UC folder). Finally, run the command:

```powershell
python stm32ai_main.py
```
You can also use any .yaml file using command below:
```powershell
python stm32ai_main.py --config-path=path_to_the_folder_of_the_yaml --config-name=name_of_your_yaml_file
```

## Local benchmarking:

To make the benchmark locally instead of using the ST Edge AI Development Cloud you need to add the path for path_to_stedgeai and to set on_cloud to false in the yaml.
- [STEdgeAI Core](https://www.st.com/en/development-tools/stedgeai-core.html)
- [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)

## Available boards for benchmark:

'STM32N6570-DK', 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32H573I-DK', 'NUCLEO-H743ZI2', 'STM32F769I-DISCO', 'STM32H735G-DK', 'STM32H7S78-DK', 'STM32F469I-DISCO', 'STM32F746G-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-F401RE', 'NUCLEO-G474RE', 'STM32MP257F-EV1', 'STM32MP135F-DK' and 'STM32MP157F-DK2'
