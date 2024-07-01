# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os

import numpy as np
import pandas as pd
import tqdm
from imgaug.augmentables.bbs import BoundingBox
from typing import Optional, Tuple, List, Dict
import tensorflow as tf


def load_dataset(training_path: str = None,
                 validation_path: Optional[str] = None,
                 quantization_path: Optional[str] = None,
                 test_path: Optional[str] = None,
                 validation_split: Optional[float] = 0.2, seed: int = 42) -> Tuple[
    tf.data.Dataset, tf.data.Dataset, tf.data.Dataset,
    tf.data.Dataset]:
    """
    Loads and preprocesses a dataset for training, validation, quantization, and testing.

    Args:
        training_path: The path to the training dataset.
        validation_path: The path to the validation dataset (default: None).
        quantization_path: The path to the quantization dataset (default: None).
        test_path: The path to the test dataset (default: None).
        validation_split: The percentage of files to use for validation (default: None).
        seed: The random seed to use for shuffling the dataset.
    Returns:
        A tuple of training, validation, quantization, and test datasets.
    """

    if validation_path and training_path:
        # Load training and validation datasets
        tf.print("Loading Training dataset... ")
        train_annotations = parse_data(training_path)
        train_images_filename_list, train_gt_labels_list, num_train_samples = load_data(train_annotations)
        train_images_filename_list = np.array(train_images_filename_list)
        train_gt_labels_list = np.array(train_gt_labels_list)
        tf.print("Loading Validation dataset... ")
        val_annotations = parse_data(validation_path)
        val_images_filename_list, val_gt_labels_list, num_val_samples = load_data(val_annotations)
        val_images_filename_list = np.array(val_images_filename_list)
        val_gt_labels_list = np.array(val_gt_labels_list)

        train_dataset = {'train_images_filename_ds': train_images_filename_list,
                         'train_gt_labels_ds': train_gt_labels_list, 'num_train_samples': num_train_samples}
        val_dataset = {'val_images_filename_ds': val_images_filename_list,
                       'val_gt_labels_ds': val_gt_labels_list, 'num_val_samples': num_val_samples}

    elif training_path and not validation_path:
        # Split the training dataset into training and validation sets
        annotations = parse_data(training_path)
        nbannots = len(annotations)
        all_annots = np.random.RandomState(seed=seed).permutation(np.arange(nbannots))
        train_split = all_annots[int(validation_split * nbannots):]
        val_split = all_annots[:int(validation_split * nbannots)]

        train_annotations, val_annotations = [annotations[i] for i in train_split], [annotations[i] for i in val_split]

        print(f"[INFO] : To ensure the model is not overfitting or underfitting, it's crucial to evaluate its performance"
              f" on a validation dataset during training. As no separate validation dataset was provided, we will split"
              f" the dataset into an {100 - 100 * validation_split}% training set and a {100 * validation_split}% "
              f"validation set. ")

        tf.print(f"Loading {100 - 100 * validation_split}% of the provided dataset as the Training dataset ...")
        train_images_filename_list, train_gt_labels_list, num_train_samples = load_data(train_annotations)

        tf.print(f"Loading {100 * validation_split}% of the provided dataset as the Validation dataset ...")
        val_images_filename_list, val_gt_labels_list, num_val_samples = load_data(val_annotations)
        train_dataset = {'train_images_filename_ds': train_images_filename_list,
                         'train_gt_labels_ds': train_gt_labels_list, 'num_train_samples': num_train_samples}
        val_dataset = {'val_images_filename_ds': val_images_filename_list,
                       'val_gt_labels_ds': val_gt_labels_list, 'num_val_samples': num_val_samples}
    else:
        print(f"[INFO] : The training path is missing, and the train_dataset variable is set to None. "
              f"Please specify the path in the YAML file to proceed with the training process")
        print(f"[INFO] : The validation path is missing, and the validation_dataset variable is set to None. "
              f"Please specify the path in the YAML file to proceed with the training process")
        train_dataset = None
        val_dataset = None

    # Load the quantization dataset if provided
    if quantization_path:
        tf.print("Loading Quantization dataset...")
        quantization_annotations = parse_data(quantization_path,no_annots=True)

        quantization_images_filename_list, quantization_gt_labels_list, num_quantization_samples = load_data(
            quantization_annotations,no_annots=True)
        quantization_dataset = {'quantization_images_filename_ds': quantization_images_filename_list,
                                'quantization_gt_labels_ds': quantization_gt_labels_list,
                                'num_quantization_samples': num_quantization_samples}

    else:
        quantization_dataset = None

    # Load the test dataset if provided
    if test_path:
        tf.print("Loading Test dataset...")
        test_annotations = parse_data(test_path)
        test_images_filename_list, test_gt_labels_list, num_test_samples = load_data(test_annotations)
        test_dataset = {'test_images_filename_ds': test_images_filename_list,
                        'test_gt_labels_ds': test_gt_labels_list, 'num_test_samples': num_test_samples}
    else:
        test_dataset = None

    # Create the training, validation, quantization, and test datasets
    return train_dataset, val_dataset, quantization_dataset, test_dataset


