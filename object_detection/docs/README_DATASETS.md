# <a>Object detection STM32 model zoo</a>

Before you start using this project, it's important to understand the supported dataset names and formats. Please note that for all the training, evaluation and quantization services, it is expected to have a dataset in TFS Tensorflow format. For the object detection use case, the `get_dataset` API call takes care of the conversion of your dataset automatically depending on the `dataset_name` and `format` attributes.

The `dataset` section and its attributes are shown in the YAML code below.

```yaml
dataset:
  format: pascal_voc
  dataset_name: pascal_voc                                    # Dataset name. Defaults to "<unnamed>".
  class_names: [ aeroplane,bicycle,bird,boat,bottle,bus,car,cat,chair,cow,diningtable,dog,horse,motorbike,person,pottedplant,sheep,sofa,train,tvmonitor ] # Names of the classes in the dataset.
  data_dir: ./datasets/pascal_voc/tmp/                       # Path to the tmp directory before the split.
  train_images_path: /local/datasets/VOC0712/JPEGImages/     # Path to the root directory of the img before split.
  train_xml_dir: /local/datasets/VOC0712/Annotations         # Path to the root directory of the xml annotations
  training_path: <training-set-root-directory>               # Path to the root directory of the training set.
  validation_path: <validation-set-root-directory>           # Path to the root directory of the validation set.
  validation_split: 0.2                                      # Training/validation sets split ratio.
  test_path: <test-set-root-directory>                       # Path to the root directory of the test set.
  quantization_path: <quantization-set-root-directory>       # Path to the root directory of the quantization set.
  quantization_split:                                        # Quantization split ratio.
  seed: 123                                                  # Random generator seed used when splitting a dataset.
```

The `dataset_name` attribute is required and serves to specify the dataset you are using. This can be a well-known dataset like coco, pascal_voc, or a custom_dataset if you have your own data and it follows the logic below:

| Dataset Name     | Allowed Formats          | Description                                                                                  |
|------------------|-------------------------|----------------------------------------------------------------------------------------------|
| `coco`           | `coco`, `tfs`           | Native COCO format or TFS TensorFlow format                                                     |
| `pascal_voc`     | `pascal_voc`, `tfs`     | Native Pascal VOC format or TFS TensorFlow format                                               |
| `darknet_yolo`   | `darknet_yolo`, `tfs`   | Native Darknet YOLO format or TFS TensorFlow format                                             |
| `custom_dataset` | `tfs`                   | Only TFS TensorFlow format; in case the dataset is already converted before evaluation                          |

Depending on the `dataset_name`, the dataset loader will check the `format` to determine if it is necessary to convert the dataset to the final **TFS TensorFlow format**. These two parameters are mandatory if the operation mode is **training**, **evaluation** and **quantization**.

The `format` attributes defines the annotation format of your dataset. This must match the format of your dataset annotations. 
It serves to check whether your dataset is in its original format or in TFS TensorFlow format. 
This determines whether it is needed to convert the dataset to the required TFS format or not. It accepts the following values: 

  * `tfs`: If the dataset is a TensorFlow Object Detection API format.
  * `coco`: If the dataset is in COCO dataset format (JSON annotations).
  * `pascal_voc`: If the dataset is in Pascal VOC XML annotation format.
  * `darknet_yolo`: If the dataset is in YOLO Darknet text file annotations.

Depending on the `format` value, some additional attributes should be defined in the dataset section:
- If the `format` is set to **coco**, the following attributes should be set:
  * The `data_dir`: Required, refers to the temporary path where the TFS files will be generated.
  * The `train_images_path`: Required, refers to the path of the training subset directory where the images are located.
  * The `train_annotations_path`: Required, refers to the path of the training subset json file of the annotations.
  * The `val_images_path`: Optional, refers to the path of the validation subset directory where the images are located.
  * The `val_annotations_path`: Optional, refers to the path of the training subset json file of the annotations.

- If the `format` is set to **pascal_voc**, the following attributes should be set:
  * The `data_dir`: Required, refers to the temporary path where the TFS files will be generated.
  * The `train_images_path`: Required, refers to the path of the training subset directory where the images are located.
  * The `train_xml_dir`: Required, refers to the path of the training subset directory containing the xml files of the annotations.
  * The `val_images_path`: Optional, refers to the path of the validation subset directory where the images are located.
  * The `val_xml_dir`: Optional, refers to the path of the training subset directory containing the xml files of the annotations.

- If the `format` is set to **darknet_yolo**, the following attributes should be set:
  * The `data_dir`: Required, refers to the path of the directory containing the txt files of the annotations along with the images.


The state machine below describes the process of dataset loading for object detection use case.


