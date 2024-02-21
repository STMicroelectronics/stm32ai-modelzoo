
# Audio event detection STM32 model zoo
## Table of Contents

### <a href="#1">1. Model Zoo Overview</a>

#### <a href="#1-1">1.1 YAML configuration file</a>

#### <a href="#1-2">1.2 Output directory structure</a>

#### <a href="#1-3">1.3 MLflow</a>

### <a href="#2">2. Supported dataset format</a>

### <a href="#3">3. Configuration file</a>

#### <a href="#3-1">3.1 YAML syntax extensions</a>

#### <a href="#3-2">3.2 Operation mode</a>

#### <a href="#3-3">3.3 Top-level sections</a>

#### <a href="#3-4">3.4 Global settings and model path</a>

#### <a href="#3-5">3.5 Datasets</a>

#### <a href="#3-6"> 3.6 Dataset-specific parameters </a>

#### <a href="#3-7">3.7 Audio temporal domain preprocessing</a>

#### <a href="#3-8">3.8 Audio feature extraction (frequency domain preprocessing)</a>

#### <a href="#3-9">3.9 Data augmentation</a>

#### <a href="#3-10">3.10 Training</a>

#### <a href="#3-11">3.11 Quantization</a>

#### <a href="#3-12">3.12 Model accuracy evaluation</a>

#### <a href="#3-13">3.13 Image class prediction</a>

#### <a href="#3-14">3.14 STM32 tools</a>

#### <a href="#3-15">3.15 Benchmarking</a>

#### <a href="#3-16">3.16 Deployment</a>

### <a href="#4">4. Training from a model file</a>

#### <a href="#4-1">4.1 Training your own model</a>

#### <a href="#4-2">4.2 Resuming a training</a>

### <a href="#5">5. Transfer learning</a>

### <a href="#6">6. Handling out-of-distribution data </a>

### <a href="#7">7. Creating your own model</a>

### <a href="#8">8. Training a model on FSD50K </a>

### <a href="#appendix-a">Appendix-A: Models available with the Model Zoo</a>

#### <a href="#a-1">A.1 Yamnet-256</a>

#### <a href="#a-2">A.2 MiniResNet</a>

#### <a href="#a-3">A.3 MiniResNetv2</a>

### <a href="#appendix-b">Appendix B: Learning rate schedulers</a>

__________________________________________

### <a id="1">1. Model Zoo Overview</a>

#### <a id="1-1">1.1 YAML configuration file</a>

The model zoo is piloted solely from the [user_config.yaml](user_config.yaml) located in the [src/](./) directory (where this README is located.)

This README explains the structure and syntax used in this file, what each parameter does, and how to edit the config file to use all of the functionalities offered by the model zoo.

Furthermore, under the [pretrained_models/](../pretrained_models/) folder, you will find several pretrained models, and next to each model you will find the configuration file that was used to obtain each of them. If you're unsure where to start from, or feel a bit overwhelmed, these can be a great starting point.

#### <a id="1-2">1.2 Output directory structure</a>

When you run the Model Zoo, the files that get created are located in the src/experiments_outputs/ by default. This behaviour can be changed. Note that this folder will not be present until you have run the model zoo at least once.

This directory contains the following files : 
- The .hydra folder contains Hydra logs
- The logs folder contains Tensorboard logs, as well as a train_metrics.csv file containing the training metrics for each epoch.
- The saved_models directory contains the output float models (if there are any)
  - best_augmented_model.h5 is the float model that obtained the best validation accuracy, with the data augmentation layers still attached.
  - last_augmented_model.h5 is the float model obtained in the last epoch, with the data augmentation layers still attached
  - best_model.h5 is the float model that obtained the best accuracy without any of the data augmentation layers. It is ready to quantize.
- The quantized_models directory contains the output quantized model (if there is one)
  - quantized_model.tflite is the quantized version of best_model.
- stm32ai_main.log is a text log of the events that happened during this run of the model zoo. 
- Several confusion matrices, as well as plots of the loss & validation accuracy curves during training are included.

#### <a id="1-3">1.3 MLflow</a>

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and for visualizing results.
The model zoo lets you use MLflow ot easily visualize the results and metrics obtained in multiple trainings.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following command:
```bash
mlflow ui
```
And open the given IP adress in your browser.

Mlflow logs for each model zoo run are stored by default under src/experiments_outputs/mlruns/
Note that this folder will not be present until you have run the model zoo at least once.

### <a id="#2">2. Supported dataset format</a>
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


The model zoo also supports specific dataset that are not provided in ESC format, such as FSD50K. For such datasets, scripts converting these datasets to the ESC format used by the model zoo are provided, so you don't need to do any of the work yourself.


### <a id="3">3. Configuration file</a>

#### <a id="3-1">3.1 YAML syntax extensions</a>

A description of the YAML language can be found at https://www.cloudbees.com/blog/yaml-tutorial-everything-you-need-get-started (many other sources are available on the Internet). We only cover here the extensions that have been made in the Model Zoo. 

We use "attribute-value" instead of "key-value" as in the YAML terminology, the term "attribute" begin more relevant to our application. We may use the term "attribute" or "section" for nested attribute-value pairs constructs as the one shown below. In the example YAML code below, we may indifferently refer to "training" as an attribute or as a section.

```yaml
training:
   model:
      name: yamnet
      embedding_size: 256
      input_shape: (64, 96, 1)
      pretrained_weights: True
```

The YAML code below shows the syntax extensions that have been made available with the Model Zoo.

```yaml
# Equivalent syntaxes for attributes with no value
attribute_1:
attribute_2: null
attribute_2: None

# Equivalent syntaxes for boolean values
attribute_1: true
attribute_2: false
attribute_3: True
attribute_4: False

# Syntax for environment variables
model_path: ${PROJECT_ROOT}/models/mymodel.h5
```

Attributes with no values can be useful to list in the configuration file all the attributes that are available in a given section and explicitly show which ones were not used.

Environment variables can be used to avoid hardcoding in the configuration file the paths to directories and files. If directories or files are moved around, you only need to change the value of the environment variables and your configuration file will keep working with no edits.

#### <a id="3-2">3.2 Operation mode</a>

The `operation_mode` top-level attribute specifies the operations you want to executed. This may be single operation or a set of chained operations.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for benchmark and 'd' for deployment.

