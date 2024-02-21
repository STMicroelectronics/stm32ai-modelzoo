 /**
 ******************************************************************************
 * @file    usb_cam.h
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
#ifndef USB_CAM
#define USB_CAM 1

#include <stdint.h>

typedef void * USB_CAM_Hdl_t;

#define USB_CAM_PAYLOAD_UNCOMPRESSED 0
#define USB_CAM_PAYLOAD_JPEG 1

typedef struct {
  void *p_hhcd; /**< Pointer on HCD_HandleTypeDef type for USB instance */
  int width; /**< Width of USB camera */
  int height; /**< Height of USB camera */
  int period; /**< Period of USB camera in 100 ns units */
  int payload_type; /**< Select USB camera payload type. Either USB_CAM_PAYLOAD_UNCOMPRESSED or
                         USB_CAM_PAYLOAD_JPEG */
} USB_CAM_Conf_t;

typedef struct {
  uint8_t *buffer; /**< buffer as push in USB_CAM_PushBuffer() call */
  int is_capture_error; /**< True when an error occured during capture */
  int len; /**< length in bytes of catured data */
} USB_CAM_CaptureInfo_t;

typedef struct {
  uint16_t idVendor; /**< USB vendor ID of detected device */
  uint16_t idProduct; /**< USB product ID of detected device */
} USB_CAM_DeviceInfo_t;

USB_CAM_Hdl_t USB_CAM_Init(USB_CAM_Conf_t *p_conf);
int USB_CAM_SetupDevice(USB_CAM_Hdl_t hdl, USB_CAM_DeviceInfo_t *p_info);
int USB_CAM_PushBuffer(USB_CAM_Hdl_t hdl, uint8_t *buffer, int len);
int USB_CAM_PopBuffer(USB_CAM_Hdl_t hdl, USB_CAM_CaptureInfo_t *p_info);

#endif