# Human activity recognition STM32 model evaluate

This tutorial shows how to quantize and evaluate your pre-trained keras models using *STM32Cube.AI*.

## Table of contents

* <a href='#benchmark'>Benchmark your model using *STM32Cube.AI* </a><br>
* <a href='#Evaluate'>Evaluate the performance of your model</a><br>


## Benchmark your model using *STM32Cube.AI*
<a id='benchmark'></a>

### **1. Configure the yaml file**
**1.1. General settings:**

Configure the **general** section in **[user_config.yaml](user_config.yaml)** as the following:

```python
general:
  project_name: HAR
```
where:

- `project_name` - *String*, name of the project.

**1.2. Load your model:**

Here you can define the model path to load and benchmark the model, also other parameters that will be useful for quantizing and evaluating the model if wanted.

To do so we will need to configure the **model** section in **[user_config.yaml](user_config.yaml)** as the following:

```python
model:
  model_type: {name : ign}
  input_shape: [24,3,1]
  model_path: ../../models/ign/ST_pretrainedmodel_public_dataset/WISDM/ign_wl_24/ign_wl_24.h5
```

where:

- `model_type` - A *dictonary* with keys relative to the model topology (see [more](../training/doc/models.json)). Example for ign *{name : ign}*, for gmp *{name : gmp}*, for svc *{name : svc}* else for a custom model use *{name : custom}*.
- `input_shape` -  A *list of int* *[H, W, C]* for the input resolution, e.g. *[24, 3, 1]*.
- `model_path` - *Path* to your model, the model can be in `.h5`, `.onnx` or `.tflite` format.

**1.4. Model quantization:**

Quantization optimizes your model to be deployed more efficiently on your embedded device by reducing its memory usage(Flash/RAM) and accelerating its inference time, with little-to-no degradation in model accuracy.

In this step you don't need to provide a dataset, your model will be quantized with fake data to be able to evaluate the optimized model footprints.

If your model is already quantized into TensorFlow `.tflite` format, or if you do not want to quantize the model, please skip this step by setting the `quantize: False`.

Configure the **quantization** section in **[user_config.yaml](user_config.yaml)** as the following:  

```python
quantization:
  quantize: True
  evaluate: True
  quantizer: TFlite_converter
  quantization_type: PTQ
  quantization_input_type: float
  quantization_output_type: float
  export_dir: quantized_models
```

where:

- `quantize` - *Boolean*, set to True to quantize your model.
- `evaluate` - *Boolean*, if True evaluate quantized model if validation or test sets are provided, else False.
- `quantizer` - *String*, only option is "TFlite_converter" which will convert model trained weights from float to integer values. The quantized model will be saved in TensorFlow Lite format.
- `quantization_type` - *String*, only option is "PTQ",i.e. "Post-Training Quantization". 
- `quantization_input_type` - *String*, can be "int8", "uint8" or "float", represents the quantization type for the model input.
- `quantization_output_type` - *String*, can be "int8", "uint8" or "float", represents the quantization type for the model output.
- `export_dir` - *String*, referres to directory name to save the quantized model.



**1.5. Benchmark your model with STM32Cube.AI:**

STM32Cube.AI will allow you to benchmark your model and estimate its footprints for STM32 target devices.

Make Sure to add the path to the stm32ai excutable under **path_to_stm32ai**, else you can use the **Developer Cloud Services** but you will need to provide your credentials to connect to the service.

```python
stm32ai:
  version: 8.1.0
  path_to_stm32ai: C:/stmicroelectronics2022/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/8.1.0/Utilities/windows/stm32ai.exe
  optimization: balanced
  footprints_on_target: B-U585I-IOT02A
```

where:
- `version` - Specify the **STM32Cube.AI** version used to benchmark the model, e.g. **8.1.0**.
- `optimization` - *String*, define the optimization used to generate the C model, available options are: "*balanced*", "*time*", "*ram*".
- `footprints_on_target` - Specify board name to evaluate the model inference time on real stm32 target, e.g. **'B-U585I-IOT02A'** (see [more](../training/doc/boards.json)), else keep **False**.
- `path_to_stm32ai` - *Path* to stm32ai executable file.

### **2. Run benchmark**

Then, run the following command:


```bash
python evaluate.py
```

## Evaluate the performance of your model
<a id='Evaluate'></a>

### **1. Configure the yaml file**

**1.1. Getting the model and quantization parameters:**


First, you need to follow the previous steps in the [benchmark](#benchmark) section to configure your **[user_config.yaml](user_config.yaml)**.

As mentioned before, you can skip most of the quantization parameters if your model is already quantized using Tflite Converter, however make sure to set `evaluate` to True.

**1.2. Preparing the dataset:**

If you are providing a float model, we suggest using `Post-Training Quantization` to optimize the model footprints. To do so, you need to provide the data used during training. The provided scripts will build the test and training datasets both to evaluate the trained model.

**1.2.1. Loading the dataset:**

Configure the **dataset** section in **[user_config.yaml](user_config.yaml)** as the following:

```python
dataset:
  name: wisdm
  class_names: [Jogging,Stationary,Stairs,Walking]
  training_path: C:/stmicroelectronics2022/external_model_zoo/WISDM_ar_v1.1/WISDM_ar_v1.1_raw.txt
```

where:

- `name` - Dataset name.
- `class_names` - A list containing the classes name.
- `training_path` - The directory where the training set is located, or the dataset path.

**1.2.2. Apply preprocessing:**

Apply preprocessing by modifiying the **preprocessing** parameters in **[user_config.yaml](user_config.yaml)** as the following:

```python
pre_processing:
  segment_len: 24
  segment_step: 24
  preprocessing: True
```

- `segment_len` - *Integer*, length of the segments while creating the segments of the time series. Each segment will be used as a single input to the AI model.
- `segment_step` - *Integer*, the setp between the starting sample of the contiguous segments, $0 <$ `segment_step` $\leq$` segment_len`.
- `preprocessing` - *Boolean*, if *True* gravity rotation and supression is applied on each segment.

### **2. Run evaluation**

Then, run the following command:

```bash
python evaluate.py
```

### **3. Visualize results**

**3.1. Saved results**

All evaluation artificats are saved under the current output simulation directory **"outputs/{run_time}"**.

For example, you can retrieve the confusion matrix generated after evaluating the float/quantized model on the validation/test set as follows:

![plot](./doc/img/float_model_confusion_matrix.JPG)

![plot](./doc/img/quantized_model_confusion_matrix.JPG)

**3.2. Run MLFlow**

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following command:

```bash
mlflow ui
```
And open the given IP adress in your browser.