| `operation_mode` attribute | Operations |
|:---------------------------|:-----------|
| 'training'     | Train a model |
| 'evaluation'   | Evaluate the accuracy of a float or quantized model |
| 'quantization' | Quantize a float model |
| 'prediction'   | Predict the classes some images belong to using a float or quantized model |
| 'benchmarking' | Benchmark a float or quantized model on an STM32 board |
| 'deployment'   | Deploy a model on an STM32 board |
| 'chain_tbqeb'  | Sequentially: training, benchmarking of trained model, quantization of trained model, evaluation of quantized model, benchmarking of quantized model |
| 'chain_tqe'    | Sequentially: training, quantization of trained model, evaluation of quantized model |
| 'chain_eqe'    | Sequentially: evaluation of a float model,  quantization, evaluation of the quantized model |
| 'chain_qb'     | Sequentially: quantization of a float model, benchmarking of quantized model |
| 'chain_eqeb'   | Sequentially: evaluation of a float model,  quantization, evaluation of quantized model, benchmarking of quantized model |
| 'chain_qd'     | Sequentially: quantization of a float model, deployment of quantized model |

#### <a id="3-3">3.3 Top-level sections</a>

The top-level sections of a configuration file are listed in the table below. They will be described in detail in the following sections.

| Attribute name | Mandatory | Usage |
|:---------|:------|:-----|
| `general` | yes | Describes the project (project name, directory where to save models, etc) |
| `dataset` | yes | Describes the dataset (dataset name, paths to data, etc) |
| `dataset_specific` | no | Parameters specific to certain datasets supported by the model zoo(currently, only FSD50K) |
| `preprocessing` | yes | Parameters used to perform time-domain processing on the audio data |
| `feature_extraction` | yes | Parameters used to perform frequency-domain processing of the audio-data, e.g. spectrogram computation.
| `data_augmentation` | no | Data augmentation applied to input spectrograms during training |
| `training` | yes | Training setup, including batch size, n° of epochs, callbacks, learning rate scheduler, etc. |
| `quantization` | no | Parameters for quantization of floating point models. |
| `prediction` | no | Path to a directory of audio files to make class predictions with |
| `deployment` | no | Parameters for the deployment of a model on an STM32 board |
| `mlflow` | yes | Parameters related to mlflow |
| `hydra` | yes | Path to the directory where model zoo outputs will be stored |

#### <a id="3-4">3.4 Global settings and model path</a>

The `general` section and its attributes are shown below.

```yaml
general:
   project_name: myproject           # Project name. Optional, defaults to "<unnamed>".
   logs_dir: logs                    # Name of the directory where log files are saved. Optional, defaults to "logs".
   saved_models_dir: saved_models    # Name of the directory where model files are saved. Optional, defaults to "saved_models".
   model_path: <file-path>           # Path to a model file.
   global_seed: 120                  # Seed used to seed random generators (an integer). Optional, defaults to 120.
   deterministic_ops: False          # Enable/disable deterministic operations (a boolean). Optional, defaults to False.
   display_figures: True             # Enable/disable the display of figures (training learning curves and confusion matrices).
                                     # Optional, defaults to True.
   gpu_memory_limit: 5              # Maximum amount of GPU memory in GBytes that TensorFlow may use (an integer).
```

The `model_path` attribute is used to provide the path to the model file you want to use to run the operation mode you selected.

Depending on the operation mode, the model file may be:
- a Keras model file (float model) with a '.h5' filename extension
- a TFlite model file (quantized model) with a '.tflite' filename extension
- an ONNX model file (quantized model) with a '.onnx' filename extension.

The table below summarizes the usage of the `model_path` attribute.

|  Operation modes | Model file type | 
|:-----------------|:----------------|
| evaluation     | Keras or TF-Lite |
| quantization, chain_eqe, chain_eqeb, chain_qb, chain_qd  | Keras |
| prediction     | Keras or TF-Lite |
| benchmarking   | Keras, TF-Lite or ONNX |
| deployment     | TF-Lite |

If you are running one of the operation modes that include a training, you can use the `model_path` attribute to train your own model rather than a model from the Model Zoo. This will be described in the "Training from a model file" section of the configuration.

The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy and Tensorflow random generators at the beginning of the main script. This is an optional attribute, the default value being 120. If you don't want random generators to be seeded, then set `global_seed` to 'None' (not recommended as this would make training results less reproducible).

Even when random generators are seeded, it is often difficult to exactly reproduce results when the same operation is run multiple times. This typically happens when the same training script is run on different hardware. The `deterministic_ops` operator can be used to enable the deterministic mode of Tensorflow. If enabled, an operation that uses the same inputs on the same hardware will have the exact same outputs every time it is run. However, determinism should be used carefully as it comes at the expense of longer run times. Refer to the Tensorflow documentation for more detail.

The `gpu_memory_limit` attribute sets an upper limit in GBytes on the amount of GPU memory Tensorflow may use. This is an optional attribute with no default value. If it is not present, memory usage is unlimited. If you have several GPUs, be aware that the limit is only set on logical gpu[0].


#### <a id="3-5">3.5 Datasets</a>

The `dataset` section and its attributes are shown in the YAML code below.
Detailed explanations of each parameter are provided at the end of this section.

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

When running the 'prediction', 'deployment' and 'chain_qd' operation modes, you will need to provide the names of the classes using the `class_names` attribute. For all the other modes, they can be inferred from the provided dataset (in which case they will all be used), but it is still recommended to provide them yourself. If you only want to use a subset of classes in your dataset, you have to provide the name of these classes in the `class_names` attribute.

When a training is run, the training set is split in two to create a validation dataset if it is not provided. When a model accuracy evaluation is run, the test set is used if there is one, otherwise the validation set is used (either provided or generated by splitting the training set).

The `validation_split` attribute specifies the training/validation set size ratio to use when splitting the training set to create a validation set. The default value is 0.2, meaning that 20% of the training set is used to create the validation set. The `seed` attribute specifies the seed value to use for randomly shuffling the dataset file before splitting it (default value is 120).

The use of quantization datasets is covered in the "Quantization" section of the documentation.

