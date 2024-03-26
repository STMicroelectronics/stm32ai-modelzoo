# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2022 STMicroelectronics.
#  * All rights reserved.
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, UpSampling2D, ZeroPadding2D, Activation, Add, BatchNormalization, GlobalAveragePooling2D, Reshape, Concatenate, Lambda
from tensorflow.keras.layers import DepthwiseConv2D
from tensorflow.keras.regularizers import L2
from anchor_boxes_utils import gen_anchors
from anchor_boxes_utils import get_sizes_ratios_ssd_v2
from typing import Tuple, Dict, List, Optional

def bbox_predictor(fmap_channels, version, layer_in, n_anchors, n_offsets=4, kernel=(3, 3), l2_reg=0.0005, bn=False, dw=False):
    '''Bounding box prediction layer'''
    if version == 'v1':
        layer_in = cascade4Conv(layer_in,fmap_channels,l2_reg,bn)

    if kernel == (1, 1):
        layer_out = Conv2D(filters=n_anchors * n_offsets, kernel_size=kernel, strides=(1, 1), padding='same',
                           kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                           activation=None, data_format="channels_last")(layer_in)
        if bn:
            layer_out = BatchNormalization()(layer_out)
    else:
        if dw:
            layer_out = DepthwiseConv2D(kernel, padding='same', depth_multiplier=1,
                                        depthwise_initializer='he_normal', depthwise_regularizer=L2(l2_reg),
                                        activation=None, data_format="channels_last")(layer_in)
            if bn:
                layer_out = BatchNormalization()(layer_out)
            layer_out = Conv2D(filters=n_anchors * n_offsets, kernel_size=(1, 1), padding='same',
                               kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                               activation=None, data_format="channels_last")(layer_out)
            if bn:
                layer_out = BatchNormalization()(layer_out)
        else:
            layer_out = Conv2D(filters=n_anchors * n_offsets, kernel_size=kernel, strides=(1, 1), padding='same',
                               kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                               activation=None, data_format="channels_last")(layer_in)
            if bn:
                layer_out = BatchNormalization()(layer_out)

    return layer_out


def cls_predictor(fmap_channels, version, layer_in, n_anchors, n_classes, kernel=(3, 3), l2_reg=0.0005, bn=False, dw=False):
    '''Category prediction layer'''
    if version == 'v1':
        layer_in = cascade4Conv(layer_in,fmap_channels,l2_reg,bn)

    if kernel == (1, 1):
        layer_out = Conv2D(filters=n_anchors * (1 + n_classes), kernel_size=kernel, strides=(1, 1), padding='same',
                           kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                           activation=None, data_format="channels_last")(layer_in)
        if bn:
            layer_out = BatchNormalization()(layer_out)
    else:
        if dw:
            layer_out = DepthwiseConv2D(kernel, padding='same', depth_multiplier=1,
                                        depthwise_initializer='he_normal', depthwise_regularizer=L2(l2_reg),
                                        activation=None, data_format="channels_last")(layer_in)
            if bn:
                layer_out = BatchNormalization()(layer_out)
            layer_out = Conv2D(filters=n_anchors * (1 + n_classes), kernel_size=(1, 1), padding='same',
                               kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                               activation=None, data_format="channels_last")(layer_out)
            if bn:
                layer_out = BatchNormalization()(layer_out)
        else:
            layer_out = Conv2D(filters=n_anchors * (1 + n_classes), kernel_size=kernel, strides=(1, 1), padding='same',
                               kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                               activation=None, data_format="channels_last")(layer_in)
            if bn:
                layer_out = BatchNormalization()(layer_out)
    return layer_out


def cascade4Conv(input,fmap_channels,l2_reg,bn):
    output = Conv2D(fmap_channels, (3, 3), padding='same',kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg), activation=None, data_format="channels_last")(input)
    if bn:
        output = BatchNormalization()(output)
    output = Activation('relu6')(output)
    for _ in range(3):
        output = Conv2D(fmap_channels, (3, 3), padding='same',kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg), activation=None, data_format="channels_last")(output)
        if bn:
            output = BatchNormalization()(output)
        output = Activation('relu6')(output)
    return output

