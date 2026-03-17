# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import numpy as np
import tensorflow as tf
from pathlib import Path
from omegaconf import DictConfig
from object_detection.tf.src.datasets.utils import compute_labels_stats, compute_class_stats, \
                    convert_dataset_to_yolo, convert_val_dataset_to_yolo, \
                    add_tfs_files_to_dataset, load_subset_dataloaders                   
from munch import DefaultMunch

from hydra.core.hydra_config import HydraConfig

def load_coco_like(cfg: DictConfig, 
                    image_size: tuple[int],
                    val_batch_size: int) -> dict:
    """
    Load COCO-format dataset and create TFS files.
    Handles both Officially downloaded COCO dataset and custom COCO-format datasets.

    Args:
        cfg (DictConfig): Configuration object containing dataset parameters including:
            For downloaded COCO dataset (download_data=True):
                - dataset.download_data: Set to True to use downloaded dataset (only allowed if training is enabled)
                - dataset.class_names: List of class names to use
            For custom dataset (download_data=False):
                - dataset.train_images_path: Path to training images
                - dataset.val_images_path: Path to validation images (optional)
                - dataset.train_annotations_path: Path to training annotations
                - dataset.val_annotations_path: Path to validation annotations (optional)
                - dataset.class_names: List of class names to use
            Common parameters:
                - dataset.format: The corresponding dataset format (tfs, darknet_yolo, coco, pascal_voc).
                - dataset.data_dir: Root directory containing raw dataset before tfs generation and splitting.
                - dataset.training_path: Path for processed training data
                - dataset.test_path: Path for processed test data
                - dataset.validation_path: Path for processed validation data
                - dataset.quantization_path: Path for quantization data (required if quantization is enabled)
                - dataset.prediction_path: Path for prediction data (required if prediction is enabled)
                - settings.max_detections: Optional maximum number of detections per image
                - settings.exclude_unlabeled_images: Whether to exclude images without labels
            - operation_mode (str): One of the supported modes or chains (e.g., chain_eqeb, training, evaluation, etc.)

    Returns:
        dict[str, tf.data.Dataset]: Dictionary containing training, validation, test,
            quantization and prediction datasets as TensorFlow datasets.
    """

    if not hasattr(cfg, 'operation_mode'):
        raise ValueError("cfg.operation_mode must be specified")

    mode_str = cfg.operation_mode.lower()

    mode_groups = DefaultMunch.fromDict({
        "training": ["training", "chain_tqeb", "chain_tqe"],
        "evaluation": ["evaluation", "chain_tqeb", "chain_tqe", "chain_eqe", "chain_eqeb"],
        "quantization": ["quantization", "chain_tqeb", "chain_tqe", "chain_eqe",
                        "chain_qb", "chain_eqeb", "chain_qd"],
        "benchmarking": ["benchmarking", "chain_tqeb", "chain_qb", "chain_eqeb"],
        "deployment": ["deployment", "chain_qd"],
        "prediction": ["prediction"],
        "compression": ["compression"]
    })
    
    # Conditional addition based on cfg.quantization.operating_mode
    if getattr(cfg.quantization, "operating_mode", None) == "full_auto":
        additional_items = ["quantization", "chain_qd", "chain_qb"]
        
        for item in additional_items:
            if item not in mode_groups.evaluation:
                mode_groups.evaluation.append(item)
    
    # Helper function to check if current mode_str belongs to a group
    def is_mode_in_group(group_name):
        return mode_str in mode_groups.get(group_name, [])

    is_training = is_mode_in_group("training")
    is_evaluation = is_mode_in_group("evaluation")
    is_quantization = is_mode_in_group("quantization")
    is_prediction = is_mode_in_group("prediction")

    # Verify required class names
    if not hasattr(cfg.dataset, 'class_names'):
        raise ValueError("Class names must be specified in cfg.dataset.class_names")

    dataset_format = getattr(cfg.dataset, "format", "").lower()

    # If training or evaluation mode
    if is_training or is_evaluation:
        if dataset_format == "coco":
            if is_training:
                # Download dataset allowed only if training is enabled
                if hasattr(cfg.dataset, 'download_data') and cfg.dataset.download_data:
                    if not hasattr(cfg.dataset, 'data_dir'):
                        raise ValueError("data_dir must be specified in cfg.dataset when download_data=True")

                    data_dir = cfg.dataset.data_dir

                    if not os.path.exists(os.path.join(data_dir, 'train2017')) or \
                        not os.path.exists(os.path.join(data_dir, 'val2017')) or \
                        not os.path.exists(os.path.join(data_dir, 'annotations')):
                        raise ValueError(f"Downloaded COCO dataset structure not found in {data_dir}. Expected train2017, val2017, and annotations directories.")

                    cfg.dataset.train_images_path = os.path.join(data_dir, 'train2017')
                    cfg.dataset.val_images_path = os.path.join(data_dir, 'val2017')
                    cfg.dataset.train_annotations_path = os.path.join(data_dir, 'annotations', 'instances_train2017.json')
                    cfg.dataset.val_annotations_path = os.path.join(data_dir, 'annotations', 'instances_val2017.json')

                else:
                    if not hasattr(cfg.dataset, 'data_dir'):
                        raise ValueError("data_dir must be specified in cfg.dataset. It will be used to store the .tfs format dataset before splitting.")
                    if not (hasattr(cfg.dataset, 'train_images_path') and cfg.dataset.train_images_path):
                        raise ValueError("For custom dataset (download_data set to False) in training mode, train_images_path must be specified in cfg.dataset")
                    if not (hasattr(cfg.dataset, 'train_annotations_path') and cfg.dataset.train_annotations_path):
                        raise ValueError("For custom dataset (download_data set to False) in training mode, train_annotations_path must be specified in cfg.dataset")
                    if not (hasattr(cfg.dataset, 'val_images_path') and cfg.dataset.val_images_path) or \
                    not (hasattr(cfg.dataset, 'val_annotations_path') and cfg.dataset.val_annotations_path):
                        print("Warning: Validation data paths not provided. Will use the validation_split from training data.")

                if not hasattr(cfg.dataset, 'training_path'):
                    raise ValueError("cfg.dataset.training_path must be specified for processed training data storage in training mode")

                if hasattr(cfg.dataset, 'validation_path') and cfg.dataset.validation_path:
                    os.makedirs(cfg.dataset.validation_path, exist_ok=True)

                raw_dataset_path = getattr(cfg.dataset, 'data_dir', None)
                if raw_dataset_path is None:
                    raw_dataset_path = getattr(cfg.dataset, 'training_path', None)

                if raw_dataset_path is None:
                    raise ValueError("Could not determine dataset root path. Please specify either data_dir or training_path in cfg.dataset")

                os.makedirs(raw_dataset_path, exist_ok=True)

                print("Starting dataset conversion to YOLO Darknet format...")
                convert_dataset_to_yolo(cfg)
                print("Dataset conversion completed.\n")

                print("Starting dataset analysis...")
                compute_class_stats(dataset_path=raw_dataset_path,
                                    dataset_name=getattr(cfg.dataset, 'dataset_name', None),
                                    histogram_dir=HydraConfig.get().runtime.output_dir)
                compute_labels_stats(dataset_path=raw_dataset_path,
                                    dataset_name=getattr(cfg.dataset, 'dataset_name', None),
                                    histogram_dir=HydraConfig.get().runtime.output_dir)
                print("Dataset analysis completed.\n")

            else: 
                #Evaluation mode 
                if not hasattr(cfg.dataset, 'test_path'):
                    raise ValueError("cfg.dataset.test_path must be specified in evaluation mode")
                if not os.path.exists(cfg.dataset.test_path):
                    raise ValueError(f"Test path {cfg.dataset.test_path} does not exist")
                tfs_dataset_path = cfg.dataset.test_path
                os.makedirs(tfs_dataset_path, exist_ok=True)
                
            # Checking the case where running evaluation without training on COCO dataset
            # In this case, we require the validation dataset path variables in the cfg
            # and convert only the validation dataset
            if mode_str in ["evaluation", "chain_eqe", "chain_eqeb"]:
                convert_val_dataset_to_yolo(cfg)

            print(f"Creating .tfs files for the {'training' if is_training else 'evaluation'} dataset...")
            exclude_unlabeled = (hasattr(cfg.dataset, 'exclude_unlabeled') and cfg.dataset.exclude_unlabeled)
            max_detections = (hasattr(cfg.dataset, 'max_detections') and cfg.dataset.max_detections)

            add_tfs_files_to_dataset(dataset_path=tfs_dataset_path,
                                    exclude_unlabeled_images=exclude_unlabeled,
                                    padded_labels_size=max_detections)
            print(".tfs files creation completed.")

        elif dataset_format == "tfs":
            # If format is tfs, directly load darknet-like without conversion or analysis
            print("Dataset format is 'tfs'. Skipping conversion and analysis steps.")
            return load_subset_dataloaders(cfg, is_training, is_evaluation,
                                    is_prediction, is_quantization,
                                    image_size=image_size, val_batch_size=val_batch_size)
        else:
            # If other formats or no format specified, proceed with existing logic or raise error if needed
            # For now, fallback to existing COCO logic or raise error
            raise ValueError(f"Unsupported dataset format '{dataset_format}' for training/evaluation mode.")

    if is_prediction:
        if not hasattr(cfg.dataset, 'prediction_path') and not cfg.dataset.prediction_path:
            raise ValueError("cfg.dataset.prediction_path must be specified in prediction mode")
        else:
            if not os.path.exists(cfg.dataset.prediction_path):
                raise ValueError(f"Prediction path {cfg.dataset.prediction_path} does not exist")

    if is_quantization:
        if not hasattr(cfg.dataset, 'quantization_path') and not cfg.dataset.quantization_path:
            raise ValueError("cfg.dataset.quantization_path must be specified in quantization mode")
        else:
            if not os.path.exists(cfg.dataset.quantization_path):
                raise ValueError(f"Quantization path {cfg.dataset.quantization_path} does not exist")

    print("Loading datasets in darknet format...")
    return load_subset_dataloaders(cfg, is_training, is_evaluation,
                            is_prediction, is_quantization, 
                            image_size=image_size, val_batch_size=val_batch_size)