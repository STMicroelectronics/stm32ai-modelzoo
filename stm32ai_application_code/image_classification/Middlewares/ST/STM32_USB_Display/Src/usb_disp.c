/**
 ******************************************************************************
 * @file    usb_disp.c
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

#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <usb_disp.h>
#include "usbd_conf.h"
#include "usbd_core.h"
#include "usbd_def.h"

#include "usb_disp_desc.h"
#include "usb_disp_format.h"
#include "usb_disp_uvc.h"

#define USB_DISP_MAX_CTX 2

#define JPEG_TIMEOUT 2000

#define UVC_BULK_FS_MPS 64
#define UVC_BULK_HS_MPS 512
#define UVC_ISO_FS_MPS 1023
#define UVC_ISO_HS_MPS 1024
#define UVC_INTERVAL(n) (10000000U/(n))

#ifndef WBVAL
#define WBVAL(x) ((uint8_t)((x) & 0x00FFU)), ((uint8_t)(((x) & 0xFF00U) >> 8U))
#endif /* WBVAL */

#ifndef DBVAL
#define DBVAL(x) ((uint8_t)((x) & 0x00FFU)), ((uint8_t)(((x) & 0xFF00U) >> 8U)), ((uint8_t)(((x) & 0xFF0000U) >> 16U)), ((uint8_t)(((x) & 0xFF000000U) >> 24U))
#endif /* DBVAL */

#include "usb_disp_conf_desc.h"

#define container_of(ptr, type, member) ({ \
  void *__mptr = (ptr); \
  __mptr - offsetof(type,member); \
})

typedef enum {
  USB_DISP_STATUS_STOP,
  USB_DISP_STATUS_STREAMING,
} USB_DISP_DisplayState_t;

typedef enum {
  USB_DISP_FRAME_DISABLED,
  USB_DISP_FRAME_FREE,
  USB_DISP_FRAME_READY,
  USB_DISP_FRAME_IN_DISPLAY,
  USB_DISP_FRAME_IN_DISPLAY_FREE,
} USB_DISP_FrameState_t;

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
} __PACKED USB_DISP_VideoControlTypeDef;

typedef struct {
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bDescriptorSubType;
  uint8_t bFrameIndex;
  uint8_t bmCapabilities;
  uint16_t wWidth;
  uint16_t wHeight;
  uint32_t dwMinBitRate;
  uint32_t dwMaxBitRate;
  uint32_t dwMaxVideoFrameBufferSize;
  uint32_t dwDefaultFrameInterval;
  uint8_t bFrameIntervalType;
  uint32_t dwFrameInterval[1];
} __PACKED USB_DISP_FrameDesc;

typedef struct {
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bDescriptorSubType;
  uint8_t bFormatIndex;
  uint8_t bNumFrameDescriptors;
  uint8_t guidFormat[16];
  uint8_t bBitsPerPixel;
  uint8_t bDefaultFrameIndex;
  uint8_t bAspectRatioX;
  uint8_t bAspectRatioY;
  uint8_t bmInterlaceFlags;
  uint8_t bCopyProtect;
  uint8_t bVariableSize;
} __PACKED USB_DISP_FbFormatDesc;

typedef struct {
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bDescriptorSubType;
  uint8_t bFrameIndex;
  uint8_t bmCapabilities;
  uint16_t wWidth;
  uint16_t wHeight;
  uint32_t dwMinBitRate;
  uint32_t dwMaxBitRate;
  uint32_t dwDefaultFrameInterval;
  uint8_t bFrameIntervalType;
  uint32_t dwBytesPerLine;
  uint32_t dwFrameInterval[1];
} __PACKED USB_DISP_FbFrameDesc;

#ifdef HAL_JPEG_MODULE_ENABLED
typedef struct {
  JPEG_HandleTypeDef *p_hjpeg;
  uint8_t *p_jpeg_scratch_buffer;
  int mcu_line_size;
  uint8_t *p_frame_pos;
  int frame_pitch;
  int line_nb;
  int *p_fsize;
  void (*cvt)(uint8_t *p_dst, uint8_t *p_src, int width, int height);
} USB_DISP_JpgCtx_t;
#endif

typedef struct USB_DISP_OnFlyCtx {
  int frame_index;
  uint8_t *cursor;
  int packet_nb;
  int packet_index;
  int last_packet_size;
  int prev_len;
  void (*cb_raw)(uint8_t *, void *);
  void *cb_args_raw;
  uint8_t *p_frame_raw;
} USB_DISP_OnFlyCtx_t;

typedef struct USB_DISP_DisplayCtx {
  int is_iso;
  int width;
  int height;
  int fps_fs;
  int fps_hs;
  int frame_buffer_size;
  int mode;
  int payload_type;
  int input_format_hint;
  uint8_t interface;
  USBD_HandleTypeDef usbd_dev;
  int is_starting;
  USB_DISP_DisplayState_t state;
  uint8_t packet[1024];
  uint8_t *frames[2];
  USB_DISP_FrameState_t fstate[2];
  int fsize[2];
  uint32_t findex[2];
  uint32_t push_index;
  uint8_t *p_frame_raw;
  int frame_size_raw;
  void (*cb_raw)(uint8_t *, void *);
  void *cb_args_raw;
  USB_DISP_OnFlyCtx_t on_fly_storage_ctx;
  USB_DISP_OnFlyCtx_t *on_fly_ctx;
  int frame_period_in_ms;
  uint32_t frame_start;
  int ep_addr;
  uint32_t ctl_buffer;
#ifdef HAL_JPEG_MODULE_ENABLED
  /* jpg context */
  USB_DISP_JpgCtx_t jpg_ctx;
#endif
  /* cvt fct */
  int (*cvtGreyToPayload)(struct USB_DISP_DisplayCtx *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height, int *fsize);
  int (*cvtArgbToPayload)(struct USB_DISP_DisplayCtx *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height, int *fsize);
  int (*cvtRgb565ToPayload)(struct USB_DISP_DisplayCtx *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height, int *fsize);
  int (*cvtYuv422ToPayload)(struct USB_DISP_DisplayCtx *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height, int *fsize);
} USB_DISP_DisplayCtx_t;

/* forward declaration */
static USBD_ClassTypeDef USB_DISP_Class;
static uint8_t USB_DISP_DataIn(USBD_HandleTypeDef *pdev, uint8_t epnum);

static USB_DISP_DisplayCtx_t *CtxArray[USB_DISP_MAX_CTX];

/* USB Standard Device Descriptor */
static uint8_t USB_DISP_DeviceQualifierDesc[USB_LEN_DEV_QUALIFIER_DESC] =
{
  USB_LEN_DEV_QUALIFIER_DESC,
  USB_DESC_TYPE_DEVICE_QUALIFIER,
  0x00,
  0x02,
  0xEF,
  0x02,
  0x01,
  0x40,
  0x01,
  0x00,
};

static USB_DISP_VideoControlTypeDef USB_DISP_VideoCommitControl =
{
  .bmHint = 0x0000U,
  .bFormatIndex = 0x01U,
  .bFrameIndex = 0x01U,
  .dwFrameInterval = UVC_INTERVAL(30),
  .wKeyFrameRate = 0x0000U,
  .wPFrameRate = 0x0000U,
  .wCompQuality = 0x0000U,
  .wCompWindowSize = 0x0000U,
  .wDelay = 0x0000U,
  .dwMaxVideoFrameSize = 0x0000U,
  .dwMaxPayloadTransferSize = 0x00000000U,
  .dwClockFrequency = 0x00000000U,
  .bmFramingInfo = 0x00U,
  .bPreferedVersion = 0x00U,
  .bMinVersion = 0x00U,
  .bMaxVersion = 0x00U,
};

static USB_DISP_VideoControlTypeDef USB_DISP_VideoProbeControl =
{
  .bmHint = 0x0000U,
  .bFormatIndex = 0x01U,
  .bFrameIndex = 0x01U,
  .dwFrameInterval = UVC_INTERVAL(30),
  .wKeyFrameRate = 0x0000U,
  .wPFrameRate = 0x0000U,
  .wCompQuality = 0x0000U,
  .wCompWindowSize = 0x0000U,
  .wDelay = 0x0000U,
  .dwMaxVideoFrameSize = 0x0000U,
  .dwMaxPayloadTransferSize = 0x00000000U,
  .dwClockFrequency = 0x00000000U,
  .bmFramingInfo = 0x00U,
  .bPreferedVersion = 0x00U,
  .bMinVersion = 0x00U,
  .bMaxVersion = 0x00U,
};

static int USB_DISP_GetBpp(int payload_type)
{
  switch (payload_type) {
  case USB_DISP_PAYLOAD_UNCOMPRESSED:
    return 16;
    break;
  case USB_DISP_PAYLOAD_JPEG:
    return 0;
    break;
  case USB_DISP_PAYLOAD_FB_RGB565:
    return 16;
    break;
  case USB_DISP_PAYLOAD_FB_BGR3:
    return 24;
    break;
  case USB_DISP_PAYLOAD_FB_GREY:
    return 8;
    break;
  case USB_DISP_PAYLOAD_FB_H264:
    return 0;
    break;
  default:
    assert(0);
  }
}