def cascade4DWConv(input,fmap_channels,l2_reg):
    output = dw_conv(input, n_filters=fmap_channels, kernel=(3, 3), strides=(1, 1), depth_multiplier=1, padding='same', l2_reg=l2_reg, activation='relu6', bn=True, dilation_rate=(1, 1))
    for _ in range(3):
        output = dw_conv(output, n_filters=fmap_channels, kernel=(3, 3), strides=(1, 1), depth_multiplier=1, padding='same', l2_reg=l2_reg, activation='relu6', bn=True, dilation_rate=(1, 1))
    return output

def fmap_forward(fmap_channels, version, fmap, img_width, img_height, sizes, ratios, clip_boxes, normalize, n_classes, kernel=(3, 3), l2_reg=0.0005, bn=False, dw=False):
    '''Get predictions from a feature map'''
    n_anchors = len(sizes) + len(ratios) - 1

    def fmap_lambda(fmap):
        return gen_anchors(fmap, img_width, img_height,sizes, ratios, clip=clip_boxes, normalize=normalize)
    anchors = fmap_lambda(fmap)

    cls_preds  = cls_predictor( fmap_channels, version, fmap, n_anchors=n_anchors, n_classes=n_classes, kernel=kernel, l2_reg=l2_reg, bn=bn, dw=dw)
    bbox_preds = bbox_predictor(fmap_channels, version, fmap, n_anchors=n_anchors, n_offsets=4,         kernel=kernel, l2_reg=l2_reg, bn=bn, dw=dw)

    anchorss = tf.tile(tf.expand_dims(anchors,0),(tf.shape(bbox_preds)[0],1,1,1,1))    
    
    return anchorss, cls_preds, bbox_preds

def dw_conv(layer_in, n_filters, kernel=(3, 3), strides=(1, 1), depth_multiplier=1,padding='same', l2_reg=0.0005, activation='relu', bn=True, dilation_rate=(1, 1)):
    '''
    Depthwise seperate convolution block
    '''
    layer_out = DepthwiseConv2D(kernel, padding=padding, strides=strides, depth_multiplier=depth_multiplier, dilation_rate=dilation_rate,
                                depthwise_initializer='he_normal', depthwise_regularizer=L2(l2_reg),
                                activation=None, data_format="channels_last")(layer_in)
    if bn:
        layer_out = BatchNormalization()(layer_out)
    layer_out = Conv2D(n_filters, (1, 1), padding=padding,
                       kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                       activation=None, data_format="channels_last")(layer_out)
    if bn:
        layer_out = BatchNormalization()(layer_out)
    layer_out = Activation(activation)(layer_out)
    return layer_out

