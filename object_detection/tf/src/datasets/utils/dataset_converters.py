# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import json
import hydra
import shutil
import argparse
from hydra.core.hydra_config import HydraConfig
from tqdm import tqdm
from munch import DefaultMunch
from omegaconf import OmegaConf
from omegaconf import DictConfig
import xml.etree.ElementTree as ET
from PIL import Image

def classes_inspector(non_existing_classes: list = None,
                      available_classes: list = None) -> None:
    """
    Ensure all defined classes are well present in the dataset

    Args:
        non_existing_classes (list): list of non found classes from the dataset
        available_classes (list): list of detected classes in the dataset

    Returns:
        None
    """
    if len(non_existing_classes) > 0:
        print("The following classes were not found: {}".format(non_existing_classes))
        print("Please make sure that your selected classes exist in the following list: {}".format(available_classes))
        print("Exiting the script...")
        sys.exit()
    else:
        print("Converting the dataset ...")


def verify_voc_classes(xml_folder: str = None,
                       classes: list = None) -> None:
    """
    Check if all expected classes are well present in the provided dataset

    Args:
        xml_folder (str): path to the xml directory
        classes (list): list of the provided classes (from the yaml file)

    Returns:
        None
    """
    print("Analyzing the dataset ...")
    available_classes = set()
    xml_files = [file for file in os.listdir(xml_folder) if file.endswith('.xml')]
    for filename in tqdm(xml_files):
        xml_path = os.path.join(xml_folder, filename)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for obj in root.findall('object'):
            name = obj.find('name').text
            print(name)
            available_classes.add(name)

    non_existing_classes = [c for c in classes if c not in available_classes]
    classes_inspector(non_existing_classes,
                      available_classes)


def convert_voc_to_yolo(xml_folder: str = None,
                        images_folder: str = None,
                        classes: list = None,
                        export_folder: str = None) -> None:
    """
    Core routine that converts voc data to yolo format and exports them

    Args:
        xml_folder (str): path to the xml directory
        images_folder (str): path to the images directory
        classes (list): list of the provided classes (from the yaml file)
        export_folder (str): path converted dataset will be stored

    Returns:
        None
    """
    verify_voc_classes(xml_folder,
                       classes)
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    xml_files = [file for file in os.listdir(xml_folder) if file.endswith('.xml')]
    for filename in tqdm(xml_files):
        copy_image = False
        xml_path = os.path.join(xml_folder, filename)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        size = root.find('size')
        width = int(size.find('width').text)
        height = int(size.find('height').text)
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(export_folder, txt_filename)

        for obj in root.findall('object'):
            name = obj.find('name').text
            if name in classes:
                with open(txt_path, 'a') as label_file:
                    copy_image = True
                    class_id = classes.index(name)
                    bbox = obj.find('bndbox')
                    xmin = float(bbox.find('xmin').text)
                    ymin = float(bbox.find('ymin').text)
                    xmax = float(bbox.find('xmax').text)
                    ymax = float(bbox.find('ymax').text)
                    x_center = (xmin + xmax) / (2 * width)
                    y_center = (ymin + ymax) / (2 * height)
                    w = (xmax - xmin) / width
                    h = (ymax - ymin) / height
                    label_file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

        if copy_image:
            image_file = os.path.splitext(filename)[0] + '.jpg'
            image_path = os.path.join(images_folder, image_file)
            shutil.copy(image_path, export_folder)


def verify_coco_classes(coco_annotations_file: str = None,
                        classes: list = None) -> None:
    """
    Check if all expected classes are well present in the provided dataset

    Args:
        coco_annotations_file (str): path to the coco annotation file
        classes (list): list of the provided classes (from the yaml file)

    Returns:
        None
    """
    print("Analyzing the dataset ...")
    with open(coco_annotations_file, 'r') as f:
        coco_data = json.load(f)

    class_names = set()
    for annotation in tqdm(coco_data['annotations']):
        category_id = annotation['category_id']
        for category in coco_data['categories']:
            if category['id'] == category_id:
                class_name = category['name']
                class_names.add(class_name)

    available_classes = list(class_names)
    non_existing_classes = [c for c in classes if c not in available_classes]
    classes_inspector(non_existing_classes,
                      available_classes)


