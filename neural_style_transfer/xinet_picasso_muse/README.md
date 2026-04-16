# Xinet_picasso_muse

## **Use case** : `Neural style transfer`

# Model description

Xinet_picasso_muse is a lightweight Neural Style Transfer approach based on [XiNets](https://openaccess.thecvf.com/content/ICCV2023/papers/Ancilotto_XiNet_Efficient_Neural_Networks_for_tinyML_ICCV_2023_paper.pdf), neural networks especially developed for microcontrollers and embedded applications. It has been trained using the COCO dataset for content images and the painting *La Muse* of **Pablo Picasso** for style image. This model achieves an extremely lightweight transfer style mechanism and high-quality stylized outputs, significantly reducing computational complexity.

Xinet_picasso_muse is implemented initially in Pytorch and is quantized in int8 format using tensorflow lite converter. To reach a better performances, the mirror padding ops have been replaced with zero padding ops.

## Network information
| Network Information     | Value                                |
|-------------------------|--------------------------------------|
|  Framework              | Tensorflow  |
|  Quantization           | int8  |
|  Paper                  | [Link to Paper](https://www.computer.org/csdl/proceedings-article/percom-workshops/2024/10502435/1Wnrsw29p5e) |



## Recommended platform
| Platform | Supported | Recommended |
|----------|-----------|-------------|
| STM32L0  | []        | []          |
| STM32L4  | []       | []          |
| STM32U5  | []       | []          |
| STM32MP1 | []       | []         |
| STM32MP2 | []       | []          |
| STM32N6| [x]       | [x]          |

---
# Performances

## Metrics
Measures are done with default STEdgeAI Core configuration with enabled input / output allocated option.


### Reference **NPU** memory footprint based on COCO dataset

|Model      | Dataset       | Format   | Resolution | Series    | Internal RAM (KiB)| External RAM (KiB)| Weights Flash (KiB) | STEdgeAI Core version |
|----------|------------------|--------|-------------|------------------|------------------|---------------------|-------|-------------------------|
| [Xinet picasso muse](./Public_pretrainedmodel_public_dataset/coco_2017_80_classes_picasso/xinet_a75_picasso_muse_160/xinet_a75_picasso_muse_160_nomp.tflite)  | COCO/Picasso | Int8 | 160x160x3 | STM32N6 |   2568.12 | 1200 | 851.86 | 4.0.0



### Reference **NPU**  inference time based on COCO Person dataset
| Model  | Dataset          | Format | Resolution  | Board            | Execution Engine | Inference time (ms) | Inf / sec   |  STEdgeAI Core version |
|--------|------------------|--------|-------------|------------------|------------------|---------------------|-------|-------------------------|
| [Xinet picasso muse](./Public_pretrainedmodel_public_dataset/coco_2017_80_classes_picasso/xinet_a75_picasso_muse_160/xinet_a75_picasso_muse_160_nomp.tflite)  | COCO/Picasso      | Int8   | 160x160x3  | STM32N6570-DK   |   NPU/MCU      |     93.96         |   10.6      |     4.0.0   |


## Retraining and Integration in a Simple Example
Retraining and deployment services are currently not provided for this model. They should be supported in the future releases.


## References

<a id="1">[1]</a> "Painting the Starry Night using XiNets" Alberto Ancilotto, Elisabetta Farella - 2024 IEEE International Conference on Pervasive Computing [Link](https://www.computer.org/csdl/proceedings-article/percom-workshops/2024/10502435/1Wnrsw29p5e)