static int USB_DISP_GetBufferNb(int mode)
{
  switch (mode) {
  case USB_DISP_MODE_LCD:
  case USB_DISP_MODE_ON_DEMAND:
    return 2;
  case USB_DISP_MODE_LCD_SINGLE_BUFFER:
  case USB_DISP_MODE_ON_DEMAND_SINGLE_BUFFER:
    return 1;
  case USB_DISP_MODE_RAW:
    return 0;
  default:
    assert(0);
  }

  return 0;
}

static int USB_DISP_IsFbPayload(int payload_type)
{
  if (payload_type < USB_DISP_PAYLOAD_FB_RGB565)
    return 0;

  return 1;
}

static int USB_DISP_RegisterCtx(USB_DISP_DisplayCtx_t *p_ctx)
{
  int i;

  for (i = 0; i < USB_DISP_MAX_CTX; i++)
  {
    if (!CtxArray[i])
      break;
  }

  if (i == USB_DISP_MAX_CTX)
    return -1;

  CtxArray[i] = p_ctx;

  return 0;
}

#ifdef HAL_JPEG_MODULE_ENABLED
static USB_DISP_DisplayCtx_t *USB_DISP_Jpeg2DispCtx(JPEG_HandleTypeDef *hjpeg)
{
  int i;

  for (i = 0; i < USB_DISP_MAX_CTX; i++)
  {
    if (CtxArray[i] && CtxArray[i]->jpg_ctx.p_hjpeg == hjpeg)
      return CtxArray[i];
  }

  assert(0);
}
#endif

static void *USB_DISP_GetConfDesc(USBD_SpeedTypeDef dev_speed)
{
  uint16_t len;

  return dev_speed == USBD_SPEED_HIGH ? USB_DISP_Class.GetHSConfigDescriptor(&len) :
                                        USB_DISP_Class.GetFSConfigDescriptor(&len);
}

static USBD_EpDescTypeDef *USB_DISP_GetEpDesc(USBD_SpeedTypeDef dev_speed)
{
  USBD_ConfigDescTypeDef *p_desc = (USBD_ConfigDescTypeDef *) USB_DISP_GetConfDesc(dev_speed);
  USBD_DescHeaderTypeDef *p_desc_hdr = (USBD_DescHeaderTypeDef *) USB_DISP_GetConfDesc(dev_speed);
  USBD_EpDescTypeDef *p_ep_desc = NULL;
  uint16_t ptr;

  if (p_desc->wTotalLength <= p_desc->bLength)
  {
    return NULL;
  }

  ptr = p_desc->bLength;
  while (ptr < p_desc->wTotalLength)
  {
    p_desc_hdr = USBD_GetNextDesc((uint8_t *)p_desc_hdr, &ptr);
    if (p_desc_hdr->bDescriptorType == USB_DESC_TYPE_ENDPOINT)
    {
      p_ep_desc = (USBD_EpDescTypeDef *)p_desc_hdr;
      break;
    }
  }

  return p_ep_desc;
}

static USBD_DescHeaderTypeDef *USB_DISP_GetDesc(USBD_SpeedTypeDef dev_speed,
                                                int (*predicate)(USBD_DescHeaderTypeDef *p_desc_hdr))
{
  USBD_ConfigDescTypeDef *p_desc = (USBD_ConfigDescTypeDef *) USB_DISP_GetConfDesc(dev_speed);
  USBD_DescHeaderTypeDef *p_desc_hdr = (USBD_DescHeaderTypeDef *) USB_DISP_GetConfDesc(dev_speed);
  uint16_t ptr;

  if (p_desc->wTotalLength <= p_desc->bLength)
  {
    return NULL;
  }

  ptr = p_desc->bLength;
  while (ptr < p_desc->wTotalLength)
  {
    p_desc_hdr = USBD_GetNextDesc((uint8_t *)p_desc_hdr, &ptr);
    if (predicate(p_desc_hdr))
      return p_desc_hdr;
  }

  return NULL;
}

static int USBD_PredicateFrameDesc(USBD_DescHeaderTypeDef *p_desc_hdr)
{
  if (p_desc_hdr->bDescriptorType != CS_INTERFACE)
    return 0;

  if (p_desc_hdr->bDescriptorSubType != VS_FRAME_UNCOMPRESSED &&
      p_desc_hdr->bDescriptorSubType != VS_FRAME_MJPEG)
    return 0;

  return 1;
}

static USB_DISP_FrameDesc *USB_DISP_GetFrameDesc(USBD_SpeedTypeDef dev_speed)
{
  return (USB_DISP_FrameDesc *) USB_DISP_GetDesc(dev_speed, USBD_PredicateFrameDesc);
}

static int USBD_PredicateFbFormatDesc(USBD_DescHeaderTypeDef *p_desc_hdr)
{
  if (p_desc_hdr->bDescriptorType != CS_INTERFACE)
    return 0;

  if (p_desc_hdr->bDescriptorSubType != VS_FORMAT_FRAME_BASED)
    return 0;

  return 1;
}

static USB_DISP_FbFormatDesc *USB_DISP_GetFbFormatDesc(USBD_SpeedTypeDef dev_speed)
{
  return (USB_DISP_FbFormatDesc *) USB_DISP_GetDesc(dev_speed, USBD_PredicateFbFormatDesc);
}

static int USBD_PredicateFbFrameDesc(USBD_DescHeaderTypeDef *p_desc_hdr)
{
  if (p_desc_hdr->bDescriptorType != CS_INTERFACE)
    return 0;

  if (p_desc_hdr->bDescriptorSubType != VS_FRAME_FRAME_BASED)
    return 0;

  return 1;
}

static USB_DISP_FbFrameDesc *USB_DISP_GetFbFrameDesc(USBD_SpeedTypeDef dev_speed)
{
  return (USB_DISP_FbFrameDesc *) USB_DISP_GetDesc(dev_speed, USBD_PredicateFbFrameDesc);
}

static uint8_t USB_DISP_InitInstance(USBD_HandleTypeDef *p_dev, uint8_t cfgidx)
{
  USB_DISP_DisplayCtx_t *p_ctx = container_of(p_dev, USB_DISP_DisplayCtx_t, usbd_dev);
  USBD_EpDescTypeDef *ep_desc;
  int type = p_ctx->is_iso ? USBD_EP_TYPE_ISOC : USBD_EP_TYPE_BULK;
  int buffer_nb;
  int i;

  ep_desc = USB_DISP_GetEpDesc(p_dev->dev_speed);
  assert(ep_desc);

  p_ctx->ep_addr = ep_desc->bEndpointAddress;

  p_dev->pClassDataCmsit[p_dev->classId] = p_ctx;
  p_dev->pClassData = p_ctx;

  /* Open EP IN */
  USBD_LL_OpenEP(p_dev, p_ctx->ep_addr, type, ep_desc->wMaxPacketSize);
  p_dev->ep_in[p_ctx->ep_addr & 0xFU].is_used = 1U;
  p_dev->ep_in[p_ctx->ep_addr & 0xFU].maxpacket = ep_desc->wMaxPacketSize;

  /* init context */
  p_ctx->interface = 0;
  p_ctx->state = USB_DISP_STATUS_STOP;
  buffer_nb = USB_DISP_GetBufferNb(p_ctx->mode);
  p_ctx->fstate[0] = USB_DISP_FRAME_DISABLED;
  p_ctx->fstate[1] = USB_DISP_FRAME_DISABLED;
  for (i = 0; i < buffer_nb; i++)
    p_ctx->fstate[i] = USB_DISP_FRAME_FREE;
  p_ctx->fsize[0] = 0;
  p_ctx->fsize[1] = 0;
  p_ctx->on_fly_ctx = NULL;
  p_ctx->frame_period_in_ms = 1000 / (p_dev->dev_speed == USBD_SPEED_HIGH ? p_ctx->fps_hs : p_ctx->fps_fs);
  p_ctx->frame_start = 0;
  p_ctx->push_index = 0;

  return USBD_OK;
}

static uint8_t USB_DISP_DeInit(USBD_HandleTypeDef *p_dev, uint8_t cfgidx)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];

  /* DeInit can be called whereas InitInstance has not yet be called */
  if (!p_ctx)
    return USBD_OK;

  USBD_LL_CloseEP(p_dev, p_ctx->ep_addr);
  p_dev->ep_in[p_ctx->ep_addr & 0xFU].is_used = 0U;

  p_dev->pClassDataCmsit[p_dev->classId] = NULL;
  p_dev->pClassData = NULL;
  p_dev->classId = 0;

  return USBD_OK;
}

