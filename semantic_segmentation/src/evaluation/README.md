# Evaluation of semantic segmentation model

Our evaluation service is a comprehensive tool that enables users to assess the accuracy of their TensorFlow Lite (.tflite), Keras (.h5) or ONNX (.onnx) semantic segmentation model. 
However, we only support channel first ONNX model so far.
By uploading their model and a evaluation set (validation or test), users can quickly and easily estimate the performance of their model and generate various metrics, in particular accuracy and average IoU.

The evaluation service is designed to be fast, efficient, and accurate, making it an essential tool for anyone looking to evaluate the performance of their semantic segmentation model.

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Configure the yaml file</b></a></summary><a id="1"></a>

To use this service and achieve your goals, you can use the [user_config.yaml](../user_config.yaml) or directly update the [evaluation_config.yaml](../config_file_examples/evaluation_config.yaml) file and use it. This file provides an example of how to configure the evaluation service to meet your specific needs.

Alternatively, you can follow the tutorial below, which shows how to evaluate your pre-trained semantic segmentation model using our evaluation service.

<ul><details open><summary><a href="#1-1">1.1 Set the model and the operation mode</a></summary><a id="1-1"></a>

As mentioned previously, all the sections of the YAML file must be set in accordance with this **[evaluation_config.yaml](../config_file_examples/evaluation_config.yaml)**.
In particular, `operation_mode` should be set to evaluation and the `evaluation` section should be filled as in the following example: 

```yaml
general:
   model_path: ../pretrained_models/deeplab_v3/ST_pretrainedmodel_public_dataset/pascal_voc_coco_2012/deeplab_v3_mobilenetv2_05_16_512_fft/deeplab_v3_mobilenetv2_05_16_512_fft.h5

operation_mode: evaluation
```
The path to the deeplab_v3 model is provided in the `model_path` parameter.

</details></ul>
<ul><details open><summary><a href="#1-2">1.2 Prepare the dataset</a></summary><a id="1-2"></a>

Information about the dataset you want use for evaluation is provided in the `dataset` section of the configuration file, as shown in the YAML code below.

```yaml
dataset:
   name: pascal_voc   # Dataset name. Mandatory. Only 'pascal_voc' is supported for the time being
   test_path: ../datasets/VOC2012_train_val/JPEGImages                              # Path to directory containing the images of the test set.
   test_masks_path: ../datasets/VOC2012_train_val/SegmentationClassAug             # Path to directory containing the masks of the test set
   test_files_path: ../datasets/VOC2012_train_val/ImageSets/Segmentation/val.txt    # Path to file containing the list of images names to be considered in 'test_path' and 'test_mask_path' for test set 
   check_image_files: False   # Enable/disable image file checking.
```

When working with a dataset for the first time, we suggest setting the `check_image_files` attribute to True. This will enable the system to load each image file and identify any corrupt, unsupported, 
or non-image files. The path to any problematic files will be reported.

The service first seeks for a test set specification defined by `test_path`, `test_masks_path` and `test_files_path` parameters. If no test set is specified, the data loader checks if a validation set is 
specified either by the parameters `validation_path`, `validation_masks_path`, `validation_files_path` or alternatively by `training_path`, `training_masks_path`, `validation_files_path`. 
In the latest, it has to be verified that no images in the `validation_files_path` list of names belongs to the set of images used for training, otherwise there will be an over-estimation of accuracy and IoU.

To finish, in case there is no validation set or test set properly specified, the available data under the `training_path` directory is randomly split into two to create a training set and a validation set. 
By default, 80% of the data is used for training and the remaining 20% is used for the validation set in the evaluation service.
If you want to use a different split ratio, you need to specify the percentage to be used for the validation set in the `validation_split` parameter (to ensure consistency in the [training](../training/README.md) and 
evaluation process, you must specify the same `validation_split` parameter value in both the training and evaluation services), as shown in the YAML example below:

