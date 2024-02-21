/**
 ******************************************************************************
 * @file    app_camera.h
 * @author  MDG Application Team
 * @brief   Library to manage camera related operation
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

#ifndef __APP_CAMERA_H
#define __APP_CAMERA_H

#ifdef __cplusplus
extern "C"
{
#endif
  
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#if CAMERA_INTERFACE == CAMERA_INTERFACE_DCMI
  #include "nucleo_h743zi2_camera_dcmi.h"
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
  #include "nucleo_h743zi2_camera_usb.h"
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_SPI
  #include "nucleo_h743zi2_camera_spi.h"
#else
#error "Selected camera interface is not supported"
#endif
  
/* Exported types ------------------------------------------------------------*/
extern AppConfig_TypeDef App_Config;
  
/* Exported functions ------------------------------------------------------- */
void Camera_Init(AppConfig_TypeDef *);
void Camera_Set_MirrorFlip(uint32_t );
void Camera_Enable_TestBar_Mode(void);
void Camera_Disable_TestBar_Mode(void);
void Camera_GetNextReadyFrame(AppConfig_TypeDef *);
void Camera_StartNewFrameAcquisition(AppConfig_TypeDef *);
 
#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* __APP_CAMERA_H */

