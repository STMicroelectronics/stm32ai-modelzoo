# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
import keras
from keras import layers
from keras.models import Model
import numpy as np
import re
from keras.ops import clip, relu

from .bn_folding import fold_bn
from .network_parsing_utils import (get_outbound_nodes, clone_function, get_output_layers_names, node_type, node_name, 
                                   node_config, node_get_weights, node_set_weights, node_activation, layer_type, 
                                   tensor_inbound_node_name, history_operation_class_name)

CLE_NEUTRAL_LAYERS_NAMES = ["ReLU", "PreLU", "Dropout", "ZeroPadding2D"]
RELU6_SAT_UP = 6.0


def _is_neutral_layer(node):
    """
        returns True if node is among so called 'neutral layers' list from equalization point of view or if node is a
        ReLU or ReLU6
        Args:
            : the Keras node we want to analyse

        Returns: a boolean indicating if the node is considered as 'neutral' for cross-layer equalization.
    """

    if node_type(node) in CLE_NEUTRAL_LAYERS_NAMES:
        return True
    elif node_type(node) == "Activation":
        if node_activation(node) in ['relu', 'relu6']:
            return True
        else:
            return False
    else:
        return False


def _is_relu6(node):
    """
        returns True if node is ReLU6
        Args:
            node: the Keras node we want to analyse

        Returns: a boolean indicating if the node is a relu6
    """

    if node_type(node) == "Activation":
        if node_activation(node) == "relu6":
            return True
    elif node_type(node) == "ReLU":
        if 'max_value' in node_config(node):
            if node_config(node)['max_value'] is None:
                return False
            elif int(node_config(node)['max_value']) == RELU6_SAT_UP:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def _bn_parameters(model):
    """
        returns a dictionary with Batch Norm parameters each time a BN immediately follows a DW. To be called before
        folding of course. It will be used for bias absorption later on
        Args:
            model: the Keras model before folding

        Returns: a dictionary with Batch Norm parameters
    """

    bn_parameters_dict = {}

    for i, layer in enumerate(model.layers):
        if layer_type(layer) == "DepthwiseConv2D":
            out_nodes, n_out_nodes, out_nodes_type, out_nodes_names = get_outbound_nodes(layer)
            # controls that DW and BN are sequential otherwise algo undefined
            if n_out_nodes == 1 and out_nodes_type[0] == "BatchNormalization":
                # store name previous DW and gamma, beta
                bn_parameters_dict[layer.name] = [node_get_weights(out_nodes[0])[0], node_get_weights(out_nodes[0])[1]]

    return bn_parameters_dict


def _high_bias_absorption(model, coupled_index, bn_params_dict, inv_s, n=3):
    """
        implement bias absorption as defined in the https://arxiv.org/abs/2201.08442 paper.
        Args:
            model: the Keras model after cross-layer equalization was executed
            coupled_index: index of couple DW+Conv2d on which was applied cross-layer equalization
            bn_params_dict: a dictionary with Batch Norm parameters for the original model
            inv_s: inverse of 's' (equalization coefficient) in reference paper.
            n: parameter to approximate Gaussian distribution width

        Returns: a dictionary with Batch Norm parameters

    """

    for k, couple_layer_idx in enumerate(coupled_index):
        name_dw = model.layers[couple_layer_idx[0]].name
        # handle the case where BN was folded, and we append the tensor name with '_bn_folded' but not in
        # bn_params_dict. Otherwise, the split keeps name_dw unchanged.
        name_dw = name_dw.split('_bn_folded')[0]

        if name_dw in bn_params_dict:
            gamma = bn_params_dict[name_dw][0] * inv_s[k]
            beta = bn_params_dict[name_dw][1] * inv_s[k]
            c = tf.nn.relu(beta - n*gamma).numpy()

            # there is a potential issue when too many samples of the activations are above saturation point. 
            # In this case, the simplifying assumptions taken by the reference paper are no longer valid from a math 
            # point of view. In this case, we disable bias absorption by setting 'c' to 0 for the corresponding channels
            sat_level = RELU6_SAT_UP * np.array(inv_s[k])
            for q, sat in enumerate(sat_level):
                if beta[q] + n*gamma[q] >= sat:
                    c[q] = 0

            w1 = model.layers[couple_layer_idx[0]].get_weights()[0]
            b1 = model.layers[couple_layer_idx[0]].get_weights()[1]
            new_b1 = b1 - c

            w2 = model.layers[couple_layer_idx[1]].get_weights()[0]
            b2 = model.layers[couple_layer_idx[1]].get_weights()[1]
            # have ch_in first
            w2_tr = np.transpose(w2, (3, 0, 1, 2))
            w2_tr_c = [np.sum(c * channel) for k, channel in enumerate(w2_tr)]
            new_b2 = w2_tr_c + b2

            model.layers[couple_layer_idx[0]].set_weights([w1, new_b1])
            model.layers[couple_layer_idx[1]].set_weights([w2, new_b2])

    return model


