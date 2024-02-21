 /**
 ******************************************************************************
 * @file    usb_cam.c
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
#include "usb_cam.h"

#include <stdlib.h>
#include <assert.h>
#include <string.h>

#include "stm32h7xx_hal.h"
#include "usbh_conf.h"
#include "usbh_core.h"
#include "usbh_def.h"
#include "usb_cam_uvc.h"

#include "usb_cam_private.h"
#include "usb_cam_enumeration.h"
#include "usb_cam_init.h"
#include "usb_cam_configure.h"

static char *st2string(HOST_StateTypeDef state)
{
  static char *s2s[] = {"HOST_IDLE","HOST_DEV_WAIT_FOR_ATTACHMENT","HOST_DEV_ATTACHED",
                 "HOST_DEV_DISCONNECTED","HOST_DETECT_DEVICE_SPEED","HOST_ENUMERATION",
                 "HOST_CLASS_REQUEST","HOST_INPUT","HOST_SET_CONFIGURATION",
                 "HOST_SET_WAKEUP_FEATURE","HOST_CHECK_CLASS","HOST_CLASS",
                 "HOST_SUSPENDED","HOST_ABORT_STATE"};

  return s2s[state];
}

static int USB_CAM_UpdateIdx(int idx)
{
  return (idx + 1) % USB_CAM_MAX_BUFFER;
}

static USBH_StatusTypeDef USB_CAM_ClassInit(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USBH_StatusTypeDef ret;

  ret = USB_CAM_ClassInitSanityCheck(phost);
  if (ret != USBH_OK)
  {
    USBH_ErrLog("UVC device not supported\n");
    return USBH_FAIL;
  }

  ret = USB_CAM_ClassInitGatherInfo(phost);
  if (ret != USBH_OK)
  {
    USBH_ErrLog("Not found supported configuration for UVC device\n");
    return USBH_FAIL;
  }

  /* alloc and configure streaming pipe */
  p_ctx->data_pipe = USBH_AllocPipe(phost, p_ctx->info.bEndpointAddress);
  if (p_ctx->data_pipe == 0xff)
  {
    USBH_ErrLog("Unable to allocate streaming pipe at address 0x%02x\n", p_ctx->info.bEndpointAddress);
    return USBH_FAIL;
  }
  ret = USBH_OpenPipe(phost, p_ctx->data_pipe, p_ctx->info.bEndpointAddress, phost->device.address,
                      phost->device.speed, USB_EP_TYPE_ISOC, USB_CAM_MAX_PACKET_SIZE);
  if (ret != USBH_OK)
  {
    USBH_ErrLog("Unable to open streaming pipe\n");
    return USBH_FAIL;
  }

  phost->pActiveClass->pData = p_ctx;
  p_ctx->setup_state = SETUP_STATE_SET_VS_ITF;
  p_ctx->next_packet_buffer_idx = 0;
  p_ctx->frame_id = -1;

  return USBH_OK;
}

static USBH_StatusTypeDef USB_CAM_ClassDeInit(struct _USBH_HandleTypeDef *phost)
{
  assert(0);

  return USBH_FAIL;
}

static USBH_StatusTypeDef USB_CAM_ClassRequests(struct _USBH_HandleTypeDef *phost)
{
  return USB_CAM_ConfigureDevice(phost);
}

static USBH_StatusTypeDef USB_CAM_ClassBgndProcess(struct _USBH_HandleTypeDef *phost)
{
  return USBH_OK;
}

static void USB_CAM_StartIsoTransaction(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  int idx = p_ctx->next_packet_buffer_idx;

  p_ctx->is_capture_ongoing = 1;
  USBH_IsocReceiveData(phost, p_ctx->packet_buffer[idx], USB_CAM_MAX_PACKET_SIZE, p_ctx->data_pipe);
  p_ctx->next_packet_buffer_idx = 1 - idx;
}

static void USB_CAM_PacketCaptureDone(struct _USBH_HandleTypeDef *phost)
{
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);
  USB_CAM_Buffer_t *buffer = &p_ctx->buffer[p_ctx->capture_idx];
  uint8_t *packet_buffer = p_ctx->packet_buffer[1 - p_ctx->next_packet_buffer_idx];
  int bHeaderLength;
  int last_rx_size;
  int bmHeaderInfo;
  int payload_len;
  int frame_id;
  int begin_of_frame;
  int end_of_frame;
  int error;

  last_rx_size = USBH_LL_GetLastXferSize(phost, p_ctx->data_pipe);
  USB_CAM_StartIsoTransaction(phost);
  if (!last_rx_size)
    return ;

  bHeaderLength = packet_buffer[0];
  bmHeaderInfo = packet_buffer[1];
  payload_len = last_rx_size - bHeaderLength;

  if (!payload_len)
    return ;

  frame_id = bmHeaderInfo & 1;
  end_of_frame = (bmHeaderInfo >> 1) & 1;
  error = (bmHeaderInfo >> 6) & 1;
  begin_of_frame = frame_id != p_ctx->frame_id;
  p_ctx->frame_id = frame_id;

  /* end_of_frame is optional. Also detect new frame when begin_of_frame seen and
   * buffer is capturing.
   */
  if (begin_of_frame && buffer->state == BUF_STATE_CAPTURING)
  {
    buffer->state = BUF_STATE_READY;
    p_ctx->capture_idx = USB_CAM_UpdateIdx(p_ctx->capture_idx);
    buffer = &p_ctx->buffer[p_ctx->capture_idx];
  }

  if (begin_of_frame && buffer->state == BUF_STATE_AVAILABLE)
  {
    buffer->rx_pos = 0;
    buffer->has_error = 0;
    buffer->state = BUF_STATE_CAPTURING;
  }
  buffer-> has_error |= error;

  if (buffer->state == BUF_STATE_CAPTURING)
  {
    int copy_len = MIN(payload_len, buffer->len - buffer->rx_pos);

    memcpy(&buffer->data[buffer->rx_pos], &packet_buffer[bHeaderLength], copy_len);
    buffer->rx_pos += copy_len;
  }

  if (end_of_frame && buffer->state == BUF_STATE_CAPTURING)
  {
    buffer->state = BUF_STATE_READY;
    p_ctx->capture_idx = USB_CAM_UpdateIdx(p_ctx->capture_idx);
  }
}