def convert_coco_to_yolo(coco_annotations_file: str = None,
                         coco_images_dir: str = None,
                         classes: list = None,
                         export_folder: str = None) -> None:
    """
    Core routine that converts coco data to yolo format and exports them

    Args:
        coco_annotations_file (str): path to the coco annotations directory
        coco_images_dir (str): path to the images directory
        classes (list): list of the provided classes (from the yaml file)
        export_folder (str): path converted dataset will be stored

    Returns:
        None
    """
    verify_coco_classes(coco_annotations_file,
                        classes)
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    with open(coco_annotations_file, 'r') as f:
        coco_data = json.load(f)

    for image_info in tqdm(coco_data['images']):
        copy_image = False
        image_file_name = image_info['file_name']
        label_file_name = os.path.splitext(image_file_name)[0] + '.txt'
        label_file_path = os.path.join(export_folder, label_file_name)
        for annotation in coco_data['annotations']:
            if annotation['image_id'] == image_info['id']:
                category_id = annotation['category_id']
                class_name = None
                for category in coco_data['categories']:
                    if category['id'] == category_id:
                        class_name = category['name']
                        break
                if class_name in classes:
                    copy_image = True
                    class_id = classes.index(class_name)
                    x, y, w, h = annotation['bbox']
                    x_center = x + (w / 2)
                    y_center = y + (h / 2)
                    x_center /= image_info['width']
                    y_center /= image_info['height']
                    w /= image_info['width']
                    h /= image_info['height']
                    with open(label_file_path, 'a') as label_file:
                        label_file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

        if copy_image:
            image_path = os.path.join(coco_images_dir, image_file_name)
            shutil.copy(image_path, export_folder)


