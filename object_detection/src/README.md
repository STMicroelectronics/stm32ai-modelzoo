# Object detection STM32 model zoo
## Table of Contents

### <a href="#1">1. Object detection Model Zoo introduction</a>

### <a href="#2">2. Object detection  tutorial</a>

#### <a href="#2-1">2.1 Choose the operation mode</a>

#### <a href="#2-2">2.2 Global settings</a>

#### <a href="#2-3">2.3 Dataset specification</a>

#### <a href="#2-4">2.4 Apply image preprocessing</a>

#### <a href="#2-5">2.5 Use data augmentation</a>

#### <a href="#2-6">2.6 Set the training parameters</a>

#### <a href="#2-7">2.7 Set the postprocessing parameters</a>

#### <a href="#2-8">2.8 Model quantization</a>

#### <a href="#2-9">2.9 Benchmark the model</a>

#### <a href="#2-10">2.10 Deploy the model</a>

#### <a href="#2-11">2.11 Hydra and MLflow settings</a>

### <a href="#3">3. Run the Object detection chained service</a>

### <a href="#4">4. Visualize chained service results</a>

#### <a href="#4-1">4.1 Saved results</a></a>

#### <a href="#4-2">4.2 Run tensorboard</a>

#### <a href="#4-3">4.3 Run MLFlow</a>

#### <a href="appendix-a">Appendix A: YAML syntax</a>

__________________________________________

### <a id="1">1. Object detection Model Zoo introduction</a>

The object detection model zoo provides a collection of independent services and pre-built chained services that can be
used to perform various functions related to machine learning for Object detection. The individual services include
tasks such as training the model or quantizing the model, while the chained services combine multiple services to
perform more complex functions, such as training the model, quantizing it, and evaluating the quantized model
successively.

To use the services in the Object detection model zoo, you can utilize the model
zoo [stm32ai_main.py](stm32ai_main.py) along with [user_config.yaml](user_config.yaml) file as input. The yaml file
specifies the service or the chained services and a set of configuration parameters such as the model (either from the
model zoo or your own custom model), the dataset, the number of epochs, and the preprocessing parameters, among others.

More information about the different services and their configuration options can be found in the <a href="#2">next
section</a>.

