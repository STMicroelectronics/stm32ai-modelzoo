# **SSDLite MobileNetV3 Small**

## **Use case** : `Object detection`

## **Model description**

SSDLite MobileNetV3 Small is a **lightweight single-shot object detection model** optimized for **real-time inference on mobile and edge devices** with minimal computational resources.

It combines the **SSDLite framework** with **MobileNetV3 Small** as the backbone. MobileNetV3 Small introduces **efficient inverted residual blocks, lightweight attention (SE modules), and hard-swish activations**, enabling a strong balance between accuracy, speed, and efficiency.  
The SSDLite head predicts object locations and class probabilities in a **single forward pass**, making the model suitable for **real-time detection** on resource-constrained platforms such as mobile devices and embedded systems.

The `ssdlite_mobilenetv3small_pt` variant is implemented in **PyTorch** and is widely used in scenarios where **ultra-low latency and minimal memory footprint** are critical.

## **Network information**

| Network information | Value |
|--------------------|-------|
| Framework          | Torch |
| Quantization       | Int8 |
| Provenance         | [torchvision GitHub](https://github.com/pytorch/vision) |
| Paper              | [SSDLite](https://arxiv.org/abs/1801.04381)<br>[MobileNetV3](https://arxiv.org/abs/1905.02244) |

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
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv3small_pt_coco_300/ssdlite_mobilenetv3small_pt_coco_300_qdq_int8.onnx) | COCO | Int8 | 300x300x3 | STM32N6 | 1763.09 | 0 | 1978.72 | 3.0.0 |

### Reference **NPU** inference time based on COCO dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv3small_pt_coco_300/ssdlite_mobilenetv3small_pt_coco_300_qdq_int8.onnx) | COCO | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 15.86 | 63.05 | 3.0.0 |

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [ssdlite_mobilenetv3small_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv3small_pt_coco_person_300/ssdlite_mobilenetv3small_pt_coco_person_300_qdq_int8.onnx) | COCO-Person | Int8 | 300x300x3 | STM32N6 | 1764.33 | 0 | 1186.25 | 3.0.0 |

### Reference **NPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssdlite_mobilenetv3small_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv3small_pt_coco_person_300/ssdlite_mobilenetv3small_pt_coco_person_300_qdq_int8.onnx) | COCO-Person | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 13.73 | 72.83 | 3.0.0 |

### Reference **NPU** memory footprint based on VOC dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|-------------------|-------------------|--------------------|-----------------------|
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv3small_pt_voc_300/ssdlite_mobilenetv3small_pt_voc_300_qdq_int8.onnx) | VOC | Int8 | 300x300x3 | STM32N6 | 1764.33 | 0 | 1376.84 | 3.0.0 |

### Reference **NPU** inference time based on VOC dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|------------|-------|------------------|--------------------|-----------|-----------------------|
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv3small_pt_voc_300/ssdlite_mobilenetv3small_pt_voc_300_qdq_int8.onnx) | VOC | Int8 | 300x300x3 | STM32N6570-DK | NPU/MCU | 14.30 | 69.93 | 3.0.0 |



### AP on COCO dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode), Number of classes: 80

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv3small_pt_coco_300/ssdlite_mobilenetv3small_pt_coco_300.onnx) | Float | 3x300x300 | 20.13 |
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/coco/ssdlite_mobilenetv3small_pt_coco_300/ssdlite_mobilenetv3small_pt_coco_300_qdq_int8.onnx) | Int8 | 3x300x300 | 18.85 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on COCO-Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Number of classes: 1


| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssdlite_mobilenetv3small_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv3small_pt_coco_person_300/ssdlite_mobilenetv3small_pt_coco_person_300.onnx) | Float | 3x300x300 | 35.19 |
| [ssdlite_mobilenetv3small_pt](./ST_pretrainedmodel_public_dataset/coco_person/ssdlite_mobilenetv3small_pt_coco_person_300/ssdlite_mobilenetv3small_pt_coco_person_300_qdq_int8.onnx) | Int8 | 3x300x300 | 31.87 |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

### AP on VOC dataset

Dataset details: [link](https://www.robots.ox.ac.uk/~vgg/projects/pascal/VOC/) , [License](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/HTML/license.html) , Number of classes: 20

| Model | Format | Resolution | AP50 |
| --- | --- | --- | --- |
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv3small_pt_voc_300/ssdlite_mobilenetv3small_pt_voc_300.onnx) | Float | 3x300x300 | 55.56 |
| [ssdlite_mobilenetv3small_pt](./Public_pretrainedmodel_public_dataset/voc/ssdlite_mobilenetv3small_pt_voc_300/ssdlite_mobilenetv3small_pt_voc_300_qdq_int8.onnx) | Int8 | 3x300x300 | 54.58 |

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

- **MobileNetV3 Small**  
  [Howard et al., *Searching for MobileNetV3*](https://arxiv.org/abs/1905.02244)

