#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import glob
import json
import warnings
from pathlib import Path
from copy import deepcopy
from omegaconf import OmegaConf, DictConfig
from munch import DefaultMunch
import numpy as np
from hydra.core.hydra_config import HydraConfig

from common.utils import postprocess_config_dict, check_config_attributes, parse_tools_section, parse_benchmarking_section, \
                      parse_mlflow_section, parse_top_level, parse_general_section, parse_quantization_section, \
                      parse_training_section, parse_prediction_section, parse_deployment_section, check_hardware_type, \
                      parse_evaluation_section, get_class_names_from_file, check_attributes, parse_compression_section, parse_model_section

def parse_dataset_section(cfg: DictConfig, mode: str = None,
                          mode_groups: DictConfig = None,
                          hardware_type: str = None) -> None:

    # List all legal attributes from your dataset config
    legal = [
        "format",
        "dataset_name",
        "class_names",
        "download_data",
        "exclude_unlabeled",
        "max_detections",
        "train_images_path",
        "val_images_path",
        "train_annotations_path",
        "val_annotations_path",
        "train_xml_dir",
        "val_xml_dir",
        "train_split", 
        "test_split",
        "val_split",
        "data_dir",
        "training_path",
        "validation_path",
        "validation_split",
        "test_path",
        "prediction_path",
        "quantization_path",
        "quantization_split",
        "seed"
    ]

    legal_pt = ["seed", "num_workers", "multiscale_range", "random_size", "data_dir", 
                "test_annotations_path", "test_images_path", "prediction_path", 
                "quantization_split", "quantization_path", "mosaic_prob", "mixup_prob", "hsv_prob", 
                "flip_prob", "degrees", "translate", "mosaic_scale", "enable_mixup", 
                "mixup_scale", "shear"]
    legal = legal + legal_pt

    required = []
    one_or_more = []

    # Define required fields based on mode
    if mode in mode_groups.training:
        required += ["training_path"]
        required += ["format"]
    elif mode in mode_groups.evaluation:
        one_or_more += ["training_path", "test_path"]
    elif mode == "prediction":
        required += ["prediction_path"]

    # Validate config keys and required attributes
    check_config_attributes(cfg, specs={"legal": legal, "all": required, "one_or_more": one_or_more},
                            section="dataset")
    
    def _contains_images(dir_path):
        if not os.path.isdir(dir_path):
            return False
        image_files = []
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            image_files.extend(glob.glob(os.path.join(dir_path, ext)))
        return len(image_files) > 0
    
    # Enforce dataset.format presence if mode is in training and evaluation group
    if mode in mode_groups.training:
        fmt = getattr(cfg, "format", None)
        if not (isinstance(fmt, str) and fmt.strip() != ""):
            raise ValueError(f"In training mode, dataset.format must be defined and non-empty. Got: {fmt}")
        dataset_format = fmt.lower()

        # Additional check for 'tfs' format
        if dataset_format == "tfs":
            training_path = getattr(cfg, "training_path", None)
            if training_path is None:
                raise ValueError("For 'tfs' format in training mode, 'training_path' must be defined in dataset section.")

            if not os.path.isdir(training_path):
                raise ValueError(f"'training_path' directory '{training_path}' does not exist or is not a directory.")

            # Helper to find matching .jpg and .tfs files
            def _check_tfs_pairs(dir_path):
                jpg_files = set(os.path.splitext(f)[0] for f in os.listdir(dir_path) if f.lower().endswith(".jpg"))
                tfs_files = set(os.path.splitext(f)[0] for f in os.listdir(dir_path) if f.lower().endswith(".tfs"))
                missing_pairs = jpg_files.symmetric_difference(tfs_files)
                return missing_pairs

            missing_pairs = _check_tfs_pairs(training_path)
            if missing_pairs:
                warnings.warn(f"'training_path' directory '{training_path}' must contain matching .jpg and .tfs files for each sample. Missing pairs: {missing_pairs}",
                    UserWarning)
                
            # Optional check for test_path
            test_path = getattr(cfg, "test_path", None)
            if test_path is not None:
                if not os.path.isdir(test_path):
                    warnings.warn(f"'test_path' directory '{test_path}' does not exist or is not a directory.")
                else:
                    missing_pairs_test = _check_tfs_pairs(test_path)
                    if missing_pairs_test:
                        warnings.warn(f"'test_path' directory '{test_path}' does not have matching .jpg and .tfs files for each sample. Missing pairs: {missing_pairs_test}")

        if dataset_format == "coco":
            # Check required paths
            if not getattr(cfg, "train_images_path", None):
                raise ValueError("For COCO format, 'train_images_path' must be defined in dataset section.")
            if not getattr(cfg, "train_annotations_path", None):
                raise ValueError("For COCO format, 'train_annotations_path' must be defined in dataset section.")

            # Check train images directory
            if not _contains_images(cfg.train_images_path):
                raise ValueError(f"Training images directory '{cfg.train_images_path}' does not contain any jpg/jpeg/png images.")

            # Check train annotations file (json)
            train_ann_path = cfg.train_annotations_path
            if not (os.path.isfile(train_ann_path) and train_ann_path.lower().endswith(".json")):
                raise ValueError(f"Training annotations path '{train_ann_path}' is not a valid JSON file.")

            # Validate JSON file can be loaded
            try:
                with open(train_ann_path, 'r') as f:
                    json.load(f)
            except Exception as e:
                raise ValueError(f"Training annotation JSON file '{train_ann_path}' could not be loaded: {e}")

            # Optional val paths with warnings
            val_images_path = getattr(cfg, "val_images_path", None)
            val_annotations_path = getattr(cfg, "val_annotations_path", None)
            if val_images_path is None or not _contains_images(val_images_path):
                warnings.warn(f"Validation images path '{val_images_path}' is missing or does not contain images.")
            if val_annotations_path is None or not (os.path.isfile(val_annotations_path) and val_annotations_path.lower().endswith(".json")):
                warnings.warn(f"Validation annotations path '{val_annotations_path}' is missing or not a valid JSON file.")

        elif dataset_format == "pascal_voc":
            # Check required paths
            if not getattr(cfg, "train_images_path", None):
                raise ValueError("For Pascal VOC format, 'train_images_path' must be defined in dataset section.")
            if not getattr(cfg, "train_xml_dir", None):
                raise ValueError("For Pascal VOC format, 'train_xml_dir' must be defined in dataset section.")

            # Check train images directory
            if not _contains_images(cfg.train_images_path):
                raise ValueError(f"Training images directory '{cfg.train_images_path}' does not contain any jpg/jpeg/png images.")

            # Check train xml directory
            train_xml_dir = cfg.train_xml_dir
            if not os.path.isdir(train_xml_dir):
                raise ValueError(f"Training XML directory '{train_xml_dir}' does not exist or is not a directory.")

            # Count images and xml files and compare
            image_count = 0
            for ext in ("*.jpg", "*.jpeg", "*.png"):
                image_count += len(glob.glob(os.path.join(cfg.train_images_path, ext)))
            xml_count = len(glob.glob(os.path.join(train_xml_dir, "*.xml")))
            if image_count != xml_count:
                raise ValueError(f"Number of images ({image_count}) and XML annotation files ({xml_count}) in training set do not match.")

            # Optional val paths with warnings
            val_images_path = getattr(cfg, "val_images_path", None)
            val_xml_dir = getattr(cfg, "val_xml_dir", None)
            if val_images_path is None or not _contains_images(val_images_path):
                warnings.warn(f"Validation images path '{val_images_path}' is missing or does not contain images.")
            if val_xml_dir is None or not os.path.isdir(val_xml_dir):
                warnings.warn(f"Validation XML directory '{val_xml_dir}' is missing or not a directory.")
            else:
                val_image_count = 0
                for ext in ("*.jpg", "*.jpeg", "*.png"):
                    val_image_count += len(glob.glob(os.path.join(val_images_path, ext))) if val_images_path else 0
                val_xml_count = len(glob.glob(os.path.join(val_xml_dir, "*.xml")))
                if val_images_path and val_image_count != val_xml_count:
                    warnings.warn(f"Number of validation images ({val_image_count}) and XML files ({val_xml_count}) do not match.")

        elif dataset_format == "darknet_yolo":
            # Check data_dir
            if not getattr(cfg, "data_dir", None):
                raise ValueError("For Darknet YOLO format, 'data_dir' must be defined in dataset section.")

            data_dir = cfg.data_dir
            if not os.path.isdir(data_dir):
                raise ValueError(f"data_dir '{data_dir}' is not a valid directory.")

            # Check images presence
            if not _contains_images(data_dir):
                raise ValueError(f"data_dir '{data_dir}' does not contain any jpg/jpeg/png images.")

            # Check xml files presence
            xml_files = glob.glob(os.path.join(data_dir, "*.txt"))
            if len(xml_files) == 0:
                raise ValueError(f"data_dir '{data_dir}' does not contain any XTXTML annotation files.")

        else:
            # For now, do not support KITTI or other formats
            pass
    else:    
        # For non-training/evaluation modes, format is optional
        dataset_format = None
        if cfg is not None:
            fmt = getattr(cfg, "format", None)
            if isinstance(fmt, str) and fmt.strip() != "":
                dataset_format = fmt.lower()

    # For modes that require class names
    if mode_groups is not None and mode in getattr(mode_groups, "deployment", []):
        # Deployment mode: only check for class_names attribute
        one_or_more = ["class_names"]
        check_config_attributes(cfg, specs={"legal": legal, "all": None, "one_or_more": one_or_more},
                               section="dataset")
        if cfg.class_names:
            print("[INFO] : Using provided class names from dataset.class_names")
        else:
            print("[WARNING] : No class_names provided in dataset section for deployment mode")
    elif not mode in ["quantization", "benchmarking", "chain_qb", "prediction"]:
        # Existing logic for other modes
        one_or_more = ["class_names"]
        check_config_attributes(cfg, specs={"legal": legal, "all": None, "one_or_more": one_or_more},
                               section="dataset")
        if cfg.class_names:
            print("[INFO] : Using provided class names from dataset.class_names")
        elif getattr(cfg, "classes_file_path", None):
            cfg.class_names = get_class_names_from_file(cfg)
            print("[INFO] : Found {} classes in label file {}".format(len(cfg.class_names), cfg.classes_file_path))
        else:
            print("[WARNING] : No class_names or classes_file_path provided in dataset section")

    # Set num_classes based on class_names or default to 80
    if not getattr(cfg, "num_classes", None):
        cfg.num_classes = len(cfg.class_names) if cfg.class_names else 80

    # Set default values for optional attributes if missing
    #if not getattr(cfg, "dataset_name", None):
    #    cfg.dataset_name = "unnamed"
    if not getattr(cfg, "validation_split", None):
        cfg.validation_split = 0.2
    if not getattr(cfg, "seed", None):
        cfg.seed = 123
    if not hasattr(cfg, "download_data"):
        cfg.download_data = False
    if not hasattr(cfg, "exclude_unlabeled"):
        cfg.exclude_unlabeled = True
    if not hasattr(cfg, "max_detections"):
        cfg.max_detections = 20

    # Validate validation_split value
    if cfg.validation_split:
        split = cfg.validation_split
        if split <= 0.0 or split >= 1.0:
            raise ValueError(f"\nThe value of `validation_split` should be > 0 and < 1. Received {split}\n"
                             "Please check the 'dataset' section of your configuration file.")

    # Validate quantization_split value
    if cfg.quantization_split and cfg.quantization_split is not None:
        split = cfg.quantization_split
        if split <= 0.0 or split > 1.0:
            raise ValueError(f"\nThe value of `quantization_split` should be > 0 and <= 1. Received {split}\n"
                             "Please check the 'dataset' section of your configuration file.")
            

