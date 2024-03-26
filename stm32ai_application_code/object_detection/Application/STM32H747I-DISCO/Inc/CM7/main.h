/**
 ******************************************************************************
 * @file    main.h
 * @author  MCD Application Team
 * @brief   Header for main.c module for Cortex-M7.
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
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

/* Includes ------------------------------------------------------------------*/
#include <stdio.h>

#include "stm32ipl.h"
#include "ai_interface.h"
#include "stm32h747i_discovery_sdram.h"
#include "stm32h747i_discovery_sd.h"
#include "stm32h747i_discovery_camera.h"
#include "stm32h747i_discovery.h"

#include "stm32h747i_discovery_sd.h"
#include "ai_model_config.h"

#if POSTPROCESS_TYPE == POSTPROCESS_CENTER_NET
#include "objdetect_centernet_pp_if.h"
#elif POSTPROCESS_TYPE == POSTPROCESS_YOLO_V2
#include "objdetect_yolov2_pp_if.h"
#elif POSTPROCESS_TYPE == POSTPROCESS_ST_SSD
#include "objdetect_ssd_st_pp_if.h"
#elif POSTPROCESS_TYPE == POSTPROCESS_SSD
#include "objdetect_ssd_pp_if.h"
#endif



#define WELCOME_MSG_0             AI_NETWORK_ORIGIN_MODEL_NAME
#define WELCOME_MSG_1            "Model Running in STM32 MCU internal memory"

#if defined (AI_NETWORK_INPUTS_IN_ACTIVATIONS) && defined (AI_NETWORK_OUTPUTS_IN_ACTIVATIONS) 
 #define WELCOME_MSG_2            "NN Input and Ouput buffers in Activation"
#elif defined (AI_NETWORK_INPUTS_IN_ACTIVATIONS)
 #define WELCOME_MSG_2            "NN Input buffer in Activation"
#elif defined (AI_NETWORK_OUTPUTS_IN_ACTIVATIONS)
 #define WELCOME_MSG_2            "NN Output buffer in Activation"
#else
 #define WELCOME_MSG_2            "NN Input/Output in dedicated buffers "
#endif

#if (QUANT_INPUT_TYPE == UINT8_FORMAT)
 #define WELCOME_MSG_3            "Input data format: UINT8"
#elif (QUANT_INPUT_TYPE == INT8_FORMAT)
 #define WELCOME_MSG_3            "Input data format: INT8"
#elif (QUANT_INPUT_TYPE == FLOAT32_FORMAT)
 #define WELCOME_MSG_3            "Input data format: FLOAT32"
#else
 #error Please check definition of QUANT_INPUT_TYPE define
#endif

#if (QUANT_OUTPUT_TYPE == UINT8_FORMAT)
 #define WELCOME_MSG_4            "Output data format: UINT8"
#elif (QUANT_OUTPUT_TYPE == INT8_FORMAT)
 #define WELCOME_MSG_4            "Output data format: INT8"
#elif (QUANT_OUTPUT_TYPE == FLOAT32_FORMAT)
 #define WELCOME_MSG_4            "Output data format: FLOAT32"
#else
 #error Please check definition of QUANT_OUTPUT_TYPE define
#endif



/*Defines related to cache settings*/
#define EXT_SDRAM_CACHE_ENABLED 1
#define NN_OUTPUT_CLASS_NUMBER AI_NET_OUTPUT_SIZE


/****************************/
/***CAMERA related defines***/
/****************************/
#define QVGA_RES_WIDTH  (320)
#define QVGA_RES_HEIGHT (240)
#define VGA_RES_WIDTH  (640)
#define VGA_RES_HEIGHT (480)

#define RGB_565_BPP (2)
#define RGB_888_BPP (3)

/* Capture size */
#define CAMERA_RESOLUTION (CAMERA_R320x240)
#define CAM_RES_WIDTH (QVGA_RES_WIDTH)
#define CAM_RES_HEIGHT (QVGA_RES_HEIGHT)

#if ASPECT_RATIO_MODE == ASPECT_RATIO_PADDING
  #define CAM_RES_WITH_BORDERS  CAM_RES_WIDTH
#endif

#define CAM_LINE_SIZE  (CAM_RES_WIDTH * RGB_565_BPP)

/**************************/
/***LCD related defines****/
/**************************/
#define SDRAM_BANK_SIZE   (8 * 1024 * 1024)  /*!< IS42S32800J has 4x8MB banks */
#define LCD_BRIGHTNESS_MIN 0
#define LCD_BRIGHTNESS_MAX 100
#define LCD_BRIGHTNESS_MID 50
#define LCD_BRIGHTNESS_STEP 10

#define ARGB8888_BYTE_PER_PIXEL 4
#define LCD_RES_WIDTH 800
#define LCD_RES_HEIGHT 480
#define LCD_BBP ARGB8888_BYTE_PER_PIXEL
#define LCD_FRAME_BUFFER_SIZE (LCD_RES_WIDTH * LCD_RES_HEIGHT * LCD_BBP)

/******************************/
/****Buffers size definition***/
/******************************/
#if ASPECT_RATIO_MODE == ASPECT_RATIO_PADDING
  #if (CAM_RES_WITH_BORDERS * CAM_RES_WITH_BORDERS * RGB_565_BPP)%32 == 0
    #define CAM_FRAME_BUFFER_SIZE (CAM_RES_WITH_BORDERS * CAM_RES_WITH_BORDERS * RGB_565_BPP)
  #else
    #define CAM_FRAME_BUFFER_SIZE (CAM_RES_WITH_BORDERS * CAM_RES_WITH_BORDERS * RGB_565_BPP + 32 - (CAM_RES_WITH_BORDERS * CAM_RES_WITH_BORDERS * RGB_565_BPP)%32)
  #endif