- `name` : *string*, name of the dataset. Must be one of "esc10", "fsd50k" or "custom". Use "custom" if using a dataset that isn't ESC-10 or FSD50K. If "fsd50K", must provide additional arguments in the `dataset_specific` section. See the next section of this readme for details.
- `class_names` : *list of strings*, Names of the classes to use when training your model, each class separated by a comma. Must have at least 2 classes. This can be a subset of available classes.
- `file_extension` : *string*, Extension of the audio files. Will be automatically appended to the end of the filenames contained in the .csv file if necessary when fetching the audio files.
- `training_audio_path` : *string*, Path to the folder containing the audio clips for the training set. See section <a href="#2">2. Supported dataset format</a> for details on the expected dataset format.
- `training_csv_path` : *string*, Path to the .csv file containing filenames and labels for the training set. See section <a href="#2">2. Supported dataset format</a> for details on the expected dataset format.
- `validation_audio_path` : *string*, Path to the folder containing the audio clips for the validation set. Leave empty to use a subset of the training set as a validation set.
- `validation_csv_path` : *string*, Path to the .csv file containing filenames and labels for the validation set. Leave empty to use a subset of the training set as a validation set.
- `validation_split` : *float*, fraction of the training set to use as validation set if the previous two parameters were left empty.
- `quantization_audio_path` : *string*, Path to the folder containing the audio clips for the quantization set. Leave empty to use a subset of the training set as a quantization set.
- `quantization_csv_path` : *string*, Path to the .csv file containing filenames and labels for the quantization set. Leave empty to use a subset of the training set as a quantization set.
- `quantization_split` : *float*, fraction of the training set to use as quantization set if the previous two parameters were left empty.
- `test_audio_path` : *string*, Path to the folder containing the audio clips for the test set. Leave empty to only perform evaluation on the validation set.
- `test_csv_path` : *string*, Path to the .csv file containing filenames and labels for the test set. Leave empty to only perform evaluation on the validation set.
- `multi_label` : *boolean*, Set to True if your dataset is a multi-label dataset, i.e. if each sample can belong to more than one class. WARNING : Currently unimplemented, leave on False.
- `use_garbage_class` : **(Experimental)** *boolean*, If set to True, any samples not belonging to classes specified in `class_names` get lumped together in a new "Other" class, and the model is trained on the classes specified in `class_names` plus this new class. 
**WARNING** : this will yield extremely poor results unless your dataset has a lot of classes, and you are using a small proportion of them in `class_names`. **If in doubt, set to False.**
Mutually exclusive with `deployment.unknown_class_threshold`. For more details, see section <a href="#6"> 6 Handling out-of-distribution data </a>
- `n_samples_per_garbage_class` : **(Experimental)** *int*, number of samples of each unused class to lump into the "Other" class. Generally, when lumping all samples from all unused classes into the "Other" class, the resulting dataset is extremely unbalanced. If this parameter is not provided, the scripts will try to infer a number that results in a dataset that isn't too poorly balanced. For more details, see section <a href="#6"> 6 Handling out-of-distribution data </a>
- `expand_last_dim` : *bool*, set to True to output patches of the shape (n_mels, n_frames, 1) instead of (n_mels, n_frames). Some models, such as Yamnet or the Miniresnets expect this input shape.

#### <a id="3-6">3.6 Dataset-specific parameters </a>

The model zoo provides support for some publicly available datasets. However, such datasets are rarely, if ever provided in the format expected by the model zoo. We have included a helpful collection of scripts to format these datasets for you. These scripts usually need a few parameters (such as the paths to various parts of the dataset), which are provided in this section of the configuration file. The parameters in this section are only used by the model zoo if the `name` argument in the dataset section is set to a specific string. (Currently, only "fsd50k").

Currently, only ESC-10 (which does not require any dataset-specific parameters) and FSD50K are supported by the model zoo. Thus, this section only covers parameters specific to FSD50K.

For more details on how to train a model using FSD50K, please consult section <a href="#7">7. Training a model on FSD50K </a>


```yaml
dataset_specific:
  # Contains dataset-specific parameters.
  # Currently only supports fsd50k.
  # These parameters only need to be filled out IF the dataset name is set to 'fsd50K'
  fsd50k:
    csv_folder: ../datasets/FSD50K/FSD50K.ground_truth
    dev_audio_folder: ../datasets/FSD50K/FSD50K.dev_audio
    eval_audio_folder: ../datasets/FSD50K/FSD50K.eval_audio
    audioset_ontology_path: preprocessing/dataset_utils/fsd50k/audioset_ontology.json
    only_keep_monolabel: True
```

- `csv_folder` : *string*, Folder where the dev and eval csv files are located. The default name for this folder in the archives downloaded from Zenodo is `FSD50K.ground_truth`
- `dev_audio_folder` : *string*, Folder where the dev audio files are located. The default name for this folder in the archives downloaded from Zenodo is `FSD50K.dev_audio`
- `eval_audio_folder` : *string*, Folder where the eval audio files are located. The default name for this folder in the archives downloaded from Zenodo is `FSD50K.eval_audio`
- `audioset_ontology_path` : *string*, Path to the audioset ontology JSON file. The file is provided in the model zoo [here](./preprocessing/dataset_utils/fsd50k/audioset_ontology.json), but you can also download it from https://github.com/audioset/ontology/blob/master/ontology.json
- `only_keep_monolabel` : *boolean*, If set to True, discard all multi-label samples. This is a comparatively small proportion of all samples. 

#### <a id="3-7">3.7 Audio temporal domain preprocessing</a>

When performing AED, it is customary to perform some preprocessing directly on the input waveform in the temporal domain before doing any feature extraction in the frequency domain, such as converting the waveform into a spectrogram.

In our case, we keep it simple, by resampling the input waveform to a target sample rate, clipping it between a minimum and maximum duration, removing silence, and repeating the waveform if it is shorter than the specified minimum duration.

The 'preprocessing' section and its attributes is shown below.

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

- `min_length` : *int*, Desired minimum length of the waveform, in seconds
- `max_length` : *int*, Desired maximum length of the waveform, in seconds
- `target_rate` : *int*, Desired sampling rate. Resulting waveform will be resampled to this rate before any further processing.
- `top_db` : *int*, Decibel full-scale threshold for silence removal. Higher means stricter. For example, using `top_db=30` will remove more audio than using `top_db=60`, because in the second case, the average power of the signal in a frame must be below -60dBfs for it to be removed, instead of -30dBfs.
- `frame_length` : *int*, Length of frames used for silence removal, in number of samples.
- `hop_length` : *int*, Hop length used for silence removal, in number of samples.
- `trim_last_second` : *boolean*,  If True, will cut the waveform to an integer number of seconds. For example, if the resulting waveform would be 4s and 500 ms, this flag will instead cut it to 4s.
- `lengthen` : *boolean*, Valid values :  "before" or "after". If set to "before", audio repetition will be performed before silence removal. If set to "after", audio repetition will be performed after. 
WARNING : setting this option to "before" may result in the resulting waveform being shorter than `min_length`, which can cause all manner of bugs (for example, not being able to extract at least one patch from a clip.) Set to "after" if you are unsure.


