# Hand landmarks quantized

## **Use case** : `Pose estimation`

# Model description


Hand landmarks is a single pose estimation model targeted for real-time processing implemented in Tensorflow.

The model is quantized in int8 format using tensorflow lite converter.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | TensorFlow Lite |
|  Quantization           | int8            |
|  Provenance             | https://github.com/PINTO0309/PINTO_model_zoo/tree/main/033_Hand_Detection_and_Tracking
|  Paper                  | https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Hand%20Tracking%20(Lite_Full)%20with%20Fairness%20Oct%202021.pdf |


## Networks inputs / outputs

With an image resolution of NxM with K keypoints to detect :

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, Kx3) | FLOAT values Where Kx3 are the (x,y,conf) values of each keypoints |

## Recommended Platforms

| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []        | []          |
| STM32U5  | []        | []          |
| STM32H7  | []        | []          |
| STM32MP1 | [x]       | []          |
| STM32MP2 | [x]       | [x]         |
| STM32N6  | [x]       | [x]         |

# Performances

## Metrics

Measures are done with default STM32Cube.AI configuration with enabled input / output allocated option.

### Reference **NPU** memory footprint based on COCO Person dataset (see Accuracy for details on dataset)
|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STM32Cube.AI version | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [hand_landmarks](Public_pretrainedmodel_custom_dataset/custom_dataset_hands_21kpts/hand_landmarks_full_224_int8_pc.tflite)  | COCO-Person | Int8 | 224x224x3 | STM32N6 |                 1739.5   | 0.0 | 3283.38 | 10.0.0  | 2.0.0 |

### Reference **NPU**  inference time based on COCO Person dataset (see Accuracy for details on dataset)
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   | STM32Cube.AI version  |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|----------------------|-------------------------|
| [hand_landmarks](Public_pretrainedmodel_custom_dataset/custom_dataset_hands_21kpts/hand_landmarks_full_224_int8_pc.tflite) | custom_dataset_hands_21kpts      | Int8     | 224x224x3  | STM32N6570-DK   | NPU/MCU | 20.75 | 48.19 | 10.0.0 | 2.0.0 |


