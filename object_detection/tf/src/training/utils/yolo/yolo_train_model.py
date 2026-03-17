# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf

from object_detection.tf.src.utils import bbox_normalized_to_abs_coords, \
         ObjectDetectionMetricsData, bbox_corners_to_center_coords
from .yolo_loss import yolo_loss, get_detector_mask
from object_detection.tf.src.utils import bbox_abs_to_normalized_coords, change_model_input_shape
from object_detection.tf.src.data_augmentation import data_augmentation
from object_detection.tf.src.postprocessing import decode_yolo_predictions, nms_box_filtering

            
class YoloTrainingModel(tf.keras.Model):

    def __init__(self,
            model,
            network_stride=None,
            num_classes=None,
            num_labels=None,
            anchors=None,
            data_augmentation_cfg=None,
            val_dataset_size=None,
            batch_size=None,
            pixels_range=None,
            image_size=None,
            max_detection_boxes=None,
            nms_score_threshold=None,
            nms_iou_threshold=None,
            metrics_iou_threshold=None):

        super(YoloTrainingModel, self).__init__()

        self.model,_ = change_model_input_shape(model,(None,None,None,3))

        self.network_stride = network_stride
        self.num_classes = num_classes
        self.image_size = image_size
        self.anchors = anchors
        self.num_detections = int(len(anchors)*(image_size[0]*image_size[1]/network_stride**2))
        self.data_augmentation_cfg = data_augmentation_cfg
        self.pixels_range = pixels_range
        self.max_detection_boxes = max_detection_boxes
        self.nms_score_threshold = nms_score_threshold
        self.nms_iou_threshold = nms_iou_threshold
        self.metrics_iou_threshold = metrics_iou_threshold
        
        self.batch_info = tf.Variable([0, image_size[0], image_size[1]], trainable=False, dtype=tf.int64)

        self.loss_tracker = tf.keras.metrics.Mean(name="loss")
        self.val_loss_tracker = tf.keras.metrics.Mean(name="val_loss")
        
        self.metrics_data = ObjectDetectionMetricsData(
                num_labels, max_detection_boxes, num_classes, self.num_detections, val_dataset_size, batch_size, name="metrics_data")


    def get_metrics_data(self):
        return self.metrics_data.get_data()
        
    def reset_metrics_data(self):
        self.metrics_data.reset()

    def set_tmp_metrics_data(self, batch):
        self.metrics_data.update_batch_index(batch,self.nms_score_threshold,self.nms_iou_threshold,self.image_size)

    def set_resolution(self, res):
        self.batch_info.assign([0,res[0],res[1]])

    def save_weights(self, filepath, overwrite=True, save_format=None, options=None):
        self.model.save_weights(
            filepath, overwrite=overwrite) #, save_format=save_format, options=options)

    def load_weights(self, filepath, skip_mismatch=False, by_name=False, options=None):
        return self.model.load_weights(
            filepath, skip_mismatch=skip_mismatch, by_name=by_name, options=options)

    def train_step(self, data):
        # GT boxes coords are normalized (x1, y1, x2, y2).
        images, gt_labels = data
        image_size = tf.shape(images)[1:3]

        if self.data_augmentation_cfg is not None:
            current_image_size = tf.cast([self.batch_info[1],self.batch_info[2]],tf.int32)
            # The data augmentation function takes absolute (x1, y1, x2, y2) coordinates.
            classes = gt_labels[..., 0:1]
            boxes = bbox_normalized_to_abs_coords(gt_labels[..., 1:], image_size=image_size)
            gt_labels = tf.concat([classes, boxes], axis=-1)
                            
            images, gt_labels_aug = data_augmentation(
                        images,
                        gt_labels,
                        config=self.data_augmentation_cfg,
                        pixels_range=self.pixels_range,
                        batch_info=self.batch_info)

            # Normalize the augmented boxes
            boxes_aug = bbox_abs_to_normalized_coords(gt_labels_aug[..., 1:], image_size=current_image_size)
            gt_labels = tf.concat([classes, boxes_aug], axis=-1)
        else:
            current_image_size = image_size
        
        # Convert GT boxes coordinates to (x, y, w, h)
        # GT classes are last in the Darknet labels format.
        gt_boxes = bbox_corners_to_center_coords(gt_labels[..., 1:], abs_corners=False)
        gt_labels_loss = tf.concat([gt_boxes, gt_labels[..., 0:1]], axis=-1)
        
        detectors_mask, matching_true_boxes = get_detector_mask(
                gt_labels_loss, self.anchors, image_size=current_image_size,
                network_stride=self.network_stride)

        with tf.GradientTape() as tape:
            predictions = self.model(images, training=True)
            loss = yolo_loss(self.anchors,
                             self.num_classes, 
                             predictions,
                             gt_labels_loss,
                             detectors_mask,
                             matching_true_boxes,
                             current_image_size)
                             
        # Compute gradients and update weights
        trainable_vars = self.trainable_variables
        gradients = tape.gradient(loss, trainable_vars)
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
        
        # # Update the loss tracker
        self.loss_tracker.update_state(loss)

        return {'loss': self.loss_tracker.result()}


    def test_step(self, data):        
        images, gt_labels = data
        image_size = tf.shape(images)[1:3]
                
        # Convert GT boxes coordinates to (x, y, w, h)
        # GT classes are last in the Darknet labels format.
        gt_boxes = bbox_corners_to_center_coords(gt_labels[..., 1:], abs_corners=False)
        gt_labels_loss = tf.concat([gt_boxes, gt_labels[..., 0:1]], axis=-1)
        
        predictions = self.model(images)
        
        # Calculate the loss
        detectors_mask, matching_true_boxes = get_detector_mask(
                            gt_labels_loss, self.anchors, image_size=image_size,
                            network_stride=self.network_stride)
        val_loss = yolo_loss(self.anchors,
                             self.num_classes, 
                             predictions,
                             gt_labels_loss,
                             detectors_mask,
                             matching_true_boxes,
                             image_size)

        # Decode the predictions
        boxes, scores = decode_yolo_predictions(predictions, self.num_classes, self.anchors, image_size)

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

        