/**
 ******************************************************************************
 * @file    usb_disp_format.h
 * @author  GPM Application Team
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

#ifndef USB_DISP_FORMAT
#define USB_DISP_FORMAT 1

#include <stdint.h>

void USB_DISP_FormatInit(void);
void USB_DISP_FormatGreyToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height);
void USB_DISP_FormatArgbToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height);
void USB_DISP_FormatRgb565ToYuv422(uint8_t *p_dst, uint8_t *p_src, int width, int height);
void USB_DISP_FormatGreyToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height);
void USB_DISP_FormatRgbArgbToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height);
void USB_DISP_FormatRgb565ToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height);
void USB_DISP_FormatYuv422ToYuv422Jpeg(uint8_t *p_dst, uint8_t *p_src, int width, int height);

#endif