def ssd_mobilenet_v2_fpnlite(l2_reg:float=0.00004, activation:str='relu6', bn_dw:bool=True,
                            bn_pred:bool=True, dw_pred:bool=False, clip_boxes:bool=False,
                            normalize:bool=True, input_shape:Tuple[int,int,int]=None,
                            class_names:List[str]=None, model_alpha:Dict=None,
                            pretrained_weights:bool=False,
                            version:str='v2',head_type:str='fpn-lite') -> tf.keras.Model:
    '''
    Define a Single Shot Detection (SSD)-MobileNetV1 or V2 model for object detection.

    Args:
        l2_reg: L2 regularization factor.
        activation: Activation function.
        bn_dw: Whether to use Batch Normalization for dw_conv.
        bn_pred: Whether to use Batch Normalization for prediction layers.
        dw_pred: Whether to use DepthWise convolution for prediction layers.
        clip_boxes: Whether to clip box coordinates to image boundaries.
        normalize: Whether to normalize bounding box coordinates.
        input_shape: Input shape of the model.
        class_names: List of class names.
        model_alpha: Model alpha.
        pretrained_weights: 'imagenet' or None
        version: string for MobileNet version 'v1' or 'v2'.
        head_type: type of head to use, either 'fpn-lite' or 'fpn'

    Returns:
        model: SSD-style model.
    '''

    #feature map sizes, if FPN head is choosen then the number of filters per convolution layer is doubled compared to the FPN-Lite head
    if head_type == 'fpn':
        fmap_channels = 256
    elif head_type == 'fpn-lite':
        fmap_channels = 128

    n_classes = len(class_names)
    img_width = input_shape[0]
    img_height = input_shape[1]
    img_channels = input_shape[2]
    inp_shape = (img_height, img_width, img_channels)

    # Load MobileNet-V1 backbones pretrained on ImageNet
    ####################################################################################

    if version=='v1':
        base_model = tf.keras.applications.MobileNet(inp_shape,
                                                     alpha=model_alpha,
                                                     include_top=False,
                                                     weights=pretrained_weights)
    elif version=='v2':
        base_model = tf.keras.applications.MobileNetV2(inp_shape,
                                                       alpha=model_alpha,
                                                       include_top=False,
                                                       weights=pretrained_weights)


    sizes, ratios = get_sizes_ratios_ssd_v2(inp_shape)
    

    # Block before prediction head (FPN or FPN-Lite) for MobileNetV1 & V2
    ####################################################################################

    if version == 'v1':
        ### Get output layers for MobileNetV1
        fmap_0 = base_model.get_layer('conv_pw_5_relu').output # (32, 32)
        fmap_1 = base_model.get_layer('conv_pw_11_relu').output # (16, 16)
        x      = base_model.get_layer('conv_pw_13_relu').output # (8, 8)
    elif version=='v2':
        ### Get output layers for MobileNetV2
        fmap_0 = base_model.get_layer('block_5_add').output # (32, 32)
        fmap_1 = base_model.get_layer('block_12_add').output # (16, 16)
        x      = base_model.get_layer('out_relu').output # (8, 8)

    fmap_0 = Conv2D(fmap_channels, (1, 1), padding='same',
                    kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                    activation= None, data_format="channels_last")(fmap_0)
    fmap_0 = BatchNormalization()(fmap_0)
    ###Get the second feature map from MobileNet
    fmap_1 = Conv2D(fmap_channels, (1, 1), padding='same',
                    kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                    activation= None, data_format="channels_last")(fmap_1)
    fmap_1 = BatchNormalization()(fmap_1)
    


    x = Conv2D(fmap_channels, (1, 1), padding='same',
                    kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                    activation= None, data_format="channels_last")(x)
    x = BatchNormalization()(x)


    fmap_2_up_1 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(x)
    fmap_1 = Add(name='fmap_1')([fmap_1,fmap_2_up_1])


    if head_type == 'fpn':
        fmap_1 = Conv2D(fmap_channels, (3, 3), padding='same',kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),activation=None, data_format="channels_last")(fmap_1)
        fmap_1 = BatchNormalization()(fmap_1)
        fmap_1 = Activation('relu6')(fmap_1)
    elif head_type == 'fpn-lite':
        fmap_1 = dw_conv(fmap_1, n_filters=fmap_channels, kernel=(3, 3), strides=(1, 1), depth_multiplier=1, padding='same', l2_reg=l2_reg, activation='relu6', bn=True, dilation_rate=(1, 1))


    fmap_1_up_0 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_1)
    fmap_0 = Add(name='fmap_0')([fmap_0,fmap_1_up_0])


    fmap_sizes = []
    anchors, cls_preds, bbox_preds = [], [], []
    n_anchors  = []
    cls_preds  = []
    bbox_preds = []
    anchors    = []
    

    if head_type == 'fpn':
        fmap_0 = Conv2D(fmap_channels, (3, 3), padding='same', strides=(1, 1), kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),activation= None, data_format="channels_last")(fmap_0)
        fmap_0 = BatchNormalization()(fmap_0)
        fmap_0 = Activation('relu6')(fmap_0)
        fmap_3 = Conv2D(fmap_channels, (3, 3), padding='same', strides=(2, 2), kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),activation= None, data_format="channels_last")(x)
        fmap_3 = BatchNormalization()(fmap_3)
        fmap_3 = Activation('relu6')(fmap_3)
        fmap_4 = Conv2D(fmap_channels, (3, 3), padding='same', strides=(2, 2), kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),activation= None, data_format="channels_last")(fmap_3)
        fmap_4 = BatchNormalization()(fmap_4)
        fmap_4 = Activation('relu6')(fmap_4)

        layers_list = [fmap_0,fmap_1,x,fmap_3,fmap_4]

    elif head_type == 'fpn-lite':
        fmap_0 = dw_conv(fmap_0, n_filters=fmap_channels, kernel=(3, 3), strides=(1, 1), depth_multiplier=1, padding='same', l2_reg=l2_reg, activation='relu6', bn=True, dilation_rate=(1, 1))
        fmap_3 = dw_conv(x     , n_filters=fmap_channels, kernel=(3, 3), strides=(2, 2), depth_multiplier=1, padding='same', l2_reg=l2_reg, activation='relu6', bn=True, dilation_rate=(1, 1))
        fmap_4 = dw_conv(fmap_3, n_filters=fmap_channels, kernel=(3, 3), strides=(2, 2), depth_multiplier=1, padding='same', l2_reg=l2_reg, activation='relu6', bn=True, dilation_rate=(1, 1))

        fmap_0_bis = cascade4DWConv(fmap_0,fmap_channels,l2_reg)
        fmap_1_bis = cascade4DWConv(fmap_1,fmap_channels,l2_reg)
        fmap_2_bis = cascade4DWConv(x,     fmap_channels,l2_reg)
        fmap_3_bis = cascade4DWConv(fmap_3,fmap_channels,l2_reg)
        fmap_4_bis = cascade4DWConv(fmap_4,fmap_channels,l2_reg)

        layers_list = [fmap_0_bis,fmap_1_bis,fmap_2_bis,fmap_3_bis,fmap_4_bis]


    ####################################################################################


    for i in range(len(layers_list)):

        fmap_sizes.append((int(layers_list[i].shape[1]), int(layers_list[i].shape[2]),))
        if head_type == 'fpn':
            anchors_i, cls_preds_i, bbox_preds_i = fmap_forward(fmap_channels, version, layers_list[i], img_width, img_height, sizes[i], ratios[i],clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=False)
        elif head_type == 'fpn-lite':
            anchors_i, cls_preds_i, bbox_preds_i = fmap_forward(fmap_channels, version, layers_list[i], img_width, img_height, sizes[i], ratios[i],clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=True)

        anchors.append(anchors_i)
        cls_preds.append(cls_preds_i)
        bbox_preds.append(bbox_preds_i)

        n_anchors.append(int(layers_list[i].shape[1]) * int(layers_list[i].shape[2]) * (len(sizes[i]) + len(ratios[i]) - 1))

        cls_preds[-1]  = Reshape((n_anchors[-1], n_classes+1))(cls_preds[-1])
        bbox_preds[-1] = Reshape((n_anchors[-1], 4))(bbox_preds[-1])
        anchors[-1]    = Reshape((n_anchors[-1], 4))(anchors[-1])



    ### Concatenate for all anchor boxes
    anchors = Concatenate(axis=1, name="anchors_concat")(anchors)
    cls_preds = Concatenate(axis=1, name="classes_concat")(cls_preds)
    bbox_preds = Concatenate(axis=1, name="bboxes_concat")(bbox_preds)

    cls_softmax = Activation('softmax', name='classes_softmax')(cls_preds)

    ### Final predictions for all anchor boxes
    predictions = Concatenate(axis=2, name='predictions')([cls_softmax, bbox_preds, anchors])

    training_model = Model(inputs=base_model.input, outputs=predictions)
    inference_model = Model(inputs=base_model.input, outputs=[cls_softmax, bbox_preds, anchors])
    

    return inference_model, training_model, fmap_sizes