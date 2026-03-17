# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2025 STMicroelectronics.
#  * All rights reserved.
#  *--------------------------------------------------------------------------------------------*/

import os
import numpy as np
from pathlib import Path
from timeit import default_timer as timer
from datetime import timedelta
from typing import List, Optional, Dict

import tensorflow as tf
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig

# Suppress TF warnings
import logging
logging.getLogger('mlflow.tensorflow').setLevel(logging.ERROR)
logging.getLogger('tensorflow').setLevel(logging.ERROR)

from common.utils import (
    log_to_file, log_last_epoch_history,
    model_summary, vis_training_curves, parse_random_periodic_resizing,
    check_training_determinism 
)
from common.training import set_frozen_layers, get_optimizer, set_dropout_rate
from object_detection.tf.src.utils import get_sizes_ratios_ssd_v1, get_sizes_ratios_ssd_v2, \
                  get_fmap_sizes, get_anchor_boxes, change_yolo_model_number_of_classes, change_yolo_x_model_number_of_classes
from object_detection.tf.src.models import model_family
from object_detection.tf.src.training.utils.callbacks import get_callbacks
from object_detection.tf.src.training.utils.ssd.ssd_train_model import SSDTrainingModel
from object_detection.tf.src.training.utils.yolo.yolo_train_model import YoloTrainingModel
from object_detection.tf.src.training.utils.yolo.yolo_x_train_model import YoloXTrainingModel

