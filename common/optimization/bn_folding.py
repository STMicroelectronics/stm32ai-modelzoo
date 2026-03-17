# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np


def _fold_batch_norm(weights, bias, gamma, beta, moving_mean, moving_var, epsilon, layer_type):
    """
         Implements equation for Backward BN weights folding.
         Args:
              weights: original weights
              bias: original bias
              gamma: multiplicative trainable parameter of the batch normalisation. Per-channel
              beta: additive trainable parameter of the batch normalisation. Per-channel
              moving_mean: moving average of the layer output. Used for centering the samples distribution after
              batch normalisation
              moving_var: moving variance of the layer output. Used for reducing the samples distribution
              epsilon: a small number to void dividing by 0
              layer_type: layer type (dense, conv2d or depthwiseconv2d)
         Returns: folded weights and bias
    """
    if bias is None:
        bias = np.zeros_like(moving_mean)
    std = np.sqrt(moving_var + epsilon)
    if layer_type == 'Conv2D':
        new_weights = weights * (gamma / std)
        new_bias = beta + (bias - moving_mean) * (gamma / std)
    elif layer_type == 'DepthwiseConv2D':
        gamma_std = (gamma / std).reshape(1, 1, -1, 1)
        new_weights = weights * gamma_std
        new_bias = beta + (bias - moving_mean) * (gamma / std)
    elif layer_type == 'Dense':
        new_weights = weights * (gamma / std)
        new_bias = beta + (bias - moving_mean) * (gamma / std)
    else:
        raise ValueError("Unsupported layer type for BN folding.")
    return new_weights, new_bias


def fold_bn(model):
    """
        Search for BN to fold in Backward direction and fold them with _fold_batch_norm function

        Args:
            model: input keras model

        Returns: a new keras model, with BN folded in backward direction
    """
    
    # Map from original layer name to new layer instance
    new_layers = {}
    # Map from original tensor id to new tensor
    tensor_map = {}

    # Create new Input layers
    for input_tensor in model.inputs:
        new_input = layers.Input(shape=input_tensor.shape[1:], name=input_tensor.name.split(":")[0])
        tensor_map[id(input_tensor)] = new_input

    # layer name list
    layer_name_list = [layer.name for layer in model.layers]

    # Build a mapping from tensor id to producing layer name
    tensor_id_to_layer_name = {}
    # model.operations rather than model.layers to have operators in the list
    for layer in model.operations: #model.layers:
        for node in layer._inbound_nodes:
            for t in node.output_tensors:
                tensor_id_to_layer_name[id(t)] = layer.name

    # Track which BN layers are folded (to skip them)
    folded_bn_layers = set()

    # Traverse layers in order
    # model.operations rather than model.layers to have operators in the list
    for layer in model.operations: #model.layers:
        if isinstance(layer, layers.InputLayer):
            continue

        # Get input tensors for this layer
        inbound_tensors = []
        for node in layer._inbound_nodes:
            for t in node.input_tensors:
                inbound_tensors.append(tensor_map.get(id(t), t))
        if not inbound_tensors:
            continue
        inbound = inbound_tensors[0] if len(inbound_tensors) == 1 else inbound_tensors

        # Check if this layer is foldable and is immediately followed by BN
        is_foldable = isinstance(layer, (layers.Conv2D, layers.DepthwiseConv2D, layers.Dense))
        # Find if any layer takes this layer's output as input and is BN
        next_bn_layer = None

        for out_node in layer._outbound_nodes:
            if isinstance(out_node.operation, layers.BatchNormalization):
                next_bn_layer = out_node.operation
                break

        if is_foldable and next_bn_layer and next_bn_layer.name not in folded_bn_layers:
            # Fold BN
            weights = layer.get_weights()
            W = weights[0]
            b = weights[1] if len(weights) > 1 else None
            gamma, beta, moving_mean, moving_var = next_bn_layer.get_weights()
            epsilon = next_bn_layer.epsilon
            if isinstance(layer, layers.Conv2D):
                W_shape = W.shape
                W = W.reshape(-1, W_shape[-1])
                new_W, new_b = _fold_batch_norm(W, b, gamma, beta, moving_mean, moving_var, epsilon, 'Conv2D')
                new_W = new_W.reshape(W_shape)
            elif isinstance(layer, layers.DepthwiseConv2D):
                new_W, new_b = _fold_batch_norm(W, b, gamma, beta, moving_mean, moving_var, epsilon, 'DepthwiseConv2D')
            elif isinstance(layer, layers.Dense):
                new_W, new_b = _fold_batch_norm(W, b, gamma, beta, moving_mean, moving_var, epsilon, 'Dense')
            else:
                raise ValueError("Unsupported layer type for BN folding.")

            # Create new layer with folded weights
            config = layer.get_config()
            config['use_bias'] = True
            new_layer = type(layer).from_config(config)
            x = new_layer(inbound)
            new_layer.set_weights([new_W, new_b])
            new_layers[layer.name] = new_layer

            # Map BN's output tensor to this new output
            for node in next_bn_layer._inbound_nodes:
                for t in node.output_tensors:
                    tensor_map[id(t)] = x
            folded_bn_layers.add(next_bn_layer.name)
        elif layer.name in folded_bn_layers:
            # This is a BN layer that was already folded, skip it
            continue
        elif layer.name not in layer_name_list:
            # Keras or TF ops and not type Layers
            if isinstance(inbound, list):
                if len(inbound) == 2:
                    x = layer(inbound[0], inbound[1])
            else:
                x = layer(inbound)
            new_layers[layer.name] = layer
            # Map this layer's output tensors
            for node in layer._inbound_nodes:
                for t in node.output_tensors:
                    tensor_map[id(t)] = x
        else:
            # Just recreate the layer
            config = layer.get_config()
            new_layer = type(layer).from_config(config)
            x = new_layer(inbound)
            if layer.get_weights():
                new_layer.set_weights(layer.get_weights())
            new_layers[layer.name] = new_layer
            # Map this layer's output tensors
            for node in layer._inbound_nodes:
                for t in node.output_tensors:
                    tensor_map[id(t)] = x

    # Build new model
    new_outputs = [tensor_map[id(out)] for out in model.outputs]
    new_inputs = [tensor_map[id(inp)] for inp in model.inputs]
    new_model = models.Model(inputs=new_inputs, outputs=new_outputs)
    return new_model