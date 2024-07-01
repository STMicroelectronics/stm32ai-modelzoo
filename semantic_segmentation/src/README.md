
# Semantic Segmentation STM32 model zoo

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Semantic segmentation Model Zoo introduction</b></a></summary><a id="1"></a>

The semantic segmentation model zoo provides a collection of independent services and pre-built chained services that can be used to perform various functions related to machine learning for semantic segmentation. 
The individual services include tasks such as training the model or quantizing the model, while the chained services combine multiple services to perform more complex functions, such as training the model, quantizing it, 
and evaluating the quantized model successively.

To use the services in the semantic segmentation model zoo, you can utilize the model zoo [stm32ai_main.py](stm32ai_main.py) along with [user_config.yaml](user_config.yaml) file as input. 
The yaml file specifies the service or the chained services and a set of configuration parameters such as the model (either from the model zoo or your own custom model), the dataset, the number of epochs, 
and the preprocessing parameters, among others.

More information about the different services and their configuration options can be found in the <a href="#2">next section</a>.

To date, the only dataset structure supported is the PASCAL VOC 2012. It means that each set can be specified by 3 parameters: the path to a directory containing the jpeg images, a second path to a directory containing the masks in .png 
and to finish a path to a file .txt containing the names of the jpeg images to be considered in the jpeg images directory for a given set. 
More details are given later in this README.

</details>
<details open><summary><a href="#2"><b>2. Semantic segmentation tutorial</b></a></summary><a id="2"></a>

This tutorial demonstrates how to use the `chain_tbqeb` services to train, benchmark, quantize, evaluate, and benchmark the model. Among the various available [models](../pretrained_models/) in the model zoo.

To get started, you will need to update the [user_config.yaml](user_config.yaml) file, which specifies the parameters and configuration options for the services that you want to use. 
Each section of the [user_config.yaml](user_config.yaml) file is explained in detail in the following sections.

<ul><details open><summary><a href="#2-1">2.1 Choose the operation mode</a></summary><a id="2-1"></a>

The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be single operation or a set of chained operations.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 
'b' for benchmark and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations |
|:---------------------------|:-----------|
| `training`| Train the supported segmentation model from the model zoo or your own model |
| `evaluation` | Evaluate the accuracy of a float or quantized model on a test or validation dataset|
| `quantization` | Quantize a float model |
| `prediction`   | Predict the classes some images belong to using a float or quantized model |
| `benchmarking` | Benchmark a float or quantized model on an STM32 board |
| `deployment`   | Deploy a model on an STM32 board |
| `chain_tbqeb`  | Sequentially: training, benchmarking of trained model, quantization of trained model, evaluation of quantized model, benchmarking of quantized model |
| `chain_tqe`    | Sequentially: training, quantization of trained model, evaluation of quantized model |
| `chain_eqe`    | Sequentially: evaluation of a float model,  quantization, evaluation of the quantized model |
| `chain_qb`     | Sequentially: quantization of a float model, benchmarking of quantized model |
| `chain_eqeb`   | Sequentially: evaluation of a float model,  quantization, evaluation of quantized model, benchmarking of quantized model |
| `chain_qd`     | Sequentially: quantization of a float model, deployment of quantized model |

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific services:

   - [training, chain_tqe, chain_tbqeb](./training/README.md)
   - [quantization, chain_eqe, chain_qb](./quantization/README.md)
   - [evaluation, chain_eqeb](./evaluation/README.md)
   - [benchmarking](./benchmarking/README.md)
   - [prediction](./prediction/README.md)
   - [deployment, chain_qd](../deployment/README.md)

In this tutorial the `operation_mode` used is the `chain_tbqeb` like shown below to train a model, benchmark, quantize, evaluate it to be later deployed in the STM32 boards.

```yaml
operation_mode: chain_tbqeb
```
</details></ul>
<ul><details open><summary><a href="#2-2">2.2 Global settings</a></summary><a id="2-2"></a>

The `general` section and its attributes are shown below.

