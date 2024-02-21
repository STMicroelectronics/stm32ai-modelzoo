 /**
 ******************************************************************************
 * @file    usb_cam_init.c
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
#include "usb_cam_init.h"

#include "usb_cam.h"
#include "usb_cam_private.h"
#include "usbh_ctlreq.h"
#include "usb_cam_uvc.h"
#include "usbh_def.h"
#include <stddef.h>
#include <stdint.h>

#define MAX_FRAME_INTERNAL_NB 16

#define get8(b, t, f) *(uint8_t *)(&b[offsetof(t, f)])
#define get16(b, t, f) LE16(&b[offsetof(t, f)])
#define get32(b, t, f) LE32(&b[offsetof(t, f)])

typedef struct {
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bEndpointAddress;
  uint8_t bmAttributes;
  uint16_t wMaxPacketSize;
  uint8_t bInterval;
} __packed USB_EpDesc;

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
  uint32_t dwFrameInterval[MAX_FRAME_INTERNAL_NB];
} __packed UVC_XxxFrameDesc;

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
} __packed UVC_UncompFmtDesc;

typedef struct {
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bDescriptorSubType;
  uint8_t bFormatIndex;
  uint8_t bNumFrameDescriptors;
  uint8_t bmFlags;
  uint8_t bDefaultFrameIndex;
  uint8_t bAspectRatioX;
  uint8_t bAspectRatioY;
  uint8_t bmInterlaceFlags;
  uint8_t bCopyProtect;
} __packed UVC_JpegFmtDesc;

typedef struct {
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bDescriptorSubType;
  uint16_t bcdUVC;
  uint16_t wTotalLength;
  uint32_t dwClockFrequency;
  uint8_t bInCollection;
} __packed UVC_ItfVcClassDesc;

typedef struct {
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bInterfaceNumber;
  uint8_t bAlternateSetting;
  uint8_t bNumEndpoints;
  uint8_t bInterfaceClass;
  uint8_t bInterfaceSubClass;
  uint8_t bInterfaceProtocol;
  uint8_t iInterface;
} __packed USB_ItfDesc;

typedef int (*USB_CAM_VisitCb)(USBH_DescHeader_t *pDesc, void *args);

static void USB_CAM_FillEpDesc(USB_EpDesc *p_desc, uint8_t *p_buf)
{
  p_desc->bLength = get8(p_buf, USB_EpDesc, bLength);
  p_desc->bDescriptorType = get8(p_buf, USB_EpDesc, bDescriptorType);
  p_desc->bEndpointAddress = get8(p_buf, USB_EpDesc, bEndpointAddress);
  p_desc->bmAttributes = get8(p_buf, USB_EpDesc, bmAttributes);
  p_desc->wMaxPacketSize = get16(p_buf, USB_EpDesc, wMaxPacketSize);
  p_desc->bInterval = get8(p_buf, USB_EpDesc, bInterval);
}

static void USB_CAM_FillXxxFrameDesc(UVC_XxxFrameDesc *p_desc, uint8_t *p_buf)
{
  int i;

  p_desc->bLength = get8(p_buf, UVC_XxxFrameDesc, bLength);
  p_desc->bDescriptorType = get8(p_buf, UVC_XxxFrameDesc, bDescriptorType);
  p_desc->bDescriptorSubType = get8(p_buf, UVC_XxxFrameDesc, bDescriptorSubType);
  p_desc->bFrameIndex = get8(p_buf, UVC_XxxFrameDesc, bFrameIndex);
  p_desc->bmCapabilities = get8(p_buf, UVC_XxxFrameDesc, bmCapabilities);
  p_desc->wWidth = get16(p_buf, UVC_XxxFrameDesc, wWidth);
  p_desc->wHeight = get16(p_buf, UVC_XxxFrameDesc, wHeight);
  p_desc->dwMinBitRate = get32(p_buf, UVC_XxxFrameDesc, dwMinBitRate);
  p_desc->dwMaxBitRate = get32(p_buf, UVC_XxxFrameDesc, dwMaxBitRate);
  p_desc->dwMaxVideoFrameBufferSize = get32(p_buf, UVC_XxxFrameDesc, dwMaxVideoFrameBufferSize);
  p_desc->dwDefaultFrameInterval = get32(p_buf, UVC_XxxFrameDesc, dwDefaultFrameInterval);
  p_desc->bFrameIntervalType = get8(p_buf, UVC_XxxFrameDesc, bFrameIntervalType);
  p_desc->bFrameIntervalType = MIN(p_desc->bFrameIntervalType, MAX_FRAME_INTERNAL_NB);
  /* FIXME : avoid read too much data if not of subtype VS_FRAME_UNCOMPRESSED */
  for (i = 0; i < p_desc->bFrameIntervalType; i++)
    p_desc->dwFrameInterval[i] = get32(p_buf, UVC_XxxFrameDesc, dwFrameInterval[i]);
}

