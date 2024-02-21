/**
 ******************************************************************************
 * @file    app_display.h
 * @author  MDG Application Team
 * @brief   Library to manage LCD display through DMA2D
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
#ifndef __APP_DISPLAY_H
#define __APP_DISPLAY_H

#ifdef __cplusplus
extern "C"
{
#endif
  
/* Includes ------------------------------------------------------------------*/
#include "main.h"
  
/* Variables -----------------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;
  
/* Exported functions ------------------------------------------------------- */
/* Protoypes */
void Display_Init(AppConfig_TypeDef *);
void Display_WelcomeScreen(AppConfig_TypeDef* );
void Display_CameraPreview(AppConfig_TypeDef *);
void Display_NetworkOutput(AppConfig_TypeDef *);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* __APP_DISPLAY_H */
