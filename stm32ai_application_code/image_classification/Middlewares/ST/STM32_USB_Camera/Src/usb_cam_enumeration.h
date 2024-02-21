 /**
 ******************************************************************************
 * @file    usb_cam_enumeration.h
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
#ifndef USB_CAM_ENUMERATION
#define USB_CAM_ENUMERATION 1

#include "usbh_def.h"

USBH_StatusTypeDef USB_CAM_ProcessEnumerationWrapper(USBH_HandleTypeDef *phost);

#endif