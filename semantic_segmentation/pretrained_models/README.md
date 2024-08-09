# Overview of semantic segmentation STM32 model zoo

The STM32 model zoo includes several models for semantic segmentation use cases pre-trained on custom and public datasets. Under each model directory, you can find the following model categories:

- `Public_pretrainedmodel_public_dataset` contains public semantic segmentation models trained on public datasets.
- `ST_pretrainedmodel_custom_dataset` contains different semantic segmentation models trained on ST custom datasets using our [training scripts](../src/training/README.md).
- `ST_pretrainedmodel_public_dataset` contains different semantic segmentation models trained on various public datasets following the [training section](../src/training/README.md) in STM32 model zoo.



<a name="seg_models"></a>
## Semantic segmentation models

The table below summarizes the performance of the models, as well as their memory footprints for deployment purposes. All the footprints reported here are calculated choosing STM32MP257F-EV1 board as target board.

By default, the results are provided for 'per channel' quantized Int8 models. 'per channel' means all weights contributing to a given layer output channel are quantized with one unique (scale, offset) couple.
The alternative is 'per tensor' quantization which means that the full weight tensor of a given layer is quantized with one unique (scale, offset) couple.
It is obviously more challenging to preserve original float model accuracy using 'per tensor' quantization. But this method is particularly well suited to fully exploit STM32MP257F-EV1 HW design.

Also, the following naming convention is used to specify the training technique of each model:

- `tfs` stands for "training from scratch", meaning that the model weights were randomly initialized before training.
- `tl` stands for "transfer learning", meaning that the model backbone weights were initialized from a pre-trained model, then only the last layer was unfrozen during the training.
- `fft` stands for "full fine-tuning", meaning that the full model weights were initialized from a transfer learning pre-trained model, and all the layers were unfrozen during the training.

The model, without any of the above suffixes, was downloaded from [the
TensorFlow DeepLabV3 page on Kaggle](https://www.kaggle.com/models/tensorflow/deeplabv3/).

Below sections contain detailed information on models memory usage and accuracies (click on the arrows to expand). Accuracies and IoU are evaluated on PASCAL VOC 2012 validation list of images.
IoU are averaged on all classes including background.

<details><summary>Deeplab v3</summary>

| Models                                                | Implementation | Dataset                | Input Resolution | Accuracy (%) | average IoU | Activation RAM (MiB) | Weights Flash (MiB) | STM32Cube.AI version      | Source                                                                                                                                                               |
|-------------------------------------------------------|----------------|------------------------|------------------|--------------|-------------|----------------------|---------------------|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| deeplabv3_257_int8_per_tensor                         | TensorFlow     |  COCO 2017 + PASCAL VOC 2012 | 257x257x3        | 88.66        | 59.06       |       25.7            |       0.86        | 9.1.0                     | Available in X-LINUX-AI package [link](https://www.st.com/en/embedded-software/x-linux-ai.html)                                                                              |
| deeplab_v3_mobilenetv2_05_fft_float32 | Tensorflow     |  COCO 2017 + PASCAL VOC 2012        | 512x512x3        | 93.29       | 73.44       | /                | /              | 9.1.0                     | [link](./deeplab_v3/ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512_fft/deeplab_v3_mobilenetv2_05_16_512_fft.h5) 
| deeplab_v3_mobilenetv2_05_fft_per_channel | Tensorflow     |  COCO 2017 + PASCAL VOC 2012        | 512x512x3        | 91.3        | 67.32       |     57.38        | 7.63             | 9.1.0                     | [link](./deeplab_v3/ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512_fft/deeplab_v3_mobilenetv2_05_16_512_fft_int8.tflite) |
deeplab_v3_mobilenetv2_05_fft_int8_f32_per_channel | Tensorflow     |  COCO 2017 + PASCAL VOC 2012        | 512x512x3        |    92.83     |   71.93     |      55.91       |       6.2        | 9.1.0                     | [link](./deeplab_v3/ST_pretrainedmodel_public_dataset/coco_2017_pascal_voc_2012/deeplab_v3_mobilenetv2_05_16_512_fft/deeplab_v3_mobilenetv2_05_16_512_fft_int8_f32.tflite) |
</details>


You can get inference time information for each models following links below:
- [deeplab_v3](./deeplab_v3/README.md)
