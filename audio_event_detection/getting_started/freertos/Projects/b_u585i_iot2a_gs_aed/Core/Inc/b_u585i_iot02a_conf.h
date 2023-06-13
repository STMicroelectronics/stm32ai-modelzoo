/**
 ******************************************************************************
 * @file    b_u585i_iot02a_conf.h
 * @author  MCD Application Team
 * @brief   configuration file.
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software component is licensed by ST under BSD 3-Clause license,
 * the "License"; You may not use this file except in compliance with the
 * License. You may obtain a copy of the License at:
 *                        opensource.org/licenses/BSD-3-Clause
 *
 ******************************************************************************
 */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef B_U585I_IOT02A_CONF_H
#define B_U585I_IOT02A_CONF_H

/* *INDENT-OFF* */
#ifdef __cplusplus
extern "C"
{
#endif
/* *INDENT-ON* */

/* Includes ------------------------------------------------------------------*/
#include "stm32u5xx_hal.h"

/* COM define */
#define USE_BSP_COM_FEATURE                 0U
#define USE_COM_LOG                         0U

/* Default EEPROM max trials */
#define EEPROM_MAX_TRIALS                   3000U

/* IRQ priorities */
#define BSP_BUTTON_USER_IT_PRIORITY         15U /* Default is lowest priority level */

/* Audio interrupt priority */
#define BSP_AUDIO_IN_IT_PRIORITY            15U /* Default is lowest priority level */

/* CAMERA interrupt priority */
#define BSP_CAMERA_IT_PRIORITY              14U /* Default is lowest priority level */

/* I2C1 and I2C2 Frequencies in Hz  */
#define BUS_I2C1_FREQUENCY                  400000UL  /* Frequency of I2C1 = 400 KHz*/
#define BUS_I2C2_FREQUENCY                  400000UL  /* Frequency of I2C2 = 400 KHz*/

/* Default AUDIO IN internal buffer size in 32-bit words per micro */
#define BSP_AUDIO_IN_DEFAULT_BUFFER_SIZE    8192UL /* 2048*4 = 8Kbytes */

/* Usage of USBPD PWR TRACE system */
#define USE_BSP_USBPD_PWR_TRACE             0U /* USBPD BSP trace system is disabled */

#define BSP_USE_CMSIS_OS                    1

/* *INDENT-OFF* */
#ifdef __cplusplus
}
#endif
/* *INDENT-ON* */

#endif /* B_U585I_IOT02A_CONF_H */