def parse_preprocessing_section(cfg: DictConfig,
                                mode:str = None) -> None:
    # cfg: 'preprocessing' section of the configuration file
    legal = ["rescaling", "resizing", "color_mode", "normalization", "mean", "std"]
    required = ["rescaling", "resizing", "color_mode"]
    if mode == 'deployment':
        # removing the obligation to have rescaling for the 'deployment' mode
        required=["resizing", "color_mode"]
        check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="preprocessing")
    else:
        check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="preprocessing")
        legal = ["scale", "offset"]
        check_config_attributes(cfg.rescaling, specs={"legal": legal, "all": legal}, section="preprocessing.rescaling")

    legal = ["interpolation", "aspect_ratio"]
    check_config_attributes(cfg.resizing, specs={"legal": legal, "all": legal}, section="preprocessing.resizing")
    if cfg.resizing.aspect_ratio not in ("fit", "crop", "padding"):
        raise ValueError("\nSupported methods for resizing images are 'fit', 'crop' and 'padding'. "
                         f"Received {cfg.resizing.aspect_ratio}\n"
                         "Please check the `resizing.aspect_ratio` attribute in "
                         "the 'preprocessing' section of your configuration file.")
                         
    # Check resizing interpolation value
    interpolation_methods = ["bilinear", "nearest", "area", "lanczos3", "lanczos5", "bicubic", "gaussian",
                             "mitchellcubic"]
    if cfg.resizing.interpolation not in interpolation_methods:
        raise ValueError(f"\nUnknown value for `interpolation` attribute. Received {cfg.resizing.interpolation}\n"
                         f"Supported values: {interpolation_methods}\n"
                         "Please check the 'resizing.attribute' in the 'preprocessing' section of your configuration file.")

    # Check color mode value
    color_modes = ["grayscale", "rgb", "rgba", "bgr"]
    if cfg.color_mode not in color_modes:
        raise ValueError(f"\nUnknown value for `color_mode` attribute. Received {cfg.color_mode}\n"
                         f"Supported values: {color_modes}\n"
                         "Please check the 'preprocessing' section of your configuration file.")


