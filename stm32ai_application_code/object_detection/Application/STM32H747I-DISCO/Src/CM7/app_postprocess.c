/**
  ******************************************************************************
  * @file    app_postprocess.c
  * @author  Artificial Intelligence Solutions group (AIS)
  * @brief   Post processing of Object Detection algorithms
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


#include "app_postprocess.h"
#if POSTPROCESS_TYPE == POSTPROCESS_SSD
#include "anchors.h"
#endif

int32_t app_postprocess_init( AppConfig_TypeDef *App_Config_Ptr)
{
    int32_t error   = AI_OBJDETECT_POSTPROCESS_ERROR_NO;
#if POSTPROCESS_TYPE == POSTPROCESS_CENTER_NET
    App_Config_Ptr->input_static_param.conf_threshold   = AI_OBJDETECT_CENTERNET_PP_CONF_THRESHOLD;		// NMS Confidence threshold that can be tuned by the user
    App_Config_Ptr->input_static_param.iou_threshold    = AI_OBJDETECT_CENTERNET_PP_IOU_THRESHOLD;		// NMS IoU threshold that can be tuned by the user
    App_Config_Ptr->input_static_param.nb_classifs      = AI_OBJDETECT_CENTERNET_PP_NB_CLASSIFS;		// Number of classifications, aligned with the training phase
    App_Config_Ptr->input_static_param.grid_height      = AI_OBJDETECT_CENTERNET_PP_GRID_HEIGHT;		// Height of the output grid, aligned with the training phase
    App_Config_Ptr->input_static_param.grid_width       = AI_OBJDETECT_CENTERNET_PP_GRID_WIDTH;		// Width of the output grid, aligned with the training phase
    App_Config_Ptr->input_static_param.max_boxes_limit  = AI_OBJDETECT_CENTERNET_PP_MAX_BOXES_LIMIT;	// Maximum number of boxes as output of the post processing, that can be tuned by the user
    App_Config_Ptr->input_static_param.optim            = AI_OBJDETECT_CENTERNET_PP_OPTIM_NORMAL;		// Only this mode is supported for now.
    error = objdetect_centernet_pp_reset((centernet_pp_static_param_t *) &App_Config_Ptr->input_static_param);
#elif POSTPROCESS_TYPE == POSTPROCESS_YOLO_V2
    App_Config_Ptr->input_static_param.conf_threshold   = AI_OBJDETECT_YOLOV2_PP_CONF_THRESHOLD;	// NMS Confidence threshold that can be tuned by the user
    App_Config_Ptr->input_static_param.iou_threshold    = AI_OBJDETECT_YOLOV2_PP_IOU_THRESHOLD;	// NMS IoU threshold that can be tuned by the user
    App_Config_Ptr->input_static_param.nb_anchors       = AI_OBJDETECT_YOLOV2_PP_NB_ANCHORS;	// Number of Anchor Boxes, aligned with the training phase
    App_Config_Ptr->input_static_param.nb_classes       = AI_OBJDETECT_YOLOV2_PP_NB_CLASSES;	// Number of classes, aligned with the training phase
    App_Config_Ptr->input_static_param.grid_height      = AI_OBJDETECT_YOLOV2_PP_GRID_HEIGHT;	// Height of the output grid, aligned with the training phase
    App_Config_Ptr->input_static_param.grid_width       = AI_OBJDETECT_YOLOV2_PP_GRID_WIDTH;	// Width of the output grid, aligned with the training phase
    App_Config_Ptr->input_static_param.nb_input_boxes   = AI_OBJDETECT_YOLOV2_PP_NB_INPUT_BOXES;	// Number of NMS input boxes, aligned with the training phase
    App_Config_Ptr->input_static_param.pAnchors         = AI_OBJDETECT_YOLOV2_PP_ANCHORS;		// Pointer on Anchor boxes, aligned with the training phase
    App_Config_Ptr->input_static_param.max_boxes_limit  = AI_OBJDETECT_YOLOV2_PP_MAX_BOXES_LIMIT;	// Maximum number of boxes as output of the post processing, that can be tuned by the user
    App_Config_Ptr->input_static_param.optim            = AI_OBJDETECT_YOLOV2_PP_OPTIM_NORMAL;	// Only this mode is supported for now.
    error = objdetect_yolov2_pp_reset((yolov2_pp_static_param_t *) &App_Config_Ptr->input_static_param);
#elif POSTPROCESS_TYPE == POSTPROCESS_ST_SSD
    App_Config_Ptr->input_static_param.nb_classes = AI_OBJDETECT_SSD_ST_PP_NB_CLASSES;
    App_Config_Ptr->input_static_param.nb_detections = AI_OBJDETECT_SSD_ST_PP_TOTAL_DETECTIONS;
    App_Config_Ptr->input_static_param.max_boxes_limit = AI_OBJDETECT_SSD_ST_PP_MAX_BOXES_LIMIT;
    App_Config_Ptr->input_static_param.conf_threshold = AI_OBJDETECT_SSD_ST_PP_CONF_THRESHOLD;
    App_Config_Ptr->input_static_param.iou_threshold = AI_OBJDETECT_SSD_ST_PP_IOU_THRESHOLD;
    App_Config_Ptr->input_static_param.nb_detect = 1;
    error = objdetect_ssd_st_pp_reset((ssd_st_pp_static_param_t *) &App_Config_Ptr->input_static_param);
#elif POSTPROCESS_TYPE == POSTPROCESS_SSD
    App_Config_Ptr->input_static_param.nb_classes = AI_OBJDETECT_SSD_PP_NB_CLASSES;
    App_Config_Ptr->input_static_param.nb_detections = AI_OBJDETECT_SSD_PP_TOTAL_DETECTIONS;
    App_Config_Ptr->input_static_param.XY_scale = AI_OBJDETECT_SSD_PP_XY_SCALE;
    App_Config_Ptr->input_static_param.WH_scale = AI_OBJDETECT_SSD_PP_WH_SCALE;
    App_Config_Ptr->input_static_param.max_boxes_limit = AI_OBJDETECT_SSD_PP_MAX_BOXES_LIMIT;
    App_Config_Ptr->input_static_param.conf_threshold = AI_OBJDETECT_SSD_PP_CONF_THRESHOLD;
    App_Config_Ptr->input_static_param.iou_threshold = AI_OBJDETECT_SSD_PP_IOU_THRESHOLD;
    App_Config_Ptr->input_static_param.nb_detect = 1;
    error = objdetect_ssd_pp_reset((ssd_pp_static_param_t *) &App_Config_Ptr->input_static_param);
#endif
    return error;
}

int32_t app_postprocess_run( void **pInput,
                            postprocess_out_t*pOutput,
                            void *pInput_static_param)
{


    int32_t error   = AI_OBJDETECT_POSTPROCESS_ERROR_NO;

#if POSTPROCESS_TYPE == POSTPROCESS_CENTER_NET
    error = objdetect_centernet_pp_process((centernet_pp_in_t*) pInput[0],
                                            (postprocess_out_t*) pOutput,
                                            (centernet_pp_static_param_t*) pInput_static_param);
#elif POSTPROCESS_TYPE == POSTPROCESS_YOLO_V2
    error = objdetect_yolov2_pp_process((yolov2_pp_in_t*) pInput[0],
                                        (postprocess_out_t*) pOutput,
                                        (yolov2_pp_static_param_t*) pInput_static_param);
#elif POSTPROCESS_TYPE == POSTPROCESS_ST_SSD
    ssd_st_pp_in_centroid_t pp_input = 
    {
        .pAnchors = pInput[2],
        .pBoxes = pInput[1],
        .pScores = pInput[0],
    };
    error = objdetect_ssd_st_pp_process((ssd_st_pp_in_centroid_t*) &pp_input,
                                        (postprocess_out_t*) pOutput,
                                        (ssd_st_pp_static_param_t*) pInput_static_param);
#elif POSTPROCESS_TYPE == POSTPROCESS_SSD
    ssd_pp_in_centroid_t pp_input = 
    {
        .pAnchors = pp_anchors,
        .pBoxes = pInput[1],
        .pScores = pInput[0],
    };
    error = objdetect_ssd_pp_process((ssd_pp_in_centroid_t*) &pp_input,
                                     (postprocess_out_t*) pOutput,
                                     (ssd_pp_static_param_t*) pInput_static_param);
#else
    #error "PostProcessing type not supported" 
#endif
    return error;
}

