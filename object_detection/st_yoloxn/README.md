# ST Yolo X quantized

## **Use case** : `Object detection`

# Model description


ST Yolo X is a real-time object detection model targeted for real-time processing implemented in Tensorflow.
This is an optimized ST version of the well known yolo x, quantized in int8 format using tensorflow lite converter.

## Network information

| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             |   |
|  Paper                  |   |



## Network inputs / outputs

For an image resolution of NxM and NC classes

| Input Shape | Description |
| ----- | ----------- |
| (1, W, H, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
|   |    |


## Recommended Platforms

| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | [x]       | []          |
| STM32MP1 | [x]       | []          |
| STM32MP2 | [x]       | [x]         |
| STM32N6  | [x]       | [x]         |


# Performances

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                                             | Hyperparameters (depth_width) | Dataset          | Format   | Resolution   | Series   |   Internal RAM (KiB) |   External RAM (KiB) |   Weights Flash (KiB) | STEdgeAI Core version   |
|-----------------------------------------------------------------------------------------------------------------------------------|-------------------------------|------------------|----------|--------------|----------|----------------------|----------------------|------------------------|-------------------------|
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_int8.tflite)      | d033_w025                     | COCO-Person      | Int8     | 192x192x3    | STM32N6  |                 333  |                    0 |                 877.66 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_int8.tflite)      | d033_w025                     | COCO-Person      | Int8     | 256x256x3    | STM32N6  |                 624  |                    0 |                 884.91 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_int8.tflite)      | d033_w025                     | COCO-Person      | Int8     | 320x320x3    | STM32N6  |                1125  |                    0 |                 895.03 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite)      | d033_w025                     | COCO-Person      | Int8     | 416x416x3    | STM32N6  |               2676.12|                    0 |                 904.03 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_int8.tflite)      | d050_w040                     | COCO-Person      | Int8     | 256x256x3    | STM32N6  |                 833  |                    0 |                2414.64 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_int8.tflite)      | d100_w025                     | COCO-Person      | Int8     | 480x480x3    | STM32N6  |               2707.5 |                    0 |                1173.25 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite)             | d033_w025                     | ST-Person        | Int8     | 416x416x3    | STM32N6  |               2676.12|                    0 |                 906.28 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d067_w025_416/st_yoloxn_d067_w025_416_int8.tflite)             | d067_w025                     | ST-Person        | Int8     | 416x416x3    | STM32N6  |               2681.41|                    0 |                1039.78 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_416/st_yoloxn_d100_w025_416_int8.tflite)             | d100_w025                     | ST-Person        | Int8     | 416x416x3    | STM32N6  |               2676.12|                    0 |                1173.28 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_int8.tflite)             | d100_w025                     | ST-Person        | Int8     | 480x480x3    | STM32N6  |               2707.5 |                    0 |                1173.25 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_w4_78.84%_w8_21.16%_a8_100%_map_47.33.onnx) | d100_w025 | ST-Person        |W4A8 | 480x480x3    | STM32N6  |               2593   |                    0 |                 738.53 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_int8.onnx) | d100_w025 | COCO-80-classes | W4A8 | 480x480x3 | STM32N6  |               3491.48|                    0 |                1217.59 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_qdq_w4_83.16%_w8_16.84%_a8_100%_map_37.34.onnx) | d033_w025 | COCO-Person | W4A8 | 192x192x3 | STM32N6  |                360   |                    0 |                 519.06 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_qdq_w4_83.16%_w8_16.84%_a8_100%_map_44.43.onnx) | d033_w025 | COCO-Person | W4A8 | 256x256x3 | STM32N6  |                624   |                    0 |                 526.31 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_qdq_w4_59.47%_w8_40.53%_a8_100%_map_50.61.onnx) | d033_w025 | COCO-Person | W4A8 | 320x320x3 | STM32N6  |               1125   |                    0 |                 638.67 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_qdq_w4_76.19%_w8_23.81%_a8_100%_map_53.97.onnx) | d033_w025 | COCO-Person | W4A8 | 416x416x3 | STM32N6  |               2670.84|                    0 |                 575.53 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_qdq_w4_62.53%_w8_37.47%_a8_100%_map_49.2.onnx)  | d050_w040 | COCO-Person | W4A8 | 256x256x3 | STM32N6  |                835   |                    0 |                1671.08 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_w4_55.23%_w8_44.77%_a8_100%_map_59.9.onnx)  | d100_w025 | COCO-Person | W4A8 | 480x480x3 | STM32N6  |               2707.5 |                    0 |                 868.8  | 3.0.0                   |


### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model                                                                                                                             | Hyperparameters (depth_width) | Dataset              | Format   | Resolution   | Board         | Execution Engine   |   Inference time (ms) |   Inf / sec | STEdgeAI Core version   |
|-----------------------------------------------------------------------------------------------------------------------------------|-------------------------------|----------------------|----------|--------------|---------------|--------------------|-----------------------|-------------|-------------------------|
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_int8.tflite)      | d033_w025                     | COCO-Person          | Int8     | 192x192x3    | STM32N6570-DK | NPU/MCU            |                  6.63 |      150.74 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_int8.tflite)      | d033_w025                     | COCO-Person          | Int8     | 256x256x3    | STM32N6570-DK | NPU/MCU            |                  9.42 |      106.17 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_int8.tflite)      | d033_w025                     | COCO-Person          | Int8     | 320x320x3    | STM32N6570-DK | NPU/MCU            |                 13.29 |       75.26 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite)      | d033_w025                     | COCO-Person          | Int8     | 416x416x3    | STM32N6570-DK | NPU/MCU            |                 21.3  |       46.95 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_int8.tflite)      | d050_w040                     | COCO-Person          | Int8     | 256x256x3    | STM32N6570-DK | NPU/MCU            |                 20.12 |       49.70 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_int8.tflite)      | d100_w025                     | COCO-Person          | Int8     | 480x480x3    | STM32N6570-DK | NPU/MCU            |                 35.8  |       27.93 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite)             | d033_w025                     | ST-Person            | Int8     | 416x416x3    | STM32N6570-DK | NPU/MCU            |                 21.66 |       46.16 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d067_w025_416/st_yoloxn_d067_w025_416_int8.tflite)             | d067_w025                     | ST-Person            | Int8     | 416x416x3    | STM32N6570-DK | NPU/MCU            |                 24.37 |       41.02 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_416/st_yoloxn_d100_w025_416_int8.tflite)             | d100_w025                     | ST-Person            | Int8     | 416x416x3    | STM32N6570-DK | NPU/MCU            |                 27.02 |       36.99 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_int8.tflite)             | d100_w025                     | ST-Person            | Int8     | 480x480x3    | STM32N6570-DK | NPU/MCU            |                 35.8  |       27.93 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_w4_78.84%_w8_21.16%_a8_100%_map_47.33.onnx) | d100_w025 | ST-Person | W4A8 | 480x480x3    | STM32N6570-DK | NPU/MCU            |                 34.27 |       29.18 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_int8.onnx) | d100_w025 | COCO-80-classes      | W4A8 | 480x480x3  | STM32N6570-DK | NPU/MCU            |                 49.34 |       20.27 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_qdq_w4_83.16%_w8_16.84%_a8_100%_map_37.34.onnx) | d033_w025 | COCO-Person | W4A8 | 192x192x3 | STM32N6570-DK | NPU/MCU            |                  6.33 |      157.96 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_qdq_w4_83.16%_w8_16.84%_a8_100%_map_44.43.onnx) | d033_w025 | COCO-Person | W4A8 | 256x256x3 | STM32N6570-DK | NPU/MCU            |                  8.20 |      121.95 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_qdq_w4_59.47%_w8_40.53%_a8_100%_map_50.61.onnx) | d033_w025 | COCO-Person | W4A8 | 320x320x3 | STM32N6570-DK | NPU/MCU            |                 11.82 |       84.66 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_qdq_w4_76.19%_w8_23.81%_a8_100%_map_53.97.onnx) | d033_w025 | COCO-Person | W4A8 | 416x416x3 | STM32N6570-DK | NPU/MCU            |                 19.87 |       50.32 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_qdq_w4_62.53%_w8_37.47%_a8_100%_map_49.2.onnx)  | d050_w040 | COCO-Person | W4A8 | 256x256x3 | STM32N6570-DK | NPU/MCU            |                 18.34 |       54.52 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_w4_55.23%_w8_44.77%_a8_100%_map_59.9.onnx)  | d100_w025 | COCO-Person | W4A8 | 480x480x3 | STM32N6570-DK | NPU/MCU            |                 34.71 |       28.80 | 3.0.0                   |


