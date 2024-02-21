/**
 ******************************************************************************
 * @file    usbd_conf.h
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

#ifndef __USBD_CONF_H
#define __USBD_CONF_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef STM32H7
#include "stm32h7xx.h"
#elif STM32N6
#include "stm32n6xx.h"
#include "stm32n6xx_hal.h"
#else
#error "STM32 family not yet supported"
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define USBD_MAX_NUM_INTERFACES                     1U
#define USBD_MAX_NUM_CONFIGURATION                  1U
#define USBD_MAX_STR_DESC_SIZ                       0x100U
#define USBD_SELF_POWERED                           1U
#define USBD_DEBUG_LEVEL                            0U

#ifdef __cplusplus
}
#endif

#endif /* __USBD_CONF_H */