```yaml
dataset:
   name: pascal_voc
   class_names: ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
                "car", "cat", "chair", "cow", "dining table", "dog", "horse", "motorbike",
                "person", "potted plant", "sheep", "sofa", "train", "tv/monitor"]
   training_path: ../datasets/VOC2012_train_val/JPEGImages                                 # Path to train jpeg images
   training_masks_path: ../datasets/VOC2012_train_val/SegmentationClassAug                 # Path to train masks files
   training_files_path: ../datasets/VOC2012_train_val/ImageSets/Segmentation/trainaug.txt  # Path to file listing the images names for training
   validation_path:
   validation_split: 0.20
   test_path:
```

</details></ul>
<ul><details open><summary><a href="#1-3">1.3 Apply preprocessing</a></summary><a id="1-3"></a>

The images from the dataset need to be preprocessed before they are presented to the network for evaluation.
This includes rescaling and resizing. In particular, they need to be rescaled exactly as they were at training step.
This is illustrated in the YAML code below:

```yaml
preprocessing:
   rescaling: { scale: 1/127.5, offset: -1 }
   resizing: 
     aspect_ratio: "fit"
     interpolation: bilinear
  color_mode: rgb
```

In this example, the pixels of the input images read in the dataset are in the interval [0, 255], that is UINT8. If you set `scale` to 1./255 and `offset` to 0, they will be rescaled to the interval [0.0, 1.0]. 
If you set `scale` to 1/127.5 and `offset` to -1, they will be rescaled to the interval [-1.0, 1.0].

The `resizing` attribute specifies the image resizing methods you want to use:
- The value of `interpolation` must be one of *{"bilinear", "nearest", "bicubic", "area", "lanczos3", "lanczos5", "gaussian", "mitchellcubic"}*.
- The value of `aspect_ratio` must be either *"fit"* or *"crop"*. If you set it to *"fit"*, the resized images will be distorted if their original aspect ratio is not the same as in the resizing size. 
If you set it to *"crop"*, images will be cropped as necessary to preserve the aspect ratio.

The `color_mode` attribute must be one of "*grayscale*", "*rgb*" or "*rgba*".

</details></ul>
<ul><details open><summary><a href="#1-4">1.4 Hydra and MLflow settings</a></summary><a id="1-4"></a>

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
<details open><summary><a href="#2"><b>2. Evaluate your model</b></a></summary><a id="2"></a>

If you chose to modify the [user_config.yaml](../user_config.yaml) you can evaluate the model by running the following command from the **src/** folder:

```bash
python stm32ai_main.py 
```
If you chose to update the [evaluation_config.yaml](../config_file_examples/evaluation_config.yaml) and use it then run the following command from the **src/** folder: 

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name evaluation_config.yaml
```
In case you want to evaluate the accuracy of the quantized model then benchmark it, you can either launch the evaluation operation mode followed by the [benchmark service](../benchmarking/README.md) that describes in details how to proceed or you can use chained services like launching **[chain_eqeb](../config_file_examples/chain_eqeb_config.yaml)** example with command below:

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name chain_eqeb_config.yaml
```

</details>
<details open><summary><a href="#3"><b>3. Visualize the evaluation results</b></a></summary><a id="3"></a>

There is no specific plots available for semantic segmentation evaluation. The service only reports the accuracy and the average IoU.
Both metrics include the contribution of the "background" class.

The accuracy estimates how well pixels are classified by comparing network output with ground truth mask. It is the ratio of well classified pixels (whatever the class) over the number of pixels within the image.
This calculation is done on each image and then averaged over the full evaluation set.

IoU (Intersection over Union) is a popular metric for segmentation that estimates how much network prediction and ground truth mask overlap. In accordance with its name,
it is the ratio between prediction and ground truth intersection (in pixels) over prediction and ground truth union (in pixels).
The IoU we report is already averaged on all classes and all images of the evaluation set.

Both accuracy and IoU will be displayed on your screen and then saved in the log file **stm32ai_main.log** under **experiments_outputs/\<date-and-time\>**.

</details>
