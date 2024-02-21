/**
  ******************************************************************************
  * @file    objdetect_ssd_pp_if.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   global interface for Post processing of SSD Object Detection
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

#ifndef __OBJDETECT_SSD_PP_IF_H__
#define __OBJDETECT_SSD_PP_IF_H__

#ifdef __cplusplus
 extern "C" {
#endif
   
#include "objdetect_ssd_pp_user_template.h"
#include "objdetect_pp_output_if.h"

   
/* I/O structures for SSD detector type */
/* ------------------------------------ */
typedef struct ssd_pp_in_centroid
{
	float32_t *pBoxes;
	float32_t *pAnchors;
	float32_t *pScores;
} ssd_pp_in_centroid_t;


/* Generic Static parameters */
/* ------------------------- */
typedef struct ssd_pp_static_param
{
	int32_t   nb_classes;
	int32_t   nb_detections;
	float32_t XY_scale;
	float32_t WH_scale;
	int32_t   max_boxes_limit;
	float32_t	conf_threshold;
	float32_t	iou_threshold;
	int32_t   nb_detect;
} ssd_pp_static_param_t;


/* Exported functions ------------------------------------------------------- */

/*!
 * @brief Resets object detection SSD post processing
 *
 * @param [IN] Input static parameters
 * @retval Error code
 */
int32_t objdetect_ssd_pp_reset(ssd_pp_static_param_t *pInput_static_param);


/*!
 * @brief Object detector post processing : includes output detector remapping,
 *        nms and score filtering for SSD.
 *
 * @param [IN] Pointer on input data
 *             Pointer on output data
 *             pointer on static parameters
 * @retval Error code
 */
int32_t objdetect_ssd_pp_process(ssd_pp_in_centroid_t *pInput, 
                                 postprocess_out_t *pOutput, 
                                 ssd_pp_static_param_t *pInput_static_param);


#endif      /* __OBJDETECT_SSD_PP_IF_H__  */
