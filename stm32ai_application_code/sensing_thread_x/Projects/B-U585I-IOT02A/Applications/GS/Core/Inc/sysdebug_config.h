/**
 ******************************************************************************
 * @file    sysdebug_config.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 1.2.0
 * @date    Oct 10, 2016
 * @brief   Configure the debug log functionality
 *
 * Each logic module of the application should define a DEBUG control byte
 * used to turn on/off the log for the module.
 *
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; COPYRIGHT 2016 STMicroelectronics</center></h2>
 *
 * Licensed under MCD-ST Liberty SW License Agreement V2, (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at:
 *
 *        http://www.st.com/software_license_agreement_liberty_v2
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ******************************************************************************
 */

#ifndef SYSDEBUG_CONFIG_H_
#define SYSDEBUG_CONFIG_H_

#ifdef __cplusplus
extern "C" {
#endif
#ifdef DEBUG
#define SYS_DBG_LEVEL          SYS_DBG_LEVEL_VERBOSE /*!< set the level of the system log: all log messages with minor level are discharged. */
#else
#define SYS_DBG_LEVEL          SYS_DBG_LEVEL_DEFAULT /*!< set the level of the system log */
#endif
#define SYS_DBG_INIT           SYS_DBG_ON               ///< Init task debug control byte
#define SYS_DBG_DRIVERS        SYS_DBG_OFF              ///< Drivers debug control byte
#define SYS_DBG_APP            SYS_DBG_ON               ///< Generic Application debug control byte
#define SYS_DBG_SYSTS          SYS_DBG_ON               ///< System timestamp debug control byte
#define SYS_DBG_APMH           SYS_DBG_ON               ///< Application Power Mode Helper debug control byte
#define SYS_DBG_HW             SYS_DBG_ON               ///< Hello World task debug control byte
#define SYS_DBG_SPIBUS         SYS_DBG_ON               ///< SPIBus task debug control byte
#define SYS_DBG_I2CBUS         SYS_DBG_ON               ///< I2CBus task debug control byte
#define SYS_DBG_ISM330DHCX     SYS_DBG_ON               ///< ISM330DHCX sensor task debug control byte
#define SYS_DBG_IMP34DT05      SYS_DBG_ON               ///< IMP34DT05 task debug control byte
#define SYS_DBG_CTRL           SYS_DBG_ON               ///< CTRL task debug control byte
#define SYS_DBG_DPU            SYS_DBG_ON               ///< DPU tasks debug control byte
#define SYS_DBG_DPT1           SYS_DBG_ON               ///< DPT1 tasks debug control byte
#define SYS_DBG_AI             SYS_DBG_ON               ///< AI tasks debug control byte
#define SYS_DBG_PRE_PROC       SYS_DBG_ON               ///< PRE_PROC task

/* ODeV - hardware configuration for the debug services provided by the framework */
/**********************************************************************************/

#include "mx.h"

/* ODeV DBG UART used for the system log */
extern UART_HandleTypeDef huart1;
void MX_USART1_UART_Init(void);

#define SYS_DBG_UART             huart1
#define SYS_DBG_UART_INIT        MX_USART1_UART_Init
#define SYS_DBG_UART_TIMEOUT_MS  5000

#endif /* SYS_DEBUG */

#ifdef __cplusplus
}
#endif

