# Yolo26n object detection quantized

## **Use case** : `Object detection`

# Model description

Yolo26n is a lightweight and efficient object detection model designed for instance segmentation tasks. It is part of the YOLO (You Only Look Once) family of models, known for their real-time object detection capabilities. The "n" in Yolo26n indicates that it is a nano version, optimized for speed and resource efficiency, making it suitable for deployment on devices with limited computational power, such as mobile devices and embedded systems.

Yolo26n is implemented in Pytorch by Ultralytics and is quantized in int8 format using ONNX QDQ.

## Network information


| Network information | Value                                      |
|---------------------|--------------------------------------------|
| Framework           | ONNX                                       |
| Quantization        | int8                                       |
| Provenance          | https://docs.ultralytics.com/tasks/detect/ |


## Networks inputs / outputs

With an image resolution of NxM and K classes to detect:

| Input Shape | Description                                              |
|-------------|----------------------------------------------------------|
| (1,3, N, M) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description                                                                             |
|--------------|-----------------------------------------------------------------------------------------|
| (1, 4+K, F)  | FLOAT values Where F = (N/8)^2 + (N/16)^2 + (N/32)^2 is the 3 concatenated feature maps |


## Recommended Platforms


| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | []        | []          |
| STM32MP1 | []        | []          |
| STM32MP2 | []        | []          |
| STM32N6  | [x]       | [x]         |


# Performances

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.
> [!CAUTION] 
> All YOLO26 hyperlinks in the tables below link to an external GitHub folder, which is subject to its own license terms:
https://github.com/stm32-hotspot/ultralytics/blob/main/LICENSE
Please also check the folder's README.md file for detailed information about its use and content:
https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/README.md

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                                                                                                               | Dataset     | Format | Resolution | Series  | Internal RAM | External RAM | Weights Flash | STEdgeAI Core version |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|--------|------------|---------|--------------|--------------|---------------|-----------------------|
| [YOLO26n per channel](https://github.com/stm32-hotspot/ultralytics/raw/refs/heads/main/examples/YOLOv8-STEdgeAI/stedgeai_models/object_detection/yolo26/yolo26_256_qdq_int8_od_coco-person-st.onnx) | COCO-Person | Int8   | 256x256x3  | STM32N6 | 722.04       | 0            | 2341.32       | 4.0.0                 |

### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                                                                                                               | Dataset     | Format | Resolution | Board         | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|--------|------------|---------------|------------------|---------------------|-----------|-----------------------|
| [YOLO26n per channel](https://github.com/stm32-hotspot/ultralytics/raw/refs/heads/main/examples/YOLOv8-STEdgeAI/stedgeai_models/object_detection/yolo26/yolo26_256_qdq_int8_od_coco-person-st.onnx) | COCO-Person | Int8   | 256x256x3  | STM32N6570-DK | NPU/MCU          | 20.99               | 47.64     | 4.0.0                 |

### AP on COCO Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287


| Model                                                                                                                                                                                               | Format | Resolution | AP*    |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|--------|
| [YOLO26n per channel](https://github.com/stm32-hotspot/ultralytics/raw/refs/heads/main/examples/YOLOv8-STEdgeAI/stedgeai_models/object_detection/yolo26/yolo26_256_qdq_int8_od_coco-person-st.onnx) | Int8   | 256x256x3  | 52.7 % |
| [YOLO26n per channel](https://github.com/stm32-hotspot/ultralytics/raw/refs/heads/main/examples/YOLOv8-STEdgeAI/stedgeai_models/object_detection/yolo26/yolo26_256_float_od_coco-person-st.onnx)    | Float  | 256x256x3  | 53.6 % |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100


## Integration in a simple example and other services support:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services).
The models are stored in the Ultralytics repository. You can find them at the following link: [Ultralytics YOLOv8-STEdgeAI Models](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/).

Please refer to the [Ultralytics documentation](https://docs.ultralytics.com/tasks/detect/#train) to retrain the models.

# References

<a id="1">[1]</a>
“Microsoft COCO: Common Objects in Context”. [Online]. Available: https://cocodataset.org/#download.
@article{DBLP:journals/corr/LinMBHPRDZ14,
  author    = {Tsung{-}Yi Lin and
               Michael Maire and
               Serge J. Belongie and
               Lubomir D. Bourdev and
               Ross B. Girshick and
               James Hays and
               Pietro Perona and
               Deva Ramanan and
               Piotr Doll{'{a} }r and
               C. Lawrence Zitnick},
  title     = {Microsoft {COCO:} Common Objects in Context},
  journal   = {CoRR},
  volume    = {abs/1405.0312},
  year      = {2014},
  url       = {http://arxiv.org/abs/1405.0312},
  archivePrefix = {arXiv},
  eprint    = {1405.0312},
  timestamp = {Mon, 13 Aug 2018 16:48:13 +0200},
  biburl    = {https://dblp.org/rec/bib/journals/corr/LinMBHPRDZ14},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
