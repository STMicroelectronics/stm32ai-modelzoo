# <a id="">Semantic Segmentation STM32 model training</a>

This readme shows how to train from scratch or apply transfer learning on a semantic segmentation model.
As an example we will demonstrate the workflow on the [Pascal VOC 2012](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/) segmentation dataset.


<details open><summary><a href="#1"><b>1. Prepare the dataset</b></a></summary><a id="1"></a>

The dataset should be structured to include directories for the images and their corresponding segmentation masks, as well as lists of filenames for training and validation. The directory tree for the dataset is outlined below:

```bash
dataset_root_directory/
   Images/
      image_1.jpg
      image_2.jpg
      ...
   Segmentation_masks/
      mask_1.png
      mask_2.png
      ...
   Image_sets/
      train.txt
      val.txt
```

A directory contains all the images used for training, validation, and testing, and another one holds the segmentation masks corresponding to the images and the last one is for text files like `train.txt` and `val.txt` which list the filenames of images that are included in the training and validation sets, respectively.

**Please ensure that the segmentation masks are formatted as images with pixel values as integers. Each integer should correspond to a different class label, effectively segmenting the image into regions based on the class they belong to.**
</details>

<details open><summary><a href="#2"><b>2.  Create your training configuration file</b></a></summary><a id="2"></a>
<ul><details open><summary><a href="#2-1">2.1  Overview</a></summary><a id="2-1"></a>

All the proposed services like the training of the model are driven by a configuration file written in the YAML language.

For training, the configuration file should include at least the following sections:

- `general`, describes your project, including your project name, model type, etc.
- `operation_mode`, describes the service or chained services to be used.
- `dataset`, describes the dataset you are using, including directory paths, class names, etc.
- `preprocessing`, specifies the methods you want to use for rescaling and resizing the images. 
- `training`, specifies your training setup, including batch size, number of epochs, optimizer, callbacks, etc.
- `mlflow`, specifies the folder to save MLFlow logs.
- `hydra`, specifies the folder to save Hydra logs.

This tutorial only describes the settings needed to train a model. In the first part, we describe basic settings.
At the end of this readme, you can also find more advanced settings and callbacks supported.
</details></ul>

<ul><details open><summary><a href="#2-2">2.2  General settings</a></summary><a id="2-2"></a>

The first section of the configuration file is the `general` section that provides information about your project.

```yaml
general:
  project_name: segmentation 
  model_type : deeplab_v3  
  logs_dir: logs
  saved_models_dir: saved_models
  gpu_memory_limit: 12
  global_seed: 127
  display_figures: False
```

The `model_type` parameter specifies the name of the model in use. Presently, the model zoo supports `deeplab_v3`. Additionally, the `Bring Your Own Model (BYOM)` functionality enables users to train and integrate their distinct models.

