/**
  ******************************************************************************
  * @file    objdetect_pp_output_if.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   global interface for Post processing of CenterNet Object Detection
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2018 STMicroelectronics.
  * All rights reserved.
  *
  * This software component is licensed by ST under Ultimate Liberty license
  * SLA0044, the "License"; You may not use this file except in compliance with
  * the License. You may obtain a copy of the License at:
  *                             www.st.com/SLA0044
  *
  ******************************************************************************
  */

#ifndef __OBJDETECT_POSTPROCESS_INTERFACE_IF_H__
#define __OBJDETECT_POSTPROCESS_INTERFACE_IF_H__


#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"


/* Error return codes */
#define AI_OBJDETECT_POSTPROCESS_ERROR_NO                    (0)
#define AI_OBJDETECT_POSTPROCESS_ERROR_BAD_HW                (-1)


typedef struct
{
	float32_t x_center;
	float32_t y_center;
	float32_t width;
	float32_t height;
	float32_t conf;
	int32_t   class_index;
} postprocess_outBuffer_t;

typedef struct
{
	postprocess_outBuffer_t *pOutBuff;
	int32_t nb_detect;
} postprocess_out_t;


#endif      /* __OBJDETECT_CENTERNET_PP_IF_H__  */


