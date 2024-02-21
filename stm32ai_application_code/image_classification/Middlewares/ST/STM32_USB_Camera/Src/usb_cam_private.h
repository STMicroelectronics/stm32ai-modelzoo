 /**
 ******************************************************************************
 * @file    usb_cam_private.h
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
#ifndef USB_CAM_PRIVATE
#define USB_CAM_PRIVATE 1

#include <stddef.h>
#include <stdint.h>

#include "usbh_def.h"
#include "usb_cam.h"

#define container_of(ptr, type, member) ({ \
  void *__mptr = (ptr); \
  __mptr - offsetof(type,member); \
})

#define UVC_VERSION_UNKNOWN 0x0000
#define UVC_VERSION_1_0 0x0100
#define UVC_VERSION_1_1 0x0110
#define UVC_VERSION_1_5 0x0150

#define USB_CAM_MAX_BUFFER 2
#define USB_CAM_MAX_PACKET_SIZE 1023

typedef struct
{
  uint16_t bmHint;
  uint8_t bFormatIndex;
  uint8_t bFrameIndex;
  uint32_t dwFrameInterval;
  uint16_t wKeyFrameRate;
  uint16_t wPFrameRate;
  uint16_t wCompQuality;
  uint16_t wCompWindowSize;
  uint16_t wDelay;
  uint32_t dwMaxVideoFrameSize;
  uint32_t dwMaxPayloadTransferSize;
} __PACKED USB_DISP_VideoControlTypeDefV10;

typedef struct
{
  uint16_t bmHint;
  uint8_t bFormatIndex;
  uint8_t bFrameIndex;
  uint32_t dwFrameInterval;
  uint16_t wKeyFrameRate;
  uint16_t wPFrameRate;
  uint16_t wCompQuality;
  uint16_t wCompWindowSize;
  uint16_t wDelay;
  uint32_t dwMaxVideoFrameSize;
  uint32_t dwMaxPayloadTransferSize;
  uint32_t dwClockFrequency;
  uint8_t bmFramingInfo;
  uint8_t bPreferedVersion;
  uint8_t bMinVersion;
  uint8_t bMaxVersion;
} __PACKED USB_DISP_VideoControlTypeDefV11;

typedef union {
  USB_DISP_VideoControlTypeDefV10 v10;
  USB_DISP_VideoControlTypeDefV11 v11;
} USB_DISP_VideoControlTypeDef;

typedef enum {
  SETUP_STATE_SET_VS_ITF,
  SETUP_STATE_SETCUR_PROBE,
  SETUP_STATE_GETCUR_PROBE,
  SETUP_STATE_SETCUR_COMMIT,
  SETUP_STATE_SET_VS_ALT_ITF,
  SETUP_STATE_LAST_STATE,
} ENUM_SetupState;

typedef enum {
  BUF_STATE_UNAVAILABLE,
  BUF_STATE_AVAILABLE,
  BUF_STATE_CAPTURING,
  BUF_STATE_READY,
} ENUM_BufferState;

typedef struct {
  uint8_t bInterfaceNumber;
  uint8_t bFormatIndex;
  uint8_t bFrameIndex;
  uint32_t dwFrameInterval;
  uint8_t bAlternateSetting;
  uint8_t bEndpointAddress;
} USB_CAM_Info_t;

typedef struct
{
  volatile ENUM_BufferState state;
  uint8_t *data;
  int len;
  int has_error;
  int rx_pos;
} USB_CAM_Buffer_t;

typedef struct {
  USBH_HandleTypeDef hUSBHost;
  int width;
  int height;
  int period;
  int payload_type;
  USB_CAM_Info_t info;
  uint16_t bcdUVC;
  uint8_t data_pipe;
  int is_capture_ongoing;
  ENUM_SetupState setup_state;
  USB_DISP_VideoControlTypeDef probe;
  USB_DISP_VideoControlTypeDef commit;
  int frame_id;
  /* iso capture buffer */
  int next_packet_buffer_idx;
  uint8_t packet_buffer[2][USB_CAM_MAX_PACKET_SIZE];
  /* user buffer handling */
  USB_CAM_Buffer_t buffer[USB_CAM_MAX_BUFFER];
  int capture_idx;
  int push_idx;
  int pop_idx;
} USB_CAM_Ctx_t;

static USB_CAM_Ctx_t *USB_CAM_USBH2Ctx(USBH_HandleTypeDef *from)
{
  return container_of(from, USB_CAM_Ctx_t, hUSBHost);
}

#endif