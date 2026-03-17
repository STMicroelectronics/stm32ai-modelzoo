
# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import sys
import torch
import cv2
import numpy as np
import tqdm
import mlflow
import onnx
import onnxruntime
import tensorflow as tf
import matplotlib.pyplot as plt
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from timeit import default_timer as timer
from datetime import timedelta
from tabulate import tabulate
from pathlib import Path

from object_detection.tf.src.postprocessing import get_detections, generate_ssd_priors,convert_locations_to_boxes
from object_detection.tf.src.utils import ai_runner_invoke
from object_detection.tf.src.utils import ObjectDetectionMetricsData, calculate_objdet_metrics, calculate_average_metrics
from common.evaluation import model_is_quantized
from common.utils import (
    ai_runner_interp, ai_interp_input_quant, ai_interp_outputs_dequant, log_to_file
)  # Common utilities for evaluation and visualization


class ONNXModelEvaluator:
    """
    A class to evaluate ONNX object detection models.

    Args:
        cfg (DictConfig): Configuration object for evaluation.
        model (onnxruntime.InferenceSession): The ONNX InferenceSession object.
        dataloaders (dict): Dictionary containing datasets for testing and validation.
    """
    def __init__(self, cfg: DictConfig, model: onnxruntime.InferenceSession,
                 dataloaders: dict = None):
        self.cfg = cfg
        self.model = model
        self.test_ds = dataloaders['test']
        self.valid_ds = dataloaders['valid']
        self.output_dir = HydraConfig.get().runtime.output_dir
        self.class_names = cfg.dataset.class_names
        self.eval_ds = None
        self.name_ds = None

    def _prepare_evaluation(self):
        """
        Prepares the evaluation process by selecting the appropriate dataset.
        """
        if self.test_ds:
            self.eval_ds = self.test_ds
            self.name_ds = "test_set"
        else:
            self.eval_ds = self.valid_ds
            self.name_ds = "validation_set"

    def _get_target(self):
        if self.cfg.evaluation and self.cfg.evaluation.target:
            return self.cfg.evaluation.target
        return "host"

    def _get_interpreter(self, target):
        name_model = os.path.basename(self.model.model_path)
        return ai_runner_interp(target, name_model)

    def _display_objdet_metrics(self, metrics, class_names):
        table = []
        classes = list(metrics.keys())
        for c in sorted(classes):
            table.append([
                class_names[c],
                round(100 * metrics[c].pre, 1),
                round(100 * metrics[c].rec, 1),
                round(100 * metrics[c].ap, 1)])

        print()
        headers = ["Class name", "Precision %", "  Recall %", "   AP %  "]
        print()
        print(tabulate(table, headers=headers, tablefmt="pipe", numalign="center"))

        mpre, mrec, mAP = calculate_average_metrics(metrics)

        print("\nAverages over classes %:")
        print("-----------------------")
        print(" Mean precision: {:.1f}".format(100 * mpre))
        print(" Mean recall:    {:.1f}".format(100 * mrec))
        print(" Mean AP (mAP):  {:.1f}".format(100 * mAP))

    def _plot_precision_versus_recall(self, metrics, class_names, plots_dir):
        """
        Plot the precision versus recall curves. AP values are the areas under these curves.
        """
        if os.path.exists(plots_dir):
            import shutil
            shutil.rmtree(plots_dir)
        os.makedirs(plots_dir)

        for c in list(metrics.keys()):
            figure = plt.figure(figsize=(10, 10))
            plt.xlabel("recall")
            plt.ylabel("interpolated precision")
            plt.title("Class '{}' (AP = {:.2f})".
                      format(class_names[c], metrics[c].ap * 100))
            plt.plot(metrics[c].interpolated_precision, metrics[c].interpolated_recall)
            plt.grid()
            plt.savefig(f"{plots_dir}/{class_names[c]}.png")
            plt.close(figure)

    def _run_evaluate(self):
        """
        Runs the evaluation process and computes metrics.

        Returns:
            dict: Dictionary of evaluation metrics for each class.
        """
        self._prepare_evaluation()
        tf.print(f'[INFO] : Evaluating the ONNX object detection model using {self.name_ds}...')
        target = self._get_target()
        input_pos = getattr(self.cfg.evaluation, 'input_chpos', 'chlast') if hasattr(self.cfg, 'evaluation') else 'chlast'
        output_pos = getattr(self.cfg.evaluation, 'input_chpos', 'chlast') if hasattr(self.cfg, 'evaluation') else 'chlast'
        ai_runner_interpreter = self._get_interpreter(target=target)

        # Load and parse ONNX model file (optional, for validation or info)
        model_path = getattr(self.model, "model_path", None)
        if model_path:
            onx = onnx.load(model_path)
            # ensure the model file is not corrupted or invalid
            onnx.checker.check_model(onx)

        input_shape = self.model.get_inputs()[0].shape  # e.g. [batch, channels, height, width] or similar

        model_batch_size = input_shape[0]
        if model_batch_size != 1 and target == 'host':
            batch_size = 64
        else:
            batch_size = 1

        # Adjust input shape for image size (assuming channels first for ONNX)
        # We expect image_size = [height, width]
        # Depending on framework, transpose may be needed in preprocessing
        image_size = [input_shape[2], input_shape[3]] if len(input_shape) == 4 else [input_shape[1], input_shape[2]]

        if self.cfg.model.framework == "torch":
            dataset_size = len(self.eval_ds.dataset)
        else:
            dataset_size = sum([x.shape[0] for x, _ in self.eval_ds])

        if self.cfg.model.framework == "torch":
            batch_size = self.eval_ds.batch_size
        else:
            exmpl, _ = iter(self.eval_ds).next()
            batch_size = exmpl.shape[0]

        if self.cfg.model.framework == "torch":
            if ("yolod" in str(getattr(self.cfg.model, "model_name", "") or "").lower()) or ("yolod" in str(getattr(self.cfg.model, "model_type", "") or "").lower()):
                ds = self.eval_ds.dataset
                _, labels, _, _ = ds[0]
                num_labels = int(labels.shape[0])
            if ("ssd" in str(getattr(self.cfg.model, "model_name", "") or "").lower()) or ("ssd" in str(getattr(self.cfg.model, "model_type", "") or "").lower()):
                ds = self.eval_ds.dataset
                _, _, labels = ds[0]
                num_labels = int(labels.shape[0])
        else:
            _, labels = iter(self.eval_ds).next()
            num_labels = int(tf.shape(labels)[1])
        
        cpp = self.cfg.postprocessing
        metrics_data = None
        num_detections = 0

        start_time = timer()

        for i, data in enumerate(tqdm.tqdm(self.eval_ds)):
            if self.cfg.model.framework == "torch":
                if ("yolod" in str(getattr(self.cfg.model, "model_name", "") or "").lower()) or ("yolod" in str(getattr(self.cfg.model, "model_type", "") or "").lower()):
                    images, gt_labels, _, _ = data
                    images_np = images.cpu().numpy()
                    gt_labels = gt_labels.cpu().numpy()
                    # gt_labels shape: (batch, num_labels, 5) [class_id, x_center, y_center, width, height]
                    gt_labels = gt_labels.copy()
                    x_center = gt_labels[..., 1]
                    y_center = gt_labels[..., 2]
                    w        = gt_labels[..., 3]
                    h        = gt_labels[..., 4]

                    x_min = x_center - w / 2.0
                    y_min = y_center - h / 2.0
                    x_max = x_center + w / 2.0
                    y_max = y_center + h / 2.0

                    # keep class id in index 0, replace [1:5] with [x_min, y_min, x_max, y_max]
                    gt_labels = tf.stack([gt_labels[..., 0], x_min, y_min, x_max, y_max],axis=-1).numpy()
                if ("ssd" in str(getattr(self.cfg.model, "model_name", "") or "").lower()) or ("ssd" in str(getattr(self.cfg.model, "model_type", "") or "").lower()):
                    # The DataLoader returns encoded boxes (MatchPrior targets), not raw GT.
                    # Fetching raw GT directly from the dataset using get_annotation().
                    images, _, _ = data  # Ignore encoded boxes/classes from DataLoader
                    images_np = images.cpu().numpy()
                    
                    dataset = self.eval_ds.dataset
                    current_batch_size = images.shape[0]
                    
                    # Detect dataset type (VOC vs COCO)
                    dataset_name = str(getattr(self.cfg.dataset, "dataset_name", "") or "").lower()
                    is_coco = "coco" in dataset_name
                    
                    # Initialize GT labels (class_id, x1, y1, x2, y2) with zeros
                    gt_labels = np.zeros((current_batch_size, num_labels, 5), dtype=np.float32)

                    for b in range(current_batch_size):
                        idx = i * batch_size + b
                        if idx < len(dataset):
                            # Fetch raw annotation
                            if hasattr(dataset, 'get_annotation'):
                                annotation_result = dataset.get_annotation(idx)
                                
                                if is_coco:
                                    # COCO returns: (image_id, (image, boxes, labels))
                                    _, (_, gt_boxes, gt_classes) = annotation_result
                                    is_difficult = np.zeros(len(gt_classes), dtype=np.uint8)  # COCO has no difficult flag
                                else:
                                    # VOC returns: (image_id, (boxes, labels, is_difficult))
                                    _, (gt_boxes, gt_classes, is_difficult) = annotation_result
                                
                                # Filter difficult examples (VOC only)
                                if not is_coco and hasattr(dataset, 'keep_difficult') and not dataset.keep_difficult:
                                    keep_mask = is_difficult == 0
                                    gt_boxes = gt_boxes[keep_mask]
                                    gt_classes = gt_classes[keep_mask]
                                
                                n_objs = min(len(gt_boxes), num_labels)
                                if n_objs > 0:
                                    # Get original image size for scaling
                                    image_id = dataset.ids[idx]
                                    if hasattr(dataset, '_read_image'):
                                        orig_image = dataset._read_image(image_id)
                                        orig_h, orig_w = orig_image.shape[:2]
                                    elif hasattr(dataset, 'get_image'):
                                        orig_image = dataset.get_image(idx)
                                        orig_h, orig_w = orig_image.shape[:2]
                                    else:
                                        # assume GT is already in correct scale
                                        orig_h, orig_w = image_size[0], image_size[1]
                                    
                                    # Classes: 1-based to 0-based (for metrics)
                                    gt_labels[b, :n_objs, 0] = gt_classes[:n_objs] - 1
                                    
                                    # Boxes: Scale from original image size to model input size
                                    scaled_boxes = gt_boxes[:n_objs].astype(np.float32).copy()
                                    scaled_boxes[:, [0, 2]] *= (image_size[1] / orig_w)  # x coords
                                    scaled_boxes[:, [1, 3]] *= (image_size[0] / orig_h)  # y coords
                                    gt_labels[b, :n_objs, 1:] = scaled_boxes
            else:
                images, gt_labels = data
                images_np = images.numpy()

            # Preprocessing: transpose if needed (e.g. channel last to channel first)
            if self.cfg.model.framework == "tf":
                if input_pos == "chfirst" or target == 'host':
                    # The transpose is doing chlast -> chfirst as the host model is onnx channel first
                    images_np = np.transpose(images_np, (0, 3, 1, 2))
            elif self.cfg.model.framework == "torch":
                if input_pos == "chlast" and target != 'host':
                    # The transpose is doing chfirst -> chlast as the model will expect channel last on target
                    images_np = np.transpose(images_np, (0, 2, 3, 1))

            # Run inference
            if model_batch_size != 1:
                if target == 'host':
                    predictions = self.model.run([o.name for o in self.model.get_outputs()], {self.model.get_inputs()[0].name: images_np})
                elif target in ['stedgeai_host', 'stedgeai_n6', 'stedgeai_h7p']:
                    data_quant = ai_interp_input_quant(ai_runner_interpreter, images_np, '.onnx')
                    predictions = ai_runner_invoke(data_quant, ai_runner_interpreter)
                    predictions = ai_interp_outputs_dequant(ai_runner_interpreter, predictions)
                else:
                    raise RuntimeError(f"Unsupported target: {target}")
            else:
                results = []
                for img in images_np:  # img shape: (3, H, W)
                    img = np.expand_dims(img, axis=0)  # Add batch dimension
                    if target == 'host':
                        pred = self.model.run([o.name for o in self.model.get_outputs()], {self.model.get_inputs()[0].name: img})
                    elif target in ['stedgeai_host', 'stedgeai_n6', 'stedgeai_h7p']:
                        data_quant = ai_interp_input_quant(ai_runner_interpreter, img, '.onnx')
                        pred = ai_runner_invoke(data_quant, ai_runner_interpreter)
                        pred = ai_interp_outputs_dequant(ai_runner_interpreter, pred)
                    else:
                        raise RuntimeError(f"Unsupported target: {target}")
                    results.append(pred)
                n_outputs = len(results[0])
                if n_outputs == 1:
                    predictions = [np.concatenate([results[j][0] for j in range(len(results))], axis=0)]
                else:
                    if ("ssd" in str(getattr(self.cfg.model, "model_name", "") or "").lower()) or ("ssd" in str(getattr(self.cfg.model, "model_type", "") or "").lower()):
                    
                        classes_list = [results[j][0] for j in range(len(results))]
                        boxes_list   = [results[j][1] for j in range(len(results))]

                        classes_concat = np.concatenate(classes_list, axis=0)  # (N_imgs, 3000, 21)
                        boxes_concat   = np.concatenate(boxes_list,   axis=0)  # (N_imgs, 3000, 4)

                        predictions = [classes_concat, boxes_concat]
                    else:
                        raise RuntimeError("ONNX evaluator currently supports only SSD models with multiple outputs.") 

            # Here we consider that the post processing is always expecting chlast data
            # If the user declares that output will be chfirst, a transpose of the output is needed else
            # the compiler will have added a transpose in the onnx model
            if self.cfg.model.framework == "tf":
                if output_pos == "chfirst" or target == 'host':
                    for idx in range(len(predictions)):
                        if len(predictions[idx].shape) == 3:
                            predictions[idx] = tf.transpose(predictions[idx], perm=[0, 2, 1]).numpy()
                        elif len(predictions[idx].shape) == 4:
                            predictions[idx] = tf.transpose(predictions[idx], perm=[0, 2, 3, 1]).numpy()

            if len(predictions) == 1:
                predictions = predictions[0]

            # Decode the predictions
            # Pierre: without the following transpose I was not able to evaluate channel first onnx model 
            # to be validated by the corresponding user story assignee 
            #predictions = [np.transpose(e, [0, 2, 3, 1]) for e in predictions] # pde proposal
            boxes, scores = get_detections(self.cfg, predictions, image_size)

            n_classes = len(self.class_names)
            
            if i == 0:
                num_detections = boxes.shape[1]
                metrics_data = ObjectDetectionMetricsData(
                    num_labels, cpp.max_detection_boxes, n_classes,
                    num_detections, dataset_size, batch_size
                )
            metrics_data.add_data(gt_labels, boxes, scores)
            metrics_data.update_batch_index(i, cpp.confidence_thresh, cpp.NMS_thresh, image_size)

        end_time = timer()
        eval_run_time = int(end_time - start_time)
        print("Evaluation run time: " + str(timedelta(seconds=eval_run_time)))

        groundtruths, detections = metrics_data.get_data()
        metrics = calculate_objdet_metrics(groundtruths, detections, cpp.IoU_eval_thresh)

        self._display_objdet_metrics(metrics, self.class_names)

        log_to_file(self.output_dir, f"ONNX object detection model dataset used: {self.cfg.dataset.dataset_name}")

        mpre, mrec, mAP = calculate_average_metrics(metrics)
        model_type = "quantized" if model_is_quantized(model_path) else "float"
        log_to_file(self.output_dir, "{}_model_mpre: {:.1f}".format(model_type, 100 * mpre))
        log_to_file(self.output_dir, "{}_model_mrec: {:.1f}".format(model_type, 100 * mrec))
        log_to_file(self.output_dir, "{}_model_map: {:.1f}".format(model_type, 100 * mAP))
        
        # Log metrics in mlflow
        mlflow.log_metric(f"{model_type}_model_mpre", round(100 * mpre, 2))
        mlflow.log_metric(f"{model_type}_model_mrec", round(100 * mrec, 2))
        mlflow.log_metric(f"{model_type}_model_mAP", round(100 * mAP, 2))
        
        if self.cfg.postprocessing.plot_metrics:
            print("\nPlotting precision versus recall curves")
            plots_dir = os.path.join(self.output_dir, "precision_vs_recall_curves", os.path.basename(getattr(self.model, "model_path", "onnx_model")))
            print("Plots directory:", plots_dir)
            self._plot_precision_versus_recall(metrics, self.class_names, plots_dir)

        print('[INFO] : Evaluation complete.')
        return metrics

    def evaluate(self):
        """
        Executes the full evaluation process.

        Returns:
            dict: Dictionary of evaluation metrics for each class.
        """
        self._prepare_evaluation()
        return self._run_evaluate()