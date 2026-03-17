# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from keras.models import Model
import numpy as np


def node_type(node):
    return node.operation.__class__.__name__


def node_config(node):
    return node.operation.get_config()


def node_activation(node):
    return node.operation.get_config()["activation"]


def node_name(node):
    # handle the case where 'name' is in the get_config() like for keras.layers or directly in operations if node is a
    # keras.ops
    if 'name' in node_config(node):
        return node_config(node)['name']
    elif node.operation.name:
        return node.operation.name
    else:
        print("Error: Detected node with no name. Each node must have a name")
        return None


def node_get_weights(node):
    return node.operation.get_weights()


def node_set_weights(node, weights):
    return node.operation.set_weights(weights)


def tensor_inbound_node_name(tensor):
    return tensor._keras_history.operation.name


def history_operation_class_name(tensor):
    return tensor._keras_history.operation.__class__.__name__

    
def layer_type(layer):
    return layer.__class__.__name__


def clone_function(layer, new_name):
    config = layer.get_config()
    config['name'] = new_name

    return layer.__class__.from_config(config)


def get_outbound_nodes(obj):
    """
        returns the outbound nodes and their properties of a specified Keras layer we want to analyse
        Args:
            obj: layer or node we analyse
        Returns:
            out_nodes: the list of the layer or node output nodes
            n_out_nodes: the number of output nodes
            out_nodes_type: the type of the output nodes ('Conv2d'...)
            out_nodes_names: list of output nodes names

    """
    if obj.__class__.__name__ is 'Node':
        out_nodes = obj.operation._outbound_nodes
    else:
        out_nodes = obj._outbound_nodes

    n_out_nodes = len(out_nodes)
    out_nodes_type = [node_type(n) for n in out_nodes]
    out_nodes_names = [node_name(n) for n in out_nodes]

    return out_nodes, n_out_nodes, out_nodes_type, out_nodes_names


def get_output_layers_names(layer):
    """
        returns the output layers names of a specified Keras layer we want to analyse
        Args:
            layer we analyse
        Returns:
            out_layers_names: list of output layer names

    """
    out_layers_names = []

    for node in layer._outbound_nodes:
        out_layers_names.append(node_name(node))

    return out_layers_names

