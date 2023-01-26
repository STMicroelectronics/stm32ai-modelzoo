/**
 ******************************************************************************
 * @file    apperror.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
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
#ifndef APPERROR_H_
#define APPERROR_H_

#ifdef __cplusplus
extern "C" {
#endif

// Low Level API error code
// ************************

#define SYS_BASE_LL_ERROR_CODE                                APP_BASE_ERROR_CODE
#define SYS_LL_UNDEFINED_ERROR_CODE                           SYS_BASE_LL_ERROR_CODE + 1

// SPI Master error code
#define SYS_BASE_SPI_M_ERROR_CODE                             SYS_BASE_LL_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_SPI_M_WRITE_READ_ERROR_CODE                       SYS_BASE_SPI_M_ERROR_CODE + 1
#define SYS_SPI_M_WRITE_ERROR_CODE                            SYS_BASE_SPI_M_ERROR_CODE + 2

// I2C Master error code
#define SYS_BASE_I2C_M_ERROR_CODE                             SYS_BASE_SPI_M_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_I2C_M_READ_ERROR_CODE                             SYS_BASE_I2C_M_ERROR_CODE + 1
#define SYS_I2C_M_WRITE_ERROR_CODE                            SYS_BASE_I2C_M_ERROR_CODE + 2


// Service Level error code
// ************************

// CircularBuffer error code
#define SYS_CB_BASE_ERROR_CODE                                SYS_BASE_I2C_M_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_CB_INVALID_ITEM_ERROR_CODE                        SYS_CB_BASE_ERROR_CODE + 1
#define SYS_CB_FULL_ERROR_CODE                                SYS_CB_BASE_ERROR_CODE + 2
#define SYS_CB_NO_READY_ITEM_ERROR_CODE                       SYS_CB_BASE_ERROR_CODE + 3

// BCProtocol error code
#define SYS_BCP_BASE_ERROR_CODE                               SYS_CB_BASE_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_BCP_CMD_NOT_SUPPORTED_ERROR_CODE                  SYS_BCP_BASE_ERROR_CODE + 1
#define SYS_BCP_CMD_EXECUTION_ERROR_CODE                      SYS_BCP_BASE_ERROR_CODE + 2

// FLASH Storage Service error code
#define SYS_BASE_FSS_ERROR_CODE                               SYS_BCP_BASE_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_FSS_FLASH_ERROR_CODE                              SYS_BCP_BASE_ERROR_CODE + 1

// Task Level error code
// *********************

// Generic task error code
#define SYS_BASE_APP_TASK_ERROR_CODE                          SYS_BASE_FSS_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_APP_TASK_UNKNOWN_REPORT_ERROR_CODE                SYS_BASE_APP_TASK_ERROR_CODE +1
#define SYS_APP_TASK_REPORT_LOST_ERROR_CODE                   SYS_BASE_APP_TASK_ERROR_CODE + 2

// SPI Bus task error code
#define SYS_BASE_SPIBUS_TASK_ERROR_CODE                       SYS_BASE_APP_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_SPIBUS_TASK_IO_ERROR_CODE                         SYS_BASE_SPIBUS_TASK_ERROR_CODE + 1
#define SYS_SPIBUS_TASK_RESUME_ERROR_CODE                     SYS_BASE_SPIBUS_TASK_ERROR_CODE + 2
#define SYS_SPIBUS_TASK_UNSUPPORTED_CMD_ERROR__CODE           SYS_BASE_SPIBUS_TASK_ERROR_CODE + 3

// I2C Bus task error code
#define SYS_BASE_I2CBUS_TASK_ERROR_CODE                       SYS_BASE_SPIBUS_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_I2CBUS_TASK_IO_ERROR_CODE                         SYS_BASE_I2CBUS_TASK_ERROR_CODE + 1
#define SYS_I2CBUS_TASK_RESUME_ERROR_CODE                     SYS_BASE_I2CBUS_TASK_ERROR_CODE + 2
#define SYS_I2CBUS_TASK_UNSUPPORTED_CMD_ERROR_CODE            SYS_BASE_I2CBUS_TASK_ERROR_CODE + 3

// AI task error code
#define SYS_BASE_AI_TASK_ERROR_CODE                           SYS_BASE_I2CBUS_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_AI_TASK_INIT_ERROR_CODE                           SYS_BASE_AI_TASK_ERROR_CODE + 1
#define SYS_AI_TASK_INVALID_CMD_ERROR_CODE                    SYS_BASE_AI_TASK_ERROR_CODE + 2
#define SYS_AI_TASK_CMD_ERROR_CODE                            SYS_BASE_AI_TASK_ERROR_CODE + 3
#define SYS_AI_TASK_IN_QUEUE_FULL_ERROR_CODE                  SYS_BASE_AI_TASK_ERROR_CODE + 4

// AppController error code
#define SYS_BASE_CTRL_TASK_ERROR_CODE                         SYS_BASE_AI_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_CTRL_IN_BUFF_FULL_ERROR_CODE                      SYS_BASE_CTRL_TASK_ERROR_CODE + 1
#define SYS_CTRL_IN_QUEUE_FULL_ERROR_CODE                     SYS_BASE_CTRL_TASK_ERROR_CODE + 2
#define SYS_CTRL_INVALID_PARAM_ERROR_CODE                     SYS_BASE_CTRL_TASK_ERROR_CODE + 3
#define SYS_CTRL_TIMER_ERROR_CODE                             SYS_BASE_CTRL_TASK_ERROR_CODE + 4
#define SYS_CTRL_WRONG_CONF_ERROR_CODE                        SYS_BASE_CTRL_TASK_ERROR_CODE + 5

// Sensor task generic error code
#define SYS_SENSOR_TASK_BASE_ERROR_CODE                       SYS_BASE_CTRL_TASK_ERROR_CODE + SYS_GROUP_ERROR_COUNT
#define SYS_SENSOR_TASK_OP_ERROR_CODE                         SYS_SENSOR_TASK_BASE_ERROR_CODE + 1

#ifdef __cplusplus
}
#endif

#endif /* APPERROR_H_ */
