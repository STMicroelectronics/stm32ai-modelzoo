/**
 ******************************************************************************
 * @file    app_display.h
 * @author  MCD Application Team
 * @brief   Library to manage LCD display through DMA2D
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2019 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
#ifndef __APP_DISPLAY_H
#define __APP_DISPLAY_H

#ifdef __cplusplus
extern "C"
{
#endif
  
#include "main.h"
#include "stm32h747i_discovery_lcd.h"
#include "stm32_lcd.h"
  
  
/* Exported types ------------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;
  
/* Exported constants --------------------------------------------------------*/
  
/* Protoypes */
void Display_Init(AppConfig_TypeDef *App_Config_Ptr);
void Display_WelcomeScreen(AppConfig_TypeDef *App_Config_Ptr);
void Display_CameraPreview(AppConfig_TypeDef *App_Config_Ptr);
void Display_NetworkOutput(AppConfig_TypeDef *App_Config_Ptr);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* __APP_DISPLAY_H */

