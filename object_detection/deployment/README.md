# Object detection STM32 model deployment

This tutorial shows how to quantize and deploy a pre-trained object detection model on an *STM32 board* using *STM32Cube.AI*.


## Table of contents

* <a href='#prereqs'>Before you start</a><br>
* <a href='#deploy'>Deploy pretrained tflite model on STM32 board</a><br>
* <a href='#quantize'>Quantize your model before deployment</a><br>

## Before you start
<a id='prereqs'></a>


Please check out [STM32 model zoo](../README.md) for object detection.

### **1. Hardware setup**

The [application code](../../stm32ai_application_code/object_detection/README.md) is running on a hardware setup made up of an STM32 microcontroller board connected to a camera module board. This version supports the following boards only:

- [STM32H747I-DISCO](https://www.st.com/en/product/stm32h747i-disco)
- [B-CAMS-OMV](https://www.st.com/en/product/b-cams-omv)

### **2. Software requirements**

You need to download and install the following software:

- [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html)
- If using [STM32Cube.AI](https://www.st.com/en/embedded-software/x-cube-ai.html) locally, open link and download the package, then `extract here` both `'.zip'` and `'.pack'` files.

### **3. Specifications**

- `serie` : STM32H7
- `IDE` : GCC
- `resizing` : nearest
- Supports only 8-bits quantized TFlite model, i.e. `quantize` : True if model not quantized
- `quantization_input_type` : uint8
- `quantization_output_type` : float


## Deploy pretrained tflite model on STM32 board
<a id='deploy'></a>

### **1. Configure the yaml file**

You can run a demo using a pretrained model from [STM32 model zoo](../pretrained_models/README.md). Please refer to the YAML file provided alongside the TFlite model to fill the following sections in [user_config.yaml](../src/user_config.yaml) (namely `Dataset Configuration` and `Load model`).

As an example, we will show how to deploy the model [ssd_mobilenet_v2_fpnlite_035_192_int8.tflite](../pretrained_models/ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192) pretrained on COCO dataset using the necessary parameters provided in [ssd_mobilenet_v2_fpnlite_035_192_config.yaml](../pretrained_models/ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_config.yaml).

**1.1. General settings:**

Configure the **general** section in **[user_config.yaml](../src/user_config.yaml)** as the following:
```yaml
general:
  project_name: coco_person_detection
  model_type: ssd_mobilenet_v2_fpnlite
  model_path: ../pretrained_models/ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite
```

where:

- `project_name` - *String*, name of the project.
- `model_type` - *String*, model type is used to adapt the postprocessing to the model. There are three possible choices: `'st_ssd_mobilenet_v1'`, `'ssd_mobilenet_v2_fpnlite'`, `'tiny_yolo_v2'`.
- `model_path` - *Path* to pretained model. Please check out pretrained models from STM32 model zoo [here](../pretrained_models/README.md).

Configure the **operation_mode** section as follow:
```yaml
operation_mode: deployment
```
where:
- operation_mode - *String*, operation to be executed when the stm32ai_main.py script is launched. The choices are: `'training'`, `'evaluation'`, `'deployment'`, `'quantization'`, `'benchmarking'`, or a combination of multiple operations: `'chain_tqeb'`, `'chain_tqe'`, `'chain_eqe'`, `'chain_qb'`, `'chain_eqeb'`, `'chain_qd'`. 

**1.2. Dataset configuration:**

You need to specify some parameters related to the dataset and the preprocessing of the data in the **[user_config.yaml](../src/user_config.yaml)** which will be parsed into a header file used to run the C application.

**1.2.1. Dataset info:**

Configure the **dataset** section in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
dataset:
  name: person_dataset
  class_names: [person]
```

where:
- `name` - Dataset name.
- `class_names` - A list containing the classes name.

**1.2.2. Preprocessing info:**

To run inference in the C application, we need to apply on the input data the same preprocessing used when training the model.

To do so, you need to specify the **preprocessing** configuration in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
preprocessing:
  rescaling:  {scale : 127.5, offset : -1}
  resizing:
    aspect_ratio: fit
    interpolation: nearest
  color_mode: rgb
```

- `rescaling` - A *dictonary* with keys *(scale, offset)* to rescale input values to a new range. To scale input image **[0:255]** in the range **[-1:1]** you should pass **{scale = 127.5, offset = -1}**, else in the range **[0:1]** you should pass **{scale = 255, offset = 0}**.
- `resizing` - **nearest**, only supported option for *application C code*.
- `aspect_ratio` - One of *fit*, *crop* or *padding*. If *crop*, resize the images without aspect ratio distortion by cropping the image as a square, if *padding*, add black borders above and below the image to make it as square, otherwise *fit*, aspect ratio may not be preserved.
- `color_mode` - One of "*grayscale*", "*rgb*" or "*bgr*".

**1.3. Post processing info:**

Apply post-processing by modifiying the post_processing parameters in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
postprocessing:
  confidence_thresh: 0.6
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.4
  plot_metrics: true
  max_detection_boxes: 10
```

- `confidence_thresh` - A *float* between 0.0 and 1.0, the score thresh to filter detections.
- `NMS_thresh` - A *float* between 0.0 and 1.0, NMS thresh to filter and reduce overlapped boxes.
- `IoU_eval_thresh` - A *float* between 0.0 and 1.0, Area of Overlap / Area of Union ratio above which two bounding boxes are detecting the same object.
- `plot_metrics` - *Boolean*, print or not the confidence level on the bounding boxes.
- `max_detection_boxes` - An *int* to filter the number of bounding boxes.

**1.4. Load model:**

You can run a demo using a pretrained model provided in [STM32 model zoo](../pretrained_models/README.md) for object detection. These models were trained and quantized on specific datasets (e.g. People...).

Also, you can directly deploy your own pretrained model if quantized using *TFlite Converter* and respecting the specified [intput/output types](#3-specifications), else you can quantize your model before deploying it by following these [steps](#quantize).

To do so, you need to configure the **model** section in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
training:
  model:
    input_shape: (192, 192, 3)
```

where:

- `input_shape` -  A *list of int* *[H, W, C]* for the input resolution, e.g. *[224, 224, 3]*.

**1.5. C project configuration:**

To deploy the model in **STM32H747I-DISCO** board, we will use *STM32Cube.AI* to convert the model into optimized C code and *STM32CubeIDE* to build the C application and flash the board.

These steps will be done automatically by configuring the **stm32ai** section in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
tools:
  stm32ai:
    version: *.*.*
    optimization: balanced
    on_cloud: true
    path_to_stm32ai: C:/Users/<XXXXX>/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/*.*.*/Utilities/windows/stm32ai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_1.*.*/STM32CubeIDE/stm32cubeide.exe
deployment:
  c_project_path: ../../stm32ai_application_code/object_detection/
  IDE: GCC
  verbosity: 1 n
  hardware_setup:
    serie: STM32H7
    board: STM32H747I-DISCO
```

where:

- `tools/stm32ai`
  - `version` - Specify the **STM32Cube.AI** version used to benchmark the model, e.g. **8.0.1**.
  - `optimization` - *String*, define the optimization used to generate the C model, options: "*balanced*", "*time*", "*ram*".
  - `on_cloud` - *Boolean*, to use or not the [STM32Cube.AI Developer Cloud](https://stm32ai-cs.st.com/home).
  - `path_to_stm32ai` - *Path* to stm32ai executable file to use local download, else **False**.
- `tools/path_to_cubeIDE` - *Path* to stm32cubeide executable file.
- `deployment`
  - `c_project_path` - *Path* to [application C code](../../stm32ai_application_code/object_detection/README.md) project.
  - `IDE` -**GCC**, only supported option for *Getting Started*.
  - `verbosity` - *0* or *1*. Mode 0 is silent, and mode 1 displays messages when building and flashing C application on STM32 target.
  - `hardware_setup/serie` - **STM32H7**, only supported option for now.
  - `hardware_setup/board` - **STM32H747I-DISCO**, only supported option for now.

### **2. Run deployment:**

First you need to connect the camera board to the *STM32H747I-DISCO* discovery board, then connect the discovery board to your computer using an usb cable.

The picture below shows how to connect the camera board to the *STM32H747I-DISCO* board using a flat flex cable:

![plot](./doc/img/hardware_setup.JPG)

Then, run the following command to build and flash the application on your board:


```bash
python stm32ai_main.py
```


### **3. Run the application:**

When the application is running on the *STM32H747I-DISCO* discovery board, the LCD displays the following information:
- Data stream from camera board
- Bounding boxes with confidence score between 0 and 1 attached
probability
- The number of object detected
- The number of frames processed per second (FPS) by the model

![plot](./doc/img/output_application.JPG)

## Quantize your model before deployment
<a id='quantize'></a>

### **1. Configure the yaml file**

In addition to the [previous steps](#1-configure-the-yaml-file), you can configure the following sections to quantize your model for the [application C code](../../stm32ai_application_code/object_detection/README.md) deployment. Also, you can evaluate its accuracy after quantization if a path to the `validation set` or `test set` is provided.

**1.1. Loading the dataset:**

Configure the **dataset** section in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
dataset:
  name: person_dataset
  class_names: [person]
  training_path: 
  validation_path: 
  test_path:
```

where:

- `name` - Dataset name. Exception for *Cifar  datasets*, the name should be "*cifar10*" or "*cifar100*".
- `class_names` - A list containing the classes name.
- `training_path` - The directory where the training set is located, or the dataset path.
- `validation_path` - Path to the validation set, needs to be provided to evaluate the model accuracy.
- `test_path` - Path to the test_set, if not provided the validation set will be used for evaluation.

**1.2. Model quantization:**

Configure the **quantization** section in **[user_config.yaml](../src/user_config.yaml)** as the following:

```yaml
quantization:
  quantizer: TFlite_converter
  quantization_type: PTQ
  quantization_input_type: uint8
  quantization_output_type: float
  export_dir: quantized_models
```

where:

- `quantizer` - *String*, only option is "TFlite_converter" which will convert model trained weights from float to integer values. The quantized model will be saved in TensorFlow Lite format.
- `quantization_type` - *String*, only option is "PTQ",i.e. "Post-Training Quantization".
- `quantization_input_type` - **int8** or **uint8**, only supported options for *getting started*.
- `quantization_output_type` - **float**, only supported option for *getting started*.
- `export_dir` - *String*, referres to directory name to save the quantized model.
