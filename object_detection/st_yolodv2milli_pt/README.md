# **STYOLOMilli**

## **Use case** : `Object detection`

## **Model description**

STYOLOMilli is a **compact and efficient object detection model** designed for deployment on **resource‑constrained hardware** such as microcontroller units (MCUs) and neural processing units (NPUs). It is part of the STYOLO family introduced alongside STResNet in the paper [STResNet & STYOLO: A New Family of Compact Classification and Object Detection Models for MCUs](https://arxiv.org/abs/2601.05364).

The model builds on a highly compressed backbone derived from the STResNet design and integrates it within a YOLOX‑style architecture optimized for low memory usage, high efficiency, and competitive accuracy. STYOLOMilli delivers strong object detection performance (33.6 mAP on MS COCO) while maintaining a **very small model footprint**, outperforming or matching other micro sized detectors such as YOLOv5n and YOLOX‑Nano on the same tasks. 

The `st_yolo_milli_pt` variant is implemented in **PyTorch** and is tuned for **ultra‑efficient inference** on edge and MCU environments.

## **Network information**

| Network information | Value |
|--------------------|-------|
| Framework          | Torch |
| Quantization       | Int8 |
| Provenance         | [STMicroelectronics Model Zoo Services](https://github.com/STMicroelectronics/stm32ai-modelzoo-services/tree/main/object_detection/object_detection) |
| Paper              | [STResNet & STYOLO (arXiv:2601.05364)](https://arxiv.org/abs/2601.05364) |

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.


## Network inputs / outputs

For an image resolution of NxM and NC classes

| Input Shape | Description |
| ----- | ----------- |
| (1, W, H, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, (W/8xH/8 + W/16xH/16 + W/32xH/32), (NC+1+4))  | Model returns bounding boxes with 6 values for each box, four coordinates (x1,y1,x2,y2), class confidence and objectness confidence |


## Recommended Platforms

| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | []       | []          |
| STM32MP1 | []       | []          |
| STM32MP2 | []       | []         |
| STM32N6  | [x]       | [x]         |


# Performances

## Metrics

Measures are done with default STEdgeAI Core configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on COCO dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_192/st_yolodv2milli_actrelu_pt_coco_192_qdq_int8.onnx) | COCO | Int8 | 192x192x3 | STM32N6 | 1008.00 | 0 | 3170.29 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_320/st_yolodv2milli_actrelu_pt_coco_320_qdq_int8.onnx) | COCO | Int8 | 320x320x3 | STM32N6 | 2718.88 | 800.00 | 3182.67 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_640/st_yolodv2milli_actrelu_pt_coco_640_qdq_int8.onnx) | COCO | Int8 | 640x640x3 | STM32N6 | 2768.00 | 9600.00 | 3189.38 | 4.0.0 |

* 640x640 coco checkpoints are provided primarily for finetuning purposes as these checkpoints are trained on large dataset at higher resolution. Models with 640 resolution is not suitable for deployment.

### Reference **NPU** inference time based on COCO dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_192/st_yolodv2milli_actrelu_pt_coco_192_qdq_int8.onnx) | COCO | Int8 | 192x192x3 | STM32N6570-DK | NPU/MCU | 17.34 | 57.6 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_320/st_yolodv2milli_actrelu_pt_coco_320_qdq_int8.onnx) | COCO | Int8 | 320x320x3 | STM32N6570-DK | NPU/MCU | 67.18 | 14.9 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_640/st_yolodv2milli_actrelu_pt_coco_640_qdq_int8.onnx) | COCO | Int8 | 640x640x3 | STM32N6570-DK | NPU/MCU | 3241.57 | 0.31 | 4.0.0 |

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_192/st_yolodv2milli_actrelu_pt_coco_person_192_qdq_int8.onnx) | COCO-Person | Int8 | 192x192x3 | STM32N6 | 1008.00 | 0 | 3155.48 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_256/st_yolodv2milli_actrelu_pt_coco_person_256_qdq_int8.onnx) | COCO-Person | Int8 | 256x256x3 | STM32N6 | 2320.00 | 0 | 3164.48 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_320/st_yolodv2milli_actrelu_pt_coco_person_320_qdq_int8.onnx) | COCO-Person | Int8 | 320x320x3 | STM32N6 | 2743.88 | 800.00 | 3167.85 | 4.0.0 |

### Reference **NPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_192/st_yolodv2milli_actrelu_pt_coco_person_192_qdq_int8.onnx) | COCO-Person | Int8 | 192x192x3 | STM32N6570-DK | NPU/MCU | 16.51 | 60.5 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_256/st_yolodv2milli_actrelu_pt_coco_person_256_qdq_int8.onnx) | COCO-Person | Int8 | 256x256x3 | STM32N6570-DK | NPU/MCU | 26.08 | 38.3 | 4.0.0 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_320/st_yolodv2milli_actrelu_pt_coco_person_320_qdq_int8.onnx) | COCO-Person | Int8 | 320x320x3 | STM32N6570-DK | NPU/MCU | 65.12 | 15.3 | 4.0.0 |



### AP on COCO dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Number of classes: 80

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_192/st_yolodv2milli_actrelu_pt_coco_192.onnx) | Float | 3x192x192 | 35.42 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_192/st_yolodv2milli_actrelu_pt_coco_192_qdq_int8.onnx) | Int8 | 3x192x192 | 32.29 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_320/st_yolodv2milli_actrelu_pt_coco_320.onnx) | Float | 3x320x320 | 45.64 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_320/st_yolodv2milli_actrelu_pt_coco_320_qdq_int8.onnx) | Int8 | 3x320x320 | 43.79 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_640/st_yolodv2milli_actrelu_pt_coco_640.onnx) | Float | 3x640x640 | 52.64 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2milli_actrelu_pt_coco_640/st_yolodv2milli_actrelu_pt_coco_640_qdq_int8.onnx) | Int8 | 3x640x640 | 51.17 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on COCO-Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Number of classes: 1


| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_192/st_yolodv2milli_actrelu_pt_coco_person_192.onnx) | Float | 3x192x192 | 61.71 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_192/st_yolodv2milli_actrelu_pt_coco_person_192_qdq_int8.onnx) | Int8 | 3x192x192 | 59.91 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_256/st_yolodv2milli_actrelu_pt_coco_person_256.onnx) | Float | 3x256x256 | 68.07 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_256/st_yolodv2milli_actrelu_pt_coco_person_256_qdq_int8.onnx) | Int8 | 3x256x256 | 66.16 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_320/st_yolodv2milli_actrelu_pt_coco_person_320.onnx) | Float | 3x320x320 | 72.12 |
| [st_yolodv2milli_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2milli_actrelu_pt_coco_person_320/st_yolodv2milli_actrelu_pt_coco_person_320_qdq_int8.onnx) | Int8 | 3x320x320 | 70.91 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


## References


- **STYOLO / STResNet paper**  
  [S. Sah & R. Kumar, *STResNet & STYOLO: A New Family of Compact Classification and Object Detection Models for MCUs*](https://arxiv.org/abs/2601.05364)

- **YOLOX (inspires STYOLO architecture)**  
  [Ge et al., *YOLOX: Exceeding YOLO Series in 2021*](https://arxiv.org/abs/2107.08430)

- **MS COCO dataset**  
  [Lin et al., *Microsoft COCO: Common Objects in Context*](https://arxiv.org/abs/1405.0312)
