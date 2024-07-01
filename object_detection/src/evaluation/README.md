# Evaluation of object detection model

Our evaluation service is a comprehensive tool that enables users to assess the accuracy of their TensorFlow Lite (
.tflite) or Keras (.h5) object detection model. By uploading their model and a validation set, users can quickly and
easily evaluate the performance of their model and generate various metrics, such as map.

The evaluation service is designed to be fast, efficient, and accurate, making it an essential tool for anyone looking
to evaluate the performance of their object detection model.

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Configure the yaml file</b></a></summary><a id="1"></a>

To use this service and achieve your goals, you can use the [user_config.yaml](../user_config.yaml) or directly update
the [evaluation_config.yaml](../config_file_examples/evaluation_config.yaml) file and use it. This file provides an
example of how to configure the evaluation service to meet your specific needs.

Alternatively, you can follow the tutorial below, which shows how to evaluate your pre-trained object detection
model using our evaluation service.

<ul><details open><summary><a href="#1-1">1.1 Set the model and the operation mode</a></summary><a id="1-1"></a>

As mentioned previously, all the sections of the YAML file must be set in accordance with
this **[README.md](../config_file_examples/evaluation_config.yaml)**.
In particular, `operation_mode` should be set to evaluation and the `evaluation` section should be filled as in the
following example:

```yaml
general:
  model_path: ../pretrained_models/st_ssd_mobilenet_v1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_192/ssd_mobilenet_v1_025_192_int8.tflite

operation_mode: evaluation
```

In this example, the path to the ST SSD MobileNet V1 model is provided in the `model_path` parameter.

</details></ul>
<ul><details open><summary><a href="#1-2">1.2 Prepare the dataset</a></summary><a id="1-2"></a>

Information about the dataset you want use for evaluation is provided in the `dataset` section of the configuration
file, as shown in the YAML code below.

```yaml
dataset:
  dataset_name: COCO_2017_person                             # Dataset name. Optional, defaults to "<unnamed>".
  test_path: <test-set-root-directory>                       # Path to the root directory of the test set.
  check_image_files: False                                   # Enable/disable image file checking.
```

In this example, the path to the validation set is provided in the `test_path` parameter.

When working with a dataset for the first time, we suggest setting the `check_image_files` attribute to True. This will
enable the system to load each image file and identify any corrupt, unsupported, or non-image files. The path to any
problematic files will be reported.

In cases where there is no validation set path or test set provided to evaluate the model trained using the training
service, the available data under the `training_path` directory is split into two to create a training set and a
validation set. By default, 80% of the data is used for training and the remaining 20% is used for the validation set in
the evaluation service.

If you want to use a different split ratio, you need to specify the percentage to be used for the validation set in
the `validation_split` parameter (to ensure consistency in the [training](../training/README.md) and evaluation process,
you must specify the same validation_split parameter value in both the training and evaluation services), as shown in
the YAML example below:

```yaml
dataset:
  name: COCO_2017_person
  class_names: [ person ]
  training_path: ../datasets/COCO_2017_person /
  validation_path:
  validation_split: 0.20
  test_path:
```

</details></ul>
<ul><details open><summary><a href="#1-3">1.3 Apply preprocessing</a></summary><a id="1-3"></a>

The images from the dataset need to be preprocessed before they are presented to the network for evaluation.
This includes rescaling and resizing. In particular, they need to be rescaled exactly as they were at training step.
This is illustrated in the YAML code below:

```yaml
preprocessing:
  rescaling: { scale: 1/127.5, offset: -1 }
  resizing:
    aspect_ratio: "fit"
    interpolation: nearest
  color_mode: rgb
```

In this example, the pixels of the input images read in the dataset are in the interval [0, 255], that is UINT8. If you
set `scale` to 1./255 and `offset` to 0, they will be rescaled to the interval [0.0, 1.0].
If you set `scale` to 1/127.5 and `offset` to -1, they will be rescaled to the interval [-1.0, 1.0].

The `resizing` attribute specifies the image resizing methods you want to use:

- The value of `interpolation` must be one of *{"bilinear", "nearest", "bicubic", "area", "lanczos3", "lanczos5", "
  gaussian", "mitchellcubic"}*.
- The value of `aspect_ratio` must have a value of *"fit"* as we do not support other values such as *"crop"*. If you
  set it to *"fit"*, the resized images will be
  distorted if their original aspect ratio is not the same as in the resizing size.

The `color_mode` attribute must be one of "*grayscale*", "*rgb*" or "*rgba*".
When you define the preprocessing parameter in the configuration file, the annotation file for the object detection
dataset will be automatically modified during preprocessing to ensure that it is aligned with the preprocessed images.
This typically involves updating the bounding box coordinates to reflect any resizing or cropping that was performed
during preprocessing.
This automatic modification of the annotations file is an important step in preparing
the dataset for object detection, as it ensures that the annotations accurately reflect the preprocessed images and
enables the model to learn from the annotated data.

</details></ul>
<ul><details open><summary><a href="#1-4">1.4 Apply post-processing</a></summary><a id="1-4"></a>

Apply post-processing by modifiying the **postprocessing** parameters in **[user_config.yaml](../user_config.yaml)** as
the following:

- `confidence_thresh` - A *float* between 0.0 and 1.0, the score thresh to filter detections .
- `NMS_thresh` - A *float* between 0.0 and 1.0, NMS thresh to filter and reduce overlapped boxes.
- `IoU_eval_thresh` - A *float* between 0.0 and 1.0, IOU thresh to calculate TP and FP.

</details></ul>
<ul><details open><summary><a href="#1-5">1.5 Hydra and MLflow settings</a></summary><a id="1-5"></a>

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used
to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment
directories. With the YAML code below, every time you run the Model Zoo, an experiment directory is created that
contains all the directories and files created during the run. The names of experiment directories are all unique as
they are based on the date and time of the run.

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
<details open><summary><a href="#2"><b>2. Evaluate your model</b></a></summary><a id="2"></a>

If you chose to modify the [user_config.yaml](../user_config.yaml) you can evaluate the model by running the following
command from the **src/** folder:

```bash
python stm32ai_main.py 
```

If you chose to update the [evaluation_config.yaml](../config_file_examples/evaluation_config.yaml) and use it then run
the following command from the **src/** folder:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name evaluation_config.yaml
```

In case you want to evaluate the accuracy of the quantized model then benchmark it, you can either launch the evaluation
operation mode followed by the [benchmark service](../benchmarking/README.md) that describes in details how to proceed
or you can use chained services like launching **[chain_eqeb](../config_file_examples/chain_eqeb_config.yaml)** example
with command below:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_eqeb_config.yaml
```

</details>
<details open><summary><a href="#3"><b>3. Visualize the evaluation results</b></a></summary><a id="3"></a>

You can retrieve the confusion matrix generated after evaluating the float/quantized model on the test set by navigating
to the appropriate directory within **experiments_outputs/\<date-and-time\>**.

You can also find the evaluation results saved in the log file **stm32ai_main.log** under **
experiments_outputs/\<date-and-time\>**.

</details>
