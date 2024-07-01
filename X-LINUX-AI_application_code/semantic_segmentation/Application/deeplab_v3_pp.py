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

class NeuralNetwork:
    """
    Class that handles Neural Network inference
    """

    def __init__(self, model_file, label_file, input_mean, input_std):
        """
        :param model_file: model to be executed
        :param label_file:  name of file containing labels
        :param input_mean: input_mean
        :param input_std: input standard deviation
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
        self._label_file = label_file
        self._input_mean = input_mean
        self._input_std = input_std
        self._floating_model = False
        self.first_inference_done = False
        self.colors_map = np.array([(0,0,0,0),          #1 background
                                    (3,35,75,180),      #2 airplane
                                    (229,204,255,180),  #3 bicycle
                                    (60,180,230,180),   #4 bird
                                    (255,210,0,180),    #5 boat
                                    (0,100,0,180),      #6 bottle
                                    (100,56,0,180),     #7 bus
                                    (52,0,100,180),     #8 car
                                    (0,247,255,180),    #9 cat
                                    (255,190,133,180),  #10 chair
                                    (255,0,0,180),      #11 cow
                                    (178,255,102,180),  #12 dining table
                                    (0,0,255,180),      #13 dog
                                    (100, 0, 40,180),   #14 horse
                                    (210,105,30,180),   #15 motorbike
                                    (230,0,126,180),    #16 person
                                    (204,204,0,180),    #17 potted plant
                                    (87,74,44,180),     #18 sheep
                                    (255,128,0,180),    #19 sofa
                                    (255,255,255,180),  #20 train
                                    (0,255,34,180)])    #21 tv

        # Initialize NN model
        self.stai_mpu_model = stai_mpu_network(model_path=self._model_file)

        # Read input tensor information
        self.num_inputs = self.stai_mpu_model.get_num_inputs()
        self.input_tensor_infos = self.stai_mpu_model.get_input_infos()

        # Read input tensor information
        self.num_outputs = self.stai_mpu_model.get_num_outputs()
        self.output_tensor_infos = self.stai_mpu_model.get_output_infos()

        # check the type of the input tensor
        if self.input_tensor_infos[0].get_dtype() == np.float32:
            self._floating_model = True
            print("Floating point graph input")

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
        # NxHxWxC, H:1, W:2, C:3
        input_tensor_shape = self.input_tensor_infos[0].get_shape()
        input_width = input_tensor_shape[1]
        input_height = input_tensor_shape[2]
        input_channel = input_tensor_shape[3]
        print("input_width", input_width)
        print("input_height", input_height)
        print("input_channel", input_channel)
        return (input_width, input_height, input_channel)

    def launch_inference(self, img):
        """
        This method launches inference using the invoke call
        :param img: the image to be inferred
        """
        # add N dim
        input_data = np.expand_dims(img, axis=0)

        if self._floating_model:
            input_data = (np.float32(input_data) - self._input_mean) / self._input_std

        self.stai_mpu_model.set_input(0, input_data)
        start = timer()
        self.stai_mpu_model.run()
        end = timer()
        inference_time = end - start
        return inference_time

    def get_results(self):
         """
         This method is used to recover NN results
         and do the minimal post-process required
         """
         output_data = self.stai_mpu_model.get_output(index=0)
         seg_map = np.squeeze(output_data)
         seg_map_np = np.asarray(seg_map)
         seg_map_argmax = np.argmax(seg_map_np, axis=2)
         seg_map_argmax = seg_map_argmax.astype(np.int8)
         seg_map_argmax = np.asarray(seg_map_argmax)
         seg_map_colored = self.colors_map[seg_map_argmax].astype(np.uint8)
         unique_label=np.unique(seg_map_argmax)
         return unique_label,seg_map_colored