### Reference **MCU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)

| Model                                                                                                                             | Hyperparameters (depth_width) | Format   | Resolution   | Series   |   Activation RAM (KiB) |   Runtime RAM (KiB) |   Weights Flash (KiB) |   Code Flash (KiB) |   Total RAM |   Total Flash | STEdgeAI Core version   |
|-----------------------------------------------------------------------------------------------------------------------------------|-------------------------------|----------|--------------|----------|------------------------|---------------------|-----------------------|--------------------|-------------|---------------|-------------------------|
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_int8.tflite)      | d033_w025                     | Int8     | 192x192x3    | STM32H7  |                 184.92 |               12.54 |                891.18 |             108.38 |      197.46 |        999.56 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_int8.tflite)      | d033_w025                     | Int8     | 256x256x3    | STM32H7  |                 324.92 |               12.54 |                891.18 |             108.38 |      337.46 |        999.84 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_int8.tflite)      | d050_w040                     | Int8     | 256x256x3    | STM32H7  |                 451.4  |               15.63 |               2435.76 |             151.42 |      467.03 |       2587.18 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_int8.tflite)      | d033_w025                     | Int8     | 320x320x3    | STM32H7  |                 504.92 |               12.54 |                891.18 |             108.38 |      517.46 |       1000.04 | 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite)      | d033_w025                     | Int8     | 416x416x3    | STM32H7  |                 849.92 |               12.54 |                891.18 |             108.38 |      862.46 |        999.99 | 3.0.0                   |


### Reference **MCU** inference time based on COCO Person dataset (see Accuracy for details on dataset)

| Model                                                                                                                             | Hyperparameters (depth_width) | Format   | Resolution   | Board            | Execution Engine   | Frequency   |   Inference time (ms) | STEdgeAI Core version   |
|-----------------------------------------------------------------------------------------------------------------------------------|-------------------------------|----------|--------------|------------------|--------------------|-------------|-----------------------|-------------------------|
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_int8.tflite)      | d033_w025                     | Int8     | 192x192x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                 357.79| 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_int8.tflite)      | d033_w025                     | Int8     | 256x256x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                 641.66| 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_int8.tflite)      | d050_w040                     | Int8     | 256x256x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                1698.36| 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_int8.tflite)      | d033_w025                     | Int8     | 320x320x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                1026.35| 3.0.0                   |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite)      | d033_w025                     | Int8     | 416x416x3    | STM32H747I-DISCO | 1 CPU              | 400 MHz     |                1797.73| 3.0.0                   |


### AP on COCO Person dataset