static void USB_DISP_StartStreaming(USBD_HandleTypeDef *p_dev)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];

  USBD_LL_FlushEP(p_dev, p_ctx->ep_addr);
  p_ctx->packet[0] = 2;
  p_ctx->packet[1] = 0;
  p_ctx->frame_start = HAL_GetTick() - p_ctx->frame_period_in_ms;
  p_ctx->is_starting = 1;
  p_ctx->state = USB_DISP_STATUS_STREAMING;
  USB_DISP_DataIn(p_dev, p_ctx->ep_addr & 0xF);
}

static void USB_DISP_StopStreaming(USBD_HandleTypeDef *p_dev)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];
  int buffer_nb = USB_DISP_GetBufferNb(p_ctx->mode);
  int i;

  p_ctx->state = USB_DISP_STATUS_STOP;
  for (i = 0; i < buffer_nb; i++)
    p_ctx->fstate[i] = USB_DISP_FRAME_FREE;
  USBD_LL_FlushEP(p_dev, p_ctx->ep_addr);
}

static uint8_t USB_DISP_HandleProbeControlGet(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];
  int dwMaxBulkPayloadTransferSize = 1024;
  int dwMaxIsoPayloadTransferSize = p_dev->dev_speed == USBD_SPEED_HIGH ? UVC_ISO_HS_MPS : UVC_ISO_FS_MPS;
  int dwMaxPayloadTransferSize = p_ctx->is_iso ? dwMaxIsoPayloadTransferSize : dwMaxBulkPayloadTransferSize;

  USB_DISP_VideoProbeControl.dwFrameInterval = p_dev->dev_speed == USBD_SPEED_HIGH ? UVC_INTERVAL(p_ctx->fps_hs) :
                                                                                    UVC_INTERVAL(p_ctx->fps_fs);
  USB_DISP_VideoProbeControl.dwMaxVideoFrameSize = p_ctx->width * p_ctx->height * 2;
  USB_DISP_VideoProbeControl.dwMaxPayloadTransferSize = dwMaxPayloadTransferSize;
  USB_DISP_VideoProbeControl.dwClockFrequency = 48000000;
  /* should not zero but not clear what value is possible for uncompressed format */
  USB_DISP_VideoProbeControl.bPreferedVersion = 0x00U;
  USB_DISP_VideoProbeControl.bMinVersion = 0x00U;
  USB_DISP_VideoProbeControl.bMaxVersion = 0x00U;

  USBD_CtlSendData(p_dev, (uint8_t *)&USB_DISP_VideoProbeControl,
                   MIN(p_req->wLength, sizeof(USB_DISP_VideoControlTypeDef)));

  return USBD_OK;
}

static uint8_t USB_DISP_HandleProbeControl(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];
  int ret = USBD_OK;

  switch (p_req->bRequest)
  {
    case UVC_GET_DEF:
    case UVC_GET_MIN:
    case UVC_GET_MAX:
    case UVC_GET_CUR:
      ret = USB_DISP_HandleProbeControlGet(p_dev, p_req);
      break;
    case UVC_SET_CUR:
      USBD_CtlPrepareRx(p_dev, (uint8_t *)&USB_DISP_VideoProbeControl,
                        MIN(p_req->wLength, sizeof(USB_DISP_VideoControlTypeDef)));
      break;
    case UVC_GET_RES:
      /* FIXME : not clear what to report here ..... */
      break;
    case UVC_GET_LEN:
      p_ctx->ctl_buffer = sizeof(USB_DISP_VideoControlTypeDef);
      USBD_CtlSendData(p_dev, (uint8_t *)&p_ctx->ctl_buffer, 2);
      break;
    case UVC_GET_INFO:
      p_ctx->ctl_buffer = 0x03;
      USBD_CtlSendData(p_dev, (uint8_t *)&p_ctx->ctl_buffer, 1);
      break;
    default:
      USBD_CtlError(p_dev, p_req);
      ret = USBD_FAIL;
      break;
  }

  return ret;
}

static uint8_t USB_DISP_HandleCommitControl(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];
  int ret = USBD_OK;

  switch (p_req->bRequest)
  {
    case UVC_GET_CUR:
      USBD_CtlSendData(p_dev, (uint8_t *)&USB_DISP_VideoCommitControl,
           MIN(p_req->wLength, sizeof(USB_DISP_VideoControlTypeDef)));
      break;
    case UVC_SET_CUR:
      USBD_CtlPrepareRx(p_dev, (uint8_t *)&USB_DISP_VideoCommitControl,
            MIN(p_req->wLength, sizeof(USB_DISP_VideoControlTypeDef)));
      if (!p_ctx->is_iso)
        USB_DISP_StartStreaming(p_dev);
      break;
    case UVC_GET_INFO:
      p_ctx->ctl_buffer = 0x03;
      USBD_CtlSendData(p_dev, (uint8_t *)&p_ctx->ctl_buffer, 1);
      break;
    default:
      USBD_CtlError(p_dev, p_req);
      ret = USBD_FAIL;
      break;
  }

  return ret;
}

static uint8_t USB_DISP_HandleSetupClassItf(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  int ret = USBD_OK;
  int itf_nb = p_req->wIndex;
  int cs = HIBYTE(p_req->wValue);

  /* no control for vc itf */
  if (!itf_nb)
  {
    USBD_CtlError(p_dev, p_req);
    return USBD_FAIL;
  }

  switch (cs)
  {
    case VS_PROBE_CONTROL_CS:
      ret = USB_DISP_HandleProbeControl(p_dev, p_req);
      break;
    case VS_COMMIT_CONTROL_CS:
      ret = USB_DISP_HandleCommitControl(p_dev, p_req);
      break;
    default:
      USBD_CtlError(p_dev, p_req);
      ret = USBD_FAIL;
      break;
  }

  return ret;
}

static uint8_t USB_DISP_HandleSetItfIso(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];
  int ret = USBD_OK;

  switch (p_req->wValue)
  {
    case 0:
      /* setup alternate 0 which as 0 bandwidth => stop streaming */
      p_ctx->interface = 0;
      USB_DISP_StopStreaming(p_dev);
      break;
    case 1:
      /* setup alternate 1 => start streaming */
      p_ctx->interface = 1;
      USB_DISP_StartStreaming(p_dev);
      break;
    default:
      USBD_CtlError(p_dev, p_req);
      ret = USBD_FAIL;
  }

  return ret;
}

static uint8_t USB_DISP_HandleSetItfBulk(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  if (p_req->wValue)
  {
    USBD_CtlError(p_dev, p_req);
    return USBD_FAIL;
  }
  else
  {
    /* nop */
    return USBD_OK;
  }
}

static uint8_t USB_DISP_HandleSetupStdItf(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];
  int ret = USBD_OK;

  switch (p_req->bRequest)
  {
    case USB_REQ_GET_STATUS:
      p_ctx->ctl_buffer = 0;
      USBD_CtlSendData(p_dev, (uint8_t *)&p_ctx->ctl_buffer, 2);
      break;
    case USB_REQ_CLEAR_FEATURE:
      /* nop */
      break;
    case USB_REQ_SET_FEATURE:
      /* nop */
      break;
    case USB_REQ_GET_INTERFACE:
      USBD_CtlSendData(p_dev, &p_ctx->interface, 1);
      break;
    case USB_REQ_SET_INTERFACE:
      if (p_ctx->is_iso)
        ret = USB_DISP_HandleSetItfIso(p_dev, p_req);
      else
        ret = USB_DISP_HandleSetItfBulk(p_dev, p_req);
      break;
    default:
      USBD_CtlError(p_dev, p_req);
      ret = USBD_FAIL;
      break;
  }

  return ret;
}

static uint8_t USB_DISP_HandleSetupItf(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  int ret = USBD_OK;

  switch (p_req->bmRequest & USB_REQ_TYPE_MASK)
  {
    case USB_REQ_TYPE_CLASS:
      ret = USB_DISP_HandleSetupClassItf(p_dev, p_req);
      break;
    case USB_REQ_TYPE_STANDARD:
      ret = USB_DISP_HandleSetupStdItf(p_dev, p_req);
      break;
    default:
      USBD_CtlError(p_dev, p_req);
      ret = USBD_FAIL;
      break;
  }

  return ret;
}

static uint8_t USB_DISP_Setup(USBD_HandleTypeDef *p_dev, USBD_SetupReqTypedef *p_req)
{
  int ret = USBD_OK;

  switch (p_req->bmRequest & 0x1f)
  {
    case USB_REQ_RECIPIENT_INTERFACE:
      ret = USB_DISP_HandleSetupItf(p_dev, p_req);
      break;
    case USB_REQ_RECIPIENT_DEVICE:
    case USB_REQ_RECIPIENT_ENDPOINT:
    default:
      USBD_CtlError(p_dev, p_req);
      ret = USBD_FAIL;
      break;
  }

  return ret;
}

static int USB_DISP_FpsOk(USB_DISP_DisplayCtx_t *p_ctx)
{
  if (HAL_GetTick() - p_ctx->frame_start >= p_ctx->frame_period_in_ms)
  {
    return 1;
  }

  return 0;
}