#else
  #if (CAM_RES_WIDTH * CAM_RES_HEIGHT * RGB_565_BPP)%32 == 0
    #define CAM_FRAME_BUFFER_SIZE (CAM_RES_WIDTH * CAM_RES_HEIGHT * RGB_565_BPP)
  #else
    #define CAM_FRAME_BUFFER_SIZE (CAM_RES_WIDTH * CAM_RES_HEIGHT * RGB_565_BPP + 32 - (CAM_RES_WIDTH * CAM_RES_HEIGHT * RGB_565_BPP)%32)
  #endif
#endif
#if (AI_NETWORK_WIDTH * AI_NETWORK_HEIGHT * RGB_565_BPP)%32 == 0
  #define RESCALED_FRAME_BUFFER_SIZE (AI_NETWORK_WIDTH * AI_NETWORK_HEIGHT * RGB_565_BPP)
#else
  #define RESCALED_FRAME_BUFFER_SIZE (AI_NETWORK_WIDTH * AI_NETWORK_HEIGHT * RGB_565_BPP + 32 - (AI_NETWORK_WIDTH * AI_NETWORK_HEIGHT * RGB_565_BPP)%32)
#endif
#if AI_NET_INPUT_SIZE_BYTES%32 == 0
  #define AI_INPUT_BUFFER_SIZE AI_NET_INPUT_SIZE_BYTES
#else
  #define AI_INPUT_BUFFER_SIZE (AI_NET_INPUT_SIZE_BYTES + 32 - AI_NET_INPUT_SIZE_BYTES%32)
#endif
#if AI_NET_OUTPUT_SIZE_BYTES%32 == 0
  #define AI_OUTPUT_BUFFER_SIZE AI_NET_OUTPUT_SIZE_BYTES
#else
  #define AI_OUTPUT_BUFFER_SIZE (AI_NET_OUTPUT_SIZE_BYTES + 32 - AI_NET_OUTPUT_SIZE_BYTES%32)
#endif
#define AI_ACTIVATION_BUFFER_SIZE AI_ACTIVATION_SIZE_BYTES

/*******************/
/****PFC defines****/
/*******************/
/*The Pixel Format Conversion method:
* 1: HW_PFC : PFC performed by mean of HW engine like DMA2D
* 2: SW_PFC : PFC is performed by mean of SW routine and LUT
*/
#define HW_PFC 1
#define SW_PFC 2


typedef enum 
{
  FRAME_CAPTURE    = 0x00,
  FRAME_RESIZE     = 0x01,
  FRAME_PFC        = 0x02,
  FRAME_PVC        = 0x03,
  FRAME_INFERENCE  = 0x04,
  
  APP_FRAMEOPERATION_NUM  
} AppFrameOperation_TypeDef;

/* Exported types ------------------------------------------------------------*/
typedef struct
{
uint16_t x;
uint16_t y;
uint32_t rowStride;
}Dma2dCfg_TypeDef;

typedef enum
{
    network_centernet = 0,
    network_yolov2 = 1,
    network_st_ssd = 2,
    network_ssd = 3,
} network_postprocess_type;

typedef struct
{ 
  /**NN Output**/
  uint32_t nn_inference_time;
  char const* nn_top1_output_class_name;
  float nn_top1_output_class_proba;
  
  /**Camera context**/
  volatile uint8_t new_frame_ready;
  uint32_t mirror_flip;
  uint32_t cropping_enable;
  
  /**Pre-Processing context**/
  uint32_t red_blue_swap;
  uint32_t PixelFormatConv;
 
  /**Display context**/
  volatile uint32_t lcd_sync;
  
  /**Utility context**/
  uint32_t Tinf_start;
  uint32_t Tinf_stop;
  uint32_t Tfps_start;
  uint32_t Tfps_stop;
  
  /**AI NN context**/
  uint8_t* lut;
  uint32_t nn_input_type; 
  uint32_t nn_output_type;
  const char** nn_output_labels;
  
  /*Post-Processing context*/
  int32_t error;
#if POSTPROCESS_TYPE == POSTPROCESS_CENTER_NET
  centernet_pp_static_param_t input_static_param;
#elif POSTPROCESS_TYPE == POSTPROCESS_YOLO_V2
  yolov2_pp_static_param_t input_static_param;
#elif POSTPROCESS_TYPE == POSTPROCESS_ST_SSD
  ssd_st_pp_static_param_t input_static_param;
#elif POSTPROCESS_TYPE == POSTPROCESS_SSD
  ssd_pp_static_param_t input_static_param;
#endif
  postprocess_out_t output;
  void  *pInput;

  /**Application buffers**/
  void* nn_output_buffer[AI_NETWORK_OUT_NUM];
  void* nn_input_buffer;
  void** activation_buffer;
  uint8_t* rescaled_image_buffer;
  uint8_t* camera_capture_buffer;
  uint8_t* camera_capture_buffer_no_borders;
  uint8_t *lcd_frame_read_buff;
  uint8_t *lcd_frame_write_buff;
  
}AppConfig_TypeDef;

/* Exported types ------------------------------------------------------------*/
extern void* NN_Activation_Buffer[];

/* Exported constants --------------------------------------------------------*/
/* Exported macro ------------------------------------------------------------*/
/* Exported functions ------------------------------------------------------- */
extern void Error_Handler(void);

#endif /* __MAIN_H */

