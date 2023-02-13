# Object detection STM32 model evaluation

This tutorial shows how to quantize and evaluate your pre-trained object detection model using *STM32Cube.AI*.

## Table of contents

* <a href='#benchmark'>Benchmark your model using *STM32Cube.AI* </a><br>
* <a href='#Evaluate'>Evaluate the performance of your model</a><br>


## Benchmark your model using *STM32Cube.AI*
<a id='benchmark'></a>

### **1. Configure the yaml file**
**1.1. General settings:**

Configure the **general** section in **[user_config.yaml](user_config.yaml)** as the following:


![plot](./doc/general_config.JPG)

where:

- `project_name` - *String*, name of the project.

**1.2. Load your model:**

Here you need to specify your model path and provide some other details about the model.

To do so we will need to configure the **model** section in **[user_config.yaml](user_config.yaml)** as the following:

![plot](./doc/model_config.JPG)

where:

- `model_type` - A *dictionary* with keys relative to the model topology. Currently only *{name : mobilenet, version : v1, alpha : 0.25 or 0.5}*, is supported.
- `input_shape` -  A *list of int* *[H, W, C]* for the input resolution, currently only *[256, 256, 3]*, *[224, 224, 3]*, *[192, 192, 3]* are supported.
- `model_path` - *Path* to your model, the model can be in `.h5`, `SavedModel` or `.tflite` format.

**1.4. Model quantization:**

Quantization optimizes your model to be deployed more efficiently on your embedded device by reducing its memory usage(Flash/RAM) and accelerating its inference time, with little degradation in model accuracy.

In this step you don't need to provide a dataset, your model will be quantized with fake data to be able to evaluate the optimized model footprints.

If your model is already quantized into TensorFlow `.tflite` format, please skip this step.

Configure the **quantization** section in **[user_config.yaml](user_config.yaml)** as the following:  

![plot](./doc/quantization.JPG)

where:

- `quantize` - *Boolean*, if True model will be quantized, else False.
- `evaluate` - *Boolean*, if True the quantized model will be evaluated and a test set or a validation set should be provided, else False.
- `quantizer` - *String*, only option is "TFlite_converter" which will convert model trained weights from float to integer values. The quantized model will be saved in TensorFlow Lite format.
- `quantization_type` - *String*, only option is "PTQ",i.e. "Post-Training Quantization". 
- `quantization_input_type` - *String*, can be "int8", "uint8" or "float", represents the quantization type for the model input.
- `quantization_output_type` - *String*, can be "int8", "uint8" or "float", represents the quantization type for the model output.
- `export_dir` - *String*, referres to directory name to save the quantized model.



**1.5. Benchmark your model with STM32Cube.AI:**

STM32CubeAI will allow you to benchmark your model and estimate its footprints for STM32 target devices.

Make Sure to add the path to the stm32ai excutable under **path_to_stm32ai**, else you will need to provide your credentials to use the **Developer Cloud Services**:

![plot](./doc/cubeai_config.JPG)

where:
- `optimization` - *String*, defines the optimization used to generate the C model, options: "*balanced*", "*time*", "*ram*".
- `footprints_on_target` - Specifies a board name to evaluate the model inference time on real stm32 target using the **Developer Cloud Services**, e.g. **'STM32H747I-DISCO'** (see [more](./doc/boards.json)), else keep **False** (i.e. only local download on **STM32Cube.AI** will be used to evaluate footprints w/o inference time).
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

If you are providing a float model, we suggest using `Post-Training Quantization` to optimize the model footprints. To do so, you need to provide the data used during training. Also, you need to make sure to provide the path for a `validation set` or a `test set` to be able to evaluate the accuracy of your model.

**1.2.1. Loading the dataset:**

Configure the **dataset** section in **[user_config.yaml](user_config.yaml)** as the following:

![plot](./doc/dataset_config.JPG)

where:

- `name` - Dataset name.
- `class_names` - A list containing the classes name *in order*.
- `training_path` - The directory where the training set is located. 
- `validation_path` - The directory where the validation set is located.
- `test_path` - Path to the test_set, if not provided the validation set will be used for evaluation.

**1.2.2. Apply preprocessing:**

Apply preprocessing by modifiying the **pre_processing** parameters in **[user_config.yaml](user_config.yaml)** as the following:

![plot](./doc/data_prepro.JPG)

- `rescaling` - A *dictonary* with keys *(scale, offset)* to rescale input values to a new range. To scale input image **[0:255]** in the range **[-1:1]** you should pass **{scale = 127.5, offset = -1}**, else in the range **[0:1]** you should pass **{scale = 255, offset = 0}**.
- `resizing` - *String*, the interpolation method used when resizing images, *only bilinear is supported for the moment*.
- `aspect_ratio` - *Boolean*, if *True* resize the images without aspect ratio distortion, else aspect ratio may not be preserved.*only False is supported for the moment*.
- `color_mode` - One of "*grayscale*", "*rgb*" or "*bgr*", "*rgba*". Whether the images will be converted to have 1, 3, or 4 channels.*only rgb is supported for the moment*.

**1.2.3. Apply post-processing:**

Apply post-processing by modifiying the **post_processing** parameters in **[user_config.yaml](user_config.yaml)** as the following:

![plot](./doc/model_postpro.JPG)

- `confidence_thresh` - A *float* between 0.0 and 1.0, the score thresh to filter detections .
- `NMS_thresh` - A *float* between 0.0 and 1.0, NMS thresh to filter and reduce overlapped boxes.
- `IoU_eval_thresh` - A *float* between 0.0 and 1.0, IOU thresh to calculate TP and FP.


### **2. Run evaluation**

Then, run the following command:

```bash
python evaluate.py
```

### **3. Visualize results**

**3.1. Saved results**

All the evaluation artificats will be saved under the current output simulation directory **"outputs/{run_time}"**.

For example, you can retrieve the plots of the Precision/Recall curves, after evaluating the float/quantized model on the test set as follows:

![plot](./doc/aeroplane_AP.JPG)

![plot](./doc/person_AP.JPG)

**3.2. Run MLFlow**

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following command:

```bash
mlflow ui
```
And open the given IP adress in your browser.