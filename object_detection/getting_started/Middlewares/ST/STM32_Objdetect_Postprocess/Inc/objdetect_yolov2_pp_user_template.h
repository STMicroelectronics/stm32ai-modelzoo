/**
  ******************************************************************************
  * @file    objdetect_yolov2_pp_user.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   User header file for Post processing of YoloV2 Object Detection
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
#ifndef __OBJDETECT_YOLOV2_PP_USER_H__
#define __OBJDETECT_YOLOV2_PP_USER_H__


#ifdef __cplusplus
  extern "C" {
#endif

#include "arm_math.h"


/* I/O configuration */
#define AI_OBJDETECT_YOLOV2_PP_NB_CLASSES        (1)
#define AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS        (2)
#define AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH        (5)
#define AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT       (5)
#define AI_OBJDETECT_YOLOV2_PP_NB_INPUT_BOXES    (AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH * AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT)

/* Anchor boxes */
static const float32_t AI_OBJDETECT_YOLOV2_PP_ANCHORS[2*AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS] = {
    0.7319915300f,     0.8066737300f, 
    1.0042938900f,     0.9427480900f, 
  };

/* --------  Tuning below can be modified by the application --------- */
#define AI_OBJDETECT_YOLOV2_PP_CONF_THRESHOLD    (0.8000000000f)
#define AI_OBJDETECT_YOLOV2_PP_IOU_THRESHOLD     (0.3000000000f)
#define AI_OBJDETECT_YOLOV2_PP_MAX_BOXES_LIMIT   (10)


#endif      /* __OBJDETECT_YOLOV2_PP_USER_H__  */

