/**
  ******************************************************************************
  * @file    lite_conv2d.h
  * @author  AIS
  * @brief   header file of AI platform lite conv2d kernel datatypes
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
#ifndef LITE_CONV2D_H
#define LITE_CONV2D_H
#pragma once

#include "ai_lite_interface.h"



/******************************************************************************/
/*  Forward Functions Section                                                 */
/******************************************************************************/

/*!
 * @brief Handles dilated conv2d convolutions (valid padding)
 * @ingroup lite_conv2d
 */
LITE_API_ENTRY
void 
forward_lite_conv2d_dilated_sssa8_ch(const ai_i8 *pData_in, 
                                     const ai_u16 dim_im_in_x,
                                     const ai_u16 dim_im_in_y,
                                     const ai_u16 n_channel_in,
                                     const ai_i8 *pWeights,
                                     const ai_u16 n_channel_out,
                                     const ai_u16 dim_kernel_x,
                                     const ai_u16 dim_kernel_y,
                                     const ai_u16 stride_x,
                                     const ai_u16 stride_y,
                                     const ai_u16 dilation_x,
                                     const ai_u16 dilation_y,
                                     const ai_i32 *pBias,
                                     const ai_i8 in_zeropoint,
                                     const ai_i8 out_zeropoint,
                                     ai_i8 *pData_out,
                                     const ai_u16 dim_im_out_x,
                                     const ai_u16 dim_im_out_y,
                                     ai_u32 height_loop_cnt, 
                                     const ai_u16 weights_prefetch_enabled, 
                                     ai_i32 scratch_size, 
                                     ai_i16 *pBuffer_a);

/*!
 * @brief Handles conv2d convolutions (valid padding) with number of channels >= 8
 * @ingroup lite_conv2d
 */
LITE_API_ENTRY
void
forward_lite_conv2d_deep_sssa8_ch(const ai_i8 *pData_in, 
                                  const ai_u16 dim_im_in_x,
                                  const ai_u16 dim_im_in_y,
                                  const ai_u16 n_channel_in,
                                  const ai_i8 *pWeights,
                                  const ai_u16 n_channel_out,
                                  const ai_u16 dim_kernel_x,
                                  const ai_u16 dim_kernel_y,
                                  const ai_u16 stride_x,
                                  const ai_u16 stride_y,
                                  const ai_i32 *pBias,
                                  const ai_i8 in_zeropoint,
                                  const ai_i8 out_zeropoint,
                                  ai_i8 *pData_out,
                                  const ai_u16 dim_im_out_x,
                                  const ai_u16 dim_im_out_y,
                                  ai_u32 height_loop_cnt, 
                                  const ai_u16 weights_prefetch_enabled, 
                                  ai_i32 scratch_size, 
                                  ai_i16 *pBuffer_a);

/*!
 * @brief Handles conv2d convolutions with same padding or with number of channels < 8
 * @ingroup lite_conv2d
 */
LITE_API_ENTRY
void
forward_lite_conv2d_sssa8_ch(const ai_i8 *pData_in, 
                             const ai_u16 dim_im_in_x,
                             const ai_u16 dim_im_in_y,
                             const ai_u16 n_channel_in,
                             const ai_i8 *pWeights,
                             const ai_u16 n_channel_out,
                             const ai_u16 dim_kernel_x,
                             const ai_u16 dim_kernel_y,
                             const ai_u16 stride_x,
                             const ai_u16 stride_y,
                             const ai_u16 padding_x,
                             const ai_u16 padding_y,
                             const ai_i32 *pBias,
                             const ai_i8 in_zeropoint,
                             const ai_i8 out_zeropoint,
                             ai_i8 *pData_out,
                             const ai_u16 dim_im_out_x,
                             const ai_u16 dim_im_out_y,
                             const ai_u16 weights_prefetch_enabled, 
                             ai_i32 scratch_size, 
                             ai_i16 *pBuffer_a);

/*!
 * @brief Handles rgb conv2d convolutions 
 * @ingroup lite_conv2d
 */
LITE_API_ENTRY
void 
forward_lite_conv2d_rgb_sssa8_ch(const ai_i8 *pData_in,
                                 const ai_u16 dim_im_in,
                                 const ai_i8 *pWeights,
                                 const ai_u16 n_channel_out,
                                 const ai_u16 dim_kernel,
                                 const ai_u16 padding,
                                 const ai_u16 stride,
                                 const ai_i32 *pBias,
                                 const ai_i8 in_zeropoint,
                                 const ai_i8 out_zeropoint,
                                 ai_i8 *pData_out, 
                                 const ai_u16 dim_im_out, 
                                 ai_i16 *pBuffer_a);

#endif    /*LITE_CONV2D_H*/
