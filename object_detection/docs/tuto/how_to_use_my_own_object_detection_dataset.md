# How to use my own object detection dataset?

To use your own dataset with ST Model Zoo object detection scripts, you need to have a dataset in one of the following formats: 
- **yolo_darknet**: Text files with normalized bounding box coordinates per image, paired with class IDs.
- **coco**: A single JSON file containing image info, object annotations with absolute bounding boxes, and category definitions.
- **pascal_voc**: One XML file per image describing objects with absolute bounding box coordinates and class names.
- **tfs**: TFRecord files containing serialized images and annotations formatted for TensorFlow Serving and detection APIs.

The dataloader API calls take care of the conversion of all the dataset formats to create .tfs files from the dataset used in order to have a faster training. It is needed to generate the .tfs before running the training through the training operation mode.

## Example:

### Convert the dataset

#### Case 1: COCO Format dataset
If you have a COCO format dataset, the dataset_name attribute should be set to coco and the format should also be set to coco. You must set:

train_images_path: directory containing your training images
train_annotations_path: COCO .json file containing the training annotations
data_dir: a temporary directory which will host the converted TFS TensorFlow dataset
Optionally, you can also provide the validation subset (val_images_path, val_annotations_path).

```` yaml
dataset:
  format: coco
  class_names: [person]
  dataset_name: coco
  exclude_unlabeled: true
  download_data: false
  max_detections: 20

  data_dir: ./datasets/COCO_2017_person/tmp/coco_like/

  train_images_path: /local/data/OD_datasets/COCO/train2017
  train_annotations_path: /local/data/OD_datasets/COCO/annotations/person_keypoints_train2017.json

  val_images_path: /local/data/OD_datasets/COCO/val2017
  val_annotations_path: /local/data/OD_datasets/COCO/annotations/person_keypoints_val2017.json

````
#### Case 2: Pascal VOC Format dataset
If your dataset is in Pascal VOC format (one XML file per image), the dataset_name must be pascal_voc and the format must also be pascal_voc. The dataloader will then convert your VOC annotations into TFS TensorFlow format.

You must set:

* `data_dir`: temporary directory where the converted TFS files will be generated
* `train_images_path`: directory containing your training images
* `train_xml_dir`: directory containing the training XML annotation files

You can optionally also specify validation paths:

* ``val_images_path`: directory containing your validation images
* ``val_xml_dir`: directory containing the validation XML annotation files

Example:

```` yaml
dataset:
  format: pascal_voc
  class_names: [person, car, bicycle]
  dataset_name: pascal_voc
  exclude_unlabeled: true
  download_data: false
  max_detections: 50

  # Temporary directory for generated TFS files
  data_dir: ./datasets/VOC_custom/tmp/tfs/

  # Training subset
  train_images_path: /local/data/OD_datasets/VOC_custom/JPEGImages/train
  train_xml_dir: /local/data/OD_datasets/VOC_custom/Annotations/train

  # Validation subset (optional)
  val_images_path: /local/data/OD_datasets/VOC_custom/JPEGImages/val
  val_xml_dir: /local/data/OD_datasets/VOC_custom/Annotations/val
````
When you run the training (or evaluation/quantization) command with this configuration, the pipeline will:

1. Read images from train_images_path (and val_images_path if provided).
2. Read XML annotations from train_xml_dir (and val_xml_dir if provided).
3. Generate .tfs TFRecord files under data_dir.
4. Use these .tfs files for the actual training/evaluation/quantization.

#### Case 3: YOLO Darknet Format dataset
If your dataset is in YOLO Darknet format (one .txt annotation file per image with normalized bounding boxes), the dataset_name must be darknet_yolo and the format must also be darknet_yolo.

For this case, the loader expects a single root directory containing both images and their corresponding YOLO .txt files:

* `data_dir`: directory containing the images and YOLO .txt annotation files
Within data_dir, a typical pattern is:
```
image_0001.jpg
image_0001.txt
image_0002.jpg
image_0002.txt
```
…
Example:

````yaml
dataset:
  format: darknet_yolo
  class_names: [person, car, bicycle]
  dataset_name: darknet_yolo
  exclude_unlabeled: true
  download_data: false
  max_detections: 50

  # Root directory containing images + YOLO .txt annotations
  data_dir: /local/data/OD_datasets/YOLO_custom/
````

With this configuration, the dataloader will:

1. Parse all images and .txt annotation files found under data_dir.
2. Convert YOLO bounding boxes and class IDs into the internal TFS TensorFlow representation.
3. Generate .tfs TFRecord files under a tool‑managed temporary folder (or within data_dir, depending on implementation).
4. Use these .tfs files for training/evaluation/quantization.

#### Case 4: Dataset already in TFS (TFRecord) format
If you already have a dataset converted to the TFS TensorFlow format compatible with the ST Model Zoo (for example, you previously ran a conversion step, or you generated it with your own tools), you can skip the conversion.

In this case:
Format must be tfs, dataset_name depends on your pipeline, for example:
reuse a known name like coco, pascal_voc, darknet_yolo if it follows the same class ordering and semantics, or use custom_dataset if it is a fully custom dataset.
You then directly point to the existing TFS directory and its TFRecord files (the exact keys may depend on your tooling; typically you at least specify data_dir and possibly separate train/val TFRecord paths if required).

Example (generic):

```` yaml
dataset:
  format: tfs
  class_names: [person, car, bicycle]
  dataset_name: custom_dataset
  exclude_unlabeled: true
  download_data: false
  max_detections: 50

  # Directory where your pre-generated .tfs TFRecords are stored
  data_dir: /local/data/OD_datasets/custom_tfs/
````

In this configuration, no additional conversion is done. The training/evaluation/quantization scripts directly read the TFS TensorFlow records.

