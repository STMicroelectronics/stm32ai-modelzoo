# Yolov8n_seg

## **Use case** : `Instance segmentation`

# Model description

Yolov8n_seg is a lightweight and efficient model designed for instance segmentation tasks. It is part of the YOLO (You Only Look Once) family of models, known for their real-time object detection capabilities. The "n" in Yolov8n_seg indicates that it is a nano version, optimized for speed and resource efficiency, making it suitable for deployment on devices with limited computational power, such as mobile devices and embedded systems.

Yolov8n_seg is implemented in Pytorch by Ultralytics and is quantized in int8 format using tensorflow lite converter.

## Network information
| Network Information     | Value                                |
|-------------------------|--------------------------------------|
|  Framework              | Tensorflow  |
|  Quantization           | int8  |
|  Paper                  | https://arxiv.org/pdf/2305.09972 |



## Recommended platform
| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []       | []          |
| STM32U5  | []       | []          |
| STM32MP1 | []       | []         |
| STM32MP2 | [x]       | []          |
| STM32N6| [x]       | [x]          |

---
# Performances

## Metrics
Measures are done with default STEdgeAI Core version configuration with enabled input / output allocated option.
> [!CAUTION] 
> All YOLOv8 hyperlinks in the tables below link to an external GitHub folder, which is subject to its own license terms:
https://github.com/stm32-hotspot/ultralytics/blob/main/LICENSE
Please also check the folder's README.md file for detailed information about its use and content:
https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/README.md


### Reference **NPU** memory footprint based on COCO dataset

|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB)| External RAM (KiB)| Weights Flash (KiB) | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------------------------|
| [Yolov8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_256_quant_pc_ii_seg_coco-st.tflite)  | COCO | Int8 | 256x256x3 | STM32N6 | 855 | 0.0 | 3393.42 | 3.0.0 |
| [Yolov8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_320_quant_pc_ii_seg_coco-st.tflite)  | COCO | Int8 | 320x320x3 | STM32N6 | 1413.89 | 0.0 | 3435.34 | 3.0.0 |



### Reference **NPU**  inference time based on COCO Person dataset 
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [YOLOv8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_256_quant_pc_ii_seg_coco-st.tflite) | COCO-Person      | Int8   | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |     31.57        |   29.72      |  3.0.0   |
| [YOLOv8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_320_quant_pc_ii_seg_coco-st.tflite) | COCO-Person     | Int8    | 320x320x3  | STM32N6570-DK   |   NPU/MCU      |       41.87      |     22.83     |   3.0.0   |

### Reference **MPU** inference time based on COCO 2017 Person dataset (instance segmentation)

| Model                                                                                                                                                          | Dataset          | Format | Resolution | Quantization   | Board           | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU | %CPU | X-LINUX-AI version | Framework         |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|--------|------------|----------------|-----------------|------------------|-----------|---------------------|-------|------|------|--------------------|-------------------|
| [YOLOv8n-seg](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_256_quant_pc_ii_seg_coco-st.tflite) | person_coco_2017 | Int8   | 256x256x3  | per-channel\*\* | STM32MP257F-EV1 | NPU/GPU          | 800 MHz   | 19.84               | 91.71 | 8.29 | 0    | v6.1.0             | TensorFlow Lite   |
| [YOLOv8n-seg](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_320_quant_pc_ii_seg_coco-st.tflite) | person_coco_2017 | Int8   | 320x320x3  | per-channel\*\* | STM32MP257F-EV1 | NPU/GPU          | 800 MHz   | 30.97               | 93.59 | 6.41 | 0    | v6.1.0             | TensorFlow Lite   |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

** **Note:** On STM32MP2 devices, per-channel quantized models are internally converted to per-tensor quantization by the compiler using an entropy-based method. This may introduce a slight loss in accuracy compared to the original per-channel models.

## Retraining and Integration in a Simple Example
Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services).
For instance segmentation, the models are stored in the Ultralytics repository. You can find them at the following link: [Ultralytics YOLOv8-STEdgeAI Models](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/).

Please refer to the [Ultralytics documentation](https://docs.ultralytics.com/tasks/segment/#train) to retrain the model.


## References

<a id="1">[1]</a> T.-Y. Lin, M. Maire, S. Belongie, J. Hays, P. Perona, D. Ramanan, P. Dollár, and C. L. Zitnick, "Microsoft COCO: Common Objects in Context." European Conference on Computer Vision (ECCV), 2014. [Link](https://arxiv.org/abs/1405.0312)

<a id="2">[2]</a> Ultralytics, "YOLOv8: Next-Generation Object Detection and Segmentation Model." Ultralytics, 2023. [Link](https://github.com/ultralytics/ultralytics)

