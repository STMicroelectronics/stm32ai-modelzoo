 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_camera_dcmi.h
 * @author  MDG Application Team
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

#ifndef __NUCLEO_H743ZI2_CAMERA_DCMI_H
#define __NUCLEO_H743ZI2_CAMERA_DCMI_H

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "nucleo_h743zi2_camera.h"
#include "nucleo_h743zi2_errno.h"
#if CAMERA_SENSOR == CAMERA_SENSOR_OV5640
  #include "ov5640.h"
#else
#error "Selected camera sensor is not supported"
#endif

/* Macros --------------------------------------------------------------------*/
#define BSP_CAMERA_IT_PRIORITY              15U

#define CAMERA_OV5640_ADDRESS               0x78U

#define CAMERA_MODE_CONTINUOUS              DCMI_MODE_CONTINUOUS
#define CAMERA_MODE_SNAPSHOT                DCMI_MODE_SNAPSHOT

/* Exported types ------------------------------------------------------------*/
typedef struct
{
  uint32_t CameraId;
  uint32_t Resolution;
  uint32_t PixelFormat;
  uint32_t LightMode;
  uint32_t ColorEffect;
  int32_t  Brightness;
  int32_t  Saturation;
  int32_t  Contrast;
  int32_t  HueDegree;
  uint32_t MirrorFlip;
  uint32_t Zoom;
  uint32_t NightMode;
  uint32_t IsMspCallbacksValid;
} CAMERA_Ctx_t;

typedef struct
{
  uint32_t Resolution;
  uint32_t LightMode;
  uint32_t ColorEffect;
  uint32_t Brightness;
  uint32_t Saturation;
  uint32_t Contrast;
  uint32_t HueDegree;
  uint32_t MirrorFlip;
  uint32_t Zoom;
  uint32_t NightMode;
} CAMERA_Capabilities_t;

/* Local variables -----------------------------------------------------------*/
extern MDMA_HandleTypeDef hmdma;

/* Public functions ----------------------------------------------------------*/
int32_t BSP_CAMERA_DCMI_Resume();
int32_t BSP_CAMERA_DCMI_Suspend();
int32_t BSP_CAMERA_DCMI_PwrDown();
int32_t BSP_CAMERA_DCMI_Init(uint32_t Resolution, uint32_t Pixel_Format);
int32_t BSP_CAMERA_DCMI_Set_Crop();
int32_t BSP_CAMERA_DCMI_StartCapture(uint8_t *camera_capture_buffer);
int32_t BSP_CAMERA_DCMI_Set_MirrorFlip(uint32_t Mirror_Flip);
int32_t BSP_CAMERA_DCMI_Set_TestBar(uint32_t Do_Testbar);
int32_t BSP_CAMERA_DCMI_HwReset();

void BSP_CAMERA_DCMI_IRQHandler();
void BSP_CAMERA_DCMI_DMA_IRQHandler();

#endif /* __NUCLEO_H743ZI2_CAMERA_DCMI_H */
