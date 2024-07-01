# <a>Dataset create TFS</a>

TFS stands for TensorFlow Strings.
`dataset_create_tfs.py` tool creates .tfs files corresponding to serialized tensors padded labels. These files are used in place of .txt files that contain ground truth information, in order to have a more efficient (faster training).

In the yaml file, it takes as input some dataset path and `max_detections` parameter provided by the user. This parameter may be extracted after running the dataset_analysis.py tool.

## <a>Example</a>

```yaml
dataset:
  dataset_name: Pascal_VOC_2007
  training_path: ../<dataset_name>/train
  validation_path: ../<dataset_name>/val
  test_path: ../<dataset_name>/test

settings:
  max_detections: 20
```

In example above Pascal_VOC_2007 will be analyzed, and :
- training, validation and test set will have .tfs files created for future training
- The max number of detections allowed per image is set (to 20 here) so only images with 20 detections or less will have their .tfs file created, and will bu used for the training and evaluation then.

Please not that:
- training_path is required while validation_path and test_path may remain empty if they don't exist.
- if max_detections value is not provided, the dataset will be analyzed and all the .tfs will be created (no filtering)

You can run the script from current directory with the following command:

```bash
python dataset_create_tfs.py
```
Or in case you launch it from another directory (example from object_detection/datasets):
```bash
python dataset_create_tfs.py --config-path ./dataset_analysis/ --config-name dataset_config.yaml
```

In example above Pascal_VOC_2007 will be analyzed, and training, validation and test set folders will have .tfs created for all images containing 20 or less detections each.