def _active_number_of_nodes(list_node):
    """
        removes 'ghost' nodes no longer linked in the graph

        Args:
            list_node: list of node at a given place in the network graph

        Returns: the number of active nodes in a list after filtering these 'ghost' tensors out.
    """

    list_node_filtered = []

    unique_names = np.unique([node_name(node) for node in list_node]).tolist()
    filtrered_t_names = unique_names
    for name_i in unique_names:
        for name_j in unique_names:
            if name_j == name_i + '_bn_folded':
                filtrered_t_names.remove(name_i)

    for member in list_node:
        if node_name(member) in filtrered_t_names:
            list_node_filtered.append(member)

    return list_node_filtered


def _couple_names_and_indexes(model):
    """
           Returns a list of DW/Conv2d couple names when candidate to equalization, and the list of DW/Conv2d
           corresponding indexes. To finish returns the list of ReLU6 layer names when in between DW and Conv2d

           Args:
               model: model after batch norm folding

        Returns: candidate couples for cross-layer equalization index, names and relu6 layer names
    """

    model_layer_coupled_names = []
    model_layer_coupled_index = []
    relu6_layer_names = []

    for i, layer in enumerate(model.layers):
        if layer_type(layer) == "DepthwiseConv2D":
            out_nodes_first, _, _, _ = get_outbound_nodes(layer)
            first_level_nodes = _active_number_of_nodes(out_nodes_first)
            # check that DW and Conv2D or activation are sequential otherwise equalization is anyway not specified
            if len(first_level_nodes) == 1:
                if node_type(first_level_nodes[0]) == "Conv2D":
                    model_layer_coupled_names.append([layer.name, node_name(first_level_nodes[0])])
                elif _is_neutral_layer(first_level_nodes[0]):
                    out_nodes_second, _, _, _ = get_outbound_nodes(first_level_nodes[0])
                    second_level_nodes = _active_number_of_nodes(out_nodes_second)
                    # check that Conv2D is sequential otherwise equalization is anyway not specified
                    if len(second_level_nodes) == 1 and node_type(second_level_nodes[0]) == "Conv2D":
                        model_layer_coupled_names.append([layer.name, node_name(second_level_nodes[0])])
                        if _is_relu6(first_level_nodes[0]):
                            relu6_layer_names.append(node_name(first_level_nodes[0]))

    for name_layer in model_layer_coupled_names:
        sub_list = [i for i, layer in enumerate(model.layers) if layer.name == name_layer[0]]
        sub_list.append([i for i, layer in enumerate(model.layers) if layer.name == name_layer[1]][0])
        model_layer_coupled_index.append(sub_list)

    return model_layer_coupled_names, model_layer_coupled_index, relu6_layer_names


def choose_tensors_when_multiple_outputs(layer_input_tensor, layer_input_signature):

    layer_input_selection = []
    list_signature_names = []

    if type(layer_input_signature) is list:
        for elem in layer_input_signature:
            if hasattr(elem, 'name'):
                list_signature_names.append(elem.name)
    else:
        list_signature_names = [layer_input_signature.name]

    for elem in layer_input_tensor:
        if type(elem) is tuple:
            for sub_elem in elem:
                if sub_elem.name in list_signature_names:
                    layer_input_selection.append(sub_elem)
        else:
            layer_input_selection.append(elem)

    return layer_input_selection


def reorder_multiple_inputs_tensors(layer=None, tensor_name_list=None):
    """
           When a layer has more than one input, we have to re-order its list of input tensors, so that they match with
           actual network graph connections. network_dict dictionary of tensors gives the list of inputs for each layer 
           but it is unordered, and sometimes order matters like for concatenation for example.
           Special care to be taken when a tensor historically came from a BN. After folding the history tensor should
           be linked in the graph.
           Returns a list of ordered input tensor names for a given layer, matching network connections

           Args:
               layer: the layer under consideration, for which we need to order the list of input tensors
               tensor_name_list: list of layer input tensor we may want to re-order

           Returns: a re-ordered list of input tensors names for the layer considered
    """

    history_class_input = [history_operation_class_name(layer.input[i]) for i in range(len(layer.input))]
    if 'BatchNormalization' in history_class_input:
        return tensor_name_list
    else:
        return [tensor_inbound_node_name(layer.input[i]) for i in range(len(layer.input))]


