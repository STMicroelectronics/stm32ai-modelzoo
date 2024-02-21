/**
  ******************************************************************************
  * @file    lite_conv2d_dqnn.h
  * @author  AIS
  * @brief   header file of AI platform lite conv kernel datatypes
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
#ifndef LITE_CONV2D_DQNN_H
#define LITE_CONV2D_DQNN_H
#pragma once

#include "ai_lite_interface.h"



/******************************************************************************/
/*  Forward Functions Section                                                 */
/******************************************************************************/

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with 0 padding (QKeras like) - Lite I/F
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_is1os1ws1_bn_pad0(const ai_u32 *pDataIn_init,
                                          ai_u32 *pDataOut_init,
                                          const ai_u32 *pWeights_init,
                                          ai_float *pScratch_32,
                                          const ai_u32 n_channel_in,
                                          const ai_u32 n_channel_out,
                                          const ai_i32 width_in, 
                                          const ai_i32 height_in,
                                          const ai_i32 width_out,
                                          const ai_i32 height_out,
                                          const ai_i32 filt_width,
                                          const ai_i32 filt_height,
                                          const ai_i32 filt_pad_x,
                                          const ai_i32 filt_pad_y,
                                          const ai_i32 filt_stride_x,
                                          const ai_i32 filt_stride_y,
                                          const ai_i32 *pThreshold);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with 0 padding (QKeras like) - Lite I/F 
 *        - Optimized thanks to Optim0 assumptions
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_is1os1ws1_bn_pad0_optim0(const ai_u32 *pDataIn_init,
                                                  ai_u32 *pDataOut_init,
                                                  const ai_u32 *pWeights_init,
                                                  ai_float *pScratch_32,
                                                  const ai_u32 n_channel_in,
                                                  const ai_u32 n_channel_out,
                                                  const ai_i32 width_in, 
                                                  const ai_i32 height_in,
                                                  const ai_i32 width_out,
                                                  const ai_i32 height_out,
                                                  const ai_i32 filt_width,
                                                  const ai_i32 filt_height,
                                                  const ai_i32 filt_pad_x,
                                                  const ai_i32 filt_pad_y,
                                                  const ai_i32 filt_stride_x,
                                                  const ai_i32 filt_stride_y,
                                                  const ai_i32 *pThreshold);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights - with 0 padding (QKeras like) - Lite I/F
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_is1os8ws1_bn_pad0(const ai_u32 *pDataIn_init,
                                          ai_i8 *pDataOut_init,
                                          const ai_u32 *pWeights_init,
                                          ai_float *pScratch_32,
                                          const ai_u32 n_channel_in,
                                          const ai_u32 n_channel_out,
                                          const ai_i32 width_in, 
                                          const ai_i32 height_in,
                                          const ai_i32 width_out,
                                          const ai_i32 height_out,
                                          const ai_i32 filt_width,
                                          const ai_i32 filt_height,
                                          const ai_i32 filt_pad_x,
                                          const ai_i32 filt_pad_y,
                                          const ai_i32 filt_stride_x,
                                          const ai_i32 filt_stride_y,
                                          const ai_float *pScale,
                                          const ai_float *pOffset);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with +1/-1 padding (Larq like) - Lite I/F
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_is1os1ws1_bn_pad1(const ai_u32 *pDataIn_init,
                                        ai_u32 *pDataOut_init,
                                        const ai_u32 *pWeights_init,
                                        ai_float *pScratch_32,
                                        const ai_u32 n_channel_in,
                                        const ai_u32 n_channel_out,
                                        const ai_i32 width_in, 
                                        const ai_i32 height_in,
                                        const ai_i32 width_out,
                                        const ai_i32 height_out,
                                        const ai_i32 filt_width,
                                        const ai_i32 filt_height,
                                        const ai_i32 filt_pad_x,
                                        const ai_i32 filt_pad_y,
                                        const ai_i32 filt_stride_x,
                                        const ai_i32 filt_stride_y,
                                        const ai_i32 *pThreshold,
                                        const ai_i32 pad_value);

