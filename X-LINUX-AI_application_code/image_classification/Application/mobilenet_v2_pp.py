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

class NeuralNetwork:
    """
    Class that handles Neural Network inference
    """
    def __init__(self, model_file, label_file, input_mean, input_std):
        """
        :param model_path:  model to be executed
        :param label_file:  name of file containing labels
        :param input_mean: input_mean
        :param input_std: input standard deviation
        """

        def load_labels(filename):
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

        # Initialization of network class
        self.stai_mpu_model = stai_mpu_network(model_path=self._model_file)

        # Read input tensor information
        self.num_inputs = self.stai_mpu_model.get_num_inputs()
        self.input_tensor_infos = self.stai_mpu_model.get_input_infos()

        # Read output tensor information
        self.num_outputs = self.stai_mpu_model.get_num_outputs()
        self.output_tensor_infos = self.stai_mpu_model.get_output_infos()

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
        input_width =  input_tensor_shape[1]
        input_height =  input_tensor_shape[2]
        input_channel =  input_tensor_shape[0]
        print("input_width",input_width)
        print("input_height",input_height)
        print("input_channel",input_channel)
        return (input_width,input_height,input_channel)

    def launch_inference(self, img):
        """
        This method launches inference using the invoke call
        :param img: the image to be inferred
        """
        # add N dim
        input_data = np.expand_dims(img, axis=0)

        if self.input_tensor_infos[0].get_dtype() == np.float32:
            input_data = (np.float32(input_data) - self._input_mean) / self._input_std

        self.stai_mpu_model.set_input(0, input_data)
        self.stai_mpu_model.run()

    def get_results(self):
        """
        This method can print and return the top_k results of the inference
        """
        output_data = self.stai_mpu_model.get_output(index=0)
        results = np.squeeze(output_data)

        top_k = results.argsort()[-5:][::-1]

        if self.output_tensor_infos[0].get_dtype() == np.uint8 :
            return (results[top_k[0]]/255, top_k[0])
        else:
            return (results[top_k[0]], top_k[0])