```yaml
general:
   project_name: segmentation        # Project name. Optional, defaults to "<unnamed>".
   logs_dir: logs                    # Name of the directory where log files are saved. Optional, defaults to "logs".
   saved_models_dir: saved_models    # Name of the directory where model files are saved. Optional, defaults to "saved_models".
   model_path: <file-path>           # Optional: Path to a model file.
   model_type : deeplab_v3           # The only supported so far, mandatory
   global_seed: 123                  # Seed used to seed random generators (an integer). Optional, defaults to 123.
   deterministic_ops: False          # Enable/disable deterministic operations (a boolean). Optional, defaults to False.
   display_figures: True             # Enable/disable the display of figures (training learning curves, display overlay images).
                                     # Optional, defaults to True.
   gpu_memory_limit: 16              # Maximum amount of GPU memory in GBytes that TensorFlow may use (an integer).
   num_threads_tflite: 4             # Number of threads for tflite interpreter. Optional, defaults to 1
```

The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy and Tensorflow random generators at the beginning of the main script. This is an optional attribute, the default value being 123. 

Even when random generators are seeded, it is often difficult to exactly reproduce results when the same operation is run multiple times. This typically happens when the same training script is run on different hardware. 
The `deterministic_ops` operator can be used to enable the deterministic mode of Tensorflow. If enabled, an operation that uses the same inputs on the same hardware will have the exact same outputs every time it is run. 
However, determinism should be used carefully as it comes at the expense of longer run times. Refer to the Tensorflow documentation for more details.

The `gpu_memory_limit` attribute sets an upper limit in GBytes on the amount of GPU memory Tensorflow may use. This is an optional attribute with no default value. If it is not present, memory usage is unlimited. 
If you have several GPUs, be aware that the limit is only set on logical gpu[0]. 

The `num_threads_tflite` parameter is only used as an input parameter for the tflite interpreter. Therefore, it has no effect on .h5 or .onnx models. 
This parameter may accelerate the tflite model evaluation in the following operation modes: `evaluation` (if a .tflite is specified in `model_path`), `chain_tbqeb`, `chain_eqe`, `chain_tqe` and `chain_eqeb` (if the quantizer is the TFlite_converter). 
However, the acceleration depends on your system resources.

The `model_path` attribute is utilized to indicate the path to the model file that you wish to use for the selected operation mode. The accepted formats for `model_path` are listed in the table below:

| Operation mode | `model_path` |
|:---------------|:-------------|
| 'evaluation'   | Keras or TF-Lite model file |
| 'quantization', 'chain_eqe', 'chain_eqeb', 'chain_qb', 'chain_qd' | Keras model file |
| 'prediction'   | Keras or TF-Lite model file |
| 'benchmarking' | Keras, TF-Lite or ONNX model file |
| 'deployment'   | TF-Lite model file |

If you are using an operation mode that involves training, you can use the `model_path` attribute to train your own custom model instead of using a model from the Model Zoo. 
This is explained in detail in the [readme](./training/README.md) file for the train service. However, in this tutorial, the `model_path` attribute is not used since we are using a pre-trained model from the Model Zoo.

To finish, setting the `model_type` is mandatory for any operation mode which includes training. So far the only topology supported is `deeplab_v3`.

</details></ul>
<ul><details open><summary><a href="#2-3">2.3 Dataset specification</a></summary><a id="2-3"></a>

The `dataset` section and its attributes are shown in the YAML code below.

```yaml
dataset:
  name: pascal_voc
  class_names: ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
                "car", "cat", "chair", "cow", "dining table", "dog", "horse", "motorbike",
                "person", "potted plant", "sheep", "sofa", "train", "tv/monitor"]
  training_path: ../datasets/VOC2012_train_val/JPEGImages                                 # Path to train jpeg images
  training_masks_path: ../datasets/VOC2012_train_val/SegmentationClassAug                 # Path to train masks files
  training_files_path: ../datasets/VOC2012_train_val/ImageSets/Segmentation/trainaug.txt  # Path to file listing the images names for training
  validation_path:        # Optional: path to validation jpeg images
  validation_masks_path:  # Optional: path to validation masks files
  validation_files_path: ../datasets/VOC2012_train_val/ImageSets/Segmentation/val.txt     # Path to file listing the images names for validation
  validation_split: 0.2 # Training/validation sets split ratio.
  test_path: ../datasets/VOC2012_test/JPEGimages                                          # Path to test jpeg images
  test_masks_path: ../datasets/VOC2012_test/SegmentationMasks                             # Path to test masks files
  test_files_path: ../datasets/VOC2012_test/ImageSets/Segmentation/test.txt               # Path to file listing the images names for test
  quantization_path:        # Optional: path to quantization jpeg images
  quantization_masks_path:  # Optional: path to quantization masks images
  quantization_files_path:  # Optional: path to file listing the images names for quantization
  quantization_split: 0.003 # Quantization split ratio.
  seed: 123 # Random generator seed used when splitting a dataset.
```