def parse_data_augmentation_section(cfg: DictConfig) -> None:
    """
    This function checks the data augmentation section of the config file.
    The attribute that introduces the section is either `data_augmentation`
    or `custom_data_augmentation`. If it is `custom_data_augmentation`,
    the name of the data augmentation function that is provided must be
    different from `data_augmentation` as this is a reserved name.

    Arguments:
        cfg (DictConfig): The entire configuration file as a DefaultMunch dictionary.
        config_dict (Dict): The entire configuration file as a regular Python dictionary.

    Returns:
        None
    """

    if cfg.data_augmentation and cfg.custom_data_augmentation:
        raise ValueError("\nThe `data_augmentation` and `custom_data_augmentation` attributes "
                         "are mutually exclusive.\nPlease check your configuration file.")
    
    if cfg.data_augmentation:
        data_aug = DefaultMunch.fromDict({})
        # The name of the Model Zoo data augmentation function is 'data_augmentation'.
        data_aug.function_name = "data_augmentation"
        data_aug.config = deepcopy(cfg.data_augmentation)

    if cfg.custom_data_augmentation:
        check_attributes(cfg.custom_data_augmentation,
                         expected=["function_name"],
                         optional=["config"],
                         section="custom_data_augmentation")
        if cfg.custom_data_augmentation["function_name"] == "data_augmentation":
            raise ValueError("\nThe function name `data_augmentation` is reserved.\n"
                             "Please use another name (attribute `function_name` in "
                             "the 'custom_data_augmentation' section).")
                                                          
        data_aug = DefaultMunch.fromDict({})
        data_aug.function_name = cfg.custom_data_augmentation.function_name
        if cfg.custom_data_augmentation.config:
            data_aug.config = deepcopy(cfg.custom_data_augmentation.config)
    
    cfg.data_augmentation = data_aug


