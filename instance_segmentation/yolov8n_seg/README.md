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
Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference **NPU** memory footprint based on COCO dataset

|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB)| External RAM (KiB)| Weights Flash (KiB) | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [Yolov8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_256_quant_pc_uf_seg_coco-st.tflite)  | COCO | Int8 | 256x256x3 | STM32N6 |   2128 | 0.0 | 3425.39 | 10.0.0 | 2.0.0 
| [Yolov8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_320_quant_pc_uf_seg_coco-st.tflite)  | COCO | Int8 | 320x320x3 | STM32N6 |   2564.06 | 0.0 | 3467.56 | 10.0.0 | 2.0.0 |



### Reference **NPU**  inference time based on COCO Person dataset 
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [YOLOv8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_256_quant_pc_uf_seg_coco-st.tflite) | COCO-Person      | Int8   | 256x256x3  | STM32N6570-DK   |   NPU/MCU      |     37.59         |   26.61      |       10.0.0        |     2.0.0   |
| [YOLOv8n seg per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/segmentation/yolov8n_320_quant_pc_uf_seg_coco-st.tflite) | COCO-Person     | Int8    | 320x320x3  | STM32N6570-DK   |   NPU/MCU      |       53.21      |     18.79     |       10.0.0        |     2.0.0   |



## Retraining and Integration in a Simple Example
Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services).
For instance segmentation, the models are stored in the Ultralytics repository. You can find them at the following link: [Ultralytics YOLOv8-STEdgeAI Models](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/).

Please refer to the [Ultralytics documentation](https://docs.ultralytics.com/tasks/segment/#train) to retrain the model.


## References

<a id="1">[1]</a> T.-Y. Lin, M. Maire, S. Belongie, J. Hays, P. Perona, D. Ramanan, P. Dollár, and C. L. Zitnick, "Microsoft COCO: Common Objects in Context." European Conference on Computer Vision (ECCV), 2014. [Link](https://arxiv.org/abs/1405.0312)

<a id="2">[2]</a> Ultralytics, "YOLOv8: Next-Generation Object Detection and Segmentation Model." Ultralytics, 2023. [Link](https://github.com/ultralytics/ultralytics)

