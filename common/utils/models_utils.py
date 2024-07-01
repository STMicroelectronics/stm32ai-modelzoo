#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
from tabulate import tabulate
from keras.utils.layer_utils import count_params
from typing import Dict, Optional, Tuple, List
import tensorflow as tf
from tensorflow.keras.models import Model
import numpy as np
import sklearn
from pathlib import Path
from onnx import ModelProto
import onnxruntime


def get_model_name(model_type: str, 
                   input_shape: int, 
                   project_name: str) -> str:
    """Returns a string representation of the model name.

    Args:
        model_type (str): Type of the model.
        input_shape (int): Input shape of the model.
        project_name (str): Name of the project.

    Returns:
        str: String representation of the model name.
    """
    # Combine strings to form model name
    strings = [model_type, str(input_shape), project_name]
    name = '_'.join([str(i) for i in strings])

    return name


def get_model_name_and_its_input_shape(model_path: str = None, 
                                       custom_objects: Dict = None) -> Tuple:
    """
    Load a model from a given file path and return the model name and
    its input shape. Supported model formats are .h5, .tflite and .onnx.
    The basename of the model file is used as the model name. The input
    shape is extracted from the model.

    Args:
        model_path (str): A path to an .h5, .tflite or .onnx model file.
        custom_objects (Dict): a dictionnary containing custom object from the model

    Returns:
        Tuple: A tuple containing the loaded model name and its input shape.
               The input shape is a tuple of length 3.
    Raises:
        ValueError: If the model file extension is not '.h5' or '.tflite'.
        RuntimeError: If the input shape of the model cannot be found.
    """

    # We use the file basename as the model name.
    model_name = Path(model_path).stem

    file_extension = Path(model_path).suffix
    if file_extension == ".h5":
        # When we resume a training, the model includes the preprocessing layers
        # (augmented model). Therefore, we need to declare the custom data
        # augmentation layer as a custom object to be able to load the model.
        model = tf.keras.models.load_model(
                        model_path,
                        custom_objects = custom_objects,
                        compile=False)
        input_shape = tuple(model.input.shape[1:])

    elif file_extension == ".tflite":
        try:
            # Load the tflite model
            interpreter = tf.lite.Interpreter(model_path=model_path)
            interpreter.allocate_tensors()
            # Get the input details
            input_details = interpreter.get_input_details()
            input_shape = input_details[0]['shape']
            input_shape = tuple(input_shape)[-3:]
        except RuntimeError as error:
            raise RuntimeError("\nUnable to extract input shape from .tflite model file\n"
                               f"Received path {model_path}") from error

    elif file_extension == ".onnx":
        try:
            # Load the model
            onx = ModelProto()
            with open(model_path, "rb") as f:
                content = f.read()
                onx.ParseFromString(content)
            sess = onnxruntime.InferenceSession(model_path)
            # Get the model input shape
            input_shape = sess.get_inputs()[0].shape
            input_shape = tuple(input_shape)[-3:]
        except RuntimeError as error:
            raise RuntimeError("\nUnable to extract input shape from .onnx model file\n"
                               f"Received path {model_path}") from error

    else:
        raise RuntimeError(f"\nUnknown/unsupported model file type.\nExpected `.tflite`, `.h5`, or `.onnx`."
                           f"\nReceived path {model_path.split('.')[-1]}")

    return model_name, input_shape


def check_model_support(model_name: str, version: Optional[str] = None,
                        supported_models: Dict = None,
                        message: Optional[str] = None) -> None:
    """
    Check if a model name and version are supported based on a dictionary of supported models and versions.

    Args:
        model_name(str): The name of the model to check.
        version(str): The version of the model to check. May be set to None by the caller.
        supported_models(Dict[str, List[str]]): A dictionary of supported models and their versions.
        message(str): An error message to print.

    Raises:
        NotImplementedError: If the model name or version is not in the list of supported models or versions.
        ValueError: If the version attribute is missing or not applicable for the given model.
    """
    if model_name not in supported_models:
        x = list(supported_models.keys())
        raise ValueError("\nSupported model names are {}. Received {}.{}".format(x, model_name, message))

    model_versions = supported_models[model_name]
    if model_versions:
        # There are different versions of the model.
        if not version:
            # The version is missing.
            raise ValueError("\nMissing `version` attribute for `{}` model.{}".format(model_name, message))
        if version not in model_versions:
            # The version is not a supported version.
            raise ValueError("\nSupported versions for `{}` model are {}. "
                             "Received {}.{}".format(model_name, model_versions, version, message))
    else:
        if version:
            # A version was given but there is no version for this model.
            raise ValueError("\nThe `version` attribute is not applicable "
                             "to '{}' model.{}".format(model_name, message))


