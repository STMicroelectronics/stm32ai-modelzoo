 /**
 ******************************************************************************
 * @file    nucleo_h743zi2.h
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

#ifndef __NUCLEO_H743ZI2_H
#define __NUCLEO_H743ZI2_H

/* Includes ------------------------------------------------------------------*/
#include "nucleo_h743zi2_errno.h"
#include "stm32h7xx_hal.h"
#include "main.h"

/* Exported types ------------------------------------------------------------*/
typedef enum
{
  LED1 = 0U,
  LED_GREEN = LED1,
  LED2 = 1U,
  LED_YELLOW = LED2,
  LED3 = 2U,
  LED_RED = LED3,
  LEDn
} Led_TypeDef;

/* Public functions ----------------------------------------------------------*/
int32_t  BSP_LED_Init(Led_TypeDef Led);
int32_t  BSP_LED_DeInit(Led_TypeDef Led);
int32_t  BSP_LED_On(Led_TypeDef Led);
int32_t  BSP_LED_Off(Led_TypeDef Led);
int32_t  BSP_LED_Toggle(Led_TypeDef Led);

#endif /* __NUCLEO_H743ZI2_H */
