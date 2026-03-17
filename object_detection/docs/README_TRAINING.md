# <a id="">Object Detection STM32 Model Training</a>

This readme shows how to train from scratch or apply transfer learning on an object detection model using a custom
dataset.
As an example, we will demonstrate the workflow on the Pascal VOC 2012 dataset, which can be downloaded directly
in [YOLO Darknet TXT](https://roboflow.com/formats/yolo-darknet-txt) format
from [here](https://public.roboflow.com/object-detection/pascal-voc-2012/1/download/darknet):



<details open><summary><a href="#1"><b>1. Prepare the dataset</b></a></summary><a id="1"></a>

After downloading and extracting the dataset files, the dataset directory tree should look as below:

```bash
dataset_directory/
...train/
......train_image_1.jpg
......train_image_1.txt
......train_image_2.jpg
......train_image_2.txt
...val/
......val_image_1.jpg
......val_image_1.txt
......val_image_2.jpg
......val_image_2.txt
```

Please note that YOLO Darknet only supports this specific directory structure for the dataset, and other formats are not
compatible.

</details>
<details open><summary><a href="#2"><b>2. Create your training configuration file</b></a></summary><a id="2"></a>
<ul><details open><summary><a href="#2-1">2.1 Overview</a></summary><a id="2-1"></a>

All the proposed services like the training of the model are driven by a configuration file written in the YAML
language.

For training, the configuration file should include at least the following sections:

- `general`, describes your project, including project name, directory where to save models, etc.
- `model`, describes the model type, the model path, the input shape of the model, etc.
- `operation_mode`, describes the service or chained services to be used
- `dataset`, describes the dataset you are using, including directory paths, class names, etc.
- `preprocessing`, specifies the methods you want to use for rescaling and resizing the images.
- `postprocessing`, parameter refers to the techniques used to refine the output of the model. This can include methods
  such as non-maximum suppression (NMS), which removes overlapping bounding boxes and retains only the most confident
  detections. Other postprocessing techniques may include filtering out detections below a certain confidence threshold,
  or applying additional heuristics to improve the accuracy of the model's predictions. By specifying the appropriate
  postprocessing methods, you can fine-tune the performance of your object detection model and achieve more accurate
  results.
- `training`, specifies your training setup, including batch size, number of epochs, optimizer, callbacks, etc.
- `mlflow`, specifies the folder to save MLFlow logs.
- `hydra`, specifies the folder to save Hydra logs.

This tutorial only describes the settings needed to train a model. In the first part, we describe basic settings.
At the end of this readme, you can also find more advanced settings and callbacks supported.

</details></ul>
<ul><details open><summary><a href="#2-2">2.2 General settings</a></summary><a id="2-2"></a>

The first section of the configuration file is the `general` section that provides information about your project.

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
```

If you want your experiments to be fully reproducible, you need to activate the `deterministic_ops` attribute and set it
to True.
Enabling the `deterministic_ops` attribute will restrict TensorFlow to use only deterministic operations on the device,
but it may lead to a drop in training performance. It should be noted that not all operations in the used version of
TensorFlow can be computed deterministically.
If your case involves any such operation, a warning message will be displayed and the attribute will be ignored.

The `logs_dir` attribute is the name of the directory where the MLFlow and TensorBoard files are saved.

The `saved_models_dir` attribute is the name of the directory where models are saved, which includes the trained model
and the quantized model. These two directories are located under the top level <hydra> directory.

The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy, and TensorFlow random generators at the beginning of the main script. This is an optional attribute, the default value being 123. If you don't want random generators to be seeded, then set `global_seed` to 'None' (not recommended as this would make training results less reproducible).

The `gpu_memory_limit` attribute sets an upper limit in GBytes on the amount of GPU memory TensorFlow may use. This is an optional attribute with no default value. If it is not present, memory usage is unlimited. If you have several GPUs, be aware that the limit is only set on logical gpu[0].

<ul><details open><summary><a href="#2-3">2.3 Model specifications</a></summary><a id="2-3"></a>

The `model` section and its attributes are shown below.

```yaml
model:
  model_type: st_yoloxn
  model_name: st_yoloxn
  #  model_path: <file-path>           # Path to a model file.
```

The `model_path` attribute is used to specify the path to the model file that you want to fine-tune or resume training
from. This parameter is essential for loading the pre-trained weights of the model and continuing the training process.
By providing the path to the model file, you can easily fine-tune the model on a new dataset or resume training from a
previous checkpoint. This allows you to leverage the knowledge learned by the model on a previous task and apply it to a
new problem, saving time and resources in the process.

The `model_type` attribute specifies the type of the model architecture that you want to train, the model family. The `model_name` attribute specifies the exact variant to use within the `model_type` family. It is important to note that only certain models are supported. These models include:

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
It is important to note that each model type has specific requirements in terms of input image size, output size of the
head and/or backbone, and other parameters. Therefore, it is important to choose the appropriate model type for your
specific use case, and to configure the training process accordingly.

</details></ul>
<ul><details open><summary><a href="#2-4">2.4 Dataset specification</a></summary><a id="2-4"></a>

Information about the dataset you want to use is provided in the `dataset` section of the configuration file, as shown in the YAML code below.

```yaml
dataset:
  format: pascal_voc
  dataset_name: pascal_voc                                    # Dataset name. Optional, defaults to "<unnamed>".
  class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ] # Names of the classes in the dataset.
  training_path: <training-set-root-directory>               # Path to the root directory of the training set.
  validation_path: <validation-set-root-directory>           # Path to the root directory of the validation set.
  validation_split: 0.2                                      # Training/validation sets split ratio.
  test_path: <test-set-root-directory>                       # Path to the root directory of the test set.
  quantization_path: <quantization-set-root-directory>       # Path to the root directory of the quantization set.
  quantization_split:                                        # Quantization split ratio.
  seed: 123                                                  # Random generator seed used when splitting a dataset.
```

The state machine below describes the rules to follow when handling dataset paths for the training.
<div align="center" style="width:50%; margin: auto;">

![plot](../../common/doc/img/state_machine_training.JPG)
</div>

If a validation set path is not provided, the available data under the training_path directory is automatically split into a training set and a validation set. By default, the split ratio is 80:20, with 80% of the data used for training and 20% used for validation. However, you can customize the split ratio by specifying the percentage to be used for the validation set in the `validation_split` parameter. This allows you to adjust the size of the validation set based on the size of your dataset and the level of accuracy you want to achieve.

It is important to note that having a validation set is crucial for evaluating the performance of your model during training and preventing overfitting.

If a `test_path` is not provided to evaluate the model accuracy after training and quantization, the validation set is used as the test set by default. This means that the model's performance on the validation set during training will serve as an estimate of its accuracy on unseen data. However, it is generally recommended to use a separate test set to evaluate the model's performance after training and quantization, as this provides a more reliable estimate of its
accuracy on new data. Using a separate test set also helps to ensure that the model has not overfit to the validation set during training.

</details></ul>
<ul><details open><summary><a href="#2-5">2.5 Dataset preprocessing</a></summary><a id="2-5"></a>

The images from the dataset need to be preprocessed before they are presented to the network. This includes rescaling
and resizing, as illustrated in the YAML code below.

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

The pixels of the input images are in the interval [0, 255], that is UINT8. If you set `scale` to 1./255 and `offset` to
0, they will be rescaled to the interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they will be
rescaled to the interval [-1.0, 1.0].

The `resizing` attribute specifies the image resizing methods you want to use:

- The value of `interpolation` must be one of *{"bilinear", "nearest", "bicubic", "area", "lanczos3", "lanczos5", "gaussian", "mitchellcubic"}*.
- The value of `aspect_ratio` must be *"fit"* as we do not support other values such as *"crop"*. If you set it to *"fit"*, the resized images will be distorted if their original aspect ratio is not the same as in the resizing size.

The `color_mode` attribute must be one of "*grayscale*", "*rgb*" or "*rgba*".

When you define the preprocessing parameter in the configuration file, the annotation file for the object detection
dataset will be automatically modified during preprocessing to ensure that it is aligned with the preprocessed images.
This typically involves updating the bounding box coordinates to reflect any resizing or cropping that was performed
during preprocessing.

This automatic modification of the annotations file is an important step in preparing
the dataset for object detection, as it ensures that the annotations accurately reflect the preprocessed images and
enables the model to learn from the annotated data.

</details></ul>
<ul><details open><summary><a href="#2-6">2.6 Data augmentation</a></summary><a id="2-6"></a>

Data augmentation is a crucial technique for improving the performance of object detection models, especially when the
dataset is too small. The data_augmentation section of the configuration file specifies the data augmentation functions
to be applied to the input images, such as rotation, shearing, translation, flipping, and blurring. Each function can be
customized with specific parameter settings to control the degree and type of augmentation applied to the input images.

It is important to note that the annotation files will also be modified during data
augmentation to ensure that it is aligned with the augmented images. This typically involves updating the bounding box
coordinates to reflect any transformations or modifications that were performed during data augmentation. Ensuring that
the annotations file accurately reflects the augmented images is crucial for training the object detection model and
evaluating its performance.

The data augmentation functions to apply to the input images are specified in the `data_augmentation` section of the
configuration file as illustrated in the YAML code below.

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
<ul><details open><summary><a href="#2-7">2.7 Apply post-processing</a></summary><a id="2-7"></a>

Apply post-processing by modifying the **postprocessing** parameters in **[user_config.yaml](../user_config.yaml)** as follows:

- `confidence_thresh` - A *float* between 0.0 and 1.0, the score threshold to filter detections.
- `NMS_thresh` - A *float* between 0.0 and 1.0, NMS threshold to filter and reduce overlapped boxes.
- `IoU_eval_thresh` - A *float* between 0.0 and 1.0, IoU threshold to calculate TP and FP.

</details></ul>
<ul><details open><summary><a href="#2-8">2.8 Loading a model</a></summary><a id="2-8"></a>

Information about the model you want to train is provided in the `training` section of the configuration file.

The YAML code below shows how you can use a st_yoloxn model from the Model Zoo.

```yaml
training:
  model:
    alpha: 0.25
    input_shape: (192, 192, 3)
    pretrained_weights: imagenet
```

The `pretrained_weights` attribute is set to "ImageNet", which indicates that the model will load the weights pretrained
on the ImageNet dataset for the backbone. This is a common practice in transfer
learning, where the model is initialized with weights learned from a large dataset and then fine-tuned on a smaller,
task-specific dataset.

However, it's worth noting that for some models, such as `Tiny YOLOv2`, the pretrained weights used are from the COCO
dataset instead of ImageNet. This is because COCO contains a wider range of object classes and is more relevant to
object detection tasks. By using COCO weights, the model can learn to detect a wider range of objects with higher
accuracy.
If `pretrained_weights` was set to "None", no pretrained weights would be loaded in the model and the training would
start *from scratch*, i.e. from randomly initialized weights.

</details></ul>
<ul><details open><summary><a href="#2-9">2.9 Training setup</a></summary><a id="2-9"></a>

The training setup is described in the `training` section of the configuration file, as illustrated in the example
below.

```yaml
training:
  batch_size: 64
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
      mode: min
      restore_best_weights: true
      patience: 60
```

The `batch_size`, `epochs` and `optimizer` attributes are mandatory. All the others are optional.

The `dropout` attribute only makes sense if your model includes a dropout layer.

All the TensorFlow optimizers can be used in the `optimizer` subsection. All the TensorFlow callbacks can be used in the `callbacks` subsection, except the ModelCheckpoint and TensorBoard callbacks that are built-in and can't be redefined.

A variety of learning rate schedulers are provided with the Model Zoo. If you want to use one of them, just include it in the `callbacks` subsection. Refer to [the learning rate schedulers README](../../common/training/lr_schedulers_README.md) for a description of the available callbacks and learning rate plotting utility.

</details></ul>
<ul><details open><summary><a href="#2-10">2.10 Hydra and MLflow settings</a></summary><a id="2-10"></a>

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used
to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment
directories. With the YAML code below, every time you run the Model Zoo, an experiment directory is created that
contains all the directories and files created during the run. The names of experiment directories are all unique as
they are based on the date and time of the run.

```yaml
hydra:
  run:
    dir: ./tf/src/experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown below:

```yaml
mlflow:
  uri: ./tf/src/experiments_outputs/mlruns
```

</details></ul>
</details>
<details open><summary><a href="#3"><b>3. Train your model</b></a></summary><a id="3"></a>

To launch your model training using a real dataset, run the following command from the **src/** folder:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name training_config.yaml
```

The trained .keras model can be found in the corresponding **experiments_outputs/** folder.

</details>
<details open><summary><a href="#4"><b>4. Visualise your results</b></a></summary><a id="4"></a>
<ul><details open><summary><a href="#4-1">4.1 Saved results</a></summary><a id="4-1"></a>

All training and evaluation artifacts are saved under the current output simulation directory **"outputs/{run_time}"**.

</details></ul>
<ul><details open><summary><a href="#4-2">4.2 Run TensorBoard</a></summary><a id="4-2"></a>

To visualize the training curves logged by TensorBoard, go to **"outputs/{run_time}"** and run the following command:

```bash
tensorboard --logdir logs
```

And open the URL `http://localhost:6006` in your browser.

</details></ul>
<ul><details open><summary><a href="#4-3">4.3 Run MLflow</a></summary><a id="4-3"></a>

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and
for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following
command:

```bash
mlflow ui
```

And open the given IP address in your browser.

</details></ul>
</details>
<details open><summary><a href="#5"><b>5. Advanced settings</b></a></summary><a id="5"></a>
<ul><details open><summary><a href="#5-1">5.1 Resuming a training</a></summary><a id="5-1"></a>

You may want to resume a training that you interrupted or that crashed.

When running a training, the model is saved at the end of each epoch in the **'saved_models'** directory that is under the experiment directory (see section "2.2 Output directories and files"). The model file is named 'last_trained_model.keras'.

To resume a training, you first need to choose the experiment you want to restart from. Then, set
the `resume_training_from` attribute of the 'training' section to the path to the 'last_trained_model.keras' file of the
experiment. An example is shown below.

```yaml
operation_mode: training

dataset:
  format: tfs
  dataset_name: coco
  training_path: <training-set-root-directory>
  validation_split: 0.2
  test_path: <test-set-root-directory>

training:
  batch_size: 64
  epochs: 150      # The number of epochs can be changed for resuming.
  dropout: 0.3
  frozen_layers: (0:1)
  optimizer:
    Adam:
      learning_rate: 0.001
  callbacks:
    ReduceLROnPlateau:
      monitor: val_accuracy
      factor: 0.1
      patience: 10
  resume_training_from: <path to the 'last_trained_model.keras' file of the interrupted/crashed training>
```

When setting the `resume_training_from` attribute, the `model:` subsection of the `training:` section and the `model_path` attribute of the `model:` section should not be used. An error will be thrown if you do so.

The configuration file of the training you are resuming should be reused as is, the only exception being the number of
epochs. If you make changes to the dropout rate, the frozen layers or the optimizer, they will be ignored and the
original settings will be kept. Changes made to the batch size or the callback section will be taken into account.
However, they may lead to unexpected results.

</details></ul>
<ul><details open><summary><a href="#5-2">5.2 Train, quantize, benchmark, and evaluate your models</a></summary><a id="5-2"></a>

In case you want to train and quantize a model, you can either launch the training operation mode followed by the quantization operation on the trained model (please refer to the quantization **[README.md](./README_QUANTIZATION.md)** that describes in detail the quantization part) or you can use chained services like launching [chain_tqe](../config_file_examples/chain_tqe_config.yaml) example with the command below:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_tqe_config.yaml
```

This specific example trains a ST YOLOXn model , fine-tunes it by retraining the latest seven layers but the fifth one (this only as an example), and quantizes it to 8-bits using quantization_split (30% in this example) of the train dataset for calibration before evaluating the quantized model.

In case you also want to execute a benchmark on top of training and quantize services, it is recommended to launch the chain service called [chain_tqeb](../config_file_examples/chain_tqeb_config.yaml) that stands for train, quantize, evaluate, benchmark like the example with the command below:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_tqeb_config.yaml
```

This specific example uses the "Bring Your Own Model" feature using `model_path`, then fine-tunes the initial model by retraining all the layers but the twenty-first (as an example), benchmarks the float model on the STM32H747I-DISCO board using the STEdgeAI developer cloud, quantizes it to 8-bits using quantization_split (30% in this example) of the train dataset for calibration before evaluating the quantized model and benchmarking it.

</details></ul>
</details>