The `logs_dir` attribute is the name of the directory where the MLFlow and TensorBoard files are saved. The `saved_models_dir` attribute is the name of the directory where trained models are saved. These two directories are located under the top level "hydra" directory (please see [chapter 2.8](#2-8) for hydra informations).

The `gpu_memory_limit` attribute sets an upper limit in GBytes on the amount of GPU memory Tensorflow may use. This is an optional attribute with no default value. If it is not present, memory usage is unlimited. If you have several GPUs, be aware that the limit is only set on logical gpu[0].

The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy and Tensorflow random generators at the beginning of the main script. This is an optional attribute, the default value being 120. If you don't want random generators to be seeded, then set `global_seed` to 'None' (not recommended as this would make training results less reproducible).

</details></ul>

<ul><details open><summary><a href="#2-3">2.3  Dataset specification</a></summary><a id="2-3"></a>

Information about the dataset you want use is provided in the `dataset` section of the configuration file, as shown in the YAML code below.

```yaml
dataset:
  name: pascal_voc
  class_names: ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
                "car", "cat", "chair", "cow", "dining table", "dog", "horse", "motorbike",
                "person", "potted plant", "sheep", "sofa", "train", "tv/monitor"]

  training_path: ../datasets/VOC2012_train_val/JPEGImages
  training_masks_path: ../datasets/VOC2012_train_val/SegmentationClass
  training_files_path: ../datasets/VOC2012_train_val/ImageSets/Segmentation/train.txt

  validation_path: ../datasets/VOC2012_train_val/JPEGImages
  validation_masks_path: ../datasets/VOC2012_train_val/SegmentationClass
  validation_files_path: ../datasets/VOC2012_train_val/ImageSets/Segmentation/val.txt
  validation_split: 
  
  test_path: 
  test_masks_path: 
  test_files_path: 

```

the `name` holds the identifier for the dataset, which in this case is pascal_voc. The `class_names` is a list of class names that the dataset contains. It includes a variety of categories such as "background", "aeroplane", "bicycle", and so on, for a total of 20 object classes plus the "background" class.

The `training_path` specifies the directory path to the training images, the `training_masks_path` points to the location of the segmentation masks corresponding to the training images and `training_files_path` indicates the file that contains the list of image filenames used for training.

The `validation_path` is designated for the directory containing the validation images, the `validation_masks_path` directs to the segmentation masks associated with these validation images, while the `validation_files_path` provides the location of the file listing the image filenames to be used for validation purposes.

By default, when the validation_path is not provided, 80% of the data is used for the training set and the remaining 20% is used for the validation set.
If you want to use a different split ratio, you need to specify in `validation_split` the ratio to be used for the validation set (value between 0 and 1).

For testing, the `test_path`, `test_masks_path`, and `test_files_path` keys are present but not populated with paths. These would typically specify the directory for test images, the directory for the corresponding segmentation masks, and the file with the list of test image filenames, respectively. The absence of values suggests that the validation set is used as the test set.

</details></ul>

<ul><details open><summary><a href="#2-4">2.4  Dataset preprocessing</a></summary><a id="2-4"></a>

The images from the dataset need to be preprocessed before they are presented to the network. This includes rescaling and resizing, as illustrated in the YAML code below.

```yaml
preprocessing:
   rescaling: {scale : 1/127.5, offset : -1}
   resizing: {interpolation: bilinear, 
               aspect_ratio: "fit"}
   color_mode: rgb
```

The pixels of the input images are in the interval [0, 255], that is UINT8. If you set `scale` to 1./255 and `offset` to 0, they will be rescaled to the interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they will be rescaled to the interval [-1.0, 1.0].

The `resizing` attribute specifies the image resizing methods you want to use:
- The value of `interpolation` must be one of *{"bilinear", "nearest", "bicubic", "area", "lanczos3", "lanczos5", "gaussian", "mitchellcubic"}*.
- The value of `aspect_ratio` must be either *"fit"* or *"crop"*. If you set it to *"fit"*, the resized images will be distorted if original aspect ratio is not the same as in the resizing size. If you set it to *"crop"*, images will be cropped as necessary to preserve the aspect ratio.

The `color_mode` attribute must be one of "*grayscale*", "*rgb*" or "*rgba*".
</details></ul>

<ul><details open><summary><a href="#2-5">2.5  Data augmentation</a></summary><a id="2-5"></a>

Data augmentation is an effective technique to reduce the overfit of a model when the dataset is too small or the semantic segmentation problem to solve is too easy for the model.

The data augmentation functions to apply to the input images are specified in the `data_augmentation` section of the configuration file file as illustrated in the YAML code below.

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

The data augmentation functions with their parameter settings are applied to the input images in their order of appearance in the configuration file. 
Refer to the data augmentation documentation **[README.md](../data_augmentation/README.md)** for more information about the available functions and their arguments.
</details></ul>

<ul><details open><summary><a href="#2-6">2.6  Loading a model</a></summary><a id="2-6"></a>

Information about the model you want to train is provided in the `training` section of the configuration file.

The YAML code below shows how you can use a MobileNet V2 as a backbone to the `deeplab_v3` model from the Model Zoo.

```yaml
training:
  model: 
    name: mobilenet            # backbone topology for model_type 
    version: v2 
    alpha: 0.5
    output_stride: 16          # the only supported for now 
    input_shape: (512, 512, 3)
    pretrained_weights: imagenet
```

The `pretrained_weights` attribute is set to "ImageNet", which indicates that you want to load the weights pretrained on the ImageNet dataset and do a *transfer learning* type of training. 

If `pretrained_weights` was set to "null", no pretrained weights would be loaded in the model and the training would start *from scratch*, i.e. from randomly initialized weights.
</details></ul>

<ul><details open><summary><a href="#2-7">2.7  Training setup</a></summary><a id="2-7"></a>

The training setup is described in the `training` section of the configuration file, as illustrated in the example below.

```yaml
training:
  dropout: 0.6
  batch_size: 16
  epochs: 1
  optimizer:
    Adam:
      learning_rate: 0.005
  callbacks:          # Optional section
    ReduceLROnPlateau:
      monitor: val_accuracy
      mode: max
      factor: 0.5
      patience: 40
      min_lr: 1.0e-05
    EarlyStopping:
      monitor: val_accuracy
      mode: max
      restore_best_weights: true
      patience: 60
```

The `batch_size`, `epochs` and `optimizer` attributes are mandatory. All the others are optional.

The `dropout` attribute only makes sense if your model includes a dropout layer. 

All the Tensorflow optimizers can be used in the `optimizer` subsection. All the Tensorflow callbacks can be used in the `callbacks` subsection, except the ModelCheckpoint and TensorBoard callbacks that are built-in and can't be redefined.

A number of learning rate schedulers are provided with the Model Zoo as custom callbacks. The YAML code below shows how to use the LRCosineDecay scheduler that implements a cosine decay function.

```yaml
training:
   batch_size: 64
   epochs: 400
   optimizer: Adam
   callbacks:
      LRCosineDecay:
         initial_learning_rate: 0.01
         decay_steps: 170
         alpha: 0.001
```
Refer to [Appendix A: Learning rate schedulers](#A) for a list of the available learning rate schedulers.
</details></ul>

<ul><details open><summary><a href="#2-8">2.8  Hydra and MLflow settings</a></summary><a id="2-8"></a>

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment directories. With the YAML code below, every time you run the Model Zoo, an experiment directory is created that contains all the directories and files created during the run. The names of experiment directories are all unique as they are based on the date and time of the run.

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

<details open><summary><a href="#3"><b>3. Train your model</b></a></summary><a id="3"></a>

To launch your model training using a real dataset, run the following command from **src/** folder:
```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name training_config.yaml
```
Trained h5 model can be found in corresponding **experiments_outputs/** folder.
</details>

<details open><summary><a href="#4"><b>4. Visualize training results</b></a></summary><a id="4"></a>
<ul><details open><summary><a href="#4-1">4.1  Saved results</a></summary><a id="4-1"></a>

All training and evaluation artifacts are saved under the current output simulation directory **"outputs/{run_time}"**.

</details></ul>
<ul><details open><summary><a href="#4-2">4.2  Run tensorboard</a></summary><a id="4-2"></a>

To visualize the training curves logged by tensorboard, go to **"outputs/{run_time}"** and run the following command:

```bash
tensorboard --logdir logs
```

And open the URL `http://localhost:6006` in your browser.
</details></ul>
<ul><details open><summary><a href="#4-3">4.3  Run MLFlow</a></summary><a id="4-3"></a>

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following command:
```bash
mlflow ui
```
And open the given IP adress in your browser.
</details></ul>
</details>

<details open><summary><a href="#5"><b>5. Advanced settings</b></a></summary><a id="5"></a>
<ul><details open><summary><a href="#5-1">5.1  Training your own model</a></summary><a id="5-1"></a>

You may want to train your own model rather than a model from the Model Zoo.

This can be done using the `model_path` attribute of the `general:` section to provide the path to the model file to use as illustrated in the example below.

```yaml
general:
   model_path: <path-to-a-Keras-model-file>    # Path to the model file to use for training

operation_mode: training

dataset:
   training_path: <training-set-root-directory>    # Path to the root directory of the training set.
   validation_split: 0.2                           # Use 20% of the training set to create the validation set.
   test_path: <test-set-root-directory>            # Path to the root directory of the test set.

training:
   batch_size: 64
   epochs: 150
   dropout: 0.3
   frozen_layers: (0, -1)
   optimizer:
      Adam:                               
         learning_rate: 0.001
   callbacks:                    
      ReduceLROnPlateau:
         monitor: val_loss
         factor: 0.1
         patience: 10
```

The model file must be a Keras model file with a '.h5' filename extension.

The `model:` subsection of the `training:` section is not present as we are not training a model from the Model Zoo. An error will be thrown if it is present when `model_path` is set.

About the model loaded from the file:
- if some layers are frozen in the model, they will be reset to trainable before training. You can use the `frozen_layers` attribute if you want to freeze these layers (or different ones).
- If you set the `dropout` attribute but the model does not include a dropout layer, an error will be thrown. Reciprocally, an error will also occur if the model includes a dropout layer but the `dropout` attribute is not set.
- If the model was trained before, the state of the optimizer won't be preserved as the model is compiled before training.

</details></ul>
<ul><details open><summary><a href="#5-2">5.2  Resuming a training</a></summary><a id="5-2"></a>

You may want to resume a training that you interrupted or that crashed.

When running a training, the model is saved at the end of each epoch in the **'saved_models'** directory that is under the experiment directory (see section "2.2 Output directories and files"). The model file is named 'last_augmented_model.h5' .

To resume a training, you first need to choose the experiment you want to restart from. Then, set the `resume_training_from` attribute of the 'training' section to the path to the 'last_augmented_model.h5' file of the experiment. An example is shown below.

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
   resume_training_from: <path to the 'last_augmented_model.h5' file of the interrupted/crashed training>
```

When setting the `resume_training_from` attribute, the `model:` subsection of the `training:` section and the `model_path` attribute of the `general:` section should not be used. An error will be thrown if you do so.

The configuration file of the training you are resuming should be reused as is, the only exception being the number of epochs. If you make changes to the dropout rate, the frozen layers or the optimizer, they will be ignored and the original settings will be kept. Changes made to the batch size or the callback section will be taken into account. However, they may lead to unexpected results.

The state of the optimizer is saved in the **last_augmented_model.h5** file, so you will restart from where you left it. The model is called 'augmented' because it includes the rescaling and data augmentation preprocessing layers.

There are two other model files in the **saved_models** directory. The one that is called **best_augmented_model.h5** is the best augmented model that was obtained since the beginning of the training. The other one that is called **best_model.h5** is the same model as **best_augmented_model.h5**, but it does not include the preprocessing layers and cannot be used to resume a training. An error will be thrown if you attempt to do so.

</details></ul>
<ul><details open><summary><a href="#5-3">5.3  Transfer learning</a></summary><a id="5-3"></a>

Transfer learning is a popular training methodology that is used to take advantage of models trained on large datasets, such as ImageNet.
The Model Zoo features that are available to implement transfer training are presented in the next sections.
<ul><details open><summary><a href="#5-3-1">5.3.1 Using ImageNet pretrained weights</a></summary><a id="5-3-1"></a>

Weights pretrained on the ImageNet dataset are available for the MobileNet-V1 and MobileNet-V2 models.

If you want to use these pretrained weights, you need to add the `pretrained_weights` attribute to the `model:` subsection of the 'training' section of the configuration file and set it to 'imagenet', as shown in the YAML code below.

```yaml
training:
   model:
      name: mobilenet
      version: v2
      alpha: 0.35
      input_shape: (224, 224, 3)
      pretrained_weights: imagenet
```

By default, no pretrained weights are loaded. If you want to make it explicit that you are not using the ImageNet weights, you may add the `pretrained_weights` attribute and left it unset or set to *null*.
</details></ul>
<ul><details open><summary><a href="#5-3-2">5.3.2 Using weights from another model</a></summary><a id="5-3-2"></a>

When you train a model, you may want to take advantage of the weights from another model that was previously trained on another, larger dataset.

Assume for example that you are training a MobileNet-V2 model on the Flowers dataset and you want to take advantage of the weights of another MobileNet-V2 model that you previously trained on the Plant Leaf Diseases dataset (for illustration purposes, this may not give valuable results).
This can be specified using the `pretrained_model_path` attribute in the `model:` subsection as shown in the YAML code below.

```yaml
training:
   model:
      name: mobilenet
      version: v2
      alpha: 0.35
      output_stride: 16
      input_shape: (224, 224, 3)
      pretrained_model_path: <path-to-a-Keras-model-file>
```

Weights are transfered between backbone layers (all layers but the head). The two models must have the same backbones, obviously. You could not transfer weights between two MobileNet-V2 models that have different 'alpha' parameter values, or from an FD-MobileNet model to a ResNet model.

This weights transfer feature is available for all the models from the Model Zoo. Note that for MobileNet models, the `pretrained_weights` and `pretrained_model_path` are mutually exclusive and an error will be raised if you use both.
</details></ul>

<ul><details open><summary><a href="#5-3-3">5.3.3 Freezing layersl</a></summary><a id="5-3-3"></a>

By default, all the layers are trainable. If you want to freeze some layers, then you need to add the optional `frozen_layers` attribute to the `training:` section of your configuration file. The indices of the layers to freeze are specified using the Python syntax for indexing into lists and arrays. Below are some examples.


```yaml
training:
   frozen_layers: (0:-1)    # Freeze all the layers but the last one
   
training:
   frozen_layers: (10:120)   # Freeze layers with indices from 10 to 119

training:
   frozen_layers: (150:)     # Freeze layers from index 150 to the last layer

training:
   frozen_layers: (8, 110:121, -1)  # Freeze layers with index 8, 110 to 120, and the last layer
```

Note that if you want to make it explicit that all the layers are trainable, you may add the `frozen_layers` attribute and left it unset or set to *None*.
</details></ul>

<ul><details open><summary><a href="#5-3-4">5.3.4 Multi-step training</a></summary><a id="5-3-4"></a>

In some cases, better results may be obtained using multiple training steps.

The first training step is generally done with only a few trainable layers, typically the head only. Then, more and more layers are made trainable in the subsequent training steps. Some other parameters may also be adjusted from one step to another, in particular the learning rate. Therefore, a different configuration file is needed at each step.

The `model_path` attribute of the `general:` section and the `trained_model_path` attribute of the `training:` section are available to implement such a multi-step training. At a given step, `model_path` is used to load the model that was trained at the previous step and `trained_model_path` is used to save the model at the end of the step.

Assume for example that you are doing a 3 steps training. Then, your 3 configurations would look as shown below.

**Training step #1 configuration file (initial training):**

```yaml
training:
   model:
      name: mobilenet
      version: v2
      alpha: 0.35
      input_shape: (128, 128, 3)
      pretrained_weights: imagenet
   frozen_layers: (0:-1)
   trained_model_path: ${MODELS_DIR}/step_1.h5
```

**Training step #2 configuration file:**

```yaml
general:
   model_path: ${MODELS_DIR}/step_1.h5

training:
   frozen_layers: (50:)
   trained_model_path: ${MODELS_DIR}/step_2.h5
```

**Training step #3 configuration file:**

```yaml
general:
   model_path: ${MODELS_DIR}/step_2.h5

training:
   frozen_layers: None
   trained_model_path: ${MODELS_DIR}/step_3.h5

```
</details></ul>
</details></ul>

<ul><details open><summary><a href="#5-4">5.4  Creating your own custom model</a></summary><a id="5-4"></a>

You can create your own custom model and get it handled as any built-in Model Zoo model. If you want to do that, you need to modify a number of Python source code files that are all located under the *\<MODEL-ZOO-ROOT>\/semantic_segmentation/src* directory root.

An example of custom model is given in the **models/custom_model.py** located in the *\<MODEL-ZOO-ROOT\>/semantic_segmentation/src/models/*. The model is constructed in the body of the *get_custom_model()* function that returns the model. Modify this function to implement your own model.

In the provided example, the *get_custom_model()* function takes in arguments:
- `num_classes`, the number of classes.
- `input_shape`, the input shape of the model.
- `dropout`, the dropout rate if a dropout layer must be included in the model.

As you modify the *get_custom_model()* function, you can add your own arguments. Assume for example that you want to have an argument `alpha` that is a float. Then, just add it to the interface of the function.

Then, your custom model can be used as any other Model Zoo model using the configuration file as shown in the YAML code below:
```yaml
training:
   model:
      name: custom
      alpha: 0.5       # The argument you added to get_custom_model().
      input_shape: (128, 128, 3)
   dropout: 0.2
```
</details></ul>

<ul><details open><summary><a href="#5-5">5.5  Train, quantize, benchmark and evaluate your model</a></summary><a id="5-5"></a>

In case you want to train and quantize a model, you can either launch the training operation mode followed by the quantization operation on the trained model (please refer to quantization **[README.md](../quantization/README.md)** that describes in details the quantization part) or you can use chained services like launching [chain_tqe](../config_file_examples/chain_tqe_config.yaml) example with command below:
```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_tqe_config.yaml
```
This specific example trains a mobilenet v2 model with imagenet pre-trained weights, fine tunes it by retraining latest seven layers but the fifth one (this only as an example), aand quantizes it 8-bits using quantization_split (30% in this example) of the train dataset for calibration before evaluating the quantized model.

In case you also want to execute a benchmark on top of training and quantize services, it is recommended to launch the chain service called [chain_tbqeb](../config_file_examples/chain_tbqeb_config.yaml) that stands for train, benchmark, quantize, evaluate, benchmark like the example with command below:
```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_tbqeb_config.yaml
```

</details></ul>
</details>

<details open><summary><a href="#A"><b>Appendix A: Learning rate schedulers</b></a></summary><a id="A"></a>

A number of callbacks are available that implement different learning rate decay functions. The *ReduceLROnPlateau* and *LearningRateScheduler* schedulers are Keras callbacks, the others are provided with the Model Zoo. They all update the learning rate at the beginning of each epoch.

To use one of these learning rate schedulers, simply add it to the list of callbacks in the `training:` section of your configuration file. 


<ul><details open><summary><a href="#A-1">A.1 Keras ReduceLROnPlateau scheduler</a></summary><a id="A-1"></a>

An example of usage of the Keras ReduceLROnPlateau learning rate scheduler is shown below.

```yaml
training:
   optimizer:
      Adam:
         learning_rate: 0.001
   callbacks:
      ReduceLROnPlateau:
         monitor: val_accuracy
         factor: 0.5
         patience: 20
         min_lr: 1e-7
         verbose: 0   # Verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

Refer to the Tensorflow documentation for more detail about the *ReduceLROnPlateau* callback.
</details></ul>

<ul><details open><summary><a href="#A-2">A.2 Keras LearningRateScheduler scheduler</a></summary><a id="A-2"></a>

An example of usage of the Tensorflow *LearningRateScheduler* scheduler is shown below.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LearningRateScheduler:   # The schedule is provided using a lambda function.
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

If you only want to implement a number of constant learning rate steps, there is no need to use the *LearningRateScheduler* callback. 
You can use the Model Zoo *LRPiecewiseConstantDecay* callback that is available for that purpose and is simpler to use.

Refer to the Tensorflow documentation for more detail about the *LearningRateScheduler* callback.
</details></ul>

<ul><details open><summary><a href="#A-3">A.3 LRLinearDecay scheduler</a></summary><a id="A-3"></a>

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

</details></ul>

<ul><details open><summary><a href="#A-4">A.4 LRExponentialDecay scheduler</a></summary><a id="A-4"></a>

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
</details></ul>

<ul><details open><summary><a href="#A-5">A.5 LRStepDecay scheduler</a></summary><a id="A-5"></a>

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
</details></ul>

<ul><details open><summary><a href="#A-6">A.6 LRCosineDecay scheduler</a></summary><a id="A-6"></a>

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

If `hold_steps` + `decay_steps` is equal to the total number of epochs, the cosine decay ends at the last epoch of the training with the learning rate reaching `end_lr`. There is no on-target constant learning rate phase in this case.

</details></ul>

<ul><details open><summary><a href="#A-7">A.7 LRWarmupCosineDecay scheduler</a></summary><a id="A-7"></a>

This callback applies a 4 phases decay function to the learning rate:
1. Warmup phase: the learning rate increases linearly from an initial value over a number of epochs until it reaches its maximum value.
2. Hold phase: the learning rate is held constant at its maximum value for a number of epochs.
3. Cosine decay phase: the learning rate decays over a number of epochs following a cosine function until it reaches its target value.
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
- If `warmup_steps` is set to 0, there is no warmup phase and the learning rate starts at `max_lr` (the `initial_lr` argument does not apply in this case and should not be used).
- If `hold_steps` is set to 0, there is no hold phase and the learning rate immediately starts decaying after reaching `max_lr`.
- If `warmup_steps` + `hold_steps` + `decay_steps` is equal to the total number of epochs, the cosine decay ends at the last epoch of the training with the learning rate reaching `end_lr`. There is no on-target constant learning rate phase in this case.
- If `warmup_steps` and `hold_steps` are both equal to 0, the callback implements the same cosine decay function as the LRCosineDecay callback.
</details></ul>

<ul><details open><summary><a href="#A-8">A.8 LRCosineDecayRestarts scheduler</a></summary><a id="A-8"></a>

This callback applies a cosine decay function with restarts to the learning rate.

At the beginning of the training, the learning rate decays from an initial value following a cosine function. After a number of epochs, the first restart occurs, i.e. the learning rate restarts from an initial value. Then, it decays following a cosine function until the second restart occurs, etc. A restart followed by a cosine decay is referred to as a "period". Periods get longer and longer and the initial learning rate of each period gets smaller and smaller as the training progresses.

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

The `t_mul` argument is used to derive the number of epochs of each period. The number of epochs of the i-th period is equal to "`t_mul`**(i - 1) * `first_decay_steps`". For example, if `first_decay_steps` is equal to 50 and `t_mul` is equal to 2, the numbers of epochs of the periods are 50, 100, 200, 450, etc.

The `m_mul` argument is used to derive the initial learning rate of the i-th period. If LR(i - 1) is the initial learning rate of period i-1, the initial learning rate of period i is equal to "LR(i-1) * `m_mul`". For example, if `initial_lr` is equal to 0.01 and `m_mul` is equal to 0.7, the initial learning rates of the restarts are 0.007, 0.0049, 0.0512, 0.00343, etc. if `m_mul` is equal to 1.0, the initial learning rate is the same for all the restarts.

</details></ul>

<ul><details open><summary><a href="#A-9">A.9 LRPolynomialDecay scheduler</a></summary><a id="A-9"></a>

This callback applies a polynomial decay function to the learning rate, given a provided initial learning rate. See the `schedule` method of the callback.

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
</details></ul>

<ul><details open><summary><a href="#A-10">A.10 LRPolynomialDecayRestarts scheduler</a></summary><a id="A-10"></a>

This callback applies a polynomial decay function to the learning rate, given a provided initial learning rate. See the `schedule` method of the callback. If the `power` argument is set to 1.0, the learning rate decreases linearly.

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
</details></ul>

<ul><details open><summary><a href="#A-11">A.11 LRPiecewiseConstantDecay scheduler</a></summary><a id="A-11"></a>

The PiecewiseConstantDecay scheduler applies a piecewise constant decay function (a number of constant value steps) to the learning rate. See the `schedule` method of the callback.

```yaml
training:
   epochs: 200
   optimizer: Adam
   callbacks:
      LRPiecewiseConstantDecay:
         boundaries: [30, 70, 150]              # The list of epochs when the learning rate starts a new constant step.
         values: [0.01, 0.005, 0.001, 0.0001]   # The number of epochs to hold the learning rate constant between two drops.
         verbose: 0                             # verbosity (0 or 1). If set to 1, the learning rate value is printed at the beginning of each epoch.
```

The `boundaries` argument is a list of integers with strictly increasing values that provide the epoch numbers  when the learning rate starts a new constant step.
The `values` argument is a list of floats that specifies the value of the learning rate for each interval defined by the `boundaries` argument. It should have one more element than `boundaries`, the last element being the learning rate value for any remaining epoch after the last epoch specified in `boundaries` (the last element).

In the example above, the learning rate is 0.01 for the first 30 epochs, 0.005 for the next 40 epochs, 0.001 for the next 80 epochs, and 0.0001 for any
subsequent epoch.
</details></ul>
</details>



