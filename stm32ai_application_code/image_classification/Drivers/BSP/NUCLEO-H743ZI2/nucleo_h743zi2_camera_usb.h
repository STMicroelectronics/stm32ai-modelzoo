 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_camera_usb.h
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

#ifndef __NUCLEO_H743ZI2_CAMERA_USB_H
#define __NUCLEO_H743ZI2_CAMERA_USB_H

/* Includes ------------------------------------------------------------------*/
#include "nucleo_h743zi2_camera.h"
#include "camera.h"

/* Public functions ----------------------------------------------------------*/
/* Initialization APIs */
int BSP_CAMERA_USB_Init(uint8_t *camera_buffer, volatile uint8_t *new_frame_ready_p);
int BSP_CAMERA_USB_StartCapture(void);
int BSP_CAMERA_USB_WaitForFrame(void);

#endif /* __NUCLEO_H743ZI2_CAMERA_USB_H */