def parse_data(train_set: str, no_annots: bool = False) -> list:
    """
    Parses the annotation files in a directory and returns their paths.

    Args:
        train_set (str): The path to the directory containing the annotation files.

    Returns:
        annotation_lines (list): A list of paths to the annotation files.
    """
    annotation_lines = []

    ext = ".txt"
    if no_annots:
        ext = ".jpg"

    for file in os.listdir(train_set):
        if file.endswith(ext):
            annotation_lines.append(os.path.join(train_set, file))

    return annotation_lines


def boxes_to_corners(boxes: np.ndarray, image: np.ndarray) -> list:
    """
    Converts bounding box coordinates from (class_id, x_center, y_center, w, h)
    format to (class_id, x_min, y_min, x_max, y_max) format.

    Args:
        boxes (np.ndarray): The bounding box coordinates in (class_id, x_center, y_center, w, h) format.
        image (np.ndarray): The input image.

    Returns:
        abs_boxes (list): The bounding box coordinates in (class_id, x_min, y_min, x_max, y_max) format.
    """
    height, width, _ = image.shape
    abs_boxes = []

    for box in boxes:
        x_min = (box[1] - box[3] / 2) * width
        y_min = (box[2] - box[4] / 2) * height
        x_max = (box[1] + box[3] / 2) * width
        y_max = (box[2] + box[4] / 2) * height
        abs_boxes.append([int(box[0] + 1), int(x_min), int(y_min), int(x_max), int(y_max)])

    return abs_boxes


def load_data(annotations: list, no_annots: bool = False) -> tuple:
    """
    Loads the image data and ground truth labels from a list of annotation files.

    Args:
        annotations (list): A list of paths to the annotation files.

    Returns:
        images (list): A list of paths to the image files.
        image_labels (np.ndarray): An array of ground truth labels with shape (num_samples, num_boxes, 5).
        num_samples (int): The number of samples in the dataset.
    """
    images = []
    image_labels = []

    for annotation in tqdm.tqdm(annotations):

        images_path = os.path.splitext(annotation)[0] + '.jpg'
        images.append(images_path)

        if not no_annots:
            image = tf.io.read_file(images_path)
            image = tf.io.decode_image(image, channels=3, expand_animations=False)
            img = image.numpy()

            txt_file_size = os.path.getsize(annotation)

            if txt_file_size != 0:
                ground_truths = pd.read_csv(annotation, sep=" ", header=None)
                ground_truths.columns = ["class_id", "x", "y", "w", "h"]
                labels = ground_truths.values.tolist()
                labels = boxes_to_corners(labels, img)
            else:
                labels = []

            image_labels.append(labels)

    image_labels = np.array(image_labels)
    num_samples = len(images)

    return images, image_labels, num_samples


def convert_to_iaa(gt_labels_list: List[List[float]]) -> List[List[BoundingBox]]:
    """
    Convert ground truth bounding boxes to imgaug BoundingBox format for data augmentation

    Args:
        gt_labels_list (List[List[float]]): a list of ground truth bounding boxes in the format of [[class_id, xmin, ymin, xmax, ymax], ...]

    Returns:
        gt_labels_list_iaa (List[List[BoundingBox]]): a list of imgaug BoundingBoxes [BoundingBox(xmin, ymin, xmax, ymax, class_id), ...]
    """
    gt_labels_list_iaa = []  # initialize empty list to hold imgaug BoundingBoxes
    for gt_labels in gt_labels_list:  # loop through each ground truth bounding box
        bbs = []  # initialize empty list to hold BoundingBoxes for each ground truth bounding box
        for label in gt_labels:  # loop through each label in the ground truth bounding box
            # create a BoundingBox object with the label's coordinates and class ID
            bb = BoundingBox(x1=label[1], y1=label[2], x2=label[3], y2=label[4], label=label[0])
            bbs.append(bb)  # add the BoundingBox to the list
        gt_labels_list_iaa.append(bbs)  # add the list of BoundingBoxes to the list of imgaug BoundingBoxes
    return gt_labels_list_iaa  # return the list of imgaug BoundingBoxes


def convert_from_iaa(gt_labels_list_iaa: list) -> np.ndarray:
    """
    Converts ground truth bounding boxes from imgaug BoundingBox format to [[class_id, xmin, ymin, xmax, ymax], ...]
    format.

    Args:
        gt_labels_list_iaa (list): A list of imgaug BoundingBoxes [BoundingBox(xmin, ymin, xmax, ymax, class_id), ...].

    Returns:
        gt_labels_list (np.ndarray): A list of ground truth bounding boxes in [[class_id, xmin, ymin, xmax, ymax], ...]
        format.
    """
    gt_labels_list = []

    # Loop through each ground truth label
    for gt_labels in gt_labels_list_iaa:
        bbs = []

        # Loop through each BoundingBox in the ground truth label
        for bb in gt_labels:
            # Create a new bounding box array and append it to the list
            xmin, ymin, xmax, ymax = bb.x1, bb.y1, bb.x2, bb.y2
            class_id = bb.label
            bbs.append([class_id, xmin, ymin, xmax, ymax])

        gt_labels_list.append(np.asarray(bbs))

    gt_labels_list = np.asarray(gt_labels_list)
    return gt_labels_list