static void USB_CAM_FillUncompFmtDesc(UVC_UncompFmtDesc *p_desc, uint8_t *p_buf)
{
  int i;

  p_desc->bLength = get8(p_buf, UVC_UncompFmtDesc, bLength);
  p_desc->bDescriptorType = get8(p_buf, UVC_UncompFmtDesc, bDescriptorType);
  p_desc->bDescriptorSubType = get8(p_buf, UVC_UncompFmtDesc, bDescriptorSubType);
  p_desc->bFormatIndex = get8(p_buf, UVC_UncompFmtDesc, bFormatIndex);
  p_desc->bNumFrameDescriptors = get8(p_buf, UVC_UncompFmtDesc, bNumFrameDescriptors);
  for (i = 0; i < 16; i++)
    p_desc->guidFormat[i] = get8(p_buf, UVC_UncompFmtDesc, guidFormat[i]);
  p_desc->bBitsPerPixel = get8(p_buf, UVC_UncompFmtDesc, bBitsPerPixel);
  p_desc->bDefaultFrameIndex = get8(p_buf, UVC_UncompFmtDesc, bDefaultFrameIndex);
  p_desc->bAspectRatioX = get8(p_buf, UVC_UncompFmtDesc, bAspectRatioX);
  p_desc->bAspectRatioY = get8(p_buf, UVC_UncompFmtDesc, bAspectRatioY);
  p_desc->bmInterlaceFlags = get8(p_buf, UVC_UncompFmtDesc, bmInterlaceFlags);
  p_desc->bCopyProtect = get8(p_buf, UVC_UncompFmtDesc, bCopyProtect);
}

static void USB_CAM_FillJpegFmtDesc(UVC_JpegFmtDesc *p_desc, uint8_t *p_buf)
{
  p_desc->bLength = get8(p_buf, UVC_JpegFmtDesc, bLength);
  p_desc->bDescriptorType = get8(p_buf, UVC_JpegFmtDesc, bDescriptorType);
  p_desc->bDescriptorSubType = get8(p_buf, UVC_JpegFmtDesc, bDescriptorSubType);
  p_desc->bFormatIndex = get8(p_buf, UVC_JpegFmtDesc, bFormatIndex);
  p_desc->bNumFrameDescriptors = get8(p_buf, UVC_JpegFmtDesc, bNumFrameDescriptors);
  p_desc->bmFlags = get8(p_buf, UVC_JpegFmtDesc, bmFlags);
  p_desc->bDefaultFrameIndex = get8(p_buf, UVC_JpegFmtDesc, bDefaultFrameIndex);
  p_desc->bAspectRatioX = get8(p_buf, UVC_JpegFmtDesc, bAspectRatioX);
  p_desc->bAspectRatioY = get8(p_buf, UVC_JpegFmtDesc, bAspectRatioY);
  p_desc->bmInterlaceFlags = get8(p_buf, UVC_JpegFmtDesc, bmInterlaceFlags);
  p_desc->bCopyProtect = get8(p_buf, UVC_JpegFmtDesc, bCopyProtect);
}

static void USB_CAM_FillItfVcClassDesc(UVC_ItfVcClassDesc *p_desc, uint8_t *p_buf)
{
  p_desc->bLength = get8(p_buf, UVC_ItfVcClassDesc, bLength);
  p_desc->bDescriptorType = get8(p_buf, UVC_ItfVcClassDesc, bDescriptorType);
  p_desc->bDescriptorSubType = get8(p_buf, UVC_ItfVcClassDesc, bDescriptorSubType);
  p_desc->bcdUVC = get16(p_buf, UVC_ItfVcClassDesc, bcdUVC);
  p_desc->wTotalLength = get16(p_buf, UVC_ItfVcClassDesc, wTotalLength);
  p_desc->dwClockFrequency = get32(p_buf, UVC_ItfVcClassDesc, dwClockFrequency);
  p_desc->bInCollection = get8(p_buf, UVC_ItfVcClassDesc, bInCollection);
}

