# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022-2023 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import onnx
from onnx import helper, numpy_helper
import numpy as np
from collections import defaultdict
import logging

import tf2onnx
import tensorflow as tf


def fold_batch_norm(onnx_model):
    """
    Fold BatchNormalization layers or Mul + Add patterns into preceding or following Conv or Gemm layers
    in an ONNX model, while handling complex residual connections with multiple branches.

    Args:
        onnx_model (onnx.ModelProto): The ONNX model to optimize.

    Returns:
        onnx.ModelProto: The optimized ONNX model with BatchNormalization layers or Mul + Add patterns folded.
    """
    graph = onnx_model.graph
    nodes_to_remove = []
    nodes_to_add = []

    # Preprocess initializers and graph mappings
    initializer_dict = {init.name: numpy_helper.to_array(init) for init in graph.initializer}
    output_to_node = {node.output[0]: node for node in graph.node}

    # Iterate through all nodes in the graph
    for node in graph.node:
        if node.op_type == "BatchNormalization":
            # Handle BatchNormalization folding
            _fold_batch_norm_node(node, graph, nodes_to_remove, nodes_to_add, initializer_dict, output_to_node)
        elif node.op_type == "Mul":
            # Check if the Mul is followed by an Add (Mul + Add pattern)
            _fold_mul_add_pattern(node, graph, nodes_to_remove, nodes_to_add, initializer_dict, output_to_node)

    # Remove unused nodes
    for node in nodes_to_remove:
        graph.node.remove(node)

    # Add updated initializers
    for initializer in nodes_to_add:
        graph.initializer.append(initializer)

    # Remove unused initializers
    _remove_unused_initializers(graph)

    # Validate the optimized model
    onnx.checker.check_model(onnx_model)
    print("Model validation passed after BatchNormalization folding.")

    return onnx_model


def _fold_batch_norm_node(bn_node, graph, nodes_to_remove, nodes_to_add, initializer_dict, output_to_node):
    """
    Fold a BatchNormalization node into a preceding or following Conv or Gemm layer.

    Args:
        bn_node (onnx.NodeProto): The BatchNormalization node to fold.
        graph (onnx.GraphProto): The ONNX graph.
        nodes_to_remove (list): List of nodes to remove from the graph.
        nodes_to_add (list): List of initializers to add to the graph.
        initializer_dict (dict): Dictionary of initializers for fast lookup.
        output_to_node (dict): Mapping from output names to nodes.
    """
    bn_input = bn_node.input[0]

    # Find preceding node
    preceding_node = output_to_node.get(bn_input)

    if preceding_node and preceding_node.op_type in ["Conv", "Gemm"]:
        print(f"Folding BatchNormalization node {bn_node.name} into preceding layer {preceding_node.name}.")
        _fold_batch_norm_into_layer(bn_node, preceding_node, nodes_to_remove, nodes_to_add, "backward", initializer_dict)
    else:
        # Find following node
        following_node = next((n for n in graph.node if bn_node.output[0] in n.input and n.op_type in ["Conv", "Gemm"]),
                              None)
        if following_node:
            print(f"Folding BatchNormalization node {bn_node.name} into following layer {following_node.name}.")
            _fold_batch_norm_into_layer(bn_node, following_node, nodes_to_remove, nodes_to_add, "forward",
                                        initializer_dict)
        else:
            print(
                f"Skipping BatchNormalization node {bn_node.name} as no suitable preceding or following layer was found.")

    # Update connections: Replace BatchNormalization's output with the preceding node's output
    _update_connections(graph, bn_node, preceding_node)


def _is_depthwise_conv(conv_node, weights):
    """
    Check if a Conv node is a depthwise convolution.

    Args:
        conv_node (onnx.NodeProto): The Conv node to check.
        weights (np.ndarray): The weights of the Conv node.

    Returns:
        bool: True if the Conv node is a depthwise convolution, False otherwise.
    """
    # Extract the group attribute from the Conv node
    group = next((attr.i for attr in conv_node.attribute if attr.name == "group"), 1)

    # Check if the group is equal to the number of output channels (depthwise condition)
    num_output_channels = weights.shape[0]  # For Conv weights, shape is (num_output_channels, num_input_channels, H, W)

    return group > 1 and group == num_output_channels


