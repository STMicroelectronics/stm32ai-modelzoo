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
import shutil
import tensorflow as tf
import matplotlib.pyplot as plt
from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from timeit import default_timer as timer
from datetime import timedelta
from tabulate import tabulate
from pathlib import Path

from object_detection.tf.src.postprocessing import get_detections
from object_detection.tf.src.models import model_family
from object_detection.tf.src.utils import ai_runner_invoke
from object_detection.tf.src.utils import ObjectDetectionMetricsData, calculate_objdet_metrics, calculate_average_metrics
from common.utils import (
    ai_runner_interp, ai_interp_input_quant, ai_interp_outputs_dequant, log_to_file, display_figures
)  # Common utilities for evaluation and visualization


class TFLiteQuantizedModelEvaluator:
    """
    A class to evaluate TensorFlow Lite (TFLite) quantized object detection models.

    Args:
        cfg (DictConfig): Configuration object for evaluation.
        model (object): The quantized TFLite Interpreter object.
        dataloaders (dict): Dictionary containing datasets for testing and validation.
    """
    def __init__(self, cfg: DictConfig, model: object,
                 dataloaders: dict = None):
        self.cfg = cfg
        self.quantized_model = model
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
        # Use the test dataset if available; otherwise, use the validation dataset
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
        name_model = os.path.basename(self.quantized_model.model_path)
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

        # Create the directory where plots will be saved
        if os.path.exists(plots_dir):
            shutil.rmtree(plots_dir)
        os.makedirs(plots_dir)

        for c in list(metrics.keys()):
            
            # Plot the precision versus recall curve
            figure = plt.figure(figsize=(10, 10))
            plt.xlabel("recall")
            plt.ylabel("interpolated precision")
            plt.title("Class '{}' (AP = {:.2f})".
                        format(class_names[c], metrics[c].ap * 100))
            plt.plot(metrics[c].interpolated_precision, metrics[c].interpolated_recall)
            plt.grid()

            # Save the plot in the plots directory
            plt.savefig(f"{plots_dir}/{class_names[c]}.png")
            plt.close(figure)

    def _run_evaluate(self):
        """
        Runs the evaluation process and computes metrics.

        Returns:
            float: Accuracy of the quantized model on the evaluation dataset.
        """
        tf.print(f'[INFO] : Evaluating the quantized object detection model using {self.name_ds}...')
        target = self._get_target()
        ai_runner_interpreter = self._get_interpreter(target=target)
        input_details = self.quantized_model.get_input_details()[0]
        output_details = self.quantized_model.get_output_details()
        model_batch_size = input_details['shape_signature'][0]
        if model_batch_size != 1 and target == 'host':
            batch_size = 64
        else:
            batch_size = 1

        input_shape = tuple(input_details['shape'][1:])
        image_size = input_shape[:2]
        dataset_size = sum([x.shape[0] for x, _ in self.eval_ds])

        exmpl, _ = iter(self.eval_ds).next()
        batch_size = exmpl.shape[0]

        _, labels = iter(self.eval_ds).next()
        num_labels = int(tf.shape(labels)[1])

        cpp = self.cfg.postprocessing
        metrics_data = None
        num_detections = 0
        predictions_all = []
        images_full = []

        start_time = timer()

        for i, data in enumerate(tqdm.tqdm(self.eval_ds)):
            images, gt_labels = data
            batch_size = int(tf.shape(images)[0])

            input_index = input_details['index']
            tensor_shape = (batch_size,) + input_shape
            self.quantized_model.resize_tensor_input(input_index, tensor_shape)
            self.quantized_model.allocate_tensors()

            scale, zero_point = input_details['quantization']
            images_quant = images / scale + zero_point
            input_dtype = input_details['dtype']
            images_quant = tf.cast(images_quant, input_dtype)
            images_quant = tf.clip_by_value(images_quant, np.iinfo(input_dtype).min, np.iinfo(input_dtype).max)
            
            if "evaluation" in self.cfg and self.cfg.evaluation:
                if "gen_npy_input" in self.cfg.evaluation and self.cfg.evaluation.gen_npy_input==True: 
                    images_full.append(images)

            if target == 'host':
                self.quantized_model.set_tensor(input_index, images_quant)
                self.quantized_model.invoke()
            elif target in ['stedgeai_host', 'stedgeai_n6', 'stedgeai_h7p']:
                data_quant = ai_interp_input_quant(ai_runner_interpreter, images.numpy(), '.tflite')
                predictions = ai_runner_invoke(data_quant, ai_runner_interpreter)
                predictions = ai_interp_outputs_dequant(ai_runner_interpreter, predictions)
            else:
                raise RuntimeError(f"Unsupported target: {target}")
            
            if model_family(self.cfg.model.model_type) in ["ssd", "st_yoloxn"]:
                if target == 'host':
                    # Model outputs are scores, boxes and anchors.
                    predictions = (self.quantized_model.get_tensor(output_details[0]['index']),
                                   self.quantized_model.get_tensor(output_details[1]['index']),
                                   self.quantized_model.get_tensor(output_details[2]['index']))
            else:
                if target == 'host':
                    predictions = self.quantized_model.get_tensor(output_details[0]['index'])
                elif target in ['stedgeai_host', 'stedgeai_n6', 'stedgeai_h7p']:
                    predictions = predictions[0]
                    
            if "evaluation" in self.cfg and self.cfg.evaluation:
                if "gen_npy_output" in self.cfg.evaluation and self.cfg.evaluation.gen_npy_output==True:
                    predictions_all.append(predictions)

            # The TFLITE version of yolov8 has channel-first outputs
            if model_family(self.cfg.model.model_type) in ["yolov8n"]:
                predictions = tf.transpose(predictions, perm=[0, 2, 1])

            boxes, scores = get_detections(self.cfg, predictions, image_size)

            if i == 0:
                num_detections = boxes.shape[1]
                metrics_data = ObjectDetectionMetricsData(
                    num_labels, cpp.max_detection_boxes, len(self.class_names),
                    num_detections, dataset_size, batch_size
                )

            metrics_data.add_data(gt_labels, boxes, scores)
            metrics_data.update_batch_index(i, cpp.confidence_thresh, cpp.NMS_thresh, image_size)
        
        # Saves evaluation dataset in a .npy
        if "evaluation" in self.cfg and self.cfg.evaluation:
            if "gen_npy_input" in self.cfg.evaluation and self.cfg.evaluation.gen_npy_input==True: 
                if "npy_in_name" in self.cfg.evaluation and self.cfg.evaluation.npy_in_name:
                    npy_in_name = self.cfg.evaluation.npy_in_name
                else:
                    npy_in_name = "unknown_npy_in_name"
                images_full = np.concatenate(images_full, axis=0)
                np.save(os.path.join(self.output_dir, f"{npy_in_name}.npy"), images_full)

        # Saves model output in a .npy
        if "evaluation" in self.cfg and self.cfg.evaluation:
            if "gen_npy_output" in self.cfg.evaluation and self.cfg.evaluation.gen_npy_output==True: 
                if "npy_out_name" in self.cfg.evaluation and self.cfg.evaluation.npy_out_name:
                    npy_out_name = self.cfg.evaluation.npy_out_name
                else:
                    npy_out_name = "unknown_npy_out_name"
                predictions_all = np.concatenate(predictions_all, axis=0)
                np.save(os.path.join(self.output_dir, f"{npy_out_name}.npy"), predictions_all)

        end_time = timer()
        eval_run_time = int(end_time - start_time)
        print("Evaluation run time: " + str(timedelta(seconds=eval_run_time)))

        groundtruths, detections = metrics_data.get_data()
        metrics = calculate_objdet_metrics(groundtruths, detections, cpp.IoU_eval_thresh)

        self._display_objdet_metrics(metrics, self.class_names)

        log_to_file(self.output_dir, f"Quantized TFLite object detection model dataset used: {self.cfg.dataset.dataset_name}")

        mpre, mrec, mAP = calculate_average_metrics(metrics)
        model_type = "quantized"
        log_to_file(self.output_dir, "{}_model_mpre: {:.1f}".format(model_type, 100 * mpre))
        log_to_file(self.output_dir, "{}_model_mrec: {:.1f}".format(model_type, 100 * mrec))
        log_to_file(self.output_dir, "{}_model_map: {:.1f}".format(model_type, 100 * mAP))
        
        # Log metrics in mlflow
        mlflow.log_metric(f"{model_type}_model_mpre", round(100 * mpre, 2))
        mlflow.log_metric(f"{model_type}_model_mrec", round(100 * mrec, 2))
        mlflow.log_metric(f"{model_type}_model_mAP", round(100 * mAP, 2))
        
        if self.cfg.postprocessing.plot_metrics:
            print("\nPlotting precision versus recall curves")
            plots_dir = os.path.join(self.output_dir, "precision_vs_recall_curves", os.path.basename(self.quantized_model.model_path))
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
        self._prepare_evaluation()      # Prepare the evaluation process
        return self._run_evaluate()
