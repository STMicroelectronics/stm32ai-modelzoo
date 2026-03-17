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
                                        add_tfs_files_to_dataset, load_subset_dataloaders                   
from munch import DefaultMunch

def load_darknet_yolo_like(cfg: DictConfig, 
                        image_size: tuple[int],
                        val_batch_size: int) -> dict:
    """
    Load Darknet YOLO-format dataset and create TFS files.
    Handles datasets where images and labels are already in Darknet format (JPEG + TXT files).

    Args:
        cfg (DictConfig): Configuration object containing dataset parameters including:
            - dataset.format: The corresponding dataset format (tfs, darknet_yolo, coco, pascal_voc).
            - dataset.data_dir: Root directory containing raw dataset (JPEG + TXT files) before tfs generation and splitting.
            - dataset.training_path: Path for processed training data
            - dataset.test_path: Path for processed test data
            - dataset.validation_path: Path for processed validation data
            - dataset.quantization_path: Path for quantization data (required if quantization is enabled)
            - dataset.prediction_path: Path for prediction data (required if prediction is enabled)
            - dataset.class_names: List of class names to use
            - dataset.download_data: Whether to download dataset (unsupported for Darknet YOLO format)
            - settings.max_detections: Optional maximum number of detections per image
            - settings.exclude_unlabeled_images: Whether to exclude images without labels
            - operation_mode (str): One of the supported modes or chains (e.g., chain_eqeb, training, evaluation, etc.)

    Returns:
        dict[str, tf.data.Dataset]: Dictionary containing training, validation, test,
            quantization and prediction datasets as TensorFlow datasets.
    """

    if not hasattr(cfg, 'operation_mode'):
        raise ValueError("cfg.operation_mode must be specified")

    # Check for unsupported download_data option
    if hasattr(cfg.dataset, 'download_data') and cfg.dataset.download_data:
        raise NotImplementedError("Downloading dataset is unsupported for Darknet YOLO TXT format. "
                                "Please prepare the dataset manually in the expected format.")

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

    def is_mode_in_group(group_name):
        return mode_str in mode_groups.get(group_name, [])

    is_training = is_mode_in_group("training")
    is_evaluation = is_mode_in_group("evaluation")
    is_quantization = is_mode_in_group("quantization")
    is_benchmarking = is_mode_in_group("benchmarking")
    is_deployment = is_mode_in_group("deployment")
    is_prediction = is_mode_in_group("prediction")

    # Verify required class names
    if not hasattr(cfg.dataset, 'class_names'):
        raise ValueError("Class names must be specified in cfg.dataset.class_names")

    # Verify data_dir presence
    if not hasattr(cfg.dataset, 'data_dir'):
        raise ValueError("cfg.dataset.data_dir must be specified to locate raw dataset")

    dataset_format = getattr(cfg.dataset, "format", "").lower()

    if is_training or is_evaluation:
        if dataset_format == "darknet_yolo":
            raw_dataset_path = cfg.dataset.data_dir
            if not os.path.exists(raw_dataset_path):
                raise ValueError(f"Raw dataset path {raw_dataset_path} does not exist")

            # Create directory if training_path is specified (for processed data)
            if is_training and hasattr(cfg.dataset, 'training_path'):
                os.makedirs(cfg.dataset.training_path, exist_ok=True)

            if hasattr(cfg.dataset, 'validation_path') and cfg.dataset.validation_path:
                os.makedirs(cfg.dataset.validation_path, exist_ok=True)

            if is_training:
                tfs_dataset_path = raw_dataset_path
                print("Starting dataset analysis...")
                compute_class_stats(dataset_path=raw_dataset_path,
                                    dataset_name=getattr(cfg.dataset, 'dataset_name', None),
                                    histogram_dir="histograms")
                compute_labels_stats(dataset_path=raw_dataset_path,
                                    dataset_name=getattr(cfg.dataset, 'dataset_name', None),
                                    histogram_dir="histograms")
                print("Dataset analysis completed.\n")
            else:
                if not hasattr(cfg.dataset, 'test_path'):
                    raise ValueError("cfg.dataset.test_path must be specified in evaluation mode")
                if not os.path.exists(cfg.dataset.test_path):
                    raise ValueError(f"Test path {cfg.dataset.test_path} does not exist")
                tfs_dataset_path = cfg.dataset.test_path
                os.makedirs(tfs_dataset_path, exist_ok=True)

            print(f"Creating .tfs files for the {'training' if is_training else 'evaluation'} dataset...")
            exclude_unlabeled = (hasattr(cfg.dataset, 'exclude_unlabeled') and cfg.dataset.exclude_unlabeled)
            max_detections = (hasattr(cfg.dataset, 'max_detections') and cfg.dataset.max_detections)

            add_tfs_files_to_dataset(dataset_path=tfs_dataset_path,
                                    exclude_unlabeled_images=exclude_unlabeled,
                                    padded_labels_size=max_detections)
            print(".tfs files creation completed.")

        elif dataset_format == "tfs":
            # If format is tfs, directly load darknet-like without conversion or analysis
            print("Dataset format is 'tfs'. Skipping analysis and .tfs creation steps.")
            return load_subset_dataloaders(cfg, is_training, is_evaluation,
                                    is_prediction, is_quantization,
                                    image_size=image_size, val_batch_size=val_batch_size)
        else:
            raise ValueError(f"Unsupported dataset format '{dataset_format}' for training/evaluation mode.")

    else:
        # For modes other than training/evaluation, proceed with existing checks

        raw_dataset_path = cfg.dataset.data_dir
        if not os.path.exists(raw_dataset_path):
            raise ValueError(f"Raw dataset path {raw_dataset_path} does not exist")

        # Create directory if training_path is specified (for processed data)
        if is_training and hasattr(cfg.dataset, 'training_path'):
            os.makedirs(cfg.dataset.training_path, exist_ok=True)

        if hasattr(cfg.dataset, 'validation_path') and cfg.dataset.validation_path:
            os.makedirs(cfg.dataset.validation_path, exist_ok=True)

    if is_prediction:
        if not hasattr(cfg.dataset, 'prediction_path'):
            raise ValueError("cfg.dataset.prediction_path must be specified in prediction mode")
        if not os.path.exists(cfg.dataset.prediction_path):
            raise ValueError(f"Prediction path {cfg.dataset.prediction_path} does not exist")

    if is_quantization:
        if not hasattr(cfg.dataset, 'quantization_path'):
            raise ValueError("cfg.dataset.quantization_path must be specified in quantization mode")
        if not os.path.exists(cfg.dataset.quantization_path):
            raise ValueError(f"Quantization path {cfg.dataset.quantization_path} does not exist")

    print("Loading datasets in darknet format...")
    return load_subset_dataloaders(cfg, is_training, is_evaluation,
                            is_prediction, is_quantization,
                            image_size=image_size, val_batch_size=val_batch_size)