def verify_kitti_classes(kitti_annotations_dir: str = None, classes: list = None) -> None:
    """
    Check if all expected classes are well present in the provided dataset

    Args:
        kitti_annotations_dir (str): path to the KITTI annotations directory
        classes (list): list of the provided classes (from the yaml file)

    Returns:
        None
    """
    print("Analyzing the dataset ...")
    available_classes = set()
    annotation_files = [file for file in os.listdir(kitti_annotations_dir) if file.endswith('.txt')]
    for filename in tqdm(annotation_files):
        annotation_path = os.path.join(kitti_annotations_dir, filename)
        with open(annotation_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                class_name = parts[0]
                available_classes.add(class_name)

    non_existing_classes = [c for c in classes if c not in available_classes]
    classes_inspector(non_existing_classes, available_classes)


def convert_kitti_to_yolo(kitti_annotations_dir: str = None,
                          kitti_images_dir: str = None,
                          classes: list = None,
                          export_folder: str = None) -> None:
    """
    Core routine that converts KITTI data to YOLO format and exports them

    Args:
        kitti_annotations_dir (str): path to the KITTI annotations directory
        kitti_images_dir (str): path to the images directory
        classes (list): list of the provided classes (from the yaml file)
        export_folder (str): path converted dataset will be stored

    Returns:
        None
    """
    verify_kitti_classes(kitti_annotations_dir, classes)
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
    annotation_files = [file for file in os.listdir(kitti_annotations_dir) if file.endswith('.txt')]
    for filename in tqdm(annotation_files):
        copy_image = False
        annotation_path = os.path.join(kitti_annotations_dir, filename)
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(export_folder, txt_filename)
        image_file = os.path.splitext(filename)[0] + '.jpg'
        image_path = os.path.join(kitti_images_dir, image_file)
        if not os.path.exists(image_path):
            continue
        image = Image.open(image_path)
        width_image, height_image = image.size

        with open(annotation_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                class_name = parts[0]
                if class_name in classes:
                    copy_image = True
                    class_id = classes.index(class_name)
                    xmin, ymin, xmax, ymax = map(float, parts[4:8])
                    width = float(parts[8])
                    height = float(parts[9])
                    if width == 0 and height == 0:
                        w = xmax - xmin
                        h = ymax - ymin
                        x_center = (xmin + xmax) / 2
                        y_center = (ymin + ymax) / 2
                    else:
                        x_center = (xmin + xmax) / (2 * width)
                        y_center = (ymin + ymax) / (2 * height)
                        w = (xmax - xmin) / width
                        h = (ymax - ymin) / height
                    x_center /= width_image
                    y_center /= height_image
                    w /= width_image
                    h /= height_image
                    with open(txt_path, 'a') as label_file:
                        label_file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")

        if copy_image:
            shutil.copy(image_path, export_folder)

def convert_val_dataset_to_yolo(cfg: DictConfig) -> None:
    """
    Converts only the validatin dataset to YOLO Darknet format according to the config.
    This is required for the case when loading the validation dataset only.

    Args:
        cfg (DictConfig): Configuration dictionary containing:
            - dataset.format: Format of the input dataset
            - dataset.val_annotations_path: Path to validation annotations (optional)
            - dataset.val_images_path: Path to validation images (optional)
            - dataset.class_names: List of class names
            - dataset.training_path: Output path for converted training data
            - dataset.validation_path: Output path for converted validation data (optional)

    Returns:
        None
    """

    if cfg.dataset.format == "coco":
        if (hasattr(cfg.dataset, 'val_annotations_file_path') and
            hasattr(cfg.dataset, 'val_images_path') and
            hasattr(cfg.dataset, 'data_dir') and
            cfg.dataset.val_annotations_file_path and
            cfg.dataset.val_images_path and
            cfg.dataset.data_dir):

            print("\nConverting validation set to YOLO format...")
            convert_coco_to_yolo(cfg.dataset.val_annotations_file_path,
                                 cfg.dataset.val_images_path,
                                 cfg.dataset.class_names,
                                 cfg.dataset.data_dir)
        else:
            raise ValueError(f"val_annotations_file_path, val_images_path and data_dir must be specified while evaluating on COCO format dataset.")


    elif cfg.dataset.format == "pascal_voc":
        # Convert validation set if all required paths are provided
        if (hasattr(cfg.dataset, 'val_xml_files_path') and
            hasattr(cfg.dataset, 'val_images_path') and
            hasattr(cfg.dataset, 'data_dir') and
            cfg.dataset.val_xml_dir and
            cfg.dataset.val_images_path and
            cfg.dataset.data_dir):

            print("\nConverting validation set to YOLO format...")
            convert_voc_to_yolo(cfg.dataset.val_xml_dir,
                               cfg.dataset.val_images_path,
                               cfg.dataset.class_names,
                               cfg.dataset.data_dir)
        else:
            raise ValueError(f"val_xml_files_path, val_images_path and data_dir must be specified while evaluating on PASCAL_VOC format dataset.")

    elif cfg.dataset.format == "yolo_darknet":
        print("Dataset is already in YOLO format. No conversion needed.")
        return

    else:
        print("Please make sure that you selected one of the following formats: {}, {}, {}, {}".format(
            "coco", "pascal_voc", "yolo_darknet", "kitti"))
        print("Exiting the script...")
        sys.exit()

def convert_dataset_to_yolo(cfg: DictConfig) -> None:
    """
    Converts the dataset to YOLO Darknet format according to the config.
    If validation paths are provided, converts both training and validation sets.

    Args:
        cfg (DictConfig): Configuration dictionary containing:
            - dataset.format: Format of the input dataset
            - dataset.train_annotations_path: Path to training annotations
            - dataset.train_images_path: Path to training images
            - dataset.val_annotations_path: Path to validation annotations (optional)
            - dataset.val_images_path: Path to validation images (optional)
            - dataset.class_names: List of class names
            - dataset.training_path: Output path for converted training data
            - dataset.validation_path: Output path for converted validation data (optional)

    Returns:
        None
    """

    if cfg.dataset.format == "coco":
        # Convert training set
        print("Converting training set to YOLO format...")
        convert_coco_to_yolo(cfg.dataset.train_annotations_path,
                            cfg.dataset.train_images_path,
                            cfg.dataset.class_names,
                            cfg.dataset.data_dir)

        # Convert validation set if all required paths are provided
        if (hasattr(cfg.dataset, 'val_annotations_file_path') and
            hasattr(cfg.dataset, 'val_images_path') and
            hasattr(cfg.dataset, 'data_dir') and
            cfg.dataset.val_annotations_file_path and
            cfg.dataset.val_images_path and
            cfg.dataset.data_dir):

            print("\nConverting validation set to YOLO format...")
            convert_coco_to_yolo(cfg.dataset.val_annotations_file_path,
                                 cfg.dataset.val_images_path,
                                 cfg.dataset.class_names,
                                 cfg.dataset.data_dir)

    elif cfg.dataset.format == "pascal_voc":
        # Convert training set
        print("Converting training set to YOLO format...")
        convert_voc_to_yolo(cfg.dataset.train_xml_dir,
                           cfg.dataset.train_images_path,
                           cfg.dataset.class_names,
                           cfg.dataset.data_dir)

        # Convert validation set if all required paths are provided
        if (hasattr(cfg.dataset, 'val_xml_files_path') and
            hasattr(cfg.dataset, 'val_images_path') and
            hasattr(cfg.dataset, 'data_dir') and
            cfg.dataset.val_xml_dir and
            cfg.dataset.val_images_path and
            cfg.dataset.data_dir):

            print("\nConverting validation set to YOLO format...")
            convert_voc_to_yolo(cfg.dataset.val_xml_dir,
                               cfg.dataset.val_images_path,
                               cfg.dataset.class_names,
                               cfg.dataset.data_dir)

    elif cfg.dataset.format == "yolo_darknet":
        print("Dataset is already in YOLO format. No conversion needed.")
        return

    else:
        print("Please make sure that you selected one of the following formats: {}, {}, {}, {}".format(
            "coco", "pascal_voc", "yolo_darknet", "kitti"))
        print("Exiting the script...")
        sys.exit()