static void USB_DISP_FillSentData(USB_DISP_DisplayCtx_t *p_ctx, USB_DISP_OnFlyCtx_t *on_fly_ctx, uint8_t *p_frame,
                                  int fsize, int packet_size)
{
  on_fly_ctx->packet_nb = (fsize + packet_size - 1) / (packet_size - 2);
  on_fly_ctx->last_packet_size = fsize % (packet_size - 2);
  if (!on_fly_ctx->last_packet_size)
  {
    on_fly_ctx->packet_nb--;
    on_fly_ctx->last_packet_size = packet_size - 2;
  }
  on_fly_ctx->cursor = p_frame;
  p_ctx->packet[1] ^= 1;

  p_ctx->is_starting = 0;
  p_ctx->frame_start = HAL_GetTick();
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartSelected(USB_DISP_DisplayCtx_t *p_ctx, int idx, int packet_size,
                                                   USB_DISP_FrameState_t buffer_state)
{
  USB_DISP_OnFlyCtx_t *on_fly_ctx = &p_ctx->on_fly_storage_ctx;

  p_ctx->fstate[idx] = buffer_state;
  on_fly_ctx->frame_index = idx;
  USB_DISP_FillSentData(p_ctx, on_fly_ctx, p_ctx->frames[idx], p_ctx->fsize[idx], packet_size);

  return on_fly_ctx;
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartSelectedRaw(USB_DISP_DisplayCtx_t *p_ctx, int packet_size)
{
  USB_DISP_OnFlyCtx_t *on_fly_ctx = &p_ctx->on_fly_storage_ctx;

  on_fly_ctx->frame_index = -1;
  USB_DISP_FillSentData(p_ctx, on_fly_ctx, p_ctx->p_frame_raw, p_ctx->frame_size_raw, packet_size);

  on_fly_ctx->cb_raw = p_ctx->cb_raw;
  on_fly_ctx->cb_args_raw = p_ctx->cb_args_raw;
  __DMB();
  p_ctx->p_frame_raw = NULL;

  return on_fly_ctx;
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartLcd(USB_DISP_DisplayCtx_t *p_ctx, int packet_size)
{
  int is_fps_ok = USB_DISP_FpsOk(p_ctx);
  int ready_idx = -1;
  int in_display_idx = -1;
  int idx;
  int i;

  if (p_ctx->is_starting == 0 && !is_fps_ok)
    return NULL;

  /* get ready index */
  for (i = 0; i < 2; i++) {
    if (p_ctx->fstate[i] != USB_DISP_FRAME_READY)
      continue;
    ready_idx = i;
    break;
  }

  /* get display index */
  for (i = 0; i < 2; i++) {
    if (p_ctx->fstate[i] != USB_DISP_FRAME_IN_DISPLAY)
      continue;
    in_display_idx = i;
    break;
  }

  if (p_ctx->is_starting) {
    if (ready_idx < 0)
      return NULL;
    idx = ready_idx;
  } else {
    idx = ready_idx >= 0 ? ready_idx : in_display_idx;
  }

  assert(idx == 0 || idx == 1);

  p_ctx->fstate[1 - idx] = USB_DISP_FRAME_FREE;

  return USB_DISP_StartSelected(p_ctx, idx, packet_size, USB_DISP_FRAME_IN_DISPLAY);
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartLcdSingleBuffer(USB_DISP_DisplayCtx_t *p_ctx, int packet_size)
{
  USB_DISP_FrameState_t buffer_next_state;
  int is_fps_ok = USB_DISP_FpsOk(p_ctx);

  if (p_ctx->is_starting == 0 && !is_fps_ok)
    return NULL;

  /* once we have displayed frame 0, we continuously displayed it */
  if (p_ctx->is_starting == 1 && p_ctx->fstate[0] != USB_DISP_FRAME_READY)
    return NULL;

  buffer_next_state = p_ctx->fstate[0] == USB_DISP_FRAME_IN_DISPLAY_FREE ? USB_DISP_FRAME_IN_DISPLAY_FREE :
                                                                           USB_DISP_FRAME_IN_DISPLAY;

  return USB_DISP_StartSelected(p_ctx, 0, packet_size, buffer_next_state);
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartOnDemand(USB_DISP_DisplayCtx_t *p_ctx, int packet_size)
{
  int is_fps_ok = USB_DISP_FpsOk(p_ctx);
  uint32_t min_push_idx = 0xffffffff;
  int select_idx = -1;
  int i;

  if (p_ctx->is_starting == 0 && !is_fps_ok)
    return NULL;

  /* select ready frame that was pushed first */
  for (i = 0; i < 2; i++) {
    if (p_ctx->fstate[i] != USB_DISP_FRAME_READY)
      continue;
    if (p_ctx->findex[i] > min_push_idx)
      continue;

    select_idx = i;
    min_push_idx = p_ctx->findex[i];
  }

  if (select_idx < 0)
    return NULL;

  return USB_DISP_StartSelected(p_ctx, select_idx, packet_size, USB_DISP_FRAME_IN_DISPLAY);
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartOnDemandSingleBuffer(USB_DISP_DisplayCtx_t *p_ctx, int packet_size)
{
  int is_fps_ok = USB_DISP_FpsOk(p_ctx);

  if (p_ctx->is_starting == 0 && !is_fps_ok)
    return NULL;

  if (p_ctx->fstate[0] != USB_DISP_FRAME_READY)
    return NULL;

  return USB_DISP_StartSelected(p_ctx, 0, packet_size, USB_DISP_FRAME_IN_DISPLAY);
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartRaw(USB_DISP_DisplayCtx_t *p_ctx, int packet_size)
{
  int is_fps_ok = USB_DISP_FpsOk(p_ctx);

  if (p_ctx->is_starting == 0 && !is_fps_ok)
    return NULL;

  if (!p_ctx->p_frame_raw)
    return NULL;

  return USB_DISP_StartSelectedRaw(p_ctx, packet_size);
}

static USB_DISP_OnFlyCtx_t *USB_DISP_StartNewFrameTransmission(USB_DISP_DisplayCtx_t *p_ctx, int packet_size)
{
  switch (p_ctx->mode) {
  case USB_DISP_MODE_LCD:
    return USB_DISP_StartLcd(p_ctx, packet_size);
  case USB_DISP_MODE_ON_DEMAND:
    return USB_DISP_StartOnDemand(p_ctx, packet_size);
  case USB_DISP_MODE_LCD_SINGLE_BUFFER:
    return USB_DISP_StartLcdSingleBuffer(p_ctx, packet_size);
  case USB_DISP_MODE_ON_DEMAND_SINGLE_BUFFER:
    return USB_DISP_StartOnDemandSingleBuffer(p_ctx, packet_size);
  case USB_DISP_MODE_RAW:
    return USB_DISP_StartRaw(p_ctx, packet_size);
  default:
    assert(0);
    break;
  }

  return NULL;
}

static void USB_DISP_UpdateOnFlyCtx(USB_DISP_DisplayCtx_t *p_ctx, int len)
{
  USB_DISP_OnFlyCtx_t *on_fly_ctx = p_ctx->on_fly_ctx;

  assert(on_fly_ctx);

  on_fly_ctx->packet_index = (on_fly_ctx->packet_index + 1) % on_fly_ctx->packet_nb;
  on_fly_ctx->cursor += len - 2;
  on_fly_ctx->prev_len = len;

  if (on_fly_ctx->packet_index)
    return ;

  /* Once displayed we can make frame free */
  if (p_ctx->mode == USB_DISP_MODE_ON_DEMAND) {
    p_ctx->fstate[on_fly_ctx->frame_index] = USB_DISP_FRAME_FREE;
  } else if (p_ctx->mode == USB_DISP_MODE_LCD_SINGLE_BUFFER) {
    p_ctx->fstate[0] = USB_DISP_FRAME_IN_DISPLAY_FREE;
  } else if (p_ctx->mode == USB_DISP_MODE_ON_DEMAND_SINGLE_BUFFER) {
    p_ctx->fstate[0] = USB_DISP_FRAME_FREE;
  } else if (p_ctx->mode == USB_DISP_MODE_RAW) {
    on_fly_ctx->cb_raw(on_fly_ctx->p_frame_raw, on_fly_ctx->cb_args_raw);
  }

  /* We reach last packet */
  p_ctx->on_fly_ctx = NULL;
}

static uint8_t USB_DISP_DataInImpl(USBD_HandleTypeDef *p_dev, uint8_t epnum, int is_incomplete)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];
  int packet_size_bulk = 1024;
  int packet_size_iso = p_dev->dev_speed == USBD_SPEED_HIGH ? UVC_ISO_HS_MPS : UVC_ISO_FS_MPS;
  int packet_size = p_ctx->is_iso ? packet_size_iso : packet_size_bulk;
  USB_DISP_OnFlyCtx_t *on_fly_ctx;
  int len;

  if (p_ctx->state != USB_DISP_STATUS_STREAMING)
  {
    return USBD_OK;
  }

  /* retransmit prev packet */
  if (is_incomplete)
  {
    len = p_ctx->on_fly_ctx ? p_ctx->on_fly_ctx->prev_len : 0;
    USBD_LL_Transmit(p_dev, p_ctx->ep_addr, p_ctx->packet, len);

    return USBD_OK;
  }

  /* select new frame */
  if (!p_ctx->on_fly_ctx)
    p_ctx->on_fly_ctx = USB_DISP_StartNewFrameTransmission(p_ctx, packet_size);

  /* no new frame send empty packet */
  if (!p_ctx->on_fly_ctx) {
    USBD_LL_Transmit(p_dev, p_ctx->ep_addr, p_ctx->packet, 2);

    return USBD_OK;
  }

  /* Send next frame packet */
  on_fly_ctx = p_ctx->on_fly_ctx;
  assert(epnum == (p_ctx->ep_addr & 0xF));
  len = on_fly_ctx->packet_index == (on_fly_ctx->packet_nb - 1) ? on_fly_ctx->last_packet_size + 2 : packet_size;
  memcpy(&p_ctx->packet[2], on_fly_ctx->cursor, len - 2);
  USBD_LL_Transmit(p_dev, p_ctx->ep_addr, p_ctx->packet, len);

  USB_DISP_UpdateOnFlyCtx(p_ctx, len);

  return USBD_OK;
}

static uint8_t USB_DISP_DataIn(USBD_HandleTypeDef *p_dev, uint8_t epnum)
{
  return USB_DISP_DataInImpl(p_dev, epnum, 0);
}

static uint8_t USB_DISP_Sof(USBD_HandleTypeDef *p_dev)
{
  /* nothing to do */

  return USBD_OK;
}

static uint8_t USB_DISP_IsoINIncomplete(USBD_HandleTypeDef *p_dev, uint8_t epnum)
{
  USB_DISP_DisplayCtx_t *p_ctx = (USB_DISP_DisplayCtx_t *) p_dev->pClassDataCmsit[p_dev->classId];

  if (p_ctx->state != USB_DISP_STATUS_STREAMING)
  {
    return USBD_OK;
  }

  /* restart streaming */
  USB_DISP_DataInImpl(p_dev, p_ctx->ep_addr & 0xF, 1);

  return USBD_OK;
}

static uint8_t *USB_DISP_GetHSIsoConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgHsIso));

  return USB_DISP_CfgHsIso;
}

static uint8_t *USB_DISP_GetFSIsoConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsIso));

  return USB_DISP_CfgFsIso;
}

