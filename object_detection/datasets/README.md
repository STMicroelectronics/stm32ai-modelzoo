# <a>Object detection STM32 model zoo</a>

## <a>Directory components</a>

This is a placeholder for object detection datasets.
This also includes some useful tools to process those datasets:
- `dataset_converter` : This tool converts datasets in COCO or Pascal VOC format to YOLO Darknet format. YOLO Darknet is the format used in the other tools below as well as in the object detection model zoo services.
- `dataset_analysis` : This tools analyzes the distribution of the dataset (classes and labels), and should be used before creating the .tfs files
- `dataset_create_tfs` : this tools creates .tfs files from the dataset used in order to have a faster training. It is needed to generate the .tfs before running the training through the training operation mode.
