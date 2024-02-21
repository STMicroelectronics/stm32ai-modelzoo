 /**
 ******************************************************************************
 * @file    usb_cam_enumeration.c
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
#include "usb_cam_enumeration.h"

#include <assert.h>

#include "usbh_conf.h"
#include "usbh_core.h"

#include "usb_cam_uvc.h"

#define USB_CAM_UVC_PARSE_CFG_SEARCH_VIDEO_IAD 0
#define USB_CAM_UVC_PARSE_CFG_GATHER_VIDEO_ITF 1

#define USB_DESC_TYPE_INTERFACE_ASSOCIATION 11

typedef struct _InterfaceAssociationDescriptor
{
  uint8_t bLength;
  uint8_t bDescriptorType;
  uint8_t bFirstInterface;
  uint8_t bInterfaceCount;
  uint8_t bFunctionClass;
  uint8_t bFunctionSubClass;
  uint8_t bFunctionProtocol;
  uint8_t iFunction;
}
USBH_InterfaceAssocDescTypeDef;

typedef struct {
  int state;
  int if_idx;
  /* info needed */
  int video_itf_idx_start;
  int video_itf_idx_end;
} USB_CAM_UVCParseCfgDescCtx;

static USBH_StatusTypeDef USB_CAM_ParseEPDesc(USBH_HandleTypeDef *phost, USBH_EpDescTypeDef *ep_descriptor, uint8_t *buf)
{
  USBH_StatusTypeDef status = USBH_OK;

  ep_descriptor->bLength          = *(uint8_t *)(buf + 0U);
  ep_descriptor->bDescriptorType  = *(uint8_t *)(buf + 1U);
  ep_descriptor->bEndpointAddress = *(uint8_t *)(buf + 2U);
  ep_descriptor->bmAttributes     = *(uint8_t *)(buf + 3U);
  ep_descriptor->wMaxPacketSize   = LE16(buf + 4U);
  ep_descriptor->bInterval        = *(uint8_t *)(buf + 6U);

  /* Make sure that wMaxPacketSize is different from 0 */
  if ((ep_descriptor->wMaxPacketSize == 0x00U) ||
      (ep_descriptor->wMaxPacketSize > USBH_MAX_EP_PACKET_SIZE) ||
      (ep_descriptor->wMaxPacketSize > USBH_MAX_DATA_BUFFER))
  {
    status = USBH_NOT_SUPPORTED;
  }

  if (phost->device.speed == (uint8_t)USBH_SPEED_HIGH)
  {
    if ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_BULK)
    {
      if (ep_descriptor->wMaxPacketSize > 512U)
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    else if ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_CTRL)
    {
      if (ep_descriptor->wMaxPacketSize > 64U)
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    /* For high-speed interrupt/isochronous endpoints, bInterval can vary from 1 to 16 */
    else if (((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_ISOC) ||
        ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_INTR))
    {
      if ((ep_descriptor->bInterval == 0U) || (ep_descriptor->bInterval > 0x10U))
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    else
    {
      status = USBH_NOT_SUPPORTED;
    }
  }
  else if (phost->device.speed == (uint8_t)USBH_SPEED_FULL)
  {
    if (((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_BULK) ||
        ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_CTRL))
    {
      if (ep_descriptor->wMaxPacketSize > 64U)
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    /* For full-speed isochronous endpoints, the value of bInterval must be in the range from 1 to 16.*/
    else if ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_ISOC)
    {
      if ((ep_descriptor->bInterval == 0U) ||
          (ep_descriptor->bInterval > 0x10U) ||
          (ep_descriptor->wMaxPacketSize > 64U))
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    /* For full-speed interrupt endpoints, the value of bInterval may be from 1 to 255.*/
    else if ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_INTR)
    {
      if ((ep_descriptor->bInterval == 0U) || (ep_descriptor->wMaxPacketSize > 1023U))
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    else
    {
      status = USBH_NOT_SUPPORTED;
    }
  }
  else if (phost->device.speed == (uint8_t)USBH_SPEED_LOW)
  {
    if ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_CTRL)
    {
      if (ep_descriptor->wMaxPacketSize != 8U)
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    /* For low-speed interrupt endpoints, the value of bInterval may be from 1 to 255.*/
    else if ((ep_descriptor->bmAttributes & EP_TYPE_MSK) == EP_TYPE_INTR)
    {
      if ((ep_descriptor->bInterval == 0U) || (ep_descriptor->wMaxPacketSize > 8U))
      {
        status = USBH_NOT_SUPPORTED;
      }
    }
    else
    {
      status = USBH_NOT_SUPPORTED;
    }
  }
  else
  {
    status = USBH_NOT_SUPPORTED;
  }

  return status;
}

static void USB_CAM_ParseInterfaceDesc(USBH_InterfaceDescTypeDef *if_descriptor, uint8_t *buf)
{
  if_descriptor->bLength            = *(uint8_t *)(buf + 0U);
  if_descriptor->bDescriptorType    = *(uint8_t *)(buf + 1U);
  if_descriptor->bInterfaceNumber   = *(uint8_t *)(buf + 2U);
  if_descriptor->bAlternateSetting  = *(uint8_t *)(buf + 3U);
  if_descriptor->bNumEndpoints      = MIN(*(uint8_t *)(buf + 4U), USBH_MAX_NUM_ENDPOINTS);
  if_descriptor->bInterfaceClass    = *(uint8_t *)(buf + 5U);
  if_descriptor->bInterfaceSubClass = *(uint8_t *)(buf + 6U);
  if_descriptor->bInterfaceProtocol = *(uint8_t *)(buf + 7U);
  if_descriptor->iInterface         = *(uint8_t *)(buf + 8U);
}

static int USB_CAM_IsInVideoIadRange(USBH_InterfaceDescTypeDef *itf, USB_CAM_UVCParseCfgDescCtx *ctx)
{
  if (itf->bInterfaceNumber < ctx->video_itf_idx_start)
    return 0;

  if (itf->bInterfaceNumber > ctx->video_itf_idx_end)
    return 0;

  return 1;
}

static void USB_CAM_SearchVideoIAD(USBH_HandleTypeDef *phost, USBH_DescHeader_t *pdesc, USB_CAM_UVCParseCfgDescCtx *ctx)
{
  USBH_InterfaceAssocDescTypeDef *itf_assoc = (USBH_InterfaceAssocDescTypeDef *)pdesc;

  if (pdesc->bDescriptorType != USB_DESC_TYPE_INTERFACE_ASSOCIATION)
    return;

  if (itf_assoc->bFunctionClass != CC_VIDEO)
    return;

  if (itf_assoc->bFunctionSubClass != SC_VIDEO_INTERFACE_COLLECTION)
    return;

  if (itf_assoc->bFunctionProtocol != PC_PROTOCOL_UNDEFINED)
    return ;

  ctx->state = USB_CAM_UVC_PARSE_CFG_GATHER_VIDEO_ITF;
  ctx->video_itf_idx_start = itf_assoc->bFirstInterface;
  ctx->video_itf_idx_end = ctx->video_itf_idx_start + itf_assoc->bInterfaceCount - 1;
}

static USBH_DescHeader_t *USB_CAM_GatherVideoItf(USBH_HandleTypeDef *phost, USBH_DescHeader_t *pdesc,
                                                 USB_CAM_UVCParseCfgDescCtx *ctx, uint16_t *pos)
{
  USBH_CfgDescTypeDef *cfg_desc = &phost->device.CfgDesc;
  USBH_InterfaceDescTypeDef *itf;
  USBH_StatusTypeDef status;
  USBH_EpDescTypeDef *pep;
  int ep_ix = 0;

  if (pdesc->bDescriptorType != USB_DESC_TYPE_INTERFACE)
    return pdesc;

  if (ctx->if_idx >= USBH_MAX_NUM_INTERFACES) {
    USBH_DbgLog("Reach max itf number. Skipping it ....");
    return pdesc;
  }

  itf = &phost->device.CfgDesc.Itf_Desc[ctx->if_idx];
  USB_CAM_ParseInterfaceDesc(itf, (uint8_t *)pdesc);
  if (!USB_CAM_IsInVideoIadRange(itf, ctx))
    return pdesc;

  /* find itf endpoints */
  while ((*pos + USB_LEN_DESC_HDR <= cfg_desc->wTotalLength) &&
         (ep_ix < itf->bNumEndpoints) && (ep_ix < USBH_MAX_NUM_ENDPOINTS))
  {
    pdesc = USBH_GetNextDesc((uint8_t *)pdesc, pos);

    if (pdesc->bDescriptorType != USB_DESC_TYPE_ENDPOINT)
      continue;

    pep = &cfg_desc->Itf_Desc[ctx->if_idx].Ep_Desc[ep_ix];
    status = USB_CAM_ParseEPDesc(phost, pep, (uint8_t *)(void *)pdesc);

    if (status != USBH_OK) {
      USBH_DbgLog("Skip itf due to unsupported ep");
      memset(itf, 0, sizeof(*itf));
      return pdesc;
    }

    ep_ix++;
  }

  if (ep_ix < itf->bNumEndpoints) {
    USBH_DbgLog("Skip itf due to missing ep");
    memset(itf, 0, sizeof(*itf));
    return pdesc;
  }

  USBH_DbgLog("Adding itf to list : %d.%d : %d endpoints",
              itf->bInterfaceNumber, itf->bAlternateSetting, itf->bNumEndpoints);

  ctx->if_idx++;

  return pdesc;
}

static USBH_StatusTypeDef USB_CAM_UVCParseCfgDesc(USBH_HandleTypeDef *phost, uint8_t *buf, uint16_t length)
{
  USBH_CfgDescTypeDef *cfg_desc = &phost->device.CfgDesc;
  USBH_DescHeader_t *pdesc = (USBH_DescHeader_t *) buf;
  USB_CAM_UVCParseCfgDescCtx ctx = { 0 };
  uint16_t pos = 0;

  ctx.state = USB_CAM_UVC_PARSE_CFG_SEARCH_VIDEO_IAD;
  ctx.if_idx = 0;

  while (pos + USB_LEN_DESC_HDR <= cfg_desc->wTotalLength)
  {
    pdesc = USBH_GetNextDesc((uint8_t *)pdesc, &pos);
    if (pdesc->bLength == 0 || pdesc->bDescriptorType == 0)
      break;
    switch (ctx.state) {
      case USB_CAM_UVC_PARSE_CFG_SEARCH_VIDEO_IAD:
        USB_CAM_SearchVideoIAD(phost, pdesc, &ctx);
        break;
      case USB_CAM_UVC_PARSE_CFG_GATHER_VIDEO_ITF:
        pdesc = USB_CAM_GatherVideoItf(phost, pdesc, &ctx, &pos);
        break;
      default:
        assert(0);
        break;
    }
  }

  return USBH_OK;
}

static USBH_StatusTypeDef USB_CAM_UVCGetCfgDesc(USBH_HandleTypeDef *phost, uint16_t length)
{
  USBH_StatusTypeDef status;
  uint8_t *pData = phost->device.CfgDesc_Raw;

  if (length > sizeof(phost->device.CfgDesc_Raw))
  {
    USBH_ErrLog("Control error: Get configuration Descriptor failed, data buffer size issue");
    return USBH_NOT_SUPPORTED;
  }

  status = USBH_GetDescriptor(phost, (USB_REQ_RECIPIENT_DEVICE | USB_REQ_TYPE_STANDARD),
                              USB_DESC_CONFIGURATION, pData, length);
  if (status != USBH_OK)
    return status;

  return USB_CAM_UVCParseCfgDesc(phost, pData, length);
}

static void USBH_DeviceNotSupported(char *msg, USBH_HandleTypeDef *phost, HOST_StateTypeDef next_state)
{
  printf("ERROR: %s\n", msg);
  phost->device.EnumCnt++;
  if (phost->device.EnumCnt > 3U)
  {
    /* Buggy Device can't complete get device desc request */
    USBH_UsrLog("Control error, Device not Responding Please unplug the Device.");
    phost->gState = HOST_ABORT_STATE;
  }
  else
  {
    /* free control pipes */
    (void)USBH_FreePipe(phost, phost->Control.pipe_out);
    (void)USBH_FreePipe(phost, phost->Control.pipe_in);

    /* Reset the USB Device */
    phost->EnumState = ENUM_IDLE;
    phost->gState = next_state;
  }
}

static USBH_StatusTypeDef USB_CAM_HandleEnumIdle(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  ReqStatus = USBH_Get_DevDesc(phost, 8U);

  switch (ReqStatus) {
    case USBH_OK:
      phost->Control.pipe_size = phost->device.DevDesc.bMaxPacketSize;

      phost->EnumState = ENUM_GET_FULL_DEV_DESC;

      /* modify control channels configuration for MaxPacket size */
      (void)USBH_OpenPipe(phost, phost->Control.pipe_in, 0x80U, phost->device.address,
                          phost->device.speed, USBH_EP_CONTROL,
                          (uint16_t)phost->Control.pipe_size);

      /* Open Control pipes */
      (void)USBH_OpenPipe(phost, phost->Control.pipe_out, 0x00U, phost->device.address,
                          phost->device.speed, USBH_EP_CONTROL,
                          (uint16_t)phost->Control.pipe_size);
      break;
    case USBH_NOT_SUPPORTED:
      USBH_DeviceNotSupported("Control error: Get Device Descriptor request failed", phost, HOST_IDLE);
      break;
    default:
      /* Do nothing */
      break;
  }

  return USBH_BUSY;
}

static USBH_StatusTypeDef USB_CAM_HandleEnumGetFullDevDesc(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  ReqStatus = USBH_Get_DevDesc(phost, USB_DEVICE_DESC_SIZE);

  switch (ReqStatus) {
    case USBH_OK:
      USBH_UsrLog("PID: %xh", phost->device.DevDesc.idProduct);
      USBH_UsrLog("VID: %xh", phost->device.DevDesc.idVendor);

      phost->EnumState = ENUM_SET_ADDR;
      break;
    case USBH_NOT_SUPPORTED:
      USBH_DeviceNotSupported("Control error: Get Full Device Descriptor request failed", phost, HOST_IDLE);
      break;
    default:
      /* Do nothing */
      break;
  }

  return USBH_BUSY;
}

static USBH_StatusTypeDef USB_CAM_HandleEnumSetAddr(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  ReqStatus = USBH_SetAddress(phost, USBH_DEVICE_ADDRESS);

  switch (ReqStatus) {
    case USBH_OK:
      USBH_Delay(2U);
      phost->device.address = USBH_DEVICE_ADDRESS;

      /* user callback for device address assigned */
      USBH_UsrLog("Address (#%d) assigned.", phost->device.address);
      phost->EnumState = ENUM_GET_CFG_DESC;

      /* modify control channels to update device address */
      (void)USBH_OpenPipe(phost, phost->Control.pipe_in, 0x80U,  phost->device.address,
                          phost->device.speed, USBH_EP_CONTROL,
                          (uint16_t)phost->Control.pipe_size);

      /* Open Control pipes */
      (void)USBH_OpenPipe(phost, phost->Control.pipe_out, 0x00U, phost->device.address,
                          phost->device.speed, USBH_EP_CONTROL,
                          (uint16_t)phost->Control.pipe_size);
      break;
    case USBH_NOT_SUPPORTED:
      USBH_DeviceNotSupported("Control error: Device Set Address request failed", phost, HOST_ABORT_STATE);
      break;
    default:
      /* Do nothing */
      break;
  }

  return USBH_BUSY;
}

static USBH_StatusTypeDef USB_CAM_HandleEnumGetCfgDesc(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  ReqStatus = USBH_Get_CfgDesc(phost, USB_CONFIGURATION_DESC_SIZE);

  switch (ReqStatus) {
    case USBH_OK:
      phost->EnumState = ENUM_GET_FULL_CFG_DESC;
      break;
    case USBH_NOT_SUPPORTED:
      USBH_DeviceNotSupported("Control error: Get Device configuration descriptor request failed", phost, HOST_IDLE);
      break;
    default:
      /* Do nothing */
      break;
  }

  return USBH_BUSY;
}

static USBH_StatusTypeDef USB_CAM_HandleEnumGetCfgFullCfgDesc(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  ReqStatus = USB_CAM_UVCGetCfgDesc(phost, phost->device.CfgDesc.wTotalLength);

  switch (ReqStatus) {
    case USBH_OK:
      phost->EnumState = ENUM_GET_MFC_STRING_DESC;
      break;
    case USBH_NOT_SUPPORTED:
      USBH_DeviceNotSupported("Control error: Get Device configuration descriptor request failed", phost, HOST_ABORT_STATE/*HOST_IDLE*/);
      break;
    default:
      /* Do nothing */
      break;
  }

  return USBH_BUSY;
}

static USBH_StatusTypeDef USB_CAM_HandleEnumGetMfcStringDesc(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  if (!phost->device.DevDesc.iManufacturer)
  {
    USBH_UsrLog("Manufacturer : N/A");
    phost->EnumState = ENUM_GET_PRODUCT_STRING_DESC;

    return USBH_BUSY;
  }

  ReqStatus = USBH_Get_StringDesc(phost, phost->device.DevDesc.iManufacturer, phost->device.Data, 0xFFU);

  switch (ReqStatus) {
    case USBH_OK:
      USBH_UsrLog("Manufacturer : %s", (char *)(void *)phost->device.Data);
      phost->EnumState = ENUM_GET_PRODUCT_STRING_DESC;
      break;
    case USBH_NOT_SUPPORTED:
      USBH_UsrLog("Manufacturer : N/A");
      phost->EnumState = ENUM_GET_PRODUCT_STRING_DESC;
      break;
    default:
      /* Do nothing */
      break;
  }

  return USBH_BUSY;
}

static USBH_StatusTypeDef USB_CAM_HandleEnumGetProductStringDesc(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  if (!phost->device.DevDesc.iProduct)
  {
    USBH_UsrLog("Product : N/A");
    phost->EnumState = ENUM_GET_SERIALNUM_STRING_DESC;

    return USBH_BUSY;
  }

  ReqStatus = USBH_Get_StringDesc(phost, phost->device.DevDesc.iProduct, phost->device.Data, 0xFFU);

  switch (ReqStatus) {
    case USBH_OK:
      USBH_UsrLog("Product : %s", (char *)(void *)phost->device.Data);
      phost->EnumState = ENUM_GET_SERIALNUM_STRING_DESC;
      break;
    case USBH_NOT_SUPPORTED:
      USBH_UsrLog("Product : N/A");
      phost->EnumState = ENUM_GET_SERIALNUM_STRING_DESC;
      break;
    default:
      /* Do nothing */
      break;
  }

  return USBH_BUSY;
}

static USBH_StatusTypeDef USB_CAM_HandleEnumGetSerialNumStringDesc(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef ReqStatus;

  if (!phost->device.DevDesc.iSerialNumber)
  {
    USBH_UsrLog("Serial Number : N/A");

    return USBH_OK;
  }

  ReqStatus = USBH_Get_StringDesc(phost, phost->device.DevDesc.iSerialNumber, phost->device.Data, 0xFFU);

  switch (ReqStatus) {
    case USBH_OK:
      USBH_UsrLog("Serial Number : %s", (char *)(void *)phost->device.Data);
      break;
    case USBH_NOT_SUPPORTED:
      USBH_UsrLog("Serial Number : N/A");
      ReqStatus = USBH_OK;
      break;
    default:
      /* Do nothing */
      break;
  }

  return ReqStatus;
}

USBH_StatusTypeDef USB_CAM_ProcessEnumerationWrapper(USBH_HandleTypeDef *phost)
{
  static ENUM_StateTypeDef PrevEnumState = ENUM_IDLE;
  USBH_StatusTypeDef res = USBH_BUSY;

  if (PrevEnumState != phost->EnumState)
    printf("  %d -> %d\n", PrevEnumState, phost->EnumState);
  switch (phost->EnumState)
  {
    case ENUM_IDLE:
      /* Get Device Desc for only 1st 8 bytes : To get EP0 MaxPacketSize */
      res = USB_CAM_HandleEnumIdle(phost);
      break;
    case ENUM_GET_FULL_DEV_DESC:
      /* Get FULL Device Desc  */
      res = USB_CAM_HandleEnumGetFullDevDesc(phost);
      break;
    case ENUM_SET_ADDR:
      /* set address */
      res = USB_CAM_HandleEnumSetAddr(phost);
      break;
    case ENUM_GET_CFG_DESC:
      /* get standard configuration descriptor */
      res = USB_CAM_HandleEnumGetCfgDesc(phost);
      break;
    case ENUM_GET_FULL_CFG_DESC:
      /* get FULL config descriptor (config, interface, endpoints) */
      res = USB_CAM_HandleEnumGetCfgFullCfgDesc(phost);
      break;
    case ENUM_GET_MFC_STRING_DESC:
      res = USB_CAM_HandleEnumGetMfcStringDesc(phost);
      break;
    case ENUM_GET_PRODUCT_STRING_DESC:
      res = USB_CAM_HandleEnumGetProductStringDesc(phost);
      break;
    case ENUM_GET_SERIALNUM_STRING_DESC:
      res = USB_CAM_HandleEnumGetSerialNumStringDesc(phost);
      break;
    default:
      assert(0);
      break;
  }
  PrevEnumState = phost->EnumState;

  return res;
}
