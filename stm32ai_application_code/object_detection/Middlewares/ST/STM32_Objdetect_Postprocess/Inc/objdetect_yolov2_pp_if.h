/**
  ******************************************************************************
  * @file    objdetect_yolov2_pp_if.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   global interface for Post processing of YoloV2 Object Detection
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

#ifndef __OBJDETECT_YOLOV2_PP_IF_H__
#define __OBJDETECT_YOLOV2_PP_IF_H__


#ifdef __cplusplus
 extern "C" {
#endif

#include "objdetect_pp_output_if.h"


/* I/O structures for YoloV2 detector type */
/* --------------------------------------- */
typedef struct yolov2_pp_inBuffer
{
	float32_t      x_center;
	float32_t      y_center;
	float32_t      width;
	float32_t      height;
	float32_t      objectness;
	float32_t      class_proba[AI_OBJDETECT_YOLOV2_PP_NB_CLASSES];
} yolov2_pp_inBuffer_t;

typedef struct yolov2_pp_in
{
	yolov2_pp_inBuffer_t inBuff[AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH * 
                              AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT * 
                              AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS];
} yolov2_pp_in_t;



/* Generic Static parameters */
/* ------------------------- */
typedef enum yolov2_pp_optim {
  AI_OBJDETECT_YOLOV2_PP_OPTIM_NORMAL     = 0,
  AI_OBJDETECT_YOLOV2_PP_OPTIM_FAST       = 1
} yolov2_pp_optim_e;


typedef struct yolov2_pp_static_param {
  int32_t  nb_classes;
  int32_t  nb_anchors;
  int32_t  grid_width;
  int32_t  grid_height;
  int32_t  nb_input_boxes;
  int32_t  max_boxes_limit;
  float32_t	conf_threshold;
  float32_t	iou_threshold;
  const float32_t	*pAnchors;
  yolov2_pp_optim_e optim;
  int32_t nb_detect;
} yolov2_pp_static_param_t;



/* Exported functions ------------------------------------------------------- */

/*!
 * @brief Resets object detection YoloV2 post processing
 *
 * @param [IN] Input static parameters
 * @retval Error code
 */
int32_t objdetect_yolov2_pp_reset(yolov2_pp_static_param_t *pInput_static_param);


/*!
 * @brief Object detector post processing : includes output detector remapping,
 *        nms and score filtering for YoloV2.
 *
 * @param [IN] Pointer on input data
 *             Pointer on output data
 *             pointer on static parameters
 * @retval Error code
 */
int32_t objdetect_yolov2_pp_process(yolov2_pp_in_t *pInput,
                                    postprocess_out_t *pOutput,
                                    yolov2_pp_static_param_t *pInput_static_param);



#endif      /* __OBJDETECT_YOLOV2_PP_IF_H__  */