static uint8_t *USB_DISP_GetOtherSpeedIsoConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsIso));

  return USB_DISP_CfgFsIso;
}

static uint8_t *USB_DISP_GetHSBulkConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgHsBulk));

  return USB_DISP_CfgHsBulk;
}

static uint8_t *USB_DISP_GetFSBulkConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsBulk));

  return USB_DISP_CfgFsBulk;
}

static uint8_t *USB_DISP_GetOtherSpeedBulkConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsBulk));

  return USB_DISP_CfgFsBulk;
}

static uint8_t *USB_DISP_GetHSIsoJpegConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgHsIsoJpeg));

  return USB_DISP_CfgHsIsoJpeg;
}

static uint8_t *USB_DISP_GetFSIsoJpegConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsIsoJpeg));

  return USB_DISP_CfgFsIsoJpeg;
}

static uint8_t *USB_DISP_GetOtherSpeedIsoJpegConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsIsoJpeg));

  return USB_DISP_CfgFsIsoJpeg;
}

static uint8_t *USB_DISP_GetHSBulkJpegConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgHsBulkJpeg));

  return USB_DISP_CfgHsBulkJpeg;
}

static uint8_t *USB_DISP_GetFSBulkJpegConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsBulkJpeg));

  return USB_DISP_CfgFsBulkJpeg;
}

static uint8_t *USB_DISP_GetOtherSpeedBulkJpegConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsBulkJpeg));

  return USB_DISP_CfgFsBulkJpeg;
}

static uint8_t *USB_DISP_GetFSBulkFbConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsBulkFb));

  return USB_DISP_CfgFsBulkFb;
}

static uint8_t *USB_DISP_GetFSIsoFbConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsIsoFb));

  return USB_DISP_CfgFsIsoFb;
}

static uint8_t *USB_DISP_GetHSBulkFbConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgHsBulkFb));

  return USB_DISP_CfgHsBulkFb;
}

static uint8_t *USB_DISP_GetHSIsoFbConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgHsIsoFb));

  return USB_DISP_CfgHsIsoFb;
}

typedef uint8_t *(*USB_DISP_ConfFct)(uint16_t *);

static uint8_t *USB_DISP_GetOtherSpeedBulkFbConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsBulkFb));

  return USB_DISP_CfgFsBulkFb;
}

static uint8_t *USB_DISP_GetOtherSpeedIsoFbConfigDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_CfgFsIsoFb));

  return USB_DISP_CfgFsIsoFb;
}

static USB_DISP_ConfFct USB_DISP_FSFctArray[6][2] = {
  {USB_DISP_GetFSBulkConfigDescriptor, USB_DISP_GetFSIsoConfigDescriptor},
  {USB_DISP_GetFSBulkJpegConfigDescriptor, USB_DISP_GetFSIsoJpegConfigDescriptor},
  {USB_DISP_GetFSBulkFbConfigDescriptor, USB_DISP_GetFSIsoFbConfigDescriptor},
  {USB_DISP_GetFSBulkFbConfigDescriptor, USB_DISP_GetFSIsoFbConfigDescriptor},
  {USB_DISP_GetFSBulkFbConfigDescriptor, USB_DISP_GetFSIsoFbConfigDescriptor},
  {USB_DISP_GetFSBulkFbConfigDescriptor, USB_DISP_GetFSIsoFbConfigDescriptor},
};

static USB_DISP_ConfFct USB_DISP_HSFctArray[6][2] = {
  {USB_DISP_GetHSBulkConfigDescriptor, USB_DISP_GetHSIsoConfigDescriptor},
  {USB_DISP_GetHSBulkJpegConfigDescriptor, USB_DISP_GetHSIsoJpegConfigDescriptor},
  {USB_DISP_GetHSBulkFbConfigDescriptor, USB_DISP_GetHSIsoFbConfigDescriptor},
  {USB_DISP_GetHSBulkFbConfigDescriptor, USB_DISP_GetHSIsoFbConfigDescriptor},
  {USB_DISP_GetHSBulkFbConfigDescriptor, USB_DISP_GetHSIsoFbConfigDescriptor},
  {USB_DISP_GetHSBulkFbConfigDescriptor, USB_DISP_GetHSIsoFbConfigDescriptor},
};

static USB_DISP_ConfFct USB_DISP_OtherFctArray[6][2] = {
  {USB_DISP_GetOtherSpeedBulkConfigDescriptor, USB_DISP_GetOtherSpeedIsoConfigDescriptor},
  {USB_DISP_GetOtherSpeedBulkJpegConfigDescriptor, USB_DISP_GetOtherSpeedIsoJpegConfigDescriptor},
  {USB_DISP_GetOtherSpeedBulkFbConfigDescriptor, USB_DISP_GetOtherSpeedIsoFbConfigDescriptor},
  {USB_DISP_GetOtherSpeedBulkFbConfigDescriptor, USB_DISP_GetOtherSpeedIsoFbConfigDescriptor},
  {USB_DISP_GetOtherSpeedBulkFbConfigDescriptor, USB_DISP_GetOtherSpeedIsoFbConfigDescriptor},
  {USB_DISP_GetOtherSpeedBulkFbConfigDescriptor, USB_DISP_GetOtherSpeedIsoFbConfigDescriptor},
};

static uint8_t *USB_DISP_GetDeviceQualifierDescriptor(uint16_t *p_length)
{
  *p_length = (uint16_t)(sizeof(USB_DISP_DeviceQualifierDesc));

  return USB_DISP_DeviceQualifierDesc;
}

static USBD_ClassTypeDef USB_DISP_Class = {
  USB_DISP_InitInstance,
  USB_DISP_DeInit,
  USB_DISP_Setup,
  NULL, /* EP0_TxSent */
  NULL, /* EP0_RxReady */
  USB_DISP_DataIn,
  NULL, /* DataOut */
  USB_DISP_Sof,
  USB_DISP_IsoINIncomplete,
  NULL, /* IsoOUTIncomplete */
#ifdef USE_USBD_COMPOSITE
  #error "composite not supported"
#else
  USB_DISP_GetHSIsoConfigDescriptor,
  USB_DISP_GetFSIsoConfigDescriptor,
  USB_DISP_GetOtherSpeedIsoConfigDescriptor,
  USB_DISP_GetDeviceQualifierDescriptor,
#endif /* USE_USBD_COMPOSITE */
#if (USBD_SUPPORT_USER_STRING_DESC == 1U)
  #error "user string not supported"
#endif
};

