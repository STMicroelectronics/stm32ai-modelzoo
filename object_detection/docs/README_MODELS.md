# Overview of object detection STM32 model zoo


The STM32 model zoo includes several models for object detection use case pre-trained on custom and public datasets.
Under each model directory, you can find the following model categories:

- `Public_pretrainedmodel_public_dataset` contains public object detection models trained on public datasets.
- `ST_pretrainedmodel_custom_dataset` contains different object detection models trained on ST custom datasets using our [training scripts](../tf/src/training). 
- `ST_pretrainedmodel_public_dataset` contains different object detection models trained on various public datasets following the [training section](./README_TRAINING.md) in STM32 model zoo.

**Feel free to explore the model zoo and get pre-trained models [here](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/master/object_detection/).**


## Model Families

You can get comprehensive footprints and performance information for each model family following the links below. 

### STMicroelectronics In-house Model
- [st_yololcv1](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/st_yololcv1/README.md) - This is an in-house optimized version of the tiny YOLO v2 object detection algorithm. It was optimized in-house to work well on embedded devices with limited computational resources.
- [st_yoloxn](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/st_yoloxn/README.md) - Unlike its predecessors, YOLOX can adopt an anchor-free approach, which simplifies the model and enhances its accuracy. It also incorporates advanced techniques such as decoupled head structures for classification and localization, and a more efficient training strategy. YOLOX is designed to achieve high accuracy and speed, making it suitable for real-time applications in various computer vision tasks. This ST variant embeds various tuning capabilities from the yaml configuration file.

### Standard Architectures
- [yolov2t](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/yolov2t/README.md) - This is a lightweight version of the original YOLO (You Only Look Once) object detection algorithm targetting embedded devices with limited computational resources.
- [yolov8n](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/yolov8n/README.md) - This is an advanced object detection model from Ultralytics that builds upon the strengths of its predecessors in the YOLO series. YOLOv8 incorporates state-of-the-art techniques such as improved backbone networks, better feature pyramid networks, and advanced anchor-free detection heads, making it highly efficient for various computer vision tasks.
- [yolov11n](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/yolov11n/README.md) - This is an even more recent variant of the YOLO family from Ultralytics. Topology is improved for efficiency, speed, accuracy with lower number of parameters.
- [face_detect_front](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_detection/facedetect_front/README.md) - BlazeFace Front 128x128 is a lightweight and efficient variant of the BlazeFace architecture, designed specifically for detecting frontal faces at a resolution of 128x128 pixels

- `yolov4` - Version 4 from Nvidia TAO train adapt and optimize toolkit with different possible backbones for feature extractions including different versions of resnet, mobilenet, darknet, efficientnet, vgg, and cspdarknet
- `yolov4t` - Version 4 __tiny__ from Nvidia TAO train adapt and optimize toolkit with backbones csp_darknet_tiny as the backbone

To get started, update the [user_config.yaml](../user_config.yaml) file, which specifies the parameters and configuration options for the services you want to use. The  `model` section of this YAML specifically relates to the model definition. Some topologies are already registered and can be accessed by the `model_type` and `model_name` attribute. 

The exhaustive list of `model_type` and corresponding `model_name` attributes currently supported for the object detection are listed herafter. 

|`model_type`           | possible `model_name`| 
|-----------------------|----------------------|
| `yolov8n`             | X         |
| `yolov11n`            | X         |
| `yolov5u`             | X         |
| `st_yoloxn`           | `st_yoloxn`, `st_yoloxn_d033_w025`, `st_yoloxn_d100_w025`, `st_yoloxn_d050_w040`        |
| `st_yololcv1`         | `st_yololcv1`|
| `yolov2t`             |  `yolov2t`   |
| `yolov4`              | X            |
| `yolov4t`             | X            |
| `face_detect_front`   | X            |

When no `model_name` attribute is possible, `model_path` is to be used.

**Feel free to explore the model zoo and get pre-trained models [here](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/master/object_detection/).**
For training and deployment guidance, refer to the STM32 AI model zoo documentation.