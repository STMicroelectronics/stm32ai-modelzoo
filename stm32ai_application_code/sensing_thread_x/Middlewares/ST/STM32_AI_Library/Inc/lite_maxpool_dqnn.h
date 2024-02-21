/**
  ******************************************************************************
  * @file    lite_maxpool_dqnn.h
  * @author  AIS
  * @brief   header file of AI platform lite maxpool kernel datatypes
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
#ifndef LITE_MAXPOOL_DQNN_H
#define LITE_MAXPOOL_DQNN_H
#pragma once

#include "ai_lite_interface.h"


/******************************************************************************/
/*  Forward Functions Section                                                 */
/******************************************************************************/

/*!
 * @brief Handles maxpool with binary input and binary output - Lite I/F
  * @ingroup lite_maxpool_dqnn
 */
LITE_API_ENTRY
void forward_lite_maxpool_is1os1(const ai_u32 *pDataIn_init, 
                                 ai_u32 *pDataOut_init,
                                 const ai_i32 width_in,
                                 const ai_i32 width_out,
                                 const ai_i32 height_in,
                                 const ai_i32 height_out,
                                 const ai_u32 n_channel_in,
                                 const ai_u32 n_channel_out,
                                 const ai_i32 pool_width,
                                 const ai_i32 pool_height,
                                 const ai_i32 pool_pad_x,
                                 const ai_i32 pool_pad_y,
                                 const ai_i32 pool_stride_x,
                                 const ai_i32 pool_stride_y,
                                 const ai_u32 pool_pad_value, 
                                 ai_float *pScratch_32);


#endif    /*LITE_MAXPOOL_DQNN_H*/
