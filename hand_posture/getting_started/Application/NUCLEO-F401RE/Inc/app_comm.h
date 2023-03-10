/**
 ******************************************************************************
 * @file    app_comm.h
 * @author  MCD Application Team
 * @brief   Library to manage communication related operation
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

#ifndef INC_APP_COMM_H_
#define INC_APP_COMM_H_

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Exported types ------------------------------------------------------------*/

/* Exported functions ------------------------------------------------------- */

__attribute__((weak)) int __io_putchar(int);
__attribute__((weak)) int __io_getchar(void);

void Comm_Init(AppConfig_TypeDef *);
void Comm_Start(AppConfig_TypeDef *);
void Comm_HandleRxCMD(AppConfig_TypeDef *);
void Comm_Print(AppConfig_TypeDef *);

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *);
void HAL_UART_ErrorCallback(UART_HandleTypeDef *);

#endif /* INC_APP_COMM_H_ */