static int USB_DISP_GotFrameBufferIndex(USB_DISP_DisplayCtx_t *p_ctx)
{
  if (p_ctx->state != USB_DISP_STATUS_STREAMING)
    return -1;

  if (p_ctx->mode == USB_DISP_MODE_RAW)
    return -1;

  for (int i = 0; i < 2; i++)
  {
    if (p_ctx->fstate[i] != USB_DISP_FRAME_FREE &&
        p_ctx->fstate[i] != USB_DISP_FRAME_IN_DISPLAY_FREE)
      continue;
    return i;
  }

  return -1;
}

static int USB_DISP_GetBitrate(int width, int height, int fps)
{
  return width * height * fps * 2 * 8;
}

static void USB_DISP_UpdateDesc(USB_DISP_FrameDesc *p_frame_desc,
      USB_DISP_Conf_t *p_conf, int fps)
{
  p_frame_desc->wWidth = p_conf->width;
  p_frame_desc->wHeight = p_conf->height;
  p_frame_desc->dwMinBitRate = USB_DISP_GetBitrate(p_conf->width, p_conf->height, fps);
  p_frame_desc->dwMaxBitRate = p_frame_desc->dwMinBitRate;
  p_frame_desc->dwMaxVideoFrameBufferSize = p_conf->width * p_conf->height * 2;
  p_frame_desc->dwDefaultFrameInterval = 10000000 / fps;
  p_frame_desc->dwFrameInterval[0] = p_frame_desc->dwDefaultFrameInterval;
}

static void USB_DISP_UpdateFbFormatDesc(USB_DISP_FbFormatDesc *p_format_desc, int payload_type)
{
  switch (payload_type) {
  case USB_DISP_PAYLOAD_FB_RGB565:
    p_format_desc->guidFormat[0] = 'R';
    p_format_desc->guidFormat[1] = 'G';
    p_format_desc->guidFormat[2] = 'B';
    p_format_desc->guidFormat[3] = 'P';
    break;
  case USB_DISP_PAYLOAD_FB_BGR3:
    p_format_desc->guidFormat[0] = 0x7d;
    p_format_desc->guidFormat[1] = 0xeb;
    p_format_desc->guidFormat[2] = 0x36;
    p_format_desc->guidFormat[3] = 0xe4;
    break;
  case USB_DISP_PAYLOAD_FB_GREY:
    p_format_desc->guidFormat[0] = 'Y';
    p_format_desc->guidFormat[1] = '8';
    p_format_desc->guidFormat[2] = ' ';
    p_format_desc->guidFormat[3] = ' ';
    break;
  case USB_DISP_PAYLOAD_FB_H264:
    p_format_desc->guidFormat[0] = 'H';
    p_format_desc->guidFormat[1] = '2';
    p_format_desc->guidFormat[2] = '6';
    p_format_desc->guidFormat[3] = '4';
    break;
  default:
    assert(0);
  }
  p_format_desc->bBitsPerPixel = USB_DISP_GetBpp(payload_type);
  p_format_desc->bVariableSize = p_format_desc->bBitsPerPixel ? 0 : 1;
}

static void USB_DISP_UpdateFbFrameDesc(USB_DISP_FbFrameDesc *p_frame_desc, USB_DISP_Conf_t *p_conf, int fps)
{
  int bpp = USB_DISP_GetBpp(p_conf->payload_type);

  p_frame_desc->wWidth = p_conf->width;
  p_frame_desc->wHeight = p_conf->height;
  p_frame_desc->dwMinBitRate = bpp ? p_conf->width * p_conf->height * fps * bpp :
                                     p_conf->width * p_conf->height * fps;
  p_frame_desc->dwMaxBitRate = p_frame_desc->dwMinBitRate;
  p_frame_desc->dwDefaultFrameInterval = 10000000 / fps;
  p_frame_desc->dwBytesPerLine = bpp ? p_conf->width * bpp : p_conf->width;
  p_frame_desc->dwFrameInterval[0] = p_frame_desc->dwDefaultFrameInterval;
}

static void USB_DISP_UpdateFbDesc(USB_DISP_FbFormatDesc *p_format_desc, USB_DISP_FbFrameDesc *p_frame_desc,
                                  USB_DISP_Conf_t *p_conf, int fps)
{
  USB_DISP_UpdateFbFormatDesc(p_format_desc, p_conf->payload_type);
  USB_DISP_UpdateFbFrameDesc(p_frame_desc, p_conf, fps);
}

static void USB_DISP_ApplyConf(USB_DISP_DisplayCtx_t *p_ctx, USB_DISP_Conf_t *p_conf)
{
  p_ctx->width = p_conf->width;
  p_ctx->height = p_conf->height;
  p_ctx->fps_fs = p_conf->fps;
  p_ctx->fps_hs = p_conf->fps;
  p_ctx->frame_buffer_size = p_conf->frame_buffer_size;
  p_ctx->frames[0] = p_conf->p_frame_buffers[0];
  p_ctx->frames[1] = p_conf->p_frame_buffers[1];
  p_ctx->is_iso = p_conf->is_iso;
  p_ctx->mode = p_conf->mode;
  p_ctx->payload_type = p_conf->payload_type;
  p_ctx->input_format_hint = p_conf->input_format_hint;
#ifdef HAL_JPEG_MODULE_ENABLED
  p_ctx->jpg_ctx.p_hjpeg = p_conf->p_hjpeg;
  p_ctx->jpg_ctx.p_jpeg_scratch_buffer = p_conf->p_jpeg_scratch_buffer;
#endif

  USB_DISP_Class.GetFSConfigDescriptor = USB_DISP_FSFctArray[p_ctx->payload_type][p_ctx->is_iso];
  USB_DISP_Class.GetHSConfigDescriptor = USB_DISP_HSFctArray[p_ctx->payload_type][p_ctx->is_iso];
  USB_DISP_Class.GetOtherSpeedConfigDescriptor = USB_DISP_OtherFctArray[p_ctx->payload_type][p_ctx->is_iso];

  if (USB_DISP_IsFbPayload(p_ctx->payload_type)) {
    USB_DISP_FbFormatDesc *p_format_desc = USB_DISP_GetFbFormatDesc(USBD_SPEED_FULL);
    USB_DISP_FbFrameDesc *p_frame_desc = USB_DISP_GetFbFrameDesc(USBD_SPEED_FULL);
    assert(p_format_desc);
    assert(p_frame_desc);
    USB_DISP_UpdateFbDesc(p_format_desc, p_frame_desc, p_conf, p_ctx->fps_fs);

  } else {
    USB_DISP_FrameDesc *p_frame_desc = USB_DISP_GetFrameDesc(USBD_SPEED_FULL);
    assert(p_frame_desc);
    USB_DISP_UpdateDesc(p_frame_desc, p_conf, p_ctx->fps_fs);
  }

  if (USB_DISP_IsFbPayload(p_ctx->payload_type)) {
    USB_DISP_FbFormatDesc *p_format_desc = USB_DISP_GetFbFormatDesc(USBD_SPEED_HIGH);
    USB_DISP_FbFrameDesc *p_frame_desc = USB_DISP_GetFbFrameDesc(USBD_SPEED_HIGH);
    assert(p_format_desc);
    assert(p_frame_desc);
    USB_DISP_UpdateFbDesc(p_format_desc, p_frame_desc, p_conf, p_ctx->fps_fs);
  } else {
    USB_DISP_FrameDesc *p_frame_desc = USB_DISP_GetFrameDesc(USBD_SPEED_HIGH);
    assert(p_frame_desc);
    USB_DISP_UpdateDesc(p_frame_desc, p_conf, p_ctx->fps_hs);
  }
}

static void USB_DISP_LinkWithPcdHandle(USBD_HandleTypeDef *p_dev, PCD_HandleTypeDef *p_hpcd)
{
  /* dma is not supported. disable it */
  if (p_hpcd->Init.dma_enable != DISABLE)
    p_hpcd->Init.dma_enable = DISABLE;

  p_hpcd->pData = p_dev;
  p_dev->pData = p_hpcd;

  HAL_PCDEx_SetRxFiFo(p_hpcd, 0x200);
  HAL_PCDEx_SetTxFiFo(p_hpcd, 0, 0x80);
  HAL_PCDEx_SetTxFiFo(p_hpcd, 1, 0x174);
}

#ifdef HAL_JPEG_MODULE_ENABLED
static void USB_DISP_SetupJpegCtx(USB_DISP_DisplayCtx_t *p_ctx, int *fsize, uint8_t *p_frame, int byte_per_pel,
                                  void (*cvt)(uint8_t *, uint8_t *, int , int ))
{
  USB_DISP_JpgCtx_t *p_jpg_ctx = &p_ctx->jpg_ctx;

  p_jpg_ctx->p_fsize = fsize;
  p_jpg_ctx->p_frame_pos = p_frame;
  p_jpg_ctx->line_nb = 0;
  p_jpg_ctx->frame_pitch = p_ctx->width * byte_per_pel;
  p_jpg_ctx->mcu_line_size = ((p_ctx->width + 15) / 16) * 256;
  p_jpg_ctx->cvt = cvt;
  p_jpg_ctx->cvt(p_jpg_ctx->p_jpeg_scratch_buffer, p_frame, p_ctx->width, MIN(p_ctx->height - p_jpg_ctx->line_nb, 8));
}

