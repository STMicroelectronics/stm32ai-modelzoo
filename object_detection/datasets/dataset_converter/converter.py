# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
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


def get_config(config: DictConfig) -> DefaultMunch:
    """
    Converts the configuration data

    Args:
        config (DictConfig): dictionary containing the entire configuration file.

    Returns:
        DefaultMunch: The configuration object.
    """
    config_dict = OmegaConf.to_container(config)
    cfg = DefaultMunch.fromDict(config_dict)
    return cfg


def classes_inspector(non_existing_classes : list=None, 
                      available_classes : list=None) -> None:
    """
    Ensure all defined classes are well present in the dataset

    Args:
        non_existing_classes (list) : list of non found classes from the dataset
        available_classes (list) : list of detected classes in the dataset

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


def verify_voc_classes(xml_folder : str=None, 
                       classes : list=None) -> None:
    """
    Check if all expected classes are well present in the provided dataset

    Args:
        xml_folder (str) : path to the xml directory
        classes (list) : list of the provided classes (from the yaml file)

    Returns:
        None
    """
    print("Analyzing the dataset ...")
    available_classes = set()
    xml_files = [file for file in os.listdir(xml_folder) if file.endswith('.xml')]
    for filename in tqdm(xml_files):
        if filename.endswith('.xml'):
            xml_path = os.path.join(xml_folder, filename)
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for obj in root.findall('object'):
                name = obj.find('name').text
                available_classes.add(name)

    non_existing_classes = [c for c in classes if c not in available_classes]
    classes_inspector(non_existing_classes, 
                      available_classes)


def convert_voc_to_yolo(xml_folder : str=None, 
                        images_folder : str=None, 
                        classes : list=None, 
                        export_folder : str=None) -> None:
    """
    Core routine that converts voc data to yolo format and exports them

    Args:
        xml_folder (str) : path to the xml directory
        images_folder (str) : path to the images directory
        classes (list) : list of the provided classes (from the yaml file)
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
        if filename.endswith('.xml'):
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
                    label_file = open(txt_path, 'a')
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
                    label_file.close()

        if copy_image:
            image_file = os.path.splitext(filename)[0] + '.jpg'
            image_path = os.path.join(images_folder, image_file)
            shutil.copy(image_path, export_folder)


def verify_coco_classes(coco_annotations_file : str=None,
                        classes : list=None) -> None:
    """
    Check if all expected classes are well present in the provided dataset

    Args:
        coco_annotations_file (str) : path to the coco annotation file
        classes (list) : list of the provided classes (from the yaml file)

    Returns:
        None
    """
    print("Analyzing the dataset ...")
    with open(coco_annotations_file, 'r') as f:
        coco_data = json.load(f)

    class_names = set()
    for annotation in tqdm(coco_data['annotations']):
        category_id = annotation['category_id']
        try:
            for category in coco_data['categories']:
                if category['id'] == category_id:
                    class_name = category['name']
                    class_names.add(class_name)
        except Exception as e:
            exceptions = e
    available_classes = list(class_names)
    non_existing_classes = [c for c in classes if c not in available_classes]
    classes_inspector(non_existing_classes, 
                      available_classes)


def convert_coco_to_yolo(coco_annotations_file : str=None, 
                         coco_images_dir : str=None, 
                         classes : list=None, 
                         export_folder : str=None) -> None:
    """
    Core routine that converts coco data to yolo format and exports them

    Args:
        coco_annotations_file (str) : path to the coco annotations directory
        coco_images_dir (str) : path to the images directory
        classes (list) : list of the provided classes (from the yaml file)
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
                try:
                    category_id = annotation['category_id']
                    for category in coco_data['categories']:
                        if category['id'] == category_id:
                            class_name = category['name']
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
                        label_file = open(label_file_path, 'a')
                        label_file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")
                        label_file.close()
                except Exception as e:
                    exceptions = e
        if copy_image:
            image_path = os.path.join(coco_images_dir, image_file_name)
            shutil.copy(image_path, export_folder)


@hydra.main(version_base=None, config_path="", config_name="dataset_config")
def main(configs: DictConfig) -> None:
    """
    Main entry point of the script.
 
    Args:
        cfg: Configuration dictionary.
 
    Returns:
        None
    """
    cfg = get_config(configs)
    cfg.output_dir = HydraConfig.get().run.dir

    # Converts COCO dataset to Yolo Darknet format
    if cfg.dataset.format == "coco_format":
        convert_coco_to_yolo(cfg.coco_format.json_annotations_file_path, 
                             cfg.coco_format.images_path,
                             cfg.dataset.class_names, 
                             cfg.coco_format.export_dir)

    # Converts Pascal VOC dataset to Yolo Darknet format
    elif cfg.dataset.format == "pascal_voc_format":
        convert_voc_to_yolo(cfg.pascal_voc_format.xml_files_path, 
                            cfg.pascal_voc_format.images_path,
                            cfg.dataset.class_names, 
                            cfg.pascal_voc_format.export_dir)

    else:
        print("Please make sure that you selected one of the following formats: {}, {}".format("coco_format",
                                                                                               "pascal_voc_format"))
        print("Exiting the script...")
        sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=str, default='', help='Path to folder containing configuration file')
    parser.add_argument('--config-name', type=str, default='user_config', help='name of the configuration file')
    
    # Add arguments to the parser
    parser.add_argument('params', nargs='*',
                        help='List of parameters to over-ride in config.yaml')
    args = parser.parse_args()

    main()
