# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
    
import tensorflow as tf

from object_detection.tf.src.utils import bbox_normalized_to_abs_coords, \
         ObjectDetectionMetricsData, bbox_abs_to_normalized_coords
from object_detection.tf.src.data_augmentation import data_augmentation
from object_detection.tf.src.postprocessing import decode_ssd_predictions, nms_box_filtering
from .ssd_anchor_matching import match_gt_anchors
from .ssd_loss import ssd_focal_loss



class SSDTrainingModel(tf.keras.Model):

    def __init__(self,
            model,
            num_classes=None,
            num_anchors=None,
            num_labels=None,
            num_detections=None,
            val_dataset_size=None,
            batch_size=None,
            anchor_boxes=None,
            data_augmentation_cfg=None,
            pixels_range=None,
            image_size=None,
            pos_iou_threshold=None,
            neg_iou_threshold=None,
            max_detection_boxes=None,
            nms_score_threshold=None,
            nms_iou_threshold=None,
            metrics_iou_threshold=None):
            
        super(SSDTrainingModel, self).__init__()
                               
        self.model = model
        self.num_classes = num_classes
        self.num_anchors = num_anchors
        self.num_labels = num_labels
        self.num_detections = num_detections
        self.anchor_boxes = anchor_boxes
        self.data_augmentation_cfg = data_augmentation_cfg
        self.pixels_range = pixels_range
        self.image_size = image_size
        self.pos_iou_threshold = pos_iou_threshold
        self.neg_iou_threshold = neg_iou_threshold
        self.nms_score_threshold = nms_score_threshold
        self.nms_iou_threshold = nms_iou_threshold
        self.metrics_iou_threshold = metrics_iou_threshold
        self.max_detection_boxes = max_detection_boxes

        self.loss_tracker = tf.keras.metrics.Mean(name="loss")
        self.val_loss_tracker = tf.keras.metrics.Mean(name="val_loss")
        
        self.metrics_data = ObjectDetectionMetricsData(
                num_labels, max_detection_boxes, num_classes, num_detections, val_dataset_size, batch_size, name="metrics_data")


    def get_metrics_data(self):
        return self.metrics_data.get_data()
        
    def reset_metrics_data(self):
        self.metrics_data.reset()

    def set_tmp_metrics_data(self, batch):
        self.metrics_data.update_batch_index(batch,self.nms_score_threshold,self.nms_iou_threshold,self.image_size)

    def save_weights(self, filepath, overwrite=True, save_format=None, options=None):
        self.model.save_weights(
            filepath, overwrite=overwrite)

    def load_weights(self, filepath, skip_mismatch=False, by_name=False, options=None):
        return self.model.load_weights(
            filepath, skip_mismatch=skip_mismatch, by_name=by_name, options=options)

    def train_step(self, data):
        # The data loader supplies groundtruth boxes in
        # normalized corners coordinates (x1, y1, x2, y2).
        images, gt_labels = data
        image_size = tf.shape(images)[1:3]

        if self.data_augmentation_cfg is not None:            
            # The data augmentation function takes absolute (x1, y1, x2, y2) coordinates.
            classes = gt_labels[..., 0:1]
            boxes = bbox_normalized_to_abs_coords(gt_labels[..., 1:], image_size=image_size)
            gt_labels = tf.concat([classes, boxes], axis=-1)

            images, gt_labels_aug = data_augmentation(images, gt_labels, self.data_augmentation_cfg, self.pixels_range)
                
            # Normalize the augmented boxes
            boxes_aug = bbox_abs_to_normalized_coords(gt_labels_aug[..., 1:], image_size=image_size)
            gt_labels = tf.concat([classes, boxes_aug], axis=-1)

        y_true = match_gt_anchors(
                            self.anchor_boxes,
                            gt_labels,
                            num_classes=self.num_classes,
                            num_anchors=self.num_anchors,
                            num_labels=self.num_labels,
                            pos_iou_threshold=self.pos_iou_threshold,
                            neg_iou_threshold=self.neg_iou_threshold)
            
        with tf.GradientTape() as tape:
            y_pred = self.model(images, training=True)
            loss = ssd_focal_loss(y_true, y_pred)

        # Compute gradients and update weights
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(loss, trainable_vars)
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
        
        # Update the loss tracker
        self.loss_tracker.update_state(loss)

        return {'loss': self.loss_tracker.result()}


    def test_step(self, data):
        # The data loader supplies groundtruth boxes in
        # normalized corner coordinates (x1, y1, x2, y2).    
        images, gt_labels = data
        image_size = tf.shape(images)[1:3]
        
        y_true = match_gt_anchors(
                            self.anchor_boxes,
                            gt_labels,
                            num_classes=self.num_classes,
                            num_anchors=self.num_anchors,
                            num_labels=self.num_labels,
                            pos_iou_threshold=self.pos_iou_threshold,
                            neg_iou_threshold=self.neg_iou_threshold)

        y_pred = self.model(images, training=False)

        val_loss = ssd_focal_loss(y_true, y_pred)
        
        # The model output tensor includes detection scores, boxes and anchor offsets.
        predictions = (y_pred[..., :-8], y_pred[..., -8:-4], y_pred[..., -4:])

        # Decode the predictions
        boxes, scores = decode_ssd_predictions(predictions)

        # Update the metrics trackers
        self.val_loss_tracker.update_state(val_loss)
        
        # Add the batch to the metrics data
        gt_boxes = bbox_normalized_to_abs_coords(gt_labels[..., 1:], image_size=image_size)
        gt_labels = tf.concat([gt_labels[..., 0:1], gt_boxes], axis=-1)        
        self.metrics_data.add_data(gt_labels, boxes, scores)
        
        return {'loss': self.val_loss_tracker.result()}

    # List trackers here to avoid the need for calling reset_state()
    @property
    def metrics(self):
        return [self.loss_tracker, self.val_loss_tracker]
