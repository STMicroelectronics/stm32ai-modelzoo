/**
 ******************************************************************************
 * @file    app_camera.h
 * @author  MCD Application Team
 * @brief   Library to manage camera related operation
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

#ifndef __APP_CAMERA_H
#define __APP_CAMERA_H

#ifdef __cplusplus
extern "C"
{
#endif
  
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32h747i_discovery_camera.h"
#include "ov9655_reg.h"
  
/* Exported types ------------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;
  
/* Exported functions ------------------------------------------------------- */

void Camera_Init(AppConfig_TypeDef *App_Config_Ptr);
void Camera_Set_MirrorFlip(uint32_t MirrorFlip);
void Camera_Enable_TestBar_Mode(void);
void Camera_Disable_TestBar_Mode(void);
void Camera_GetNextReadyFrame(AppConfig_TypeDef *App_Config_Ptr);
void Camera_StartNewFrameAcquisition(AppConfig_TypeDef *App_Config_Ptr);
 
#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* __APP_CAMERA_H */