#### <a id="3-8">3.8 Audio feature extraction (frequency domain preprocessing)</a>

In a typical AED pipeline, once the temporal domain preprocessing has been performed on the input waveform, it is usually converted to a frequency-domain representation, such as a mel-spectrogram, or array of MFCC coefficients, and the model is trained on this representation.

In the model zoo, we convert the input waveform to a log-mel spectrogram. This spectrogram is then cut into several patches of fixed size, and each patch is fed as input to the model. When running the model on the board, patches are computed on the fly, and passed as input to the model in realtime.

Different models expect spectrograms computed with different parameters. You can reference the several `config.yaml` files provided with the pretrained models in the zoo [../pretrained_models](../pretrained_models/) to find out which parameters were used for each model.

The 'feature_extraction' section and its attributes is shown below.

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
- `patch_length` : *int*, Number of frames to include in each patch. Patches will be of shape (`n_mels`, `patch_length`)
- `n_mels` : *int*, Number of mel filter bins. Patches will be of shape `n_mels` x `patch_length`
- `overlap` : *float*, Real number between 0 and 1. Proportion of overlap between patches. Note that the total overlap with all other patches will be double this value. For example, if `overlap` is set to 0.25, with `patch_length=40` then patch N will share its first 10 frames will patch N-1, and its last 10 frames with patch N+1, for a total of 20 frames shared with other patches, i.e. half its frames.
- `n_fft` : *int*, Size of the FFT, in number of samples
- `hop_length` : *int*, Hop length (i.e. number of successive samples) between different frames, in number of samples.
- `window_length` : *int*, Size of the signal window. Set equal to `n_fft` if you want to avoid window padding
- `window` : *string*, Window type. Only Hanning windows ("hann") are currently supported for deployment on STM32 boards.
- `center` : *boolean*, If True, frames are centered, i.e. frame `n` is centered around sample number `n * hop_length`. If False, frames begin at sample number `n * hop_length`
- `pad_mode` : *int*, Padding mode used if center is True. If center is False, does nothing.
- `power` : *float*, Exponent for the magnitude spectrogram. Set to 1.0 for energy spectrogram, and 2.0 for power spectrogram. Other values are invalid.
- `fmin` : *int*, Minimum frequency used when computing mel filter bins
- `fmax` : *int*, Maximum frequency used when computing mel filter bins
- `norm` : *string*, Mel filter weights normalization. Set to "slaney" or "None" if you are unsure. **Some models, like Yamnet, expect no normalization (i.e. this parameter set to "None")**
- `htk` : *boolean*, If true, use the [HTK](https://htk.eng.cam.ac.uk/) formula to compute mel filter weights. Set to "False" if you are unsure. **Some models, like Yamnet, expect this to be True**.
- `to_db` : *boolean*, If set to True, logmelspectrograms are expressed in dBfs units.  Set to "True" if you are unsure. **Some models, like Yamnet expect this to be False**.
- `include_last_patch` : *boolean*, If set to False, discards the last patch if it does not contain `patch_length` frames. If true, this patch is returned.
WARNING : Setting this option to True will cause errors when using models with a fixed input size !
Leave to "False" if unsure.



#### <a id="#3-9">3.9 Data augmentation</a>
Data augmentation has proved an effective technique to reduce the overfit of a network and make it generalize better. It is generally useful when the dataset is small.

If you want your model's performance to transfer well to real world, real-time inference, it is important to apply data augmentation during training, in order to make your model robust to various perturbations. 
This may degrade the performance displayed when evaluating the model on its validation or test set, however the model's performance when running on the board is very often improved.

The data augmentation provided in the model zoo is applied directly on the input patches (as opposed to on the waveform), because it would be too expensive to recompute the patches each epoch.

The data augmentation currently available in the model zoo is rudimentary, but more will be coming in future updates.

The data augmentation layers applied to input patches training are specified in the optional `data_augmentation` section of the configuration file. They are only applied during training.

An example of data augmentation section is shown below.

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

- `GaussianNoise`: Adds Gaussian noise to spectrogram patches.
Be careful, as the amplitude of values in your spectrograms can change greatly depending on normalization and whether or not decibel scale is used. Make sure to set this parameter in accordance.
  - `enable` : Set to True to enable this data augmentation layer
  - `scale` : Standard deviation (i.e. scale) of the Gaussian noise to add to the spectrogram patches.

- `VolumeAugment`: Randomly scales volume on spectrogram patches. The volume of spectrogram patches is randomly scaled by a float picked for each batch uniformly between min_scale and max_scale. This layer automatically differentiates between decibel and non-decibel scales, so unlike with `GaussianNoise`, you don't need to adapt the scales yourself.
  - `enable` : Set to True to enable this data augmentation layer
  - `min_scale`: *float*, minimum scale for random volume scaling
  - `max_scale`: *float*, maximum scale for random volume scaling
  
- `SpecAug`: SpecAugment (https://arxiv.org/abs/1904.08779). SpecAugment randomly masks contiguous columns or rows in a spectrogram. Implementation by MichaelisTrofficus, taken from https://github.com/MichaelisTrofficus/spec_augment
Warning : This can really degrade your model performance if used improperly. When in doubt, set to False.
  - `enable` : Set to True to enable this data augmentation layer
  - `freq_mask_param`: *int*, number of rows to mask in each contiguous block
  - `time_mask_param`: *int* , number of columns to mask in each contiguous block
  - `n_freq_mask`: *int*, number of contiguous blocks to mask on the frequency axis
  - `n_time_mask`: *int*, number of contiguous blocks to mask on the time axis
  - `mask_value` : *float*, value to replace masked values with. Be sure to set this properly relative to the scale of values in your spectrogram, unless you want to get terrible performance.


#### <a id="3-10">3.10 Training</a>

A 'training' section is required in all the operation modes that include a training, namely 'training', 'tqeb' and 'tqde.

The YAML code below is a typical example of 'training' setup.
A detailed explanation of every parameter is provided at the end of this section 

```yaml
operation_mode: "training"

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
- Additional attributes are needed depending on the type of model. For example, an `embedding_size` attribute is required for a Yamnet model and  `n_stacks` and `version` attributes are required for a Miniresnet model. To know which models require which attributes, please consult <a href="#appendix-a">Appendix-A: Models available with the Model Zoo</a>, or the [models.json](training/doc/models.json) documentation. Additionally, you can reference the configuration files provided with the pretrained models in [../pretrained_models](../pretrained_models/)
- The optional `pretrained_weights` attribute can be used to load pretrained weights in the model before it gets trained, and perform transfer learning.
If set to True, pretrained weights are loaded, and if set to False the model is trained from scratch. If you want to load pretrained weights, and fine-tune the entire model (instead of just performing transfer learning by retraining the last layer), you can set the `fine_tune` parameter to True.
Transfer learning is covered in the "Transfer learning" section of the documentation.

The `batch_size` and `epochs` attributes are mandatory.

The `dropout` attribute is optional. By default, no dropout layer is inserted in the model.

All the Keras optimizers are supported. If you are not passing any argument to the optimizer, you may write it on one line. For example: "optimizer: Adam".

The `callbacks` subsection is optional. All the Keras callbacks are supported. Note that several callbacks are built-in and cannot be redefined, including ModelCheckpoint, TensorBoard and CSVLogger. 

A variety of learning rate schedulers are provided with the Model Zoo. If you want to use one of them, just include it in the `callbacks` subsection. Refer to Appendix C for a description of the available callbacks and learning rate plotting utility.

The best model obtained at the end of the training is saved in the 'experiments_outputs/\<date-and-time\>/saved_models' directory and is called 'best_model.h5' (see section <a href="#1-2">1.3 Output directory structure</a>). Make sure not to use the 'best_augmentation_model.h5' file for deployment or evaluation as it includes the data augmentation layers.


- `model` : Section dedicated to the model
  - `name` : *string*, name of the model
  - `input_shape` : *tuple of ints*, Input shape of the models. Should be (n_mels, n_frames) (for Miniresnets) or (n_mels, n_frames, 1) (for Yamnets)
  - `pretrained_weights` : *boolean*, Set to True to load pretrained backbone weights, freeze them and perform transfer learning.
  - `other attributes` : consult the [models.json](training/doc/models.json) documentation to know which ones are required, and which values are allowed.
- `fine_tune` : *boolean*, if True, and `pretrained_weights` is also True, perform fine-tuning by unfreezing backbone weights. Leave on False if you just want to perform transfer learning.
- `dropout` : *float* , Adds dropout to the last layer of your model if set to a float > 0. Is disabled if set to 0.
- `batch_size` : *int*. Batch size of the various datasets (training, validation, test, quantization) used in the model zoo.
- `epochs` : *int*. Number of epochs to train the model for . You will want to set this to a larger number when training from scratch.
- `optimizer` : A Keras optimizer. Use "Adam" if unsure.
  - `learning_rate` : *float*, initial learning rate.
- `callbacks` : Any Keras callback, including learning rate schedulers.


#### <a id="3-11">3.11 Quantization</a>

If you run one of the operation modes that includes a model quantization, you need to include a 'quantization' section in your configuration file, as shown in the YAML code below. You still need a dataset, preprocessing and feature_extraction section, but they are omitted here for the sake of readability.

```yaml
general:
   model_path: <path-to-a-Keras-model-file>   # Float model to quantize

dataset:
  name: esc10
  class_names: ['dog', 'chainsaw', 'crackling_fire', 'helicopter', 'rain', 'crying_baby', 'clock_tick', 'sneezing', 'rooster', 'sea_waves']
  file_extension: '.wav'
  training_audio_path: ..\datasets\ESC-50\audio # Mandatory
  training_csv_path:   ..\datasets\ESC-50\meta\esc50.csv # Mandatory

  validation_audio_path: # Optional
  validation_csv_path: # Optional
  validation_split: 0.2  # Optional, default value is 0.2

  quantization_audio_path: # Optional
  quantization_csv_path: # Optional
  quantization_split:  # Optional

  test_audio_path: # Optional
  test_csv_path: # Optional

  multi_label: False 
  use_garbage_class: True 
  n_samples_per_garbage_class: 2
  expand_last_dim: True
  seed: 120 # Optional, there is a default seed
  to_cache: True
  shuffle: True
operation_mode: quantization

quantization:
   quantizer: TFlite_converter
   quantization_type: PTQ
   quantization_input_type: float
   quantization_output_type: uint8
   export_dir: quantized_models       # Optional, defaults to "quantized_models".
```

The model file must be Keras model file (float model) with a '.h5' filename extension.

The supported quantizer is 'TFLite_converter' and the supported method is 'PTQ'.

By default, the quantized model is saved in the 'quantized_models' directory under the 'experiments_outputs' directory. You may use the optional `export_dir` attribute to change the name of this directory.

With the configuration file shown above, quantization will be performed using fake data, because you did not provide a quantization dataset, or a quantization split. If you have a dataset at your disposal, it is recommended that you use it as using representative data may improve quantization results. All you need to do is to add a 'dataset' section to your configuration file and provide the path to the audio directory & the csv file associated with the dataset as shown below

```yaml
general:
   model_path: <path-to-a-Keras-model-file>       # Path to the model to quantize

operation_mode: quantization

dataset:
   quantization_csv_path: <dataset-csv-file> # Dataset to use as representative data
   quantization_audio_path: <dataset_audio_folder>    # Dataset to use as representative data
```

If you are running a chain mode, you may take advantage of a dataset required for other purposes than quantization. For example, a training set is available when you run the 'chain_tbeqb' and 'chain_tqe' operation modes. But training sets are large and quantization run times could be very long. To avoid this issue, you can set the `quantization_split` attribute to use only a portion of the dataset.

```yaml
dataset:
   training_csv_path: <dataset-csv-file>
   training_audio_path: <dataset_audio_folder>
   quantization_split: 0.05         # Use 5% of the training set for quantization
```

By default, the value of the `quantization_split` attribute is set to 1.0, meaning that the whole quantization dataset is used if you leave this attribute empty. This is NOT recommended as it will take forever. 


#### <a id="3-12">3.12 Model accuracy evaluation</a>

The YAML code below shows how you can evaluate the accuracy of a model. You still need a dataset, preprocessing and feature_extraction section, but they are omitted here for the sake of readability.

```yaml
general:
   model_path: <path-to-a-Keras-or-TFlite-model-file>       # Path to the model to evaluate

operation_mode: evaluation

dataset:
   test_csv_path: <dataset_csv_file> # CSV file of the dataset to use for evaluation
   test_audio_path: <dataset_audio_folder> # Audio folder of the dataset to use for evaluation
```

The model file can a Keras model file (float model) with a '.h5' extension or a TFlite model with a '.tflite' extension.

If no test dataset is available, the validation dataset is used instead. If there is no validation dataset, then you need to provide a training set that will be split to create one. This can be specified using the `validation_path`, `training_path` and `validation_split` attribute (see the <a id="3-5">3.5 Datasets</a> section of the documentation).


#### <a id="3-13">3.13 Audio file prediction</a>

You can predict the class of some audio files as shown in the YAML code below. You still need a dataset, preprocessing and feature_extraction section, but they are omitted here for the sake of readability.

```yaml
general:
   model_path: <path-to-a-Keras-or-TFlite-model-file>           # Path to the model to use to make predictions
   class_names: ['dog', 'chainsaw', 'crackling_fire', 'helicopter', 'rain', 'crying_baby', 'clock_tick', 'sneezing', 'rooster', 'sea_waves']   # Names of the classes

operation_mode: prediction

prediction:
   test_files_path: ${AUDIO_FILES_DIR}   # Path to a directory containing the audio files to predict
```

The model file can a Keras model file (float model) with a '.h5' extension or a TFlite model with a '.tflite' extension.

The class names have to be provided as there is no dataset to infer them from.


#### <a id="3-14">3.14 STM32 tools</a>

This section covers the usage of the STM32-X-CUBEAI tool, which benchmarks .tflite and .h5 models, and converts them to C code
The `tools` section in the config file looks like this : 

```yaml
tools:
  stm32ai:
    version: 8.1.0
    optimization: balanced
    on_cloud: True
    path_to_stm32ai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/<*.*.*>/Utilities/windows/stm32ai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_1.10.1/STM32CubeIDE/stm32cubeide.exe
```
where : 
- `version` - The **STM32Cube.AI** version used to benchmark the model, e.g. **8.1.0**.
- `optimization` - *String*, define the optimization used to generate the C model, options: "*balanced*", "*time*", "*ram*".
- `on_cloud` : Set to True to use the STM32 developer cloud to benchmark and convert models. You will need to make an account at [https://stm32ai-cs.st.com/home](https://stm32ai-cs.st.com/home) and will be prompted for your credentials at runtime. If you use the developer cloud, you do not need to set the next two parameters.
- `path_to_stm32ai` - *Path* to stm32ai executable file. Is only used if `on_cloud` is set to False
- `path_to_cubeIDE` - *Path* to CubeIDE executable file. Is only used if `on_cloud` is set to False

#### <a id="3-15">3.15 Benchmarking</a>

The YAML code below shows how to benchmark a model on an STM32 board You still need a preprocessing and feature_extraction section, but they are omitted here for the sake of readability.

```yaml
general:
   model_path: <path-to-the-model-file>     # Path to the Keras, TFlite or ONNX model file to benchmark

operation_mode: benchmarking

benchmarking:
   board: B-U585I-IOT02A     # Name of the STM32 board to benchmark the model on
```

The model file can be either:
- a Keras model file (float model) with a '.h5' filename extension
- a TFlite model file (quantized model) with a '.tflite' filename extension
- an ONNX model file (quantized model) with an '.onnx' filename extension.
 
The `board` attribute is used to provide the name of the STM32 board to benchmark the model on. The available boards are 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32F469I-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-H743ZI2', 'STM32H747I-DISCO', 'STM32H735G-DK', 'STM32F769I-DISCO', 'NUCLEO-G474RE', 'NUCLEO-F401RE' and 'STM32F746G-DISCO'.

For AED, the only board available for deployment is the B-U585I-IOT02A, and so we recommend setting `board` to 'B-U585I-IOT02A'


#### <a id="3-16">3.16 Deployment</a>

The YAML code below shows how to deploy a model on an STM32 board.
Note that you need a preprocessing and feature_extraction section, even though no data is being preprocessed. This is because the parameters in these sections are being used to create look-up tables that are used by the C application to preprocess data on the board in realtime.

```yaml
general:
   model_path: <path-to-a-TFlite-model-file>     # Path to the model file to deploy

dataset:
  name: esc10
  class_names: ['dog', 'chainsaw', 'crackling_fire', 'helicopter', 'rain', 'crying_baby', 'clock_tick', 'sneezing', 'rooster', 'sea_waves']
  file_extension: '.wav'

preprocessing:
  min_length: 1
  max_length : 10
  target_rate: 16000
  top_db: 60
  frame_length: 3200
  hop_length: 3200
  trim_last_second: False
  lengthen : 'after'

feature_extraction:
  patch_length: 96
  n_mels: 64
  overlap: 0.25
  n_fft: 512
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

tools:
  stm32ai:
    version: 8.1.0
    optimization: balanced
    on_cloud: True
    path_to_stm32ai:  C:/ST/STM32CubeAI/en.x-cube-ai-windows_v8.1.0/windows/stm32ai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_1.10.1/STM32CubeIDE/stm32cubeide.exe

benchmarking:
  board: B-U585I-IOT02A

deployment:
  c_project_path: ../../stm32ai_application_code/sensing_free_rtos
  IDE: GCC
  verbosity: 1 n
  hardware_setup:
    serie: STM32U5
    board: B-U585I-IOT02A
  unknown_class_threshold: 0.0 # Threshold used for OOD detection. Mutually exclusive with use_garbage_class # Set to 0 to disable. To enable, set to any float between 0 and 1.
```
The model file must be a TFlite model file (quantized model) with a '.tflite' file extension.

The class names have to be provided as there is no dataset to infer them from.

- `c_project_path` : *Path*, Path to the C application. Should be either `../../stm32ai_application_code/sensing_free_rtos` or `../../stm32ai_application_code/sensing_thread_x`. The main difference between the two different versions is in licenses. There is no performance difference between the two.
**IMPORTANT NOTE : The baud rate used in the serial port for the two versions is different. If using `../../stm32ai_application_code/sensing_free_rtos`, the expected baud rate is 115200, and for `../../stm32ai_application_code/sensing_thread_x` it is 921600.**
- `ide` : Toolchain to use for compiling the C application. Should be `GCC`
- `verbosity` : Verbosity of the compiler
- `hardware_setup` : Series and board on which to dpeloy the model. Currently, only the B-U585I-IOT02A board is supported
- `unknown_class_threshold` : *float*, used to perform OOD detection. If > 0, thresholds the model output probabilities, and if the maximum probability is below this threshold, displays "Unknown class" instead of the model prediction.
**WARNING : Mutually exclusive with `dataset.use_garbage_class`**. Consult the section on OOD detection in the model zoo for more details.


### <a id="4">4. Training from a model file</a>

#### <a id="4-1">4.1 Training your own model</a>

You may want to train your own model rather than a model from the Model Zoo.

This can be done using the `model_path` attribute to provide the path to the model file you want to use as shown in the YAML code below. You still need a dataset, preprocessing and feature_extraction section, but they are omitted here for the sake of readability.

```yaml
general:
   model_path: <path-to-a-Keras-model-file>    # Path to the model file to use for training

operation_mode: training

training:
  dropout: 0
  batch_size: 16
  epochs: 2 
  resume_training_from: # Optional, use to resume a training from a previous experiment.
                        # Example: experiments_outputs/2023_10_26_18_36_09/saved_models/last_augmented_model.h5 
  optimizer:
    Adam:
      learning_rate: 0.001
  callbacks:          # Optional section
    ReduceLROnPlateau:
      monitor: val_accuracy
      mode: max
      factor: 0.5
      patience: 100
      min_lr: 1.0e-05
    # LRWarmupCosineDecay:
    #   initial_lr: 0.0001
    #   warmup_steps: 100
    #   max_lr: 0.005
    #   hold_steps: 100
    #   decay_steps: 800
    #   end_lr: 5.0e-05
    EarlyStopping:
      monitor: val_accuracy
      mode: max
      restore_best_weights: true
      patience: 60
```

The model file must be a Keras model file with a '.h5' filename extension.

The 'model' subsection of the 'training' section is not present as we are not training a model from the Model Zoo. An error will be thrown if it is added when `model_path` is set.

Note that:
- if some layers are frozen in the model file, they will be reset to trainable before training.
- If you set the `dropout` attribute but the model does not include a dropout layer, an error will be thrown. Reciprocally, an error will also occur if the model includes a dropout layer but the `dropout` attribute is not set.
- If the model file was saved with the optimizer, its state won't be preserved as the model file is compiled before training.


#### <a id="4-2">4.2. Resuming a training</a>

You may want to resume a training that you interrupted or that crashed.

When training a model, the model is saved at the end of each epoch in the current experiment output directory tree. The model file is in the 'experiments_outputs/<date-and-time\>/saved_models' directory and it is named 'last_augmented_model.h5' (see section "1.3 Output directory structure").

To resume a training, you need to choose the experiment you want to restart from and set the `resume_training_from` attribute in the `training` section to the path to the 'last_augmented_model.h5' model file of this experiment. An example is shown in the YAML code example below. You still need a dataset, preprocessing and feature_extraction section, but they are omitted here for the sake of readability.


```yaml
operation_mode: training

training:
   bach_size: 64
   epochs: 150
   resume_training_from: <path-to-a-Keras-model-path>   # Path to the 'last_augmented_model.h5' file to resume training from
```

When setting the `resume_training_from` attribute, the `model` subsection of the 'training' section and the `model_path` attribute in the 'general' section should not be used. An error will be thrown if you do so.

It is recommended that you restart from the same configuration file that you used for the training you are resuming. If you make changes to the dropout rate, the frozen layers or the optimizer, they will ignored and the settings from the training you are resuming will be kept. Changes made to the batch size, number of epochs and callbacks will be taken into account.

There are two other model files in the same directory as the 'last_augmented_model.h5' file. The one that is called 'best_augmented_model.h5' is the best model that was obtained and can be used to resume a training. The other one that is called 'best_model.h5' is the same model but it cannot be used to resume a training as it does not include the data augmentation layers.


### <a id="5">5. Transfer learning</a>

Transfer learning is a popular training technique used to take advantage of models trained on large datasets.

The Model Zoo offers pretrained backbones for various models, and the ability to perform transfer learning or fine-tuning using these backbones.

To use a pretrained backbone, set the `training.model.pretrained_weights` attribute of your config file to `True`. (see section <a href="3-10">3.10 Training</a>). 
This will load a pretrained backbone, freeze the backbone weights, and add a trainable classification head on top of the backbone. The backbone is treated as a frozen feature extractor.

If instead, you wish to also make the backbone weights trainable, you must also set the `training.fine_tune` argument to True (see section <a href="3-10">3.10 Training</a>) This will unfreeze all the backbone weights that were loaded, making all the weights in your model trainable.

Here's a small table summarizing the available options : 

| `pretrained_weights` | `fine_tune` | Trainable weights |  Method |
|:---------------------|:------------|:------------------|:--------|
| True     | False | Classification head only | Transfer learning |
| True | True | All | Fine-tuning |
| False | False or True | All | Training from scratch



### <a id="6">6. Handling out-of-distribution data </a>

A common issue in audio event detection applications is being able to reject samples which do not come from one of the classes the model is trained on.
The model zoo provides several baseline options for doing this. 

The first option consists of thresholding the network output probabilities at runtime. **This is a naïve baseline which does not yield great results**, but is a good starting point. 

You can set the threshold in the config file, by tuning the `deployment.unknown_class_threshold` parameters (see section <a href="3-16">3.16 Deployment</a>>).
This parameter is a float between 0 and 1.

Setting it to 0 disables the thresholding, while setting it above 0 will display the sample as belonging to the "unknown" class, if the maximum probability output by the network for this sample is lower than the threshold, and will display the class predicted by the network if the probability is above the threshold.


The second option for OOD detection consists of adding an additional "Other" class to your model at training time, using samples from the dataset which do not belong to any of the classes specified in `dataset.class_names`.

**IMPORTANT NOTE** : This feature is **experimental**. It will yield **very poor results** if the dataset provided does not have a very large number of unused classes to lump into the "Other" class. Do not expect great results from this, unless you are using a dataset with a LOT of different classes, and you are using a small subset of them (for example, using 5 classes out of 200 with FSD50K.)

To enable this option, set the `dataset.use_garbage_class` parameter to `True` (see section<a href="3-5">3.5 Datasets</a>).

Additionally, you can use the `dataset.n_samples_per_garbage_class`(see section<a href="3-5">3.5 Datasets</a>) parameter to control how many samples from each unused class are sent to the "Other" class. This can help keeping the resulting dataset balanced.

**IMPORTANT NOTE** These two methods are **NOT COMPATIBLE**, and cannot be used together. You must enable one or the other, or none at all.
This means that if `dataset.use_garbage_class` is set to `True`, then `deployment.unknown_class_threshold` must be set to 0, and that if `deployment.unknown_class_threshold` is set to a float > 0, then `dataset.use_garbage_class` must be set to `False`

### <a id="7">7. Creating your own model</a>

You can create your own custom model and get it handled as any built-in Model Zoo model. If you want to do that, you need to modify a number of Python source code files that are all located under the *<MODEL-ZOO-ROOT>/image_classification/src* directory root.

An example of custom model is given in file *models/custom_model.py*. The model is constructed in the body of the *get_custom_model()* function that returns the model. Modify this function to implement your own model.

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

If you want to use transfer learning with your custom model, you need to modify the value of the argument `last_layer_index` in the call to the function `transfer_pretrained_weights()` in file *utils/models_mgt.py*. This argument needs to be set to the index of the last layer of the model backbone, i.e. the last layer before the classifier begins. Layer indices are numbered from 0 (the input layer has index 0).

After doing this, you will be able to use transfer learning as shown below:

```yaml
training:
   model:
      name: custom
      alpha: 0.5
      input_shape: (128, 128, 3)
      pretrained_model_path: ${MODELS}/pretrained_model.h5
   dropout: 0.2
```

### <a id="8">8. Training a model on FSD50K </a>

**Download the dataset**
Download the dataset here : https://zenodo.org/record/4060432
The dataset is comprised of several archives. We suggest extracting them all in the same folder, for example `../datasets/FSD50K/`.

After extraction you should end up with the following folders : 
- `FSD50K.dev_audio`
- `FSD50K.doc`
- `FSD50K.eval_audio`
- `FSD50K.ground_truth`
- `FSD50K.metadata`

Strictly speaking, `FSD50K.metadata` and `FSD50K.doc` are unnecessary, so they can be deleted.

**Set up the dataset-specific parameters**
First, set `dataset.name` to `fsd50k` in the configuration file. See section<a href="3-5">3.5 Datasets</a> for more details.

You will need to set some dataset-specific parameters in the configuration file.
See <a href="3-6">3.6 Dataset-specific parameters </a> for a detailed description of each parameter.

**NOTE** The regular `training_audio_path`, `training_csv_path`, `validation_audio_path`, `validation_csv_path`, `validation_split` are unused when using FSD50K. Instead, the dev set is used as the training set, and the eval set as the validation set.

**Pre-process the dataset**
In order to make FSD50K compatible with the model zoo's expected dataset format, we make a few changes to the dataset. 
Notably, we **unsmear** labels, and then convert the labels to monolabel.
FSD50K comes with smeared labels. This means that some labels are added automatically. For example, any sample with the Electric_guitar label, will automatically be assigned the Music label. Unsmearing simply undoes this process, e.g. only the Electric_guitar label would remain.

Then, we remove multilabel example. You can choose whether or not this is done by toggling the `dataset_specific.fsd50k.only_keep_monolabel` parameter

Support for multilabel inference is coming, so you will be able to keep smeared labels and multilabel samples in the future.

All this happens automatically if you set `dataset.name` to `fsd50k`.

That's it !

### <a id="appendix-a">Appendix A: Available Model Zoo models</a>

The models that are available with the Model Zoo and their parameters are described below.

The 'model' sections that are shown below must be added to the 'training' section of the configuration file.

When using pretrained backbones with these models, you will want to have specific preprocessing and feature extraction parameters. Please, refer to the configuration files provided in [pretrained_models/](../pretrained_models/) for these parameters.

If you are fine-tuning, or training from scratch, feel free to use whichever preprocessing and feature extraction parameters you desire !

 
#### <a id="a-1">A.1 Yamnet-256</a>

```yaml
model:
   name: yamnet
    embedding_size: 256
    input_shape: (64, 96, 1)
    pretrained_weights: True # Set to True if you want to use pretrained weights provided in the model zoo
                             # Yamnet-256 can only be used with pretrained weights.
```

This is a smaller version of Yamnet (https://www.kaggle.com/models/google/yamnet/) that outputs embeddings of size 256, and has been stripped of its preprocessing layers.
Note that we only allow using Yamnet with Google's pretrained weights (otherwise it'd just be a regular MobileNetv1), hence `pretrained_weights` must be set to True.


#### <a id="a-2">A.2 MiniResNet</a>

```yaml
model:
   name: miniresnet
    n_stacks: 1
    pooling: None
    version: v1
    input_shape: (64, 50)
    pretrained_weights: True # Set to True if you want to use pretrained weights provided in the model zoo
```

These are small ResNets, based upon the Keras implementation (https://keras.io/api/applications/resnet/)

`n_stacks` can be any integer >= 1, but values bigger than 2 are not recommended.
`pooling` can be `None`, `avg` or `max`. Depending on the number of stacks, classes and shape of input patches, it might be interesting to set `pooling: None`, as the number of filters might be too low for average and max pooling to yield good results.
`input_shape` must be given in the format (n_mels, n_frames).
`pretrained_weights` can be either True or False.


#### <a id="a-3">A.3 MiniResNetV2</a>

```yaml
model:
    name: miniresnet
    n_stacks: 1
    pooling: None
    version: v2
    input_shape: (64, 50)
    pretrained_weights: True # Set to True if you want to use pretrained weights provided in the model zoo
```

These are small ResNetv2s, based upon the Keras implementation (https://keras.io/api/applications/resnet/)

`n_stacks` can be any integer >= 1, but values bigger than 2 are not recommended.
`pooling` can be `None`, `avg` or `max`. Depending on the number of stacks, classes and shape of input patches, it might be interesting to set `pooling: None`, as the number of filters might be too low for average and max pooling to yield good results.
`input_shape` must be given in the format (n_mels, n_frames).
`pretrained_weights` can be either True or False.



### <a xid="appendix-b">Appendix B: learning rate schedulers

A number of callbacks are available that implement different learning rate decay functions. The ReduceLROnPlateau and LearningRateScheduler schedulers are Keras  schedulers, the others are provided with the Model Zoo.

To use one of these learning rate schedulers, simply add it to the list of callbacks in the 'training' section of your configuration file. The learning rate is updated at the beginning of each epoch.

This appendix is available in [training/lr_schedulers_README.md](training/lr_schedulers_README.md)
