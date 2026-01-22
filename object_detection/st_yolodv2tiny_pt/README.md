# **STYOLOTiny**

## **Use case** : `Object detection`

## **Model description**

STYOLOTiny is a **compact, efficient object detection model** designed for deployment on **resource‑constrained devices** such as microcontrollers (MCUs), embedded systems, and edge accelerators. It belongs to the STYOLO family introduced in *“STResNet & STYOLO: A New Family of Compact Classification and Object Detection Models for MCUs”* (arXiv:2601.05364).

The model uses a **highly compressed backbone** derived from STResNet along with a **YOLO‑style detection head**, optimized for **low memory usage, minimal compute, and real‑time inference**. STYOLOTiny targets scenarios where **small model footprint and fast inference** are critical, offering competitive detection performance on standard benchmarks compared to other micro‑sized detectors.

The `st_yolodv2tiny_pt` variant has a slightly larger footprint compared to `st_yolodv2milli_pt` and it is implemented in **PyTorch** and intended for **ultra‑efficient object detection** on edge and MCU environments.


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
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_192/st_yolodv2tiny_actrelu_pt_coco_192_qdq_int8.onnx) | COCO | Int8 | 192x192x3 | STM32N6 | 1597.50 | 0 | 4789.56 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_288/st_yolodv2tiny_actrelu_pt_coco_288_qdq_int8.onnx) | COCO | Int8 | 288x288x3 | STM32N6 | 2644.00 | 648.00 | 4801.37 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_640/st_yolodv2tiny_actrelu_pt_coco_640_qdq_int8.onnx) | COCO | Int8 | 640x640x3 | STM32N6 | 2796.56 | 9600.00 | 4811.48 | 3.0.0 |

* 640x640 coco checkpoints are provided primarily for finetuning purposes as these checkpoints are trained on large dataset at higher resolution. Models with 640 resolution is not suitable for deployment.

### Reference **NPU** inference time based on COCO dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_192/st_yolodv2tiny_actrelu_pt_coco_192_qdq_int8.onnx) | COCO | Int8 | 192x192x3 | STM32N6570-DK | NPU/MCU | 26.52 | 37.71 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_288/st_yolodv2tiny_actrelu_pt_coco_288_qdq_int8.onnx) | COCO | Int8 | 288x288x3 | STM32N6570-DK | NPU/MCU | 66.66 | 15.00 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_640/st_yolodv2tiny_actrelu_pt_coco_640_qdq_int8.onnx) | COCO | Int8 | 640x640x3 | STM32N6570-DK | NPU/MCU | 3100.00 | 0.32 | 3.0.0 |

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_192/st_yolodv2tiny_actrelu_pt_coco_person_192_qdq_int8.onnx) | COCO-Person | Int8 | 192x192x3 | STM32N6 | 1597.50 | 0 | 4767.34 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_256/st_yolodv2tiny_actrelu_pt_coco_person_256_qdq_int8.onnx) | COCO-Person | Int8 | 256x256x3 | STM32N6 | 2424.00 | 0 | 4774.09 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_288/st_yolodv2tiny_actrelu_pt_coco_person_288_qdq_int8.onnx) | COCO-Person | Int8 | 288x288x3 | STM32N6 | 2644.00 | 648.00 | 4779.15 | 3.0.0 |

### Reference **NPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_192/st_yolodv2tiny_actrelu_pt_coco_person_192_qdq_int8.onnx) | COCO-Person | Int8 | 192x192x3 | STM32N6570-DK | NPU/MCU | 25.50 | 39.22 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_256/st_yolodv2tiny_actrelu_pt_coco_person_256_qdq_int8.onnx) | COCO-Person | Int8 | 256x256x3 | STM32N6570-DK | NPU/MCU | 37.23 | 26.86 | 3.0.0 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_288/st_yolodv2tiny_actrelu_pt_coco_person_288_qdq_int8.onnx) | COCO-Person | Int8 | 288x288x3 | STM32N6570-DK | NPU/MCU | 64.87 | 15.42 | 3.0.0 |




### AP on COCO dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Number of classes: 80

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_192/st_yolodv2tiny_actrelu_pt_coco_192.onnx) | Float | 3x192x192 | 37.45 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_192/st_yolodv2tiny_actrelu_pt_coco_192_qdq_int8.onnx) | Int8 | 3x192x192 | 35.78 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_288/st_yolodv2tiny_actrelu_pt_coco_288.onnx) | Float | 3x288x288 | 45.62 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_288/st_yolodv2tiny_actrelu_pt_coco_288_qdq_int8.onnx) | Int8 | 3x288x288 | 44.57 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_640/st_yolodv2tiny_actrelu_pt_coco_640.onnx) | Float | 3x640x640 | 54.32 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco/st_yolodv2tiny_actrelu_pt_coco_640/st_yolodv2tiny_actrelu_pt_coco_640_qdq_int8.onnx) | Int8 | 3x640x640 | 53.46 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on COCO-Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Number of classes: 1


| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_192/st_yolodv2tiny_actrelu_pt_coco_person_192.onnx) | Float | 3x192x192 | 62.75 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_192/st_yolodv2tiny_actrelu_pt_coco_person_192_qdq_int8.onnx) | Int8 | 3x192x192 | 62.15 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_256/st_yolodv2tiny_actrelu_pt_coco_person_256.onnx) | Float | 3x256x256 | 69.22 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_256/st_yolodv2tiny_actrelu_pt_coco_person_256_qdq_int8.onnx) | Int8 | 3x256x256 | 68.41 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_288/st_yolodv2tiny_actrelu_pt_coco_person_288.onnx) | Float | 3x288x288 | 71.02 |
| [st_yolodv2tiny_pt](./ST_pretrainedmodel_public_dataset/coco_person/st_yolodv2tiny_actrelu_pt_coco_person_288/st_yolodv2tiny_actrelu_pt_coco_person_288_qdq_int8.onnx) | Int8 | 3x288x288 | 70.72 |

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
