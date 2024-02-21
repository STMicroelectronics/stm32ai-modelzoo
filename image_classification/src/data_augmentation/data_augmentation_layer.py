# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow import keras
from keras import backend
from keras.engine import base_layer
from keras.engine import base_preprocessing_layer
from keras.utils import control_flow_util
import data_augmentation


class DataAugmentationLayer(base_layer.Layer):

    def __init__(self,
                data_augmentation_fn,
                config=None,
                pixels_range=None,
                batches_per_epoch=None,
                **kwargs):
        base_preprocessing_layer.keras_kpl_gauge.get_cell('DataAugmentationLayer').set(True)
        super(DataAugmentationLayer, self).__init__(**kwargs)
        self.data_augmentation_fn = data_augmentation_fn
        self.config_dict = config
        self.pixels_range = pixels_range
        self.batches_per_epoch = batches_per_epoch
        # Get the data augmentation
        # Variable used to keep track of batch info:
        #   batch_info[0]   batch number since beginning of training
        #   batch_info[1]   epoch
        #   batch_info[2]   width of the previous image
        #   batch_info[3]   height of the previous image
        self.batch_info = tf.Variable([0, 0, 0, 0], trainable=False, dtype=tf.int32)

        # Get the data augmentation function the layer will call
        # every time it receives a batch of images to augment
        try:
            self.data_augmentation_func = eval("data_augmentation." + data_augmentation_fn)
        except:
            raise RuntimeError("Unable to find data augmentation function `{}` in `data_augmentation` package")


    def call(self, inputs, training=True):
        if training is None:
            training = backend.learning_phase()
        inputs = tf.convert_to_tensor(inputs)
            
        def transform_input_data():
            # Call the user-defined data augmentation function
            outputs = self.data_augmentation_func(
                    inputs,
                    self.config_dict,
                    pixels_range=self.pixels_range,
                    batch_info=self.batch_info)

            # Record the batch info
            batch = self.batch_info[0]
            self.batch_info.assign([
                    batch + 1,
                    (batch + 1) // self.batches_per_epoch,
                    tf.shape(outputs)[1],
                    tf.shape(outputs)[2]
                ])

            return outputs
        
        return control_flow_util.smart_cond(training, transform_input_data, lambda: inputs)


    def get_config(self):
        config = {
            'data_augmentation_fn': self.data_augmentation_fn,
            'config': self.config_dict,
            'pixels_range': self.pixels_range,
            'batches_per_epoch': self.batches_per_epoch,
        }
        base_config = super(DataAugmentationLayer, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