The `name` attribute is mandatory. To date, a unique value is accepted: `pascal_voc`. This parameter is used in the data_loader in order to correctly construct each dataset expecting PASCAL VOC 2012 structure.
In the future, it could be extended to other datasets type.

As already mentioned, to respect PASCAL VOC 2012 structure we need 3 paths for each set. As an exception, due to the specific structure of PASCAL VOC, the validation set only needs one parameter: the validation files path. 
It will automatically fetch the specified images in the training path jpeg images directory and the corresponding masks in the training masks path.

if `validation_files_path` is not provided, the training set is split in two to create a validation dataset. When a model accuracy evaluation is run, the test set is used if there is one, otherwise the validation set is used 
(either provided or generated by splitting the training set).

The `validation_split` attribute specifies the training/validation set size ratio to use when splitting the training set to create a validation set. The default value is 0.2, meaning that 20% of the training set is used to create 
the validation set. The `seed` attribute specifies the seed value to use for randomly shuffling the dataset file before splitting it (default value is 123).

The 3 quantization path attributes are used to specify a dataset for the quantization process. If these attributes are not provided and a training set is available, the training set is used for the quantization. 
However, training sets can be quite large and the quantization process can take a long time to run. To avoid this issue, you can set the `quantization_split` attribute to use only a random portion of the dataset for quantization.

**Please ensure that the segmentation masks are formatted as images with pixel values as integers. Each integer should correspond to a different class label, effectively segmenting the image into regions based on the class they belong to.**

</details></ul>
<ul><details open><summary><a href="#2-4">2.4 Apply image preprocessing</a></summary><a id="2-4"></a>

Images need to be rescaled and resized before they can be used. This is specified in the 'preprocessing' section that is required in all the operation modes.

The 'preprocessing' section for this tutorial is shown below.

```yaml
preprocessing:
   rescaling:
      # Image rescaling parameters
      scale : 1/127.5
      offset : -1
   resizing:
      # Image resizing parameters
      interpolation: bilinear
      aspect_ratio: fit
   color_mode: rgb
```

Images are rescaled using the formula "Out = scale\*In + offset". Pixel values of input images usually are integers in the interval [0, 255]. If you set *scale* to 1./255 and offset to 0, pixel values are rescaled to the interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they are rescaled to the interval [-1.0, 1.0].

The resizing interpolation methods that are supported include 'bilinear', 'nearest', 'bicubic', 'area', 'lanczos3', 'lanczos5', 'gaussian' and 'mitchellcubic'. Refer to the Tensorflow documentation of the tf.image.resize function 
for more details. However, we observed slightly improved results using 'bilinear' instead of 'nearest' for example, at a price of some additional computational load. 

The `aspect_ratio` attribute may be set to either:
- 'fit', images will be fit to the target size. Input images may be smaller or larger than the target size. They will be distorted to some extent if their original aspect ratio is not the same as the resizing aspect ratio.
- 'crop', images will be cropped to preserve the aspect aspect. The input images should be larger than the target size to use this mode.
- 'padding', images will be padded with zeros (black borders) to meet the target size. The input images should be smaller than the target size to use this mode.

If some images in your dataset are larger than the resizing size and some others are smaller, you will obtain a mix of cropped and padded images if you set `aspect_ratio` to 'crop' or 'padding'.

The `color_mode` attribute can be set to either *"grayscale"*, *"rgb"* or *"rgba"*. However, to date, we have only considered *"rgb"* for training, evaluating and quantizing models.

</details></ul>
<ul><details open><summary><a href="#2-5">2.5 Use data augmentation</a></summary><a id="2-5"></a>

The data augmentation functions to apply to the input images during a training are specified in the optional `data_augmentation` section of the configuration file. They are only applied to the images during training.