static void USB_CAM_FillItfDesc(USB_ItfDesc *p_desc, uint8_t *p_buf)
{
  p_desc->bLength = get8(p_buf, USB_ItfDesc, bLength);;
  p_desc->bDescriptorType = get8(p_buf, USB_ItfDesc, bDescriptorType);;
  p_desc->bInterfaceNumber = get8(p_buf, USB_ItfDesc, bInterfaceNumber);;
  p_desc->bAlternateSetting = get8(p_buf, USB_ItfDesc, bAlternateSetting);;
  p_desc->bNumEndpoints = get8(p_buf, USB_ItfDesc, bNumEndpoints);;
  p_desc->bInterfaceClass = get8(p_buf, USB_ItfDesc, bInterfaceClass);;
  p_desc->bInterfaceSubClass = get8(p_buf, USB_ItfDesc, bInterfaceSubClass);;
  p_desc->bInterfaceProtocol = get8(p_buf, USB_ItfDesc, bInterfaceProtocol);;
  p_desc->iInterface = get8(p_buf, USB_ItfDesc, iInterface);;
}

static USBH_DescHeader_t *USB_CAM_VisitDesc(USBH_DescHeader_t *p_desc, int len,
                                            USB_CAM_VisitCb cb, void *cb_args)
{
  uint16_t pos = 0;
  int ret;

  while (pos + p_desc->bLength <= len && p_desc->bLength > 0)
  {
    ret = cb(p_desc, cb_args);
    if (ret)
      return p_desc;
    p_desc = USBH_GetNextDesc((uint8_t *) p_desc, &pos);
  }

  return NULL;
}

static USBH_DescHeader_t *USB_CAM_VisitCfgDesc(struct _USBH_HandleTypeDef *phost,
                                               USB_CAM_VisitCb cb, void *cb_args)
{
  USBH_CfgDescTypeDef *p_desc = &phost->device.CfgDesc;

  return USB_CAM_VisitDesc((USBH_DescHeader_t *) &phost->device.CfgDesc_Raw, p_desc->wTotalLength, cb, cb_args);
}

static int USB_CAM_FindItfVcClassDesc(USBH_DescHeader_t *pDesc, void *args)
{
  UVC_ItfVcClassDesc itf_desc;

  if (pDesc->bLength < 12 ||
      pDesc->bDescriptorType != CS_INTERFACE)
    return 0;

  USB_CAM_FillItfVcClassDesc(&itf_desc, (uint8_t *) pDesc);
  if (itf_desc.bDescriptorSubType != VC_HEADER)
    return 0;

  *((uint16_t *) args) = itf_desc.bcdUVC;

  return 1;
}

static int USB_CAM_GetUvcVersion(struct _USBH_HandleTypeDef *phost)
{
  uint16_t version = UVC_VERSION_UNKNOWN;
  
  USB_CAM_VisitCfgDesc(phost, USB_CAM_FindItfVcClassDesc, &version);

  return version;
}

static int USB_CAM_HasSupportedVC(struct _USBH_HandleTypeDef *phost)
{
  USBH_InterfaceDescTypeDef *itf = &phost->device.CfgDesc.Itf_Desc[0];

  if (itf->bDescriptorType != INTERFACE_DESC_TYPE ||
      itf->bInterfaceClass != CC_VIDEO ||
      itf->bInterfaceSubClass != SC_VIDEOCONTROL ||
      itf->bInterfaceProtocol != PC_PROTOCOL_UNDEFINED)
    return 0;

  return 1;
}

static int USB_CAM_HasSupportedVS(struct _USBH_HandleTypeDef *phost)
{
  USBH_InterfaceDescTypeDef *itf = &phost->device.CfgDesc.Itf_Desc[1];

  if (itf->bDescriptorType != INTERFACE_DESC_TYPE ||
      itf->bInterfaceClass != CC_VIDEO ||
      itf->bInterfaceSubClass != SC_VIDEOSTREAMING ||
      itf->bInterfaceProtocol != PC_PROTOCOL_UNDEFINED)
    return 0;

  /* We don't support bulk mode yet */
  if (itf->bNumEndpoints)
    return 0;

  return 1;
}

USBH_StatusTypeDef USB_CAM_ClassInitSanityCheck(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  int version;

  if (!USB_CAM_HasSupportedVC(phost))
  {
    USBH_ErrLog("No video control interface found\n");
    return USBH_FAIL;
  }

  if (!USB_CAM_HasSupportedVS(phost))
  {
    USBH_ErrLog("No video streaming interface found\n");
    return USBH_FAIL;
  }

  version = USB_CAM_GetUvcVersion(phost);
  if (version != UVC_VERSION_1_0 && version != UVC_VERSION_1_1)
  {
    USBH_ErrLog("UVC 1.0/1.1 supported. Camera version is 0x%04x\n", version);
    return USBH_FAIL;
  }
  p_ctx->bcdUVC = version;

  return USBH_OK;
}

