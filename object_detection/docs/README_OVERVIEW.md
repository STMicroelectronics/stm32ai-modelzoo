# Object detection STM32 model zoo

Remember that minimalistic yaml files are available [here](../config_file_examples/) to play with specific services, and that all pre-trained models in the [STM32 model zoo](https://github.com/STMicroelectronics/stm32ai-modelzoo/) are provided with their configuration .yaml file used to generate them. These are very good starting points to start playing with!

## <a id="">Table of contents</a>

1. [Object detection Model Zoo introduction](#1)
2. [Object detection tutorial](#2)
   - [2.1 Choose the operation mode](#2-1)
   - [2.2 Global settings](#2-2)
   - [2.3 Model settings](#2-3)
   - [2.4 Dataset specification](#2-4)
   - [2.5 Apply image preprocessing](#2-5)
   - [2.6 Use data augmentation](#2-6)
   - [2.6 Set the training parameters](#2-6)
   - [2.7 Set the postprocessing parameters](#2-7)
   - [2.8 Model quantization](#2-8)
   - [2.9 Benchmark the model](#2-9)
   - [2.10 Deploy the model](#2-10)
   - [2.11 Hydra and MLflow settings](#2-11)
3. [Run the object detection chained service](#3)
4. [Visualize the chained services results](#4)
   - [4.1 Saved results](#4-1)
   - [4.2 Run tensorboard](#4-2)
   - [4.3 Run ClearML](#4-3)
   - [4.4 Run MLFlow](#4-4)
5. [Appendix A: YAML syntax](#A)



<details open><summary><a href="#1"><b>1. Object detection Model Zoo introduction</b></a></summary><a id="1"></a>

The object detection model zoo provides a collection of independent services and pre-built chained services that can be
used to perform various functions related to machine learning for Object detection. The individual services include
tasks such as training the model or quantizing the model, while the chained services combine multiple services to
perform more complex functions, such as training the model, quantizing it, and evaluating the quantized model
successively.

To use the services in the Object detection model zoo, you can utilize the model zoo [stm32ai_main.py](../stm32ai_main.py) along with the [user_config.yaml](../user_config.yaml) file as input. The yaml file specifies the service or the chained services and a set of configuration parameters such as the model (either from the model zoo or your own custom model), the dataset, the number of epochs, and the preprocessing parameters, among others.

More information about the different services and their configuration options can be found in the <a href="#2">next
section</a>.

The object detection datasets are expected to be in TFS TensorFlow format. For this project, we are using the Pascal VOC 2012 dataset, which can be downloaded directly in YOLO Darknet TXT format from [here](https://public.roboflow.com/object-detection/pascal-voc-2012/1/download/darknet).

An example of this structure is shown below:

```yaml
<dataset-root-directory>
train/:
  train_image_1.jpg
  train_image_1.txt
  train_image_2.jpg
  train_image_2.txt
val/:
  val_image_1.jpg
  val_image_1.txt
  val_image_2.jpg
  val_image_2.txt
```

</details>
<details open><summary><a href="#2"><b>2. Object detection tutorial</b></a></summary><a id="2"></a>

This tutorial demonstrates how to use the `chain_tqeb` services to train, benchmark, quantize, evaluate, and benchmark
the model.

To get started, you will need to update the [user_config.yaml](../user_config.yaml) file, which specifies the parameters and configuration options for the services that you want to use. Each section of the [user_config.yaml](../user_config.yaml) file is explained in detail in the following sections.

<ul><details open><summary><a href="#2-1">2.1 Choose the operation mode</a></summary><a id="2-1"></a>

The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be a single operation or a set of chained operations.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for benchmark, and 'd' for deployment on an STM32 board.

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

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific services:

- [training, chain_tqe, chain_tqeb](./README_TRAINING.md)
- [quantization, chain_eqe, chain_qb](./README_QUANTIZATION.md)
- [evaluation, chain_eqeb](./README_EVALUATION.md)
- [benchmarking](./README_BENCHMARKING.md)
- deployment, chain_qd ([STM32H7](./README_DEPLOYMENT_STM32H7.md), [STM32N6](./README_DEPLOYMENT_STM32N6.md), [STM32MPU](./README_DEPLOYMENT_MPU.md))

In this tutorial, the `operation_mode` used is the `chain_tqeb` as shown below to train a model, quantize, evaluate it to be later deployed in the STM32 boards.

```yaml
operation_mode: chain_tqeb
```

</details></ul>
<ul><details open><summary><a href="#2-2">2.2 Global settings</a></summary><a id="2-2"></a>

The `general` section and its attributes are shown below.

```yaml
general:
  project_name: Pascal_VOC_2012_Demo           # Project name. Optional, defaults to "<unnamed>".
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

The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy, and Tensorflow random generators at the beginning of the main script. This is an optional attribute, the default value being 123. If you don't want random generators to be seeded, then set `global_seed` to 'None' (not recommended as this would make training results less reproducible).

Even when random generators are seeded, it is often difficult to exactly reproduce results when the same operation is
run multiple times. This typically happens when the same training script is run on different hardware.
The `deterministic_ops` operator can be used to enable the deterministic mode of Tensorflow. If enabled, an operation
that uses the same inputs on the same hardware will have the exact same outputs every time it is run. However,
determinism should be used carefully as it comes at the expense of longer run times. Refer to the Tensorflow
documentation for more details.

The `gpu_memory_limit` attribute sets an upper limit in GBytes on the amount of GPU memory Tensorflow may use. This is
an optional attribute with no default value. If it is not present, memory usage is unlimited. If you have several GPUs,
be aware that the limit is only set on logical gpu[0].

The `num_threads_tflite` parameter is only used as an input parameter for the tflite interpreter. Therefore, it has no effect on .keras or .onnx models. 
This parameter may accelerate the tflite model evaluation in the following operation modes:  `evaluation` (if a .tflite is specified in `model_path`), 
`chain_tbqeb`, `chain_eqe`, `chain_tqe` and `chain_eqeb` (if the quantizer is the TFlite_converter). 
However, the acceleration depends on your system resources.

</details></ul>
<ul><details open><summary><a href="#2-3">2.3 Model settings</a></summary><a id="2-3"></a>
The `model` section and its attributes are shown below.

```yaml
model:
  model_type: st_yoloxn
  model_name: st_yoloxn
  model_path: 
```

The `model_path` attribute is utilized to indicate the path to the model file that you wish to use for the selected operation mode. 

The `model_type` attribute specifies the type of the model architecture that you want to train, the model family. The `model_name` attribute specifies the exact variant to use within the `model_type` family.
It is important to note that only certain models are supported. These models include:

- `yolov8n` : is an advanced object detection model from Ultralytics that builds upon the strengths of its predecessors in the YOLO series. It is designed for real-time object detection, offering high accuracy and speed. YOLOv8 incorporates state-of-the-art techniques such as improved backbone networks, better feature pyramid networks, and advanced anchor-free detection heads, making it highly efficient for various computer vision tasks. Don't hesitate to check the tuto ["How can I quantize, evaluate and deploy an Ultralytics Yolov8 model?"](./tuto/How_to_deploy_yolov8_yolov5_object_detection.md) for more information on Ultralytics Yolov8 model deployment.

- `yolov11n` : is an advanced object detection model from Ultralytics that builds upon the strengths of its predecessors in the YOLO series. It is designed for real-time object detection, offering high accuracy and speed. YOLOv11 incorporates state-of-the-art techniques such as improved backbone networks, better feature pyramid networks, and advanced anchor-free detection heads, making it highly efficient for various computer vision tasks. Don't hesitate to check the tuto ["How can I quantize, evaluate and deploy an Ultralytics Yolov8 model?"](./tuto/How_to_deploy_yolov8_yolov5_object_detection.md) for more information on Ultralytics Yolov11 model deployment.

- `yolov5u`: (You Only Look Once version 5 from Ultralytics) is a popular object detection model known for its balance of speed and accuracy. It is part of the YOLO family and is designed to perform real-time object detection. Don't hesitate to check the tuto ["How can I quantize, evaluate and deploy an Ultralytics Yolov5 model?"](./tuto/How_to_deploy_yolov8_yolov5_object_detection.md) for more information on Ultralytics Yolov5u model deployment.
 
- `st_yoloxn`: is an advanced object detection model that builds upon the YOLO (You Only Look Once) series, offering significant improvements in performance and flexibility. Unlike its predecessors, YOLOX can adopt an anchor-free approach, which simplifies the model and enhances its accuracy. It also incorporates advanced techniques such as decoupled head structures for classification and localization, and a more efficient training strategy. YOLOX is designed to achieve high accuracy and speed, making it suitable for real-time applications in various computer vision tasks. This ST variant embeds various tuning capabilities from the yaml configuration file.
 
- `st_yololcv1`: This is a lightweight version of the tiny yolo v2 object detection algorithm. It was optimized to work well on embedded devices with limited computational resources.

- `yolov2t`: This is a lightweight version of the YOLO (You Only Look Once) object detection algorithm. It is designed to work well on embedded devices with limited computational resources.

The exhaustive list of `model_type` and corresponding `model_name` is the following: 

|`model_type`           | possible `model_name`| 
|-----------------------|----------------------|
| `yolov8n`             | X         |
| `yolov11n`            | X         |
| `yolov5u`             | X         |
| `st_yoloxn`           | `st_yoloxn`, `st_yoloxn_d033_w025`, `st_yoloxn_d100_w025`, `st_yoloxn_d050_w040`        |
| `st_yololcv1`         | `st_yololcv1`|
| `yolov2t`             |  `yolov2t`   |
| `yolov4`              | X            |
| `yolov4t`             | X            |
| `face_detect_front`   | X            |

When no `model_name` attribute is possible, `model_path` is to be used.

It is important to note that each model type has specific requirements in terms of input image size, output size of the head and/or backbone, and other parameters. Therefore, it is important to choose the appropriate model type for your
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
the [readme](./README_TRAINING.md) file for the train service. However, in this tutorial, the `model_path` attribute is
not used since we are using a pre-trained model from the Model Zoo.

</details></ul>
<ul><details open><summary><a href="#2-4">2.4 Dataset specification</a></summary><a id="2-4"></a>

Before you start using this project, it's important to understand the supported dataset names and formats. Please note that for all the training, evaluation and quantization services, it is expected to have a dataset in TFS Tensorflow format. For the object detection use case, the `get_dataset` API call takes care of the conversion of your dataset automatically depending on the `dataset_name` and `format` attributes.

The `dataset` section and its attributes are shown in the YAML code below.

```yaml
dataset:
  format: pascal_voc
  dataset_name: pascal_voc                                    # Dataset name. Optional, defaults to "<unnamed>".
  class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ] # Names of the classes in the dataset.
  data_dir: ./datasets/pascal_voc/tmp/                       # Path to the tmp directory before the split.
  train_images_path: /local/datasets/VOC0712/JPEGImages/     # Path to the root directory of the img before split.
  train_xml_dir: /local/datasets/VOC0712/Annotations         # Path to the root directory of the xml annotations
  training_path: <training-set-root-directory>               # Path to the root directory of the training set.
  validation_path: <validation-set-root-directory>           # Path to the root directory of the validation set.
  validation_split: 0.2                                      # Training/validation sets split ratio.
  test_path: <test-set-root-directory>                       # Path to the root directory of the test set.
  quantization_path: <quantization-set-root-directory>       # Path to the root directory of the quantization set.
  quantization_split:                                        # Quantization split ratio.
  seed: 123                                                  # Random generator seed used when splitting a dataset.
```

The `dataset_name` attribute is required and serves to specify the dataset you are using. This can be a well-known dataset like coco, pascal_voc, or a custom_dataset if you have your own data and it follows the logic below:

| Dataset Name     | Allowed Formats          | Description                                                                                  |
|------------------|-------------------------|----------------------------------------------------------------------------------------------|
| `coco`           | `coco`, `tfs`           | Native COCO format or TFS TensorFlow format                                                     |
| `pascal_voc`     | `pascal_voc`, `tfs`     | Native Pascal VOC format or TFS TensorFlow format                                               |
| `darknet_yolo`   | `darknet_yolo`, `tfs`   | Native Darknet YOLO format or TFS TensorFlow format                                             |
| `custom_dataset` | `tfs`                   | Only TFS TensorFlow format; in case the dataset is already converted before evaluation                          |

Depending on the `dataset_name`, the dataset loader will check the `format` to determine if it is necessary to convert the dataset to the final **TFS TensorFlow format**. These two parameters are mandatory if the operation mode is **training**, **evaluation** and **quantization**.

The `format` attributes defines the annotation format of your dataset. This must match the format of your dataset annotations. 
It serves to check whether your dataset is in its original format or in TFS TensorFlow format. 
This determines whether it is needed to convert the dataset to the required TFS format or not. It accepts the following values: 

  * `tfs`: If the dataset is a TensorFlow Object Detection API format.
  * `coco`: If the dataset is in COCO dataset format (JSON annotations).
  * `pascal_voc`: If the dataset is in Pascal VOC XML annotation format.
  * `darknet_yolo`: If the dataset is in YOLO Darknet text file annotations.

Depending on the `format` value, some additional attributes should be defined in the dataset section:
- If the `format` is set to **coco**, the following attributes should be set:
  * The `data_dir`: Required, refers to the temporary path where the TFS files will be generated.
  * The `train_images_path`: Required, refers to the path of the training subset directory where the images are located.
  * The `train_annotations_path`: Required, refers to the path of the training subset json file of the annotations.
  * The `val_images_path`: Optional, refers to the path of the validation subset directory where the images are located.
  * The `val_annotations_path`: Optional, refers to the path of the training subset json file of the annotations.

- If the `format` is set to **pascal_voc**, the following attributes should be set:
  * The `data_dir`: Required, refers to the temporary path where the TFS files will be generated.
  * The `train_images_path`: Required, refers to the path of the training subset directory where the images are located.
  * The `train_xml_dir`: Required, refers to the path of the training subset directory containing the xml files of the annotations.
  * The `val_images_path`: Optional, refers to the path of the validation subset directory where the images are located.
  * The `val_xml_dir`: Optional, refers to the path of the training subset directory containing the xml files of the annotations.

- If the `format` is set to **darknet_yolo**, the following attributes should be set:
  * The `data_dir`: Required, refers to the path of the directory containing the txt files of the annotations along with the images.


The state machine below describes the process of dataset loading for object detection use case.


```
                                                   dataset_name
                                                         |
                                                         |
        +----------------------------------+--------------------------+-------------------------------+
        |                                  |                          |                               |
        |                                  |                          |                               |
      "coco"                           "pascal_voc"              "darknet_yolo"                "custom_dataset"
        |                                  |                          |                               |
        |                                  |                          |                               |
  +-----+------------+           +-----+-----------+          +-------+-------+               +-------+-------+ 
  |                  |           |                 |          |               |               |               |
supported        unsupported    supported    unsupported   supported     unsupported      supported      unsupported        
 format:           format        format         format      format:        format           format         format
      |                             |                           |                             |
  +---+-----+                   +---+---+                  +----+-----+                       |
  |         |                   |       |                  |          |                       |
 coco      tfs             pascal_voc  tfs            darknet_yolo   tfs                     tfs
  |         |                   |       |                  |          |                   (Custom dataset
  |         |                   |       |                  |          |                    should be used
  |         |                   |       |                  |          |                   if the conversion
  |   dataset.format=tfs        |  dataset.format=tfs      |    dataset.format=tfs         has already been
  |   (already TFS)             |    (already TFS)         |      (already TFS)            done in a previous
  |         |                   |       |                  |          |                    training or eval)
  |         |                   |       |                  |          |                       |
  |   load TFS directly         |   load TFS directly      |      load TFS directly      load TFS directly
  |                             |                          |                                  |
  |                             |                          |                                  |
dataset.format=coco     dataset.format=pascal_voc      dataset.format=darknet_yolo            |
(needs conversion)         (needs conversion)             (needs conversion)                  |
        |                         |                               |                           |
        v                         v                               v                           |
convert coco to tfs      convert pascal_voc to tfs     convert darknet yolo to tfs            |
        |                         |                               |                           |
        +-------------------------+-------------------------------+---------------------------+
                                                |
                                        Dataset in TFS format
                                            (used for)
                          +---------------------+-----------------------+
                          |                     |                       |
                      training             evaluation             quantization

```


The `class_names` attribute specifies the classes in the dataset. This information must be provided in the YAML file. If the `class_names` attribute is absent, the `classes_name_file` argument can be used as an alternative, pointing to a text file containing the class names.

The attribute `download_data` is a boolean flag that is supported only if the `dataset_name` is set to **coco** or **pascal_voc**. It used to control whether the dataset should be automatically downloaded from the official source if it is not already present locally.

- If set to true, the system will attempt to download the dataset from the official source of each of the datasets.
- If set to false, the system expects the dataset to be already available locally and will not perform any download operation.

The `exclude_unlabeled` attribute is a boolean flag that, when set to True, instructs the dataset loader or processing script to exclude images that do not contain any labeled objects (i.e., images without annotations) from the training or evaluation dataset.

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

</details></ul>
<ul><details open><summary><a href="#2-5">2.5 Apply image preprocessing</a></summary><a id="2-5"></a>

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

Please note that the 'fit' option is the only supported option for the `aspect_ratio` attribute. When using this option,
the images will be resized to fit the target size. It is important to note that input images may be smaller or larger
than the target size, and will be distorted to some extent if their original aspect ratio is not the same as the
resizing aspect ratio. Additionally, bounding boxes should be adjusted to maintain their relative positions and sizes in
the resized images.

The `color_mode` attribute can be set to either *"grayscale"*, *"rgb"* or *"rgba"*.

</details></ul>
<ul><details open><summary><a href="#2-6">2.6 Use data augmentation</a></summary><a id="2-6"></a>

The data augmentation functions to apply to the input images during a training are specified in the
optional `data_augmentation` section of the configuration file. They are only applied to the images during training.

For this tutorial, the data augmentation section is shown below.

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

</details></ul>
<ul><details open><summary><a href="#2-7">2.7 Set the training parameters</a></summary><a id="2-7"></a>

A 'training' section is required in all the operation modes that include a training, namely 'training', 'chain_tqeb' and 'chain_tqe'. In this tutorial, we will be using a custom object detection model called st_yoloxn.

As an example, we will be using our custom st_yoloxn model, which uses a MobileNet V1 with an alpha value of 0.25 as its backbone, to do so we will need to configure the model section in [user_config.yaml](../user_config.yaml) as the following:

```yaml
training:
  model:
    alpha: 0.25
    input_shape: (192, 192, 3)
    pretrained_weights: imagenet
  batch_size: 64
  epochs: 150
  dropout: 0.5
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
- Additional attributes are needed depending on the type of model. For example:
  - `alpha` attribute is required for SSD MobileNet models.
  - `depth_mul` st_yoloxn attribute, It is a multiplier for the depth of the network, default value is 0.33. Recommended values for optimum performance are: 0.34, 0.67, 1.0, 1.34, 1.67, ...
  - `width_mul` st_yoloxn attribute, It is a multiplier for the width of the network, default value is 0.25. Recommended values for optimum performance are: 0.25 +- x * 0.03125

The `batch_size` and `epochs` attributes are mandatory.

The `dropout` attribute is optional and specifies the dropout rate to use during training. By default, no dropout is applied.

The `optimizer` subsection specifies the optimizer to use during training. In this example, the Adam optimizer is used with an initial learning rate of 0.001.
- The optional `pretrained_weights` attribute can be used to load pretrained weights in the model before it gets trained. By default, no pretrained weights are loaded.

The `frozen_layers` attribute is used to specify which layers of the model should be frozen (i.e., made non-trainable) during training. In this example, all layers except the last one are frozen.

The `callbacks` subsection is optional. All the Keras callbacks are supported. Note that several callbacks are built-in
and cannot be redefined, including ModelCheckpoint, TensorBoard and CSVLoggerr.

A variety of learning rate schedulers are provided with the Model Zoo. If you want to use one of them, just include it
in the `callbacks` subsection. Refer to the training service [README](./README_TRAINING.md) for a description of the
available callbacks and learning rate plotting utility.

The best model obtained at the end of the training is saved in the 'experiments_outputs/\<date-and-time\>/saved_models'
directory and is called 'best_model.keras' (see section <a href="#4">visualize the chained services results</a>).

</details></ul>

<ul><details open><summary><a href="#2-8">2.8 Set the postprocessing parameters</a></summary><a id="2-8"></a>

A 'postprocessing' section is required in all operation modes for object detection models. This section includes
parameters such as NMS threshold, confidence threshold, IoU evaluation threshold, and maximum detection boxes. These
parameters are necessary for proper post-processing of object detection results.

```yaml
postprocessing:
  confidence_thresh: 0.001
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 100
```

`NMS_thresh (Non-Maximum SuppressionThreshold)`: This parameter controls the overlapping bounding boxes that are considered as separate detections. A higher NMS threshold will result in fewer detections, while a lower threshold will result in more detections. To improve object detection, you can experiment with different NMS thresholds to find the optimal value for your specific use case.

- **confidence_thresh**: This parameter controls the minimum confidence score required for a detection to be considered valid. A higher confidence threshold will result in fewer detections, while a lower threshold will result in more detections.

- **IoU_eval_thresh**: This parameter controls the minimum overlap required between two bounding boxes for them to be considered as the same object. A higher IoU threshold will result in fewer detections, while a lower threshold will result in more detections.

- **max_detection_boxes**: This parameter controls the maximum number of detections that can be output by the object detection model. A higher maximum detection boxes value will result in more detections, while a lower value will result in fewer detections.

- **plot_metrics**: This parameter is an optional parameter in the object detection model that controls whether or not to plot the precision versus recall curves. By default, this parameter is set to False, which means that the precision versus recall curves will not be plotted. If you set this parameter to True, the object detection model will generate and display the precision versus recall curves, which can be helpful for evaluating the performance of the model.

Overall, improving object detection requires careful tuning of these post-processing parameters based on your specific use case. Experimenting with different values and evaluating the results can help you find the optimal values for your object detection model.

</details></ul>
<ul><details open><summary><a href="#2-9">2.9 model quantization </a></summary><a id="2-9"></a>

The `quantization` section is required in all the operation modes that include a quantization, namely `quantization`, `chain_tqe`, `chain_tqeb`, `chain_eqe`, `chain_eqeb`, `chain_qb`, and `chain_qd`.

The `quantization` section for this tutorial is shown below.

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

<ul><details open><summary><a href="#2-10">2.10 Benchmark the model</a></summary><a id="2-10"></a>

The [STEdgeAI Developer Cloud](https://stedgeai-dc.st.com/home) allows you to benchmark your model and estimate its
footprints and inference time for different STM32 target devices. To use this feature, set the `on_cloud` attribute to
True. Alternatively, you can use [STEdgeAI Core](https://www.st.com/en/development-tools/stedgeai-core.html) to benchmark
your model and estimate its footprints for STM32 target devices locally. To do this, make sure to add the path to
the `stedgeai` executable under the `path_to_stedgeai` attribute and set the `on_cloud` attribute to False.

The `optimization` defines the optimization used to generate the C model, options: "balanced", "time", "ram".

The `board` attribute is used to provide the name of the STM32 board to benchmark the model on. The available boards are 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32F469I-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-H743ZI2', 'STM32H747I-DISCO', 'STM32H735G-DK', 'STM32F769I-DISCO', 'NUCLEO-G474RE', 'NUCLEO-F401RE' and 'STM32F746G-DISCO'.

```yaml
tools:
  stedgeai:
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/ST/STEdgeAI/<x.y>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

benchmarking:
  board: STM32H747I-DISCO     # Name of the STM32 board to benchmark the model on
```

The `path_to_cubeIDE` attribute is for the deployment service which is not part of the
`chain_tqeb` used in this tutorial.

</details></ul>
<ul><details open><summary><a href="#2-10">2.10 Deploy the model</a></summary><a id="2-10"></a>

In this tutorial, we are using the `chain_tqeb` toolchain, which does not include the deployment service. However, if
you want to deploy the model after running the chain, you can do so by referring to
the deployment README and modifying the `deployment_config.yaml` file or by setting the `operation_mode`
to `deploy` and modifying the `user_config.yaml` file as described below:

```yaml
general:
  project: my_project

model:
  model_path: <path-to-a-TFlite-model-file>     # Path to the model file to deploy

dataset:
  format: tfs
  dataset_name: pascal_voc
  class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ]

postprocessing:
  confidence_thresh: 0.5
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 10

tools:
  stedgeai:
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/ST/STEdgeAI/<x.y>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

deployment:
  c_project_path: ../application_code/object_detection/STM32H7/
  IDE: GCC
  verbosity: 1
  hardware_setup:
    serie: STM32H7
    board: STM32H747I-DISCO
```

In the `general` section, users must provide the name of the current project.

In the `model` section, user must provide the path to the TFlite model file that they want to deploy using
the `model_path` attribute.

The `dataset` section requires users to provide the `dataset_name`, the `format` and  the names of the classes using the `class_names` attribute.

The `postprocessing` section requires users to provide the values for the post-processing parameters. These parameters
include the `NMS_thresh`, `confidence_thresh`, `IoU_eval_thresh`, and `max_detection_boxes`. By providing
these values in the postprocessing section, the object detection model can properly post-process the results and
generate accurate detections. It is important to carefully tune these parameters based on your specific use case to
achieve optimal performance.

The `tools` section includes information about the **stedgeai** toolchain, such as the version, optimization level, and path
to the `stedgeai.exe` file.

Finally, in the `deployment` section, users must provide information about the hardware setup, such as the series and
board of the STM32 device, as well as the input and output interfaces. Once all of these sections have been filled in,
users can run the deployment service to deploy their model to the STM32 device.

Please refer to readme below for a complete deployment tutorial:
- on H7-MCU : [README_STM32H7.md](./README_DEPLOYMENT_STM32H7.md)
- on N6-NPU : [README_STM32N6.md](./README_DEPLOYMENT_STM32N6.md)
- on MPU : [README_MPU.md](./README_DEPLOYMENT_MPU.md)

</details></ul>
<ul><details open><summary><a href="#2-11">2.11 Hydra and MLflow settings</a></summary><a id="2-11"></a>

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used
to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment
directories. In the YAML code below, it is set to save the outputs as explained in the section <a id="4">visualize the
chained services results</a>:

```yaml
hydra:
  run:
    dir: ./tf/src/experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown
below:

```yaml
mlflow:
  uri: ./tf/src/experiments_outputs/mlruns
```

</details></ul>
</details>
<details open><summary><a href="#3"><b>3. Run the object detection chained service</b></a></summary><a id="3"></a>

After updating the [user_config.yaml](../user_config.yaml) file, please run the following command:

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
    files                                 +--- training_metrics.csv
                                          +--- training_curves.png
                                          +--- float_model_confusion_matrix_validation_set.png
                                          |
      +-----------------------------------+--------------------------------+------------+
      |                                   |                                |            |
      |                                   |                                |            |
 saved_models                      quantized_models                       logs        .hydra
      |                                   |                                |            |
      +--- best_augmented_model.keras     +--- quantized_model.keras   TensorBoard     Hydra
      +--- last_augmented_model.keras                                     files        files
      +--- best_model.keras
```

The file named 'stm32ai_main.log' under each experiment directory is the log file saved during the execution of the '
stm32ai_main.py' script. The contents of the other files saved under an experiment directory are described in the table
below.

|  File             |  Directory | Contents               |
|:-------------------|:-------------------------|:-----------------------|
| best_augmented_model.keras | saved_models | Best model saved during training, rescaling and data augmentation layers included (Keras) |
| last_augmented_model.keras | saved_models | Last model saved at the end of a training, rescaling and data augmentation layers included (Keras) |
| best_model.keras           | saved_models | Best model obtained at the end of a training (Keras) |
| quantized_model.tflite  | quantized_models | Quantized model (TFlite) |
| training_metrics.csv    | metrics | Training metrics CSV including epochs, losses, accuracies and learning rate |
| training_curves.png     | metrics | Training learning curves (losses and accuracies) |
| float_model_confusion_matrix_test_set.png | metrics | Float model confusion matrix | 
| quantized_model_confusion_matrix_test_set.png | metrics | Quantized model confusion matrix |

All the directory names, including the naming pattern of experiment directories, can be changed using the configuration
file. The names of the files cannot be changed.

The models in the 'best_augmented_model.keras' and 'last_augmented_model.keras' Keras files contain rescaling and data
augmentation layers. These files can be used to resume a training that you interrupted or that crashed. This will be
explained in section training service [README](./README_TRAINING.md). These model files are not intended to be used
outside of the Model Zoo context.

<ul><details open><summary><a href="#4-1">4.1 Saved results</a></summary><a id="4-1"></a>

All of the training and evaluation artifacts are saved in the current output simulation directory, which is located
at **experiments_outputs/\<date-and-time\>**.

For example, you can retrieve the confusion matrix generated after evaluating the float and the quantized model on the
test set by navigating to the appropriate directory within **experiments_outputs/\<date-and-time\>**.

</details></ul>
<ul><details open><summary><a href="#4-2">4.2 Run tensorboard</a></summary><a id="4-2"></a>

To visualize the training curves that were logged by TensorBoard, navigate to the **
experiments_outputs/\<date-and-time\>** directory and run the following command:

```bash
tensorboard --logdir logs
```

This will start a server and its address will be displayed. Use this address in a web browser to connect to the server.
Then, using the web browser, you will able to explore the learning curves and other training metrics.

</details></ul>
<ul><details open><summary><a href="#4-3">4.3 Run ClearML</a></summary><a id="4-3"></a>

ClearML is an open-source tool used for logging and tracking machine learning experiments. It allows you to record metrics, parameters, and results, making it easier to monitor and compare diffrent runs.

Follow these steps to configurate ClearML for logging your results. This setup only needs to be done once. if you haven't set it up yet, complete the steps below. if you've already configured ClearML, your results should be automatically logged and available in your session.

- Sign up for free to the [ClearML Hosted Service](https://app.clear.ml), then go to your ClearML workspace and create new credentials.

- Create a `clearml.conf` file and paste the credentials into it. If you are behind a proxy or using SSL portals, add `verify_certificate = False` to the configuration to make it work. Here is an example of what your `clearml.conf` file might look like:

    ```ini
    api {
        web_server: https://app.clear.ml
        api_server: https://api.clear.ml
        files_server: https://files.clear.ml
        # Add this line if you are behind a proxy or using SSL portals
        verify_certificate = False
        credentials {
            "access_key" = "YOUR_ACCESS_KEY"
            "secret_key" = "YOUR_SECRET_KEY"
        }
    }
  
    ```

Once configured, your experiments will be logged directly and shown in the project section under the name of your project.

</details></ul>
<ul><details open><summary><a href="#4-4">4.4 Run MLFlow</a></summary><a id="4-4"></a>

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
