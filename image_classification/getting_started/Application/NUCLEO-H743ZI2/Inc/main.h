/**
 ******************************************************************************
 * @file    main.h
 * @author  MDG Application Team
 * @brief   Header for main.c module for Cortex-M7.
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
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

#include "stm32h7xx_hal.h"

#include "stm32ipl.h"
#include "ai_interface.h"

#include "nucleo_h743zi2_camera.h"
#include "nucleo_h743zi2.h"

#include "ai_model_config.h"

/* Exported macro ------------------------------------------------------------*/
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

#define NN_OUTPUT_CLASS_NUMBER AI_NET_OUTPUT_SIZE


/****************************/
/***CAMERA related defines***/
/****************************/
#define QVGA_RES_WIDTH  320
#define QVGA_RES_HEIGHT 240

#define RGB_565_BPP 2
#define RGB_888_BPP 3
#define ARGB8888_BPP 4

/*QVGA capture*/
#if ASPECT_RATIO_MODE == KEEP_ASPECT_RATIO_CROP
  #define CAM_RES_WIDTH  QVGA_RES_HEIGHT
  #define CAM_RES_HEIGHT QVGA_RES_HEIGHT
#else
  #define CAM_RES_WIDTH  QVGA_RES_WIDTH
  #define CAM_RES_HEIGHT QVGA_RES_HEIGHT
#endif

#if ASPECT_RATIO_MODE == KEEP_ASPECT_RATIO_PADDING
  #define RES_WITH_BORDERS  QVGA_RES_WIDTH
#endif

#define CAM_LINE_SIZE  (CAM_RES_WIDTH * 2U) /* 16-bit per px in RGB565 */

/**************************/
/***LCD related defines****/
/**************************/
#define LCD_BRIGHTNESS_MIN 0
#define LCD_BRIGHTNESS_MAX 100
#define LCD_BRIGHTNESS_MID 50
#define LCD_BRIGHTNESS_STEP 10

#define LCD_RES_WIDTH 320
#define LCD_RES_HEIGHT 240
#define LCD_BPP RGB_565_BPP
#define LCD_FRAME_BUFFER_SIZE (LCD_RES_WIDTH * LCD_RES_HEIGHT * LCD_BPP)

/******************************/
/****Buffers size definition***/
/******************************/
#if ASPECT_RATIO_MODE == KEEP_ASPECT_RATIO_PADDING
#define CAM_FRAME_BUFFER_SIZE (RES_WITH_BORDERS * RES_WITH_BORDERS * RGB_565_BPP)
#else
#define CAM_FRAME_BUFFER_SIZE (CAM_RES_WIDTH * CAM_RES_HEIGHT * RGB_565_BPP)
#endif
#define RESCALED_FRAME_BUFFER_SIZE (AI_NETWORK_WIDTH * AI_NETWORK_HEIGHT * RGB_565_BPP)
#define AI_INPUT_BUFFER_SIZE AI_NET_INPUT_SIZE_BYTES
#define AI_OUTPUT_BUFFER_SIZE AI_NET_OUTPUT_SIZE_BYTES 
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


#define B1_Pin GPIO_PIN_13
#define B1_GPIO_Port GPIOC
#define I2C_DISPLAY_SDA_Pin GPIO_PIN_0
#define I2C_DISPLAY_SDA_GPIO_Port GPIOF
#define I2C_DISPLAY_SCL_Pin GPIO_PIN_1
#define I2C_DISPLAY_SCL_GPIO_Port GPIOF
#define CAMERA_RST_Pin GPIO_PIN_2
#define CAMERA_RST_GPIO_Port GPIOF
#define CAMERA_EN_Pin GPIO_PIN_3
#define CAMERA_EN_GPIO_Port GPIOF
#define LD1_Pin GPIO_PIN_0
#define LD1_GPIO_Port GPIOB
#define DISP_NRESET_Pin GPIO_PIN_11
#define DISP_NRESET_GPIO_Port GPIOE
#define DISPLAY_TE_Pin GPIO_PIN_13
#define DISPLAY_TE_GPIO_Port GPIOE
#define DISPLAY_TE_EXTI_IRQn EXTI15_10_IRQn
#define SPI_DISPLAY_SCK_Pin GPIO_PIN_13
#define SPI_DISPLAY_SCK_GPIO_Port GPIOB
#define LD3_Pin GPIO_PIN_14
#define LD3_GPIO_Port GPIOB
#define SPI_DISPLAY_MOSI_Pin GPIO_PIN_15
#define SPI_DISPLAY_MOSI_GPIO_Port GPIOB
#define STLINK_RX_Pin GPIO_PIN_8
#define STLINK_RX_GPIO_Port GPIOD
#define STLINK_TX_Pin GPIO_PIN_9
#define STLINK_TX_GPIO_Port GPIOD
#define USB_OTG_FS_PWR_EN_Pin GPIO_PIN_10
#define USB_OTG_FS_PWR_EN_GPIO_Port GPIOD
#define USB_OTG_FS_OVCR_Pin GPIO_PIN_7
#define USB_OTG_FS_OVCR_GPIO_Port GPIOG
#define SPI_CAMERA_SCK_Pin GPIO_PIN_3
#define SPI_CAMERA_SCK_GPIO_Port GPIOB
#define SPI_CAMERA_MISO_Pin GPIO_PIN_4
#define SPI_CAMERA_MISO_GPIO_Port GPIOB
#define SPI_CAMERA_MOSI_Pin GPIO_PIN_5
#define SPI_CAMERA_MOSI_GPIO_Port GPIOB
#define I2C_CAMERA_SCL_Pin GPIO_PIN_8
#define I2C_CAMERA_SCL_GPIO_Port GPIOB
#define I2C_CAMERA_SDA_Pin GPIO_PIN_9
#define I2C_CAMERA_SDA_GPIO_Port GPIOB
#define LD2_Pin GPIO_PIN_1
#define LD2_GPIO_Port GPIOE

/* Exported types ------------------------------------------------------------*/
typedef enum 
{
  FRAME_CAPTURE    = 0x00,
  FRAME_RESIZE     = 0x01,
  FRAME_PFC        = 0x02,
  FRAME_PVC        = 0x03,
  FRAME_INFERENCE  = 0x04,
  
  APP_FRAMEOPERATION_NUM  
} AppFrameOperation_TypeDef;

typedef struct
{
uint16_t x;
uint16_t y;
uint32_t rowStride;
} Dma2dCfg_TypeDef;

typedef struct
{ 
  /**NN Output**/
  uint32_t nn_inference_time;
  char const* nn_top1_output_class_name;
  float nn_top1_output_class_proba;
  int ranking[NN_OUTPUT_CLASS_NUMBER];
  
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
  float    nn_input_norm_scale;
  int32_t  nn_input_norm_zp;  
  const char** nn_output_labels;
  
  /**Application buffers**/
  void* nn_output_buffer;
  void* nn_input_buffer;
  void* activation_buffer;
  uint8_t* rescaled_image_buffer;
  uint8_t* camera_capture_buffer;
  uint8_t* camera_capture_buffer_no_borders;
  uint8_t *lcd_frame_buff; /* Only one buffer is used for output to save RAM */
  
} AppConfig_TypeDef;

/* Exported variables  -------------------------------------------------------*/
extern uint8_t NN_Activation_Buffer[];

/* Exported functions --------------------------------------------------------*/
extern void Error_Handler(void);

#endif /* __MAIN_H */