The object detection datasets are expected to be in YOLO Darknet TXT format. For this project, we are using the Pascal
VOC 2012 dataset, which can be downloaded directly in YOLO Darknet TXT format
from [here](https://public.roboflow.com/object-detection/pascal-voc-2012/1/download/darknet).

An example of this structure is shown below:

```yaml
<dataset-root-directory>
train/:
  train_image_1.jpg
  train_image_1.txt
  train_image_2.jpg
  train_image_2.txt
val/:
  val_image_1.jpg,
  val_image_1.txt
  val_image_2.jpg,
  val_image_2.txt
```

### <a id="2">2. Object detection tutorial</a>

This tutorial demonstrates how to use the `chain_tqeb` services to train, benchmark, quantize, evaluate, and benchmark
the model.

To get started, you will need to update the [user_config.yaml](user_config.yaml) file, which specifies the parameters
and configuration options for the services that you want to use. Each section of
the [user_config.yaml](user_config.yaml) file is explained in detail in the following sections.

#### <a id="2-1">2.1 Choose the operation mode</a>

The `operation_mode` top-level attribute specifies the operations or the service you want to executed. This may be
single operation or a set of chained operations.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table
below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for
benchmark and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations                                                                                                                                          |
|:-------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| `training`               | Train a model from the variety of object detection models in the model zoo or your own model                                                        |
| `evaluation`             | Evaluate the accuracy of a float or quantized model on a test or validation dataset                                                                 |
| `quantization`           | Quantize a float model                                                                                                                              |
| `prediction`             | Predict the classes and bounding boxes of some images using a float or quantized model.                                                             |
| `benchmarking`           | Benchmark a float or quantized model on an STM32 board                                                                                              |
| `deployment`             | Deploy a model on an STM32 board                                                                                                                    |
| `chain_tqeb`             | Sequentially: training, quantization of trained model, evaluation of quantized model, benchmarking of quantized model                               |
| `chain_tqe`              | Sequentially: training, quantization of trained model, evaluation of quantized model                                                                |
| `chain_eqe`              | Sequentially: evaluation of a float model, quantization, evaluation of the quantized model                                                          |
| `chain_qb`               | Sequentially: quantization of a float model, benchmarking of quantized model                                                                        |
| `chain_eqeb`             | Sequentially: evaluation of a float model, quantization, evaluation of quantized model, benchmarking of quantized model                             |
| `chain_qd`               | Sequentially: quantization of a float model, deployment of quantized model                                                                          |

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific
services:

- [training, chain_tqe, chain_tqeb](./training/README.md)
- [quantization, chain_eqe, chain_qb](./quantization/README.md)
- [evaluation, chain_eqeb](./evaluation/README.md)
- [benchmarking](./benchmarking/README.md)
- [deployment, chain_qd](../deployment/README.md)

In this tutorial the `operation_mode` used is the `chain_tqeb` like shown below to train a model, quantize,
evaluate it to be later deployed in the STM32 boards.

```yaml
operation_mode: chain_tqeb
```

#### <a id="2-2">2.2 Global settings</a>

The `general` section and its attributes are shown below.

```yaml
general:
  project_name: Pascal_VOC_2012_Demo           # Project name. Optional, defaults to "<unnamed>".
  model_type: st_ssd_mobilenet_v1   # Name of the model 
  logs_dir: logs                    # Name of the directory where log files are saved. Optional, defaults to "logs".
  saved_models_dir: saved_models    # Name of the directory where model files are saved. Optional, defaults to "saved_models".
  #  model_path: <file-path>           # Path to a model file.
  global_seed: 123                  # Seed used to seed random generators (an integer). Optional, defaults to 123.
  deterministic_ops: False          # Enable/disable deterministic operations (a boolean). Optional, defaults to False.
  display_figures: True             # Enable/disable the display of figures (training learning curves and confusion matrices).
  # Optional, defaults to True.
  gpu_memory_limit: 16              # Maximum amount of GPU memory in GBytes that TensorFlow may use (an integer).
```

The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy and Tensorflow random
generators at the beginning of the main script. This is an optional attribute, the default value being 123. If you don't
want random generators to be seeded, then set `global_seed` to 'None' (not recommended as this would make training
results less reproducible).

Even when random generators are seeded, it is often difficult to exactly reproduce results when the same operation is
run multiple times. This typically happens when the same training script is run on different hardware.
The `deterministic_ops` operator can be used to enable the deterministic mode of Tensorflow. If enabled, an operation
that uses the same inputs on the same hardware will have the exact same outputs every time it is run. However,
determinism should be used carefully as it comes at the expense of longer run times. Refer to the Tensorflow
documentation for more details.

The `gpu_memory_limit` attribute sets an upper limit in GBytes on the amount of GPU memory Tensorflow may use. This is
an optional attribute with no default value. If it is not present, memory usage is unlimited. If you have several GPUs,
be aware that the limit is only set on logical gpu[0].

The `model_path` attribute is utilized to indicate the path to the model file that you wish to use for the selected
operation mode. The accepted formats for `model_path` are listed in the table below:

The `model_type` attribute specifies the type of the model architecture that you want to train. It is important to note
that only certain models are supported. These models include:

- `tiny_yolo_v2`: This is a lightweight version of the YOLO (You Only Look Once) object detection algorithm. It is
  designed
  to work well on embedded devices with limited computational resources.

- `ssd_mobilenet_v2_fpnlite`: This is a Single Shot Detector (SSD) architecture that uses a MobileNetV2 backbone and a
  Feature Pyramid Network (FPN) head. It is designed to be fast and accurate, and is well-suited for use cases where
  real-time object detection is required.

- `st_ssd_mobilenet_v1 `: This is a variant of the SSD architecture that uses a MobileNetV1 backbone and a custom
  head(ST). It is designed to be robust to scale and orientation changes in the input images.

It is important to note that each model type has specific requirements in terms of input image size, output size of the
head and/or backbone, and other parameters. Therefore, it is important to choose the appropriate model type for your
specific use case, and to configure the training process accordingly.

| Operation mode | `model_path` |
|:---------------|:-------------|
| 'evaluation'   | Keras or TF-Lite model file |
| 'quantization', 'chain_eqe', 'chain_eqeb', 'chain_qb', 'chain_qd' | Keras model file |
| 'prediction'   | Keras or TF-Lite model file |
| 'benchmarking' | Keras, TF-Lite or ONNX model file |
| 'deployment'   | TF-Lite model file |

If you are using an operation mode that involves training, you can use the `model_path` attribute to train your own
custom model instead of using a model from the Model Zoo. This is explained in detail in
the [readme](./training/README.md) file for the train service. However, in this tutorial, the `model_path` attribute is
not used since we are using a pre-trained model from the Model Zoo.

#### <a id="2-3">2.3 Dataset specification</a>

The `dataset` section and its attributes are shown in the YAML code below.

```yaml
dataset:
  dataset_name: Pascal_VOC_2012                                    # Dataset name. Optional, defaults to "<unnamed>".
  class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ] # Names of the classes in the dataset.
  training_path: <training-set-root-directory>               # Path to the root directory of the training set.
  validation_path: <validation-set-root-directory>           # Path to the root directory of the validation set.
  validation_split: 0.2                                      # Training/validation sets split ratio.
  test_path: <test-set-root-directory>                       # Path to the root directory of the test set.
  quantization_path: <quantization-set-root-directory>       # Path to the root directory of the quantization set.
  quantization_split:                                        # Quantization split ratio.
  seed: 123                                                  # Random generator seed used when splitting a dataset.
```

The `name` attribute is optional and can be used to specify the name of your dataset.

When a training is run, the training set is split in two to create a validation dataset if `validation_path` is not
provided. When a model accuracy evaluation is run, the test set is used if there is one, otherwise the validation set is
used (either provided or generated by splitting the training set).

The `validation_split` attribute specifies the training/validation set size ratio to use when splitting the training set
to create a validation set. The default value is 0.2, meaning that 20% of the training set is used to create the
validation set. The `seed` attribute specifies the seed value to use for randomly shuffling the dataset file before
splitting it (default value is 123).

The `quantization_path` attribute is used to specify a dataset for the quantization process. If this attribute is not
provided and a training set is available, the training set is used for the quantization. However, training sets can be
quite large and the quantization process can take a long time to run. To avoid this issue, you can set
the `quantization_split` attribute to use only a portion of the dataset for quantization.

#### <a id="2-4">2.4 Apply image preprocessing</a>

Object detection requires images to be preprocessed by rescaling and resizing them before they can be used. This is
specified in the 'preprocessing' section, which is mandatory in all operation modes. Additionally, bounding boxes should
be processed along with the images to accurately detect objects in the images.
This is specified in the 'preprocessing' section that is required in all the operation modes.

The 'preprocessing' section for this tutorial is shown below.

```yaml
preprocessing:
  rescaling:
    # Image rescaling parameters
    scale: 1/127.5
    offset: -1
  resizing:
    # Image resizing parameters
    interpolation: bilinear
    aspect_ratio: fit
  color_mode: rgb
```

Images are rescaled using the formula "Out = scale\*In + offset". Pixel values of input images usually are integers in
the interval [0, 255]. If you set *scale* to 1./255 and offset to 0, pixel values are rescaled to the
interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they are rescaled to the interval [-1.0, 1.0].

The resizing interpolation methods that are supported include 'bilinear', 'nearest', 'bicubic', 'area', 'lanczos3', '
lanczos5', 'gaussian' and 'mitchellcubic'. Refer to the Tensorflow documentation of the tf.image.resize function for
more detail.

Please note that the 'fit' option is the only supported option for the `aspect_ratio` attribute. When using this option,
the images will be resized to fit the target size. It is important to note that input images may be smaller or larger
than the target size, and will be distorted to some extent if their original aspect ratio is not the same as the
resizing aspect ratio. Additionally, bounding boxes should be adjusted to maintain their relative positions and sizes in
the resized images.

The `color_mode` attribute can be set to either *"grayscale"*, *"rgb"* or *"rgba"*.

#### <a id="2-5">2.5 Use data augmentation</a>

The data augmentation functions to apply to the input images during a training are specified in the
optional `data_augmentation` section of the configuration file. They are only applied to the images during training.

For this tutorial data augmentation section is shown below.

```yaml
data_augmentation:
  rotation: 30
  shearing: 15
  translation: 0.1
  vertical_flip: 0.5
  horizontal_flip: 0.2
  gaussian_blur: 3.0
  linear_contrast: [ 0.75, 1.5 ]
```

When applying data augmentation for object detection, it is important to take into account both the augmentation of the
input images and the modification of the annotations file to ensure that the model is trained on accurate and
representative data.

#### <a id="2-6">2.6 Set the training parameters</a>

A 'training' section is required in all the operation modes that include a training, namely 'training', chain_tqeb'
and 'chain_tqe'.
In this tutorial, we will be using a custom object detection model called st_ssd_mobilenet_v1. This model is a custom
SSD (
Single Shot Detector) model that uses MobileNetv1 as its backbone. The backbone weights have been pre-trained on the
ImageNet dataset, which is a large dataset consisting of 1.4 million images and 1000 classes.

As an example, we will be using our custom st_ssd_mobilenet_v1 model, which uses a MobileNet V1 with an alpha value of
0.25 as its backbone, to do
so we will
need to configure the model section in [user_config.yaml](user_config.yaml) as the following:

```yaml
training:
  model:
    alpha: 0.25
    input_shape: (192, 192, 3)
    pretrained_weights: imagenet
  bach_size: 64
  epochs: 150
  dropout:
  frozen_layers: (0, -1)   # Make all layers non-trainable except the last one
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
      monitor: val_loss
      mode: max
      restore_best_weights: true
      patience: 60
```

The `model` subsection is used to specify a model that is available with the Model Zoo:

- The `input_shape` attribute must always be present.
- Additional attributes are needed depending on the type of model. For example, an `alpha` attribute is required for
  SSD MobileNet models.
- The optional `pretrained_weights` attribute can be used to load pretrained weights in the model before it gets
  trained. By default, no pretrained weights are loaded.

The `batch_size` and `epochs` attributes are mandatory.

The `dropout_rate` attribute is optional. By default, no dropout layer is inserted in the model.

All the Keras optimizers are supported. If you are not passing any argument to the optimizer, you may write it on one
line. For example: "optimizer: Adam".

The optional `frozen_layers` attribute is used to make some layers of the model non-trainable. Together with
the `pretrained_weights` attribute of the `model` subsection, it is useful when a transfer learning approach is used to
train the model. Another attribute of the `model` subsection called `pretrained_weights`is also available to load the
weights from another model (not shown in the YAML code above). Transfer learning is covered in the "Transfer learning"
section of the documentation.

The `callbacks` subsection is optional. All the Keras callbacks are supported. Note that several callbacks are built-in
and cannot be redefined, including ModelCheckpoint, TensorBoard and CSVLoggerr.

A variety of learning rate schedulers are provided with the Model Zoo. If you want to use one of them, just include it
in the `callbacks` subsection. Refer to the training service [README](training/README.md) for a description of the
available callbacks and learning rate plotting utility.

The best model obtained at the end of the training is saved in the 'experiments_outputs/\<date-and-time\>/saved_models'
directory and is called 'best_model.h5' (see section <a href="#4">visualize the chained services results</a>).

#### <a id="2-7">2.7 Set the postprocessing parameters</a>

A 'postprocessing' section is required in all operation modes for object detection models. This section includes
parameters such as NMS threshold, confidence threshold, IoU evaluation threshold, and maximum detection boxes. These
parameters are necessary for proper post-processing of object detection results.

```yaml
postprocessing:
  confidence_thresh: 0.6
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.3
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 10
```

The `NMS_thresh (Non-Maximum SuppressionThreshold)`: This parameter controls the overlapping bounding boxes that are
considered as
separate detections. A higher NMS threshold will result in fewer detections, while a lower threshold will result in more
detections. To improve object detection, you can experiment with different NMS thresholds to find the optimal value for
your specific use case.

The `confidence_thresh`: This parameter controls the minimum confidence score required for a detection to be
considered
valid. A higher confidence threshold will result in fewer detections, while a lower threshold will result in more
detections.
the `IoU_eval_thresh`: This parameter controls the minimum overlap required between two
bounding boxes for them to be considered as the same object. A higher IoU threshold will result in fewer detections,
while a lower threshold will result in more detections.

The `max_detection_boxes` : This parameter controls the maximum number of detections that can be output by the
object
detection model. A higher maximum detection boxes value will result in more detections, while a lower value will result
in fewer detections.
The `plot_metrics`  parameter is an optional parameter in the object detection model that controls whether or not to
plot the precision versus recall curves. By default, this parameter is set to False, which means that the precision
versus recall curves will not be plotted. If you set this parameter to True, the object detection model will generate
and display the precision versus recall curves, which can be helpful for evaluating the performance of the model.

Overall, improving object detection requires careful tuning of these post-processing parameters based on your specific
use case. Experimenting with different values and evaluating the results can help you find the optimal values for your
object detection model.

#### <a id="2-8">2.8 Model quantization</a>

Configure the quantization section in [user_config.yaml](user_config.yaml) as the following:

```yaml

quantization:
  quantizer: TFlite_converter
  quantization_type: PTQ
  quantization_input_type: float
  quantization_output_type: uint8
  export_dir: quantized_models       # Optional, defaults to "quantized_models".
```

This section is used to configure the quantization process, which optimizes the model for efficient deployment on
embedded devices by reducing its memory usage (Flash/RAM) and accelerating its inference time, with minimal degradation
in model accuracy. The `quantizer` attribute expects the value "TFlite_converter", which is used to convert the trained
model weights from float to integer values and transfer the model to a TensorFlow Lite format.

The `quantization_type` attribute only allows the value "PTQ," which stands for Post Training Quantization. To specify
the quantization type for the model input and output, use the `quantization_input_type` and `quantization_output_type`
attributes, respectively.

The `quantization_input_type` attribute is a string that can be set to "int8", "uint8," or "float" to represent the
quantization type for the model input. Similarly, the `quantization_output_type` attribute is a string that can be set
to "int8", "uint8," or "float" to represent the quantization type for the model output.

By default, the quantized model is saved in the 'quantized_models' directory under the 'experiments_outputs' directory.
You may use the optional `export_dir` attribute to change the name of this directory.

#### <a id="2-9">2.9 Benchmark the model</a>

The [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) allows you to benchmark your model and estimate its
footprints and inference time for different STM32 target devices. To use this feature, set the `on_cloud` attribute to
True. Alternatively, you can use [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) to benchmark
your model and estimate its footprints for STM32 target devices locally. To do this, make sure to add the path to
the `stm32ai` executable under the `path_to_stm32ai` attribute and set the `on_cloud` attribute to False.

The `version` attribute to specify the **STM32Cube.AI** version used to benchmark the model, e.g. 8.1.0 and
the `optimization` defines the optimization used to generate the C model, options: "balanced", "time", "ram".

The `board` attribute is used to provide the name of the STM32 board to benchmark the model on. The available boards
are 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32F469I-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-H743ZI2', '
STM32H747I-DISCO', 'STM32H735G-DK', 'STM32F769I-DISCO', 'NUCLEO-G474RE', 'NUCLEO-F401RE' and 'STM32F746G-DISCO'.

```yaml
tools:
  stm32ai:
    version: 8.1.0
    optimization: balanced
    on_cloud: True
    path_to_stm32ai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stm32ai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_1.10.1/STM32CubeIDE/stm32cubeide.exe

benchmarking:
  board: STM32H747I-DISCO     # Name of the STM32 board to benchmark the model on
```

The `path_to_cubeIDE` attribute is for the [deployment](../deployment/README.md) service which is not part the
chain `chain_tqeb` used in this tutorial.

#### <a id="2-10">2.10 Deploy the model</a>

In this tutorial, we are using the `chain_tqeb` toolchain, which does not include the deployment service. However, if
you want to deploy the model after running the chain, you can do so by referring to
the [README](../deployment/README.md) and modifying the `deployment_config.yaml` file or by setting the `operation_mode`
to `deploy` and modifying the `user_config.yaml` file as described below:

```yaml
general:
  model_path: <path-to-a-TFlite-model-file>     # Path to the model file to deploy

dataset:
  class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ]

postprocessing:
  confidence_thresh: 0.6
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.3
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 10

tools:
  stm32ai:
    version: 8.1.0
    optimization: balanced
    on_cloud: True
    path_to_stm32ai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stm32ai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_1.10.1/STM32CubeIDE/stm32cubeide.exe

deployment:
  c_project_path: ../../stm32ai_application_code/object_detection/
  IDE: GCC
  verbosity: 1
  hardware_setup:
    serie: STM32H7
    board: STM32H747I-DISCO
    input: CAMERA_INTERFACE_DCMI
    output: DISPLAY_INTERFACE_USB
```

In the `general` section, users must provide the path to the TFlite model file that they want to deploy using
the `model_path` attribute.

The `dataset` section requires users to provide the names of the classes using the `class_names` attribute.

The `postprocessing` section requires users to provide the values for the post-processing parameters. These parameters
include the `NMS_thresh`, `confidence_thresh`, `IoU_eval_thresh`, and `max_detection_boxes`. By providing
these values in the postprocessing section, the object detection model can properly post-process the results and
generate accurate detections. It is important to carefully tune these parameters based on your specific use case to
achieve optimal performance.

The `tools` section includes information about the STM32AI toolchain, such as the version, optimization level, and path
to the `stm32ai.exe` file.

Finally, in the `deployment` section, users must provide information about the hardware setup, such as the series and
board of the STM32 device, as well as the input and output interfaces. Once all of these sections have been filled in,
users can run the deployment service to deploy their model to the STM32 device.

#### <a id="2-11">2.11 Hydra and MLflow settings</a>

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used
to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment
directories. In the YAML code below, it is set to save the outputs as explained in the section <a id="4">visualize the
chained services results</a>:

```yaml
hydra:
  run:
    dir: ./experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown
below:

```yaml
mlflow:
  uri: ./experiments_outputs/mlruns
```

### <a id="3">3. Run the object detection chained service</a>

After updating the [user_config.yaml](user_config.yaml) file, please run the following command:

```bash
python stm32ai_main.py
```

* Note that you can provide YAML attributes as arguments in the command, as shown below:

```bash
python stm32ai_main.py operation_mode='chain_eb'
```

### <a id="4">4. Visualize the chained services results</a>

Every time you run the Model Zoo, an experiment directory is created that contains all the directories and files created
during the run. The names of experiment directories are all unique as they are based on the date and time of the run.

Experiment directories are managed using the Hydra Python package. Refer to [Hydra Home](https://hydra.cc/) for more
information about this package.

By default, all the experiment directories are under the <MODEL-ZOO-ROOT>/object_detection/src/experiments_outputs
directory and their names follow the "%Y_%m_%d_%H_%M_%S" pattern.

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
                                          +--- float_model_confusion_matrix_validation_set.png
                                          |
      +-----------------------------------+--------------------------------+------------+
      |                                   |                                |            |
      |                                   |                                |            |
 saved_models                      quantized_models                       logs        .hydra
      |                                   |                                |            |
      +--- best_augmented_model.h5        +--- quantized_model.h5     TensorBoard     Hydra
      +--- last_augmented_model.h5                                       files        files
      +--- best_model.h5
```

The file named 'stm32ai_main.log' under each experiment directory is the log file saved during the execution of the '
stm32ai_main.py' script. The contents of the other files saved under an experiment directory are described in the table
below.

|  File             |  Directory | Contents               |
|:-------------------|:-------------------------|:-----------------------|
| best_augmented_model.h5 | saved_models | Best model saved during training, rescaling and data augmentation layers included (Keras) |
| last_augmented_model.h5 | saved_models | Last model saved at the end of a training, rescaling and data augmentation layers included (Keras) |
| best_model.h5           | saved_models | Best model obtained at the end of a training (Keras) |
| quantized_model.tflite  | quantized_models | Quantized model (TFlite) |
| training_metrics.csv    | metrics | Training metrics CSV including epochs, losses, accuracies and learning rate |
| training_curves.png     | metrics | Training learning curves (losses and accuracies) |
| float_model_confusion_matrix_test_set.png | metrics | Float model confusion matrix | 
| quantized_model_confusion_matrix_test_set.png | metrics | Quantized model confusion matrix |

All the directory names, including the naming pattern of experiment directories, can be changed using the configuration
file. The names of the files cannot be changed.
s
The models in the 'best_augmented_model.h5' and 'last_augmented_model.h5' Keras files contain rescaling and data
augmentation layers. These files can be used to resume a training that you interrupted or that crashed. This will be
explained in section training service [README](training/README.md). These model files are not intended to be used
outside of the Model Zoo context.

#### <a id="4-1">4.1 Saved results</a>

All of the training and evaluation artifacts are saved in the current output simulation directory, which is located
at **experiments_outputs/\<date-and-time\>**.

For example, you can retrieve the confusion matrix generated after evaluating the float and the quantized model on the
test set by navigating to the appropriate directory within **experiments_outputs/\<date-and-time\>**.

#### <a id="4-2">4.2 Run tensorboard</a>

To visualize the training curves that were logged by TensorBoard, navigate to the **
experiments_outputs/\<date-and-time\>** directory and run the following command:

```bash
tensorboard --logdir logs
```

This will start a server and its address will be displayed. Use this address in a web browser to connect to the server.
Then, using the web browser, you will able to explore the learning curves and other training metrics.

#### <a id="4-3">4.3 Run MLFlow</a>

MLflow is an API that allows you to log parameters, code versions, metrics, and artifacts while running machine learning
code, and provides a way to visualize the results.

To view and examine the results of multiple trainings, you can navigate to the **experiments_outputs** directory and
access the MLflow Webapp by running the following command:

```bash
mlflow ui
```

This will start a server and its address will be displayed. Use this address in a web browser to connect to the server.
Then, using the web browser, you will be able to navigate the different experiment directories and look at the metrics
they were collected. Refer to [MLflow Home](https://mlflow.org/) for more information about MLflow.

### <a id="appendix-a">Appendix A: YAML syntax</a>

**Example and terminology:**

An example of YAML code is shown below.

```yaml
preprocessing:
  rescaling:
    scale: 1/127.5
    offset: -1
  resizing:
    aspect_ratio: fit
    interpolation: bilinear
```

The code consists of a number of nested "key-value" pairs. The column character is used as a separator between the key
and the value.

Indentation is how YAML denotes nesting. The specification forbids tabs because tools treat them differently. A common
practice is to use 2 or 3 spaces but you can use any number of them.

We use "attribute-value" instead of "key-value" as in the YAML terminology, the term "attribute" being more relevant to
our application. We may use the term "attribute" or "section" for nested attribute-value pairs constructs. In the
example above, we may indifferently refer to "preprocessing" as an attribute (whose value is a list of nested
constructs) or as a section.

**Comments:**

Comments begin with a pound sign. They can appear after an attribute value or take up an entire line.

```yaml
preprocessing:
  rescaling:
    scale: 1/127.5   # This is a comment.
    offset: -1
  resizing:
    # This is a comment.
    aspect_ratio: fit
    interpolation: bilinear
  color_mode: rgb
```

**Attributes with no value:**

The YAML language supports attributes with no value. The code below shows the alternative syntaxes you can use for such
attributes.

```yaml
attribute_1:
attribute_2: ~
attribute_3: null
attribute_4: None     # Model Zoo extension
```

The value *None* is a Model Zoo extension that was made because it is intuitive to Python users.

Attributes with no value can be useful to list in the configuration file all the attributes that are available in a
given section and explicitly show which ones were not used.

**Strings:**

You can enclose strings in single or double quotes. However, unless the string contains special YAML characters, you
don't need to use quotes.

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

If a string value includes YAML special characters, you need to enclose it in single or double quotes. In the example
below, the string includes the ',' character, so quotes are required.

```yaml
name: "Pepper,_bell___Bacterial_spot"
```

**Strings spanning multiple lines:**

You can write long strings on multiple lines for better readability. This can be done using the '|' (pipe) continuation
character as shown in the example below.

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

Note that when using the first syntax, strings that contain YAML special characters don't need to be enclosed in quotes.
In the example above, the string includes the ',' character.

**Booleans:**

The syntaxes you can use for boolean values are shown below. Supported values have been extended to *True* and *False*
in the Model Zoo as they are intuitive to Python users.

```yaml
# YAML native syntax
attribute_1: true
attribute_2: false

# Model Zoo extensions
attribute_3: True
attribute_4: False
```

**Numbers and numerical expressions:**

Attribute values can be integer numbers, floating-point numbers or numerical expressions as shown in the YAML code
below.

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
class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ]
```

is equivalent to this one:

```yaml
class_names:
  - aeroplane
  - bicycle
  - bird
  - sunflowers
  - boat ...

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
