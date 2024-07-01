# Audio event detection STM32 model training

This tutorial shows how to train from scratch or apply transfer learning on an AED model.
As an example we will demonstrate the workflow on the [ESC-10]("https://github.com/karolpiczak/ESC-50") classification dataset.

`Note:` If you are training a model in order to deploy it with the [STM32 application code](../../../stm32ai_application_code/sensing_free_rtos/README.md), please check out the application specifications [here](../../deployment/README.md).

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Download the dataset and extract it</b></a></summary><a id="1"></a>

ESC-10 is distributed as part of a larger dataset, ESC-50. In this tutorial, we will download the ESC-50 dataset, but only use the ESC-10 subset for training, evaluating or performing transfer learning on the models.

Download the latest dataset release from https://github.com/karolpiczak/ESC-50#download

Then, extract the archive to a folder of your choice. The default location expected by the model zoo is the [../../datasets/](../../datasets/) folder, but this can be configured.

By default, the model zoo expects that datasets are given in ESC format, meaning the same format as the [ESC-50](https://github.com/karolpiczak/ESC-50) dataset.

This means that your dataset must be comprised of 
- A folder containing the audio files. All audio files must share the same format. No mixing .wav and .flac in the same folder, for example.
- A .csv file with at least a "filename" column and a "category" column.
  - The "filename" column must contain the filenames of the audio files (with or without the file extension)
  - The "category" column must contain the label(s) in string format. For multi-label datasets, this column should contain lists of strings.
  
For example, such a .csv file (with a single row here) would look like this : 

| `filename` | `category` |
|:---------------------------|:-----------|
| '1-137-A-32.wav'     | 'dog' |


The model zoo also supports specific dataset that are not provided in ESC format, such as FSD50K. 
These datasets are usually not provided in the ESC format expected by the model zoo.
Fortunately, for such datasets, scripts converting these datasets to the ESC format used by the model zoo are provided, so you don't need to do any of the work yourself.

If you want to use FSD50K, download the latest release from https://zenodo.org/record/4060432
Then, extract the several archives you have downloaded to a folder of your choice. The default location expected by the model zoo is the [../../datasets](../../datasets/) folder, but this can be configured.

For more details on how to use FSD50K in the model zoo, please consult section 8 of the [main README](../README.md)

</details>
<details open><summary><a href="#2"><b>2. Create your configuration file</b></a></summary><a id="2"></a>
<ul><details open><summary><a href="#2-1">2.1 Overview</a></summary><a id="2-1"></a>

The training, evaluation, quantization and benchmarking of the model are driven by a configuration file written in the YAML language. This configuration file is called [user_config.yaml](../user_config.yaml) and is located in the [src/](../) directory.

A configuration file includes the following sections:

- `general`, describes your project, including project name, directory where to save models, etc.
- `operation_mode`, a string describing the operation mode of the model zoo. You'll want to set it to "training" for this tutorial.
- `dataset`, describes the dataset your are using, including directory paths, class names, etc.
- `dataset_specific`, parameters specific to certain datasets supported by the model zoo(currently, only FSD50K)
- `preprocessing`, parameters used to perform time-domain processing on the audio data
- `feature_extraction`, parameters used to perform frequency-domain processing of the audio-data, e.g. spectrogram computation.
- `training`, specifies your training setup, including batch size, number of epochs, optimizer, callbacks, etc.
- `quantization`, specifies the quantization configuration to reduce your model memory usage and inference time.
- `stm32ai`, specifies the STM32Cube.AI configuration to benchmark your model on a board, including memory footprints, inference time, etc.
- `mlflow`, specifies the folder to save MLFlow logs.
- `hydra`, specifies the folder to save Hydra logs.

This tutorial only describes enough settings for you to be able to run an example. Please refer  to the [main README](../README.md) for more information. The model zoo offers many more features than those described in this short tutorial.

#### **TensorFlow deterministic operations**

If you want your experiments to be fully reproducible, you need to activate the `deterministic_ops` attribute.

```yaml
general:
   deterministic_ops: True
```

Enabling the `deterministic_ops` attribute will restrict TensorFlow to use only deterministic operations on the device, but it may lead to a drop in training performance. It should be noted that not all operations in the used version of TensorFlow can be computed deterministically. If your case involves any such operation, a warning message will be displayed and the attribute will be ignored.

</details></ul>
<ul><details open><summary><a href="#2-2">2.2. Using an available configuration file</a></summary><a id="2-2"></a>

The [pretrained_models](../../pretrained_models/) directory contains several subfolders, one for each model architecture.
Some of these models need quite different pre-processing, feature extraction and training parameters, and using different ones could lead to wildly varying performance.

**Each of these subdirectories contains the config.yaml file that was used to train the model**.
To use these in training, copy them over to the [src/](../) folder, and rename them to `user_config.yaml`

If using one of these configuration files, you will need to change the `operation_mode` parameter to `training`. See the next section for more information

**If you want to reproduce the listed performance, we recommend you use these available .yaml files**

**Performance may be quite different if you use different parameters**

</details></ul>
<ul><details open><summary><a href="#2-3">2.3 Operation mode</a></summary><a id="2-3"></a>

The `operation_mode` attribute of the configuration file lets you choose which service of the model zoo you want to use (training, evaluation, quantization, deployment, or benchmarking). You can even chain these services together ! Refer to section 3.2 of the [main README](../README.md)

For this tutorial, you just need to set `operation_mode` to `"training"`, like so : 

```yaml
operation_mode: training
```

</details></ul>
<ul><details open><summary><a href="#2-4">2.4 General settings</a></summary><a id="2-4"></a>

The first section of the configuration file is the `general` section that provides information about your project.

```yaml
general:
   project_name: myproject           # Project name. Optional, defaults to "<unnamed>".
   logs_dir: logs                    # Name of the directory where log files are saved. Optional, defaults to "logs".
   saved_models_dir: saved_models    # Name of the directory where model files are saved. Optional, defaults to "saved_models".
   model_path:           # Path to a model file. # Leave blank if you want to train from scratch, or perform transfer learning with a backbone provided in the model zoo.
   global_seed: 120                  # Seed used to seed random generators (an integer). Optional, defaults to 120.
   deterministic_ops: False          # Enable/disable deterministic operations (a boolean). Optional, defaults to False.
   display_figures: True             # Enable/disable the display of figures (training learning curves and confusion matrices).
                                     # Optional, defaults to True.
   gpu_memory_limit: 5              # Maximum amount of GPU memory in GBytes that TensorFlow may use (an integer).
```

The `logs_dir` attribute is the name of the directory where the MLFlow and TensorBoard files are saved. The `saved_models_dir` attribute is the name of the directory where models are saved, which includes the trained models. These two directories are located under the top level <hydra> directory.

For more details on the structure of the output directory, please consult section 1.2 of the [main README](../README.md)

</details></ul>
<ul><details open><summary><a href="#2-5">2.5 Dataset specification</a></summary><a id="2-5"></a>

Information about the dataset you want to use is provided in the `dataset` section of the configuration file, as shown in the YAML code below.

```yaml
dataset:
  name: esc10 # Name of the dataset. Use 'esc10' for ESC-10, 'fsd50k' for FSD50K and 'custom' for any other dataset
  class_names: ['dog', 'chainsaw', 'crackling_fire', 'helicopter', 'rain', 'crying_baby', 'clock_tick', 'sneezing', 'rooster', 'sea_waves'] # Names of the classes to use when training your model
  file_extension: '.wav' # File extension of the audio files
  training_audio_path: ..\datasets\ESC-50\audio # Mandatory
  training_csv_path:   ..\datasets\ESC-50\meta\esc50.csv # Mandatory

  validation_audio_path: # Optional
  validation_csv_path: # Optional
  validation_split: 0.2  # Optional, default value is 0.2

  quantization_audio_path: # Optional
  quantization_csv_path: # Optional
  quantization_split: 0.1 # Optional

  test_audio_path: # Optional
  test_csv_path: # Optional

  multi_label: False # Set to True if dataset is multi-label
  use_garbage_class: False # See the "Handling out of distribution data" section
  n_samples_per_garbage_class: 2 # See the "Handling out of distribution data" section
  expand_last_dim: True # Set to True to make patches of shape (n_mels, n_frames, 1) instead of (n_mels, n_frames)
  seed: 120 # Optional, there is a default seed
  to_cache: True # Cache the resulting Tensorflow datasets
  shuffle: True # Shuffle the resulting Tensorflow datasets. Won't shuffle validation & test sets.
```

ESC-10 is comprised of a .csv file containing filenames and labels, and a folder containing all the audio files. You must provide a path to the .csv file and the audio directory in the configuration file, like in the example above.

In this example, no validation set path is provided, so the available data under the *training_audio_path* directory is split in two to create a training set and a validation set. By default, 80% of the data is used for the training set and the remaining 20% is used for the validation set. 

No test set path is provided in this example to evaluate the model accuracy after training Therefore, the validation set is used as the test set.

For more details on this section, please consult section 3.5 and section 6 of the [main README](../README.md)

</details></ul>
<ul><details open><summary><a href="#2-6">2.6 Loading a model</a></summary><a id="2-6"></a>

Information about the model you want to train is provided in the `model` section of the configuration file.

The YAML code below shows how you can use a Yamnet-256 model from the Model Zoo.

```yaml
training:
  model: # Use it if you want to use a model from the zoo, mutually exclusive with 'general.model_path'
    name: yamnet # Name of the model
    embedding_size: 256
    input_shape: (64, 96, 1)
    pretrained_weights: True # Set to True if you want to use pretrained weights provided in the model zoo
                             # Yamnet-256 can only be used with pretrained weights.
```

The `pretrained_weights` attribute is set to "True", which indicates that you want to load a pretrained backbone and perform transfer learning. Note that in our case, Yamnet-256 can only be used with pretrained weights, but this is not the case for other models.

For more information on the different modes of transfer learning (transfer learning, fine-tuning, training from scratch...), please consult section 5 of the [main README](../README.md).

For more information on the different models available of the model zoo, please consult appendix A of the [main README](../README.md)

You may want to use your own model instead of a model from the Model Zoo. This can be done by simply leaving the `training.model` section empty, and instead passing a path to a `.h5` Keras model file in `general.model_path`, like so : 
```yaml
general:
   project_name: myproject           # Project name. Optional, defaults to "<unnamed>".
   logs_dir: logs                    # Name of the directory where log files are saved. Optional, defaults to "logs".
   saved_models_dir: saved_models    # Name of the directory where model files are saved. Optional, defaults to "saved_models".
   model_path:  <path_to_your_model.h5>         # Path to a model file. # Leave blank if you want to train from scratch, or perform transfer learning with a backbone provided in the model zoo.
   global_seed: 120                  # Seed used to seed random generators (an integer). Optional, defaults to 120.
   deterministic_ops: False          # Enable/disable deterministic operations (a boolean). Optional, defaults to False.
   display_figures: True             # Enable/disable the display of figures (training learning curves and confusion matrices).
                                     # Optional, defaults to True.
   gpu_memory_limit: 5              # Maximum amount of GPU memory in GBytes that TensorFlow may use (an integer).

training:
   model: # Use it if you want to use a model from the zoo, mutually exclusive with 'general.model_path'
   ```

</details></ul>
<ul><details open><summary><a href="#2-7">2.7 Audio temporal domain preprocessing</a></summary><a id="2-7"></a>

When performing AED, it is customary to perform some preprocessing directly on the input waveform in the temporal domain before doing any feature extraction in the frequency domain, such as converting the waveform into a spectrogram.

In our case, we keep it simple, by resampling the input waveform to a target sample rate, clipping it between a minimum and maximum duration, removing silence, and repeating the waveform if it is shorter than the specified minimum duration.

The 'preprocessing' section handles this part of the pipeline, and an example is show below.

```yaml
preprocessing:
  min_length: 1
  max_length : 10
  target_rate: 16000 # Must be either 16000 or 48000 if deploying on a STM32 board
  top_db: 60
  frame_length: 3200
  hop_length: 3200
  trim_last_second: False
  lengthen : 'after'
```

For more details on what each parameter does, please refer to section 3.7 of the [main README](../README.md)

Different models are trained using different set of preprocessing parameters, and using different ones may lead to poor performance. Please refer to section <a href="#2.2"> 2.2 </a> of this README for instructions on how to retrieve the configuration files used to train the different pretrained models provided in the zoo.

</details></ul>
<ul><details open><summary><a href="#2-8">2.8 Audio feature extraction (frequency domain preprocessing)</a></summary><a id="2-8"></a>

In a typical AED pipeline, once the temporal domain preprocessing has been performed on the input waveform, it is usually converted to a frequency-domain representation, such as a mel-spectrogram, or array of MFCC coefficients, and the model is trained on this representation.

In the model zoo, we convert the input waveform to a log-mel spectrogram. This spectrogram is then cut into several patches of fixed size, and each patch is fed as input to the model. When running the model on the board, patches are computed on the fly, and passed as input to the model in realtime.

The 'feature_extraction' section handles this part of the pipeline, and an example is show below.

```yaml
feature_extraction:
  patch_length: 96
  n_mels: 64
  overlap: 0.25
  n_fft: 512 # Must be a power of 2 if deploying on a STM32 board
  hop_length: 160
  window_length: 400
  window: hann
  center: False
  pad_mode: constant
  power: 1.0
  fmin: 125
  fmax: 7500
  norm: None
  htk : True
  to_db : False
  include_last_patch: False
```
For more details on what each parameter does, please refer to section 3.8 of the [main README](../README.md)
Different models are trained using different set of feature extraction parameters, and using different ones may lead to poor performance. Please refer to section <a href="#2.2"> 2.2 </a> of this README for instructions on how to retrieve the configuration files used to train the different pretrained models provided in the zoo.

</details></ul>
<ul><details open><summary><a href="#2-9">2.9 Data augmentation</a></summary><a id="2-9"></a>

Data augmentation has proved an effective technique to reduce the overfit of a network and make it generalize better. It is generally useful when the dataset is small.

If you want your model's performance to transfer well to real world, real-time inference, it is important to apply data augmentation during training, in order to make your model robust to various perturbations. 
This may degrade the performance displayed when evaluating the model on its validation or test set, however the model's performance when running on the board is very often improved.

The data augmentation provided in the model zoo is applied directly on the input patches (as opposed to on the waveform), because it would be too expensive to recompute the patches each epoch.

The data augmentation currently available in the model zoo is rudimentary, but more will be coming in future updates.

The data augmentation layers applied to input patches training are specified in the optional `data_augmentation` section of the configuration file. They are only applied during training.

An example of a data augmentation section is shown below.

```yaml
data_augmentation:
  GaussianNoise: 
    enable: True
    scale : 0.1
  VolumeAugment:
    enable: True
    min_scale: 0.8
    max_scale: 1.2
  SpecAug: 
    enable : False
    freq_mask_param: 1
    time_mask_param: 1
    n_freq_mask: 3
    n_time_mask: 4
    mask_value : 0
```

For more details on what each parameter does, please refer to section 3.9 of the [main README](../README.md)

It is worth noting that the scale of Gaussian noise applied should depend on the range of values in your log melspectrogram. This is especially dependent on whether you are using spectrogram in dBfs scale or not, and the type of normalization used.

Using SpecAug can sometimes lead to drastic drops in performance. If unsure, we recommend leaving it disabled.

</details></ul>
<ul><details open><summary><a href="#2-10">2.10 Training setup</a></summary><a id="2-10"></a>
 
The training setup is described in the `training` section of the configuration file, as illustrated in the example below.

```yaml
training:
  model: # Use it if you want to use a model from the zoo, mutually exclusive with 'general.model_path'
    name: yamnet # Name of the model
    embedding_size: 256
    input_shape: (64, 96, 1)
    pretrained_weights: True # Set to True if you want to use pretrained weights provided in the model zoo
                             # Yamnet-256 can only be used with pretrained weights.
  fine_tune: False # Set to True if you want to fine-tune a pretrained model from the zoo
  dropout: 0 # Set to a float >0 to add dropout to the last layer of the model
  batch_size: 16
  epochs: 50 # Number of epochs to run 
  resume_training_from: # Optional, use to resume a training from a previous experiment.
                        # Example: experiments_outputs/2023_10_26_18_36_09/saved_models/last_augmented_model.h5 
  optimizer:
    Adam:  # Use the ADAM optimizer with learning rate 0.001
      learning_rate: 0.001
  callbacks:          # Use the ReduceLROnPlateau Keras callback
    ReduceLROnPlateau:
      monitor: val_accuracy
      mode: max
      factor: 0.5
      patience: 100
      min_lr: 1.0e-05
    EarlyStopping:
      monitor: val_accuracy
      mode: max
      restore_best_weights: true
      patience: 60
#  trained_model_path: trained.h5   # Optional, use it if you want to save the best model at the end of the training to a path of your choice
```

The `model` subsection is used to specify a model that is available with the Model Zoo:
- The `name` and `input_shape` attributes must always be present.
- Additional attributes are needed depending on the type of model. For example, an `embedding_size` attribute is required for a Yamnet model and  `n_stacks` and `version` attributes are required for a Miniresnet model. To know which models require which attributes, please consult Appending A of the [main README](../README.md), or the [models.json](doc/models.json) documentation. Additionally, you can reference the configuration files provided with the pretrained models in [../pretrained_models](../../pretrained_models/)
- The optional `pretrained_weights` attribute can be used to load pretrained weights in the model before it gets trained, and perform transfer learning.
If set to True, pretrained weights are loaded, and if set to False the model is trained from scratch. If you want to load pretrained weights, and fine-tune the entire model (instead of just performing transfer learning by retraining the last layer), you can set the `fine_tune` parameter to True.
Transfer learning is covered in section 5 of the [main README](../README.md)

The `batch_size` and `epochs` attributes are mandatory.

The `dropout` attribute is optional. By default, no dropout layer is inserted in the model.

All the Keras optimizers are supported. If you are not passing any argument to the optimizer, you may write it on one line. For example: "optimizer: Adam".

The `callbacks` subsection is optional. All the Keras callbacks are supported. Note that several callbacks are built-in and cannot be redefined, including ModelCheckpoint, TensorBoard and CSVLogger. 

A variety of learning rate schedulers are provided with the Model Zoo. If you want to use one of them, just include it in the `callbacks` subsection. Refer to [the learning rate schedulers README](../../../common/training/lr_schedulers_README.md) for a description of the available callbacks and learning rate plotting utility.

The best model obtained at the end of the training is saved in the 'experiments_outputs/\<date-and-time\>/saved_models' directory and is called 'best_model.h5' (see section 1.3 of the [main README](../README.md)). Make sure not to use the 'best_augmentation_model.h5' file for deployment or evaluation as it includes the data augmentation layers.
For more details on what each parameter does, please refer to section 3.9 of the [main README](../README.md)

</details></ul>
</details>
<details open><summary><a href="#3"><b>3. Train your model</b></a></summary><a id="3"></a>

Run the following command, from the [src/](../) directory:

```bash
python stm32ai_main.py
```

</details>
<details open><summary><a href="#4"><b>4. Model evaluation</b></a></summary><a id="4"></a>

After training is completed, your model will be evaluated on the validation set.
Additionally, if you have provided a test set (see section <a href="2.5"> 2.5 - Dataset specification </a>), the model will also be evaluated on the provided test set.

Two kinds of accuracies will be reported : patch-level accuracy, and clip-level accuracy.
As we explained in section <a href="2.8"> 2.8 Audio feature extraction (frequency domain preprocessing) </a>, each audio clip is converted to a spectrogram and split into patches before being passed to the model.

Once the model has made predictions on each patch, we have a predicted label vector per patch, and so we can compute the accuracy patch-per-patch : this is patch-level accuracy.
We can also aggregate the predictions based on which audio clip each patch belonged to, giving us a single predicted label vector for each audio clip. These are used to compute clip-level accuracy.

Because clip-level accuracy aggregates several predictions, is it typically higher than patch-level accuracy.

</details>
<details open><summary><a href="#5"><b>5. Visualize training results</b></a></summary><a id="5"></a>

All training artifacts, figures, and models are saved under the output directory specified in the config file, like so : 

```yaml
hydra:
  run:
    dir: ./experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```
By default, the output directory is `src/experiments_outputs/<date_time_of_your_run>/`(../experiments_outputs). Note that this directory will NOT exist before you run the model zoo at least once.

This directory contains the following files : 
- The .hydra folder contains Hydra logs
- The logs folder contains Tensorboard logs, as well as a train_metrics.csv file containing the training metrics for each epoch.
- The saved_models directory contains the output float models (if there are any)
  - best_augmented_model.h5 is the float model that obtained the best validation accuracy, with the data augmentation layers still attached.
  - last_augmented_model.h5 is the float model obtained in the last epoch, with the data augmentation layers still attached
  - best_model.h5 is the float model that obtained the best accuracy without any of the data augmentation layers. It is ready to quantize.
- stm32ai_main.log is a text log of the events that happened during this run of the model zoo. 
- Several confusion matrices, as well as plots of the loss & validation accuracy curves during training are included.

For more details on the list of outputs, and the structure of the output directory, please consult section 1.2 of the [main README](../README.md)

</details>
<details open><summary><a href="#6"><b>6. Run tensorboard</b></a></summary><a id="6"></a>

To visualize the training curves logged by tensorboard, go to the output directory (by default, `src/experiments_outputs/<date_time_of_your_run>/`) and run the following command:

```bash
tensorboard --logdir logs
```

And open the URL `http://localhost:6006` in your browser.

</details>
<details open><summary><a href="#7"><b>7. Run MLFlow</b></a></summary><a id="7"></a>

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following command:
```bash
mlflow ui
```
And open the given IP adress in your browser.

</details>