static void USB_CAM_NotifyURBChange_Callback(HCD_HandleTypeDef *hhcd, uint8_t chnum, HCD_URBStateTypeDef urb_state)
{
  struct _USBH_HandleTypeDef *phost = hhcd->pData;
  USB_CAM_Ctx_t *p_ctx = USB_CAM_USBH2Ctx(phost);

  if (!p_ctx->is_capture_ongoing)
    return ;

  if (p_ctx->data_pipe != chnum)
    return ;

  if (urb_state == URB_DONE)
    USB_CAM_PacketCaptureDone(phost);
}

static USBH_StatusTypeDef USB_CAM_ClassSOFProcess(struct _USBH_HandleTypeDef *phost)
{
  return USBH_OK;
}

static USBH_ClassTypeDef UVC_Class = {
  "UVC", /* Video */
  0x0E,
  USB_CAM_ClassInit,
  USB_CAM_ClassDeInit,
  USB_CAM_ClassRequests,
  USB_CAM_ClassBgndProcess,
  USB_CAM_ClassSOFProcess,
  NULL,
};

static void USB_CAM_UserProcess(USBH_HandleTypeDef * phost, uint8_t id)
{
  ;
}

static USBH_StatusTypeDef USB_CAM_ProcessWrapper(USBH_HandleTypeDef *phost)
{
  USBH_StatusTypeDef res = USBH_FAIL;
  HOST_StateTypeDef prev_state;

  prev_state = phost->gState;

  /* check for Host pending port disconnect event */
  if (phost->device.is_disconnected == 1U)
  {
    phost->gState = HOST_DEV_DISCONNECTED;
  }
  switch (phost->gState) {
    case HOST_ENUMERATION:
      res = USB_CAM_ProcessEnumerationWrapper(phost);
      if (res == USBH_OK)
      {
        /* The function shall return USBH_OK when full enumeration is complete */
        USBH_UsrLog("Enumeration done.");

        phost->device.current_interface = 0U;

        if (phost->device.DevDesc.bNumConfigurations == 1U)
        {
          USBH_UsrLog("This device has only 1 configuration.");
          phost->gState = HOST_SET_CONFIGURATION;
        }
        else
        {
          phost->gState = HOST_INPUT;
        }
#if (USBH_USE_OS == 1U)
        phost->os_msg = (uint32_t)USBH_STATE_CHANGED_EVENT;
#if (osCMSIS < 0x20000U)
        (void)osMessagePut(phost->os_event, phost->os_msg, 0U);
#else
        (void)osMessageQueuePut(phost->os_event, &phost->os_msg, 0U, 0U);
#endif
#endif
      }
      break;
    default:
      res = USBH_Process(phost);
  }
  /* ... and end here */

  if (phost->gState != prev_state)
    USBH_DbgLog("%s -> %s", st2string(prev_state), st2string(phost->gState));

  return res;
}

static int USB_CAM_ContinueProcess(USBH_HandleTypeDef *phost)
{
  int is_continue_process = 0;

  switch (phost->gState) {
    case HOST_IDLE :
    case HOST_DEV_WAIT_FOR_ATTACHMENT:
    case HOST_DEV_ATTACHED:
    case HOST_DEV_DISCONNECTED:
    case HOST_DETECT_DEVICE_SPEED:
    case HOST_ENUMERATION:
    case HOST_CLASS_REQUEST:
    case HOST_INPUT:
    case HOST_SET_CONFIGURATION:
    case HOST_SET_WAKEUP_FEATURE:
    case HOST_CHECK_CLASS:
    case HOST_SUSPENDED:
      is_continue_process = 1;
      break;
    case HOST_CLASS:
    case HOST_ABORT_STATE:
      is_continue_process = 0;
      break;
    default:
      assert(0);
      is_continue_process = 0;
  }

  return is_continue_process;
}

