# <a xid="">Yolo Darknet Dataset Converter</a>

`converter.py` converts datasets in COCO or Pascal VOC format to YOLO Darknet format. It currently supports the following formats:
- COCO
- Pascal VOC


## <a>Example</a>

 Suppose we have a dataset in COCO format, you can use the following configuration:

```
dataset:
  format: coco_format
  class_names: [black-knight,black-pawn,black-queen,black-rook,white-bishop]

coco_format:
  images_path: ../chess_coco/train
  json_annotations_file_path: ../train/_annotations_coco.json
  export_dir: subset_chess/train
```
For Pascal VOC it should look like this:
```
dataset:
  format: pascal_voc_format
  class_names: [black-knight,black-pawn,black-queen,black-rook,white-bishop]
  
pascal_voc_format:
  images_path: ../pascal_voc_valid/VOCdevkit/VOC2007/JPEGImages
  xml_files_path: ../pascal_voc_valid/VOCdevkit/VOC2007/Annotations
  export_dir: subset_chess/train

```

Finally to convert this dataset to Yolo Darknet TXT format, run the script with the following command:

```
python converter.py dataset_config.yaml
```

The converted dataset will be saved in the `subset_chess/train` directory.