For this tutorial data augmentation section is shown below.

```yaml
data_augmentation:   
  random_contrast:
    factor: 0.4
    change_rate: 1.0
  random_gaussian_noise:
    stddev: (0.0001, 0.005)
  random_jpeg_quality:
    jpeg_quality: (60, 100)
    change_rate: 0.025
  random_posterize:
    bits: (4, 8)
    change_rate: 0.025
  random_brightness:
    factor: 0.05
    change_rate: 1.0
```

The data augmentation functions are applied to the input images in their order of appearance in the configuration file. If an argument of a given function is omitted, the default value is used. There are no constraints on the number of functions, types of functions and order of functions. 

Please refer to [the data augmentation documentation](data_augmentation/README.md) for a list of functions that are available and the transforms they apply to the input images.

</details></ul>
<ul><details open><summary><a href="#2-6">2.6 Set the training parameters</a></summary><a id="2-6"></a>

A 'training' section is required in all the operation modes that include a training, namely 'training', chain_tbqeb' and 'chain_tqe'.

In this tutorial, we consider the training of deeplab_v3 (with ASPP head) as defined in [models](./models/deeplabv3.py). It uses a MobileNet V2 model as backbone, pre-trained on the ImageNet dataset, a large dataset consisting of 1.4M images and 1000 classes. 
As an example we will use a MobileNet V2 with alpha = 0.5, to do so we will need to configure the model section in [user_config.yaml](user_config.yaml) as the following:

```yaml
training:
   model:
      name: mobilenet    # backbone topology for model_type                 
      version: v2
      alpha: 0.5
      output_stride: 16  # the only supported for now
      input_shape: (512, 512, 3)
      pretrained_weights: imagenet
      pretrained_model_path:
   batch_size: 64
   epochs: 150
   dropout: 0.3          # Insert a dropout layer in the model and set rate to 0.3
   frozen_layers: None   # Make all layers non-trainable except the last one
   optimizer:
      # Use Keras Adam optimizer with initial LR set to 0.001             
      Adam:                               
         learning_rate: 0.001
   callbacks:                    
      # Use Keras ReduceLROnPlateau learning rate scheduler             
      ReduceLROnPlateau:
         monitor: val_loss
         factor: 0.1
         patience: 10
      # Use Keras EarlyStopping to stop training and not overfit
      EarlyStopping:
         monitor: val_accuracy
         mode: max
         restore_best_weights: true
         patience: 60
```

The `model` subsection is used to specify a model that is available with the Model Zoo:
- The `name` and `input_shape` attributes must always be present. The `name` specifies the topology used as backbone for the considered `model_type`.
- Additional attributes are needed depending on the type of model. For example, an `alpha` attribute is required for a MobileNet model.
- The optional `pretrained_weights` attribute can be used to load pretrained weights in the model before it gets trained. By default, no pretrained weights are loaded.

The `batch_size` and `epochs` attributes are mandatory.

The `dropout` attribute is optional. By default, no dropout layer is inserted in the model.

All the Keras optimizers are supported. If you are not passing any argument to the optimizer, you may write it on one line. For example: "optimizer: Adam".

The optional `frozen_layers` attribute is used to make some layers of the model non-trainable. Together with the `pretrained_weights` attribute of the `model` subsection, 
it is useful when a transfer learning approach is used to train the model or in case we decide to fine-tune only a specified subset of layers. 
Another attribute of the `model` subsection called `pretrained_weights`is also available to load the weights from another model (not shown in the YAML code above). 

The `callbacks` subsection is optional. All the Keras callbacks are supported. Note that several callbacks are built-in and cannot be redefined, including ModelCheckpoint, TensorBoard and CSVLoggerr. 

A variety of learning rate schedulers are provided with the Model Zoo. If you want to use one of them, just include it in the `callbacks` subsection. Refer to the training service [README](training/README.md) for a description 
of the available callbacks and learning rate plotting utility.

The best model obtained at the end of the training is saved in the 'experiments_outputs/\<date-and-time\>/saved_models' directory and is called 'best_model.h5' (see section <a href="#4">visualize the chained services results</a>). 
Make sure not to use the 'best_augmentation_model.h5' file as it includes the rescaling and data augmentation layers

