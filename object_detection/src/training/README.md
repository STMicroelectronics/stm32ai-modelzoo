# <a id="">Object detection STM32 model training</a>

This readme shows how to train from scratch or apply transfer learning on an object detection model using a custom
dataset.
As an example, we will demonstrate the workflow on the Pascal VOC 2012 dataset, which can be downloaded directly
in [YOLO Darknet TXT](https://roboflow.com/formats/yolo-darknet-txt) format
from [here](https://public.roboflow.com/object-detection/pascal-voc-2012/1/download/darknet):

## <a id="">Table of contents</a>

### <a href="#1">1. Prepare the dataset</a>

### <a href="#2">2. Create your training configuration file</a>

#### <a href="#2-1">2.1  Overview</a>

#### <a href="#2-2">2.2  General settings</a>

#### <a href="#2-3">2.3  Dataset specification</a>

#### <a href="#2-4">2.4  Dataset preprocessing</a>

#### <a href="#2-5">2.5  Data augmentation</a>

#### <a href="#2-6">2.6  Apply post-processing</a>

#### <a href="#2-7">2.7  Loading a model</a>

#### <a href="#2-8">2.8  Training setup</a>

#### <a href="#2-9">2.9  Hydra and MLflow settings</a>

### <a href="#3">3. Train your model</a>

### <a href="#4">4. Visualize training results</a>

#### <a href="#4-1">4.1  Saved results</a>

#### <a href="#4-2">4.2 Run tensorboard</a>

#### <a href="#4-3">4.3  Run MLFlow</a>

### <a href="#5">5. Advanced settings</a>

#### <a href="#5-1">5.1  Resuming a training</a>

#### <a href="#5-3">5.3  Transfer learning</a>

#### <a href="#5-5">5.5  Train, quantize, benchmark and evaluate your model</a>

### <a href="#A">Appendix A: Learning rate schedulers</a>

## <a id="1">1. Prepare the dataset</a>

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

## <a id="2">2. Create your training configuration file</a>

### <a id="2-1">2.1 Overview</a>

All the proposed services like the training of the model are driven by a configuration file written in the YAML
language.

For training, the configuration file should include at least the following sections:

- `general`, describes your project, including project name, directory where to save models, etc.
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

### <a id="2-2">2.2 General settings</a>

The first section of the configuration file is the `general` section that provides information about your project.

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

If you want your experiments to be fully reproducible, you need to activate the `deterministic_ops` attribute and set it
to True.
Enabling the `deterministic_ops` attribute will restrict TensorFlow to use only deterministic operations on the device,
but it may lead to a drop in training performance. It should be noted that not all operations in the used version of
TensorFlow can be computed deterministically.
If your case involves any such operation, a warning message will be displayed and the attribute will be ignored.

The `logs_dir` attribute is the name of the directory where the MLFlow and TensorBoard files are saved.

The `saved_models_dir` attribute is the name of the directory where models are saved, which includes the trained model
and the quantized model. These two directories are located under the top level <hydra> directory.

The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy and Tensorflow random
generators at the beginning of the main script. This is an optional attribute, the default value being 123. If you don't
want random generators to be seeded, then set `global_seed` to 'None' (not recommended as this would make training
results less reproducible).

The `gpu_memory_limit` attribute sets an upper limit in GBytes on the amount of GPU memory Tensorflow may use. This is
an optional attribute with no default value. If it is not present, memory usage is unlimited. If you have several GPUs,
be aware that the limit is only set on logical gpu[0].

The `model_path` attribute is used to specify the path to the model file that you want to fine-tune or resume training
from. This parameter is essential for loading the pre-trained weights of the model and continuing the training process.
By providing the path to the model file, you can easily fine-tune the model on a new dataset or resume training from a
previous checkpoint. This allows you to leverage the knowledge learned by the model on a previous task and apply it to a
new problem, saving time and resources in the process.

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

### <a id="2-3">2.3 Dataset specification</a>

Information about the dataset you want use is provided in the `dataset` section of the configuration file, as shown in
the YAML code below.

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

If a validation set path is not provided, the available data under the training_path directory is automatically split
into a training set and a validation set.
By default, the split ratio is 80:20, with 80% of the data used for training
and 20% used for validation. However, you can customize the split ratio by specifying the percentage to be used for the
validation set in the `validation_split` parameter. This allows you to adjust the size of the validation set based on
the
size of your dataset and the level of accuracy you want to achieve.

It is important to note that having a validation set is crucial for evaluating the performance of your model during
training and preventing overfitting.

If a `test_path` is not provided to evaluate the model accuracy after training and quantization, the validation set is
used as the test set by default. This means that the model's performance on the validation set during training will
serve as an estimate of its accuracy on unseen data. However, it is generally recommended to use a separate test set to
evaluate the model's performance after training and quantization, as this provides a more reliable estimate of its
accuracy on new data. Using a separate test set also helps to ensure that the model has not overfit to the validation
set during training.

### <a id="2-4">2.4 Dataset preprocessing</a>

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
    interpolation: bilinear
    aspect_ratio: fit
  color_mode: rgb
```

The pixels of the input images are in the interval [0, 255], that is UINT8. If you set `scale` to 1./255 and `offset` to
0, they will be rescaled to the interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they will be
rescaled to the interval [-1.0, 1.0].

The `resizing` attribute specifies the image resizing methods you want to use:

- The value of `interpolation` must be one of *{"bilinear", "nearest", "bicubic", "area", "lanczos3", "lanczos5", "
  gaussian", "mitchellcubic"}*.
- The value of `aspect_ratio`  must have a value of  *"fit"* as we do not support other values such as *"crop"*. If you
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

### <a id="2-5">2.5 Data augmentation</a>

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

### <a id="2-6">2.6 Apply post-processing</a>

Apply post-processing by modifiying the **postprocessing** parameters in **[user_config.yaml](../user_config.yaml)** as
the following:

- `confidence_thresh` - A *float* between 0.0 and 1.0, the score thresh to filter detections .
- `NMS_thresh` - A *float* between 0.0 and 1.0, NMS thresh to filter and reduce overlapped boxes.
- `IoU_eval_thresh` - A *float* between 0.0 and 1.0, IOU thresh to calculate TP and FP.

### <a id="2-7">2.7 Loading a model</a>

Information about the model you want to train is provided in the `training` section of the configuration file.

The YAML code below shows how you can use a st_ssd_mobilenet_v1 model from the Model Zoo.

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

### <a id="2-8">2.8 Training setup</a>

The training setup is described in the `training` section of the configuration file, as illustrated in the example
below.

```yaml
training:
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
      mode: min
      restore_best_weights: true
      patience: 60
```

The `batch_size`, `epochs` and `optimizer` attributes are mandatory. All the others are optional.

The `dropout` attribute only makes sense if your model includes a dropout layer.

All the Tensorflow optimizers can be used in the `optimizer` subsection. All the Tensorflow callbacks can be used in
the `callbacks` subsection, except the ModelCheckpoint and TensorBoard callbacks that are built-in and can't be
redefined.

### <a id="2-9">2.9 Hydra and MLflow settings</a>

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

## <a id="3">**3. Train your model**</a>

To launch your model training using a real dataset, run the following command from **src/** folder:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name training_config.yaml
```

Trained h5 model can be found in corresponding **experiments_outputs/** folder.

## <a id="4">**4. Visualise your results**</a>

### <a id="4-1">**4.1 Saved results**</a>

All training and evaluation artifacts are saved under the current output simulation directory **"outputs/{run_time}"**.


### <a id="4-2">**4.2. Run tensorboard**</a>

To visualize the training curves logged by tensorboard, go to **"outputs/{run_time}"** and run the following command:

```bash
tensorboard --logdir logs
```

And open the URL `http://localhost:6006` in your browser.

### <a id="5">**4.3. Run MLFlow**</a>

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and
for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following
command:

```bash
mlflow ui
```

And open the given IP adress in your browser.

## <a id="5">5. Advanced settings</a>

### <a id="5-1">5.1. Resuming a training</a>

You may want to resume a training that you interrupted or that crashed.

When running a training, the model is saved at the end of each epoch in the **'saved_models'** directory that is under
the experiment directory (see section "2.2 Output directories and files"). The model file is named '
last_trained_model.h5' .

To resume a training, you first need to choose the experiment you want to restart from. Then, set
the `resume_training_from` attribute of the 'training' section to the path to the 'last_trained_model.h5' file of the
experiment. An example is shown below.

```yaml
operation_mode: training

dataset:
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
  resume_training_from: <path to the 'last_trained_model.h5' file of the interrupted/crashed training>
```

When setting the `resume_training_from` attribute, the `model:` subsection of the `training:` section and
the `model_path` attribute of the `general:` section should not be used. An error will be thrown if you do so.

The configuration file of the training you are resuming should be reused as is, the only exception being the number of
epochs. If you make changes to the dropout rate, the frozen layers or the optimizer, they will be ignored and the
original settings will be kept. Changes made to the batch size or the callback section will be taken into account.
However, they may lead to unexpected results.

### <a id="5-2">5.2 Train, quantize, benchmark and evaluate your models</a>

In case you want to train and quantize a model, you can either launch the training operation mode followed by the
quantization operation on the trained model (please refer to quantization **[README.md](../quantization/README.md)**
that describes in details the quantization part) or you can use chained services like
launching [chain_tqe](../config_file_examples/chain_tqe_config.yaml) example with command below:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_tqe_config.yaml
```

This specific example trains a mobilenet v2 model with imagenet pre-trained weights, fine tunes it by retraining latest
seven layers but the fifth one (this only as an example), and quantizes it 8-bits using quantization_split (30% in this
example) of the train dataset for calibration before evaluating the quantized model.

In case you also want to execute a benchmark on top of training and quantize services, it is recommended to launch the
chain service called [chain_tqeb](../config_file_examples/chain_tqeb_config.yaml) that stands for train, benchmark,
quantize, evaluate, benchmark like the example with command below:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_tqeb_config.yaml
```

This specific example uses the "Bring Your Own Model" feature using `model_path`, then fine tunes the initial model by
retraining all the layers but the twenty first (as an example), benchmarks the float model STM32H747I-DISCO board using
the STM32Cube.AI developer cloud, quantizes it 8-bits using quantization_split (30% in this example) of the train
dataset for calibration before evaluating the quantized model and benchmarking it.

## <a id="A">Appendix A: Learning rate schedulers</a>

A number of callbacks are available that implement different learning rate decay functions. The *ReduceLROnPlateau*
and *LearningRateScheduler* schedulers are Keras callbacks, the others are provided with the Model Zoo. They all update
the learning rate at the beginning of each epoch.

To use one of these learning rate schedulers, simply add it to the list of callbacks in the `training:` section of your
configuration file.

### <a id="a-1">A.1 Plotting the learning rate before training</a>

A script that plots the learning rate schedule without running a training is available. To run it, change the current
directory to *\<MODEL-ZOO-ROOT\>image_classification/src/training* and execute **plot_learning_rate_schedule.py**. The
script reads the `training:` section of your configuration file to get the number of training epochs, and the name and
arguments of the learning rate scheduler in the `callbacks:` subsection.

We encourage you to run this script. It does not require any extra work as it only needs your configuration file. It may
save you a lot of time to choose a learning rate scheduler and tune its parameters.

You can use the script to vizualize the output of the learning rate schedulers that are presented in the following
schedule. Just copy the examples and paste them to a configuration file.

Note that the script cannot be used with the Tensorflow *ReduceLROnPlateau* scheduler as the learning rate schedule is
only available after training.

### <a id="a-2">A.2 Keras ReduceLROnPlateau scheduler</a>

An example of usage of the Keras ReduceLROnPlateau learning rate scheduler is shown below.

```yaml
training:
  optimizer:
    Adam:
      learning_rate: 0.001
  callbacks:
    ReduceLROnPlateau:
      monitor: val_loss
      factor: 0.5
      patience: 20
      min_lr: 1e-7
      verbose: 0   # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

Refer to the Tensorflow documentation for more detail about the *ReduceLROnPlateau* callback.

### <a id="a-3">A.3 Keras LearningRateScheduler scheduler</a>

An example of usage of the Tensorflow *LearningRateScheduler* scheduler is shown below.

```yaml
training:
  epochs: 200
  optimizer: Adam
  callbacks:
    LearningRateScheduler: # The schedule is provided using a lambda function.
      schedule: |-
        lambda epoch, lr:
           (0.0005*epoch + 0.00001) if epoch < 20
           else (0.01 if epoch < 50
           else (lr / (1 + 0.0005 * epoch)
        ))
      verbose: 0   # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

In this example, the learning rate decay function includes 3 phases:

1. linear warmup from 0.00001 to 0.01 over the first 20 epochs
2. constant step at 0.01 for the next 30 epochs
3. time-based decay over the remaining epochs.

If you only want to implement a number of constant learning rate steps, there is no need to use the *
LearningRateScheduler* callback.
You can use the Model Zoo *LRPiecewiseConstantDecay* callback that is available for that purpose and is simpler to use.

Refer to the Tensorflow documentation for more detail about the *LearningRateScheduler* callback.

### <a id="a-4">A.4 LRLinearDecay scheduler</a>

This callback applies a 2 phases decay function to the learning rate:

1. Hold phase: the learning rate is held constant at its initial value for a number of epochs.
2. Decay phase: the learning rate decays linearly over a number of epochs.

An example is shown below.

```yaml
training:
  epochs: 200
  optimizer: Adam
  callbacks:
    LRLinearDecay:
      initial_lr: 0.001   # Initial learning rate.
      hold_steps: 20      # Number of epochs to hold the learning rate constant at 'initial_lr' before starting to decay.
      decay_steps: 150    # Number of epochs to decay linearly over.
      end_lr: 1e-7        # End value of the learning rate.
      verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

### <a id="a-5">A.5 LRExponentialDecay scheduler</a>

This callback applies a 2 phases decay function to the learning rate:

1. Hold phase: the learning rate is held constant at its initial value for a number of epochs.
2. Decay phase: the learning rate decays following an exponential function.

```yaml
training:
  epochs: 200
  optimizer: Adam
  callbacks:
    LRExponentialDecay:
      initial_lr: 0.001  # Initial learning rate.
      hold_steps: 20     # Number of epochs to hold the learning rate constant at 'initial_lr' before starting to decay.
      decay_rate: 0.02   # A float, the decay rate of the exponential. Increasing the value causes the learning rate to decrease faster.
      min_lr: 1e-7       # minimum value of the learning rate.
      verbose: 0         # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

### <a id="a-6">A.6 LRStepDecay scheduler</a>

This callback applies a staircase decay function with an exponential trend to the learning rate.

```yaml
training:
  epochs: 200
  optimizer: Adam
  callbacks:
    LRStepDecay:
      initial_lr: 0.001   # Initial learning rate.
      step_size: 30       # The number of epochs to hold the learning rate constant between two drops.
      decay_rate: 0.4     # The decay rate of the exponential. Decreasing the value of `decay_rate`
      # causes the learning rate to decrease faster.
      min_lr: 1e-7        # Minimum value of the learning rate.
      verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

### <a id="a-7">A.7 LRCosineDecay scheduler</a>

This callback applies a 3 phases decay function to the learning rate:

1. Hold phase: the learning rate is held constant at its initial value.
3. Cosine decay phase: the learning rate decays over a number of epochs
   following a cosine function until it reaches its target value.
4. On target phase: the leaning rate is held constant at its target value for any number of subsequent epochs.

```yaml
training:
  epochs: 200
  optimizer: Adam
  callbacks:
    LRCosineDecay:
      initial_lr: 0.001   # Initial learning rate.
      hold_steps: 20      # The number of epochs to hold the learning rate constant between two drops.
      decay_steps: 180    # the number of steps to decay over following a cosine function
      end_lr: 1e-7        # The learning rate value reached at the end of the cosine decay phase. 
      # The learning rate is held constant at this value for any subsequent epochs.
      verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

If `hold_steps` is set to 0, there is no hold phase and the learning rate immediately starts decaying from `initial_lr`.

If `hold_steps` + `decay_steps` is equal to the total number of epochs, the cosine decay ends at the last epoch of the
training with the learning rate reaching `end_lr`. There is no on-target constant learning rate phase in this case.

### <a id="a-8">A.8 LRWarmupCosineDecay scheduler</a>

This callback applies a 4 phases decay function to the learning rate:

1. Warmup phase: the learning rate increases linearly from an initial value over a number of epochs until it reaches its
   maximum value.
2. Hold phase: the learning rate is held constant at its maximum value for a number of epochs.
3. Cosine decay phase: the learning rate decays over a number of epochs following a cosine function until it reaches its
   target value.
4. On target phase: the leaning rate is held constant at its target value for any number of subsequent epochs.

```yaml
training:
  epochs: 400
  optimizer: Adam
  callbacks:
    LRWarmupCosineDecay:
      initial_lr: 1e-6   # Initial learning rate.
      warmup_steps: 30   # the number of epochs to increase the learning rate linearly over.
      max_lr: 0.001      # The maximum value of the learning rate reached at the end of the linear increase phase
      hold_steps: 50     # the number of epochs to hold the learning rate constant at `max_lr` before starting to decay
      decay_steps: 320   # the number of steps to decay over following a cosine function.
      end_lr: 1e-6       # the learning rate value reached at the end of the cosine decay phase. The learning rate
      # is held constant at this value for any subsequent epochs.
      verbose: 0         # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

About the arguments:

- If `warmup_steps` is set to 0, there is no warmup phase and the learning rate starts at `max_lr` (the `initial_lr`
  argument does not apply in this case and should not be used).
- If `hold_steps` is set to 0, there is no hold phase and the learning rate immediately starts decaying after
  reaching `max_lr`.
- If `warmup_steps` + `hold_steps` + `decay_steps` is equal to the total number of epochs, the cosine decay ends at the
  last epoch of the training with the learning rate reaching `end_lr`. There is no on-target constant learning rate
  phase in this case.
- If `warmup_steps` and `hold_steps` are both equal to 0, the callback implements the same cosine decay function as the
  LRCosineDecay callback.

### <a id="a-9">A.9 LRCosineDecayRestarts scheduler</a>

This callback applies a cosine decay function with restarts to the learning rate.

At the beginning of the training, the learning rate decays from an initial value following a cosine function. After a
number of epochs, the first restart occurs, i.e. the learning rate restarts from an initial value. Then, it decays
following a cosine function until the second restart occurs, etc. A restart followed by a cosine decay is referred to as
a "period". Periods get longer and longer and the initial learning rate of each period gets smaller and smaller as the
training progresses.

Reference paper:
[Loshchilov & Hutter, ICLR2016](https://arxiv.org/abs/1608.03983), SGDR: Stochastic Gradient Descent with Warm Restarts.

```yaml
training:
  epochs: 350
  optimizer: Adam
  callbacks:
    LRCosineDecayRestarts:
      initial_lr: 0.001      # Initial learning rate.
      first_decay_steps: 50  # An integer, the number of epochs to decay over in the first period. 
      # The numbers of epochs of the subsequent periods are a function of `first_decay_steps` and `t_mul`
      end_lr: 1e-6           # The value of the learning rate reached at the end of each period
      t_mul: 2               # A positive integer, used to derive the number of epochs of each period.
      m_mul: 0.8             # A float smaller than or equal to 1.0, used to derive the initial learning rate of the i-th period.

      verbose: 0             # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

The `t_mul` argument is used to derive the number of epochs of each period. The number of epochs of the i-th period is
equal to "`t_mul`**(i - 1) * `first_decay_steps`". For example, if `first_decay_steps` is equal to 50 and `t_mul` is
equal to 2, the numbers of epochs of the periods are 50, 100, 200, 450, etc.

The `m_mul` argument is used to derive the initial learning rate of the i-th period. If LR(i - 1) is the initial
learning rate of period i-1, the initial learning rate of period i is equal to "LR(i-1) * `m_mul`". For example,
if `initial_lr` is equal to 0.01 and `m_mul` is equal to 0.7, the initial learning rates of the restarts are 0.007,
0.0049, 0.0512, 0.00343, etc. if `m_mul` is equal to 1.0, the initial learning rate is the same for all the restarts.

### <a id="a-10">A.10 LRPolynomialDecay scheduler</a>

This callback applies a polynomial decay function to the learning rate, given a provided initial learning rate. See
the `schedule` method of the callback.

```yaml
training:
  epochs: 300
  optimizer: Adam
  callbacks:
    LRPolynomialDecay:
      initial_lr: 0.001   # Initial learning rate.
      hold_steps: 30      # number of epochs to hold the learning rate constant at `initial_lr` before starting to decay
      decay_steps: 270    # The decay rate of the exponential. Decreasing the value of `decay_rate` causes the learning rate to decrease faster.
      end_lr: 1e-7        # end learning rate.
      verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

### <a id="a-11">A.11 LRPolynomialDecayRestarts scheduler</a>

This callback applies a polynomial decay function to the learning rate, given a provided initial learning rate. See
the `schedule` method of the callback. If the `power` argument is set to 1.0, the learning rate decreases linearly.

```yaml
training:
  epochs: 400
  optimizer: Adam
  callbacks:
    LRPolynomialDecayRestarts:
      initial_lr: 0.001   # Initial learning rate.
      hold_steps: 30      # the number of epochs to hold the learning rate constant at `initial_lr` before starting to decay.
      decay_steps: 120    # see `schedule` function
      end_lr: 1e-7        # Minimum value of the learning rate.
      power: 0.5          # The power of the polynomial
      verbose: 0          # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

With the settings of the example above, the learning rate restarts from 0.00001 at epochs 130, 230 and 330.

### <a id="a-12">A.12 LRPiecewiseConstantDecay scheduler</a>

The PiecewiseConstantDecay scheduler applies a piecewise constant decay function (a number of constant value steps) to
the learning rate. See the `schedule` method of the callback.

```yaml
training:
  epochs: 200
  optimizer: Adam
  callbacks:
    LRPiecewiseConstantDecay:
      boundaries: [ 30, 70, 150 ]              # The list of epochs when the learning rate starts a new constant step.
      values: [ 0.01, 0.005, 0.001, 0.0001 ]   # The number of epochs to hold the learning rate constant between two drops.
      verbose: 0                             # verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

The `boundaries` argument is a list of integers with strictly increasing values that provide the epoch numbers when the
learning rate starts a new constant step.
The `values` argument is a list of floats that specifies the value of the learning rate for each interval defined by
the `boundaries` argument. It should have one more element than `boundaries`, the last element being the learning rate
value for any remaining epoch after the last epoch specified in `boundaries` (the last element).

In the example above, the learning rate is 0.01 for the first 30 epochs, 0.005 for the next 40 epochs, 0.001 for the
next 80 epochs, and 0.0001 for any
subsequent epoch.
