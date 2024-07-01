#!/usr/bin/python3
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

from stai_mpu import stai_mpu_network
import numpy as np
from timeit import default_timer as timer
import math

class NeuralNetwork:
    """
    Class that handles Neural Network inference
    """

    def __init__(self, model_file, label_file, input_mean, input_std, confidence_thresh, iou_threshold):
        """
        :param model_file: model to be executed
        :param label_file: name of file containing labels
        :param input_mean: input_mean
        :param input_std: input standard deviation
        :confidence_thresh: confidence threshold used to filter NN results
        :iou_threshold: intersection over union threshold used to filter NN results
        """


        def load_labels(filename):
            """
            :return: list of labels extracted from label file
            """
            my_labels = []
            input_file = open(filename, 'r')
            for l in input_file:
                my_labels.append(l.strip())
            return my_labels

        self._model_file = model_file
        print("NN model used : ", self._model_file)
        if "mobilenet_v1" in self._model_file :
            self.model_type = "ssd_mobilenet_v1"
        elif "mobilenet_v2" in self._model_file :
            self.model_type = "ssd_mobilenet_v2"
        self._label_file = label_file
        self._input_mean = input_mean
        self._input_std = input_std
        self.confidence_threshold = confidence_thresh
        self.iou_threshold  = iou_threshold
        self.number_of_boxes = 0

        # Initialize NN model
        self.stai_mpu_model = stai_mpu_network(model_path=self._model_file)

        # Read input tensor information
        self.num_inputs = self.stai_mpu_model.get_num_inputs()
        self.input_tensor_infos = self.stai_mpu_model.get_input_infos()

        # Read output tensor information
        self.num_outputs = self.stai_mpu_model.get_num_outputs()
        self.output_tensor_infos = self.stai_mpu_model.get_output_infos()

        # Load labels
        self._labels = load_labels(self._label_file)

    def get_labels(self):
        """
        :return: list of NN model labels loaded
        """
        return self._labels

    def get_img_size(self):
        """
        :return: size of NN input image size
        """
        input_tensor_shape = self.input_tensor_infos[0].get_shape()
        print("input_tensor_shape",input_tensor_shape)
        input_width = input_tensor_shape[1]
        input_height = input_tensor_shape[2]
        input_channel = input_tensor_shape[3]
        return (input_width, input_height, input_channel)

    def launch_inference(self, img):
        """
        This method launches inference using the invoke call
        :param img: the image to be inferred
        """
        # add N dim
        input_data = np.expand_dims(img, axis=0)

        # preprocess input data if necessary
        if self.input_tensor_infos[0].get_dtype() == np.float32:
            input_data = (np.float32(input_data) - self._input_mean) / self._input_std

        # set NN model input with input data
        self.stai_mpu_model.set_input(0, input_data)
        start = timer()
        # run inference
        self.stai_mpu_model.run()
        end = timer()
        # return the inference time
        inference_time = end - start
        return inference_time

    def get_results(self):
        """
        Get the raw outputs of the NN models and apply postprocessing
        """
        if self.model_type == "ssd_mobilenet_v2":
            anchors = self.stai_mpu_model.get_output(index=2)
            encoded_boxes = self.stai_mpu_model.get_output(index=1)
            class_prediction = self.stai_mpu_model.get_output(index=0)
            locations, classes, scores = self.postprocess_predictions(class_prediction,encoded_boxes,anchors, nms_thresh=self.iou_threshold, confidence_thresh=self.confidence_threshold)
        elif self.model_type == "ssd_mobilenet_v1":
            locations = self.stai_mpu_model.get_output(index=0)
            classes = self.stai_mpu_model.get_output(index=1)
            scores = self.stai_mpu_model.get_output(index=2)

        #Get backend used
        self.stai_backend = self.stai_mpu_model.get_backend_engine()
        return locations, classes, scores

    def non_max_supression(self,decoded_boxes,scores,classes, iou_threshold):
        """
        Filter overlapping bounding boxes to keep only relevant boxes.
        """
        if len(decoded_boxes) == 0:
            return np.array([]),np.array([]),np.array([])

        bb_keeped_idexes = []
        x1 = decoded_boxes[:,0]
        y1 = decoded_boxes[:,1]
        x2 = decoded_boxes[:,2]
        y2 = decoded_boxes[:,3]
        bb_area = (x2 - x1) * (y2 - y1)
        sorted_scores = np.argsort(scores)[::-1]
        while len(sorted_scores) > 0:
            i = sorted_scores[0]
            bb_keeped_idexes.append(i)

            xmax = np.maximum(x1[i], x1[sorted_scores[1:]])
            ymax = np.maximum(y1[i], y1[sorted_scores[1:]])
            xmin = np.minimum(x2[i], x2[sorted_scores[1:]])
            ymin = np.minimum(y2[i], y2[sorted_scores[1:]])

            w, h = np.maximum(0, xmin - xmax), np.maximum(0, ymin - ymax)
            overlap_area = w * h
            overlap = overlap_area / (bb_area[i] + bb_area[sorted_scores[1:]] - overlap_area)
            inds = np.where(overlap <= iou_threshold)[0]
            sorted_scores = sorted_scores[inds + 1]
        if bb_keeped_idexes :
            return decoded_boxes[bb_keeped_idexes], scores[bb_keeped_idexes], classes[bb_keeped_idexes]
        else:
            return np.array([]),np.array([]),np.array([])

    def decode_predictions(self, encoded_bbox, anchors):
        """
        Function used to decode raw NN output using associated anchors.
        Returns a list of decoded outputs.
        """
        decoded_boxes = []
        num_boxes = len(encoded_bbox)

        for i in range(num_boxes):
            a_xmin =  anchors[i][0]
            a_ymin =  anchors[i][1]
            a_xmax =  anchors[i][2]
            a_ymax =  anchors[i][3]

            bb_xmin = encoded_bbox[i][0]
            bb_ymin = encoded_bbox[i][1]
            bb_xmax = encoded_bbox[i][2]
            bb_ymax = encoded_bbox[i][3]

            w = a_xmax - a_xmin
            h = a_ymax - a_ymin

            decoded_xmin = bb_xmin * w + a_xmin
            decoded_ymin = bb_ymin * h + a_ymin
            decoded_xmax = bb_xmax * w + a_xmax
            decoded_ymax = bb_ymax * h + a_ymax

            decoded_boxes.append((decoded_xmin,decoded_ymin,decoded_xmax,decoded_ymax))
        decoded_boxes = np.array(decoded_boxes)
        return decoded_boxes

    def postprocess_predictions(self,
                                predicted_scores,
                                predicted_boxes,
                                predicted_anchors,
                                nms_thresh: float = 0.45,
                                confidence_thresh: float = 0.70):
        """
        Postprocesses the predictions to filter out weak and overlapping bounding boxes.
        """

        #Filter bounding boxes by the confidence threshold
        predicted_scores = predicted_scores[0]
        predicted_boxes = predicted_boxes[0]
        predicted_anchors = predicted_anchors[0]

        filtered_classes_indexes = np.where(np.any(predicted_scores[:,1:81] > confidence_thresh, axis=1))[0]

        filtered_prediction = predicted_boxes[filtered_classes_indexes]
        filtered_anchors = predicted_anchors[filtered_classes_indexes]

        #Extract Score and Classes
        class_prediction = predicted_scores[filtered_classes_indexes]
        filtered_score = np.max(class_prediction, axis=1)
        filtered_class = np.argmax(class_prediction, axis=1)

        #Decode raw predictions outputs
        decoded_bb = self.decode_predictions(filtered_prediction,filtered_anchors)

        #Remove overlapping bounding boxes
        locations, scores, classes = self.non_max_supression(decoded_bb,np.array(filtered_score),np.array(filtered_class),nms_thresh)

        if len(locations) > 0:
            locations = np.expand_dims(locations, axis=0)
            scores = np.expand_dims(scores, axis=0)
            classes = np.expand_dims(classes, axis=0)
            return np.array(locations), classes, scores
        else:
            return np.array([]),np.array([]),np.array([])

    def get_label(self, idx, classes):
        """
        Get the label name based on the idex of the class
        """
        labels = self.get_labels()
        return labels[int(classes[0][idx])]