def insert_layer_in_graph(model, layer_list, insert_layer, inv_scale, insert_layer_name=None, position='replace'):
    """
        Returns a model where some layers (layer_List) have been replaced by a new layer type 'insert_layer' with
        as parameter an element of 'inv_scale'

        Args:
            model: keras model after cross-layer equalization and bias absorption
            layer_list: list of layer names we want to replace in the graph
            insert_layer: the layer we want to insert in replacement in the graph
            inv_scale: inverse of 's' (equalization coefficient) as described in https://arxiv.org/abs/2201.08442 paper.
            insert_layer_name: name of the layer we insert. Not used at the moment
            position: could be 'replace', 'after', 'before'. Always 'replace' for cross-layer equalization

        Returns: a keras model with specified layers replaced by new insert_layer
    """

    # early exit
    if not layer_list:
        return model
    # Auxiliary dictionary to describe the network graph
    network_dict = {'input_layers_of': {}, 'new_output_tensor_of': {}}

    # Set the input layers of each layer. We parse the network using model.operations rather than model.layers that
    # contains only objects of class keras.layers and no longer operators.
    for layer in model.operations:
        out_layers_names = get_output_layers_names(layer)
        for name in out_layers_names:
            if name not in network_dict['input_layers_of']:
                network_dict['input_layers_of'].update(
                        {name: [layer.name]})
            else:
                if layer.name not in network_dict['input_layers_of'][name]:
                    network_dict['input_layers_of'][name].append(layer.name)

    for layer in model.operations[1:]:
        in_tensor_list = network_dict['input_layers_of'][layer.name]
        if len(in_tensor_list) > 1:
            network_dict['input_layers_of'][layer.name] = reorder_multiple_inputs_tensors(layer=layer,
                                                                                          tensor_name_list=in_tensor_list)

    # Set the output tensor of the input layer
    if len(model.input) == 1:
        network_dict['new_output_tensor_of'].update({model.layers[0].name: model.input[0]})
    else:
        network_dict['new_output_tensor_of'].update({model.layers[0].name: model.input})
    # Iterate over all layers after the input
    model_outputs = []
    count = 0

    # actual layer name list
    layer_name_list = [layer.name for layer in model.layers]

    # For graph modifications we again parse the network using model.operations rather than model.layers that
    # contains only objects of class keras.layers and no longer operators.
    for layer in model.operations[1:]:
        # Determine input tensors
        layer_input = [network_dict['new_output_tensor_of'][layer_aux]
                       for layer_aux in network_dict['input_layers_of'][layer.name]]
        layer_input = choose_tensors_when_multiple_outputs(layer_input, layer.input)

        if len(layer_input) == 1:
            layer_input = layer_input[0]

        # Insert layer if name matches
        if layer.name in layer_list:
            if position == 'replace':
                x = layer_input
            elif position == 'after':
                x = layer(layer_input)
            elif position == 'before':
                pass
            else:
                raise ValueError('position must be: before, after or replace')

            if insert_layer:
                if type(insert_layer) is list:
                    new_layer = insert_layer[count]
                    x = new_layer(x)
                elif insert_layer.__class__.__name__ == 'ReLU':
                    new_layer = insert_layer()
                    new_layer._name = '{}_{}'.format(layer.name, 'modified_to_relu')
                    x = new_layer(x)
                elif (insert_layer.__class__.__name__ == 'function' or
                      insert_layer.__class__.__name__ == 'cython_function_or_method'):
                    # adaptive clip
                    x = insert_layer(t=x, invs=inv_scale[count])
                else:
                    pass
                count = count + 1

            if position == 'before':
                x = layer(x)
        else:
            if layer.__class__.__name__ == 'TFOpLambda' or layer.__class__.__name__ == 'SlicingOpLambda':
                print("Lamdba layer detected")
            elif layer.name not in layer_name_list:
            # Keras or TF ops and not type Layers
                if isinstance(layer_input, list):
                    if len(layer_input) == 2:
                        x = layer(layer_input[0], layer_input[1])
                else:
                    x = layer(layer_input)
            else:
                x = layer(layer_input)

        # Set new output tensor (the original one, or the one of the inserted layer)
        network_dict['new_output_tensor_of'].update({layer.name: x})

        # Save tensor in output list if it is output in initial model at origin, if layer_name
        if layer.name in model.output_names:
            model_outputs.append(x)

    return Model(inputs=model.input, outputs=model_outputs)


