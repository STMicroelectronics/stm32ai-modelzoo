# Yolov8n Pose quantized

## **Use case** : [Pose estimation](../../../pose_estimation/README.md)

# Model description


Yolov8n Pose is a multi pose estimation model targeted for real-time processing implemented in Pytorch by Ultralytics.

The model is quantized in int8 format using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             | https://docs.ultralytics.com/tasks/pose/ |


## Networks inputs / outputs

With an image resolution of NxM with K keypoints to detect :

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, Kx3, F) | FLOAT values Where F = (N/8)^2 + (N/16)^2 + (N/32)^2 is the 3 concatenated feature maps and K is the number of keypoints|


## Recommended Platforms


| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | []        | []          |
| STM32MP1 | []        | []          |
| STM32MP2 | [x]       | [x]         |


# Performances

## Deployment


To deploy your model, you need to configure the [user_config.yaml](../../src/user_config.yaml) file following the [tutorial](../../deployment/README_MPU.md).


## Metrics


Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.


### Reference **MPU** inference time based on COCO Person dataset (see Accuracy for details on dataset)

| Model                                                                                                                                                              | Format | Resolution | Quantization  | Board             | Execution Engine | Frequency | Inference time (ms) | %NPU  | %GPU  | %CPU | X-LINUX-AI version |       Framework       |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|------------|---------------|-------------------|------------------|-----------|---------------------|-------|-------|------|--------------------|-----------------------|
| [YOLOv8n pose per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/pose_estimation/yolov8n_256_quant_pc_uf_pose_coco-st.tflite) | Int8   | 256x256x3  |  per-channel**  | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 102.8 ms            | 11.70  | 88.30 |0     | v5.0.0             | OpenVX                |
| [YOLOv8n pose per tensor](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/pose_estimation/yolov8n_256_quant_pt_uf_pose_coco-st.tflite)  | Int8   | 256x256x3  |  per-tensor     | STM32MP257F-DK2   | NPU/GPU          | 800  MHz  | 17.57 ms            | 86.79  | 13.21 |0     | v5.0.0             | OpenVX                |

** **To get the most out of MP25 NPU hardware acceleration, please use per-tensor quantization**

### AP0.5 on COCO Person dataset


Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

To build the multi pose validation dataset we used this [script](../../datasets/dataset_converter/converter.py), following the [tutorial](../../datasets/dataset_converter/README.md).

| Model | Format | Resolution |       AP0.5*   |
|-------|--------|------------|----------------|
| [YOLOv8n pose per channel](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/pose_estimation/yolov8n_256_quant_pc_uf_pose_coco-st.tflite) | Int8   | 256x256x3  | 51.06 %  |
| [YOLOv8n pose per tensor](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/pose_estimation/yolov8n_256_quant_pt_uf_pose_coco-st.tflite)  | Int8   | 256x256x3  | 48.43 %  |


\* NMS_THRESH = 0.1, SCORE_THRESH = 0.001

## Demos
### Integration in a simple example


Please refer to the generic guideline [here](../../deployment/README_MPU.md)


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
