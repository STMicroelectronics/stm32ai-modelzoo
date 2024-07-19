# <a xid="">Yolo Darknet Dataset Converter</a>

`converter.py` converts datasets in COCO format to YOLO Darknet format. It currently supports the following formats:
- COCO


## <a>Example</a>

Let's say the the COCO dataset un raw format is in PATH_TO_COCO.

To convert this dataset to Yolo Darknet TXT format for single pose estimation, run the script with the following command:

```
python converter.py --path PATH_TO_COCO --pose single --keypoints 13 --outputdir ./pose_estimation
```

For multiple pose estimation, run the script with the following command:

```
python converter.py --path PATH_TO_COCO --pose multi --keypoints 17 --outputdir ./pose_estimation
```

The converted datasets will be saved in the `./pose_estimation/single/13kpts/train|val` and `./pose_estimation/multi/17kpts/train|val` directories.