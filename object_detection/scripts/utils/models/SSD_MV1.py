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
from anchor_boxes_utils import get_sizes_ratios


def bbox_predictor(layer_in, n_anchors, n_offsets=4, kernel=(
        3, 3), l2_reg=0.0005, bn=False, dw=False):
    '''Bounding box prediction layer'''
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


def cls_predictor(layer_in, n_anchors, n_classes, kernel=(
        3, 3), l2_reg=0.0005, bn=False, dw=False):
    '''Category prediction layer'''
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


def fmap_forward(fmap, img_width, img_height, sizes, ratios, clip_boxes,
                 normalize, n_classes, kernel=(3, 3), l2_reg=0.0005, bn=False, dw=False):
    '''Get predictions from a feature map'''
    n_anchors = len(sizes) + len(ratios) - 1

    def fmap_lambda(fmap):
        return gen_anchors(fmap, img_width, img_height,sizes, ratios, clip=clip_boxes, normalize=normalize)
    anchors = Lambda(fmap_lambda)(fmap)
    cls_preds = cls_predictor(
        fmap, n_anchors=n_anchors, n_classes=n_classes, kernel=kernel, l2_reg=l2_reg, bn=bn, dw=dw)
    bbox_preds = bbox_predictor(
        fmap, n_anchors=n_anchors, n_offsets=4, kernel=kernel, l2_reg=l2_reg, bn=bn, dw=dw)
    return anchors, cls_preds, bbox_preds


def dw_conv(layer_in, n_filters, kernel=(3, 3), strides=(1, 1), depth_multiplier=1,
            padding='same', l2_reg=0.0005, activation='relu', bn=True, dilation_rate=(1, 1)):
    '''
    Depthwise seperate convolution block
    '''
    layer_out = DepthwiseConv2D(kernel, padding=padding, strides=strides, depth_multiplier=depth_multiplier, dilation_rate=dilation_rate,
                                depthwise_initializer='he_normal', depthwise_regularizer=L2(l2_reg),
                                activation=None, data_format="channels_last")(layer_in)
    if bn:
        layer_out = BatchNormalization()(layer_out)
    layer_out = Activation(activation)(layer_out)
    layer_out = Conv2D(n_filters, (1, 1), padding=padding,
                       kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                       activation=None, data_format="channels_last")(layer_out)
    if bn:
        layer_out = BatchNormalization()(layer_out)
    layer_out = Activation(activation)(layer_out)
    return layer_out


