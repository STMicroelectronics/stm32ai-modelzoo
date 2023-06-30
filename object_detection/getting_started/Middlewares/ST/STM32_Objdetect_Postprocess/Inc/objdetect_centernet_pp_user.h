/**
  ******************************************************************************
  * @file    objdetect_centernet_pp_user.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   User header file for Post processing of CenterNet Object Detection
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

/* ---------------    Generated code    ----------------- */
#ifndef __OBJDETECT_CENTERNET_PP_USER_H__
#define __OBJDETECT_CENTERNET_PP_USER_H__


#ifdef __cplusplus
  extern "C" {
#endif

#include "arm_math.h"


/* I/O configuration */
#define AI_OBJDETECT_CENTERNET_PP_GRID_WIDTH        (64)
#define AI_OBJDETECT_CENTERNET_PP_GRID_HEIGHT       (64)
#define AI_OBJDETECT_CENTERNET_PP_NB_INPUT_BOXES    (AI_OBJDETECT_CENTERNET_PP_GRID_WIDTH * AI_OBJDETECT_CENTERNET_PP_GRID_HEIGHT)
#define AI_OBJDETECT_CENTERNET_PP_NB_CLASSIFS       (7)


/* --------  Tuning below can be modified by the application --------- */
#define AI_OBJDETECT_CENTERNET_PP_CONF_THRESHOLD    (0.3000000000f)
#define AI_OBJDETECT_CENTERNET_PP_IOU_THRESHOLD     (0.3000000000f)
#define AI_OBJDETECT_CENTERNET_PP_MAX_BOXES_LIMIT   (20)


#endif      /* __OBJDETECT_CENTERNET_PP_USER_H__  */

