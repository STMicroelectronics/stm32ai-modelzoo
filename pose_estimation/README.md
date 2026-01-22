# Pose estimation STM32 model zoo

Models are stored depending on the way they have been trained :
* `ST_pretrainedmodel_public_dataset` folder contains models trained by ST using public datasets
* `ST_pretrainedmodel_custom_dataset` folder contains models trained by ST using custom datasets
* `Public_pretrainedmodel_public_dataset` folder contains public models using public datasets

## List of available models families depending on UC features:
* [hand landmarks](./handlandmarks/README.md) : single pose estimation with 21 keypoints
* [head landmarks](./headlandmarks/README.md) : single pose estimation with 468 and 478 keypoints
* [movenet](./movenet/README.md) : single pose estimation with 13 and 17 keypoints
* [yolo v8 pose](./yolov8n_pose/README.md) : multi pose estimation with 17 keypoints
* [yolo 11 pose](./yolov11n_pose/README.md) : multi pose estimation with 17 keypoints

