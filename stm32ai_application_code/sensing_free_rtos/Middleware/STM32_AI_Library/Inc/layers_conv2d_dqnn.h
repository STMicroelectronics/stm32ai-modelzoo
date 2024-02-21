/**
  ******************************************************************************
  * @file    layers_conv2d_dqnn.h
  * @author  AIS
  * @brief   header file of AI platform DQNN conv datatypes
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  @verbatim
  @endverbatim
  ******************************************************************************
  */
#ifndef LAYERS_CONV2D_DQNN_H
#define LAYERS_CONV2D_DQNN_H
#pragma once

#include "layers_common.h"
#include "layers_conv2d.h"

/*!
 * @defgroup layers_conv2d_dqnn Layers Definitions
 * @brief definition 
 *
 */

AI_API_DECLARE_BEGIN


#define AI_DQNN_PAD_1_KEY     (1)
#define AI_DQNN_PAD_M1_KEY    (-1)
#define AI_DQNN_PAD_0_KEY     (0)
#define AI_DQNN_PAD_1_VALUE   (0x0)
#define AI_DQNN_PAD_M1_VALUE  (0xFFFFFFFF)
#define AI_DQNN_PAD_0_VALUE   (0x2)


/*!
 * @struct ai_layer_conv2d_dqnn
 * @ingroup layers_conv2d_dqnn
 * @brief conv2d_dqnn layer
 *
 * @ref forward_conv2d_is1os1ws1
 */
typedef AI_ALIGNED_TYPE(struct, 4) ai_layer_conv2d_dqnn_ {
  AI_LAYER_CONV2D_FIELDS_DECLARE
  ai_i32  pad_value;
} ai_layer_conv2d_dqnn;


/******************************************************************************/
/*  Forward Functions Section                                                 */
/******************************************************************************/

/*!
 * @brief Handles point wise convolution with binary input, binary output and 
 *        binary weights
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_pw_is1os1ws1_bn(ai_layer *pLayer);

/*!
 * @brief Handles point wise convolution with binary input, binary output and 
 *        binary weights - Optimized thanks to Optim2 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_pw_is1os1ws1_bn_optim2(ai_layer *pLayer);

/*!
 * @brief Handles point wise convolution with binary input, 8-bits output and 
 *        binary weights
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_pw_is1os8ws1_bn(ai_layer *pLayer);

/*!
 * @brief Handles point wise convolution with binary input, 8-bits output and 
 *        binary weights - Optimized thanks to Optim1 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_pw_is1os8ws1_bn_optim1(ai_layer *pLayer);

/*!
 * @brief Handles point-wise convolution with binary input, float32 output 
 *        and binary weights
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_pw_is1of32ws1_bn(ai_layer *pLayer);

/*!
 * @brief Handles point-wise convolution with binary input, float32 output 
 *        and binary weights - Optimized thanks to Optim1 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_pw_is1of32ws1_bn_optim1(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os1ws1_bn(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - Optimized thanks to Optim2 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os1ws1_bn_optim2(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os8ws1_bn(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights - Optimized thanks to Optim1 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os8ws1_bn_optim1(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with 0 padding (QKeras like)
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os1ws1_bn_pad0(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with 0 padding (QKeras like) - Optimized thanks to 
 *        Optim0 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os1ws1_bn_pad0_optim0(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights - with 0 padding (QKeras like)
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os8ws1_bn_pad0(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with +1/-1 padding (Larq like)
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os1ws1_bn_pad1(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with +1/-1 padding (Larq like) - Optimized thanks 
 *        to Optim2 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os1ws1_bn_pad1_optim2(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights - with +1/-1 padding (Larq like)
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os8ws1_bn_pad1(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights - with +1/-1 padding (Larq like) - Optimized thanks 
 *        to Optim1 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is1os8ws1_bn_pad1_optim1(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with 8-bits quantized Input and weights and 
 *        binary output
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is8os1ws8(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with 8-bits quantized Input and weights and 
 *        binary output - Optimized thanks to Optim2 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is8os1ws8_optim2(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with 8-bits quantized Input and weights and 
 *        binary output - quantized with DoReFa SotA quantizer
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_dorefa_is8os1ws8(ai_layer *pLayer);

/*!
 * @brief Handles depth-wise convolution with binary input, binary output and 
 *        binary weights
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_dw_is1os1ws1_bn(ai_layer *pLayer);

/*!
 * @brief Handles depth-wise convolution with binary input, binary output and 
 *        binary weights - Optimized thanks to Optim3 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_dw_is1os1ws1_bn_optim3(ai_layer *pLayer);

/*!
 * @brief Handles depth-wise convolution with binary input, binary output and 
 *        binary weights - with 0 padding (QKeras like)
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_dw_is1os1ws1_bn_pad0(ai_layer *pLayer);

/*!
 * @brief Handles depth-wise convolution with binary input, binary output and 
 *        binary weights - with 0 padding (QKeras like) - Optimized thanks to 
 *        Optim3 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_dw_is1os1ws1_bn_pad0_optim3(ai_layer *pLayer);

/*!
 * @brief Handles depth-wise convolution with binary input, binary output and 
 *        binary weights - with +1/-1 padding (Larq like)
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_dw_is1os1ws1_bn_pad1(ai_layer *pLayer);

/*!
 * @brief Handles depth-wise convolution with binary input, binary output and 
 *        binary weights - with +1/-1 padding (Larq like) - Optimized thanks to 
 *        Optim3 assumptions
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_dw_is1os1ws1_bn_pad1_optim3(ai_layer *pLayer);

/*!
 * @brief Handles 2D convolution with 8-bits quantized Input and output and 
 *        binary weights
 * @ingroup layers_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
AI_INTERNAL_API
void forward_conv2d_is8os8ws1(ai_layer *pLayer);



AI_API_DECLARE_END

#endif    /*LAYERS_CONV2D_DQNN_H*/
