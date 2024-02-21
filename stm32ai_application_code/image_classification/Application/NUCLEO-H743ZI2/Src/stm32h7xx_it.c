/**
 ******************************************************************************
 * @file    stm32h7xx_it.c
 * @author  MDG Application Team
 * @brief   Main Interrupt Service Routines for Cortex-M7.
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

/* Includes ------------------------------------------------------------------*/
#include "stm32h7xx_it.h"
#include "nucleo_h743zi2_camera_dcmi.h"
#include "nucleo_h743zi2_lcd.h"

/* External variables --------------------------------------------------------*/
#if DISPLAY_INTERFACE == DISPLAY_INTERFACE_USB
extern PCD_HandleTypeDef hpcd_USB_OTG_FS;
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
extern HCD_HandleTypeDef hhcd_USB_OTG_FS;
#endif

/* Functions Definition ------------------------------------------------------*/

/******************************************************************************/
/*            Cortex-M7 Processor Exceptions Handlers                         */
/******************************************************************************/

/**
  * @brief   This function handles NMI exception.
  * @param  None
  * @retval None
  */
void NMI_Handler(void)
{
}

/**
  * @brief  This function handles Hard Fault exception.
  * @param  None
  * @retval None
  */
void HardFault_Handler(void)
{
  /* Go to infinite loop when Hard Fault exception occurs */
  while (1)
  {
  }
}

/**
  * @brief  This function handles Memory Manage exception.
  * @param  None
  * @retval None
  */
void MemManage_Handler(void)
{
  /* Go to infinite loop when Memory Manage exception occurs */
  while (1)
  {
  }
}

/**
  * @brief  This function handles Bus Fault exception.
  * @param  None
  * @retval None
  */
void BusFault_Handler(void)
{
  /* Go to infinite loop when Bus Fault exception occurs */
  while (1)
  {
  }
}

/**
  * @brief  This function handles Usage Fault exception.
  * @param  None
  * @retval None
  */
void UsageFault_Handler(void)
{
  /* Go to infinite loop when Usage Fault exception occurs */
  while (1)
  {
  }
}

/**
  * @brief  This function handles SVCall exception.
  * @param  None
  * @retval None
  */
void SVC_Handler(void)
{
}

/**
  * @brief  This function handles Debug Monitor exception.
  * @param  None
  * @retval None
  */
void DebugMon_Handler(void)
{
}

/**
  * @brief  This function handles PendSVC exception.
  * @param  None
  * @retval None
  */
void PendSV_Handler(void)
{
}

/**
  * @brief  This function handles SysTick Handler.
  * @param  None
  * @retval None
  */
void SysTick_Handler(void)
{
  HAL_IncTick();
}

/******************************************************************************/
/*                stm32H7xx  Peripherals Interrupt Handlers                   */
/*  Add here the Interrupt Handler for the used peripheral(s) (PPP), for the  */
/*  available peripheral interrupt handler's name please refer to the startup */
/*  file (startup_stm32h7xx.s).                                               */
/******************************************************************************/

/**
  * @brief This function handles USB On The Go FS global interrupt.
  */
void OTG_FS_IRQHandler(void)
{
#if DISPLAY_INTERFACE == DISPLAY_INTERFACE_USB
  HAL_PCD_IRQHandler(&hpcd_USB_OTG_FS);
#elif CAMERA_INTERFACE == CAMERA_INTERFACE_USB
  HAL_HCD_IRQHandler(&hhcd_USB_OTG_FS);
#endif
  ;
}

/**
  * @brief This function handles EXTI line[9:5] interrupts.
  */
void EXTI9_5_IRQHandler(void)
{
  HAL_GPIO_EXTI_IRQHandler(USB_OTG_FS_OVCR_Pin);
}

/**
  * @brief  DMA interrupt handler.
  * @param  None
  * @retval None
  */
void DMA2_Stream3_IRQHandler(void)
{
  BSP_CAMERA_DCMI_DMA_IRQHandler();
}

/**
  * @brief  DCMI interrupt handler.
  * @param  None
  * @retval None
  */
void DCMI_IRQHandler(void)
{
   BSP_CAMERA_DCMI_IRQHandler();
}

/**
  * @brief  MDMA interrupt handler.
  * @param  None
  * @retval None
  */
void MDMA_IRQHandler(void)
{
  HAL_MDMA_IRQHandler(&hmdma);
}

/**
  * @brief  This function handles DMA2D Handler.
  * @param  None
  * @retval None
  */
void DMA2D_IRQHandler(void)
{
  HAL_DMA2D_IRQHandler(&hlcd_dma2d);
}
