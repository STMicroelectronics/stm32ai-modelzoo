/**
  ******************************************************************************
  * @file    objdetect_pp_loc.h
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   local header file for Post processing of Object Detection
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

#ifndef __OBJDETECT_PP_LOC_H__
#define __OBJDETECT_PP_LOC_H__


#ifdef __cplusplus
 extern "C" {
#endif

#include "arm_math.h"


extern void objdetect_maxi(float32_t *arr, int32_t len_arr, float32_t *maxim, int32_t *index);
extern float32_t objdetect_sigmoid_f(float32_t x);
extern void objdetect_softmax_f(float32_t *input_x, float32_t *output_x, int32_t len_x, float32_t *tmp_x);
extern float32_t objdetect_box_iou(float32_t *a, float32_t *b);


/*-----------------------------     YOLO_V2      -----------------------------*/
/* Offsets to access YoloV2 input data */
#define AI_YOLOV2_PP_XCENTER      (0)
#define AI_YOLOV2_PP_YCENTER      (1)
#define AI_YOLOV2_PP_WIDTHREL     (2)
#define AI_YOLOV2_PP_HEIGHTREL    (3)
#define AI_YOLOV2_PP_OBJECTNESS   (4)
#define AI_YOLOV2_PP_CLASSPROB    (5)

typedef int _Cmpfun(const void *, const void *);
extern void qsort(void *, size_t, size_t, _Cmpfun *);


/*-----------------------------       SSD        -----------------------------*/
/* Offsets to access SSD input data */
#define AI_SSD_PP_CENTROID_YCENTER          (0)
#define AI_SSD_PP_CENTROID_XCENTER          (1)
#define AI_SSD_PP_CENTROID_HEIGHTREL        (2)
#define AI_SSD_PP_CENTROID_WIDTHREL         (3)
#define AI_SSD_PP_BOX_STRIDE                (4)

/*-----------------------------       SSD  ST      -----------------------------*/
/* Offsets to access SSD ST input data */
#define AI_SSD_ST_PP_XMIN          (0)
#define AI_SSD_ST_PP_YMIN          (1)
#define AI_SSD_ST_PP_XMAX          (2)
#define AI_SSD_ST_PP_YMAX          (3)
#define AI_SSD_ST_PP_BOX_STRIDE    (4)

#define AI_SSD_ST_PP_CENTROID_YCENTER          (0)
#define AI_SSD_ST_PP_CENTROID_XCENTER          (1)
#define AI_SSD_ST_PP_CENTROID_HEIGHTREL        (2)
#define AI_SSD_ST_PP_CENTROID_WIDTHREL         (3)


/*-----------------------------     CENTER_NET      -----------------------------*/
/* Offsets to access CenterNet input data */
#define AI_CENTERNET_PP_CONFCENTER   (0)
#define AI_CENTERNET_PP_WIDTH        (1)
#define AI_CENTERNET_PP_HEIGHT       (2)
#define AI_CENTERNET_PP_XOFFSET      (3)
#define AI_CENTERNET_PP_YOFFSET      (4)
#define AI_CENTERNET_PP_CLASSPROB    (5)
#define AI_CENTERNET_PP_MAPSEG_NEXTOFFSET    (1)


#endif   /*  __OBJDETECT_PP_LOC_H__  */