Dataset details: [link](https://cocodataset.org/#download) , License [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode) , Quotation[[1]](#1) , Number of classes: 80, Number of images: 118,287

| Model | Hyperparameters (depth_width) | Format | Resolution | Depth Multiplier | Width Multiplier | Anchors | AP |
|-------|------------------------------|--------|------------|------------------|------------------|---------|----|
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_int8.tflite) | d033_w025 | Int8  | 192x192x3 | 0.33 | 0.25 | 1 | 38.16 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192.keras)      | d033_w025 | Float | 192x192x3 | 0.33 | 0.25 | 1 | 38.82 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_192/st_yoloxn_d033_w025_192_qdq_w4_83.16%_w8_16.84%_a8_100%_map_37.34.onnx) | d033_w025 | W4A8 | 192x192x3 | 0.33 | 0.25 | 1 | 37.34 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_int8.tflite) | d033_w025 | Int8  | 256x256x3 | 0.33 | 0.25 | 1 | 44.85 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256.keras)      | d033_w025 | Float | 256x256x3 | 0.33 | 0.25 | 1 | 45.12 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_256/st_yoloxn_d033_w025_256_qdq_w4_83.16%_w8_16.84%_a8_100%_map_44.43.onnx) | d033_w025 | W4A8 | 192x192x3 | 0.33 | 0.25 | 1 | 44.43 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_int8.tflite) | d050_w040 | Int8  | 256x256x3 | 0.5  | 0.4  | 1 | 50.05 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256.keras)      | d050_w040 | Float | 256x256x3 | 0.5  | 0.4  | 1 | 51.07 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d050_w040_256/st_yoloxn_d050_w040_256_qdq_w4_62.53%_w8_37.47%_a8_100%_map_49.2.onnx) | d050_w040 | W4A8 | 256x256x3 | 0.33 | 0.25 | 1 | 49.2 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_int8.tflite) | d033_w025 | Int8  | 320x320x3 | 0.33 | 0.25 | 1 | 51.17 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320.keras)      | d033_w025 | Float | 320x320x3 | 0.33 | 0.25 | 1 | 51.69 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_320/st_yoloxn_d033_w025_320_qdq_w4_59.47%_w8_40.53%_a8_100%_map_50.61.onnx) | d033_w025 | W4A8 | 320x320x3 | 0.33 | 0.25 | 1 | 50.61 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite) | d033_w025 | Int8  | 416x416x3 | 0.33 | 0.25 | 1 | 54.8 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416.keras)      | d033_w025 | Float | 416x416x3 | 0.33 | 0.25 | 1 | 54.82 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_qdq_w4_76.19%_w8_23.81%_a8_100%_map_53.97.onnx) | d033_w025 | W4A8 | 416x416x3 | 0.33 | 0.25 | 1 | 53.97 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_int8.tflite) | d100_w025 | Int8  | 480x480x3 | 1.0  | 0.25 | 3 | 61.1 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480.keras)      | d100_w025 | Float | 480x480x3 | 1.0  | 0.25 | 3 | 61.7 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_w4_55.23%_w8_44.77%_a8_100%_map_59.9.onnx) | d100_w025 | W4A8 | 480x480x3 | 0.33 | 0.25 | 1 | 59.9 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416_int8.tflite)       | d033_w025 | Int8  | 416x416x3 | 0.33 | 0.25 | 1 | 42.58 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d033_w025_416/st_yoloxn_d033_w025_416.keras)             | d033_w025 | Float | 416x416x3 | 0.33 | 0.25 | 1 | 44.28 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d067_w025_416/st_yoloxn_d067_w025_416_int8.tflite)       | d067_w025 | Int8  | 416x416x3 | 0.67 | 0.25 | 1 | 46.2 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d067_w025_416/st_yoloxn_d067_w025_416.keras)             | d067_w025 | Float | 416x416x3 | 0.67 | 0.25 | 1 | 46.7 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_416/st_yoloxn_d100_w025_416_int8.tflite)       | d100_w025 | Int8  | 416x416x3 | 1.0  | 0.25 | 1 | 47.27 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_416/st_yoloxn_d100_w025_416.keras)             | d100_w025 | Float | 416x416x3 | 1.0  | 0.25 | 1 | 48.14 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_int8.tflite)       | d100_w025 | Int8  | 480x480x3 | 1.0  | 0.25 | 1 | 48.15 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480.keras)             | d100_w025 | Float | 480x480x3 | 1.0  | 0.25 | 1 | 48.68 % |
| [st_yoloxn](ST_pretrainedmodel_custom_dataset/st_person/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480_qdq_w4_78.84%_w8_21.16%_a8_100%_map_47.33.onnx) | d100_w025 | W4A8 | 480x480x3 | 1.0  | 0.25 | 1 | 47.3 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480.tflite) | d100_w025 | Int8  | 480x480x3 | 1.0  | 0.25 | 1 | 34.3 % |
| [st_yoloxn](ST_pretrainedmodel_public_dataset/coco_2017_80_classes/st_yoloxn_d100_w025_480/st_yoloxn_d100_w025_480.keras)  | d100_w025 | Float | 480x480x3 | 1.0  | 0.25 | 1 | 35.7 % |

\* EVAL_IOU = 0.5, NMS_THRESH = 0.5, SCORE_THRESH = 0.001, MAX_DETECTIONS = 100

## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


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
