/**
  ******************************************************************************
  * @file    objdetect_ssd_pp_user.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   User header file for Post processing of SSD Object Detection
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

#ifndef __OBJDETECT_SSD_ST_PP_USER_H__
#define __OBJDETECT_SSD_ST_PP_USER_H__


#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"


/* I/O configuration */
#define AI_OBJDETECT_SSD_ST_PP_TOTAL_DETECTIONS            (3830)
#define AI_OBJDETECT_SSD_ST_PP_NB_CLASSES                  (2)

/* --------  Tuning below can be modified by the application --------- */
#define AI_OBJDETECT_SSD_ST_PP_CONF_THRESHOLD              (0.6f)
#define AI_OBJDETECT_SSD_ST_PP_IOU_THRESHOLD               (0.3f)
#define AI_OBJDETECT_SSD_ST_PP_MAX_BOXES_LIMIT             (100)


#endif      /* __OBJDETECT_SSD_ST_PP_USER_H__  */

