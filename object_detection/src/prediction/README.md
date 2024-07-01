# Object detection prediction

Our prediction service is a simple and efficient tool that allows users to upload their TensorFlow Lite (.tflite) or Keras (.h5) model and a set of images for prediction. The service then uses the model to predict the class and position of each object in the image of the set. This can be particularly useful for anyone working with object detection tasks and looking for a quick and easy way to generate predictions. Our prediction service is designed to be user-friendly and accessible, making it an ideal solution for both beginners and experts alike.

## <a id="">Table of contents</a>

<details open><summary><a href="#1"><b>1. Configure the yaml file</b></a></summary><a id="1"></a>

To use the prediction service, users must fill in the 'prediction' section of the [user_config.yaml](../user_config.yaml) file like the [prediction_config.yaml](../config_file_examples/prediction_config.yaml) or as shown in the example below:

```yaml
general:
   model_type: <model-type>                                     # st_ssd_mobilenet_v1, ssd_mobilenet_v2_fpnlite, tiny_yolo_v2
   model_path: <path-to-a-Keras-or-TFlite-model-file>           # Path to the model to use to make predictions

operation_mode: prediction

preprocessing:
   rescaling: { scale: 1/127.5, offset: -1 }
   resizing:
      aspect_ratio: fit
      interpolation: nearest
   color_mode: rgb

dataset:
   class_names: [ person ]   # Names of the classes

prediction:
  test_files_path: ../test_files

postprocessing:
  confidence_thresh: 0.6
  NMS_thresh: 0.5
  IoU_eval_thresh: 0.3
  max_detection_boxes: 10
```

In the 'general' section, users must provide the path to their model file using the `model_path` attribute. This can be either a Keras model file with a '.h5' filename extension (float model) or a TensorFlow Lite model file with a '.tflite' filename extension (quantized model).

The 'dataset' section requires users to provide the names of the classes using the `class_names` attribute, as there is no dataset available to infer them.

Finally, users must provide the path to the directory containing the images to predict using the `test_files_path` attribute in `prediction` section. Once all of these sections have been filled in, users can run the prediction service to generate predictions for their set of images.

**Hydra and MLflow settings**

The `mlflow` and `hydra` sections must always be present in the YAML configuration file. The `hydra` section can be used to specify the name of the directory where experiment directories are saved and/or the pattern used to name experiment directories. With the YAML code below, every time you run the Model Zoo, an experiment directory is created that contains all the directories and files created during the run. The names of experiment directories are all unique as they are based on the date and time of the run.

```yaml
hydra:
   run:
      dir: ./experiments_outputs/${now:%Y_%m_%d_%H_%M_%S}
```

The `mlflow` section is used to specify the location and name of the directory where MLflow files are saved, as shown below:

```yaml
mlflow:
   uri: ./experiments_outputs/mlruns
```

</details>
<details open><summary><a href="#2"><b>2. Launch the prediction</b></a></summary><a id="2"></a>

If you chose to modify the [user_config.yaml](../user_config.yaml) you can evaluate the model by running the following command from the **src/** folder:

```bash
python stm32ai_main.py 
```
If you chose to update the [prediction_config.yaml](../config_file_examples/prediction_config.yaml) and use it then run the following command from the **src/** folder: 

```bash
python stm32ai_main.py --config-path ./config_file_examples/ --config-name prediction_config.yaml
```

</details>