def _cross_layer_equalisation(model, coupled_index):
    """
        Returns a model where couple layers weights are equalized as described in https://arxiv.org/abs/2201.08442 paper

        Args:
            model: keras model after folding
            coupled_index: index of all the couples DW/Conv2d eligible to equalisation

        Returns: a model with weights and bias updated by cross-layer equalization, and the list of inverse 
        equalisation coefficients.
    """

    eps = 0.0
    list_inv_s = []

    for couple_layer_idx in coupled_index:
        w1 = model.layers[couple_layer_idx[0]].get_weights()[0]
        b1 = model.layers[couple_layer_idx[0]].get_weights()[1]
        # have ch_out first
        w1_tr = np.transpose(w1, (2, 0, 1, 3))

        w2 = model.layers[couple_layer_idx[1]].get_weights()[0]
        b2 = model.layers[couple_layer_idx[1]].get_weights()[1]
        # have ch_in first
        w2_tr = np.transpose(w2, (2, 0, 1, 3))

        # vector s calculation
        r1 = [np.max(e) - np.min(e) for e in w1_tr]
        r2 = [np.max(e) - np.min(e) for e in w2_tr]
        s = [1/(r2[k] + eps) * np.sqrt(r1[k] * r2[k]) for k in range(len(r1))]

        # Treat the corner case where s(k) == 0 in this case it would be impossible to calculate 1/s(k)
        # In case r1(k) was null we can set s(k) to 1 because there is no need in this case to scale down this channel
        # weights, since in any case they are null
        for idx, e in enumerate(s):
            if e == 0 and r1[idx] == 0:
                s[idx] = 1

        inv_s = [1/(e + eps) for e in s]
        list_inv_s.append(inv_s)

        new_w1_tr = [inv_s[k]*channel for k, channel in enumerate(w1_tr)]
        new_w1 = np.array(np.transpose(new_w1_tr, (1, 2, 0, 3)))
        new_b1 = inv_s * b1

        new_w2_tr = [s[k]*channel for k, channel in enumerate(w2_tr)]
        new_w2 = np.array(np.transpose(new_w2_tr, (1, 2, 0, 3)))

        model.layers[couple_layer_idx[0]].set_weights([new_w1, new_b1])
        model.layers[couple_layer_idx[1]].set_weights([new_w2, b2])

    return model, list_inv_s


def _zero_irrelevant_channels(model, min_weights_th, ct_value=0.0):
    """
        Returns a model with weights arbitrarily set to constant value typically 0, if all weights corresponding to a
        given output channel are below 'min_weight_th' in absolute value. Restricted to Conv2d and DW.
        This helps reducing possible bias saturation issue at quantization, when weights channel scale is very small

        Args:
            model: keras model after batch normalisation folding
            min_weights_th: arbitrary threshold under which we consider current weights to be replaced by 'ct_value'
            ct_value: constant value set to the weights when they are < min_weights_th for a given channel. For
            this application ct_value is always set to 0.0

        Returns: the keras model with weights updated

    """

    for layer in model.layers:

        if layer.__class__.__name__ == 'Functional':
            _zero_irrelevant_channels(layer, min_weights_th)
        if layer.__class__.__name__ in ("Conv2D", "DepthwiseConv2D"):
            # weights
            bias_exist = len(layer.get_weights()) == 2
            if bias_exist:
                w = layer.get_weights()[0]
                b = layer.get_weights()[1]
            else:
                w = layer.get_weights()[0]
            if layer.__class__.__name__ == "DepthwiseConv2D":
                # have ch_out first
                w = np.transpose(w, (2, 0, 1, 3))
                for i, we in enumerate(w):
                    if np.abs(np.min(we)) < min_weights_th and np.abs(np.max(we)) < min_weights_th:
                        w[i] = ct_value * np.ones((w.shape[1], w.shape[2], w.shape[3]))
                w = np.transpose(w, (1, 2, 0, 3))
                if bias_exist:
                    layer.set_weights([w, b])
                else:
                    layer.set_weights([w])
            elif layer.__class__.__name__ == "Conv2D":
                # have ch_out first
                w = np.transpose(w, (3, 0, 1, 2))
                for i, we in enumerate(w):
                    if np.abs(np.min(we)) < min_weights_th and np.abs(np.max(we)) < min_weights_th:
                        w[i] = ct_value * np.ones((w.shape[1], w.shape[2], w.shape[3]))
                w = np.transpose(w, (1, 2, 3, 0))
                if bias_exist:
                    layer.set_weights([w, b])
                else:
                    layer.set_weights([w])

    return model