static int USB_CAM_StateLoop(USBH_HandleTypeDef *phost, USB_CAM_DeviceInfo_t *p_info)
{
  do
  {
    USB_CAM_ProcessWrapper(phost);
  } while (USB_CAM_ContinueProcess(phost));

  p_info->idVendor = phost->device.DevDesc.idVendor;
  p_info->idProduct = phost->device.DevDesc.idProduct;

  return phost->gState == HOST_CLASS;
}

void HAL_HCD_HC_NotifyURBChange_Callback(HCD_HandleTypeDef *hhcd, uint8_t chnum, HCD_URBStateTypeDef urb_state)
{
  USB_CAM_NotifyURBChange_Callback(hhcd, chnum, urb_state);
}

/**
 * @brief Initialize USB camera
 *
 * This will configure and start USB host stack.
 *
 * @param p_conf USB camera configuration parameters
 * @return return USB camera handle in case of success else NULL value is returned
 */
USB_CAM_Hdl_t USB_CAM_Init(USB_CAM_Conf_t *p_conf)
{
  HCD_HandleTypeDef *p_hhcd;
  USB_CAM_Ctx_t *p_ctx;
  int ret;

  p_ctx = calloc(1, sizeof(*p_ctx));
  if (!p_ctx)
    goto calloc_error;

  /* Link the driver to the stack */
  p_hhcd = p_conf->p_hhcd;
  p_hhcd->pData = &p_ctx->hUSBHost;
  p_ctx->hUSBHost.pData = p_hhcd;
  p_ctx->width = p_conf->width;
  p_ctx->height = p_conf->height;
  p_ctx->period = p_conf->period;
  p_ctx->payload_type = p_conf->payload_type;

  ret = USBH_Init(&p_ctx->hUSBHost, USB_CAM_UserProcess, 0);
  if (ret != USBH_OK)
    goto USBH_Init_error;

  ret = USBH_RegisterClass(&p_ctx->hUSBHost, &UVC_Class);
  if (ret != USBH_OK)
    goto USBH_RegisterClass_error;

  ret = USBH_Start(&p_ctx->hUSBHost);
  if (ret != USBH_OK)
    goto USBH_Start_error;

  return p_ctx;

USBH_Start_error:
USBH_RegisterClass_error:
  USBH_DeInit(&p_ctx->hUSBHost);
USBH_Init_error:
  free(p_ctx);
calloc_error:

  return NULL;
}

/**
 * @brief Detect and configure USB device
 *
 * This will detect device and search for a valid configuration. If valid
 * configuration is founded then device is initialized and capture start.
 *
 * @param hdl USB camera handle
 * @param p_info device information returned in case of success
 * @return return 0 in case of success else a negative value is returned
 */
int USB_CAM_SetupDevice(USB_CAM_Hdl_t hdl, USB_CAM_DeviceInfo_t *p_info)
{
  USB_CAM_Ctx_t *p_ctx = hdl;
  int ret;

  ret = USB_CAM_StateLoop(&p_ctx->hUSBHost, p_info) ? 0 : -1;
  if (ret == 0)
  {
    USB_CAM_StartIsoTransaction(&p_ctx->hUSBHost);
  }

  return ret;
}

/**
 * @brief Push capture buffer
 *
 * This will push a capture buffer that will be filled with camera data.
 *
 * @param hdl USB camera handle
 * @param buffer User provide buffer
 * @param len length of buffer in bytes. For USB_CAM_PAYLOAD_UNCOMPRESSED it must be of
 *            size (width * height * 2) bytes.
 * @return return 0 in case of success else a negative value is returned
 */
int USB_CAM_PushBuffer(USB_CAM_Hdl_t hdl, uint8_t *buffer, int len)
{
  USB_CAM_Ctx_t *p_ctx = hdl;
  USB_CAM_Buffer_t *cam_buffer = &p_ctx->buffer[p_ctx->push_idx];

  if (cam_buffer->state != BUF_STATE_UNAVAILABLE)
    return -1;

  cam_buffer->data = buffer;
  cam_buffer->len = len;
  cam_buffer->rx_pos = 0;
  /* FIXME : add WMB */
  cam_buffer->state = BUF_STATE_AVAILABLE;
  p_ctx->push_idx = USB_CAM_UpdateIdx(p_ctx->push_idx);

  return 0;
}

/**
 * @brief Pop capture buffer
 *
 * This will return a buffer for which capture data have been filled
 *
 * @param hdl USB camera handle
 * @param p_info Capture data information
 * @return return 0 in case of success else a negative value is returned
 */
int USB_CAM_PopBuffer(USB_CAM_Hdl_t hdl, USB_CAM_CaptureInfo_t *p_info)
{
  USB_CAM_Ctx_t *p_ctx = hdl;
  USB_CAM_Buffer_t *buffer = &p_ctx->buffer[p_ctx->pop_idx];

  if (buffer->state != BUF_STATE_READY)
    return -1;

  p_info->is_capture_error = buffer->has_error;
  p_info->buffer = buffer->data;
  p_info->len = buffer->rx_pos;
  buffer->state = BUF_STATE_UNAVAILABLE;
  p_ctx->pop_idx = USB_CAM_UpdateIdx(p_ctx->pop_idx);

  return 0;
}
