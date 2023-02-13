# Overview of object detection STM32 model zoo


The STM32 model zoo includes several models for object detection use case pre-trained on custom and public datasets.
Under each model directory, you can find the following model categories:

- `Public_pretrainedmodel_public_dataset` contains public object detection models trained on public datasets.
- `ST_pretrainedmodel_custom_dataset` contains different object detection models trained on ST custom datasets using our [training scripts](../scripts/training/README.md). 
- `ST_pretrainedmodel_public_dataset` contains different object detection models trained on various public datasets following the [training section](../scripts/training/README.md) in STM32 model zoo.





<a name="ic_models"></a>
## Object detection models

The table below summarizes the performance of the models, as well as their memory footprints generated using STM32Cube.AI (v7.3.0) for deployment purposes.

By default, the results are provided for quantized Int8 models.
When nothing is precised in the model name, training is done using transfer learning technique from a pre-trained model. Else, "tfs" stands for "training from scratch".


| Models                     | Implementation | Dataset    | Input Resolution | mAP*          | MACCs    (M) | Activation RAM (KiB) | Weights Flash (KiB) | Source
|---------------------------|----------------|------------|------------------|---------------|--------------|----------------------|----------------------|--------
| SSD MobileNet v1 0.25   | TensorFlow     | COCO Person dataset    | 192x192x3   | 33.84%                |   40.57        |   195.6            |   438.28        |    [link](ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_192/ssd_mobilenet_v1_025_192_int8.tflite)
| SSD MobileNet v1 0.25   | TensorFlow     | COCO Person dataset    | 224x224x3   | 43.86%                |   60.14        |   333.25            |   595.66        |    [link](ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_224/ssd_mobilenet_v1_025_224_int8.tflite)
| SSD MobileNet v1 0.25   | TensorFlow     | COCO Person dataset    | 256x256x3   | 47.03%                |   72.72        |   347.3            |   595.66        |    [link](ssd_mobilenetv1/ST_pretrainedmodel_public_dataset/COCO/ssd_mobilenet_v1_0.25_256/ssd_mobilenet_v1_025_256_int8.tflite)
| ST Yolo LC v1 tfs   | TensorFlow     | COCO Person dataset    | 192x192x3   | 39.92%                |   61.9        |   157.44              |   276.73              |    Please Contact Edge.ai@st.com
| ST Yolo LC v1 tfs   | TensorFlow     | COCO Person dataset    | 224x224x3   | 42.75%                |   84.25        |   210.69              |   276.73              |    Please Contact Edge.ai@st.com
| ST Yolo LC v1 tfs   | TensorFlow     | COCO Person dataset    | 256x256x3   | 45.09%                |   110.05        |   271.94              |   276.73              |    Please Contact Edge.ai@st.com

\* EVAL_IOU = 0.4, NMS_THRESH = 0.5, SCORE_THRESH = 0.001