class ODTrainer:
    """
    Object detection trainer.

    Public workflow:
        trainer.prepare()
        trainer.enable_determinism()
        trainer.fit()
        best_model = trainer.save_and_evaluate()
        # or simply: best_model = trainer.train()

    SSDTrainingModel, YoloTrainingModel and YoloXTrainingModel wraps
    base model with preprocessing and data augmentation.
    """
    def __init__(self, cfg: DictConfig, model: tf.keras.Model, dataloaders: Dict[str, tf.data.Dataset]):
        """
        Initialize trainer with configuration, base model and dataloaders.

        Args:
            cfg: Hydra DictConfig containing all sections.
            model: Base segmentation backbone/head tf.keras.Model.
            dataloaders: Dict with keys 'train', 'valid', optional 'test' mapping to tf.data.Dataset.
        """
        self.cfg = cfg
        self.base_model = model
        self.train_ds = dataloaders.get('train')
        self.valid_ds = dataloaders.get('valid')
        self.test_ds = dataloaders.get('test')
        self.output_dir = Path(HydraConfig.get().runtime.output_dir)
        self.saved_models_dir = os.path.join(self.output_dir, cfg.general.saved_models_dir)
        self.callbacks = None
        self.history = None
        self.train_model = None
        self.class_names = cfg.dataset.class_names
        self.num_classes = len(self.class_names)

    def prepare(self):
        """
        Prepare training artifacts:
          - Create output directories.
          - Log dataset/model info.
          - Adjust number of classes.
          - Freeze layers if requested.
          - Wrap model in SegmentationTrainingModel (adds preprocessing & augmentation).
          - Compile wrapped model.
          - Instantiate callbacks.
        """
        Path(self.saved_models_dir).mkdir(parents=True, exist_ok=True)
        train_batches = sum(1 for _ in self.train_ds) if self.train_ds is not None else 0
        valid_batches = sum(1 for _ in self.valid_ds) if self.valid_ds is not None else 0
        test_batches = sum(1 for _ in self.test_ds) if self.test_ds is not None else 0
        print("Dataset stats:")
        print("  classes:", self.num_classes)
        print("  training batches:", train_batches)
        print("  validation batches:", valid_batches)
        print("  test batches:" if self.test_ds else "  no test set", test_batches if self.test_ds else "")

        # Log dataset and model info
        log_to_file(self.output_dir, f"Dataset : {self.cfg.dataset.dataset_name}")
        if self.cfg.model.model_name:
            log_to_file(self.output_dir, f"Model name : {self.cfg.model.model_name}")
            print(f"[INFO] : using {self.cfg.model.model_name} model")
            if self.cfg.model.pretrained_weights:
                print(f"[INFO] : Initialized model with '{self.cfg.model.pretrained_weights}' pretrained weights")
                log_to_file(self.output_dir,(f"Pretrained weights : {self.cfg.model.pretrained_weights}"))

        elif self.cfg.model.model_path:
            print(f"[INFO] : The model type is {self.cfg.model.model_path}")
            log_to_file(self.output_dir, f"Model type : {self.cfg.model.model_type}")
            if self.cfg.model.resume_training_from:
                log_to_file(self.output_dir, f"Resuming training from : {self.cfg.model.model_path}")
                print(f"[INFO] : resuming training from {self.cfg.model.model_path} model")
            else:
                print(f"[INFO] : using {self.cfg.model.model_path} model")
                log_to_file(self.output_dir, f"Model file : {self.cfg.model.model_path}")
                if self.cfg.model.model_type in ["yolov2t","st_yololcv1"]:
                    self.base_model = change_yolo_model_number_of_classes(self.base_model,num_classes=self.num_classes,
                                                                num_anchors=len(self.cfg.postprocessing.yolo_anchors))
                elif self.cfg.model.model_type in ["st_yoloxn"]:
                    self.base_model = change_yolo_x_model_number_of_classes(self.base_model,num_classes=self.num_classes,
                                                                num_anchors=len(self.cfg.postprocessing.yolo_anchors))

        self.base_model.compile()
        base_model_path = os.path.join(self.saved_models_dir, "base_model.keras")
        self.base_model.save(base_model_path)

        if getattr(self.cfg.training, "frozen_layers", None) and self.cfg.training.frozen_layers != "None":
            set_frozen_layers(self.base_model, frozen_layers=self.cfg.training.frozen_layers)

        # Set rate on dropout layer if any
        if getattr(self.cfg.training, "dropout", None) and self.cfg.training.dropout:
            set_dropout_rate(self.base_model, dropout_rate=self.cfg.training.dropout)

        model_summary(self.base_model)
        
        print("Metrics calculation parameters:")
        print("  confidence threshold:", self.cfg.postprocessing.confidence_thresh)
        print("  NMS IoU threshold:", self.cfg.postprocessing.NMS_thresh)
        print("  max detection boxes:", self.cfg.postprocessing.max_detection_boxes)
        print("  metrics IoU threshold:", self.cfg.postprocessing.IoU_eval_thresh)

        scale = self.cfg.preprocessing.rescaling.scale
        offset = self.cfg.preprocessing.rescaling.offset
        pixels_range = (offset, scale * 255 + offset)
        
        # Get the number of groundtruth labels used in the datasets
        _, labels = iter(self.train_ds).next()
        num_labels = int(tf.shape(labels)[1])

        # Get the size of the validation set
        val_dataset_size = sum([x.shape[0] for x, _ in self.valid_ds])
        exmpl,_  = iter(self.valid_ds).next()
        batch_size = exmpl.shape[0]
        
        #change number of classes in the model if needed
        model_input_shape = self.cfg.model.input_shape
        if None in tuple(model_input_shape):
            raise ValueError(f"\nThe model input shape is unspecified. Got {str(model_input_shape)}\n"
                            "Unable to proceed with training.")
        
        if model_family(self.cfg.model.model_type) == "ssd":
            # Get the anchor boxes
            fmap_sizes = get_fmap_sizes(self.cfg.model.model_type, model_input_shape)

            if self.cfg.model.model_type == "st_ssd_mobilenet_v1":
                anchor_sizes, anchor_ratios = get_sizes_ratios_ssd_v1(model_input_shape)
            elif self.cfg.model.model_type == "ssd_mobilenet_v2_fpnlite":
                anchor_sizes, anchor_ratios = get_sizes_ratios_ssd_v2(model_input_shape)

            anchor_boxes = get_anchor_boxes(
                                fmap_sizes,
                                model_input_shape[:2],
                                sizes=anchor_sizes,
                                ratios=anchor_ratios,
                                normalize=True,
                                clip_boxes=False)
            
            # Concatenate scores, boxes and anchors
            # to get a model suitable for training
            tmoutput = tf.keras.layers.Concatenate(axis=2, name='predictions')(self.base_model.outputs)
            train_model = tf.keras.models.Model(inputs=self.base_model.input, outputs=tmoutput)

            data_augmentation_cfg = self.cfg.data_augmentation.config if self.cfg.data_augmentation else None
            num_anchors = np.shape(anchor_boxes)[0]
            cpp = self.cfg.postprocessing
            self.train_model = SSDTrainingModel(
                                train_model,
                                num_classes=len(self.class_names),
                                num_anchors=num_anchors,
                                num_labels=num_labels,
                                num_detections=anchor_boxes.shape[0],
                                val_dataset_size=val_dataset_size,
                                batch_size=batch_size,
                                anchor_boxes=anchor_boxes,
                                data_augmentation_cfg=data_augmentation_cfg,
                                pixels_range=pixels_range,
                                image_size=model_input_shape[:2],
                                pos_iou_threshold=0.5,
                                neg_iou_threshold=0.3,
                                max_detection_boxes=cpp.max_detection_boxes,
                                nms_score_threshold=cpp.confidence_thresh,
                                nms_iou_threshold=cpp.NMS_thresh,
                                metrics_iou_threshold=cpp.IoU_eval_thresh)
        elif model_family(self.cfg.model.model_type) == "yolo":
            cpp = self.cfg.postprocessing

            print("Using Yolo anchors:")
            for anchor in cpp.yolo_anchors:
                print(" ", anchor)

            data_augmentation_cfg = self.cfg.data_augmentation.config if self.cfg.data_augmentation else None

            # Create the custom model
            self.train_model = YoloTrainingModel(
                                self.base_model,
                                network_stride=cpp.network_stride,
                                num_classes=self.num_classes,
                                num_labels=num_labels,
                                anchors=cpp.yolo_anchors,
                                data_augmentation_cfg=data_augmentation_cfg,
                                val_dataset_size=val_dataset_size,
                                batch_size=batch_size,
                                pixels_range=pixels_range,
                                image_size=model_input_shape[:2],
                                max_detection_boxes=cpp.max_detection_boxes,
                                nms_score_threshold=cpp.confidence_thresh,
                                nms_iou_threshold=cpp.NMS_thresh,
                                metrics_iou_threshold=cpp.IoU_eval_thresh)
        elif model_family(self.cfg.model.model_type) == "st_yoloxn":
            cpp = self.cfg.postprocessing

            print("Using Yolo anchors:")
            for anchor in cpp.yolo_anchors:
                print(" ", anchor)

            if self.cfg.training.model is not None:
                ctm = self.cfg.training.model
                print("Using depth_mul: ",ctm.depth_mul)
                print("Using width_mul: ",ctm.width_mul)

            data_augmentation_cfg = self.cfg.data_augmentation.config if self.cfg.data_augmentation else None

            # Create the custom model
            self.train_model = YoloXTrainingModel(
                                self.base_model,
                                network_stride=cpp.network_stride,
                                num_classes=self.num_classes,
                                num_labels=num_labels,
                                anchors=cpp.yolo_anchors,
                                data_augmentation_cfg=data_augmentation_cfg,
                                val_dataset_size=val_dataset_size,
                                batch_size=batch_size,
                                pixels_range=pixels_range,
                                image_size=model_input_shape[:2],
                                max_detection_boxes=cpp.max_detection_boxes,
                                nms_score_threshold=cpp.confidence_thresh,
                                nms_iou_threshold=cpp.NMS_thresh,
                                metrics_iou_threshold=cpp.IoU_eval_thresh)

        self.train_model.compile(optimizer=get_optimizer(self.cfg.training.optimizer))
        
        # If multi-resolution is used, we need to check that the
        # random image sizes are compatible with the network stride.
        image_sizes = None
        period = None
        if self.cfg.data_augmentation:
            cda = self.cfg.data_augmentation #cfg.data_augmentation.config
            cpp = self.cfg.postprocessing
            message = "\nPlease check the `random_periodic_resizing` section in your configuration file."
            if "random_periodic_resizing" in cda:
                # Parse the random image sizes and check that
                # they are compatible with the network stride
                image_sizes = parse_random_periodic_resizing(cda.random_periodic_resizing, cpp.network_stride)
                period = self.cfg.data_augmentation.config.random_periodic_resizing.period

        # Set up callbacks
        tensorboard_log_dir = os.path.join(self.output_dir, self.cfg.general.logs_dir)
        metrics_dir = os.path.join(self.output_dir, self.cfg.general.logs_dir, "metrics")
        
        self.callbacks = get_callbacks(
                    cfg=self.cfg.training.callbacks,
                    num_classes=self.num_classes,
                    iou_eval_threshold=self.cfg.postprocessing.IoU_eval_thresh,
                    image_sizes=image_sizes,
                    period=period,
                    saved_models_dir=self.saved_models_dir,
                    log_dir=tensorboard_log_dir,
                    metrics_dir=metrics_dir)

    def enable_determinism(self):
        """
        Enable deterministic TensorFlow operations if cfg.general.deterministic_ops is True.

        Falls back to non-deterministic if verification fails.
        """
        if getattr(self.cfg.general, "deterministic_ops", False):
            sample = self.train_ds.take(1)
            tf.config.experimental.enable_op_determinism()
            if not check_training_determinism(self.train_model, sample):
                print("[WARNING] Some ops are not deterministic, disabling determinism.")
                tf.config.experimental.enable_op_determinism.__globals__['_pywrap_determinism'].enable(False)

    def fit(self):
        """
        Execute Keras fit loop on wrapped training model.

        Handles optional dry-run (steps_per_epoch override), logs runtime,
        and records final epoch metrics. Optionally plots curves.
        """
        print("[INFO] : Starting training")
        steps_per_epoch = self.cfg.training.dryrun if getattr(self.cfg.training, "dryrun", None) else None
        start_time = timer()
        self.history = self.train_model.fit(
            self.train_ds,
            validation_data=self.valid_ds,
            epochs=self.cfg.training.epochs,
            callbacks=self.callbacks,
            steps_per_epoch=steps_per_epoch
        )
        end_time = timer()
        # Log the last epoch history
        last_epoch = log_last_epoch_history(self.cfg, self.output_dir)
        # Calculate and log the runtime in the log file
        fit_run_time = int(end_time - start_time)
        avg_time = round(fit_run_time / (int(last_epoch) + 1), 2)
        print("Training runtime:", str(timedelta(seconds=fit_run_time)))
        log_to_file(self.output_dir, f"Training runtime : {fit_run_time} s\nAverage time per epoch : {avg_time} s")
        if self.cfg.general.display_figures:
            vis_training_curves(history=self.history, output_dir=self.output_dir)

    def save(self):
        """
        Save best and last models by loading stored weights into base model.
        Evaluates best model on validation and test datasets if provided.

        Returns:
            best_model (tf.keras.Model): Unwrapped model loaded with best weights.
        """
        best_weights_path = os.path.join(self.saved_models_dir, "best_weights.weights.h5")
        best_model_path = os.path.join(self.saved_models_dir, "best_model.keras")
        last_weights_path = os.path.join(self.saved_models_dir, "last_weights.weights.h5")
        last_model_path = os.path.join(self.saved_models_dir, "last_model.keras")

        # Save the last and the best models
        self.base_model.load_weights(best_weights_path)
        self.base_model.save(best_model_path)
        self.base_model.load_weights(last_weights_path)
        self.base_model.save(last_model_path)

        print("[INFO] Saved trained models:")
        print("  best model:", best_model_path)
        print("  last model:", last_model_path)

        # Load the best model as an object and pass to evaluate
        best_model = tf.keras.models.load_model(best_model_path, compile=False)
        setattr(best_model, 'model_path', best_model_path)
        print('[INFO] : Training complete.')
        
        return best_model

    def train(self):
        """
        Convenience orchestration method running:
          prepare -> enable_determinism -> fit -> save_and_evaluate

        Returns:
            best_model (tf.keras.Model)
        """
        self.prepare()
        self.enable_determinism()
        self.fit()
        return self.save()
