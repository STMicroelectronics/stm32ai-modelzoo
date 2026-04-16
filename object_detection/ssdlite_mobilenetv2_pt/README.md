# **SSDLite MobileNetV2**

## **Use case** : `Object detection`

## **Model description**

SSDLite MobileNetV2 is a **lightweight single-shot object detection model** optimized for **real-time inference on mobile and edge devices**. 

It combines the **SSDLite framework**, a streamlined version of SSD for efficiency, with **MobileNetV2** as the backbone. MobileNetV2 uses **inverted residual blocks and linear bottlenecks**, enabling a strong balance between accuracy and computational efficiency while keeping the model small and fast.  
The SSDLite head predicts object locations and class probabilities in a **single forward pass**, making the model suitable for **real-time detection** in resource-constrained environments.

The `ssdlite_mobilenetv2_pt` variant is implemented in **PyTorch** and is widely used in applications requiring **low latency, minimal memory footprint, and high energy efficiency**, such as mobile vision apps and embedded systems.

## **Network information**

| Network information | Value |
|--------------------|-------|
| Framework          | Torch |
| Quantization       | Int8 |
| Provenance         | [torchvision GitHub](https://github.com/pytorch/vision) |
| Paper              | [SSDLite](https://arxiv.org/abs/1801.04381)<br>[MobileNetV2](https://arxiv.org/abs/1801.04381) |

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
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv2_pt_coco_300/ssdlite_mobilenetv2_pt_coco_300_qdq_int8.onnx) | COCO | Int8 | 300x300x3 | STM32N6 | 2408.59 | 2109.38 | 5121.38 | 4.0.0 |

### Reference **NPU** inference time based on COCO dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv2_pt_coco_300/ssdlite_mobilenetv2_pt_coco_300_qdq_int8.onnx) | COCO | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 121.02 | 8.27 | 4.0.0 |

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [ssdlite_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv2_pt_coco_person_300/ssdlite_mobilenetv2_pt_coco_person_300_qdq_int8.onnx) | COCO-Person | Int8 | 300x300x3 | STM32N6 | 2374.34 | 2109.38 | 3758.63 | 4.0.0 |

### Reference **NPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssdlite_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv2_pt_coco_person_300/ssdlite_mobilenetv2_pt_coco_person_300_qdq_int8.onnx) | COCO-Person | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 117.25 | 8.53 | 4.0.0 |

### Reference **NPU** memory footprint based on VOC dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv2_pt_voc_300/ssdlite_mobilenetv2_pt_voc_300_qdq_int8.onnx) | VOC | Int8 | 300x300x3 | STM32N6 | 2374.81 | 2109.38 | 4086.38 | 4.0.0 |

### Reference **NPU** inference time based on VOC dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv2_pt_voc_300/ssdlite_mobilenetv2_pt_voc_300_qdq_int8.onnx) | VOC | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 118.10 | 8.47 | 4.0.0 |



### AP on COCO dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Number of classes: 80

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv2_pt_coco_300/ssdlite_mobilenetv2_pt_coco_300.onnx) | Float | 3x300x300 | 29.03 |
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv2_pt_coco_300/ssdlite_mobilenetv2_pt_coco_300_qdq_int8.onnx) | Int8 | 3x300x300 | 28.60 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on COCO-Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Number of classes: 1

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssdlite_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv2_pt_coco_person_300/ssdlite_mobilenetv2_pt_coco_person_300.onnx) | Float | 3x300x300 | 39.90 |
| [ssdlite_mobilenetv2_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv2_pt_coco_person_300/ssdlite_mobilenetv2_pt_coco_person_300_qdq_int8.onnx) | Int8 | 3x300x300 | 39.71 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on VOC dataset

Dataset details: [link](https://www.robots.ox.ac.uk/~vgg/projects/pascal/VOC/) , [License](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/HTML/license.html) , Number of classes: 20

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv2_pt_voc_300/ssdlite_mobilenetv2_pt_voc_300.onnx) | Float | 3x300x300 | 70.17 |
| [ssdlite_mobilenetv2_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv2_pt_voc_300/ssdlite_mobilenetv2_pt_voc_300_qdq_int8.onnx) | Int8 | 3x300x300 | 70.07 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


## References

- **COCO**  
  [Lin et al., *Microsoft COCO: Common Objects in Context*](https://arxiv.org/abs/1405.0312)

- **PASCAL VOC**  
  [Everingham et al., *The PASCAL Visual Object Classes (VOC) Challenge*](http://host.robots.ox.ac.uk/pascal/VOC/pubs/everingham10.pdf)

- **SSDLite**  
  [Howard et al., *MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications* (SSDLite section)](https://arxiv.org/abs/1801.04381)

- **MobileNetV2**  
  [Sandler et al., *MobileNetV2: Inverted Residuals and Linear Bottlenecks*](https://arxiv.org/abs/1801.04381)
