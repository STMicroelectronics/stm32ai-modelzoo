# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import warnings
import numpy as np
import tqdm
import mlflow
import tensorflow as tf
import matplotlib.pyplot as plt
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from timeit import default_timer as timer
from datetime import timedelta
from tabulate import tabulate
from pathlib import Path

from object_detection.tf.src.postprocessing import get_detections
from object_detection.tf.src.utils import ObjectDetectionMetricsData, calculate_objdet_metrics, calculate_average_metrics
from common.utils import log_to_file, count_h5_parameters


class KerasModelEvaluator:
    """
    A class to evaluate Keras object detection models.

    Args:
        cfg (DictConfig): Configuration object for evaluation.
        model (tf.keras.Model): The Keras model to evaluate.
        dataloaders (dict): Dictionary containing datasets for testing and validation.
    """
    def __init__(self, cfg: DictConfig, model: tf.keras.Model,
                 dataloaders: dict = None):
        self.cfg = cfg
        self.model = model
        self.test_ds = dataloaders['test']
        self.valid_ds = dataloaders['valid']
        self.output_dir = HydraConfig.get().runtime.output_dir
        self.class_names = cfg.dataset.class_names
        self.display_figures = cfg.general.display_figures
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
        # Count the number of parameters in the model and log them
        count_h5_parameters(output_dir=self.output_dir,
                            model=self.model)
        tf.print(f'[INFO] : Evaluating the Keras object detection model using {self.name_ds}...')
        input_shape = self.model.input_shape[1:] #self.model.input.shape[1:3]
        dataset_size = sum([x.shape[0] for x, _ in self.eval_ds])

        exmpl, _ = iter(self.eval_ds).next()
        batch_size = exmpl.shape[0]

        _, labels = iter(self.eval_ds).next()
        num_labels = int(tf.shape(labels)[1])

        cpp = self.cfg.postprocessing
        metrics_data = None
        num_detections = 0

        start_time = timer()

        for i, data in enumerate(tqdm.tqdm(self.eval_ds)):
            images, gt_labels = data
            image_size = tf.shape(images)[1:3]

            predictions = self.model(images)

            boxes, scores = get_detections(self.cfg, predictions, image_size)

            if i == 0:
                num_detections = boxes.shape[1]
                metrics_data = ObjectDetectionMetricsData(
                    num_labels, cpp.max_detection_boxes, len(self.class_names),
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

        log_to_file(self.output_dir, f"Keras object detection model dataset used: {self.cfg.dataset.dataset_name}")

        mpre, mrec, mAP = calculate_average_metrics(metrics)
        model_type = "float"
        log_to_file(self.output_dir, "{}_model_mpre: {:.1f}".format(model_type, 100 * mpre))
        log_to_file(self.output_dir, "{}_model_mrec: {:.1f}".format(model_type, 100 * mrec))
        log_to_file(self.output_dir, "{}_model_map: {:.1f}".format(model_type, 100 * mAP))
        
        # Log metrics in mlflow
        mlflow.log_metric(f"{model_type}_model_mpre", round(100 * mpre, 2))
        mlflow.log_metric(f"{model_type}_model_mrec", round(100 * mrec, 2))
        mlflow.log_metric(f"{model_type}_model_mAP", round(100 * mAP, 2))

        if self.cfg.postprocessing.plot_metrics:
            print("\nPlotting precision versus recall curves")
            plots_dir = os.path.join(self.output_dir, "precision_vs_recall_curves", os.path.basename(getattr(self.model, "model_path", "keras_model")))
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
