```
                                                   dataset_name
                                                         |
                                                         |
        +----------------------------------+--------------------------+-------------------------------+
        |                                  |                          |                               |
        |                                  |                          |                               |
      coco                           pascal_voc              darknet_yolo                "custom_dataset"
        |                                  |                          |                               |
        |                                  |                          |                               |
  +-----+------------+           +-----+-----------+          +-------+-------+               +-------+-------+ 
  |                  |           |                 |          |               |               |               |
supported        unsupported    supported    unsupported   supported     unsupported      supported      unsupported        
 format:           format        format         format      format:        format           format         format
      |                             |                           |                             |
  +---+-----+                   +---+---+                  +----+-----+                       |
  |         |                   |       |                  |          |                       |
 coco      tfs             pascal_voc  tfs            darknet_yolo   tfs                     tfs
  |         |                   |       |                  |          |                (Custom dataset
  |         |                   |       |                  |          |                 should be used
  |         |                   |       |                  |          |                if the conversion
  |   dataset.format=tfs        |  dataset.format=tfs      |    dataset.format=tfs     has already been
  |   (already TFS)             |    (already TFS)         |      (already TFS)        done in a previous
  |         |                   |       |                  |          |                training or eval)
  |         |                   |       |                  |          |                       |
  |   load TFS directly         |   load TFS directly      |      load TFS directly      load TFS directly
  |                             |                          |                                  |
  |                             |                          |                                  |
dataset.format=coco     dataset.format=pascal_voc      dataset.format=darknet_yolo            |
(needs conversion)         (needs conversion)             (needs conversion)                  |
        |                         |                               |                           |
        v                         v                               v                           |
convert coco to tfs      convert pascal_voc to tfs     convert darknet yolo to tfs            |
        |                         |                               |                           |
        +-------------------------+-------------------------------+---------------------------+
                                                |
                                        Dataset in TFS format
                                            (used for)
                          +---------------------+-----------------------+
                          |                     |                       |
                      training             evaluation             quantization

```

## Dataset Configuration

### Details of Required / Optional Attributes per `(dataset_name, format)`

---

### 1. `dataset_name = coco`

**Supported `format` values:**

- `tfs`
- `coco`

#### 1.a `format = tfs`

- Dataset is already in **TFS TensorFlow** format.
- Loader reads TFS files directly.

**Required attributes**

- `data_dir`  
  → Temporary path where the TFS files are located.

---

#### 1.b `format = coco`

- Dataset is in **COCO JSON** annotation format and must be converted to TFS.

**Required attributes**

- `data_dir`  
  → Temporary path where the TFS files will be generated.
- `train_images_path`  
  → Path to training images directory.
- `train_annotations_path`  
  → Path to training subset COCO JSON annotations file.

**Optional attributes**

- `val_images_path`  
  → Path to validation images directory.
- `val_annotations_path`  
  → Path to validation subset COCO JSON annotations file.

**Conversion flow**

1. Read images/annotations from `train_*` (and optionally `val_*`).
2. Generate TFS TensorFlow records into `data_dir`.
3. Load resulting TFS dataset for training / evaluation / quantization with the specified split ratios.

---

### 2. `dataset_name = pascal_voc`

**Supported `format` values:**

- `tfs`
- `pascal_voc`

#### 2.a `format = tfs`

- Dataset is already in **TFS TensorFlow** format.
- Loader reads TFS files directly.

**Required attributes**

- `data_dir`  
  → Temporary path where the TFS files are located.

---

#### 2.b `format = pascal_voc`

- Dataset is in **Pascal VOC XML** annotation format and must be converted.

**Required attributes**

- `data_dir`  
  → Temporary path where the TFS files will be generated.
- `train_images_path`  
  → Path to training images directory.
- `train_xml_dir`  
  → Path to directory containing training XML annotation files.

**Optional attributes**

- `val_images_path`  
  → Path to validation images directory.
- `val_xml_dir`  
  → Path to directory containing validation XML annotation files.

**Conversion flow**

1. Read images/annotations from `train_*` (and optionally `val_*`).
2. Generate TFS TensorFlow records into `data_dir`.
3. Load resulting TFS dataset for training / evaluation / quantization.

---

### 3. `dataset_name = darknet_yolo`

**Supported `format` values:**

- `tfs`
- `darknet_yolo`

#### 3.a `format = tfs`

- Dataset is already in **TFS TensorFlow** format.
- Loader reads TFS files directly.

**Required attributes**

- `data_dir`  
  → Temporary path where the TFS files are located.

---

#### 3.b `format = darknet_yolo`

- Dataset is in **YOLO Darknet text** annotation format and must be converted.

**Required attributes**

- `data_dir`  
  → Path to the directory containing:
  - the `.txt` annotation files
  - the corresponding images

> No separate train/val split paths are specified. By convention, `data_dir` contains both the `.txt` files and images to be converted.

**Conversion flow**

1. Parse YOLO `.txt` annotations and corresponding images in `data_dir`.
2. Generate TFS TensorFlow records.
3. Load resulting TFS dataset for training / evaluation / quantization.

---

### 4. `dataset_name = "custom_dataset"`

**Supported `format` values:**

- `tfs`

This case assumes:

- The user has already produced a **TFS TensorFlow dataset** externally or from a previous operation.
- The loader only reads the TFS dataset (no conversion is performed).

**Required / optional attributes**

- Depend on your custom TFS dataset layout (not defined here).
- At minimum, paths pointing to the TFS TFRecord files (train/val) must be provided according to the specific tool’s configuration schema.

---

### Operation Modes and Mandatory Parameters

For the following operation modes:

- `training`
- `evaluation`
- `quantization`

The following parameters are **mandatory**:

- `dataset_name`
- `format`