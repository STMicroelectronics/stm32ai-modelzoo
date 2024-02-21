/**
 ******************************************************************************
 * @file    usbd_conf.c
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

#include "usbd_core.h"

#include <assert.h>

/* Implement usb ll functions */
USBD_StatusTypeDef USBD_LL_Init(USBD_HandleTypeDef *p_dev)
{
  UNUSED(p_dev);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_DeInit(USBD_HandleTypeDef *p_dev)
{
  UNUSED(p_dev);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_Start(USBD_HandleTypeDef *p_dev)
{
  HAL_PCD_Start(p_dev->pData);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_Stop(USBD_HandleTypeDef *p_dev)
{
  HAL_PCD_Stop(p_dev->pData);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_OpenEP(USBD_HandleTypeDef *p_dev, uint8_t ep_addr, uint8_t ep_type, uint16_t ep_mps)
{
  HAL_PCD_EP_Open(p_dev->pData, ep_addr, ep_mps, ep_type);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_CloseEP(USBD_HandleTypeDef *p_dev, uint8_t ep_addr)
{
  HAL_PCD_EP_Close(p_dev->pData, ep_addr);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_FlushEP(USBD_HandleTypeDef *p_dev, uint8_t ep_addr)
{
  HAL_PCD_EP_Flush(p_dev->pData, ep_addr);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_StallEP(USBD_HandleTypeDef *p_dev, uint8_t ep_addr)
{
  HAL_PCD_EP_SetStall(p_dev->pData, ep_addr);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_ClearStallEP(USBD_HandleTypeDef *p_dev, uint8_t ep_addr)
{
  HAL_PCD_EP_ClrStall(p_dev->pData, ep_addr);

  return USBD_OK;
}

uint8_t USBD_LL_IsStallEP(USBD_HandleTypeDef *p_dev, uint8_t ep_addr)
{
  PCD_HandleTypeDef *hpcd = p_dev->pData;

  if ((ep_addr & 0x80U) == 0x80U)
  {
    return hpcd->IN_ep[ep_addr & 0x7FU].is_stall;
  }
  else
  {
    return hpcd->OUT_ep[ep_addr & 0x7FU].is_stall;
  }

  return 0U;
}

USBD_StatusTypeDef USBD_LL_SetUSBAddress(USBD_HandleTypeDef *p_dev, uint8_t dev_addr)
{
  HAL_PCD_SetAddress(p_dev->pData, dev_addr);;

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_Transmit(USBD_HandleTypeDef *p_dev, uint8_t ep_addr, uint8_t *p_buf, uint32_t size)
{
  /* Get the packet total length */
  p_dev->ep_in[ep_addr & 0x7FU].total_length = size;

  (void)HAL_PCD_EP_Transmit(p_dev->pData, ep_addr, p_buf, size);

  return USBD_OK;
}

USBD_StatusTypeDef USBD_LL_PrepareReceive(USBD_HandleTypeDef *p_dev, uint8_t ep_addr, uint8_t *p_buf, uint32_t size)
{
  HAL_PCD_EP_Receive(p_dev->pData, ep_addr, p_buf, size);

  return USBD_OK;
}

uint32_t USBD_LL_GetRxDataSize(USBD_HandleTypeDef *p_dev, uint8_t ep_addr)
{
  return HAL_PCD_EP_GetRxCount(p_dev->pData, ep_addr);
}

void *USBD_static_malloc(uint32_t size)
{
  UNUSED(size);

  assert(0 && "implement static allocation for state");

  return NULL;
}

void USBD_static_free(void *p)
{
  UNUSED(p);
}

void USBD_LL_Delay(uint32_t Delay)
{
  HAL_Delay(Delay);
}



/* Implement LL Driver Callbacks (PCD -> USB Device Library) */
void HAL_PCD_SetupStageCallback(PCD_HandleTypeDef *p_hpcd)
{
  USBD_LL_SetupStage(p_hpcd->pData, (uint8_t *) p_hpcd->Setup);
}


void HAL_PCD_DataOutStageCallback(PCD_HandleTypeDef *p_hpcd, uint8_t epnum)
{
  USBD_LL_DataOutStage(p_hpcd->pData, epnum, p_hpcd->OUT_ep[epnum].xfer_buff);
}


void HAL_PCD_DataInStageCallback(PCD_HandleTypeDef *p_hpcd, uint8_t epnum)
{
  USBD_LL_DataInStage(p_hpcd->pData, epnum, p_hpcd->IN_ep[epnum].xfer_buff);
}

void HAL_PCD_SOFCallback(PCD_HandleTypeDef *p_hpcd)
{
  USBD_LL_SOF(p_hpcd->pData);
}

void HAL_PCD_ResetCallback(PCD_HandleTypeDef *p_hpcd)
{
  USBD_SpeedTypeDef speed;

  /* Set USB Current Speed */
  switch (p_hpcd->Init.speed)
  {
    case PCD_SPEED_HIGH:
      speed = USBD_SPEED_HIGH;
      break;
    case PCD_SPEED_FULL:
      speed = USBD_SPEED_FULL;
      break;
    default:
      speed = USBD_SPEED_FULL;
      break;
  }

  /* Reset Device */
  USBD_LL_Reset(p_hpcd->pData);

  USBD_LL_SetSpeed(p_hpcd->pData, speed);
}

void HAL_PCD_SuspendCallback(PCD_HandleTypeDef *p_hpcd)
{
  USBD_LL_Suspend(p_hpcd->pData);
}

void HAL_PCD_ResumeCallback(PCD_HandleTypeDef *p_hpcd)
{
  USBD_LL_Resume(p_hpcd->pData);
}

void HAL_PCD_ISOOUTIncompleteCallback(PCD_HandleTypeDef *p_hpcd, uint8_t epnum)
{
  USBD_LL_IsoOUTIncomplete(p_hpcd->pData, epnum);
}

void HAL_PCD_ISOINIncompleteCallback(PCD_HandleTypeDef *p_hpcd, uint8_t epnum)
{
  USBD_LL_IsoINIncomplete(p_hpcd->pData, epnum);
}

void HAL_PCD_ConnectCallback(PCD_HandleTypeDef *p_hpcd)
{
  USBD_LL_DevConnected(p_hpcd->pData);
}

void HAL_PCD_DisconnectCallback(PCD_HandleTypeDef *p_hpcd)
{
  USBD_LL_DevDisconnected(p_hpcd->pData);
}

