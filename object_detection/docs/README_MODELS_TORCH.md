# Overview of PyTorch STM32 Model Zoo for Object Detection

The STM32 model zoo includes several PyTorch-based models for object detection use cases, converted to ONNX format and optimized for STM32N6 NPU deployment. All models are pre-trained on ImageNet and quantized using QDQ INT8 quantization.

## Model Categories

- `ST_pretrainedmodel_public_dataset` contains  PyTorch object detection models pretrained by ST on open source datasets such as MS COCO, Pascal VOC, COCO person and converted to ONNX format with QDQ quantization.

**Explore the complete PyTorch model zoo with pre-trained models optimized for STM32N6.**

## Model Families

You can get comprehensive footprints and performance information for each model family following the links below:

### Single Shot Detector (SSD) Models
Variation of SSD models using different backbone and heads
- [ssd_mobilenetv1_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/ssd_mobilenetv1_pt/README.md) – Single shot detector with MobilenetV1 backbone 
- [ssd_mobilenetv2_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/ssd_mobilenetv2_pt/README.md) – Single shot detector with MobilenetV2 backbone 
- [ssdlite_mobilenetv1_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/ssdlite_mobilenetv1_pt/README.md) – Single shot detector lite with MobilenetV1 backbone 
- [ssdlite_mobilenetv2_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/ssdlite_mobilenetv2_pt/README.md) – Single shot detector lite with MobilenetV2 backbone 
- [ssdlite_mobilenetv3mall_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/ssdlite_mobilenetv3mall_pt/README.md) – Single shot detector lite with MobilenetV3small backbone 
- [ssdlite_mobilenetv3large_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/ssdlite_mobilenetv3large_pt/README.md) – Single shot detector lite with MobilenetV3large backbone 

### ST_YOLOD Models
STMicroelectronics in house developed model especially optimized for size and memory with a competitive performance on Imagenet (and other datasets)
- [st_yolodv2milli_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/st_yolodv2milli_pt/README.md) – Extreme compression of STResNet for backbone and YOLOX head and modified YOLOX neck.  
- [st_yolodv2tiny_pt](https://github.com/STMicroelectronics/stm32ai-modelzoo/blob/master/object_classification/st_yolodv2tiny_pt/README.md) – Extreme compression of STResNet for backbone and YOLOX head and modified YOLOX neck. 

**Feel free to explore the model zoo and get pre-trained models [here](https://github.com/STMicroelectronics/stm32ai-modelzoo/tree/master/object_detection/).**
For training and deployment guidance, refer to the STM32 AI model zoo documentation.