</details></ul>
<ul><details open><summary><a href="#2-7">2.7 Model quantization</a></summary><a id="2-7"></a>

Configure the quantization section in [user_config.yaml](user_config.yaml) as the following:

```yaml

quantization:
   quantizer: TFlite_converter        # or onnx_quantizer (when quantizing onnx float model)
   quantization_type: PTQ             
   quantization_input_type: float     # float for onnx_quantizer
   quantization_output_type: uint8    # float for onnx_quantizer
   granularity: per_tensor            # Optional, defaults to "per_channel".
   optimize: True                     # Optional, defaults to False. Only used when granularity is per_tensor
   target_opset: 17                   # Optional, defaults to 17.
   export_dir: quantized_models       # Optional, defaults to "quantized_models".
```

This section is used to configure the quantization process, which optimizes the model for efficient deployment on embedded devices by reducing its memory usage (Flash/RAM) and accelerating its inference time, with minimal degradation in model accuracy. The `quantizer` attribute expects the value `TFlite_converter`, 
which is used to convert the trained model weights from float to integer values and transfer the model to a TensorFlow Lite format. Alternatively, if a float onnx model is to be quantized, the value for the `quantizer` 
should be set to `Onnx_quantizer`.

The `quantization_type` attribute only allows the value "PTQ," which stands for Post Training Quantization. To specify the quantization type for the model input and output, use the `quantization_input_type` 
and `quantization_output_type` attributes, respectively. 

The `quantization_input_type` attribute is a string that can be set to "int8", "uint8," or "float" to represent the quantization type for the model input. 
Similarly, the `quantization_output_type` attribute is a string that can be set to "int8", "uint8," or "float" to represent the quantization type for the model output. 

These values are not accounted for when using `Onnx_quantizer`. As both input and output types for the model are float and only the weights and activations are quantized.

The `granularity` is either "per_channel" or "per_tensor". If the parameter is not set, it will default to "per_channel". 'per channel' means all weights contributing to a given layer output channel are quantized with 
one unique (scale, offset) couple. The alternative is 'per tensor' quantization which means that the full weight tensor of a given layer is quantized with one unique (scale, offset) couple. 
It is obviously more challenging to preserve original float model accuracy using 'per tensor' quantization. But this method is particularly well suited to fully exploit STM32MP2 platforms HW design.

Some topologies can be slightly optimized to become "per_tensor" quantization friendly. Therefore, we propose to optimize the model to improve the "per-tensor" quantization. 
This is controlled by the `optimize` parameter. Only used when quantizing a (.h5) model using TFlite_converter.
By default, it is False and no optimization is applied. When set to True, some modifications are applied on original network. Please note that these optimizations only apply when granularity is "per_tensor". 
To finish, some topologies cannot be optimized. So even if `optimize` is set to True, there is no guarantee that "per_tensor" quantization will preserve the float model accuracy for all the topologies.

The `target_opset` is an integer parameter. This is only needed or accounted for when using `Onnx_quantizer` and is ignored when using `TFlite_converter`. Before doing the onnx quantization, the onnx opset of the model is updated to the target_opset. If no value is provided a default value of 17 is used.

By default, the quantized model is saved in the 'quantized_models' directory under the 'experiments_outputs' directory. You may use the optional `export_dir` attribute to change the name of this directory.

</details></ul>
<ul><details open><summary><a href="#2-8">2.8 Benchmark the model</a></summary><a id="2-8"></a>

The [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) allows you to benchmark your model and estimate its footprints and inference time for different STM32 target devices. 
To use this feature, set the `on_cloud` attribute to True. Alternatively, you can use [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) to benchmark your model and estimate its footprints 
for STM32 target devices locally. To do this, make sure to add the path to the `stedgeai` executable under the `path_to_stedgeai` attribute and set the `on_cloud` attribute to False.

The `version` attribute to specify the **STM32Cube.AI** version used to benchmark the model, e.g. 9.1.0 and the `optimization` defines the optimization used to generate the C model, options: "balanced", "time", "ram".

