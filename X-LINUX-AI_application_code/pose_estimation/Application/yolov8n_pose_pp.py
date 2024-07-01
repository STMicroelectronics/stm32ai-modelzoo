#!/usr/bin/python3
#
# Copyright (c) 2024 STMicroelectronics.
# All rights reserved.
#
# This software is licensed under terms that can be found in the LICENSE file
# in the root directory of this software component.
# If no LICENSE file comes with this software, it is provided AS-IS.

from stai_mpu import stai_mpu_network
from timeit import default_timer as timer
import numpy as np
class NeuralNetwork:
    """
    Class that handles Neural Network inference
    """
    def __init__(self, model_file, input_mean, input_std, conf_threshold, iou_threshold, normalize):
        """
        :param model_path:  model to be executed
        :param input_mean: input_mean
        :param input_std: input standard deviation
        """
        self._model_file = model_file
        print("NN model used : ", self._model_file)
        self._input_mean = input_mean
        self._input_std = input_std
        self._floating_model = False
        self._conf_threshold = conf_threshold
        self._iou_threshold = iou_threshold
        self._normalize = normalize

        # Initialize NN model
        self.stai_mpu_model = stai_mpu_network(model_path=self._model_file)

        # Read input tensor information
        self.num_inputs = self.stai_mpu_model.get_num_inputs()
        self.input_tensor_infos = self.stai_mpu_model.get_input_infos()

        # Read output tensor information
        self.num_outputs = self.stai_mpu_model.get_num_outputs()
        self.output_tensor_infos = self.stai_mpu_model.get_output_infos()

    def get_img_size(self):
        """
        :return: size of NN input image size
        """
        # NxHxWxC, H:1, W:2, C:3
        input_tensor_shape = self.input_tensor_infos[0].get_shape()
        input_width =  input_tensor_shape[1]
        input_height =  input_tensor_shape[2]
        input_channel =  input_tensor_shape[0]
        return (input_width,input_height,input_channel)

    def extract_keypoints(self, keypoints):
        """
        Extracting relevant keypoints
        """
        sub_kpts =[]
        for i in range(0, len(keypoints), 3):
            # Slice out three elements to create a sublist
            sublist = keypoints[i:i+3]
            sub_kpts.append(sublist)
        return sub_kpts

    def intersection(self, rect1, rect2):
        """
        This method return the intersection of two rectangles
        """
        rect1_x1,rect1_y1,rect1_x2,rect1_y2 = rect1[:4]
        rect2_x1,rect2_y1,rect2_x2,rect2_y2 = rect2[:4]
        x1 = max(rect1_x1,rect2_x1)
        y1 = max(rect1_y1,rect2_y1)
        x2 = min(rect1_x2,rect2_x2)
        y2 = min(rect1_y2,rect2_y2)
        return (x2-x1)*(y2-y1)

    def union(self, rect1,rect2):
        """
        This method return the union of two rectangles
        """
        rect1_x1,rect1_y1,rect1_x2,rect1_y2 = rect1[:4]
        rect2_x1,rect2_y1,rect2_x2,rect2_y2 = rect2[:4]
        rect1_area = (rect1_x2-rect1_x1)*(rect1_y2-rect1_y1)
        rect2_area = (rect2_x2-rect2_x1)*(rect2_y2-rect2_y1)
        return rect1_area + rect2_area - self.intersection(rect1,rect2)

    def iou(self, rect1,rect2):
        """
        This method compute IoU
        """
        return self.intersection(rect1,rect2)/self.union(rect1,rect2)

    def post_process_YoloV8(self, outputs):
        """
        Postprocessing the predictions to filter out weak and overlapping bounding boxes and
        extract in good boxes relevant keypoints of human body.
        """
        # Lists to hold respective values while unwrapping.
        base_objects_list = []
        final_dets = []
        self.sorted_objects_list = []

        # Get NN output and transpose it
        output_data = np.transpose(outputs)

        # Split output -> 0-4: box coordinates, 5: person confidence, 6-56: 17 x (keypoints score; x coordinate; y coordinate)
        indices = np.where(np.any(output_data[:, 4:5] > self._conf_threshold, axis=1))[0]
        filtered_outputs = output_data[indices]

        for output in filtered_outputs:
            x_center, y_center, width, height = output[:4]
            left = (x_center - width/2)
            top = (y_center - height/2)
            right = (x_center + width/2)
            bottom = (y_center + height/2)
            confidence = output[4]
            kpts = output[5:]
            base_objects_list.append([left, top, right, bottom, confidence, width, height, kpts])

        # Do NMS
        base_objects_list.sort(key=lambda x: x[4], reverse=True)
        while len(base_objects_list)>0:
            final_dets.append(base_objects_list[0])
            base_objects_list = [objects for objects in base_objects_list if self.iou(objects,base_objects_list[0])<self._iou_threshold]

        return final_dets

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

        self.stai_mpu_model.set_input(0, input_data)
        self.stai_mpu_model.run()

    def get_results(self):
        """
        This method return inference results
        """
        # Maps bones to a OpenCV BGR color.
        self.KEYPOINT_EDGE_TO_COLOR = {
            (0, 1):   (0.796, 0.705, 0.235),
            (0, 2):   (0.494, 0, 0.901),
            (1, 3):   (0.796, 0.705, 0.235),
            (2, 4):   (0.494, 0, 0.901),
            (5, 7):   (0.796, 0.705, 0.235),
            (7, 9):   (0.796, 0.705, 0.235),
            (6, 8):   (0.494, 0, 0.901),
            (8, 10):  (0.494, 0, 0.901),
            (5, 6):   (0, 0.823, 1),
            (5, 11):  (0.796, 0.705, 0.235),
            (6, 12):  (0.494, 0, 0.901),
            (11, 12): (0, 0.823, 1),
            (11, 13): (0.796, 0.705, 0.235),
            (13, 15): (0.796, 0.705, 0.235),
            (12, 14): (0.494, 0, 0.901),
            (14, 16): (0.494, 0, 0.901)
        }
        output_data = self.stai_mpu_model.get_output(index=0)
        final_detections = self.post_process_YoloV8(np.squeeze(output_data))
        self.height, self.width, _ = self.get_img_size()
        (keypoint_locs, keypoint_edges, edge_colors) = self.keypoints_and_edges_for_display(final_detections)
        self._nn_finished = True

        return keypoint_locs, keypoint_edges, edge_colors


    def keypoints_and_edges_for_display(self, final_detections):
        """Returns high confidence keypoints and edges for visualization.
        Args:
        keypoints_with_scores: A numpy array with shape [1, 1, 17, 3] representing
        the keypoint coordinates and scores returned from the MoveNet model.
        height: height of the image in pixels.
        width: width of the image in pixels.
        keypoint_threshold: minimum confidence score for a keypoint to be
        visualized.
        Returns:
        A (keypoints_xy, edges_xy, edge_colors) containing:
        * the coordinates of all keypoints of all detected entities;
        * the coordinates of all skeleton edges of all detected entities;
        * the colors in which the edges should be plotted.

        Movenet post-processing comes from MoveNet: Ultra fast and accurate pose detection model
        License Apache-2.0 : https://www.tensorflow.org/hub/tutorials/movenet
        """
        keypoint_threshold = 0.4
        keypoints_all = []
        keypoint_edges_all = []
        edge_colors = []
        kpts_scores = []
        for detection in final_detections:
            kpts = detection[7]
            kpts_x = kpts[0::3]
            kpts_y = kpts[1::3]
            kpts_scores = kpts[2::3]
            kpts_absolute_xy = np.stack([self.width * np.array(kpts_x), self.height * np.array(kpts_y)], axis=-1)
            kpts_above_thresh_absolute = kpts_absolute_xy[kpts_scores > keypoint_threshold, :]
            keypoints_all.append(kpts_above_thresh_absolute)

            for edge_pair, color in self.KEYPOINT_EDGE_TO_COLOR.items():
                if (kpts_scores[edge_pair[0]] > keypoint_threshold and kpts_scores[edge_pair[1]] > keypoint_threshold):
                    x_start = kpts_absolute_xy[edge_pair[0], 0]
                    y_start = kpts_absolute_xy[edge_pair[0], 1]
                    x_end = kpts_absolute_xy[edge_pair[1], 0]
                    y_end = kpts_absolute_xy[edge_pair[1], 1]
                    line_seg = np.array([[x_start, y_start], [x_end, y_end]])
                    keypoint_edges_all.append(line_seg)
                    edge_colors.append(color)
        if keypoints_all:
            keypoints_xy = np.concatenate(keypoints_all, axis=0)
        else:
            keypoints_xy = np.zeros((0, 17, 2))

        if keypoint_edges_all:
            edges_xy = np.stack(keypoint_edges_all, axis=0)
        else:
            edges_xy = np.zeros((0, 2, 2))

        return keypoints_xy, edges_xy, edge_colors