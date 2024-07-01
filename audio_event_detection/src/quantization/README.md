# Audio event detection STM32 model quantization

Quantization is a good way to optimize your models before deploying.
Quantizing your models can drastically reduce their memory footprint (both for RAM and Flash), and speed up their inference time. However, this usually comes at the cost of a small performance drop.
Currently, the model zoo only supports Post-training quantization (PTQ) using int8 weights.

This tutorial will guide you through quantizing a Keras floating point model using the model zoo using post-training quantization. 
The model zoo can also quantize floating point ONNX models. For more details, please refer to please refer to section 3.11 of the [main README](../README.md)

We strongly recommend you follow the [training tutorial](../training/README.md) first. We will continue using the ESC-10 dataset for this tutorial.

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. YAML file configuration</b></a></summary><a id="1"></a>
<ul><details open><summary><a href="#1-1">1.1 Using an available configuration file</a></summary><a id="1-1"></a>

The [pretrained_models](../../pretrained_models/) directory contains several subfolders, one for each model architecture.
Some of these models need quite different pre-processing, feature extraction and training parameters, and using different ones could lead to wildly varying performance.

**Each of these subdirectories contains the config.yaml file that was used to train the model**.
To use these in quantization, copy them over to the [src/](../) folder, and rename them to `user_config.yaml`

If using one of these configuration files, you will need to change the `operation_mode` parameter to `quantization`. See the next section for more information

**If you want to reproduce the listed performance, we recommend you use these available .yaml files**

**Performance may be quite different if you use different parameters**

</details></ul>
<ul><details open><summary><a href="#1-2">1.2 Operation mode</a></summary><a id="1-2"></a>

The `operation_mode` attribute of the configuration file lets you choose which service of the model zoo you want to use (training, evaluation, quantization, deployment, or benchmarking). You can even chain these services together ! Refer to section 3.2 of the [main README](../README.md)

For this tutorial, you just need to set `operation_mode` to `"quantization"`, like so : 

```yaml
operation_mode: quantization
```

</details></ul>
<ul><details open><summary><a href="#1-3">1.3 General settings</a></summary><a id="1-3"></a>

The first section of the configuration file is the `general` section that provides information about your project.

You will need to provide the path to the Keras `.h5` model you wish to quantize in the `model_path` attribute, like in this example :  

```yaml
general:
   project_name: myproject           # Project name. Optional, defaults to "<unnamed>".
   logs_dir: logs                    # Name of the directory where log files are saved. Optional, defaults to "logs".
   saved_models_dir: saved_models    # Name of the directory where model files are saved. Optional, defaults to "saved_models".
   model_path:  <path_to_model_to_quantize.h5>         # Path to a model file. # Leave blank if you want to train from scratch, or perform transfer learning with a backbone provided in the model zoo.
   global_seed: 120                  # Seed used to seed random generators (an integer). Optional, defaults to 120.
   deterministic_ops: False          # Enable/disable deterministic operations (a boolean). Optional, defaults to False.
   display_figures: True             # Enable/disable the display of figures (training learning curves and confusion matrices).
                                     # Optional, defaults to True.
   gpu_memory_limit: 5              # Maximum amount of GPU memory in GBytes that TensorFlow may use (an integer).
```

The `logs_dir` attribute is the name of the directory where the MLFlow and TensorBoard files are saved. The `saved_models_dir` attribute is the name of the directory where models are saved, which includes the quantized model. These two directories are located under the top level <hydra> directory.

For more details on the structure of the output directory, please consult section 1.2 of the [main README](../README.md)

</details></ul>
<ul><details open><summary><a href="#1-4">1.4 Dataset specification</a></summary><a id="1-4"></a>

Information about the dataset you want use is provided in the `dataset` section of the configuration file, as shown in the YAML code below.

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

In this example, no explicit quantization set is provided. However, the `quantization_split` attribute is set to 0.1, which means that 10% of the training set will be used as the representative dataset for quantization. If you wish to provide a separate quantization dataset, simply use the `quantization_csv_path` and `quantization_split` attributes.

For quantization, the validation and test datasets do not matter.

For more details on this section, please consult section 3.5 and section 6 of the [main README](../README.md)

</details></ul>
<ul><details open><summary><a href="#1-5">1.5 Audio temporal domain preprocessing</a></summary><a id="1-5"></a>

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
<ul><details open><summary><a href="#1-6">1.6 Audio feature extraction (frequency domain preprocessing)</a></summary><a id="1-6"></a>

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
<ul><details open><summary><a href="#1-7">1.7 Quantization parameters</a></summary><a id="1-7"></a>

You will need to include a quantization section in your configuration file, as shown in the example below.
Note that the `quantization_input_type` and `quantization_output_type` attributes only concern the dtype of the input and output tensors respectively. The weight tensors are always quantized to int8.
Note that for audio models, we currently only support deploying models which take fp32 input, and have uint8 output.

```yaml
quantization:
   quantizer: TFlite_converter
   quantization_type: PTQ # Only "PTQ" is currently supported
   quantization_input_type: float
   quantization_output_type: uint8
   export_dir: quantized_models       # Optional, defaults to "quantized_models".
```

For more details on what each parameter does, please refer to section 3.11 of the [main README](../README.md)

</details></ul>
</details>
<details open><summary><a href="#2"><b>2. Run quantization</b></a></summary><a id="2"></a>

Once you have finished setting up your config file, run the following command from the [src/](../) directory : 

```bash
python stm32ai_main.py 
```

</details>
<details open><summary><a href="#3"><b>3. Results</b></a></summary><a id="3"></a>

All quantization artifacts, figures, and models are saved under the output directory specified in the config file, like so : 

```yaml
hydra:
  run:
    dir: ./experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```
By default, the output directory is `src/experiments_outputs/<date_time_of_your_run>/`(../experiments_outputs). Note that this directory will NOT exist before you run the model zoo at least once.

This directory contains the following file, among others : 
- The quantized_models contains a quantized_model.tflite file, which is your quantized model !

For more details on the list of outputs, and the structure of the output directory, please consult section 1.2 of the [main README](../README.md)

</details>
<details open><summary><a href="#4"><b>4. Run MLFlow</b></a></summary><a id="4"></a>

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following command:

```bash
mlflow ui
```
And open the given IP adress in your browser.

</details>