def _fold_batch_norm_into_layer(bn_node, target_node, nodes_to_remove, nodes_to_add, direction, initializer_dict):
    """
    Fold a BatchNormalization layer into a target Conv or Gemm layer, with support for depthwise convolutions.

    Args:
        bn_node (onnx.NodeProto): The BatchNormalization node to fold.
        target_node (onnx.NodeProto): The target Conv or Gemm node to fold into.
        graph (onnx.GraphProto): The ONNX graph.
        nodes_to_remove (list): List of nodes to remove from the graph.
        nodes_to_add (list): List of initializers to add to the graph.
        direction (str): "backward" or "forward" to indicate folding direction.
        initializer_dict (dict): Dictionary of initializers for fast lookup.
    """
    # Extract BatchNormalization parameters
    scale = _get_initializer(initializer_dict, bn_node.input[1])
    bias = _get_initializer(initializer_dict, bn_node.input[2])
    mean = _get_initializer(initializer_dict, bn_node.input[3])
    var = _get_initializer(initializer_dict, bn_node.input[4])
    epsilon = float(bn_node.attribute[0].f)

    # Extract weights and biases of the target layer
    weights = _get_initializer(initializer_dict, target_node.input[1])
    if len(target_node.input) > 2:
        biases = _get_initializer(initializer_dict, target_node.input[2])
    else:
        biases = np.zeros(weights.shape[0] if target_node.op_type == "Conv" else weights.shape[1], dtype=np.float32)

    # Check if the Conv layer is a depthwise convolution
    is_depthwise = target_node.op_type == "Conv" and _is_depthwise_conv(target_node, weights)

    # Ensure scale, bias, mean, and variance have the correct shape
    if target_node.op_type == "Conv":
        if is_depthwise:
            # For depthwise convolutions, parameters should match the number of groups (channels)
            scale = scale.reshape(-1, 1, 1, 1)
            bias = bias.reshape(-1)
            mean = mean.reshape(-1)
            var = var.reshape(-1)

    # Compute new weights and biases based on the folding direction
    if direction == "backward":
        if target_node.op_type == "Conv":
            new_weights = weights * (scale / np.sqrt(var + epsilon)).reshape(-1, 1, 1, 1)
        elif target_node.op_type == "Gemm":
            new_weights = weights * (scale / np.sqrt(var + epsilon)).reshape(1, -1)
        new_biases = (biases - mean) * (scale / np.sqrt(var + epsilon)) + bias
    elif direction == "forward":
        if target_node.op_type == "Conv":
            new_weights = weights * scale.reshape(-1, 1, 1, 1)
        elif target_node.op_type == "Gemm":
            new_weights = weights * scale.reshape(1, -1)
        new_biases = (biases - mean) * (scale / np.sqrt(var + epsilon)) + bias
    else:
        raise ValueError(f"Invalid folding direction: {direction}")

    # Generate unique names for the new initializers
    new_weight_name = target_node.input[1] + "_folded"
    new_bias_name = (target_node.input[2] if len(target_node.input) > 2 else target_node.input[1] + "_bias") + "_folded"

    # Update weights and biases in the graph
    new_weight_initializer = numpy_helper.from_array(new_weights, new_weight_name)
    new_bias_initializer = numpy_helper.from_array(new_biases, new_bias_name)

    # Update the target node to use the new initializer names
    target_node.input[1] = new_weight_name
    if len(target_node.input) > 2:
        target_node.input[2] = new_bias_name
    else:
        target_node.input.append(new_bias_name)

    # Add new initializers
    nodes_to_add.append(new_weight_initializer)
    nodes_to_add.append(new_bias_initializer)

    # Mark BatchNormalization node for removal
    nodes_to_remove.append(bn_node)


def _fold_mul_add_pattern(mul_node, graph, nodes_to_remove, nodes_to_add, initializer_dict, output_to_node):
    """
    Fold a Mul + Add pattern into a preceding or following Conv or Gemm layer.

    Args:
        mul_node (onnx.NodeProto): The Mul node to fold.
        graph (onnx.GraphProto): The ONNX graph.
        nodes_to_remove (list): List of nodes to remove from the graph.
        nodes_to_add (list): List of initializers to add to the graph.
        initializer_dict (dict): Dictionary of initializers for fast lookup.
        output_to_node (dict): Mapping from output names to nodes.
    """
    # Check if the Mul is followed by an Add
    mul_output = mul_node.output[0]
    add_node = next((n for n in graph.node if mul_output in n.input and n.op_type == "Add"), None)
    if not add_node:
        return  # No Add node found, skip

    # Extract scale and bias from Mul and Add
    scale = _get_initializer(initializer_dict, mul_node.input[1])
    bias = _get_initializer(initializer_dict, add_node.input[1])
    if scale == None or bias == None:
        return

    # Find preceding node
    preceding_node = output_to_node.get(mul_node.input[0])

    if preceding_node and preceding_node.op_type in ["Conv", "Gemm"]:
        print(f"Folding Mul + Add pattern into preceding layer {preceding_node.name}.")
        _fold_mul_add_into_layer(preceding_node, scale, bias, graph, nodes_to_add, "backward")
        # Update connections: Replace Add's output with the preceding node's output
        _update_connections(graph, add_node, preceding_node)
    else:
        # Find following node
        following_node = next(
            (n for n in graph.node if add_node.output[0] in n.input and n.op_type in ["Conv", "Gemm"]), None)
        if following_node:
            print(f"Folding Mul + Add pattern into following layer {following_node.name}.")
            _fold_mul_add_into_layer(following_node, scale, bias, graph, nodes_to_add, "forward")
            # Update connections: Replace Add's output with the following node's input
            _update_connections(graph, add_node, following_node)
        else:
            print(f"Skipping Mul + Add pattern as no suitable preceding or following layer was found.")

    # Mark Mul and Add nodes for removal
    nodes_to_remove.append(mul_node)
    nodes_to_remove.append(add_node)


