/**
 ******************************************************************************
 * @file    app_sensor.h
 * @author  MCD Application Team
 * @brief   Library to manage TOF sensor related operation
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

#ifndef INC_APP_SENSOR_H_
#define INC_APP_SENSOR_H_

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Exported types ------------------------------------------------------------*/

/* Exported functions ------------------------------------------------------- */

void Sensor_Init(AppConfig_TypeDef *);
void Sensor_StartRanging(AppConfig_TypeDef *);
void Sensor_GetRangingData(AppConfig_TypeDef *);
void Sensor_StopRanging(AppConfig_TypeDef *);

void HAL_GPIO_EXTI_Callback(uint16_t);

#endif /* INC_APP_SENSOR_H_ */