The `board` attribute is used to provide the name of the STM32 board to benchmark the model on. 
The available boards are 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32F469I-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-H743ZI2', 'STM32H747I-DISCO', 'STM32H735G-DK', 'STM32F769I-DISCO', 'NUCLEO-G474RE', 'NUCLEO-F401RE' and 'STM32F746G-DISCO'.
However, for segmentation models, we clearly recommend choose an MPU plateform (more memory, more computational power) in particular 'STM32MP257F-EV1'.

```yaml
tools:
   stedgeai:
      version: 9.1.0
      optimization: balanced
      on_cloud: True
      path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
   path_to_cubeIDE: C:/ST/STM32CubeIDE_1.15.0/STM32CubeIDE/stm32cubeide.exe

benchmarking:
   board: STM32MP257F-EV1     # Name of the STM32 board to benchmark the model on
```
The `path_to_cubeIDE` attribute is for the [deployment](../deployment/README.md) service which is not part the chain `chain_tbqeb` used in this tutorial.

</details></ul>
<ul><details open><summary><a href="#2-9">2.9 Deploy the model</a></summary><a id="2-9"></a>

In this tutorial, we are using the `chain_tbqeb` toolchain, which does not include the deployment service. 
However, if you want to deploy the model after running the chain, you can do so by referring to the [README](../deployment/README.md) and modifying the `deployment_config.yaml` file 
or by setting the `operation_mode` to `deploy` and modifying the `user_config.yaml` file as described below:

```yaml
general:
   model_path: <path-to-a-TFlite-model-file>     # Path to the model file to deploy

dataset:
   class_names: ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
                "car", "cat", "chair", "cow", "dining table", "dog", "horse", "motorbike",
                "person", "potted plant", "sheep", "sofa", "train", "tv/monitor"] 

tools:
   stedgeai:
      version: 9.1.0
      optimization: balanced
      on_cloud: True
      path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
   path_to_cubeIDE: C:/ST/STM32CubeIDE_1.15.0/STM32CubeIDE/stm32cubeide.exe

deployment:
  c_project_path: ../../stm32ai_application_code/semantic_segmentation/
  IDE: GCC
  verbosity: 1
  hardware_setup:
    serie: STM32MP2
    board: STM32MP257F-EV1
    input: CAMERA_INTERFACE_DCMI
    output: DISPLAY_INTERFACE_USB
```

In the `general` section, users must provide the path to the TFlite model file that they want to deploy using the `model_path` attribute.

The `dataset` section requires users to provide the names of the classes using the `class_names` attribute.

The `tools` section includes information about the **stedgeai** toolchain, such as the version, optimization level, and path to the `stedgeai.exe` file.

Finally, in the `deployment` section, users must provide information about the hardware setup, such as the series and board of the STM32 device, as well as the input and output interfaces. 
Once all of these sections have been filled in, users can run the deployment service to deploy their model to the STM32 device.

</details></ul>
<ul><details open><summary><a href="#2-10">2.10 Hydra and MLflow settings</a></summary><a id="2-10"></a>
 
The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment directories. In the YAML code below, it is set to save the outputs as explained in the section <a href="#4">visualize the chained services results</a> :

```yaml
hydra:
   run:
      dir: ./experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown below:

```yaml
mlflow:
   uri: ./experiments_outputs/mlruns
```
</details></ul>
</details>
<details open><summary><a href="#3"><b>3. Run the semantic segmentation chained service</b></a></summary><a id="3"></a>

After updating the [user_config.yaml](user_config.yaml) file, please run the following command:

```bash
python stm32ai_main.py
```
* Note that you can provide YAML attributes as arguments in the command, as shown below:

```bash
python stm32ai_main.py operation_mode='chain_tbqeb'
```

</details>
<details open><summary><a href="#4"><b>4. Visualize the chained services results</b></a></summary><a id="4"></a>

Every time you run the Model Zoo, an experiment directory is created that contains all the directories and files created during the run. The names of experiment directories are all unique as they are based on the date and time of the run.

Experiment directories are managed using the Hydra Python package. Refer to [Hydra Home](https://hydra.cc/) for more information about this package.

By default, all the experiment directories are under the <MODEL-ZOO-ROOT>/semantic_segmentation/src/experiments_outputs directory and their names follow the "%Y_%m_%d_%H_%M_%S" pattern.

This is illustrated in the figure below.

```
                                  experiments_outputs
                                          |
                                          |
      +--------------+--------------------+--------------------+
      |              |                    |                    |
      |              |                    |                    |
    mlruns    <date-and-time>        <date-and-time>      <date-and-time> 
      |                                   |              
    MLflow                                +--- stm32ai_main.log
    files                                 +--- training_metrics.csv
                                          +--- training_curves.png
                                          |
                                          |
      +-----------------------------------+--------------------------------+------------+
      |                                   |                                |            |
      |                                   |                                |            |
 saved_models                      quantized_models                       logs        .hydra
      |                                   |                                |            |
      +--- best_augmented_model.h5        +--- quantized_model.h5     TensorBoard     Hydra
      +--- last_augmented_model.h5        +--- optimized_model.h5        files        files
      +--- best_model.h5