@keras.saving.register_keras_serializable()
class STCustomClip(keras.layers.Layer):
    def __init__(self, name=None, min_vector=None, max_vector=None, **kwargs):
        # important to add **kwargs if super().get_config() is called in get_config() because it brings 
        # parameters defined in kwargs
        super().__init__(name=name, **kwargs)
        self.min_vector = min_vector
        self.max_vector = max_vector

    def call(self, inputs):
        return keras.ops.clip(x=inputs, x_min=self.min_vector, x_max=self.max_vector)

    def get_config(self):
        config = super().get_config()
        config.update({"min_vector": self.min_vector})
        config.update({"max_vector": self.max_vector})
        return config


def _adaptive_clip_per_channel(t=None, invs=None):
    """
        Returns a layer for adaptive channel clipping whose level is given through 'invs'
        Restricted to ReLU6

        Args:
            t: a Keras tensor input of the adaptive clip per channel layer
            invs: list of equalisation coefficients as described in https://arxiv.org/abs/2201.08442 reference paper

        Returns:
            A tensorflow layer for adaptive clipping per-channel
    """
    nb_ch_out = int(t.shape[-1])
    ch_sat_level = [RELU6_SAT_UP*k for k in invs]
    scale = (np.max(ch_sat_level) - np.min(ch_sat_level)) / 65535
    ch_sat_level = np.round(ch_sat_level / scale) * scale

    # although not useful from a math point of view since the following clip has clip_min == 0, the addition of this
    # relu before the clip will make the interpreter understand it needs to fuse it with previous layer which helps
    # reducing the dynamic range of the layer output and thus to find a smaller scale and eventually reduce the
    # quantization noise.
    name_layer = 'ReLU_' + t.name
    custom_activ = layers.ReLU(name=name_layer)(t)

    name_layer = 'ST_Custom_Clip_' + t.name
    # important to cast to lists otherwise issue at model loading because from_config() expects basic python types and
    # not np types
    custom_activ = STCustomClip(name=name_layer,
                                min_vector=np.zeros(nb_ch_out).tolist(),
                                max_vector=ch_sat_level.tolist())(custom_activ)

    return custom_activ


def model_formatting_ptq_per_tensor(model_origin):
    """
        Returns a keras model after all the PTQ optimization chain was executed:
            - batch norm folding
            - zeroing irrelevant channels (too weak)
            - cross layer equalisation (CLE)
            - bias absorption
            - insertion of the adaptive clip layers wherever needed

        Args:
            model_origin: the original Keras model

        Returns:
            A Keras model optimized for subsequent per-tensor quantization
    """

    # keep in memory BN parameters for future bias absorption
    bn_params_dict = _bn_parameters(model_origin)

    # BN folding
    model_folded = fold_bn(model_origin)
    #bw_bn_folding(model_origin, epsilon=1e-3, dead_channel_th=1e-10)

    # zeroing some channels to avoid bias saturation at quantization
    model_folded = _zero_irrelevant_channels(model_folded, min_weights_th=1e-10)

    # extract layer couples names and indexes for equalization
    layer_coupled_names, layer_coupled_index, layer_to_replace_names = _couple_names_and_indexes(model_folded)

    # performs reference paper cross-layer equalization on selected couples
    model_cle, list_inv_s = _cross_layer_equalisation(model=model_folded, coupled_index=layer_coupled_index)

    # performs bias absorption, which is optional
    model_cle = _high_bias_absorption(model=model_cle, coupled_index=layer_coupled_index, inv_s=list_inv_s,
                                     bn_params_dict=bn_params_dict, n=3)

    # insert adaptive channel clipping layers at the right places in the graph
    model_cle = insert_layer_in_graph(model=model_cle, layer_list=layer_to_replace_names,
                                      insert_layer=_adaptive_clip_per_channel, inv_scale=list_inv_s,
                                      insert_layer_name=None,
                                      position='replace')
    return model_cle