def check_attribute_value(attribute_value: str, values: List[str] = None,
                          name: str = None, message: str = None) -> None:
    """
    Check if an attribute value is valid based on a list of supported values.
    Args:
        attribute_value(str): The value of the attribute to check.
        values(List[str]): A list of supported values.
        name(str): The name of the attribute being checked.
        message(str): A message to print if the attribute is not supported.
    Raises:
        ValueError: If the attribute value is not in the list of supported values.
    """
    if attribute_value not in values:
        raise ValueError(f"\nSupported values for `{name}` attribute are {values}. "
                         f"Received {attribute_value}.{message}")


def transfer_pretrained_weights(target_model: tf.keras.Model, source_model_path: str = None,
                                end_layer_index: int = None, target_model_name: str = None) -> None:
    # NOTE : Unused in AED for now.
    # When it's ready to use, call it after loading model in get_model.
    """
    Copy the weights of a source model to a target model. Only the backbone weights
    are copied as the two models can have different classifiers.

    Args:
        target_model (tf.keras.Model): The target model.
        source_model_path (str): Path to the source model file (h5 file).
        end_layer_index (int): Index of the last backbone layer (the first layer of the model has index 0).
        target_model_name (str): The name of the target model.

    Raises:
        ValueError: The source model file cannot be found.
        ValueError: The two models are incompatible because they have different backbones.
    """

    if source_model_path:
        if not os.path.isfile(source_model_path):
            raise ValueError("Unable to find pretrained model file.\nReceived "
                             f"model path {source_model_path}")
        source_model = tf.keras.models.load_model(source_model_path, compile=False)

    message = f"\nUnable to transfer to model `{target_model_name}`"
    message += f"the weights from model {source_model_path}\n"
    message += "Models are incompatible (backbones are different)."
    if len(source_model.layers) < end_layer_index + 1:
        raise ValueError(message)
    for i in range(end_layer_index + 1):
        weights = source_model.layers[i].get_weights()
        try:
            target_model.layers[i].set_weights(weights)
        except ValueError as error:
            raise message from error


def model_summary(model):
    """
    This function displays a model summary. It is similar to a Keras
    model summary with the additional information:
    - Indices of layers
    - Trainable/non-trainable status of layers
    - Total number of layers
    - Number of trainable layers
    - Number of non-trainable layers
    """
    # Create the summary table
    num_layers = len(model.layers)
    trainable_layers = 0
    table = []
    for i, layer in enumerate(model.layers):
        layer_type = layer.__class__.__name__
        if layer_type == "InputLayer":
            layer_shape = model.input.shape
        else:
            layer_shape = layer.output_shape
        is_trainable = True if layer.trainable else False
        num_params = layer.count_params()
        if layer.trainable:
            trainable_layers += 1
        table.append([i, is_trainable, layer.name, layer_type, num_params, layer_shape])

    # Display the table
    print(108 * '=')
    print("  Model:", model.name)
    print(108 * '=')
    print(tabulate(table, headers=["Layer index", "Trainable", "Name", "Type", "Params#", "Output shape"]))
    print(108 * '-')
    print("Total params:", model.count_params())
    print("Trainable params: ", count_params(model.trainable_weights))
    print("Non-trainable params: ", count_params(model.non_trainable_weights))
    print(108 * '-')
    print("Total layers:", num_layers)
    print("Trainable layers:", trainable_layers)
    print("Non-trainable layers:", num_layers - trainable_layers)
    print(108 * '=')


