# How can I finetune a ST Model Zoo model on my own dataset?

With ST Model Zoo, you can easily pick an already pretrained model and finetune it on your own dataset.

## Pick a pretrained model

A choice of model architectures pretrained on multiple datasets can be found [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/tree/main/object_detection/pretrained_models).
Find the model you would like to use based on it's input size and performance on various benchmarks.

## Finetune the model on my dataset

For the object detection use case, the dataset must be of **TFS TensorFlow format** format as described in the [how to article](./how_to_use_my_own_object_detection_dataset.md)
A simple example dataset to use could be for example this one: [Pascal VOC](https://public.roboflow.com/object-detection/pascal-voc-2012/1).

### Operation modes:

Depending on what you want to do, you can use the operation modes below:
- Training:
    - To simply train the model on my data and get as output the trained tensorflow model (.keras).
- Chain_tqe:
    - To train, quantize and evaluate the model in one go. You get as ouput both the train and quantized trained models (.keras and .tflite)
- Chain_tqeb:
    - To train, quantize, evaluate and benchmark the quantized model in one go.

For any details regarding the parameters of the config file, you can look here:
- [Training documentation](../README_TRAINING.md)
- [Evaluation documentation](../README_EVALUATION.md)
- [Quantization documentation](../README_QUANTIZATION.md)
- [Benchmark documentation](../README_OVERVIEW.md)

### User_config.yaml:

Below is an example of configuration file for the chain_tqeb as it is the most complete operation mode. 
Here we use a st_sst_mobilenet_v1 with an input size of (224,224,3)
For simpler operation mode, you can delete the part not needed if you want.

The most important parts here are to define:
- The model type in model section (from the pretrained_model folder)
- The operation mode
- The dataset name, format and paths (need to be .tfs files, look [here](./how_to_use_my_own_object_detection_dataset.md))
- The preprocessing
- The input_size, pretrained weight and training parameters
- The benchmarking, quantization and deployment part if requested by the chosen operation mode

```yaml
# user_config.yaml

general:
  project_name: my_retraining
  logs_dir: logs
  saved_models_dir: saved_models
  gpu_memory_limit: 16
  global_seed: 127

model:
  model_type: st_yoloxn

operation_mode: chain_tqeb

dataset:
  format: tfs
  dataset_name: custom_dataset
  class_names: [<your-classes>]
  training_path: <train-set-root-directory>  
  validation_path: <validation-set-root-directory>  
  test_path: <test-set-root-directory>
  # Needed if quantization in operation mode
  quantization_path: <quantization-set-root-directory>  
  quantization_split: 0.3

preprocessing:
  rescaling:  {scale : 127.5, offset : -1}
  resizing:
    aspect_ratio: fit
    interpolation: nearest
  color_mode: rgb

# Optional
data_augmentation:
  random_contrast:
    factor: 0.4
  random_brightness:
    factor: 0.3
  random_flip:
    mode: horizontal
  random_translation:
    width_factor: 0.1
    height_factor: 0.1
  random_rotation:
    factor: 0.05

training:
  model:
    alpha: 0.25
    input_shape: (224, 224, 3) # model size
    pretrained_weights: imagenet # pretrained weights
  dropout: null
  batch_size: 64
  epochs: 1000
  optimizer:
    Adam:
      learning_rate: 0.001
  callbacks:
    ReduceLROnPlateau:
      monitor: val_loss
      patience: 20
    EarlyStopping:
      monitor: val_loss
      patience: 40

# Optional
postprocessing:
  confidence_thresh: 0.001
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  plot_metrics: true
  max_detection_boxes: 100

# Needed if quantization in operation mode
quantization:
  quantizer: TFlite_converter
  quantization_type: PTQ
  quantization_input_type: uint8
  quantization_output_type: float
  export_dir: quantized_models

# Needed if benchmarking in operation mode
benchmarking:
  board: STM32H747I-DISCO

# Needed if quantization,benchmarking in operation mode
tools:
  stedgeai:
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/ST/STEdgeAI/<x.y>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

# Needed if deployment in operation mode
deployment:
  c_project_path: ../../stm32ai_application_code/object_detection/
  IDE: GCC
  verbosity: 1
  hardware_setup:
    serie: STM32H7
    board: STM32H747I-DISCO

mlflow:
  uri: ./tf/src/experiments_outputs/mlruns
  
hydra:
  run:
    dir: ./tf/src/experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

## Run the script:

Edit the user_config.yaml then open a CMD (make sure to be in the UC folder). Finally, run the command:

```powershell
python stm32ai_main.py
```
You can also use any .yaml file using command below:
```powershell
python stm32ai_main.py --config-path=path_to_the_folder_of_the_yaml --config-name=name_of_your_yaml_file
```

