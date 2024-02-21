# Image classification STM32 model quantization

Post training quantization is a good way to optimize your neural network models before deploying. This enables the deployment process more efficient on your embedded devices by reducing the required memory usage (Flash/RAM) and reducing the inference time by accelerating the computations, and all this with little-to-no degradation in the model accuracy.

This tutorial shows how to qunatize a floating point model with real data. As an example we will demonstrate the workflow on the [tf_flowers](https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz) classification dataset.


## Table of contents

* Configure the yaml file
* Quantize and evaluate the performance of your model


## **Configure the yaml file**

All the sections of the YAML file must be setted like describes in the **[README.md](../README.md)** with setting the `operation_mode` to quantize, other wise you can precise the `operation_mode` later when running the experience by `python stm32ai_main.py operation_mode=quantize`.

### 1.1 Prepare the dataset

Information about the dataset you want use is provided in the `dataset` section of the configuration file, as shown in the YAML code below.

```yaml
dataset:
  name: flowers 
  class_names: [daisy, dandelion, roses, sunflowers, tulips]
  training_path: /dataset/flower_photos
  validation_path:
  validation_split: 0.15
  test_path:
  quantization_path: 
  quantization_split: 0.8
  seed: 0
```

In this example the only provided path is the training set path, to quantize the model properly a pourcentage defined by `quantization_split` from the training set is used for the quantization.

To evaluate the model accuracy after quantization the validation set is used as the test set, which is a percentage defined by `validation_split` from the training set. 

### 1.2 Apply preprocessing

The images from the dataset need to be preprocessed before they are presented to the network. This includes rescaling and resizing, as illustrated in the YAML code below.

```yaml
preprocessing:
   rescaling: { scale: 1/127.5, offset: -1 }
   resizing: 
     interpolation: nearest
     aspect_ratio: "fit"
   color_mode: rgb
```

The pixels of the input images are in the interval [0, 255]. If you set `scale` to 1./255 and `offset` to 0, they will be rescaled to the interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they will be rescaled to the interval [-1.0, 1.0].

The `resizing` attribute specifies the image resizing methods you want to use:
- The value of `interpolation` must be one of *{"bilinear", "nearest", "bicubic", "area", "lanczos3", "lanczos5", "gaussian", "mitchellcubic"}*.
- The value of `aspect_ratio` must be either *"fit"* or *"crop"*. If you set it to *"fit"*, the resized images will be distorted if their original aspect ratio is not the same as in the resizing size. If you set it to *"crop"*, images will be cropped as necessary to preserve the aspect ration.

The `color_mode` attribute must be one of "*grayscale*", "*rgb*" or "*bgr*".



### 1.3 Getting the model and quantization parameters

As precised previously all the sections of the YAML file must be setted like describes in the **[README.md](../README.md)** with setting the `operation_mode` to quantize and the `quantization` as the following: 

```yaml
quantization:
  model_path: ../pretrained_models/mobilenetv2/ST_pretrainedmodel_public_dataset/flowers/mobilenet_v2_0.35_128/mobilenet_v2_0.35_128.h5
  quantize: True
  evaluate: True
  quantizer: TFlite_converter
  quantization_type: PTQ
  quantization_input_type: uint8
  quantization_output_type: float
  export_dir: quantized_models
```


**where**:

- `model_path` - *String*, specifies the path of the model to be quantized.
- `quantize` - *Boolean*, if True model will be quantized, else False.
- `evaluate` - *Boolean*, if True evaluate quantized model if validation or test sets are provided, else False.
- `quantizer` - *String*, only option is "TFlite_converter" which will convert model trained weights from float to integer values. The quantized model will be saved in TensorFlow Lite format.
- `quantization_type` - *String*, only option is "PTQ",i.e. "Post-Training Quantization". 
- `quantization_input_type` - *String*, can be "int8", "uint8" or "float", represents the quantization type for the model input.
- `quantization_output_type` - *String*, can be "int8", "uint8" or "float", represents the quantization type for the model output.
- `export_dir` - *String*, referres to directory name to save the quantized model.


## **Run the quantization and the evaluation of your model**

Then, run the following command:

```bash
python stm32ai_main.py operation_mode=quantize
```

## **Visualize results**

### 3.1. Saved results

All evaluation artifats are saved under the current output simulation directory **"experiments_outputs/{run_time}"**.

For example, you can retrieve the confusion matrix generated after evaluating the quantized model on the validation/test set as follows:


//

//

### 3.2. Run MLFlow

MLflow is an API for logging parameters, code versions, metrics, and artifacts while running machine learning code and for visualizing results.
To view and examine the results of multiple trainings, you can simply access the MLFlow Webapp by running the following command:

```bash
mlflow ui
```
And open the given IP adress in your browser.