/* Jpeg callbacks */
void HAL_JPEG_DataReadyCallback(JPEG_HandleTypeDef *hjpeg, uint8_t *pDataOut, uint32_t OutDataLength)
{
  USB_DISP_DisplayCtx_t *p_ctx = USB_DISP_Jpeg2DispCtx(hjpeg);
  USB_DISP_JpgCtx_t *p_jpg_ctx = &p_ctx->jpg_ctx;

  *p_jpg_ctx->p_fsize = OutDataLength;
}

void HAL_JPEG_GetDataCallback(JPEG_HandleTypeDef *hjpeg, uint32_t NbDecodedData)
{
  USB_DISP_DisplayCtx_t *p_ctx = USB_DISP_Jpeg2DispCtx(hjpeg);
  USB_DISP_JpgCtx_t *p_jpg_ctx = &p_ctx->jpg_ctx;

  p_jpg_ctx->line_nb += 8;

  if (p_jpg_ctx->line_nb >= p_ctx->height)
    return ;

  p_jpg_ctx->p_frame_pos += p_jpg_ctx->frame_pitch * 8;
  p_jpg_ctx->cvt(p_jpg_ctx->p_jpeg_scratch_buffer, p_jpg_ctx->p_frame_pos, p_ctx->width, MIN(p_ctx->height - p_jpg_ctx->line_nb, 8));
  HAL_JPEG_ConfigInputBuffer(p_jpg_ctx->p_hjpeg, p_jpg_ctx->p_jpeg_scratch_buffer, p_jpg_ctx->mcu_line_size);
}
#endif

static int USB_DISP_SanityChecks(USB_DISP_Conf_t *p_conf)
{
  int buffer_nb;
  int i;

  if (p_conf->p_hpcd == NULL)
  {
    return -1;
  }

  /* width must be even */
  if (p_conf->width % 2)
  {
    return -1;
  }

  /* valid display mode */
  if (p_conf->mode != USB_DISP_MODE_LCD && p_conf->mode != USB_DISP_MODE_ON_DEMAND &&
      p_conf->mode != USB_DISP_MODE_LCD_SINGLE_BUFFER && p_conf->mode != USB_DISP_MODE_ON_DEMAND_SINGLE_BUFFER &&
      p_conf->mode != USB_DISP_MODE_RAW)
  {
    return -1;
  }

  /* check buffers according to display mode */
  buffer_nb = USB_DISP_GetBufferNb(p_conf->mode);
  for (i = 0; i < buffer_nb; i++) {
    if (p_conf->p_frame_buffers[i] == NULL)
      return -1;
    if (p_conf->frame_buffer_size == 0)
      return -1;
  }

  /* valid display mode */
  if (p_conf->payload_type != USB_DISP_PAYLOAD_UNCOMPRESSED
      && p_conf->payload_type != USB_DISP_PAYLOAD_FB_RGB565
      && p_conf->payload_type != USB_DISP_PAYLOAD_FB_BGR3
      && p_conf->payload_type != USB_DISP_PAYLOAD_FB_GREY
#ifdef HAL_JPEG_MODULE_ENABLED
      && p_conf->payload_type != USB_DISP_PAYLOAD_JPEG
#endif
  )
  {
    return -1;
  }

  /* additionnal checks for USB_DISP_PAYLOAD_JPEG payload type */
  if (p_conf->payload_type == USB_DISP_PAYLOAD_JPEG)
  {
    if (p_conf->p_jpeg_scratch_buffer == NULL)
    {
      return -1;
    }
    if (p_conf->p_hjpeg == NULL)
    {
      return -1;
    }
  }

  /* for fix size payload */
  if (p_conf->payload_type == USB_DISP_PAYLOAD_UNCOMPRESSED &&
      p_conf->frame_buffer_size < p_conf->width * p_conf->height * 2)
  {
    return -1;
  }
  if (p_conf->payload_type == USB_DISP_PAYLOAD_FB_RGB565 &&
      p_conf->frame_buffer_size < p_conf->width * p_conf->height * 2)
  {
    return -1;
  }
  if (p_conf->payload_type == USB_DISP_PAYLOAD_FB_BGR3 &&
      p_conf->frame_buffer_size < p_conf->width * p_conf->height * 3)
  {
    return -1;
  }
  if (p_conf->payload_type == USB_DISP_PAYLOAD_FB_GREY &&
      p_conf->frame_buffer_size < p_conf->width * p_conf->height)
  {
    return -1;
  }

  return 0;
}

static int USB_DISP_CvtUnsupported(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                   int *fsize)
{
  *fsize = 0;

  return -1;
}

static int USB_DISP_CvtGreyToYuv422(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  *fsize = width * height * 2;
  USB_DISP_FormatGreyToYuv422(p_dst, p_src, width, height);

  return 0;
}

static int USB_DISP_CvtArgbToYuv422(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  *fsize = width * height * 2;
  USB_DISP_FormatArgbToYuv422(p_dst, p_src, width, height);

  return 0;
}

static int USB_DISP_CvtRgb565ToYuv422(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  *fsize = width * height * 2;
  USB_DISP_FormatRgb565ToYuv422(p_dst, p_src, width, height);

  return 0;
}

static int USB_DISP_CvtYuv422ToYuv422(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  *fsize = width * height * 2;
  memcpy(p_dst, p_src, *fsize);

  return 0;
}

static int USB_DISP_CvtXxxToJpeg(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize, int byte_per_pel, void (*cvt)(uint8_t *, uint8_t *, int , int ))
{
#ifdef HAL_JPEG_MODULE_ENABLED
  USB_DISP_JpgCtx_t *p_jpg_ctx = &p_ctx->jpg_ctx;
  int ret;

  USB_DISP_SetupJpegCtx(p_ctx, fsize, p_src, byte_per_pel, cvt);
  ret = HAL_JPEG_Encode(p_jpg_ctx->p_hjpeg, p_jpg_ctx->p_jpeg_scratch_buffer, p_jpg_ctx->mcu_line_size,
                        p_dst, p_ctx->frame_buffer_size, JPEG_TIMEOUT);

  return ret == HAL_OK ? 0 : -1;
#else
  return USB_DISP_CvtUnsupported(p_ctx, p_dst, p_src, width, height, fsize);
#endif
}

static int USB_DISP_CvtGreyToJpeg(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  return USB_DISP_CvtXxxToJpeg(p_ctx, p_dst, p_src, width, height, fsize, 1, USB_DISP_FormatGreyToYuv422Jpeg);
}

static int USB_DISP_CvtArgbToJpeg(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  return USB_DISP_CvtXxxToJpeg(p_ctx, p_dst, p_src, width, height, fsize, 4, USB_DISP_FormatRgbArgbToYuv422Jpeg);
}

static int USB_DISP_CvtRgb565ToJpeg(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  return USB_DISP_CvtXxxToJpeg(p_ctx, p_dst, p_src, width, height, fsize, 2, USB_DISP_FormatRgb565ToYuv422Jpeg);
}

static int USB_DISP_CvtYuv422ToJpeg(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  return USB_DISP_CvtXxxToJpeg(p_ctx, p_dst, p_src, width, height, fsize, 2, USB_DISP_FormatYuv422ToYuv422Jpeg);
}

static int USB_DISP_CvtRgb565ToRgb565(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  *fsize = width * height * 2;
  memcpy(p_dst, p_src, *fsize);

  return 0;
}

static int USB_DISP_CvtGreyToGrey(USB_DISP_DisplayCtx_t *p_ctx, uint8_t *p_dst, uint8_t *p_src, int width, int height,
                                    int *fsize)
{
  *fsize = width * height;
  memcpy(p_dst, p_src, *fsize);

  return 0;
}

static void USB_DISP_SetupCvtUncompressed(USB_DISP_DisplayCtx_t *p_ctx)
{
  p_ctx->cvtGreyToPayload = USB_DISP_CvtGreyToYuv422;
  p_ctx->cvtArgbToPayload = USB_DISP_CvtArgbToYuv422;
  p_ctx->cvtRgb565ToPayload = USB_DISP_CvtRgb565ToYuv422;
  p_ctx->cvtYuv422ToPayload = USB_DISP_CvtYuv422ToYuv422;
}

static void USB_DISP_SetupCvtJpeg(USB_DISP_DisplayCtx_t *p_ctx)
{
  p_ctx->cvtGreyToPayload = USB_DISP_CvtGreyToJpeg;
  p_ctx->cvtArgbToPayload = USB_DISP_CvtArgbToJpeg;
  p_ctx->cvtRgb565ToPayload = USB_DISP_CvtRgb565ToJpeg;
  p_ctx->cvtYuv422ToPayload = USB_DISP_CvtYuv422ToJpeg;
}

