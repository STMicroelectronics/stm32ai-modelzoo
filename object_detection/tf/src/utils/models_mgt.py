#  /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import os
import tensorflow as tf
from omegaconf import DictConfig
from tensorflow.keras import layers



def change_yolo_model_number_of_classes(model,num_classes,num_anchors):

    output_shape = (5 + num_classes)*num_anchors

    # If the model already has the correct number of classes -> dont do anything
    for outp in model.outputs:
        if outp.shape[0] == output_shape:
            return model

    l = -1
    l_list = []

    while True:

        layer_type = type(model.layers[l])
        layer_config = model.layers[l].get_config()

        if layer_type in [layers.Conv2D,
                          layers.Conv2DTranspose,
                          layers.Conv1D,
                          layers.Conv1DTranspose,
                          layers.Dense]:
            if layer_type in [layers.Conv2D,layers.Conv2DTranspose,layers.Conv1D,layers.Conv1DTranspose]:
                layer_config['filters'] = output_shape
                new_layer = layer_type(**layer_config)
                outputs = new_layer(model.layers[l-1].output)
            else:
                layer_config['units'] = output_shape
                new_layer = layer_type(**layer_config)
                outputs = new_layer(model.layers[l-1].output)

            for i,new_l in enumerate(l_list[::-1]):
                outputs = new_l(outputs)

            return tf.keras.Model(inputs=model.input, outputs=outputs, name=model.name)

        else:
            l_list.append(layer_type(**layer_config))
            l-=1

    return None


def search_layer(tensor,model,with_his="output"):
    for i,l in enumerate(model.layers): # search which layer has this tensor as output
        if not type(l)==layers.InputLayer:
            if with_his=="output":
                for lo in (l.output if type(l.output)==list else [l.output]):
                    if tensor is lo:
                        return i
            if with_his=="input":
                if tensor in (l.input if type(l.input)==list else [l.input]):
                    return i
    return None

def change_yolo_x_model_number_of_classes(model,num_classes,num_anchors):

    model_outputs = model.outputs

    concatenate_layers_indexes = []
    for o in model_outputs:
        concatenate_layers_indexes.append(search_layer(o,model,'output'))

    output_tensors_list = [] # list of output tensors of the new model

    for c in concatenate_layers_indexes: # for all Yolo_X heads

        # concatenate layer infos
        concatenate_layer_inputs = model.layers[c].input
        concatenate_layer_type   = type(model.layers[c])
        concatenate_layer_config = model.layers[c].get_config()

        new_concatenate_layer_inputs = []

        list_of_shapes = [4*num_anchors,1*num_anchors,num_classes*num_anchors]

        for i,t in enumerate(concatenate_layer_inputs):
            if t.shape[-1] != list_of_shapes[i]:

                conv_layer_index = search_layer(t,model,"output")

                conv_layer_input  = model.layers[conv_layer_index].input
                conv_layer_type   = type(model.layers[conv_layer_index])
                conv_layer_config = model.layers[conv_layer_index].get_config()

                # change the number of filters of the Conv2d layer
                conv_layer_config['filters'] = list_of_shapes[i]

                new_conv_layer = conv_layer_type(**conv_layer_config)
                new_concatenate_layer_inputs.append(new_conv_layer(conv_layer_input))
            else:
                new_concatenate_layer_inputs.append(concatenate_layer_inputs[i])

        new_concatenate_layer = concatenate_layer_type(**concatenate_layer_config)
        output_tensors_list.append(new_concatenate_layer(new_concatenate_layer_inputs))

    return tf.keras.Model(inputs=model.input, outputs=output_tensors_list, name=model.name)

def change_model_input_shape(model,new_inp_shape):
    
    conf = model.get_config()
    conf['layers'][0]['config']['batch_shape'] = new_inp_shape
    new_model = model.__class__.from_config(conf, custom_objects={})

    # iterate over all the layers that we want to get weights from
    weights = [layer.get_weights() for layer in model.layers[1:]]
    for layer, weight in zip(new_model.layers[1:], weights):
        layer.set_weights(weight)

    old_inp_shape = model.get_config()['layers'][0]['config']['batch_shape']

    return new_model, old_inp_shape

