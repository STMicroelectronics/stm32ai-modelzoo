# Head landmarks quantized

## **Use case** : `Pose estimation`

# Model description


Head landmarks is a single pose estimation model targeted for real-time processing implemented in ONNX.

The model is quantized in int8 format using onnx quantizer.

## Network information


| Network information     |  Value          |
|-------------------------|-----------------|
|  Framework              | ONNX Runtime    |
|  Quantization           | int8            |
|  Provenance             | https://github.com/PINTO0309/PINTO_model_zoo/tree/main/032_FaceMesh
|  Paper                  | https://developers.google.com/ml-kit/vision/face-mesh-detection |


## Networks inputs / outputs

With an image resolution of NxM with K keypoints to detect :

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, 1, 1, Kx2) | FLOAT values Where Kx2 are the (x,y) values of each keypoints |

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

### Reference **NPU** memory footprint
|Model      | Format   | Resolution | Series    | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB)  | STEdgeAI Core version |
|----------|--------|-------------|------------------|------------------|---------------------|-------|-------------------------|
| [head_landmarks](Public_pretrainedmodel_custom_dataset/custom_dataset_heads_468kpts/facelandmarksv1_192_int8.onnx)  | Int8 | 224x224x3 | STM32N6 | 1739.5  | 0.0 | 3246.47 | 4.0.0 |

### Reference **NPU**  inference time
| Model  | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec     |  STEdgeAI Core version |
|--------|--------|-------------|------------------|------------------|---------------------|-------|-------------------------|
| [head_landmarks](Public_pretrainedmodel_custom_dataset/custom_dataset_heads_468kpts/facelandmarksv1_192_int8.onnx) | Int8     | 224x224x3  | STM32N6570-DK   | NPU/MCU | 5.48 | 182.4 | 4.0.0 |


