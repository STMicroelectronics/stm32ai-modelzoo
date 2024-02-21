/**
  ******************************************************************************
  * @file    objdetect_centernet_pp_if.h
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

#ifndef __OBJDETECT_CENTERNET_PP_IF_H__
#define __OBJDETECT_CENTERNET_PP_IF_H__


#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"
#include "objdetect_pp_output_if.h"



/* I/O structures for CenterNet detector type */
/* ------------------------------------------ */
typedef struct centernet_pp_inBuffer
{
    float32_t      conf_center;
    float32_t      width;
    float32_t      height;
	float32_t      x_offset;
	float32_t      y_offset;
	float32_t      class_proba[AI_OBJDETECT_CENTERNET_PP_NB_CLASSIFS];
	float32_t      map_segmentation;
} centernet_pp_inBuffer_t;

typedef struct centernet_pp_in
{
	centernet_pp_inBuffer_t inBuff[AI_OBJDETECT_CENTERNET_PP_GRID_WIDTH *
                                   AI_OBJDETECT_CENTERNET_PP_GRID_HEIGHT];
} centernet_pp_in_t;


/* Generic Static parameters */
/* ------------------------- */
typedef enum centernet_pp_optim {
  AI_OBJDETECT_CENTERNET_PP_OPTIM_NORMAL     = 0,
  AI_OBJDETECT_CENTERNET_PP_OPTIM_ACCURACY,
  AI_OBJDETECT_CENTERNET_PP_OPTIM_SPEED
} centernet_pp_optim_e;


typedef struct centernet_pp_static_param {
  int32_t  nb_classifs;
  int32_t  grid_width;
  int32_t  grid_height;
  int32_t  max_boxes_limit;
  float32_t	conf_threshold;
  float32_t	iou_threshold;
  centernet_pp_optim_e optim;
  int32_t nb_detect;
} centernet_pp_static_param_t;



/* Exported functions ------------------------------------------------------- */

/*!
 * @brief Resets object detection CenterNet post processing
 *
 * @param [IN] Input static parameters
 * @retval Error code
 */
int32_t objdetect_centernet_pp_reset(centernet_pp_static_param_t *pInput_static_param);


/*!
 * @brief Object detector post processing : includes output detector remapping,
 *        nms and score filtering for CenterNet.
 *
 * @param [IN] Pointer on input data
 *             Pointer on output data
 *             pointer on static parameters
 * @retval Error code
 */
int32_t objdetect_centernet_pp_process(centernet_pp_in_t *pInput,
                                       postprocess_out_t *pOutput,
                                       centernet_pp_static_param_t *pInput_static_param);



#endif      /* __OBJDETECT_CENTERNET_PP_IF_H__  */


