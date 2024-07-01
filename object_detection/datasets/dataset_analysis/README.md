# <a>Dataset analysis</a>

`dataset_analysis.py` tool analyzes the distribution of the dataset (classes and labels), and should be used before creating the .tfs files

It first provides some information on the dataset classes and labels like the number of images, statistics on the number of labels per image, images with no detection, number of classes and detections per classes. Corresponding histograms are then printed and stored.
A second step consists in providing more data in case you want to filter a bit the dataset :  
- Calculates the percentage of filtered images corresponding to the maximum number of detections kept per image : `max_detections` usage in yaml below
- Calculates the maximum number of detections in the input images corresponding to the max percentage of the dataset to be filtered by removing images with a lot a detections : `max_percentage_filtered` usage in yaml below

## <a>Example</a>

```yaml
dataset:
  dataset_name: Pascal_VOC_2007
  dataset_path: ../<dataset_name>/train

settings:
  max_detections: 40
  max_percentage_filtered: 1.5
```

In example above Pascal_VOC_2007 will be analyzed, and :
- percentage of the dataset corresponding to more than 40 detections (max_detections) will be outputted
- max number of detections per image corresponding to 1.5% of the provided dataset path will be outputted

This information can be used as input to `dataset_create_tfs` in case you want to filter a bit the dataset to remove images with too much detections.

To analyze provided dataset, run the script from current directory with the following command:

```bash
python dataset_analysis.py
```
Or in case you launch it from another directory (example from object_detection/datasets):
```bash
python dataset_analysis.py --config-path ./dataset_analysis/ --config-name dataset_config.yaml
```