def _parse_postprocessing_section(cfg: DictConfig, model_type: str) -> None:
    # cfg: 'postprocessing' section of the configuration file

    legal = ["confidence_thresh", "NMS_thresh", "IoU_eval_thresh", "yolo_anchors", "plot_metrics",
             'max_detection_boxes', 'crop_stretch_percents']
    required = ["confidence_thresh", "NMS_thresh", "IoU_eval_thresh"]
    check_config_attributes(cfg, specs={"legal": legal, "all": required}, section="postprocessing")

    if model_type == "yolov2t":
        cfg.network_stride = 32
    elif model_type == "st_yololcv1":
        cfg.network_stride = 16
    elif model_type == "st_yoloxn":
        cfg.network_stride = [8,16,32]
    
    # Set default YOLO anchors
    if not cfg.yolo_anchors and model_type == "st_yoloxn":
        cfg.yolo_anchors = [0.5, 0.5]
    elif not cfg.yolo_anchors:
        cfg.yolo_anchors = [0.076023, 0.258508, 0.163031, 0.413531, 0.234769, 0.702585, 0.427054, 0.715892, 0.748154, 0.857092]
    print("cfg.yolo_anchors:",cfg.yolo_anchors)
    # Check the YOLO anchors syntax and convert to a numpy array
    if len(cfg.yolo_anchors) % 2 != 0:
        raise ValueError("\nThe Yolo anchors list should contain an even number of floats.\n"
                         "Please check the value of the 'postprocessing.yolo_anchors' attribute "
                         "in your configuration file.")
    num_anchors = int(len(cfg.yolo_anchors) / 2)
    cfg.num_anchors = num_anchors
    anchors = np.array(cfg.yolo_anchors, dtype=np.float32)
    cfg.yolo_anchors = np.reshape(anchors, [num_anchors, 2])
    
    cfg.plot_metrics = cfg.plot_metrics if cfg.plot_metrics is not None else False