```
The optimized_model.h5 is only issued if quantization `granularity` is 'per_tensor' and `optimize` is set to True.

The file named 'stm32ai_main.log' under each experiment directory is the log file saved during the execution of the 'stm32ai_main.py' script. 
The contents of the other files saved under an experiment directory are described in the table below.

|  File             |  Directory | Contents               |
|:-------------------|:-------------------------|:-----------------------|
| best_augmented_model.h5 | saved_models | Best model saved during training, rescaling and data augmentation layers included (Keras) |
| last_augmented_model.h5 | saved_models | Last model saved at the end of a training, rescaling and data augmentation layers included (Keras) |
| best_model.h5           | saved_models | Best model obtained at the end of a training (Keras) |
| quantized_model.tflite  | quantized_models | Quantized model (TFlite) |
| optimized_model.h5      | quantized_models | Optimized model if 'per_tensor' quantization |
| training_metrics.csv    | metrics | Training metrics CSV including epochs, losses, accuracies and learning rate |
| training_curves.png     | metrics | Training learning curves (losses and accuracies) |


All the directory names, including the naming pattern of experiment directories, can be changed using the configuration file. The names of the files cannot be changed.
The models in the 'best_augmented_model.h5' and 'last_augmented_model.h5' Keras files contain rescaling and data augmentation layers. 
These files can be used to resume a training that you interrupted or that crashed. This will be explained in section training service [README](training/README.md). These model files are not intended to be used outside of the Model Zoo context.

<ul><details open><summary><a href="#4-1">4.1 Saved results</a></summary><a id="4-1"></a>

All of the training and evaluation artifacts are saved in the current output simulation directory, which is located at **experiments_outputs/\<date-and-time\>**.

For example, you can retrieve the accuracy and average IoU generated after evaluating the float and the quantized model on the test set in **experiments_outputs/\<date-and-time\>stm32ai_main.log**.
These values are also displayed on your screen for information.


</details></ul>
<ul><details open><summary><a href="#4-2">4.2 Run tensorboard</a></summary><a id="4-2"></a>
 
To visualize the training curves that were logged by TensorBoard, navigate to the **experiments_outputs/\<date-and-time\>** directory and run the following command:

```bash
tensorboard --logdir logs
```
This will start a server and its address will be displayed. Use this address in a web browser to connect to the server. Then, using the web browser, you will able to explore the learning curves and other training metrics.

</details></ul>
<ul><details open><summary><a href="#4-3">4.3 Run MLFlow</a></summary><a id="4-3"></a>

MLflow is an API that allows you to log parameters, code versions, metrics, and artifacts while running machine learning code, and provides a way to visualize the results. 

To view and examine the results of multiple trainings, you can navigate to the **experiments_outputs** directory and access the MLflow Webapp by running the following command:

```bash
mlflow ui
```
This will start a server and its address will be displayed. Use this address in a web browser to connect to the server. Then, using the web browser, you will be able to navigate the different experiment directories and look at the metrics they were collected. Refer to [MLflow Home](https://mlflow.org/) for more information about MLflow.

</details></ul>
</details>

<details open><summary><a href="#A"><b>Appendix A: YAML syntax</b></a></summary><a id="A"></a>

**Example and terminology:**

An example of YAML code is shown below.

```yaml
preprocessing:
   rescaling:
      scale : 1/127.5
      offset : -1
   resizing:
      aspect_ratio: fit
      interpolation: bilinear
