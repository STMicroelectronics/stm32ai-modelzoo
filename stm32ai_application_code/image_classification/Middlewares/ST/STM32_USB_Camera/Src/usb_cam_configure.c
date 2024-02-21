 /**
 ******************************************************************************
 * @file    usb_cam_configure.c
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
#include "usb_cam_configure.h"

#include <assert.h>

#include "usb_cam_private.h"
#include "usbh_core.h"
#include "usb_cam_uvc.h"
#include "usbh_def.h"

static char *USB_CAM_st2string(ENUM_SetupState state)
{
  static char *s2s[] = {"SETUP_STATE_SET_VS_ITF", "SETUP_STATE_SETCUR_PROBE", "SETUP_STATE_GETCUR_PROBE",
                        "SETUP_STATE_SETCUR_COMMIT", "SETUP_STATE_SET_VS_ALT_ITF", "SETUP_STATE_LAST_STATE",
  };

  return s2s[state];
}

static USBH_StatusTypeDef USB_CAM_GoNextStateIfOk(USB_CAM_Ctx_t *p_ctx, USBH_StatusTypeDef status,
                                                  ENUM_SetupState next_state)
{
  switch (status) {
    case USBH_OK:
      p_ctx->setup_state = next_state;
      return USBH_BUSY;
    case USBH_BUSY:
      return USBH_BUSY;
    default:
      return USBH_FAIL;
  }
}

static USBH_StatusTypeDef USB_CAM_SetCurCmd(struct _USBH_HandleTypeDef *phost, uint16_t cs,
                                            uint16_t itf_nb, int len, uint8_t *buf)
{
  if (phost->RequestState == CMD_SEND)
  {
    phost->Control.setup.b.bmRequestType = USB_H2D | USB_REQ_TYPE_CLASS | USB_REQ_RECIPIENT_INTERFACE;
    phost->Control.setup.b.bRequest = UVC_SET_CUR;
    phost->Control.setup.b.wValue.w = cs;
    phost->Control.setup.b.wIndex.w = itf_nb;
    phost->Control.setup.b.wLength.w = len;
  }

  return USBH_CtlReq(phost, buf, len);
}

static USBH_StatusTypeDef USB_CAM_GetCurCmd(struct _USBH_HandleTypeDef *phost, uint16_t cs,
                                            uint16_t itf_nb, int len, uint8_t *buf)
{
  if (phost->RequestState == CMD_SEND)
  {
    phost->Control.setup.b.bmRequestType = USB_D2H | USB_REQ_TYPE_CLASS | USB_REQ_RECIPIENT_INTERFACE;
    phost->Control.setup.b.bRequest = UVC_GET_CUR;
    phost->Control.setup.b.wValue.w = cs;
    phost->Control.setup.b.wIndex.w = itf_nb;
    phost->Control.setup.b.wLength.w = len;
  }

  return USBH_CtlReq(phost, buf, len);
}

static USBH_StatusTypeDef USB_CAM_SetupVsItf(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  ret = USBH_SetInterface(phost, p_ctx->info.bInterfaceNumber, 0);

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_SETCUR_PROBE);
}

static USBH_StatusTypeDef USB_CAM_SetCurProbeV10(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  p_ctx->probe.v10.bFormatIndex = p_ctx->info.bFormatIndex;
  p_ctx->probe.v10.bFrameIndex = p_ctx->info.bFrameIndex;
  p_ctx->probe.v10.dwFrameInterval = p_ctx->info.dwFrameInterval;
  ret = USB_CAM_SetCurCmd(phost, VS_PROBE_CONTROL, p_ctx->info.bInterfaceNumber,
                          sizeof(p_ctx->probe.v10), (uint8_t *)&p_ctx->probe.v10);

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_GETCUR_PROBE);
}

static USBH_StatusTypeDef USB_CAM_SetCurProbeV11(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  p_ctx->probe.v11.bFormatIndex = p_ctx->info.bFormatIndex;
  p_ctx->probe.v11.bFrameIndex = p_ctx->info.bFrameIndex;
  p_ctx->probe.v11.dwFrameInterval = p_ctx->info.dwFrameInterval;
  ret = USB_CAM_SetCurCmd(phost, VS_PROBE_CONTROL, p_ctx->info.bInterfaceNumber,
                          sizeof(p_ctx->probe.v11), (uint8_t *)&p_ctx->probe.v11);

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_GETCUR_PROBE);
}

static USBH_StatusTypeDef USB_CAM_SetCurProbe(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);

  switch(p_ctx->bcdUVC)
  {
    case UVC_VERSION_1_0:
      return USB_CAM_SetCurProbeV10(phost);
    case UVC_VERSION_1_1:
      return USB_CAM_SetCurProbeV11(phost);
    default:
      return USBH_FAIL;
  }
}

static USBH_StatusTypeDef USB_CAM_GetCurProbeV10(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  ret = USB_CAM_GetCurCmd(phost, VS_PROBE_CONTROL, p_ctx->info.bInterfaceNumber,
                          sizeof(p_ctx->probe.v10), (uint8_t *)&p_ctx->probe.v10);

  if (ret == USBH_OK)
  {
    if (p_ctx->probe.v10.bFormatIndex != p_ctx->info.bFormatIndex ||
        p_ctx->probe.v10.bFrameIndex != p_ctx->info.bFrameIndex ||
        p_ctx->probe.v10.dwFrameInterval != p_ctx->info.dwFrameInterval)
    {
      USBH_DbgLog("Unable to setup device");
      return USBH_FAIL;
    }
  }

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_SETCUR_COMMIT);
}

static USBH_StatusTypeDef USB_CAM_GetCurProbeV11(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  ret = USB_CAM_GetCurCmd(phost, VS_PROBE_CONTROL, p_ctx->info.bInterfaceNumber,
                          sizeof(p_ctx->probe.v11), (uint8_t *)&p_ctx->probe.v11);

  if (ret == USBH_OK)
  {
    if (p_ctx->probe.v11.bFormatIndex != p_ctx->info.bFormatIndex ||
        p_ctx->probe.v11.bFrameIndex != p_ctx->info.bFrameIndex ||
        p_ctx->probe.v11.dwFrameInterval != p_ctx->info.dwFrameInterval)
    {
      USBH_DbgLog("Unable to setup device");
      return USBH_FAIL;
    }
  }

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_SETCUR_COMMIT);
}

static USBH_StatusTypeDef USB_CAM_GetCurProbe(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);

  switch(p_ctx->bcdUVC)
  {
    case UVC_VERSION_1_0:
      return USB_CAM_GetCurProbeV10(phost);
    case UVC_VERSION_1_1:
      return USB_CAM_GetCurProbeV11(phost);
    default:
      return USBH_FAIL;
  }
}

static USBH_StatusTypeDef USB_CAM_SetCurCommitV10(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  p_ctx->commit = p_ctx->probe;
  ret = USB_CAM_SetCurCmd(phost, VS_COMMIT_CONTROL, p_ctx->info.bInterfaceNumber,
                          sizeof(p_ctx->commit.v10), (uint8_t *)&p_ctx->commit.v10);

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_SET_VS_ALT_ITF);
}

static USBH_StatusTypeDef USB_CAM_SetCurCommitV11(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  p_ctx->commit = p_ctx->probe;
  ret = USB_CAM_SetCurCmd(phost, VS_COMMIT_CONTROL, p_ctx->info.bInterfaceNumber,
                          sizeof(p_ctx->commit.v11), (uint8_t *)&p_ctx->commit.v11);

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_SET_VS_ALT_ITF);
}

static USBH_StatusTypeDef USB_CAM_SetCurCommit(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);

  switch(p_ctx->bcdUVC)
  {
    case UVC_VERSION_1_0:
      return USB_CAM_SetCurCommitV10(phost);
    case UVC_VERSION_1_1:
      return USB_CAM_SetCurCommitV11(phost);
    default:
      return USBH_FAIL;
  }
}

static USBH_StatusTypeDef USB_CAM_SetupVsAltItf(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  ret = USBH_SetInterface(phost, p_ctx->info.bInterfaceNumber, p_ctx->info.bAlternateSetting);

  return USB_CAM_GoNextStateIfOk(p_ctx, ret, SETUP_STATE_LAST_STATE);
}

USBH_StatusTypeDef USB_CAM_ConfigureDevice(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret = USBH_BUSY;
  ENUM_SetupState prev_state;

  prev_state = p_ctx->setup_state;
  switch (p_ctx->setup_state) {
    case SETUP_STATE_SET_VS_ITF:
      ret = USB_CAM_SetupVsItf(phost);
    case SETUP_STATE_SETCUR_PROBE:
      ret = USB_CAM_SetCurProbe(phost);
      break;
    case SETUP_STATE_GETCUR_PROBE:
      ret = USB_CAM_GetCurProbe(phost);
      break;
    case SETUP_STATE_SETCUR_COMMIT:
      ret = USB_CAM_SetCurCommit(phost);
      break;
    case SETUP_STATE_SET_VS_ALT_ITF:
      ret = USB_CAM_SetupVsAltItf(phost);
      break;
    case SETUP_STATE_LAST_STATE:
      ret = USBH_OK;
      break;
    default:
      ret = USBH_FAIL;
      assert(0);
      break;
  }

  if (p_ctx->setup_state != prev_state)
    USBH_DbgLog("### %s -> %s", USB_CAM_st2string(prev_state), USB_CAM_st2string(p_ctx->setup_state));

  return ret;
}
