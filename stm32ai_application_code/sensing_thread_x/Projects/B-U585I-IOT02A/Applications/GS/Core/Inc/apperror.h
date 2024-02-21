/**
 ******************************************************************************
 * @file    apperror.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 1.0.0
 * @date    Nov 14, 2017
 *
 * @brief Application specific error code
 *
 * Application defines its own error code in this file starting form the
 * constant APP_BASE_ERROR_CODE.
 * It is recommended to group the error code in the following groups:
 * - Low Level API error code
 * - Service Level error code
 * - Task Level error code
 *
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; COPYRIGHT 2017 STMicroelectronics</center></h2>
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
#ifndef APPERROR_H_
#define APPERROR_H_

#ifdef __cplusplus
extern "C" {
#endif

// Low Level API error code
// ************************

#define SYS_BASE_LL_ERROR_CODE                                APP_BASE_ERROR_CODE
#define SYS_LL_UNDEFINED_ERROR_CODE                           SYS_BASE_LL_ERROR_CODE + 1

// IP error
//#define SYS_BASE_XX_ERROR_CODE                               APP_BASE_ERROR_CODE

// DFSDM driver error code
#define SYS_BASE_DFSDM_DRV_ERROR_CODE                         SYS_BASE_LL_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_DFSDM_DRV_GENERIC_ERROR_CODE                      APP_BASE_ERROR_CODE + 1

// SPI Master error code
#define SYS_BASE_SPI_M_ERROR_CODE                              SYS_DFSDM_DRV_GENERIC_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_SPI_M_WRITE_READ_ERROR_CODE                        SYS_BASE_SPI_M_ERROR_CODE + 1
#define SYS_SPI_M_WRITE_ERROR_CODE                             SYS_BASE_SPI_M_ERROR_CODE + 2

// I2C Master error code
#define SYS_BASE_I2C_M_ERROR_CODE                              SYS_BASE_SPI_M_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_I2C_M_READ_ERROR_CODE                              SYS_BASE_I2C_M_ERROR_CODE + 1
#define SYS_I2C_M_WRITE_ERROR_CODE                             SYS_BASE_I2C_M_ERROR_CODE + 2

// Service Level error code
// ************************

// CircularBuffer error code
#define SYS_CB_BASE_ERROR_CODE                                SYS_BASE_IEVTSRC_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_CB_INVALID_ITEM_ERROR_CODE                        SYS_CB_BASE_ERROR_CODE + 1
#define SYS_CB_FULL_ERROR_CODE                                SYS_CB_BASE_ERROR_CODE + 2
#define SYS_CB_NO_READY_ITEM_ERROR_CODE                       SYS_CB_BASE_ERROR_CODE + 3

// Task Level error code
// *********************

// Generic task error code
#define SYS_BASE_APP_TASK_ERROR_CODE                           SYS_CB_BASE_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_APP_TASK_UNKNOWN_MSG_ERROR_CODE                    SYS_BASE_APP_TASK_ERROR_CODE +1
#define SYS_APP_TASK_MSG_LOST_ERROR_CODE                       SYS_BASE_APP_TASK_ERROR_CODE + 2

// SPI Bus task error code
#define SYS_BASE_SPIBUS_TASK_ERROR_CODE                        SYS_BASE_APP_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_SPIBUS_TASK_IO_ERROR_CODE                          SYS_BASE_SPIBUS_TASK_ERROR_CODE + 1
#define SYS_SPIBUS_TASK_RESUME_ERROR_CODE                      SYS_BASE_SPIBUS_TASK_ERROR_CODE + 2
#define SYS_SPIBUS_TASK_UNSUPPORTED_CMD_ERROR__CODE            SYS_BASE_SPIBUS_TASK_ERROR_CODE + 3

// I2C Bus task error code
#define SYS_BASE_I2CBUS_TASK_ERROR_CODE                        SYS_BASE_SPIBUS_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_I2CBUS_TASK_IO_ERROR_CODE                          SYS_BASE_I2CBUS_TASK_ERROR_CODE + 1
#define SYS_I2CBUS_TASK_RESUME_ERROR_CODE                      SYS_BASE_I2CBUS_TASK_ERROR_CODE + 2

// AI task error code
#define SYS_AI_TASK_BASE_ERROR_CODE                           SYS_BASE_I2CBUS_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_AI_TASK_INIT_ERROR_CODE                           SYS_AI_TASK_BASE_ERROR_CODE + 1
#define SYS_AI_TASK_INVALID_CMD_ERROR_CODE                    SYS_AI_TASK_BASE_ERROR_CODE + 2
#define SYS_AI_TASK_CMD_ERROR_CODE                            SYS_AI_TASK_BASE_ERROR_CODE + 3
#define SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE                  SYS_AI_TASK_BASE_ERROR_CODE + 4

// PRE PROC task error code
#define SYS_PREPROC_TASK_BASE_ERROR_CODE                       SYS_AI_TASK_BASE_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_PREPROC_TASK_IN_QUEUE_FULL_ERROR_CODE              SYS_PREPROC_TASK_BASE_ERROR_CODE + 1
#define SYS_PREPROC_TASK_SENSOR_NON_ACTIVE_ERROR_CODE          SYS_PREPROC_TASK_BASE_ERROR_CODE + 2

#ifdef __cplusplus
}
#endif

#endif /* APPERROR_H_ */
