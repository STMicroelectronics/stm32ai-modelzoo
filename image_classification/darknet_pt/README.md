# DarkNetTiny

## **Use case** : `Image classification`

# Model description


DarkNet is a convolutional neural network architecture that serves as the backbone for the YOLO (You Only Look Once) object detection series. It is designed for **efficient feature extraction with a focus on real-time object detection applications**.

DarkNetTiny is the compact version designed for embedded deployment. It features **Leaky ReLU activations**, **batch normalization** after every convolutional layer, and uses **global average pooling** instead of fully connected layers to reduce parameter count.

The straightforward stack of convolutional layers makes it easy to implement and modify, while maintaining competitive performance on edge devices.

(source: https://arxiv.org/abs/1804.02767)

The model is quantized to **int8** using **ONNX Runtime** and exported for efficient deployment.

## Network information


| Network Information | Value |
|--------------------|-------|
| Framework          | Torch |
| MParams            | ~1.04 M |
| Quantization       | Int8 |
| Provenance         | https://github.com/pjreddie/darknet |
| Paper              | https://arxiv.org/abs/1804.02767 |

## Network inputs / outputs


For an image resolution of NxM and P classes

| Input Shape | Description |
| ----- | ----------- |
| (1, N, M, 3) | Single NxM RGB image with UINT8 values between 0 and 255 |

| Output Shape | Description |
| ----- | ----------- |
| (1, P) | Per-class confidence for P classes in FLOAT32|


## Recommended platforms


| Platform | Supported | Recommended |
|----------|-----------|-----------|
| STM32L0  |[]|[]|
| STM32L4  |[]|[]|
| STM32U5  |[]|[]|
| STM32H7  |[]|[]|
| STM32MP1 |[]|[]|
| STM32MP2 |[]|[]|
| STM32N6  |[x]|[x]|

# Performances

## Metrics

- Measures are done with default STEdgeAI Core configuration with enabled input / output allocated option.
- All the models are trained from scratch on Imagenet dataset 

### Reference **NPU** memory footprint on Imagenet dataset (see Accuracy for details on dataset)
| Model | Dataset | Format | Resolution | Series | Internal RAM (KiB) | External RAM (KiB) | Weights Flash (KiB) | STEdgeAI Core version |
|-------|---------|--------|------------|--------|--------------|--------------|---------------|----------------------|
| [darknettiny_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/darknettiny_pt_224/darknettiny_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6 | 539 | 0 | 1067.11 | 3.0.0 |

### Reference **NPU** inference time on Imagenet dataset (see Accuracy for details on dataset)
| Model | Dataset  | Format | Resolution | Board | Execution Engine | Inference time (ms) | Inf / sec | STEdgeAI Core version |
|-------|---------|--------|--------|------------|-------|-----------------|-------------------|---------------------|
| [darknettiny_pt_224](./Public_pretrainedmodel_public_dataset/Imagenet/darknettiny_pt_224/darknettiny_pt_224_qdq_int8.onnx) | Imagenet | Int8 | 224×224×3 | STM32N6570-DK | NPU/MCU | 7.54 | 132.63 | 3.0.0  |

### Accuracy with Imagenet dataset

Dataset details: [link](https://www.image-net.org)
Number of classes: 1000.
To perform the quantization, we calibrated the activations with a random subset of the training set.
For the sake of simplicity, the accuracy reported here was estimated on the 50000 labelled images of the validation set.

| model | Format | Resolution | Top 1 Accuracy |
| --- | --- | --- | --- |
| [darknettiny_pt](./Public_pretrainedmodel_public_dataset/Imagenet/darknettiny_pt_224/darknettiny_pt_224.onnx) | Float | 224x224x3 | 60.34 % |
| [darknettiny_pt](./Public_pretrainedmodel_public_dataset/Imagenet/darknettiny_pt_224/darknettiny_pt_224_qdq_int8.onnx) | Int8 | 224x224x3 | 52.64 % |



## Retraining and Integration in a simple example:

Please refer to the stm32ai-modelzoo-services GitHub [here](https://github.com/STMicroelectronics/stm32ai-modelzoo-services)



# References

<a id="1">[1]</a> - **Dataset**: Imagenet (ILSVRC 2012) — https://www.image-net.org/

<a id="2">[2]</a> - **Model**: DarkNet — https://github.com/pjreddie/darknet