def ssd_model(cfg, l2_reg=0.0005, activation='relu6', bn_dw=True,bn_pred=True, dw_pred=False,clip_boxes=False,normalize=True):
    '''
    Define a SSD-style model
    Arguments:
        l2_reg: L2 regulization
        activation: activation function
        bn_dw: using Batch Normalization for dw_conv
        bn_pred: using Batch Normalization for prediction layers
        dw_pred: using DepthWise convolution for prediction layers
        fmap_channels: number of channels of feature maps
    Return:
        model: SSD-style model
    '''
    #feature map sizes
    fmap_channels = 32
    n_classes = len(cfg.dataset.class_names)
    img_width = cfg.model.input_shape[0]
    img_height = cfg.model.input_shape[1]
    img_channels = cfg.model.input_shape[2]
    inp_shape = (img_height, img_width, img_channels)
    # Load MobileNet-V1 pretrained on ImageNet
    assert cfg.model.input_shape[0] in [256,224,192],"only the following input sizes are supported[256,224,192] "
    if cfg.model.transfer_learning == True:
        base_model = tf.keras.applications.MobileNet(inp_shape,
                                                   alpha=cfg.model.model_type.alpha,
                                                   include_top=False,
                                                   weights='imagenet')
    else:
        base_model = tf.keras.applications.MobileNet(inp_shape,
                                                    alpha=cfg.model.model_type.alpha,
                                                    include_top=False, weights=None)
    sizes,ratios = get_sizes_ratios(cfg)

    if cfg.model.input_shape[0] == 192:
        ###Get the first feature map from MobileNet
        fmap_0 = base_model.get_layer('conv_pw_5_relu').output # (24, 24)
        fmap_0 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(fmap_0)
        fmap_0 = BatchNormalization()(fmap_0)
        ###Get the second feature map from MobileNet
        fmap_1 = base_model.get_layer('conv_pw_11_relu').output # (12, 12)
        fmap_1 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(fmap_1)
        fmap_1 = BatchNormalization()(fmap_1)
        ###Get the third feature map from MobileNet
        x = base_model.get_layer('conv_pw_13_relu').output # (6, 6)
        fmap_2 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_2 = BatchNormalization()(fmap_2)
        ###Add some extra convolution layers for additional feature maps
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(2, 2),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(1, 1),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))

        fmap_3 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_3 = BatchNormalization()(fmap_3) # (3, 3)

        x = GlobalAveragePooling2D()(x)

        x = Reshape((1, 1, int(x.shape[1])))(x)

        ###Integrate Feature Pyramid Network (https://arxiv.org/pdf/1612.03144.pdf)
        ### Feature map 4
        fmap_4 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x) # (1, 1)
        fmap_4 = BatchNormalization(name="fmap_4")(fmap_4)

        fmap_4_size = (int(fmap_4.shape[1]), int(fmap_4.shape[2]),)
        anchors_4, cls_preds_4, bbox_preds_4 = fmap_forward(fmap_4, img_width, img_height, sizes[4], ratios[4],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_4 = int(fmap_4.shape[1]) * int(fmap_4.shape[2]) * (len(sizes[4]) + len(ratios[4]) - 1)
        cls_preds_4 = Reshape((n_anchors_4, n_classes+1))(cls_preds_4)
        bbox_preds_4 = Reshape((n_anchors_4, 4))(bbox_preds_4)
        anchors_4 = Reshape((n_anchors_4, 4))(anchors_4)

        ### Feature map 3
        fmap_4_up_3 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_4)
        fmap_4_up_3 = ZeroPadding2D(padding=((1, 0), (1, 0)))(fmap_4_up_3) # (3, 3)
        fmap_3 = Add(name='fmap_3')([fmap_3, fmap_4_up_3]) # (3, 3)

        fmap_3_size = (int(fmap_3.shape[1]), int(fmap_3.shape[2]),)
        anchors_3, cls_preds_3, bbox_preds_3 = fmap_forward(fmap_3, img_width, img_height, sizes[3], ratios[3],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_3 = int(fmap_3.shape[1]) * int(fmap_3.shape[2]) * (len(sizes[3]) + len(ratios[3]) - 1)
        cls_preds_3 = Reshape((n_anchors_3, n_classes+1))(cls_preds_3)
        bbox_preds_3 = Reshape((n_anchors_3, 4))(bbox_preds_3)
        anchors_3 = Reshape((n_anchors_3, 4))(anchors_3)

        ### Feature map 2
        fmap_3_up_2 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_3)
        fmap_2 = Add(name='fmap_2')([fmap_2, fmap_3_up_2]) # (6, 6)

        fmap_2_size = (int(fmap_2.shape[1]), int(fmap_2.shape[2]),)
        anchors_2, cls_preds_2, bbox_preds_2 = fmap_forward(fmap_2, img_width, img_height, sizes[2], ratios[2],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_2 = int(fmap_2.shape[1]) * int(fmap_2.shape[2]) * (len(sizes[2]) + len(ratios[2]) - 1)
        cls_preds_2 = Reshape((n_anchors_2, n_classes+1))(cls_preds_2)
        bbox_preds_2 = Reshape((n_anchors_2, 4))(bbox_preds_2)
        anchors_2 = Reshape((n_anchors_2, 4))(anchors_2)

        ### Feature map 1
        fmap_2_up_1 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_2)
        fmap_1 = Add(name='fmap_1')([fmap_1, fmap_2_up_1]) # (12, 12)

        fmap_1_size = (int(fmap_1.shape[1]), int(fmap_1.shape[2]),)
        anchors_1, cls_preds_1, bbox_preds_1 = fmap_forward(fmap_1, img_width, img_height, sizes[1], ratios[1],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_1 = int(fmap_1.shape[1]) * int(fmap_1.shape[2]) * (len(sizes[1]) + len(ratios[1]) - 1)
        cls_preds_1 = Reshape((n_anchors_1, n_classes+1))(cls_preds_1)
        bbox_preds_1 = Reshape((n_anchors_1, 4))(bbox_preds_1)
        anchors_1 = Reshape((n_anchors_1, 4))(anchors_1)

        ### Feature map 0
        fmap_1_up_0 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_1)
        fmap_0 = Add(name='fmap_0')([fmap_0, fmap_1_up_0]) # (24, 24)

        fmap_0_size = (int(fmap_0.shape[1]), int(fmap_0.shape[2]),)
        anchors_0, cls_preds_0, bbox_preds_0 = fmap_forward(fmap_0, img_width, img_height, sizes[0], ratios[0],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_0 = int(fmap_0.shape[1]) * int(fmap_0.shape[2]) * (len(sizes[0]) + len(ratios[0]) - 1)
        cls_preds_0 = Reshape((n_anchors_0, n_classes+1))(cls_preds_0)
        bbox_preds_0 = Reshape((n_anchors_0, 4))(bbox_preds_0)
        anchors_0 = Reshape((n_anchors_0, 4))(anchors_0)

        ### Concatenate for all anchor boxes
        anchors = Concatenate(axis=1, name="anchors_concat")([anchors_0, anchors_1, anchors_2, anchors_3, anchors_4])
        cls_preds = Concatenate(axis=1, name="classes_concat")([cls_preds_0, cls_preds_1, cls_preds_2, cls_preds_3, cls_preds_4])
        bbox_preds = Concatenate(axis=1, name="bboxes_concat")([bbox_preds_0, bbox_preds_1, bbox_preds_2, bbox_preds_3, bbox_preds_4])

        cls_softmax = Activation('softmax', name='classes_softmax')(cls_preds)

        ### Final predictions for all anchor boxes
        predictions = Concatenate(axis=2, name='predictions')([cls_softmax, bbox_preds, anchors])

        model = Model(inputs=base_model.input, outputs=predictions)

        fmap_sizes = []
        fmap_sizes.append(fmap_0_size)
        fmap_sizes.append(fmap_1_size)
        fmap_sizes.append(fmap_2_size)
        fmap_sizes.append(fmap_3_size)
        fmap_sizes.append(fmap_4_size)

        return model, fmap_sizes

    elif cfg.model.input_shape[0] == 224:
        ###Get the first feature map from MobileNet
        fmap_0 = base_model.get_layer('conv_pw_5_relu').output # (28, 28)
        fmap_0 = ZeroPadding2D(padding=(2, 2))(fmap_0) # (32, 32)
        fmap_0 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(fmap_0)
        fmap_0 = BatchNormalization()(fmap_0)
        ###Get the second feature map from MobileNet
        fmap_1 = base_model.get_layer('conv_pw_11_relu').output # (14, 14)
        fmap_1 = ZeroPadding2D(padding=(1, 1))(fmap_1) # (16, 16)
        fmap_1 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(fmap_1)
        fmap_1 = BatchNormalization()(fmap_1)
        ###Get the third feature map from MobileNet
        x = base_model.get_layer('conv_pw_13_relu').output # (7, 7)
        x = ZeroPadding2D(padding=((1, 0), (1, 0)))(x) # (8, 8)
        fmap_2 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_2 = BatchNormalization()(fmap_2)
        ###Add some extra convolution layers for additional feature maps
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(2, 2),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(1, 1),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))

        fmap_3 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_3 = BatchNormalization()(fmap_3)
        ###Add some extra convolution layers for additional feature maps
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(2, 2),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(1, 1),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))

        fmap_4 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_4 = BatchNormalization()(fmap_4)

        x = GlobalAveragePooling2D()(x)

        x = Reshape((1, 1, int(x.shape[1])))(x)

        ###Integrate Feature Pyramid Network (https://arxiv.org/pdf/1612.03144.pdf)
        ### Feature map 5
        fmap_5 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x) # (1, 1)
        fmap_5 = BatchNormalization(name="fmap_5")(fmap_5)

        fmap_5_size = (int(fmap_5.shape[1]), int(fmap_5.shape[2]),)
        anchors_5, cls_preds_5, bbox_preds_5 = fmap_forward(fmap_5, img_width, img_height, sizes[5], ratios[5],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(1,1), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_5 = int(fmap_5.shape[1]) * int(fmap_5.shape[2]) * (len(sizes[5]) + len(ratios[5]) - 1)
        cls_preds_5 = Reshape((n_anchors_5, n_classes+1))(cls_preds_5)
        bbox_preds_5 = Reshape((n_anchors_5, 4))(bbox_preds_5)
        anchors_5 = Reshape((n_anchors_5, 4))(anchors_5)

        ### Feature map 4
        fmap_5_up_4 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_5)
        fmap_4 = Add(name='fmap_4')([fmap_4, fmap_5_up_4]) # (2, 2)

        fmap_4_size = (int(fmap_4.shape[1]), int(fmap_4.shape[2]),)
        anchors_4, cls_preds_4, bbox_preds_4 = fmap_forward(fmap_4, img_width, img_height, sizes[4], ratios[4],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_4 = int(fmap_4.shape[1]) * int(fmap_4.shape[2]) * (len(sizes[4]) + len(ratios[4]) - 1)
        cls_preds_4 = Reshape((n_anchors_4, n_classes+1))(cls_preds_4)
        bbox_preds_4 = Reshape((n_anchors_4, 4))(bbox_preds_4)
        anchors_4 = Reshape((n_anchors_4, 4))(anchors_4)

        ### Feature map 3
        fmap_4_up_3 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_4)
        fmap_3 = Add(name='fmap_3')([fmap_3, fmap_4_up_3]) # (4, 4)

        fmap_3_size = (int(fmap_3.shape[1]), int(fmap_3.shape[2]),)
        anchors_3, cls_preds_3, bbox_preds_3 = fmap_forward(fmap_3, img_width, img_height, sizes[3], ratios[3],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_3 = int(fmap_3.shape[1]) * int(fmap_3.shape[2]) * (len(sizes[3]) + len(ratios[3]) - 1)
        cls_preds_3 = Reshape((n_anchors_3, n_classes+1))(cls_preds_3)
        bbox_preds_3 = Reshape((n_anchors_3, 4))(bbox_preds_3)
        anchors_3 = Reshape((n_anchors_3, 4))(anchors_3)

        ### Feature map 2
        fmap_3_up_2 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_3)
        fmap_2 = Add(name='fmap_2')([fmap_2, fmap_3_up_2]) # (8, 8)

        fmap_2_size = (int(fmap_2.shape[1]), int(fmap_2.shape[2]),)
        anchors_2, cls_preds_2, bbox_preds_2 = fmap_forward(fmap_2, img_width, img_height, sizes[2], ratios[2],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_2 = int(fmap_2.shape[1]) * int(fmap_2.shape[2]) * (len(sizes[2]) + len(ratios[2]) - 1)
        cls_preds_2 = Reshape((n_anchors_2, n_classes+1))(cls_preds_2)
        bbox_preds_2 = Reshape((n_anchors_2, 4))(bbox_preds_2)
        anchors_2 = Reshape((n_anchors_2, 4))(anchors_2)

        ### Feature map 1
        fmap_2_up_1 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_2)
        fmap_1 = Add(name='fmap_1')([fmap_1, fmap_2_up_1]) # (16, 16)

        fmap_1_size = (int(fmap_1.shape[1]), int(fmap_1.shape[2]),)
        anchors_1, cls_preds_1, bbox_preds_1 = fmap_forward(fmap_1, img_width, img_height, sizes[1], ratios[1],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_1 = int(fmap_1.shape[1]) * int(fmap_1.shape[2]) * (len(sizes[1]) + len(ratios[1]) - 1)
        cls_preds_1 = Reshape((n_anchors_1, n_classes+1))(cls_preds_1)
        bbox_preds_1 = Reshape((n_anchors_1, 4))(bbox_preds_1)
        anchors_1 = Reshape((n_anchors_1, 4))(anchors_1)

        ### Feature map 0
        fmap_1_up_0 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_1)
        fmap_0 = Add(name='fmap_0')([fmap_0, fmap_1_up_0]) # (32, 32)

        fmap_0_size = (int(fmap_0.shape[1]), int(fmap_0.shape[2]),)
        anchors_0, cls_preds_0, bbox_preds_0 = fmap_forward(fmap_0, img_width, img_height, sizes[0], ratios[0],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_0 = int(fmap_0.shape[1]) * int(fmap_0.shape[2]) * (len(sizes[0]) + len(ratios[0]) - 1)
        cls_preds_0 = Reshape((n_anchors_0, n_classes+1))(cls_preds_0)
        bbox_preds_0 = Reshape((n_anchors_0, 4))(bbox_preds_0)
        anchors_0 = Reshape((n_anchors_0, 4))(anchors_0)

        ### Concatenate for all anchor boxes
        anchors = Concatenate(axis=1, name="anchors_concat")([anchors_0, anchors_1, anchors_2, anchors_3, anchors_4, anchors_5])
        cls_preds = Concatenate(axis=1, name="classes_concat")([cls_preds_0, cls_preds_1, cls_preds_2, cls_preds_3, cls_preds_4, cls_preds_5])
        bbox_preds = Concatenate(axis=1, name="bboxes_concat")([bbox_preds_0, bbox_preds_1, bbox_preds_2, bbox_preds_3, bbox_preds_4, bbox_preds_5])

        cls_softmax = Activation('softmax', name='classes_softmax')(cls_preds)

        ### Final predictions for all anchor boxes
        predictions = Concatenate(axis=2, name='predictions')([cls_softmax, bbox_preds, anchors])

        model = Model(inputs=base_model.input, outputs=predictions)

        fmap_sizes = []
        fmap_sizes.append(fmap_0_size)
        fmap_sizes.append(fmap_1_size)
        fmap_sizes.append(fmap_2_size)
        fmap_sizes.append(fmap_3_size)
        fmap_sizes.append(fmap_4_size)
        fmap_sizes.append(fmap_5_size)

        return model, fmap_sizes
    else:
        ###Get the first feature map from MobileNet
        fmap_0 = base_model.get_layer('conv_pw_5_relu').output # (32, 32)
        fmap_0 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(fmap_0)
        fmap_0 = BatchNormalization()(fmap_0)
        ###Get the second feature map from MobileNet
        fmap_1 = base_model.get_layer('conv_pw_11_relu').output # (16, 16)
        fmap_1 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(fmap_1)
        fmap_1 = BatchNormalization()(fmap_1)
        ###Get the third feature map from MobileNet
        x = base_model.get_layer('conv_pw_13_relu').output # (8, 8)
        fmap_2 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_2 = BatchNormalization()(fmap_2)
        ###Add some extra convolution layers for additional feature maps
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(2, 2),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(1, 1),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))

        fmap_3 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_3 = BatchNormalization()(fmap_3)

        ###Add some extra convolution layers for additional feature maps
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(2, 2),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))
        x = dw_conv(x, n_filters=256, kernel=(3,3), strides=(1, 1),
                    depth_multiplier=1, padding='same', l2_reg=l2_reg, activation=activation, bn=bn_dw, dilation_rate=(1, 1))

        fmap_4 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x)
        fmap_4 = BatchNormalization()(fmap_4)

        x = GlobalAveragePooling2D()(x)

        x = Reshape((1, 1, int(x.shape[1])))(x)

        ###Integrate Feature Pyramid Network (https://arxiv.org/pdf/1612.03144.pdf)
        ### Feature map 5
        fmap_5 = Conv2D(fmap_channels, (1, 1), padding='same',
                        kernel_initializer='he_normal', kernel_regularizer=L2(l2_reg),
                        activation= None, data_format="channels_last")(x) # (1, 1)
        fmap_5 = BatchNormalization(name="fmap_5")(fmap_5)

        fmap_5_size = (int(fmap_5.shape[1]), int(fmap_5.shape[2]),)
        anchors_5, cls_preds_5, bbox_preds_5 = fmap_forward(fmap_5, img_width, img_height, sizes[5], ratios[5],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(1,1), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_5 = int(fmap_5.shape[1]) * int(fmap_5.shape[2]) * (len(sizes[5]) + len(ratios[5]) - 1)
        cls_preds_5 = Reshape((n_anchors_5, n_classes+1))(cls_preds_5)
        bbox_preds_5 = Reshape((n_anchors_5, 4))(bbox_preds_5)
        anchors_5 = Reshape((n_anchors_5, 4))(anchors_5)

        ### Feature map 4
        fmap_5_up_4 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_5)
        fmap_4 = Add(name='fmap_4')([fmap_4, fmap_5_up_4]) # (2, 2)

        fmap_4_size = (int(fmap_4.shape[1]), int(fmap_4.shape[2]),)
        anchors_4, cls_preds_4, bbox_preds_4 = fmap_forward(fmap_4, img_width, img_height, sizes[4], ratios[4],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_4 = int(fmap_4.shape[1]) * int(fmap_4.shape[2]) * (len(sizes[4]) + len(ratios[4]) - 1)
        cls_preds_4 = Reshape((n_anchors_4, n_classes+1))(cls_preds_4)
        bbox_preds_4 = Reshape((n_anchors_4, 4))(bbox_preds_4)
        anchors_4 = Reshape((n_anchors_4, 4))(anchors_4)

        ### Feature map 3
        fmap_4_up_3 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_4)
        fmap_3 = Add(name='fmap_3')([fmap_3, fmap_4_up_3]) # (4, 4)

        fmap_3_size = (int(fmap_3.shape[1]), int(fmap_3.shape[2]),)
        anchors_3, cls_preds_3, bbox_preds_3 = fmap_forward(fmap_3, img_width, img_height, sizes[3], ratios[3],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_3 = int(fmap_3.shape[1]) * int(fmap_3.shape[2]) * (len(sizes[3]) + len(ratios[3]) - 1)
        cls_preds_3 = Reshape((n_anchors_3, n_classes+1))(cls_preds_3)
        bbox_preds_3 = Reshape((n_anchors_3, 4))(bbox_preds_3)
        anchors_3 = Reshape((n_anchors_3, 4))(anchors_3)

        ### Feature map 2
        fmap_3_up_2 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_3)
        fmap_2 = Add(name='fmap_2')([fmap_2, fmap_3_up_2]) # (8, 8)

        fmap_2_size = (int(fmap_2.shape[1]), int(fmap_2.shape[2]),)
        anchors_2, cls_preds_2, bbox_preds_2 = fmap_forward(fmap_2, img_width, img_height, sizes[2], ratios[2],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_2 = int(fmap_2.shape[1]) * int(fmap_2.shape[2]) * (len(sizes[2]) + len(ratios[2]) - 1)
        cls_preds_2 = Reshape((n_anchors_2, n_classes+1))(cls_preds_2)
        bbox_preds_2 = Reshape((n_anchors_2, 4))(bbox_preds_2)
        anchors_2 = Reshape((n_anchors_2, 4))(anchors_2)

        ### Feature map 1
        fmap_2_up_1 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_2)
        fmap_1 = Add(name='fmap_1')([fmap_1, fmap_2_up_1]) # (16, 16)

        fmap_1_size = (int(fmap_1.shape[1]), int(fmap_1.shape[2]),)
        anchors_1, cls_preds_1, bbox_preds_1 = fmap_forward(fmap_1, img_width, img_height, sizes[1], ratios[1],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_1 = int(fmap_1.shape[1]) * int(fmap_1.shape[2]) * (len(sizes[1]) + len(ratios[1]) - 1)
        cls_preds_1 = Reshape((n_anchors_1, n_classes+1))(cls_preds_1)
        bbox_preds_1 = Reshape((n_anchors_1, 4))(bbox_preds_1)
        anchors_1 = Reshape((n_anchors_1, 4))(anchors_1)

        ### Feature map 0
        fmap_1_up_0 = UpSampling2D(size=(2, 2), data_format="channels_last", interpolation='bilinear')(fmap_1)
        fmap_0 = Add(name='fmap_0')([fmap_0, fmap_1_up_0]) # (32, 32)

        fmap_0_size = (int(fmap_0.shape[1]), int(fmap_0.shape[2]),)
        anchors_0, cls_preds_0, bbox_preds_0 = fmap_forward(fmap_0, img_width, img_height, sizes[0], ratios[0],
                                                              clip_boxes=clip_boxes, normalize=normalize, n_classes=n_classes,
                                                              kernel=(3,3), l2_reg=l2_reg, bn=bn_pred, dw=dw_pred)
        n_anchors_0 = int(fmap_0.shape[1]) * int(fmap_0.shape[2]) * (len(sizes[0]) + len(ratios[0]) - 1)
        cls_preds_0 = Reshape((n_anchors_0, n_classes+1))(cls_preds_0)
        bbox_preds_0 = Reshape((n_anchors_0, 4))(bbox_preds_0)
        anchors_0 = Reshape((n_anchors_0, 4))(anchors_0)

        ### Concatenate for all anchor boxes
        anchors = Concatenate(axis=1, name="anchors_concat")([anchors_0, anchors_1, anchors_2, anchors_3, anchors_4, anchors_5])
        cls_preds = Concatenate(axis=1, name="classes_concat")([cls_preds_0, cls_preds_1, cls_preds_2, cls_preds_3, cls_preds_4, cls_preds_5])
        bbox_preds = Concatenate(axis=1, name="bboxes_concat")([bbox_preds_0, bbox_preds_1, bbox_preds_2, bbox_preds_3, bbox_preds_4, bbox_preds_5])

        cls_softmax = Activation('softmax', name='classes_softmax')(cls_preds)

        ### Final predictions for all anchor boxes
        predictions = Concatenate(axis=2, name='predictions')([cls_softmax, bbox_preds, anchors])

        model = Model(inputs=base_model.input, outputs=predictions)

        fmap_sizes = []
        fmap_sizes.append(fmap_0_size)
        fmap_sizes.append(fmap_1_size)
        fmap_sizes.append(fmap_2_size)
        fmap_sizes.append(fmap_3_size)
        fmap_sizes.append(fmap_4_size)
        fmap_sizes.append(fmap_5_size)

        return model, fmap_sizes