def _fold_mul_add_into_layer(target_node, scale, bias, graph, nodes_to_add, direction):
    """
    Fold a Mul + Add pattern into a target Conv or Gemm layer, with support for depthwise convolutions.

    Args:
        target_node (onnx.NodeProto): The target Conv or Gemm node to fold into.
        scale (np.ndarray): The scale values from the Mul node.
        bias (np.ndarray): The bias values from the Add node.
        graph (onnx.GraphProto): The ONNX graph.
        nodes_to_remove (list): List of nodes to remove from the graph.
        nodes_to_add (list): List of initializers to add to the graph.
        direction (str): "backward" or "forward" to indicate folding direction.
    """
    # Extract weights and biases of the target layer
    weights = _get_initializer({init.name: numpy_helper.to_array(init) for init in graph.initializer},
                               target_node.input[1])
    if len(target_node.input) > 2:
        biases = _get_initializer({init.name: numpy_helper.to_array(init) for init in graph.initializer},
                                  target_node.input[2])
    else:
        biases = np.zeros(weights.shape[0] if target_node.op_type == "Conv" else weights.shape[1], dtype=np.float32)

    # Check if the Conv layer is a depthwise convolution
    is_depthwise = target_node.op_type == "Conv" and _is_depthwise_conv(target_node, weights)

    # Ensure scale and bias have the correct shape
    if target_node.op_type == "Conv":
        if is_depthwise:
            # For depthwise convolutions, scale and bias should match the number of groups (channels)
            scale = scale.reshape(-1, 1, 1, 1)
            bias = bias.reshape(-1)

    if direction == "backward":
        if target_node.op_type == "Conv":
            if is_depthwise:
                # Apply scale per channel for depthwise convolutions
                new_weights = weights * scale
            else:
                new_weights = weights * scale
        elif target_node.op_type == "Gemm":
            new_weights = weights * scale
        new_biases = biases * scale.flatten() + bias
    elif direction == "forward":
        if target_node.op_type == "Conv":
            if is_depthwise:
                # Apply scale per channel for depthwise convolutions
                new_weights = weights * scale.reshape(-1, 1, 1, 1)
            else:
                new_weights = weights * scale.reshape(-1, 1, 1, 1)
        elif target_node.op_type == "Gemm":
            new_weights = weights * scale.reshape(1, -1)
        new_biases = biases * scale + bias
    else:
        raise ValueError(f"Invalid folding direction: {direction}")

    # Generate unique names for the new initializers
    new_weight_name = target_node.input[1] + "_folded"
    new_bias_name = (target_node.input[2] if len(target_node.input) > 2 else target_node.input[1] + "_bias") + "_folded"

    # Update weights and biases in the graph
    new_weight_initializer = numpy_helper.from_array(new_weights, new_weight_name)
    new_bias_initializer = numpy_helper.from_array(new_biases, new_bias_name)

    # Update the target node to use the new initializer names
    target_node.input[1] = new_weight_name
    if len(target_node.input) > 2:
        target_node.input[2] = new_bias_name
    else:
        target_node.input.append(new_bias_name)

    # Add new initializers
    nodes_to_add.append(new_weight_initializer)
    nodes_to_add.append(new_bias_initializer)


def _update_connections(graph, node_to_remove, preceding_node):
    """
    Update the connections in the graph to bypass a node being removed.

    Args:
        graph (onnx.GraphProto): The ONNX graph.
        node_to_remove (onnx.NodeProto): The node to remove.
        preceding_node (onnx.NodeProto): The preceding Conv or Gemm node.
    """
    if preceding_node is None:
        return

    # Replace all occurrences of the node's output with the preceding node's output
    node_output = node_to_remove.output[0]
    preceding_output = preceding_node.output[0]

    for node in graph.node:
        for i, input_name in enumerate(node.input):
            if input_name == node_output:
                node.input[i] = preceding_output


def _remove_unused_initializers(graph):
    """
    Remove unused initializers from the graph.

    Args:
        graph (onnx.GraphProto): The ONNX graph.
    """
    # Collect all used initializer names
    used_initializers = set()
    for node in graph.node:
        for input_name in node.input:
            used_initializers.add(input_name)

    # Remove initializers that are not used
    unused_initializers = [init for init in graph.initializer if init.name not in used_initializers]
    for init in unused_initializers:
        print(f"Removing unused initializer: {init.name}")
        graph.initializer.remove(init)


def _get_initializer(initializer_dict, name):
    """
    Retrieve an initializer from the dictionary, with error handling for missing initializers.

    Args:
        initializer_dict (dict): Dictionary of initializers.
        name (str): Name of the initializer to retrieve.

    Returns:
        np.ndarray: The initializer array.

    Raises:
        ValueError: If the initializer is not found.
    """
    if name not in initializer_dict:
        #print("name : ", name)
        #raise ValueError(f"Initializer '{name}' not found in the model.")
        return None
    return initializer_dict[name]