typedef struct {
  /* target */
  int target_width;
  int target_height;
  int target_period;
  int target_payload_type;
  uint8_t bTargetInterfaceNumber;
  /* current state */
  uint8_t bCurrentInterfaceNumber;
  uint8_t bCurrentAlternateSetting;
  uint8_t bCurrentFormatIndex;
  uint8_t bCurrentNumFrameDescriptors;
  uint16_t wCurrentMaxPacketSize;
  /* found info */
  uint8_t bFormatIndex;
  uint8_t bFrameIndex;
  uint32_t dwFrameInterval;
  uint8_t bAlternateSetting;
  uint8_t bEndpointAddress;
} USB_CAM_GetInfoCtx;

static int USB_CAM_IsItfDesc(USBH_DescHeader_t *p_desc, USB_CAM_GetInfoCtx *p_ctx)
{
  USB_ItfDesc desc;

  if (p_desc->bLength != sizeof(USB_ItfDesc) ||
      p_desc->bDescriptorType != 4)
    return 0;

  USB_CAM_FillItfDesc(&desc, (uint8_t *)p_desc);
  p_ctx->bCurrentInterfaceNumber = desc.bInterfaceNumber;
  p_ctx->bCurrentAlternateSetting = desc.bAlternateSetting;
  p_ctx->bCurrentFormatIndex = 0;
  p_ctx->bCurrentNumFrameDescriptors = 0;

  return 1;
}

static int USB_CAM_IsUvcEndpointDesc(USBH_DescHeader_t *p_desc, USB_CAM_GetInfoCtx *p_ctx)
{
  USB_EpDesc desc;

  if (p_desc->bLength != sizeof(desc) ||
      p_desc->bDescriptorType != 5)
    return 0;

  USB_CAM_FillEpDesc(&desc, (uint8_t *)p_desc);

  if (desc.wMaxPacketSize <= p_ctx->wCurrentMaxPacketSize ||
      desc.wMaxPacketSize > USB_CAM_MAX_PACKET_SIZE)
    return 1;

  p_ctx->wCurrentMaxPacketSize = desc.wMaxPacketSize;
  p_ctx->bAlternateSetting = p_ctx->bCurrentAlternateSetting;
  p_ctx->bEndpointAddress = desc.bEndpointAddress;

  return 1;
}

static int USB_CAM_IsUvcUncompressedFmtDesc(USBH_DescHeader_t *p_desc, USB_CAM_GetInfoCtx *p_ctx)
{
  const uint8_t YUY2_guid[] = {0x59, 0x55, 0x59, 0x32, 0x00, 0x00, 0x10, 0x00,
                               0x80, 0x00, 0x00, 0xAA, 0x00, 0x38, 0x9B, 0x71};
  UVC_UncompFmtDesc desc;
  int i;

  if (p_desc->bLength != sizeof(UVC_UncompFmtDesc) ||
      p_desc->bDescriptorType != CS_INTERFACE)
    return 0;

  USB_CAM_FillUncompFmtDesc(&desc, (uint8_t *)p_desc);

  if (desc.bDescriptorSubType != VS_FORMAT_UNCOMPRESSED)
    return 0;

  for (i = 0; i < 16; i++)
  {
    if (desc.guidFormat[i] != YUY2_guid[i])
      return 0;
  }

  p_ctx->bCurrentFormatIndex = desc.bFormatIndex;
  p_ctx->bCurrentNumFrameDescriptors = desc.bNumFrameDescriptors;

  return 1;
}

static int USB_CAM_IsUvcJpegFmtDesc(USBH_DescHeader_t *p_desc, USB_CAM_GetInfoCtx *p_ctx)
{
  UVC_JpegFmtDesc desc;

  if (p_desc->bLength != sizeof(UVC_JpegFmtDesc) ||
      p_desc->bDescriptorType != CS_INTERFACE)
    return 0;

  USB_CAM_FillJpegFmtDesc(&desc, (uint8_t *)p_desc);

  if (desc.bDescriptorSubType != VS_FORMAT_MJPEG)
    return 0;

  p_ctx->bCurrentFormatIndex = desc.bFormatIndex;
  p_ctx->bCurrentNumFrameDescriptors = desc.bNumFrameDescriptors;

  return 1;
}