def change_yolo_model_number_of_classes(model,num_classes,num_anchors):

    output_shape = (5 + num_classes)*num_anchors

    # If the model already has the correct number of classes -> dont do anything
    for outp in model.outputs:
        if outp.shape[0] == output_shape:
            return model

    l = -1
    l_list = []

    while True:

        layer_type = type(model.layers[l])
        layer_config = model.layers[l].get_config()

        if layer_type in [layers.Conv2D,
                          layers.Conv2DTranspose,
                          layers.Conv1D,
                          layers.Conv1DTranspose,
                          layers.Dense]:
            if layer_type in [layers.Conv2D,layers.Conv2DTranspose,layers.Conv1D,layers.Conv1DTranspose]:
                layer_config['filters'] = output_shape
                new_layer = layer_type(**layer_config)
                outputs = new_layer(model.layers[l-1].output)
            else:
                layer_config['units'] = output_shape
                new_layer = layer_type(**layer_config)
                outputs = new_layer(model.layers[l-1].output)

            for i,new_l in enumerate(l_list[::-1]):
                outputs = new_l(outputs)

            return tf.keras.Model(inputs=model.input, outputs=outputs, name=model.name)

        else:
            l_list.append(layer_type(**layer_config))
            l-=1

    return None


def search_layer(tensor,model,with_his="output"):
    for i,l in enumerate(model.layers): # search which layer has this tensor as output
        if with_his=="output":
            if tensor in (l.output if type(l.output)==list else [l.output]):
                return i
        if with_his=="input":
            if tensor in (l.input if type(l.input)==list else [l.input]):
                return i
    return None

def change_yolo_x_model_number_of_classes(model,num_classes,num_anchors):

    model_outputs = model.outputs

    concatenate_layers_indexes = []
    for o in model_outputs:
        concatenate_layers_indexes.append(search_layer(o,model,'output'))

    output_tensors_list = [] # list of output tensors of the new model

    for c in concatenate_layers_indexes: # for all Yolo_X heads

        # concatenate layer infos
        concatenate_layer_inputs = model.layers[c].input
        concatenate_layer_type   = type(model.layers[c])
        concatenate_layer_config = model.layers[c].get_config()

        new_concatenate_layer_inputs = []

        list_of_shapes = [4*num_anchors,1*num_anchors,num_classes*num_anchors]

        for i,t in enumerate(concatenate_layer_inputs):
            if t.shape[-1] != list_of_shapes[i]:

                conv_layer_index = search_layer(t,model,"output")

                conv_layer_input  = model.layers[conv_layer_index].input
                conv_layer_type   = type(model.layers[conv_layer_index])
                conv_layer_config = model.layers[conv_layer_index].get_config()

                # change the number of filters of the Conv2d layer
                conv_layer_config['filters'] = list_of_shapes[i]

                new_conv_layer = conv_layer_type(**conv_layer_config)
                new_concatenate_layer_inputs.append(new_conv_layer(conv_layer_input))
            else:
                new_concatenate_layer_inputs.append(concatenate_layer_inputs[i])

        new_concatenate_layer = concatenate_layer_type(**concatenate_layer_config)
        output_tensors_list.append(new_concatenate_layer(new_concatenate_layer_inputs))

    return tf.keras.Model(inputs=model.input, outputs=output_tensors_list, name=model.name)


def ai_runner_invoke(image_processed,ai_runner_interpreter):
    def reduce_shape(x):  # reduce shape (request by legacy API)
        old_shape = x.shape
        n_shape = [old_shape[0]]
        for v in x.shape[1:len(x.shape) - 1]:
            if v != 1:
                n_shape.append(v)
        n_shape.append(old_shape[-1])
        return x.reshape(n_shape)

    preds, _ = ai_runner_interpreter.invoke(image_processed)
    predictions = []
    for x in preds:
        x = reduce_shape(x)
        predictions.append(x.copy())
    return predictions