/*!
 * @brief Handles 2D convolution with binary input, binary output and 
 *        binary weights - with +1/-1 padding (Larq like) - Lite I/F
 *        - Optimized thanks to Optim2 assumptions
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_is1os1ws1_bn_pad1_optim2(const ai_u32 *pDataIn_init,
                                                  ai_u32 *pDataOut_init,
                                                  const ai_u32 *pWeights_init,
                                                  ai_float *pScratch_32,
                                                  const ai_u32 n_channel_in,
                                                  const ai_u32 n_channel_out,
                                                  const ai_i32 width_in, 
                                                  const ai_i32 height_in,
                                                  const ai_i32 width_out,
                                                  const ai_i32 height_out,
                                                  const ai_i32 filt_width,
                                                  const ai_i32 filt_height,
                                                  const ai_i32 filt_pad_x,
                                                  const ai_i32 filt_pad_y,
                                                  const ai_i32 filt_stride_x,
                                                  const ai_i32 filt_stride_y,
                                                  const ai_i32 *pThreshold,
                                                  const ai_i32 pad_value);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights - with +1/-1 padding (Larq like) - Lite I/F
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_is1os8ws1_bn_pad1(const ai_u32 *pDataIn_init,
                                        ai_i8 *pDataOut_init,
                                        const ai_u32 *pWeights_init,
                                        ai_float *pScratch_32,
                                        const ai_u32 n_channel_in,
                                        const ai_u32 n_channel_out,
                                        const ai_i32 width_in, 
                                        const ai_i32 height_in,
                                        const ai_i32 width_out,
                                        const ai_i32 height_out,
                                        const ai_i32 filt_width,
                                        const ai_i32 filt_height,
                                        const ai_i32 filt_pad_x,
                                        const ai_i32 filt_pad_y,
                                        const ai_i32 filt_stride_x,
                                        const ai_i32 filt_stride_y,
                                        const ai_float *pScale,
                                        const ai_float *pOffset,
                                        const ai_i32 pad_value);

/*!
 * @brief Handles 2D convolution with binary input, 8-bits output and 
 *        binary weights - with +1/-1 padding (Larq like) - Lite I/F 
 *        - Optimized thanks to Optim1 assumptions
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_is1os8ws1_bn_pad1_optim1(const ai_u32 *pDataIn_init,
                                                  ai_i8 *pDataOut_init,
                                                  const ai_u32 *pWeights_init,
                                                  ai_float *pScratch_32,
                                                  const ai_u32 n_channel_in,
                                                  const ai_u32 n_channel_out,
                                                  const ai_i32 width_in, 
                                                  const ai_i32 height_in,
                                                  const ai_i32 width_out,
                                                  const ai_i32 height_out,
                                                  const ai_i32 filt_width,
                                                  const ai_i32 filt_height,
                                                  const ai_i32 filt_pad_x,
                                                  const ai_i32 filt_pad_y,
                                                  const ai_i32 filt_stride_x,
                                                  const ai_i32 filt_stride_y,
                                                  const ai_float *pScale,
                                                  const ai_float *pOffset,
                                                  const ai_i32 pad_value);

/*!
 * @brief Handles 2D convolution with 8-bits quantized Input and weights and 
 *        binary output - Lite I/F
 * @ingroup lite_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
LITE_API_ENTRY
void forward_lite_conv2d_is8os1ws8(const ai_i8 *pDataIn_init,
                                   ai_u32 *pDataOut_init,
                                   const ai_i8 *pWeights_init,
                                   ai_float *pScratch_32,
                                   const ai_u32 n_channel_in,
                                   const ai_u32 n_channel_out,
                                   const ai_i32 width_in, 
                                   const ai_i32 height_in,
                                   const ai_i32 width_out,
                                   const ai_i32 height_out,
                                   const ai_i32 filt_width,
                                   const ai_i32 filt_height,
                                   const ai_i32 filt_pad_x,
                                   const ai_i32 filt_pad_y,
                                   const ai_i32 filt_stride_x,
                                   const ai_i32 filt_stride_y,
                                   const ai_i32 *pThreshold,
                                   const ai_i8 in_zeropoint);

/*!
 * @brief Handles 2D convolution with 8-bits quantized Input and weights and 
 *        binary output - Lite I/F - Optimized thanks to Optim2 assumptions
 * @ingroup lite_conv2d_dqnn
 * @param layer conv2d_dqnn layer
 */
LITE_API_ENTRY
void forward_lite_conv2d_is8os1ws8_optim2(const ai_i8 *pDataIn_init,
                                         ai_u32 *pDataOut_init,
                                         const ai_i8 *pWeights_init,
                                         ai_float *pScratch_32,
                                         const ai_u32 n_channel_in,
                                         const ai_u32 n_channel_out,
                                         const ai_i32 width_in, 
                                         const ai_i32 height_in,
                                         const ai_i32 width_out,
                                         const ai_i32 height_out,
                                         const ai_i32 filt_width,
                                         const ai_i32 filt_height,
                                         const ai_i32 filt_pad_x,
                                         const ai_i32 filt_pad_y,
                                         const ai_i32 filt_stride_x,
                                         const ai_i32 filt_stride_y,
                                         const ai_i32 *pThreshold,
                                         const ai_i8 in_zeropoint);

/*!
 * @brief Handles 2D convolution with 8-bits quantized Input and weights and 
 *        binary output - quantized with DoReFa SotA quantizer, lite I/F
 * @ingroup lite_conv2d_dqnn
 */
LITE_API_ENTRY
void forward_lite_conv2d_dorefa_is8os1ws8(const ai_i8 *pDataIn_init,
                                          ai_u32 *pDataOut_init,
                                          const ai_u8 *pWeights_init,
                                          ai_float *pScratch_32,
                                          const ai_u32 n_channel_in,
                                          const ai_u32 n_channel_out,
                                          const ai_i32 width_in, 
                                          const ai_i32 height_in,
                                          const ai_i32 width_out,
                                          const ai_i32 height_out,
                                          const ai_i32 filt_width,
                                          const ai_i32 filt_height,
                                          const ai_i32 filt_pad_x,
                                          const ai_i32 filt_pad_y,
                                          const ai_i32 filt_stride_x,
                                          const ai_i32 filt_stride_y,
                                          const ai_i32 *pThreshold,
                                          const ai_i8 in_zeropoint);



#endif    /*LITE_CONV2D_DQNN_H*/
