# Pose estimation STM32 model zoo

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Pose estimation Model Zoo introduction</b></a></summary><a id="1"></a>

The pose estimation model zoo provides a collection of independent services and pre-built chained services that can be
used to perform various functions related to machine learning for Pose estimation. The individual services include
tasks such as evaluating or quantizing the model, while the chained services combine multiple services to
perform more complex functions, such as evaluating the float model, quantizing it, and evaluating the quantized model
successively.

To use the services in the Pose estimation model zoo, you can utilize the model
zoo [stm32ai_main.py](stm32ai_main.py) along with [user_config.yaml](user_config.yaml) file as input. The yaml file
specifies the service or the chained services and a set of configuration parameters such as the model (either from the
model zoo or your own custom model), the dataset, the number of epochs, and the preprocessing parameters, among others.

More information about the different services and their configuration options can be found in the <a href="#2">next
section</a>.

The pose estimation datasets are expected to be in YOLO Darknet TXT format. For this project, we are using the COCO2017 pose dataset, which can be downloaded from [here](https://cocodataset.org/) then converted to YOLO Darknet TXT format.

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

</details>
<details open><summary><a href="#2"><b>2. Pose estimation tutorial</b></a></summary><a id="2"></a>

This tutorial demonstrates how to use the `chain_eqeb` services to evaluate, quantize, evaluate, and benchmark
the model.

To get started, you will need to update the [user_config.yaml](user_config.yaml) file, which specifies the parameters
and configuration options for the services that you want to use. Each section of
the [user_config.yaml](user_config.yaml) file is explained in detail in the following sections.

<ul><details open><summary><a href="#2-1">2.1 Choose the operation mode</a></summary><a id="2-1"></a>

The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be
single operation or a set of chained operations.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table
below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for
benchmark and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations                                                                                                                                          |
|:-------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| `evaluation`             | Evaluate the accuracy of a float or quantized model on a test or validation dataset                                                                 |
| `quantization`           | Quantize a float model                                                                                                                              |
| `prediction`             | Predict the classes and bounding boxes of some images using a float or quantized model.                                                             |
| `benchmarking`           | Benchmark a float or quantized model on an STM32 board                                                                                              |
| `deployment`             | Deploy a model on an STM32 board                                                                                                                    |
| `chain_eqe`              | Sequentially: evaluation of a float model, quantization, evaluation of the quantized model                                                          |
| `chain_qb`               | Sequentially: quantization of a float model, benchmarking of quantized model                                                                        |
| `chain_eqeb`             | Sequentially: evaluation of a float model, quantization, evaluation of quantized model, benchmarking of quantized model                             |
| `chain_qd`               | Sequentially: quantization of a float model, deployment of quantized model                                                                          |

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific
services:

- [quantization, chain_eqe, chain_qb](./quantization/README.md)
- [evaluation, chain_eqeb](./evaluation/README.md)
- [benchmarking](./benchmarking/README.md)
- [deployment, chain_qd](../deployment/README.md)

In this tutorial the `operation_mode` used is the `chain_eqeb` like shown below to evaluate a model, quantize,
evaluate it to be later deployed in the STM32 boards.

```yaml
operation_mode: chain_eqeb
```

</details></ul>
<ul><details open><summary><a href="#2-2">2.2 Global settings</a></summary><a id="2-2"></a>

The `general` section and its attributes are shown below.

```yaml
general:
  project_name: COCO2017_pose_Demo  # Project name. Optional, defaults to "<unnamed>".
  model_type: yolo_mpe              # Name of the model 
  logs_dir: logs                    # Name of the directory where log files are saved. Optional, defaults to "logs".
  saved_models_dir: saved_models    # Name of the directory where model files are saved. Optional, defaults to "saved_models".
  #  model_path: <file-path>           # Path to a model file.
  global_seed: 123                  # Seed used to seed random generators (an integer). Optional, defaults to 123.
  deterministic_ops: False          # Enable/disable deterministic operations (a boolean). Optional, defaults to False.
  display_figures: True             # Enable/disable the display of figures (training learning curves and confusion matrices).
  # Optional, defaults to True.
  gpu_memory_limit: 16              # Maximum amount of GPU memory in GBytes that TensorFlow may use (an integer).
  num_threads_tflite: 4             # Number of threads for tflite interpreter. Optional, defaults to 1
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

The `num_threads_tflite` parameter is only used as an input parameter for the tflite interpreter. Therefore, it has no effect on .h5 or .onnx models. 
This parameter may accelerate the tflite model evaluation in the following operation modes:  `evaluation` (if a .tflite is specified in `model_path`), 
`chain_eqe`, and `chain_eqeb` (if the quantizer is the TFlite_converter). 
However, the acceleration depends on your system resources.

The `model_path` attribute is utilized to indicate the path to the model file that you wish to use for the selected
operation mode. The accepted formats for `model_path` are listed in the table below:

The `model_type` attribute specifies the type of the model architecture that you want to train. It is important to note
that only certain models are supported. These models include:

- `spe`: These are single pose estimation models that outputs directly the keypoints positions and confidences.

- `heatmaps_spe`: These are single pose estimation models that outputs heatmaps that we must 
post-process in order to get the keypoints positions and confidences.

- `yolo_mpe `: These are the YOLO (You Only Look Once) multiple pose estimation models that outputs the same tensor 
as in object detection but with the addition of a set of keypoints for each bbox.

It is important to note that each model type has specific requirements in terms of input image size, output size of the
head and/or backbone, and other parameters. Therefore, it is important to choose the appropriate model type for your
specific use case.

| Operation mode | `model_path` |
|:---------------|:-------------|
| 'evaluation'   | Keras or TF-Lite model file |
| 'quantization', 'chain_eqe', 'chain_eqeb', 'chain_qb', 'chain_qd' | Keras model file |
| 'prediction'   | Keras or TF-Lite model file |
| 'benchmarking' | Keras, TF-Lite or ONNX model file |
| 'deployment'   | TF-Lite model file |

</details></ul>
<ul><details open><summary><a href="#2-3">2.3 Dataset specification</a></summary><a id="2-3"></a>

The `dataset` section and its attributes are shown in the YAML code below.

```yaml
dataset:
  keypoints: 17                                              # Number of keypoints per poses
  dataset_name: COCO2017_pose                                # Dataset name. Optional, defaults to "<unnamed>".
  training_path: <training-set-root-directory>               # Path to the root directory of the training set.
  validation_path: <validation-set-root-directory>           # Path to the root directory of the validation set.
  validation_split: 0.2                                      # Training/validation sets split ratio.
  test_path: <test-set-root-directory>                       # Path to the root directory of the test set.
  quantization_path: <quantization-set-root-directory>       # Path to the root directory of the quantization set.
  quantization_split:                                        # Quantization split ratio.
  seed: 123                                                  # Random generator seed used when splitting a dataset.
```

The `name` attribute is optional and can be used to specify the name of your dataset.

When `training_path` is set, the training set is splited in two to create a validation dataset if `validation_path` is not
provided. When a model accuracy evaluation is run, the `test_path` is used if there is one, otherwise the `validation_path` is
used (either provided or generated by splitting the training set).

The `validation_split` attribute specifies the training/validation set size ratio to use when splitting the training set
to create a validation set. The default value is 0.2, meaning that 20% of the training set is used to create the
validation set. The `seed` attribute specifies the seed value to use for randomly shuffling the dataset file before
splitting it (default value is 123).

The `quantization_path` attribute is used to specify a dataset for the quantization process. If this attribute is not
provided and a training set is available, the training set is used for the quantization. However, training sets can be
quite large and the quantization process can take a long time to run. To avoid this issue, you can set
the `quantization_split` attribute to use only a portion of the dataset for quantization.

</details></ul>
<ul><details open><summary><a href="#2-4">2.4 Apply image preprocessing</a></summary><a id="2-4"></a>

Pose estimation requires images to be preprocessed by rescaling and resizing them before they can be used. This is
specified in the 'preprocessing' section, which is mandatory in all operation modes.

The 'preprocessing' section for this tutorial is shown below.

```yaml
preprocessing:
  rescaling:
    # Image rescaling parameters
    scale: 1/127.5
    offset: -1
  resizing:
    # Image resizing parameters
    interpolation: nearest
    aspect_ratio: fit
  color_mode: rgb
```

Images are rescaled using the formula "Out = scale\*In + offset". Pixel values of input images usually are integers in
the interval [0, 255]. If you set *scale* to 1./255 and offset to 0, pixel values are rescaled to the
interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they are rescaled to the interval [-1.0, 1.0].

The resizing interpolation methods that are supported include 'bilinear', 'nearest', 'bicubic', 'area', 'lanczos3', '
lanczos5', 'gaussian' and 'mitchellcubic'. Refer to the Tensorflow documentation of the tf.image.resize function for
more detail.

The supported `aspect_ratio` attributes are 'fit' and 'padding'. When using this option,
the images will be resized to fit the target size. It is important to note that input images may be smaller or larger
than the target size, and will be distorted ('fit') or paddded ('padding') to some extent if their original aspect ratio is not the same as the
resizing aspect ratio. Additionally, bounding boxes and keypoints should be adjusted to maintain their relative positions and sizes in
the resized images.

The `color_mode` attribute can be set to either *"grayscale"*, *"rgb"* or *"rgba"*.

</details></ul>
<ul><details open><summary><a href="#2-6">2.6 Set the training parameters</a></summary><a id="2-6"></a>

For the moment, this section is only used to set the batch size of all datasets.
This is usefull to accelerate evaluation or quantization.

Please note that some models don't support bach_size different from 1.

```yaml
training:
  bach_size: 64
```

The `batch_size` attributes sets the number of images to be used simultaneously during an inference.

</details></ul>
<ul><details open><summary><a href="#2-7">2.7 Set the postprocessing parameters</a></summary><a id="2-7"></a>

A 'postprocessing' section is required in all operation modes for object detection models. This section includes
parameters such as NMS threshold, confidence threshold, IoU evaluation threshold, and maximum detection boxes. These
parameters are necessary for proper post-processing of object detection results.

```yaml
postprocessing:
  kpts_conf_thresh: 0.15
  confidence_thresh: 0.001
  NMS_thresh: 0.1
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 100
```

The `kpts_conf_thresh`: This parameter controls the visualization of the keypoints, 
if a keypoint's confidence is lower than this parameter, his color is turned from blue to red and its skeleton connections are not drawn.

Note that the following parameters are only used in the multiple pose estimation pipeline.

The `NMS_thresh (Non-Maximum SuppressionThreshold)`: This parameter controls the overlapping bounding boxes that are
considered as
separate detections. A higher NMS threshold will result in fewer detections, while a lower threshold will result in more
detections. To improve object detection, you can experiment with different NMS thresholds to find the optimal value for
your specific use case.

The `confidence_thresh`: This parameter controls the minimum confidence score required for a detection to be
considered
valid. A higher confidence threshold will result in fewer detections, while a lower threshold will result in more
detections.

The `max_detection_boxes` : This parameter controls the maximum number of detections that can be output by the
multi pose estimation model. A higher maximum detection boxes value will result in more detections, while a lower value will result
in fewer detections.

The `plot_metrics`  parameter is an optional parameter in the multi pose estimation model that controls whether or not to
plot the precision versus recall curves. By default, this parameter is set to False, which means that the precision
versus recall curves will not be plotted. If you set this parameter to True, the multi pose estimation model will generate
and display the precision versus recall curves, which can be helpful for evaluating the performance of the model.

Overall, improving multi pose estimation requires careful tuning of these post-processing parameters based on your specific
use case. Experimenting with different values and evaluating the results can help you find the optimal values for your
multi pose estimation model.

</details></ul>
<ul><details open><summary><a href="#2-8">2.8 Model quantization</a></summary><a id="2-8"></a>

Configure the quantization section in [user_config.yaml](user_config.yaml) as the following:

```yaml

quantization:
  quantizer: TFlite_converter
  quantization_type: PTQ
  quantization_input_type: float
  quantization_output_type: uint8
  granularity: per_tensor            # Optional, defaults to "per_channel".
  optimize: True                     # Optional, defaults to False.
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

The quantization `granularity` is either "per_channel" or "per_tensor". If the parameter is not set, it will default to 
"per_channel". 'per channel' means all weights contributing to a given layer output channel are quantized with one 
unique (scale, offset) couple. The alternative is 'per tensor' quantization which means that the full weight tensor of 
a given layer is quantized with one unique (scale, offset) couple. 
It is obviously more challenging to preserve original float model accuracy using 'per tensor' quantization. But this 
method is particularly well suited to fully exploit STM32MP2 platforms HW design.

Some topologies can be slightly optimized to become "per_tensor" quantization friendly. Therefore, we propose to 
optimize the model to improve the "per-tensor" quantization. This is controlled by the `optimize` parameter. By default, 
it is False and no optimization is applied. When set to True, some modifications are applied on original network. 
Please note that these optimizations only apply when granularity is "per_tensor". To finish, some topologies cannot be 
optimized. So even if `optimize` is set to True, there is no guarantee that "per_tensor" quantization will preserve the 
float model accuracy for all the topologies.

By default, the quantized model is saved in the 'quantized_models' directory under the 'experiments_outputs' directory.
You may use the optional `export_dir` attribute to change the name of this directory.

</details></ul>
<ul><details open><summary><a href="#2-9">2.9 Benchmark the model</a></summary><a id="2-9"></a>

The [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home) allows you to benchmark your model and estimate its
footprints and inference time for different STM32 target devices. To use this feature, set the `on_cloud` attribute to
True. Alternatively, you can use [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) to benchmark
your model and estimate its footprints for STM32 target devices locally. To do this, make sure to add the path to
the `stm32ai` executable under the `path_to_stm32ai` attribute and set the `on_cloud` attribute to False.

The `version` attribute to specify the **STM32Cube.AI** version used to benchmark the model, e.g. 9.1.0 and
the `optimization` defines the optimization used to generate the C model, options: "balanced", "time", "ram".

The `board` attribute is used to provide the name of the STM32 board to benchmark the model on. The available boards
are 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32F469I-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-H743ZI2', '
STM32H747I-DISCO', 'STM32H735G-DK', 'STM32F769I-DISCO', 'NUCLEO-G474RE', 'NUCLEO-F401RE' and 'STM32F746G-DISCO'.

```yaml
tools:
  stedgeai:
    version: 9.1.0
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

benchmarking:
  board: STM32H747I-DISCO     # Name of the STM32 board to benchmark the model on
```

The `path_to_cubeIDE` attribute is for the [deployment](../deployment/README.md) service which is not part the
chain `chain_eqeb` used in this tutorial.

</details></ul>
<ul><details open><summary><a href="#2-10">2.10 Deploy the model</a></summary><a id="2-10"></a>

In this tutorial, we are using the `chain_eqeb` toolchain, which does not include the deployment service. However, if
you want to deploy the model after running the chain, you can do so by referring to
the [README](../deployment/README.md) and modifying the `deployment_config.yaml` file or by setting the `operation_mode`
to `deploy` and modifying the `user_config.yaml` file as described below:

```yaml
general:
  model_path: <path-to-a-TFlite-model-file>     # Path to the model file to deploy
  model_type: yolo_mpe

postprocessing:
  confidence_thresh: 0.25
  NMS_thresh: 0.7
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 10

tools:
  stedgeai:
    version: 9.1.0
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

deployment:
  c_project_path: ../../stm32ai_application_code/pose_estimation/
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
include the `confidence_thresh`, `NMS_thresh`, `confidence_thresh`, and `max_detection_boxes`. By providing
these values in the postprocessing section, the pose estimation model can properly post-process the results and
generate accurate detections. It is important to carefully tune these parameters based on your specific use case to
achieve optimal performance.

The `tools` section includes information about the STM32AI toolchain, such as the version, optimization level, and path
to the `stm32ai.exe` file.

Finally, in the `deployment` section, users must provide information about the hardware setup, such as the series and
board of the STM32 device, as well as the input and output interfaces. Once all of these sections have been filled in,
users can run the deployment service to deploy their model to the STM32 device.

</details></ul>
<ul><details open><summary><a href="#2-11">2.11 Hydra and MLflow settings</a></summary><a id="2-11"></a>

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

</details></ul>
</details>
<details open><summary><a href="#3"><b>3. Run the object detection chained service</b></a></summary><a id="3"></a>

After updating the [user_config.yaml](user_config.yaml) file, please run the following command:

```bash
python stm32ai_main.py
```

* Note that you can provide YAML attributes as arguments in the command, as shown below:

```bash
python stm32ai_main.py operation_mode='chain_eb'
```

</details>
<details open><summary><a href="#4"><b>4. Visualize the chained services results</b></a></summary><a id="4"></a>

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
    files                                 |
                                          |
                                          +--------------------------------+------------+
                                          |                                |            |
                                          |                                |            |
                                 quantized_models                       logs        .hydra
                                          |                                |            |
                                          +--- quantized_model.tflite  TensorBoard    Hydra
                                                                         files        files
```
The file named 'stm32ai_main.log' under each experiment directory is the log file saved during the execution of the '
stm32ai_main.py' script. The contents of the other files saved under an experiment directory are described in the table
below.

|  File             |  Directory | Contents               |
|:-------------------|:-------------------------|:-----------------------|
| quantized_model.tflite  | quantized_models | Quantized model (TFlite) |
| float_model_precision_recall_curve.png | metrics | Float model precision-recall curve | 
| quantized_model_precision_recall_curve.png | metrics | Quantized model precision-recall curve |

All the directory names, including the naming pattern of experiment directories, can be changed using the configuration
file. The names of the files cannot be changed.

The models in the 'best_augmented_model.h5' and 'last_augmented_model.h5' Keras files contain rescaling and data
augmentation layers. These files can be used to resume a training that you interrupted or that crashed. This will be
explained in section training service [README](training/README.md). These model files are not intended to be used
outside of the Model Zoo context.

<ul><details open><summary><a href="#4-1">4.1 Saved results</a></summary><a id="4-1"></a>

All of the training and evaluation artifacts are saved in the current output simulation directory, which is located
at **experiments_outputs/\<date-and-time\>**.

For example, you can retrieve the confusion matrix generated after evaluating the float and the quantized model on the
test set by navigating to the appropriate directory within **experiments_outputs/\<date-and-time\>**.

</details></ul>
<ul><details open><summary><a href="#4-3">4.3 Run MLFlow</a></summary><a id="4-3"></a>

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

</details></ul>
</details>
<details open><summary><a href="#A"><b>Appendix A: YAML syntax</b></a></summary><a id="A"></a>

**Example and terminology:**

An example of YAML code is shown below.

```yaml
preprocessing:
  rescaling:
    scale: 1/127.5
    offset: -1
  resizing:
    aspect_ratio: fit
    interpolation: nearest
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
    interpolation: nearest
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
  interpolation: nearest
```

is equivalent to this one:

```yaml
resizing:
  aspect_ratio: "fit"
  interpolation: "nearest"
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

</details>