 /**
 ******************************************************************************
 * @file    nucleo_h743zi2_display_usb.h
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

#ifndef __NUCLEO_H743ZI2_DISPLAY_USB_H
#define __NUCLEO_H743ZI2_DISPLAY_USB_H

/* Includes ------------------------------------------------------------------*/
#include "nucleo_h743zi2_lcd.h"
#include "lcd.h"

/* Public functions ----------------------------------------------------------*/
/* Initialization APIs */
int BSP_DISPLAY_USB_Init(uint32_t Orientation, void (*cb)(uint8_t *p_frame, void *cb_args));
int BSP_DISPLAY_USB_ImageBufferRGB565(uint8_t *buffer);
int BSP_DISPLAY_USB_ImageBufferYUV422(uint8_t *buffer);

#endif /* __NUCLEO_H743ZI2_DISPLAY_USB_H */