```

The code consists of a number of nested "key-value" pairs. The column character is used as a separator between the key and the value.

Indentation is how YAML denotes nesting. The specification forbids tabs because tools treat them differently. A common practice is to use 2 or 3 spaces but you can use any number of them. 

We use "attribute-value" instead of "key-value" as in the YAML terminology, the term "attribute" being more relevant to our application. We may use the term "attribute" or "section" for nested attribute-value pairs constructs. In the example above, we may indifferently refer to "preprocessing" as an attribute (whose value is a list of nested constructs) or as a section.

**Comments:**

Comments begin with a pound sign. They can appear after an attribute value or take up an entire line.

```yaml
preprocessing:
   rescaling:
      scale : 1/127.5   # This is a comment.
      offset : -1
   resizing:
      # This is a comment.
      aspect_ratio: fit
      interpolation: bilinear
   color_mode: rgb
```

**Attributes with no value:**

The YAML language supports attributes with no value. The code below shows the alternative syntaxes you can use for such attributes.

```yaml
attribute_1:
attribute_2: ~
attribute_3: null
attribute_4: None     # Model Zoo extension
```
The value *None* is a Model Zoo extension that was made because it is intuitive to Python users.

Attributes with no value can be useful to list in the configuration file all the attributes that are available in a given section and explicitly show which ones were not used.

**Strings:**

You can enclose strings in single or double quotes. However, unless the string contains special YAML characters, you don't need to use quotes.

This syntax:

```yaml
resizing:
   aspect_ratio: fit
   interpolation: bilinear
```

is equivalent to this one:

```yaml
resizing:
   aspect_ratio: "fit"
   interpolation: "bilinear"
```

**Strings with special characters:**

If a string value includes YAML special characters, you need to enclose it in single or double quotes. In the example below, the string includes the ',' character, so quotes are required.

```yaml
name: "Pepper,_bell___Bacterial_spot"
```

**Strings spanning multiple lines:**

You can write long strings on multiple lines for better readability. This can be done using the '|' (pipe) continuation character as shown in the example below.

This syntax:

```yaml
LearningRateScheduler:
   schedule: |
      lambda epoch, lr:
          (0.0005*epoch + 0.00001) if epoch < 20 else
          (0.01 if epoch < 50 else
          (lr / (1 + 0.0005 * epoch)))
```

is equivalent to this one:

```yaml
LearningRateScheduler:
   schedule: "lambda epoch, lr: (0.0005*epoch + 0.00001) if epoch < 20 else (0.01 if epoch < 50 else (lr / (1 + 0.0005 * epoch)))"
```

Note that when using the first syntax, strings that contain YAML special characters don't need to be enclosed in quotes. In the example above, the string includes the ',' character.

**Booleans:**

The syntaxes you can use for boolean values are shown below. Supported values have been extended to *True* and *False* in the Model Zoo as they are intuitive to Python users.

```yaml
# YAML native syntax
attribute_1: true
attribute_2: false

# Model Zoo extensions
attribute_3: True
attribute_4: False
```

**Numbers and numerical expressions:**

Attribute values can be integer numbers, floating-point numbers or numerical expressions as shown in the YAML code below.

```yaml
ReduceLROnPlateau:
   patience: 10    # Integer value
   factor: 0.1     # Floating-point value
   min_lr: 1e-6    # Floating-point value, exponential notation

rescaling:
   scale: 1/127.5  # Numerical expression, evaluated to 0.00784314
   offset: -1
```

**Lists:**

You can specify lists on a single line or on multiple lines as shown below.
This syntax:

```yaml
class_names: ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
              "car", "cat", "chair", "cow", "dining table", "dog", "horse", "motorbike",
              "person", "potted plant", "sheep", "sofa", "train", "tv/monitor"]
```
is equivalent to this one:

```yaml
class_names:
- background
- aeroplane
- bicycle
- bird
- boat
- ...
```

**Multiple attribute-value pairs on one line:**

Multiple attribute-value pairs can be specified on one line as shown below.

This syntax:

```yaml
rescaling: { scale: 1/127.5, offset: -1 }
```
is equivalent to this one:

```yaml
rescaling:
   scale: 1/127.5,
   offset: -1
```
</details>
