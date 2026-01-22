# **SSD MobileNetV2**

## **Use case** : `Object detection`

## **Model description**

SSD MobileNetV2 is a **single-shot object detection model** designed for **efficient and low-latency inference** on resource-constrained devices such as mobile and edge platforms.

The model combines the **Single Shot Detector (SSD)** framework with **MobileNetV2** as the backbone network. MobileNetV2 employs **inverted residual blocks and linear bottlenecks**, enabling a strong balance between accuracy and computational efficiency.  
The SSD head performs object localization and classification in a **single forward pass**, making the model suitable for real-time detection scenarios.

The `ssd_mobilenetv2_pt` variant is implemented in **PyTorch** and is commonly used as a lightweight baseline for object detection tasks where **speed, memory footprint, and power efficiency** are critical.

## **Network information**

| Network information | Value |
|--------------------|-------|
| Framework          | Torch |
| Quantization       | Int8 |
| Provenance         | [torchvision GitHub](https://github.com/pytorch/vision) |
| Paper              | [SSD](https://arxiv.org/abs/1512.02325)<br>[MobileNetV2](https://arxiv.org/abs/1801.04381) |

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.


## Network inputs / outputs

For an image resolution of NxM and NC classes

| Input Shape | Description |
| ----- | ----------- |
| (1, W, H, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, 3000,(1+NC) and (1,3000,4)) | Model returns two output vectors of bounding boxes where first output returns confidence for each class (+ background class) and second output returns bounding box coordinates (x1, y1, x2,y2) |


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
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssd_mobilenetv2_pt_coco_300/ssd_mobilenetv2_pt_coco_300_qdq_int8.onnx) | COCO | Int8 | 300x300x3 | STM32N6 | 2323.25 | 2109.38 | 20033.69 | 3.0.0 |

### Reference **NPU** inference time based on COCO dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssd_mobilenetv2_pt_coco_300/ssd_mobilenetv2_pt_coco_300_qdq_int8.onnx) | COCO | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 158.49 | 6.31 | 3.0.0 |

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [ssd_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssd_mobilenetv2_pt_coco_person_300/ssd_mobilenetv2_pt_coco_person_300_qdq_int8.onnx) | COCO-Person | Int8 | 300x300x3 | STM32N6 | 2182.72 | 2109.38 | 8005.94 | 3.0.0 |

### Reference **NPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssd_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssd_mobilenetv2_pt_coco_person_300/ssd_mobilenetv2_pt_coco_person_300_qdq_int8.onnx) | COCO-Person | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 126.19 | 7.92 | 3.0.0 |

### Reference **NPU** memory footprint based on VOC dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssd_mobilenetv2_pt_voc_300/ssd_mobilenetv2_pt_voc_300_qdq_int8.onnx) | VOC | Int8 | 300x300x3 | STM32N6 | 2237.00 | 2109.38 | 10898.69 | 3.0.0 |

### Reference **NPU** inference time based on VOC dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssd_mobilenetv2_pt_voc_300/ssd_mobilenetv2_pt_voc_300_qdq_int8.onnx) | VOC | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 135.06 | 7.40 | 3.0.0 |



### AP on COCO dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Number of classes: 80

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssd_mobilenetv2_pt_coco_300/ssd_mobilenetv2_pt_coco_300.onnx) | Float | 3x300x300 | 31.75 |
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssd_mobilenetv2_pt_coco_300/ssd_mobilenetv2_pt_coco_300_qdq_int8.onnx) | Int8 | 3x300x300 | 31.29 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on COCO-Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Number of classes: 1

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssd_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssd_mobilenetv2_pt_coco_person_300/ssd_mobilenetv2_pt_coco_person_300.onnx) | Float | 3x300x300 | 41.91 |
| [ssd_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssd_mobilenetv2_pt_coco_person_300/ssd_mobilenetv2_pt_coco_person_300_qdq_int8.onnx) | Int8 | 3x300x300 | 41.74 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on VOC dataset

Dataset details: [link](https://www.robots.ox.ac.uk/~vgg/projects/pascal/VOC/) , [License](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/HTML/license.html) , Number of classes: 20

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssd_mobilenetv2_pt_voc_300/ssd_mobilenetv2_pt_voc_300.onnx) | Float | 3x300x300 | 67.03 |
| [ssd_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssd_mobilenetv2_pt_voc_300/ssd_mobilenetv2_pt_voc_300_qdq_int8.onnx) | Int8 | 3x300x300 | 66.91 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100


## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


## Datasets

- **COCO**  
  [Lin et al., *Microsoft COCO: Common Objects in Context*](https://arxiv.org/abs/1405.0312)

- **PASCAL VOC**  
  [Everingham et al., *The PASCAL Visual Object Classes (VOC) Challenge*](http://host.robots.ox.ac.uk/pascal/VOC/pubs/everingham10.pdf)

## References

- **SSD**  
  [Liu et al., *SSD: Single Shot MultiBox Detector*](https://arxiv.org/abs/1512.02325)

- **MobileNetV2**  
  [Sandler et al., *MobileNetV2: Inverted Residuals and Linear Bottlenecks*](https://arxiv.org/abs/1801.04381)