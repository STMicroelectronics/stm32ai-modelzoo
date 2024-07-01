# Overview of object detection STM32 model zoo


The STM32 model zoo includes several models for object detection use case pre-trained on custom and public datasets.
Under each model directory, you can find the following model categories:

- `Public_pretrainedmodel_public_dataset` contains public object detection models trained on public datasets.
- `ST_pretrainedmodel_custom_dataset` contains different object detection models trained on ST custom datasets using our [training scripts](../src/training). 
- `ST_pretrainedmodel_public_dataset` contains different object detection models trained on various public datasets following the [training section](../src/training/README.md) in STM32 model zoo.

<a name="od_models"></a>

## Object detection models

The table below summarizes the performance of the models, as well as their memory footprints generated using STM32Cube.AI for deployment purposes.

By default, the results are provided for quantized Int8 models.
When nothing is precised in the model name, training is done using transfer learning technique from a pre-trained model. Else, "tfs" stands for "training from scratch".

Below sections contain detailed information on models memory usage and accuracies (click on the arrows to expand):
<details><summary>ST SSD MobileNet v1</summary>

| Models                     | Implementation | Dataset    | Input Resolution | mAP*          | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version  | Source
|---------------------------|----------------|------------|------------------|---------------|--------------|----------------------|----------------------|-----------------------|--------
| ST SSD MobileNet v1 0.25   | TensorFlow     | COCO Person dataset    | 192x192x3   | 33.70%                |   40.48        |   266.3            |   438.28        | 9.1.0                 |    [link](st_ssd_mobilenet_v1/ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_192/st_ssd_mobilenet_v1_025_192_int8.tflite)
| ST SSD MobileNet v1 0.25   | TensorFlow     | COCO Person dataset    | 224x224x3   | 44.45%                |   59.98       |   379.6             |   595.66        | 9.1.0                 |    [link](st_ssd_mobilenet_v1/ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_224/st_ssd_mobilenet_v1_025_224_int8.tflite)
| ST SSD MobileNet v1 0.25   | TensorFlow     | COCO Person dataset    | 256x256x3   | 46.26%                |   72.55        |   456.1             |   595.66        | 9.1.0                 |    [link](st_ssd_mobilenet_v1/ST_pretrainedmodel_public_dataset/coco_2017_person/st_ssd_mobilenet_v1_025_256/st_ssd_mobilenet_v1_025_256_int8.tflite)

</details>
<details><summary>SSD MobileNet v2</summary>

| Models                     | Implementation | Dataset    | Input Resolution | mAP*          | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version  | Source
|---------------------------|----------------|------------|------------------|---------------|--------------|----------------------|----------------------|-----------------------|--------
| SSD MobileNet v2 0.35 FPN-lite | TensorFlow     | COCO Person dataset    | 192x192x3   | 40.73%                |   122.54        |   711.45            |   984.25        | 9.1.0                 |    [link](ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_192/ssd_mobilenet_v2_fpnlite_035_192_int8.tflite)
| SSD MobileNet v2 0.35 FPN-lite | TensorFlow     | COCO Person dataset    | 224x224x3   | 48.67%                |   167.15        |   956.82            |   1007.78        | 9.1.0                 |    [link](ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_224/ssd_mobilenet_v2_fpnlite_035_224_int8.tflite)
| SSD MobileNet v2 0.35 FPN-lite | TensorFlow     | COCO Person dataset    | 256x256x3   | 55.56%                |   217.85        |   1238.29            |   1032.26        | 9.1.0                 |    [link](ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_256/ssd_mobilenet_v2_fpnlite_035_256_int8.tflite)
| SSD MobileNet v2 0.35 FPN-lite | TensorFlow     | COCO Person dataset    | 416x416x3   | 59.09%                |   576.57        |   2541.43            |   1109.27        | 9.1.0                 |    [link](ssd_mobilenet_v2_fpnlite/ST_pretrainedmodel_public_dataset/coco_2017_person/ssd_mobilenet_v2_fpnlite_035_416/ssd_mobilenet_v2_fpnlite_035_416_int8.tflite)

</details>
<details><summary>TinyYolo v2</summary>

| Models                     | Implementation | Dataset    | Input Resolution | mAP*          | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version  | Source
|---------------------------|----------------|------------|------------------|---------------|--------------|----------------------|----------------------|-----------------------|--------
| Tiny Yolo v2            | TensorFlow     | COCO Person dataset    | 224x224x3   | 30.91%                |   777.48       |   249.35             |   10776        | 9.1.0                 |    [link](tiny_yolo_v2/ST_pretrainedmodel_public_dataset/coco_2017_person/tiny_yolo_v2_224/tiny_yolo_v2_224_int8.tflite)
| Tiny Yolo v2            | TensorFlow     | COCO Person dataset    | 416x416x3   | 41.44%                |   2681.51        |   979.35             |   10776        | 9.1.0                 |    [link](tiny_yolo_v2/ST_pretrainedmodel_public_dataset/coco_2017_person/tiny_yolo_v2_416/tiny_yolo_v2_416_int8.tflite)

</details>
<details><summary>ST Yolo LC</summary>

| Models                     | Implementation | Dataset    | Input Resolution | mAP*          | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version  | Source
|---------------------------|----------------|------------|------------------|---------------|--------------|----------------------|----------------------|-----------------------|--------
| ST Yolo LC v1 tfs   | TensorFlow     | COCO Person dataset    | 192x192x3   | 31.61%                |   61.9        |   166.29              |   276.73              | 9.1.0                 |    [link](st_yolo_lc_v1/ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_lc_v1_192/st_yolo_lc_v1_192_int8.tflite)
| ST Yolo LC v1 tfs   | TensorFlow     | COCO Person dataset    | 224x224x3   | 36.80%                |   84.26        |   217.29              |   276.73              | 9.1.0                 |    [link](st_yolo_lc_v1/ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_lc_v1_224/st_yolo_lc_v1_224_int8.tflite)
| ST Yolo LC v1 tfs   | TensorFlow     | COCO Person dataset    | 256x256x3   | 40.58%                |   110.05        |   278.29              |   276.73              | 9.1.0                 |    [link](st_yolo_lc_v1/ST_pretrainedmodel_public_dataset/coco_2017_person/st_yolo_lc_v1_256/st_yolo_lc_v1_256_int8.tflite)

</details>

\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH = 0.001.

You can get inference time information for each models following links below:
- [ST SSD Mobilenet v1](./st_ssd_mobilenet_v1/README.md)
- [SSD Mobilenet v2](./ssd_mobilenet_v2_fpnlite/README.md)
- [Tiny Yolo v2](./tiny_yolo_v2/README.md)
- [ST Yolo LC](./st_yolo_lc_v1/README.md)