def tf_dataset_to_np_array(input_ds, nchw=True, labels_included=True):
    """
    Converts a TensorFlow dataset into two NumPy arrays containing the data and labels.

    This function iterates over the provided TensorFlow dataset, casts the image data to
    float32, and then converts the images and labels into NumPy arrays. The images and
    labels from all batches are concatenated along the first axis (batch dimension) to
    form two unified arrays.

    Parameters:
    - input_ds (tf.data.Dataset): A TensorFlow dataset object that yields tuples of
      (images, labels) when iterated over.

    - labels_included (bool): A boolean that represent whether or not the dataset 
      contains the labels of the images (True) or just the images (False)

    Returns:
    - tuple: A tuple containing two NumPy arrays:
        - The first array contains the image data from the dataset.
        - The second array contains the corresponding labels.

    Example:
    ```python
    import tensorflow as tf
    import numpy as np

    # Assuming `dataset` is a pre-defined TensorFlow dataset with image-label pairs
    data, labels = tf_dataset_to_np_array(dataset)

    print(data.shape)   # Prints the shape of the image data array
    print(labels.shape) # Prints the shape of the labels array

    # Assuming `dataset` is a pre-defined TensorFlow dataset with image only
    data, _ = tf_dataset_to_np_array(dataset,labels_included=False)

    print(data.shape)   # Prints the shape of the image data array
    ```

    Note:
    - The input TensorFlow dataset is expected to yield batches of data.
    - The function assumes that the dataset yields data in the form of (images, labels),
      where `images` are the features and `labels` are the corresponding targets
      or the data is of the form (images).
    - The function will fail if the input dataset does not yield data in the expected format.
    """
    batch_data = []
    batch_labels = []
    if labels_included:
        for images, labels in input_ds:
            images = tf.cast(images, dtype=tf.float32).numpy()
            batch_data.append(images)
            batch_labels.append(labels)
        batch_labels = np.concatenate(batch_labels, axis=0)
    else:
        for images in input_ds:
            images = tf.cast(images, dtype=tf.float32).numpy()
            batch_data.append(images)
    batch_data = np.concatenate(batch_data, axis=0)
    
    # Convert image to input data
    if nchw and batch_data is not None:
        if batch_data.ndim == 4:
            # For a 4D array with shape [n, h, w, c], the new order will be [n, c, h, w]
            axes_order = (0, 3, 1, 2)
        elif batch_data.ndim == 3:
            # For a 3D array with shape [n, h, c], the new order will be [n, c, h]
            axes_order = (0, 2, 1)
        else:
            raise ValueError("The input array must have either 3 or 4 dimensions.")
        batch_data = np.transpose(batch_data, axes_order)

    return batch_data, batch_labels


def compute_confusion_matrix(test_set: tf.data.Dataset = None, model: Model = None) -> Tuple[np.ndarray, np.float]:
    """
    Computes the confusion matrix and logs it as an image summary.

    Args:
        test_set (tf.data.Dataset): The test dataset to evaluate the model on.
        model (tf.keras.models.Model): The trained model to evaluate.
    Returns:
        confusion_matrix and accuracy
    """
    test_pred = []
    test_labels = []
    for data in test_set:
        test_pred_score = model.predict_on_batch(data[0])
        if test_pred_score.shape[1] > 1:
            # Multi-label classification
            test_pred.append(np.argmax(test_pred_score, axis=1))
        else:
            # Binary classification
            test_pred_score = np.where(test_pred_score < 0.5, 0, 1)
            test_pred.append(np.squeeze(test_pred_score))
        # handle both types of the ground truth labels (one-hotcoded or integer)
        batch_labels = np.argmax(data[1], axis=1) if len(data[1].shape)>1 else data[1]
        test_labels.append(batch_labels)

    labels = np.concatenate(test_labels, axis=0)
    logits = np.concatenate(test_pred, axis=0)
    test_accuracy = round((np.sum(labels == logits) * 100) / len(labels), 2)

    # Calculate the confusion matrix.
    cm = sklearn.metrics.confusion_matrix(labels, logits)
    return cm, test_accuracy