static int USB_CAM_IsUvcXxxFrameDesc(USBH_DescHeader_t *p_desc, USB_CAM_GetInfoCtx *p_ctx)
{
  UVC_XxxFrameDesc desc;
  int i;

  if (p_desc->bLength < 26 ||
      p_desc->bDescriptorType != CS_INTERFACE)
    return 0;

  USB_CAM_FillXxxFrameDesc(&desc, (uint8_t *) p_desc);

  if (p_ctx->bCurrentNumFrameDescriptors == 0)
    return 0;

  if (desc.bDescriptorSubType != VS_FRAME_UNCOMPRESSED &&
      desc.bDescriptorSubType != VS_FRAME_MJPEG)
    return 0;

  if (desc.bFrameIndex == p_ctx->bCurrentNumFrameDescriptors)
  {
    p_ctx->bCurrentFormatIndex = 0;
    p_ctx->bCurrentNumFrameDescriptors = 0;
  }

  if (desc.wWidth != p_ctx->target_width ||
      desc.wHeight != p_ctx->target_height)
    return 1;

  if (!desc.bFrameIntervalType)
    return 1;

  for (i = 0; i < desc.bFrameIntervalType; i++)
  {
    if (desc.dwFrameInterval[i] == p_ctx->target_period)
      break;
  }
  if (i == desc.bFrameIntervalType)
    return 1;

  /* we found it !!!! */
  p_ctx->bFormatIndex = p_ctx->bCurrentFormatIndex;
  p_ctx->bFrameIndex = desc.bFrameIndex;
  p_ctx->dwFrameInterval = desc.dwFrameInterval[i];

  return 1;
}

static int USB_CAM_FindInfo(USBH_DescHeader_t *p_desc, void *args)
{
  USB_CAM_GetInfoCtx *p_ctx = (USB_CAM_GetInfoCtx *) args;

  if (USB_CAM_IsItfDesc(p_desc, p_ctx))
    return 0;

  if (p_ctx->bCurrentInterfaceNumber != p_ctx->bTargetInterfaceNumber)
    return 0;

  if (USB_CAM_IsUvcEndpointDesc(p_desc, p_ctx))
    return 0;

  if (p_ctx->target_payload_type == USB_CAM_PAYLOAD_UNCOMPRESSED && USB_CAM_IsUvcUncompressedFmtDesc(p_desc, p_ctx))
    return 0;

  if (p_ctx->target_payload_type == USB_CAM_PAYLOAD_JPEG && USB_CAM_IsUvcJpegFmtDesc(p_desc, p_ctx))
     return 0;

  if (USB_CAM_IsUvcXxxFrameDesc(p_desc, p_ctx))
    return 0;

  return 0;
}

static USBH_StatusTypeDef USB_CAM_GetInfo(struct _USBH_HandleTypeDef *phost)
{
  USBH_InterfaceDescTypeDef *itf = &phost->device.CfgDesc.Itf_Desc[1];
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USB_CAM_Info_t *p_info = &p_ctx->info;
  USB_CAM_GetInfoCtx ctx = {
    .bTargetInterfaceNumber = itf->bInterfaceNumber,
    .target_width = p_ctx->width,
    .target_height = p_ctx->height,
    .target_period = p_ctx->period,
    .target_payload_type = p_ctx->payload_type,
  };

  USB_CAM_VisitCfgDesc(phost, USB_CAM_FindInfo, &ctx);
  USBH_DbgLog("XXX bFormatIndex = %d", ctx.bFormatIndex);
  USBH_DbgLog("XXX bFrameIndex = %d", ctx.bFrameIndex);
  USBH_DbgLog("XXX dwFrameInterval = %ld", ctx.dwFrameInterval);
  USBH_DbgLog("XXX bAlternateSetting = %d", ctx.bAlternateSetting);
  USBH_DbgLog("XXX bEndpointAddress = 0x%02x", ctx.bEndpointAddress);
  USBH_DbgLog("XXX wCurrentMaxPacketSize = %d", ctx.wCurrentMaxPacketSize);

  p_info->bInterfaceNumber = itf->bInterfaceNumber;
  p_info->bFormatIndex = ctx.bFormatIndex;
  p_info->bFrameIndex = ctx.bFrameIndex;
  p_info->dwFrameInterval = ctx.dwFrameInterval;
  p_info->bAlternateSetting = ctx.bAlternateSetting;
  p_info->bEndpointAddress = ctx.bEndpointAddress;

  return p_info->bFrameIndex ? USBH_OK : USBH_FAIL;
}

USBH_StatusTypeDef USB_CAM_ClassInitGatherInfo(struct _USBH_HandleTypeDef *phost)
{
  return USB_CAM_GetInfo(phost);
}
