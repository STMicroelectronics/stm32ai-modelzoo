# Yunet

## **Use case** : `Face detection`

# Model description

Yunet is a lightweight and efficient face detection model optimized for real-time applications on embedded devices. Yunet designed specifically for detecting faces and 5 keypoints (2x eyes, 2x mouth, nose). The models are quantized to int8 format using ONNX QDQ to reduce memory footprint and improve inference speed on resource-constrained hardware.

Yunet is known for its fast inference and accuracy, making it suitable for applications such as face tracking, augmented reality, and user authentication.

## Network information

| Network information | Value                                                                      |
|---------------------|----------------------------------------------------------------------------|
| Framework           | ONNX                                                                       |
| Quantization        | int8                                                                       |
| Provenance          | https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet |

## Network inputs / outputs

| Input Shape  | Description                                              |
|--------------|----------------------------------------------------------|
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |



YuNet produces multi-scale outputs for face detection and landmark localization. Yunet has 3 strides (32,16,8), for each stride S, outputs have the following shapes.

| Output Shape | Description                                           |
|--------------|-------------------------------------------------------|
| (1, F, 1)    | **Classification scores:** Probability of face        |
| (1, F, 1)    | **IoU scores:** Predicted IoU                         |
| (1, F, 4)    | **Bounding box regression:** [dx, dy, dw, dh] offsets |
| (1, F, 10)   | **Landmark regression:** 5 facial landmarks (x, y)    |

Where:

- **F = (N/S)×(M/S)**  (Total number of detections for a given stride S)
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

## Performances

### Metrics

Performance metrics are measured using default STM32Cube.AI configurations with input/output allocated buffers.

| Model                                                                                                | Dataset    | Format | Resolution | Series  | Internal RAM (KB) | External RAM (KB) | Weights Flash (KB) | STEdgeAI Core version |
|------------------------------------------------------------------------------------------------------|------------|--------|------------|---------|-------------------|-------------------|--------------------|-----------------------|
| [yunet 320x320](Public_pretrainedmodel_public_dataset/widerface/yunetn_320/yunetn_320_qdq_int8.onnx) | WIDER FACE | Int8   | 3x320x320  | STM32N6 | 1130.49           | 0                 | 92.31              | 3.0.0                 |

### Reference **NPU** inference time (example)

| Model                                                                                                | Dataset    | Format | Resolution | Board         | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|------------------------------------------------------------------------------------------------------|------------|--------|------------|---------------|------------------|---------------------|-----------|-----------------------|
| [yunet 320x320](Public_pretrainedmodel_public_dataset/widerface/yunetn_320/yunetn_320_qdq_int8.onnx) | WIDER FACE | Int8   | 3x320x320  | STM32N6570-DK | NPU/MCU          | 6.74                | 147.36    | 3.0.0                 |


## Integration and support

For integration examples and additional services, please refer to the STM32 AI model zoo services repository:  
[https://github.com/STMicroelectronics/stm32ai-modelzoo-services](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)


## References

- Yunet paper: [https://link.springer.com/article/10.1007/s11633-023-1423-y](https://link.springer.com/article/10.1007/s11633-023-1423-y)  
- MediaPipe Yunet model repository: [https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet]https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet)  
- WIDER FACE dataset: [http://shuoyang1213.me/WIDERFACE/](http://shuoyang1213.me/WIDERFACE/)