def get_config(config_data: DictConfig) -> DefaultMunch:
    """
    Converts the configuration data, performs some checks and reformats
    some sections so that they are easier to use later on.

    Args:
        config_data (DictConfig): dictionary containing the entire configuration file.

    Returns:
        DefaultMunch: The configuration object.
    """

    config_dict = OmegaConf.to_container(config_data)

    # Restore booleans, numerical expressions and tuples
    # Expand environment variables
    postprocess_config_dict(config_dict, replace_none_string=True)

    # Top level section parsing
    cfg = DefaultMunch.fromDict(config_dict)
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
    mode_choices = ["training", "evaluation", "deployment",
                    "quantization", "benchmarking", "chain_tqeb", "chain_tqe",
                    "chain_eqe", "chain_qb", "chain_eqeb", "chain_qd", "prediction", "compression"]
    legal = ["general", "model", "operation_mode", "dataset", "compression", "preprocessing", "data_augmentation",
             "training", "postprocessing", "quantization", "evaluation", "prediction", "tools",
             "benchmarking", "deployment", "mlflow", "hydra"]
    parse_top_level(cfg, 
                    mode_groups=mode_groups,
                    mode_choices=mode_choices,
                    legal=legal)
    print(f"[INFO] : Running `{cfg.operation_mode}` operation mode")
    cfg.use_case = "object_detection"
    if cfg.model:
        legal = ["framework", "model_path", "resume_training_from", "model_name", "pretrained", "input_shape",
                 "depth_mul", "width_mul", "model_type"]
        
        legal_pt = ["pretrained_dataset", "pretrained_input_shape", "depthwise", "num_classes", "depth", "width", "act", "in_channels", 
                    "out_features", "width_mult"]
        
        
        
        legal = legal + legal_pt 
        required=["model_type"]
        parse_model_section(cfg.model, mode=cfg.operation_mode, mode_groups=mode_groups, legal=legal, required=required)
    # General section parsing
    if not cfg.general:
        cfg.general = DefaultMunch.fromDict({})
    legal = ["project_name", "logs_dir", "saved_models_dir", "deterministic_ops",
            "display_figures", "global_seed", "gpu_memory_limit", "num_threads_tflite"]
    
    legal_pt = [
    "saved_models_dir", "resume_training_from","start_epoch",
    "fp16","occupy","logger","global_seed"]
    
    legal = legal + legal_pt
    required = []
    parse_general_section(cfg.general, 
                          mode=cfg.operation_mode, 
                          mode_groups=mode_groups,
                          legal=legal,
                          required=required,
                          output_dir = HydraConfig.get().runtime.output_dir)
                          
    # Select hardware_type from yaml information
    check_hardware_type(cfg, mode_groups)
                        
    # Dataset section parsing
    if not cfg.dataset:
        cfg.dataset = DefaultMunch.fromDict({})
    
    
    parse_dataset_section(cfg.dataset,
                          mode=cfg.operation_mode,
                          mode_groups=mode_groups,
                          hardware_type=cfg.hardware_type)
                          
    # Preprocessing section parsing
    parse_preprocessing_section(cfg.preprocessing,
                                mode=cfg.operation_mode)

    # Data augmentation section parsing
    if cfg.operation_mode in mode_groups.training:
        if cfg.data_augmentation or cfg.custom_data_augmentation:
            parse_data_augmentation_section(cfg)

    # Compression section parsing
    if cfg.operation_mode in mode_groups.compression:
        legal = ["factor", "strong_optimization"]
        parse_compression_section(cfg.compression,
                                   legal=legal)

    # Training section parsing
    if cfg.operation_mode in mode_groups.training:
        model_path_used = bool(cfg.model.model_path)
        model_type_used = bool(cfg.model.model_type)
        legal = ["batch_size", "epochs", "optimizer", "dropout", "frozen_layers",
                "callbacks", "dryrun"]
        
        legal_pt = ["trainer_name", "batch_size", "warmup_epochs", "max_epoch", "warmup_lr", "min_lr_ratio", 
         "basic_lr_per_img", "scheduler", "no_aug_epochs", "ema", "weight_decay", 
         "momentum", "print_interval", "eval_interval", "save_history_ckpt", "validation_epochs", 
         "lr","base_net_lr", "extra_layers_lr", "gamma", "scheduler","t_max", "resume_training_from", "start_epoch", "fp16"]
  
        legal = legal + legal_pt

        parse_training_section(cfg.training,
                               legal=legal) 
        if cfg.model.framework == "tf":
            cfg.training.trainer_name = "od_trainer"

    # Postprocessing section parsing
    # This section is always needed except for benchmarking.
    if cfg.operation_mode in (mode_groups.training + mode_groups.evaluation +
                              mode_groups.quantization + mode_groups.deployment +
                              mode_groups.prediction + mode_groups.compression):
        if cfg.hardware_type == "MCU":
            _parse_postprocessing_section(cfg.postprocessing, cfg.model.model_type)

    # Quantization section parsing
    if cfg.operation_mode in mode_groups.quantization:
        legal = ["quantizer", "quantization_type", "quantization_input_type", "quantization_output_type", "granularity",
                 "export_dir", "optimize", "target_opset", "operating_mode",
                 "onnx_quant_parameters", "onnx_extra_options", "iterative_quant_parameters"]
        parse_quantization_section(cfg.quantization,
                                   legal=legal)

    # Evaluation section parsing
    if cfg.operation_mode in mode_groups.evaluation:
        if not "evaluation" in cfg:
            cfg.evaluation = DefaultMunch.fromDict({})
        legal = ["gen_npy_input", "gen_npy_output", "npy_in_name", "npy_out_name", "target", 
                 "profile", "input_type", "output_type", "input_chpos", "output_chpos"]
        parse_evaluation_section(cfg.evaluation,
                                 legal=legal)

    # Prediction section parsing
    if cfg.operation_mode == "prediction":
        if not "prediction" in cfg:
            cfg.prediction = DefaultMunch.fromDict({})
        parse_prediction_section(cfg.prediction)

    # Tools section parsing
    if (
        cfg.operation_mode in (mode_groups.benchmarking + mode_groups.deployment)
        or (
            cfg.operation_mode == "evaluation"
            and "evaluation" in cfg
            and "target" in cfg.evaluation
            and cfg.evaluation.target != "host"
        )
        or (
            cfg.operation_mode == "prediction"
            and "prediction" in cfg
            and "target" in cfg.prediction
            and cfg.prediction.target != "host"
        )
    ):
        parse_tools_section(cfg.tools, 
                            cfg.operation_mode,
                            cfg.hardware_type)

    #For MPU, check if online benchmarking is activated
    if cfg.operation_mode in mode_groups.benchmarking:
        if "STM32MP" in cfg.benchmarking.board :
            if cfg.operation_mode == "benchmarking" and not(cfg.tools.stedgeai.on_cloud):
                print("Target selected for benchmark :", cfg.benchmarking.board)
                print("Offline benchmarking for MPU is not yet available please use online benchmarking")
                exit(1)

    # Benchmarking section parsing
    if cfg.operation_mode in mode_groups.benchmarking:
        parse_benchmarking_section(cfg.benchmarking)
        if cfg.hardware_type == "MPU" :
            if not (cfg.tools.stedgeai.on_cloud):
                print("Target selected for benchmark :", cfg.benchmarking.board)
                print("Offline benchmarking for MPU is not yet available please use online benchmarking")
                exit(1)

    # Deployment section parsing
    if cfg.operation_mode in mode_groups.deployment:
        if cfg.hardware_type == "MCU":
            legal = ["c_project_path", "IDE", "verbosity", "hardware_setup"]
            legal_hw = ["serie", "board", "stlink_serial_number"]
            # Append additional items if board is "NUCLEO-H743ZI2"
            if cfg.deployment.hardware_setup.board == "NUCLEO-H743ZI2":
                legal_hw += ["input", "output"]
            # Append additional items if board is "NUCLEO-N657X0-Q"
            if cfg.deployment.hardware_setup.board == "NUCLEO-N657X0-Q":
                legal_hw += ["output"]
        else:
            legal = ["c_project_path", "board_deploy_path", "verbosity", "hardware_setup"]
            legal_hw = ["serie", "board", "ip_address", "stlink_serial_number"]
            if cfg.preprocessing.color_mode != "rgb":
                raise ValueError("\n Color mode used is not supported for deployment on MPU target \n Please use RGB format")
            if cfg.preprocessing.resizing.aspect_ratio != "fit":
                raise ValueError("\n Aspect ratio used is not supported for deployment on MPU target \n Please use 'fit' aspect ratio")
        parse_deployment_section(cfg.deployment,
                                 legal=legal,
                                 legal_hw=legal_hw)

    # MLFlow section parsing
    parse_mlflow_section(cfg.mlflow)

    return cfg
