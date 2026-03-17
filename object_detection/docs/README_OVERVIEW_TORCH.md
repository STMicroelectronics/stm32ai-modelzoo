# Object detection STM32 model zoo

Remember that minimalistic yaml files are available [here](../config_file_examples_pt/) to play with specific services, and that all pre-trained models in the [STM32 model zoo](https://github.com/STMicroelectronics/stm32ai-modelzoo/) are provided with their configuration .yaml file used to generate them. These are very good starting points to start playing with!

## <a id="">Table of contents</a>

1. [Object detection Model Zoo introduction](#1)
   - [1.1 Datasets](#1-1) 
   - [1.2 Models](#1-2) 
2. [Object detection tutorial](#2)
   - [2.1 Choose the operation mode](#2-1)
   - [2.2 Global settings](#2-2)
   - [2.3 Model settings](#2-3)
   - [2.4 Dataset specification](#2-4)
   - [2.5 Use data augmentation](#2-5)
   - [2.6 Set the training parameters](#2-6)
   - [2.7 Apply image preprocessing](#2-7)
   - [2.8 Set the postprocessing parameters](#2-8)
   - [2.9 Model quantization](#2-9)
   - [2.10 Benchmark the model](#2-10)
   - [2.11 Deploy the model](#2-11)
   - [2.12 Hydra and MLflow settings](#2-12)
3. [Run the object detection chained service](#3)
4. [Visualize the chained services results](#4)
   - [4.1 Saved results](#4-1)
   - [4.2 Run tensorboard](#4-2)
   - [4.3 Run ClearML](#4-3)
   - [4.4 Run MLFlow](#4-4)
5. [Appendix A: YAML syntax](#A)



<details open><summary><a href="#1"><b>1. Object detection Model Zoo introduction</b></a></summary><a id="1"></a>

The object detection model zoo for Torch provides a collection of independent services and pre-built chained services that can be
used to perform various functions related to machine learning for Object detection. The individual services include
tasks such as training, evaluation and quantization of the model as individual task, while the chained services combine multiple services to
perform more complex functions, such as training, quantizing and evaluating the quantized model
successively.

To use the services in the Object detection model zoo, you can utilize the model zoo [stm32ai_main.py](../stm32ai_main.py) along with the [user_config_pt.yaml](../user_config.yaml) file as input. The yaml file specifies the service or the chained services and a set of configuration parameters such as the model (either from the model zoo or your own custom model), the dataset, the number of epochs, and the preprocessing parameters, among others.

More information about the different services and their configuration options can be found in the <a href="#2">next
section</a>.

We primarily support the datasets to be in MS-COCO format. 
1. COCO (Supported by ST_YOLOD models)
2. COCO and Pascal VOC (Supported by SSD models)
</details></ul>

<ul><details open><summary><a href="#1-1">1.1 Datasets</a></summary><a id="1-1"></a>

<ul><details open><summary><a href="#1-1-1">1.1.1 COCO datasets</a></summary><a id="1-1-1"></a>

The COCO is a large-scale benchmark widely used for object detection, instance segmentation, and keypoint detection, containing everyday scenes with multiple objects labeled using rich annotations such as bounding boxes, segmentation masks, and class labels. The official COCO dataset folder structure, as released by the COCO team, is organized by year-based splits and separates images from annotations. At the top level, COCO contains an images/ directory with subfolders like train2017/, val2017/, and test2017/ that store the actual JPEG images, and an annotations/ directory that holds JSON files describing labels and metadata. The most common annotation files are instances_train2017.json and instances_val2017.json (object detection and segmentation), along with others such as captions_*.json (image captions) and person_keypoints_*.json (human keypoints) but for object detection, only instances_train2017.json and instances_val2017.json files are used. A typical layout looks like this:
COCO dataset can be directly downloaded from from [here](https://cocodataset.org/#download).

An example of this structure is shown below:

```yaml
coco/
├── annotations/
│   ├── instances_train2017.json # json with all training annotation 
│   ├── instances_val2017.json
│   ├── captions_train2017.json
│   ├── captions_val2017.json
│   ├── person_keypoints_train2017.json
│   └── person_keypoints_val2017.json
└── images/
    ├── train2017/ # training images files 
    ├── val2017/
    └── test2017/
```

For custom datasets or for custom classes one can create new instances files as below (for eg. _person for person class only or _small for a small dataset for testing purposes) without modifying the structure of images folder. 
```yaml
/neutrino/datasets/coco/annotations/
├── instances_train2017.json
├── instances_train2017_person.json
├── instances_train2017_small.json
├── instances_val2017.json
├── instances_val2017_person.json
├── instances_val2017_small.json
├── custom_train2017.json
└── custom_val2017.json
```

Pascal VOC dataset can be converted to coco format by using open source services like [voc2coco](https://github.com/yukkyo/voc2coco) or [tiny_coco_dataset](https://github.com/lizhogn/tiny_coco_dataset) to create a minimalistic training set in coco format. 

**Download Instructions**

The most commonly used version for object detection and instance segmentation is **COCO 2017**, which includes training, validation, and test splits.

**Option 1: Command-Line Download (Recommended)**

```bash
mkdir -p ~/datasets/coco
cd ~/datasets/coco

# Download images
wget http://images.cocodataset.org/zips/train2017.zip
wget http://images.cocodataset.org/zips/val2017.zip

# (Optional) test images
wget http://images.cocodataset.org/zips/test2017.zip

# Download annotations
wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip

# unzip 
unzip train2017.zip
unzip val2017.zip
unzip test2017.zip        # optional
unzip annotations_trainval2017.zip
```

**Option 2: Manual Download**

1. Go to the official COCO dataset page https://cocodataset.org and navigate to Download → COCO 2017 Dataset

2. Download:
```yaml
train2017.zip
val2017.zip
annotations_trainval2017.zip
(Optional) test2017.zip
```
3. Extract all files into a single coco/ directory.

</details></ul>

<ul><details open><summary><a href="#1-1-2">1.1.2 Pascal VOC datasets</a></summary><a id="1-1-2"></a>

The Pascal Visual Object Classes (VOC) dataset is a classic benchmark for object detection, image classification, and semantic segmentation. It contains images annotated with bounding boxes, object class labels, and (for segmentation tasks) pixel-level masks. Pascal VOC is widely used for prototyping, debugging, and benchmarking detection pipelines because of its lean annotations, fixed class set (20 object classes), and relatively smaller size compared to COCO.

**Folder Structure (VOC 2007 / VOC 2012)**

After extraction, the Pascal VOC dataset follows a standardized directory layout. The root folder is named `VOCdevkit`, which may contain one or more dataset versions such as `VOC2007` and `VOC2012`.
```yaml
VOCdevkit/
└── VOC2012/ # or VOC2007/
├── Annotations/ # XML files (one per image) with object labels & boxes
├── ImageSets/
│ ├── Main/ # train/val/test splits for detection & classification
│ │ ├── train.txt
│ │ ├── val.txt
│ │ ├── trainval.txt
│ │ └── test.txt
│ └── Segmentation/ # splits for segmentation tasks
├── JPEGImages/ # all images (.jpg)
├── SegmentationClass/ # pixel-wise semantic segmentation masks
├── SegmentationObject/ # instance-level segmentation masks
└── README.md
```


**Download Instructions**

**Option 1: Official Pascal VOC Website (Manual)**

1. Visit the official Pascal VOC site  
   http://host.robots.ox.ac.uk/pascal/VOC/

2. Download one or both datasets:
   - **VOC2007** (commonly used for detection benchmarks)
   - **VOC2012** (larger and more recent)

3. Extract the tar files:
   ```bash
   tar -xvf VOCtrainval_11-May-2012.tar
   tar -xvf VOCtrainval_06-Nov-2007.tar
   ```


**Option 2: Command Line Download (Recommended)**
```
mkdir -p ~/datasets
cd ~/datasets

# VOC 2012
wget http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar
tar -xvf VOCtrainval_11-May-2012.tar

# VOC 2007 (optional)
wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval_06-Nov-2007.tar
tar -xvf VOCtrainval_06-Nov-2007.tar
```

</details></ul>

</details></ul>

<ul><details open><summary><a href="#1-2">1.2 Models</a></summary><a id="1-2"></a>
Object detection for torch framework supports two object detection model families: ST_YOLOD and SSD, chosen to balance efficiency, accuracy, and deployment feasibility on resource-constrained devices.

<ul><details open><summary><a href="#1-2-1">1.2.1 ST_YOLOD Models</a></summary><a id="1-2-1"></a>

**ST_YOLOD** is an in-house, efficiency-focused object detection model developed by **ST**, designed for low-latency and low-memory deployment while maintaining competitive detection performance. The architecture emphasizes lightweight convolutional blocks, optimized feature aggregation, and simplified detection heads. 

ST_YOLO is evaluated in two size variants:

`YOLODv2-Milli` - An ultra-lightweight variation of ST_YOLOD

`YOLODv2-Tiny` - A slightly larger and more expressive variant 

> *Reference*: ST_YOLOD architecture details are described in this paper ([arXiv link](https://arxiv.org/abs/2601.05364)).

</details></ul>

<ul><details open><summary><a href="#1-2-2">1.2.2 SSD Models</a></summary><a id="1-2-2"></a>

**SSD** is a well-established single-stage object detection framework that predicts object bounding boxes and class probabilities from multiple feature maps at different scales. 

We evaluate six SSD-based variants, all using MobileNet backbones to ensure fair comparison with lightweight models:

`SSDLite-MobileNetV1` - Uses depthwise separable convolutions to reduce computation while retaining SSD’s multi-scale detection capability.

`SSDLite-MobileNetV2` - Builds on inverted residual blocks and linear bottlenecks for improved efficiency and accuracy over V1.

`SSDLite-MobileNetV3-Small`- Optimized for very low-latency scenarios, leveraging MobileNetV3’s hardware-aware design.

`SSDLite-MobileNetV3-Large` - A higher-capacity MobileNetV3 variant that improves accuracy while maintaining mobile-friendly performance.

`SSD-MobileNetV1` - A non-Lite SSD configuration using MobileNetV1, providing a stronger baseline at the cost of increased computation.

`SSD-MobileNetV2`- Combines standard SSD heads with a MobileNetV2 backbone, offering improved representational capacity compared to Lite variants.

</details></ul>

</details></ul>
</details>
<details open><summary><a href="#2"><b>2. Object detection tutorial</b></a></summary><a id="2"></a>

This tutorial demonstrates how to use the `chain_tqeb` services to train, benchmark, quantize, evaluate, and benchmark
the model.

To get started, you will need to update the [user_config_pt.yaml](../user_config_pt.yaml) file, which specifies the parameters and configuration options for the services that you want to use. Each section of the [user_config_pt.yaml](../user_config_pt.yaml) file is explained in detail in the following sections.

<ul><details open><summary><a href="#2-1">2.1 Choose the operation mode</a></summary><a id="2-1"></a>


The `operation_mode` top-level attribute specifies the operations or the service you want to execute. This may be a single operation or a set of chained operations.

The different values of the `operation_mode` attribute and the corresponding operations are described in the table below. In the names of the chain modes, 't' stands for training, 'e' for evaluation, 'q' for quantization, 'b' for benchmark, and 'd' for deployment on an STM32 board.

| operation_mode attribute | Operations                                                                                                                                          |
|:-------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| `training`               | Train a model from the variety of object detection models in the model zoo or your own model                                                        |
| `evaluation`             | Evaluate the accuracy of a float or quantized model on a test or validation dataset                                                                 |
| `quantization`           | Quantize a float model                                                                                                                              |
| `prediction`             | Predict the classes and bounding boxes of some images using a float or quantized model.                                                             |
| `benchmarking`           | Benchmark a float or quantized model on an STM32 board                                                                                              |
| `deployment`             | Deploy a model on an STM32 board                                                                                                                    |
| `chain_tqeb`             | Sequentially: training, quantization of trained model, evaluation of quantized model, benchmarking of quantized model                               |
| `chain_tqe`              | Sequentially: training, quantization of trained model, evaluation of quantized model                                                                |
| `chain_eqe`              | Sequentially: evaluation of a float model, quantization, evaluation of the quantized model                                                          |
| `chain_qb`               | Sequentially: quantization of a float model, benchmarking of quantized model                                                                        |
| `chain_eqeb`             | Sequentially: evaluation of a float model, quantization, evaluation of quantized model, benchmarking of quantized model                             |
| `chain_qd`               | Sequentially: quantization of a float model, deployment of quantized model                                                                          |

You can refer to readme links below that provide typical examples of operation modes, and tutorials on specific services:

- [training, chain_tqe, chain_tqeb](./README_TRAINING.md)
- [quantization, chain_eqe, chain_qb](./README_QUANTIZATION.md)
- [evaluation, chain_eqeb](./README_EVALUATION.md)
- [benchmarking](./README_BENCHMARKING.md)
- deployment, chain_qd ([STM32H7](./README_DEPLOYMENT_STM32H7.md), [STM32N6](./README_DEPLOYMENT_STM32N6.md), [STM32MPU](./README_DEPLOYMENT_MPU.md))

In this tutorial, the `operation_mode` used is the `chain_tqeb` as shown below to train a model, quantize, evaluate it to be later deployed in the STM32 boards.

```yaml
operation_mode: chain_tqeb
```
</details></ul>

<ul><details open><summary><a href="#2-2">2.2 Global settings</a></summary><a id="2-2"></a>

The `general` section and its attributes are shown below.

```yaml
general:
  saved_models_dir: 'st_yolodv2milli_actrelu_pt' # trained model, log, eval etc will be stored in the sub dir
  global_seed: 42                  # Seed used to seed random generators (an integer). Optional, defaults to 123.
```
The `saved_models_dir` attribute is the name of the directory where models are saved, which includes the trained model
and the quantized model. These two directories are located under the top level <hydra> directory.


The `global_seed` attribute specifies the value of the seed to use to seed the Python, numpy, and PyTorch random generators at the beginning of the main script. This is an optional attribute, the default value being 123. If you don't want random generators to be seeded, then set `global_seed` to 'None' (not recommended as this would make training results less reproducible).

Even when random generators are seeded, it is often difficult to exactly reproduce results when the same operation is
run multiple times. This typically happens when the same training script is run on different hardware.


</details></ul>

<ul><details open><summary><a href="#2-3">2.3 Model specification</a></summary><a id="2-3"></a>

<ul><details open><summary><a href="#2-3-1">2.3.1 SSD Models</a></summary><a id="2-3-1"></a>

```yaml
model:
  framework: 'torch' 
  model_type : ssd
  model_path : ''
  # model_name options for SSD model 
  # ['ssd_mobilenetv1_pt', 'ssdlite_mobilenetv1_pt', 'ssd_mobilenetv2_pt', 'ssdlite_mobilenetv2_pt', 'ssdlite_mobilenetv3small_pt', 'ssdlite_mobilenetv3large_pt']
  model_name: "ssdlite_mobilenetv2_pt"
  width_mult: 1.0
  pretrained: True
  # dataset name coco_person is for pretrained dataset coco_person
  pretrained_dataset : coco_person
  input_shape: [3, 300, 300]
  num_classes: 1
```

The `framework` attribute specifies the deep learning framework used for this model. In this example, `'torch'` indicates **PyTorch** is used.  

The `model_type` attribute defines the type of model architecture. Here, `ssd` is selected, indicating that a Single Shot MultiBox Detector (SSD) will be used.  

The `model_name` attribute specifies the exact SSD variant to use. Available options for SSD models include:
- `ssd_mobilenetv1_pt`
- `ssdlite_mobilenetv1_pt`
- `ssd_mobilenetv2_pt`
- `ssdlite_mobilenetv2_pt`
- `ssdlite_mobilenetv3small_pt`
- `ssdlite_mobilenetv3large_pt`  

In this example, `"ssdlite_mobilenetv2_pt"` is chosen for its balance of efficiency and accuracy on edge devices.  

The `width_mult` attribute controls the width multiplier for the backbone network, scaling the number of channels in the network. A value of `1.0` uses the standard width.  

The `pretrained` attribute indicates whether to use **pretrained weights**. Setting it to `True` allows the model to leverage weights trained on a larger dataset for better initialization.  

The `pretrained_dataset` attribute specifies the dataset used for pretraining. In this example, `coco_person` means the pretrained weights were trained specifically on the COCO person class.  

The `input_shape` attribute defines the expected input tensor dimensions as `[channels, height, width]`. Here, `[3, 300, 300]` corresponds to standard RGB images resized to 300×300 pixels.  

The `num_classes` attribute specifies the number of output classes for detection. Here, `1` indicates that only a single class (person) is being detected.  


</details></ul>

<ul><details open><summary><a href="#2-3-2">2.3.2 ST_YOLOD Models</a></summary><a id="2-3-2"></a>


```yaml
# ---------------- Model Configuration ---------------- #
model:
  framework: 'torch' 
  model_type : st_yolod # this config is for yolod model family 
  model_path : '' 
  # following are supported models 
  # ['st_yolodv2milli_actrelu_pt', 'st_yolodv2tiny_actrelu_pt']
  model_name: st_yolodv2milli_actrelu_pt 
  pretrained: True
  # dataset name coco_person is for pretrained dataset coco_person
  pretrained_dataset: coco # this yaml is for coco style annotation only 
  input_shape: [3, 640, 640]  # (channel, height, width)
  pretrained_input_shape : [3, 640, 640]
  num_classes: 1 # number of classes 
```

The `framework` attribute specifies the deep learning framework used for this model. Here, `'torch'` indicates that **PyTorch** is used.  

The `model_type` attribute defines the model family. In this example, `st_yolod` indicates that this configuration is for the **ST_YOLOD model family**, an in-house efficient object detector.  

The `model_name` attribute specifies the exact ST_YOLOD variant to use. Supported models include:
- `st_yolodv2milli_actrelu_pt` – an ultra-lightweight variant optimized for extremely constrained devices.  
- `st_yolodv2tiny_actrelu_pt` – a slightly larger variant with improved accuracy while remaining efficient.  

The `pretrained` attribute indicates whether to use **pretrained weights**. Setting it to `True` allows the model to leverage previously trained weights for better initialization.  

The `pretrained_dataset` attribute specifies the dataset used for pretraining. In this case, `coco` indicates that the pretrained weights were trained on the COCO dataset with COCO-style annotations.  

The `input_shape` attribute defines the expected input tensor dimensions as `[channels, height, width]`. Here, `[3, 640, 640]` corresponds to RGB images resized to 640×640 pixels.  

The `pretrained_input_shape` attribute specifies the input shape used during pretraining, ensuring compatibility when loading pretrained weights.  

The `num_classes` attribute specifies the number of detection classes. Here, `1` indicates that the model is configured to detect a single class (e.g., person).  

</details></ul>


The `model_path` attribute is common and it is utilized to indicate the path to the model file that you wish to use for the selected
operation mode. The accepted formats for `model_path` are listed in the table below:

| Operation mode | `model_path`                                     |
|:---------------|:-------------------------------------------------|
| 'evaluation'   | .pt or ONNX (float or QDQ) file |
| 'quantization', 'chain_eqe', 'chain_eqeb', 'chain_qb', 'chain_qd' | .pt or ONNX (float or QDQ) model file          |
| 'prediction'   | .pt or ONNX (float or QDQ) file |
| 'benchmarking' | .pt or ONNX (float or QDQ) file |
| 'deployment'   | .pt or ONNX (QDQ) file |

If you are providing `.pt` file for `model_path` then you also have to provide `model_name` so that model definition can be created before loading weights from `.pt` file.


It is important to note that each model type has specific requirements in terms of input image size, output size of the head and/or backbone, and other parameters. Therefore, it is important to choose the appropriate model type for your
specific use case, and to configure the training process accordingly.

If you are using an operation mode that involves training, you can use the `model_path` attribute to train your own
custom model instead of using a model from the Model Zoo. This is explained in detail in
the [readme](./README_TRAINING.md) file for the train service. However, in this tutorial, the `model_path` attribute is
not used since we are using a pre-trained model from the Model Zoo.


</details></ul>

<ul><details open><summary><a href="#2-4">2.4 Dataset specification</a></summary><a id="2-4"></a>

As explained in the <a href="#1-1">Dataset section</a>, 
object detection for torch framework supports Pascal VOC and COCO datasets for training, The `dataset` section and its attributes are shown in the YAML code below. 

<ul><details open><summary><a href="#2-4-1">2.4.1 COCO Dataset </a></summary><a id="2-4-1"></a>

```yaml

  format : coco 
  dataset_name : coco
  class_names: ["person"]
  training_path : " " # leave empty 
  train_images_path : ../../datasets/coco/train2017
  train_annotations_path: ../../datasets/coco/annotations/instances_train2017.json  # Name of annotation file for training
  val_images_path : ../../datasets/coco/val2017
  val_annotations_path: ../../datasets/coco/annotations/instances_val2017.json  # Name of annotation file for evaluation, 
  test_images_path : ../../datasets/coco/train2017
  test_annotations_path: ../../datasets/coco/annotations/instances_train2017.json  # Name of annotation file for training
  quantization_path : ../../datasets/coco/val2017
  prediction_path: ../../datasets/coco/annotations/instances_val2017.json  # Name of annotation file for evaluation, 
  seed : 123
```

The `format` attribute is optional and can be used to specify format `coco` or `voc`
The `dataset_name` attribute is to specify the name of dataset `coco` or `voc`. Based on this attribute dataloader is selected. 

The `class_names` attribute specifies the classes in the dataset. This information must be provided in the YAML file (only for evaluation, prediction, quantization), class_names is directly accessible from coco or pascal voc annotations in `training` operation. If the `class_names` attribute is absent, the `classes_name_file` argument can be used as an alternative, pointing to a text file containing the class names.

The `train_images_path` is set to the image folder on COCO format dataset 
The `train_annotations_path` is set to json annotations path. Both images and annotations path are mandatory
`val_images_path`. `val_annotations_path`, `test_images_path`, `test_annotations_path` is used in similar way for validation and test data. 

When a model accuracy evaluation is run, the test set is used if there is one, otherwise the validation set is
used. 

The `prediction_split` is set to the image folder used for prediction. 

The `seed` attribute specifies the seed value to use for randomly shuffling the dataset file before
splitting it (default value is 123).

The `quantization_path` attribute is used to specify a dataset for the quantization process. If this attribute is not
provided and a training set is available, the training set is used for the quantization. However, training sets can be
quite large and the quantization process can take a long time to run. To avoid this issue, you can set
the `quantization_split` attribute to use only a portion of the dataset for quantization.

```training_path``` attribute is not used for torch but should be kept empty to ensure other pipelines work efficiently. 

</details></ul>

<ul><details open><summary><a href="#2-4-2">2.4.2 Pascal VOC Dataset  </a></summary><a id="2-4-2"></a>



```yaml
  train_images_path : ../../datasets/VOCdevkit/VOC2012/JPEGImages # image folder (image files)
  train_annotations_path: ../../datasets/VOCdevkit/VOC2012/Annotations # annotation folder *.xml files
  train_split :  ../../datasets/VOCdevkit/VOC2012/ImageSets/Main/trainval.txt # list of images (names) as in pascal voc
  val_images_path : ../../datasets/VOCdevkit/VOC2007/JPEGImages/
  val_annotations_path: ../../datasets/VOCdevkit/VOC2007/Annotations/  
  val_split : ../../datasets/VOCdevkit/VOC2007/ImageSets/Main/test.txt
```

yaml structure for Pascal voc differs only for data folder structure. 

The `train_images_path` is set to the image folder on voc format dataset (usually JPEGImages in standard voc data) 
The `train_annotations_path` is set to xmls annotations folder. 
The `train_split` is set to .txt with list of images for train, test, validation etc. 

images, annotations folders and train_split file path are mandatory. Everything else remains same as the COCO format yaml file. 

</details></ul>

</details></ul>

<ul><details open><summary><a href="#2-5">2.5 Use data augmentation</a></summary><a id="2-5"></a>

The data augmentation functions to apply to the input images during a training are specified in the
data_augmentation is part of `dataset` section of the configuration file. They are only applied to the images during training.

For this tutorial, the data augmentation section is shown below.

```yaml
  # augmentation and used for training only 
  num_workers: 4  # Set worker to 4  training process costs a lot of memory, reduce this value.
  multiscale_range: 5  # Actual multiscale ranges: [640 - 5 * 32, 640 + 5 * 32]. To disable multiscale training, set the value to 0.
  random_size: [10, 20] # You can uncomment this line to specify a multiscale range
  mosaic_prob: 0.5  # Probability of applying mosaic augmentation
  mixup_prob: 1.0  # Probability of applying mixup augmentation
  hsv_prob: 1.0  # Probability of applying HSV augmentation
  flip_prob: 0.5  # Probability of applying flip augmentation
  degrees: 10.0  # Rotation angle range, for example, if set to 2, the true range is (-2, 2)
  translate: 0.1  # Translate range, for example, if set to 0.1, the true range is (-0.1, 0.1)
  mosaic_scale: (0.5, 1.5)  # Scale range for mosaic augmentation
  enable_mixup: False  # Apply mixup augmentation or not
  mixup_scale: (0.5, 1.5)  # Scale range for mixup augmentation
  shear: 2.0  # Shear angle range, for example, if set to 2, the true range is (-2, 2)
```

When applying data augmentation for object detection, it is important to take into account both the augmentation of the
input images and the modification of the annotations file to ensure that the model is trained on accurate and
representative data.

**Parameter Descriptions:**

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `num_workers` | Number of CPU workers for data loading. Reduce if running out of memory. | 2-8 |
| `multiscale_range` | Range for multi-scale training. Images are randomly resized within `[base - range*32, base + range*32]`. Set to 0 to disable. | 0-10 |
| `mosaic_prob` | Probability of applying mosaic augmentation, which combines 4 images into one to increase context diversity. | 0.0-1.0 |
| `mixup_prob` | Probability of applying mixup, which blends two images together to improve generalization. | 0.0-1.0 |
| `hsv_prob` | Probability of adjusting Hue, Saturation, and Value (brightness) of images for color robustness. | 0.0-1.0 |
| `flip_prob` | Probability of horizontal flip. Set to 0.5 for balanced left/right augmentation. | 0.0-0.5 |
| `degrees` | Maximum rotation angle in degrees. Range is `[-degrees, +degrees]`. | 0-15 |
| `translate` | Maximum translation as fraction of image size. Range is `[-translate, +translate]`. | 0.0-0.2 |
| `shear` | Maximum shear angle in degrees. Range is `[-shear, +shear]`. | 0-5 |
| `mosaic_scale` | Scale range for mosaic augmentation (min, max). | (0.5, 1.5) |
| `enable_mixup` | Enable/disable mixup augmentation entirely. | True/False |
| `mixup_scale` | Scale range for mixup augmentation (min, max). | (0.5, 1.5) |

**Tips for Tuning:**
- Start conservative: Begin with lower probabilities (0.3-0.5) and gradually increase if the model underfits.
- Reduce for small datasets: Heavy augmentation on small datasets can destabilize training.
- Disable for fine-tuning: When fine-tuning a pretrained model, consider reducing augmentation strength. 

  
**Further Reading:**
 - [Mosaic Augmentation (YOLOv4)](https://arxiv.org/abs/2004.10934) - Combines 4 images into one
 - [MixUp Augmentation](https://arxiv.org/abs/1710.09412) - Image blending for regularization
 - [YOLOX Training](https://arxiv.org/abs/2107.08430) - Explains multi-scale and augmentation strategies


</details></ul>

<ul><details open><summary><a href="#2-6">2.6 Set the training parameters</a></summary><a id="2-6"></a>

A 'training' section is required in all the operation modes that include a training, namely 'training', 'chain_tqeb' and 'chain_tqe'. In this tutorial, we will be using a custom object detection model called st_ssd_mobilenet_v1. This model is a custom SSD (Single Shot Detector) model that uses MobileNetv1 as its backbone. The backbone weights have been pre-trained on the ImageNet dataset, which is a large dataset consisting of 1.4 million images and 1000 classes.

We will explain two different training config files as we support two different trainers called `ssd` and `yolod`. 

<ul><details open><summary><a href="#2-6-1">2.6.1 YOLOD Trainer</a></summary><a id="2-6-1"></a>

Configure the training section in [training_config_coco.yaml](../config_file_examples_pt/yolod/st_yolodv2_pt/training_config_coco.yaml) to use ST_YOLOD triner (to be used for ST_YOLOD models) 

```yaml
training:
  trainer_name : 'yolod' # ['yolod' trainer supported only]
  batch_size: 64
  warmup_epochs: 1 # epoch number used for warmup
  epochs: 300 # max training epoch
  scheduler: "yoloxwarmcos"  # Name of LRScheduler
  no_aug_epochs: 15 # Last #epoch to close augmentation like mosaic
  ema: True  # Apply EMA during training
  print_interval: 1  # Log period in iterations. For example, if set to 1, user could see log every iteration.
  eval_interval: 1  # Evaluation period in epochs. For example, if set to 1, model will be evaluated after every epoch.
  save_history_ckpt: True  # Save history checkpoint or not. If set to False, YOLOD will only save the latest and best checkpoint.
  optimizer: 
    SGD:
      learning_rate: 0.01 
      momentum: 0.9  # Momentum of optimizer
      warmup_lr: 0.0  # minimum learning rate during warmup
      min_lr_ratio: 0.05  # Minimum learning rate ratio
      weight_decay: 5e-4  # Weight decay of optimizer
  resume_training_from: '' # 
  start_epoch: 0
  fp16: True
```

The `trainer_name` subsection is used to specify the trainer. We use `ssd` trainer for SSD models and `yolod` trainers for YOLOD models but in the future variations these trainers can be selected for different models. 

The `batch_size` and `epochs` attributes are mandatory for training.

The `warmup_epochs` (default value -1) specifies the number of initial epochs during which the learning rate is gradually increased from warmup_lr to the base learning rate. This helps stabilize training in the early stages. 

The `scheduler` subsection specifies the learning rate scheduler.  `yoloxwarmcos` scheduler is used as default schedule for `yolod` models.

The `no_aug_epochs` subsection specifies number of epochs before the last epoch when augmentations like mosaic should be disabled. This is to get better mAP for the model. 

The `ema` attribute specifies whether to apply **Exponential Moving Average (EMA)** during training. Setting it to `True` helps stabilize training and often improves final model accuracy.  

The `print_interval` attribute defines the logging frequency in iterations. For example, if set to `1`, the training progress and metrics will be printed after every iteration.  

The `eval_interval` attribute sets the evaluation period in epochs. For example, if set to `1`, the model will be evaluated after every epoch.  

The `save_history_ckpt` attribute determines whether to save all historical checkpoints. If `True`, all checkpoints are saved. If `False`, only the latest and best checkpoints are kept.  

The `optimizer` subsection specifies the optimization algorithm and its hyperparameters. In this example, **SGD** is used with the following parameters:
- `learning_rate`: initial learning rate (e.g., 0.01)  
- `momentum`: momentum factor for SGD (e.g., 0.9)  
- `warmup_lr`: minimum learning rate used during warmup (e.g., 0.0)  
- `min_lr_ratio`: ratio to scale the minimum learning rate relative to initial LR (e.g., 0.05)  
- `weight_decay`: weight decay coefficient for regularization (e.g., 5e-4)  
All the training results can be reproduced using SGD with recommended hyperparameters in config files. For large datasets and CNN models SGD is always recommended but for faster experiments Adam can be used. Adam may not generalize well but can converge faster. 

The `resume_training_from` attribute specifies the path to a checkpoint to resume training from. An empty string `''` means training starts from scratch.  

The `start_epoch` attribute defines the epoch number to start training from, typically `0` for fresh training.  

The `fp16` attribute indicates whether to use **mixed precision training** (half-precision) to reduce memory usage and improve training speed. Setting it to `True` enables FP16 training.

The best model obtained at the end of the training is saved in the 'experiments_outputs/\<date-and-time\>/saved_models'
directory and is called 'best_model' (see section <a href="#4">visualize the chained services results</a>).

</details></ul>

<ul><details open><summary><a href="#2-6-2">2.6.2 SSD Trainer </a></summary><a id="2-6-2"></a>

```yaml
training:
  trainer_name : ssd
  batch_size: 32
  epochs: 300
  validation_epochs: 2
  print_interval : 100
  base_net_lr: null             
  extra_layers_lr: null
  momentum: 0.9
  weight_decay: 0.0005
  gamma: 0.1
  scheduler: "cosine"  
  t_max: 200
  optimizer: 
    SGD:
      learning_rate: 0.01 
      momentum: 0.9
      weight_decay: 0.0005
  ```

The `trainer_name` attribute specifies which trainer to use for model training. In this example, `ssd` is selected, indicating that the SSD training pipeline will be used.  

The `batch_size` attribute defines the number of samples processed per iteration. Here, it is set to `32`, which balances memory usage and training efficiency.  

The `epochs` attribute specifies the total number of training cycles over the entire dataset. In this example, the model will train for `300` epochs.  

The `validation_epochs` attribute determines how frequently validation is performed, in terms of epochs. A value of `2` means validation runs every 2 epochs.  

The `print_interval` attribute sets how often training logs are printed, in terms of iterations. For example, a value of `100` will display metrics every 100 iterations.  

The `base_net_lr` and `extra_layers_lr` attributes allow custom learning rates for the backbone network and extra layers. A value of `null` uses the default learning rate for all layers.  

The `momentum` attribute specifies the momentum factor for the optimizer, which helps accelerate gradient descent and smooth updates. Here, it is set to `0.9`.  

The `weight_decay` attribute controls L2 regularization to prevent overfitting. In this configuration, it is set to `0.0005`.  

The `gamma` attribute is used in learning rate schedulers for step decay, defining the decay factor applied at each step. Here, it is set to `0.1`.  

The `scheduler` attribute specifies the learning rate scheduling strategy. `"cosine"` indicates the cosine annealing schedule, gradually reducing the learning rate in a cosine curve.  

The `t_max` attribute sets the maximum number of iterations for the cosine scheduler before restarting. In this case, it is `200`.  

The `optimizer` subsection defines the optimization algorithm and its hyperparameters. In this example, **SGD** is used with:
- `learning_rate`: initial learning rate (e.g., `0.01`)  
- `momentum`: momentum factor (e.g., `0.9`)  
- `weight_decay`: L2 regularization coefficient (e.g., `0.0005`)  
All the training results can be reproduced using SGD with recommended hyperparameters in config files. For large datasets and CNN models SGD is always recommended but for faster experiments Adam can be used. Adam may not generalize well but can converge faster. 

These attributes collectively control the training behavior, learning rate updates, optimization stability, and logging frequency for the SSD training pipeline.
</details></ul>

</details></ul>

<ul><details open><summary><a href="#2-7">2.7 Apply image preprocessing</a></summary><a id="2-7"></a>

Object detection requires images to be preprocessed by rescaling and resizing them before they can be used. This is
specified in the 'preprocessing' section, which is mandatory in all operation modes. Additionally, bounding boxes should
be processed along with the images to accurately detect objects in the images.
This is specified in the 'preprocessing' section that is required in all the operation modes.

The 'preprocessing' section for this tutorial is shown below.

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

Images are rescaled using the formula "Out = scale\*In + offset". Pixel values of input images usually are integers in
the interval [0, 255]. If you set *scale* to 1./255 and offset to 0, pixel values are rescaled to the
interval [0.0, 1.0]. If you set *scale* to 1/127.5 and *offset* to -1, they are rescaled to the interval [-1.0, 1.0].

The resizing interpolation methods that are supported include 'bilinear', 'nearest', 'bicubic', 'area', 'lanczos3', '
lanczos5', 'gaussian' and 'mitchellcubic'. Refer to the [Pytorch resize](https://docs.pytorch.org/vision/main/generated/torchvision.transforms.functional.resize.html) function documentation for
more detail.

Please note that the 'fit' option is the only supported option for the `aspect_ratio` attribute. When using this option,
the images will be resized to fit the target size. It is important to note that input images may be smaller or larger
than the target size, and will be distorted to some extent if their original aspect ratio is not the same as the
resizing aspect ratio. Additionally, bounding boxes should be adjusted to maintain their relative positions and sizes in
the resized images.

The `color_mode` attribute can be set to either *"grayscale"*, *"rgb"* or *"rgba"*. 

preprocessing parameters for different models can vary based on different training strategies and specific yaml file for model/dataset combination should be referred. 
* [SSD-coco](../config_file_examples_pt/ssd/training_config_coco.yaml)
* [SSD - voc](../config_file_examples_pt/ssd/training_config_voc.yaml)
* [ST_YOLOD - coco](../config_file_examples_pt/yolod/st_yolodv2_pt/training_config_coco.yaml)


</details></ul>

<ul><details open><summary><a href="#2-8">2.8 Set the postprocessing parameters</a></summary><a id="2-8"></a>

A 'postprocessing' section is required in all operation modes for object detection models. This section includes
parameters such as NMS threshold, confidence threshold, IoU evaluation threshold, and maximum detection boxes. These
parameters are necessary for proper post-processing of object detection results.

```yaml
postprocessing:
  confidence_thresh: 0.001
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 100
```

`NMS_thresh (Non-Maximum Suppression Threshold)`: This parameter controls the overlapping bounding boxes that are considered as separate detections. A higher NMS threshold will result in fewer detections, while a lower threshold will result in more detections. To improve object detection, you can experiment with different NMS thresholds to find the optimal value for your specific use case.

- **confidence_thresh**: This parameter controls the minimum confidence score required for a detection to be considered valid. A higher confidence threshold will result in fewer detections, while a lower threshold will result in more detections.

- **IoU_eval_thresh**: This parameter controls the minimum overlap required between two bounding boxes for them to be considered as the same object. A higher IoU threshold will result in fewer detections, while a lower threshold will result in more detections.

- **max_detection_boxes**: This parameter controls the maximum number of detections that can be output by the object detection model. A higher maximum detection boxes value will result in more detections, while a lower value will result in fewer detections.

- **plot_metrics**: This parameter is an optional parameter in the object detection model that controls whether or not to plot the precision versus recall curves. By default, this parameter is set to False, which means that the precision versus recall curves will not be plotted. If you set this parameter to True, the object detection model will generate and display the precision versus recall curves, which can be helpful for evaluating the performance of the model.

Overall, improving object detection requires careful tuning of these post-processing parameters based on your specific use case. Experimenting with different values and evaluating the results can help you find the optimal values for your object detection model.

</details></ul>

<ul><details open><summary><a href="#2-9">2.9 Model quantization</a></summary><a id="2-9"></a>

The `quantization` section is required in all the operation modes that include a quantization, namely `quantization`, `chain_tqe`, `chain_tqeb`, `chain_eqe`, `chain_eqeb`, `chain_qb`, and `chain_qd`.

The `quantization` section for this tutorial is shown below.

```yaml
quantization:
  quantizer: `onnx_quantizer`
  quantization_type: PTQ
  quantization_input_type: float
  quantization_output_type: uint8
  granularity: per_channel            # Optional, defaults to "per_channel".
  export_dir: quantized_models       # Optional, defaults to "quantized_models".
```

This section is used to configure the quantization process, which optimizes the model for efficient deployment on
embedded devices by reducing its memory usage (Flash/RAM) and accelerating its inference time, with minimal degradation
in model accuracy. The `quantizer` attribute expects the value `onnx_quantizer`, which is used to convert the trained
model weights from float to integer values and transfer the model to a .onnx format.

The `quantization_type` attribute only allows the value "PTQ," which stands for Post Training Quantization. To specify
the quantization type for the model input and output, use the `quantization_input_type` and `quantization_output_type`
attributes, respectively.

The `quantization_input_type` attribute is a string that can be set to "int8", "uint8," or "float" to represent the
quantization type for the model input. Similarly, the `quantization_output_type` attribute is a string that can be set
to "int8", "uint8," or "float" to represent the quantization type for the model output. 
These values are not accounted for when using `onnx_quantizer` as both model input and output types are float and only the weights and activations are quantized.

The quantization `granularity` is either "per_channel" or "per_tensor". If the parameter is not set, it will default to 
"per_channel". 'per channel' means all weights contributing to a given layer output channel are quantized with one 
unique (scale, offset) couple. The alternative is 'per tensor' quantization which means that the full weight tensor of 
a given layer is quantized with one unique (scale, offset) couple. 
It is obviously more challenging to preserve original float model accuracy using 'per tensor' quantization. But this 
method is particularly well suited to fully exploit STM32MP2 platforms HW design.

More ONNX quantization options can be found in [README_QUANTIZATION_TOOL.md](./README_QUANTIZATION_TOOL.md)

By default, the quantized model is saved in the 'quantized_models' directory under the 'experiments_outputs' directory.
You may use the optional `export_dir` attribute to change the name of this directory.

</details></ul>


<ul><details open><summary><a href="#2-10">2.10 Benchmark the model</a></summary><a id="2-10"></a>

The [STEdgeAI Developer Cloud](https://stedgeai-dc.st.com/home) allows you to benchmark your model and estimate its footprints and inference time for different STM32 target devices. To use this feature, set the `on_cloud` attribute to True. Alternatively, you can use [STEdgeAI Core](https://www.st.com/en/development-tools/stedgeai-core.html) to benchmark your model and estimate its footprints for STM32 target devices locally. To do this, make sure to add the path to the `stedgeai` executable under the `path_to_stedgeai` attribute and set the `on_cloud` attribute to False.

The `optimization` defines the optimization used to generate the C model, options: `balanced`, `time`, `ram`.

The `board` attribute is used to provide the name of the STM32 board to benchmark the model on. The available boards are 'STM32N6570-DK', 'STM32H747I-DISCO', 'STM32H7B3I-DK', 'STM32F469I-DISCO', 'B-U585I-IOT02A', 'STM32L4R9I-DISCO', 'NUCLEO-H743ZI2', 'STM32H735G-DK', 'STM32F769I-DISCO', 'NUCLEO-G474RE', 'NUCLEO-F401RE', and 'STM32F746G-DISCO'.

```yaml
tools:
  stedgeai:
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/ST/STEdgeAI/<x.y>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

benchmarking:
   board: STM32H747I-DISCO     # Name of the STM32 board to benchmark the model on
```
The `path_to_cubeIDE` attribute is for the deployment service which is not part of the chain `chain_tqeb` used in this tutorial.


</details></ul>

<ul><details open><summary><a href="#2-11">2.11 Deploy the model</a></summary><a id="2-11"></a>

In this tutorial, we are using the `chain_tqeb` toolchain, which does not include the deployment service. However, if
you want to deploy the model after running the chain, you can do so by referring to
the deployment README and modifying the `deployment_config.yaml` file or by setting the `operation_mode`
to `deploy` and modifying the `user_config.yaml` file as described below:

```yaml
model:
  model_path: <path-to-an-ONNX-QDQ-model-file>     # Path to the model file to deploy

dataset:
  class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ]

postprocessing:
  confidence_thresh: 0.5
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.5
  plot_metrics: False   # Plot precision versus recall curves. Default is False.
  max_detection_boxes: 10

tools:
  stedgeai:
    optimization: balanced
    on_cloud: True
    path_to_stedgeai: C:/ST/STEdgeAI/<x.y>/Utilities/windows/stedgeai.exe
  path_to_cubeIDE: C:/ST/STM32CubeIDE_<*.*.*>/STM32CubeIDE/stm32cubeide.exe

deployment:
  c_project_path: ../application_code/object_detection/STM32H7/
  IDE: GCC
  verbosity: 1
  hardware_setup:
    serie: STM32H7
    board: STM32H747I-DISCO
```

In the `model` section, users must provide the path to the TFlite model file that they want to deploy using
the `model_path` attribute.

The `dataset` section requires users to provide the names of the classes using the `class_names` attribute.

The `postprocessing` section requires users to provide the values for the post-processing parameters. These parameters
include the `NMS_thresh`, `confidence_thresh`, `IoU_eval_thresh`, and `max_detection_boxes`. By providing
these values in the postprocessing section, the object detection model can properly post-process the results and
generate accurate detections. It is important to carefully tune these parameters based on your specific use case to
achieve optimal performance.

The `tools` section includes information about the **stedgeai** toolchain, such as the version, optimization level, and path
to the `stedgeai.exe` file.

Finally, in the `deployment` section, users must provide information about the hardware setup, such as the series and
board of the STM32 device, as well as the input and output interfaces. Once all of these sections have been filled in,
users can run the deployment service to deploy their model to the STM32 device.

Please refer to readme below for a complete deployment tutorial:
- on H7-MCU : [README_STM32H7.md](./README_DEPLOYMENT_STM32H7.md)
- on N6-NPU : [README_STM32N6.md](./README_DEPLOYMENT_STM32N6.md)
- on MPU : [README_MPU.md](./README_DEPLOYMENT_MPU.md)

</details></ul>

<ul><details open><summary><a href="#2-12">2.12 Hydra and MLflow settings</a></summary><a id="2-12"></a>

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used
to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment
directories. In the YAML code below, it is set to save the outputs as explained in the section <a id="4">visualize the
chained services results</a>:

```yaml
hydra:
  run:
    dir: ./src/experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown
below:

```yaml
mlflow:
  uri: ./src/experiments_outputs/mlruns
```

</details></ul>
</details>
<details open><summary><a href="#3"><b>3. Run the object detection chained service</b></a></summary><a id="3"></a>

After updating the [user_config_pt.yaml](../user_config_pt.yaml) file, please run the following command:

```bash
cd stm32ai-modelzoo-services/object_detection
python ./stm32ai_main.py --config-path ./ --config-name  user_config_pt.yaml
```


</details>
<details open><summary><a href="#4"><b>4. Visualize the chained services results</b></a></summary><a id="4"></a>

Every time you run the Model Zoo, an experiment directory is created that contains all the directories and files created
during the run. The names of experiment directories are all unique as they are based on the date and time of the run.

Experiment directories are managed using the Hydra Python package. Refer to [Hydra Home](https://hydra.cc/) for more
information about this package.

By default, all the experiment directories are under the <MODEL-ZOO-ROOT>/object_detection/src/experiments_outputs
directory and their names follow the "%Y_%m_%d_%H_%M_%S" pattern.

This is illustrated in the figure below.

```
                                  experiments_outputs
                                          |
                                          |
      +-------------------+-------------------+-------------------+
      |                   |                   |                   |
      |                   |                   |                   |
    mlruns         <date-and-time>     <date-and-time>     <date-and-time> 
      |                                      |              
    MLflow                                   +--- stm32ai_main.log
    files                                    |
                                             +-----------------------------------+
                                             |                                   |
                                             |                                   |
                                        .hydra/                          <model_name>/
                                             |                                   |
                                        config.yaml                        tensorboard/
                                        hydra.yaml                         best_ckpt.pth
                                        overrides.yaml                     epoch_1_ckpt.pth
                                                                           epoch_2_ckpt.pth
                                                                           ...
                                                                           |
                                                                  quantized_models/
                                                                           |
                                                                    <model_name>_infer.onnx
                                                                    <model_name>_quant_qdq_pc.onnx
```

The file named 'stm32ai_main.log' under each experiment directory is the log file saved during the execution of the '
stm32ai_main.py' script. The contents of the other files saved under an experiment directory are described in the table
below.

|  File/Directory       |  Location | Contents               |
|:----------------------|:----------|:-----------------------|
| best_ckpt.pth | <model_name>/ | Best model checkpoint saved during training (PyTorch) |
| epoch_X_ckpt.pth | <model_name>/ | Model checkpoint saved at epoch X (PyTorch) |
| tensorboard/ | <model_name>/ | TensorBoard event files for training visualization |
| <model_name>_infer.onnx | quantized_models/ | Quantized ONNX model for inference |
| <model_name>_quant_qdq_pc.onnx | quantized_models/ | Quantized ONNX model with QDQ (Quantize-Dequantize) operators |
| config.yaml | .hydra/ | Main configuration file used for the experiment |
| hydra.yaml | .hydra/ | Hydra framework configuration |
| overrides.yaml | .hydra/ | Configuration overrides applied to this run |

All the directory names, including the naming pattern of experiment directories, can be changed using the configuration
file. The names of the files cannot be changed.

The PyTorch checkpoint files 'best_ckpt.pth' and 'epoch_X_ckpt.pth' can be used to resume a training that you interrupted or that crashed. This will be explained in the training service [README](./README_TRAINING.md). The quantized ONNX files in the 'quantized_models/' directory are ready for deployment on STM32 devices.

<ul><details open><summary><a href="#4-1">4.1 Saved results</a></summary><a id="4-1"></a>

All of the training and evaluation artifacts are saved in the current output simulation directory, which is located
at **experiments_outputs/\<date-and-time\>**.

For example, you can retrieve the confusion matrix generated after evaluating the float and the quantized model on the
test set by navigating to the appropriate directory within **experiments_outputs/\<date-and-time\>**.

</details></ul>
<ul><details open><summary><a href="#4-2">4.2 Run tensorboard</a></summary><a id="4-2"></a>

To visualize the training curves that were logged by TensorBoard, navigate to the **
experiments_outputs/\<date-and-time\>** directory and run the following command:

```bash
tensorboard --logdir logs
```

This will start a server and its address will be displayed. Use this address in a web browser to connect to the server.
Then, using the web browser, you will able to explore the learning curves and other training metrics.

</details></ul>
<ul><details open><summary><a href="#4-3">4.3 Run ClearML</a></summary><a id="4-3"></a>

ClearML is an open-source tool used for logging and tracking machine learning experiments. It allows you to record metrics, parameters, and results, making it easier to monitor and compare different runs.

Follow these steps to configure ClearML for logging your results. This setup only needs to be done once. If you haven't set it up yet, complete the steps below. If you've already configured ClearML, your results should be automatically logged and available in your session.

- Sign up for free to the [ClearML Hosted Service](https://app.clear.ml), then go to your ClearML workspace and create new credentials.

- Create a `clearml.conf` file and paste the credentials into it. If you are behind a proxy or using SSL portals, add `verify_certificate = False` to the configuration to make it work. Here is an example of what your `clearml.conf` file might look like:

    ```ini
    api {
        web_server: https://app.clear.ml
        api_server: https://api.clear.ml
        files_server: https://files.clear.ml
        # Add this line if you are behind a proxy or using SSL portals
        verify_certificate = False
        credentials {
            "access_key" = "YOUR_ACCESS_KEY"
            "secret_key" = "YOUR_SECRET_KEY"
        }
    }
  
    ```

Once configured, your experiments will be logged directly and shown in the project section under the name of your project.

</details></ul>
<ul><details open><summary><a href="#4-4">4.4 Run MLFlow</a></summary><a id="4-4"></a>

MLflow is an API that allows you to log parameters, code versions, metrics, and artifacts while running machine learning
code, and provides a way to visualize the results.

To view and examine the results of multiple trainings, you can navigate to the **experiments_outputs** directory and
access the MLflow Webapp by running the following command:

```bash
mlflow ui
```

This will start a server and its address will be displayed. Use this address in a web browser to connect to the server.
Then, using the web browser, you will be able to navigate the different experiment directories and look at the metrics
they were collected. Refer to [MLflow Home](https://mlflow.org/) for more information about MLflow.

</details></ul>
</details>
<details open><summary><a href="#A"><b>5. Appendix A: YAML syntax</b></a></summary><a id="A"></a>

**Example and terminology:**

An example of YAML code is shown below.

```yaml
preprocessing:
  rescaling:
    scale: 1/127.5
    offset: -1
  resizing:
    aspect_ratio: fit
    interpolation: nearest
```

The code consists of a number of nested "key-value" pairs. The column character is used as a separator between the key
and the value.

Indentation is how YAML denotes nesting. The specification forbids tabs because tools treat them differently. A common
practice is to use 2 or 3 spaces but you can use any number of them.

We use "attribute-value" instead of "key-value" as in the YAML terminology, the term "attribute" being more relevant to
our application. We may use the term "attribute" or "section" for nested attribute-value pairs constructs. In the
example above, we may indifferently refer to "preprocessing" as an attribute (whose value is a list of nested
constructs) or as a section.

**Comments:**

Comments begin with a pound sign. They can appear after an attribute value or take up an entire line.

```yaml
preprocessing:
  rescaling:
    scale: 1/127.5   # This is a comment.
    offset: -1
  resizing:
    # This is a comment.
    aspect_ratio: fit
    interpolation: nearest
  color_mode: rgb
```

**Attributes with no value:**

The YAML language supports attributes with no value. The code below shows the alternative syntaxes you can use for such
attributes.

```yaml
attribute_1:
attribute_2: ~
attribute_3: null
attribute_4: None     # Model Zoo extension
```

The value *None* is a Model Zoo extension that was made because it is intuitive to Python users.

Attributes with no value can be useful to list in the configuration file all the attributes that are available in a
given section and explicitly show which ones were not used.

**Strings:**

You can enclose strings in single or double quotes. However, unless the string contains special YAML characters, you
don't need to use quotes.

This syntax:

```yaml
resizing:
  aspect_ratio: fit
  interpolation: nearest
```

is equivalent to this one:

```yaml
resizing:
  aspect_ratio: "fit"
  interpolation: "nearest"
```

**Strings with special characters:**

If a string value includes YAML special characters, you need to enclose it in single or double quotes. In the example
below, the string includes the ',' character, so quotes are required.

```yaml
name: "Pepper,_bell___Bacterial_spot"
```

**Strings spanning multiple lines:**

You can write long strings on multiple lines for better readability. This can be done using the '|' (pipe) continuation
character as shown in the example below.

This syntax:

```yaml
LearningRateScheduler:
  schedule: |
    lambda epoch, lr:
        (0.0005*epoch + 0.00001) if epoch < 20 else
        (0.01 if epoch < 50 else
        (lr / (1 + 0.0005 * epoch)))
```

is equivalent to this one:

```yaml
LearningRateScheduler:
  schedule: "lambda epoch, lr: (0.0005*epoch + 0.00001) if epoch < 20 else (0.01 if epoch < 50 else (lr / (1 + 0.0005 * epoch)))"
```

Note that when using the first syntax, strings that contain YAML special characters don't need to be enclosed in quotes.
In the example above, the string includes the ',' character.

**Booleans:**

The syntaxes you can use for boolean values are shown below. Supported values have been extended to *True* and *False*
in the Model Zoo as they are intuitive to Python users.

```yaml
# YAML native syntax
attribute_1: true
attribute_2: false

# Model Zoo extensions
attribute_3: True
attribute_4: False
```

**Numbers and numerical expressions:**

Attribute values can be integer numbers, floating-point numbers or numerical expressions as shown in the YAML code
below.

```yaml
dataset:
seed: 123
  random_size: [10, 20] # list
  mosaic_prob: 0.5  # float
  degrees: 10  # integer

rescaling:
  scale: 1/127.5  # Numerical expression, evaluated to 0.00784314
  offset: -1
```

**Lists:**

You can specify lists on a single line or on multiple lines as shown below.

This syntax:

```yaml
class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ]
```

is equivalent to this one:

```yaml
class_names:
  - aeroplane
  - bicycle
  - bird
  - sunflowers
  - boat ...

```

**Multiple attribute-value pairs on one line:**

Multiple attribute-value pairs can be specified on one line as shown below.

This syntax:

```yaml
rescaling: { scale: 1/127.5, offset: -1 }
```

is equivalent to this one:

```yaml
rescaling:
  scale: 1/127.5
  offset: -1
```

</details>
