/**
 ******************************************************************************
 * @file    sysdebug_config.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 * @brief   Configure the debug log functionality
 *
 * Each logic module of the application should define a DEBUG control byte
 * used to turn on/off the log for the module.
 *
 *********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *********************************************************************************
 */

#ifndef SYSDEBUG_CONFIG_H_
#define SYSDEBUG_CONFIG_H_

#ifdef __cplusplus
extern "C" {
#endif

#define SYS_DBG_LEVEL                      SYS_DBG_LEVEL_SEVERE /*!< set the level of the system log: all log messages with minor level are discharged. */

/* Example */
/* #define SYS_DBG_MODULE1     SYS_DBG_ON|GTS_DBG_HALT   */
/* #define SYS_DBG_MODULE2     SYS_DBG_ON                */


#define SYS_DBG_INIT                       SYS_DBG_ON      ///< Init task debug control byte
#define SYS_DBG_DRIVERS                    SYS_DBG_OFF     ///< Drivers debug control byte
#define SYS_DBG_APP                        SYS_DBG_OFF     ///< Generic Application debug control byte
#define SYS_DBG_APMH                       SYS_DBG_ON      ///< Application Power Mode Helper debug control byte
#define SYS_DBG_HW                         SYS_DBG_OFF     ///< Hello World task debug control byte
#define SYS_DBG_SPIBUS                     SYS_DBG_ON      ///< SPIBus task debug control byte
#define SYS_DBG_I2CBUS                     SYS_DBG_OFF     ///< I2CBus task debug control byte
#define SYS_DBG_ISM330DHCX                 SYS_DBG_ON      ///< ISM330DHCX sensor task debug control byte
#define SYS_DBG_IIS3DWB                    SYS_DBG_ON      ///< IIS3DWB sensor task debug control byte
#define SYS_DBG_HTS221                     SYS_DBG_OFF     ///< HTS221 sensor task debug control byte
#define SYS_DBG_LPS22HH                    SYS_DBG_OFF     ///< LPS22HH sensor task debug control byte
#define SYS_DBG_ENV                        SYS_DBG_OFF     ///< ENV sensor task debug control byte
#define SYS_DBG_IMP23ABSU                  SYS_DBG_ON      ///< IMP23ABSU sensor task debug control byte
#define SYS_DBG_UTIL                       SYS_DBG_OFF     ///< Utility task debug control byte
#define SYS_DBG_NAI                        SYS_DBG_ON      ///< NanoEdge AI task debug control byte
#define SYS_DBG_AI                         SYS_DBG_ON      ///< CubeAI plus ML extension task debug control byte
#define SYS_DBG_AI_USC                     SYS_DBG_ON      ///< CubeAI plus ML extension task debug control byte
#define SYS_DBG_MFCC                       SYS_DBG_ON      ///< Mfcc task debug control byte
#define SYS_DBG_CTRL                       SYS_DBG_ON      ///< Application Controller (console) task debug control byte
#define SYS_DBG_BCP                        SYS_DBG_ON      ///< Battery Charger Protocol debug control byte
#define SYS_DBG_DATA_INJECTOR              SYS_DBG_ON      ///< Data Injector task debug control byte
#define SYS_DBG_DATA_FSS                   SYS_DBG_ON      ///< FLASH Storage service debug control byte


/* eLooM - hardware configuration for the debug services provided by the framework */
/**********************************************************************************/

#include "mx.h"

/* eLooM test point PINs */
#define SYS_DBG_TP1_PORT                   SYS_DBG_TP1_GPIO_Port
#define SYS_DBG_TP1_PIN                    SYS_DBG_TP1_Pin
#define SYS_DBG_TP1_CLK_ENABLE             __HAL_RCC_GPIOG_CLK_ENABLE
#define SYS_DBG_TP2_PORT                   SYS_DBG_TP2_GPIO_Port
#define SYS_DBG_TP2_PIN                    SYS_DBG_TP2_Pin
#define SYS_DBG_TP2_CLK_ENABLE             __HAL_RCC_GPIOG_CLK_ENABLE

/* eLooM DBG UART used for the system log */
extern UART_HandleTypeDef huart2;
void MX_USART2_UART_Init(void);

#define SYS_DBG_UART                       huart2
#define SYS_DBG_UART_INIT                  MX_USART2_UART_Init
#define SYS_DBG_UART_TIMEOUT_MS            5000

/* eLooM runtime statistic timer configuration for FreeRTOS */
extern TIM_HandleTypeDef htim6;
void MX_TIM6_Init(void);

#define SYS_DBG_TIM                        htim6
#define SYS_DBG_TIM_INIT                   MX_TIM6_Init
#define SYS_DBG_TIM_IRQ_N                  TIM6_DAC_IRQn
#define SYS_DBG_TIM_IRQ_HANDLER            TIM6_DACUNDER_IRQHandler
#endif /* SYS_DEBUG */


#ifdef __cplusplus
}
#endif