static void USB_DISP_SetupCvtRgb565(USB_DISP_DisplayCtx_t *p_ctx)
{
  p_ctx->cvtGreyToPayload = USB_DISP_CvtUnsupported;
  p_ctx->cvtArgbToPayload = USB_DISP_CvtUnsupported;
  p_ctx->cvtRgb565ToPayload = USB_DISP_CvtRgb565ToRgb565;
  p_ctx->cvtYuv422ToPayload = USB_DISP_CvtUnsupported;
}

static void USB_DISP_SetupCvtGrey(USB_DISP_DisplayCtx_t *p_ctx)
{
  p_ctx->cvtGreyToPayload = USB_DISP_CvtGreyToGrey;
  p_ctx->cvtArgbToPayload = USB_DISP_CvtUnsupported;
  p_ctx->cvtRgb565ToPayload = USB_DISP_CvtUnsupported;
  p_ctx->cvtYuv422ToPayload = USB_DISP_CvtUnsupported;
}

static void USB_DISP_SetupCvtUnknown(USB_DISP_DisplayCtx_t *p_ctx)
{
  p_ctx->cvtGreyToPayload = USB_DISP_CvtUnsupported;
  p_ctx->cvtArgbToPayload = USB_DISP_CvtUnsupported;
  p_ctx->cvtRgb565ToPayload = USB_DISP_CvtUnsupported;
  p_ctx->cvtYuv422ToPayload = USB_DISP_CvtUnsupported;
}

static void USB_DISP_SetupCvt(USB_DISP_DisplayCtx_t *p_ctx)
{
  switch (p_ctx->payload_type) {
  case USB_DISP_PAYLOAD_UNCOMPRESSED:
    USB_DISP_SetupCvtUncompressed(p_ctx);
    break;
  case USB_DISP_PAYLOAD_JPEG:
    USB_DISP_SetupCvtJpeg(p_ctx);
    break;
  case USB_DISP_PAYLOAD_FB_RGB565:
    USB_DISP_SetupCvtRgb565(p_ctx);
    break;
  case USB_DISP_PAYLOAD_FB_GREY:
    USB_DISP_SetupCvtGrey(p_ctx);
    break;
  default:
    USB_DISP_SetupCvtUnknown(p_ctx);
  }
}

static int USB_DISP_Show(USB_DISP_Hdl_t hdl, uint8_t *p_frame,
                         int (*cvt)(USB_DISP_DisplayCtx_t *, uint8_t *, uint8_t *, int , int , int *))
{
  USB_DISP_DisplayCtx_t *p_ctx = hdl;
  int idx = USB_DISP_GotFrameBufferIndex(p_ctx);
  int ret;

  if (idx < 0)
  {
    return 0;
  }

  ret = cvt(p_ctx, p_ctx->frames[idx], p_frame, p_ctx->width, p_ctx->height, &p_ctx->fsize[idx]);
  if (ret)
  {
    return 0;
  }

  p_ctx->findex[idx] = p_ctx->push_index++;
  __DMB();
  p_ctx->fstate[idx] = USB_DISP_FRAME_READY;

  return 1;
}

/**
 * @brief Initialize USB display
 *
 * This will update USB descriptors according to request configuration and will then
 * start USB device stack.
 *
 * @param p_conf USB display configuration parameters
 * @return return USB display handle in case of success else NULL value is returned
 */
USB_DISP_Hdl_t USB_DISP_Init(USB_DISP_Conf_t *p_conf)
{
  USB_DISP_DisplayCtx_t *p_ctx;
  USBD_HandleTypeDef *pdev;
#ifdef HAL_JPEG_MODULE_ENABLED
  JPEG_ConfTypeDef jpeg_conf;
#endif

  if (USB_DISP_SanityChecks(p_conf))
    goto error;

  p_ctx = calloc(1, sizeof(*p_ctx));
  if (!p_ctx)
    goto error;
  pdev = &p_ctx->usbd_dev;

  USB_DISP_FormatInit();
  USB_DISP_ApplyConf(p_ctx, p_conf);

#ifdef HAL_JPEG_MODULE_ENABLED
  if (p_conf->payload_type == USB_DISP_PAYLOAD_JPEG)
  {
    jpeg_conf.ColorSpace        = JPEG_YCBCR_COLORSPACE;
    jpeg_conf.ChromaSubsampling = JPEG_422_SUBSAMPLING;
    jpeg_conf.ImageWidth        = p_conf->width;
    jpeg_conf.ImageHeight       = p_conf->height;
    jpeg_conf.ImageQuality      = 90;
    if (HAL_JPEG_ConfigEncoding(p_conf->p_hjpeg, &jpeg_conf) != HAL_OK)
      goto error_dealloc_ctx;
  }
#endif

#ifdef STM32H7
  HAL_PWREx_EnableUSBVoltageDetector();
#endif

  USB_DISP_SetupCvt(p_ctx);

  if (USBD_Init(pdev, &USB_DISP_Desc, 0) != USBD_OK)
    goto error_dealloc_ctx;
  USB_DISP_LinkWithPcdHandle(pdev, p_conf->p_hpcd);

  if (USBD_RegisterClass(pdev, &USB_DISP_Class) != USBD_OK)
    goto error_usb_deinit;

  if (USBD_Start(pdev) != USBD_OK)
    goto error_usb_deinit;

  if (USB_DISP_RegisterCtx(p_ctx))
    goto error_usb_deinit;

  return p_ctx;

error_usb_deinit:
  USBD_DeInit(pdev);
error_dealloc_ctx:
  free(p_ctx);
error:

  return NULL;
}

/**
 * @brief Display monochrome frame
 *
 * Provide frame will be converted to USB display format and provide to host for display
 *
 * @param p_frame Monochrome frame data to display
 * @return return 1 if frame will be displayed else return 0 is frame is dropped
 */
int USB_DISP_ShowGrey(USB_DISP_Hdl_t hdl, uint8_t *p_frame)
{
  USB_DISP_DisplayCtx_t *p_ctx = hdl;

  return USB_DISP_Show(hdl, p_frame, p_ctx->cvtGreyToPayload);
}

/**
 * @brief Display argb frame
 *
 * Provide frame will be converted to USB display format and provide to host for display
 *
 * @param p_frame argb frame data to display
 * @return return 1 if frame will be displayed else return 0 is frame is dropped
 */
int USB_DISP_ShowArgb(USB_DISP_Hdl_t hdl, uint8_t *p_frame)
{
  USB_DISP_DisplayCtx_t *p_ctx = hdl;

  return USB_DISP_Show(hdl, p_frame, p_ctx->cvtArgbToPayload);
}

/**
 * @brief Display 565 rgb frame
 *
 * Provide frame will be converted to USB display format and provide to host for display
 *
 * @param p_frame 565 rgb frame data to display
 * @return return 1 if frame will be displayed else return 0 is frame is dropped
 */
int USB_DISP_ShowRgb565(USB_DISP_Hdl_t hdl, uint8_t *p_frame)
{
  USB_DISP_DisplayCtx_t *p_ctx = hdl;

  return USB_DISP_Show(hdl, p_frame, p_ctx->cvtRgb565ToPayload);
}

/**
 * @brief Display yuv422 frame
 *
 * Provide frame will be converted to USB display format and provide to host for display
 * yuv422 if 422 format with interleaved luma, chroma components (YUYVYUYV ....)
 *
 * @param p_frame yuv422 frame data to display
 * @return return 1 if frame will be displayed else return 0 is frame is dropped
 */
int USB_DISP_ShowYuv422(USB_DISP_Hdl_t hdl, uint8_t *p_frame)
{
  USB_DISP_DisplayCtx_t *p_ctx = hdl;

  return USB_DISP_Show(hdl, p_frame, p_ctx->cvtYuv422ToPayload);
}

/**
 ******************************************************************************
 * @file    usb_disp.c
 * @author  MCD Application Team
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

/**
 * @brief Display raw frame
 *
 * Provide frame will sent as this. So it must have same type as payload_type. Size should
 * also have the correct value. When frame will have been transmit cb will be called to notify user.
 *
 * @param p_frame raw frame data to display
 * @param frame_size size of raw frame in bytes
 * @param cb callback user function called once frame transmit is finished
 * @param cb_args user parameter provide to user callback function
 * @return return 1 if frame will be displayed else return 0 is frame is dropped
 */
int USB_DISP_ShowRaw(USB_DISP_Hdl_t hdl, uint8_t *p_frame, int frame_size, void (*cb)(uint8_t *p_frame, void *cb_args),
                     void *cb_args)
{
  USB_DISP_DisplayCtx_t *p_ctx = hdl;

  if (p_ctx->state != USB_DISP_STATUS_STREAMING)
    return 0;
  if (p_ctx->mode != USB_DISP_MODE_RAW)
    return 0;
  if (p_ctx->p_frame_raw)
    return 0;

  if (!p_frame)
    return 0;
  if (!frame_size)
    return 0;
  if (!cb)
    return 0;

  p_ctx->frame_size_raw = frame_size;
  p_ctx->cb_raw = cb;
  p_ctx->cb_args_raw = cb_args;
  __DMB();
  p_ctx->p_frame_raw = p_frame;

  return 1;
}
