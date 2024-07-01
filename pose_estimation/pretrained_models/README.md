# Overview of pose estimation STM32 model zoo


The STM32 model zoo includes several models for object detection use case pre-trained on custom and public datasets.
Under each model directory, you can find the following model categories:

- `Public_pretrainedmodel_custom_dataset` contains public pose estimation models trained on custom datasets.
- `ST_pretrainedmodel_public_dataset` contains pose estimation models trained on public datasets.

<a name="pose_models"></a>

## Pose estimation models

The table below summarizes the performance of the models, as well as their memory footprints generated using STM32Cube.AI for deployment purposes.

By default, the results are provided for quantized Int8 models.

Below sections contain detailed information on models memory usage and accuracies (click on the arrows to expand):

<details><summary>MoveNet</summary>

| Models                     | Implementation | Dataset    | Input Resolution | OKS          | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version  | Source
|---------------------------|----------------|------------|------------------|---------------|--------------|----------------------|----------------------|-----------------------|--------
| ST MoveNet Lightning heatmaps   | TensorFlow     | COCO single pose 13kpts   | 192x192x3   | *51.96%               |   237.887      |   1394.41           |   2300.69      | 9.1.0                 |    [link](movenet/ST_pretrainedmodel_public_dataset/custom_dataset_person_13kpts/st_movenet_lightning_heatmaps_192/st_movenet_lightning_heatmaps_192_int8.tflite)
| MoveNet Lightning heatmaps      | TensorFlow     | COCO single pose 17kpts   | 192x192x3   | 53.92%                |   238.8        |   1394.41           |   2301.08      | 9.1.0                 |    [link](movenet/Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_192/movenet_lightning_heatmaps_192_int8.tflite)
| MoveNet Lightning heatmaps      | TensorFlow     | COCO single pose 17kpts   | 224x224x3   | 56.89%                |   325.026      |   1710.0            |   2301.08      | 9.1.0                 |    [link](movenet/Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_224/movenet_lightning_heatmaps_224_int8.tflite)
| MoveNet Lightning heatmaps      | TensorFlow     | COCO single pose 17kpts   | 256x256x3   | 58.74%                |   424.519      |   2077.92           |   2301.08      | 9.1.0                 |    [link](movenet/Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_heatmaps_256/movenet_lightning_heatmaps_256_int8.tflite)
| MoveNet Lightning               | TensorFlow     | COCO single pose 17kpts   | 192x192x3   | 54.12%                |   NA           |   NA                |   NA           | 9.1.0                 |    [link](movenet/Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_lightning_192/movenet_singlepose_lightning_192_int8.tflite)
| MoveNet Thunder                 | TensorFlow     | COCO single pose 17kpts   | 256x256x3   | 64.43%                |   NA           |   NA                |   NA           | 9.1.0                 |    [link](movenet/Public_pretrainedmodel_custom_dataset/custom_dataset_person_17kpts/movenet_thunder_256/movenet_singlepose_thunder_256_int8.tflite)

</details>
<details><summary>YOLOv8n pose</summary>

| Models                     | Implementation | Dataset    | Input Resolution | mAP_0.5**         | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version  | Source
|---------------------------|----------------|------------|------------------|---------------|--------------|----------------------|----------------------|-----------------------|--------
| YOLOv8n pose per channel  | TensorFlow     | COCO multi pose 17kpts    | 256x256x3   | 51.06%                |   741.778      |   855.47            |   3449.16      | 9.1.0                 |    [stm32-hotspot](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/pose_estimation/yolov8n_256_quant_pc_uf_pose_coco-st.tflite)
| YOLOv8n pose per tensor   | TensorFlow     | COCO multi pose 17kpts    | 256x256x3   | 48.43%                |   741.778      |   786.43            |   3321.03      | 9.1.0                 |    [stm32-hotspot](https://github.com/stm32-hotspot/ultralytics/blob/main/examples/YOLOv8-STEdgeAI/stedgeai_models/pose_estimation/yolov8n_256_quant_pt_uf_pose_coco-st.tflite)
</details>

\* keypoints = 13

\** NMS_THRESH = 0.1, SCORE_THRESH = 0.001

You can get inference time information for each models following links below:
- [MoveNet](./movenet/README.md)
- [YOLOv8n pose](./yolov8n_pose/README.md)

