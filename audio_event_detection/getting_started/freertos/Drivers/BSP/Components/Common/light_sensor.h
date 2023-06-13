/**
  ******************************************************************************
  * @file    light_sensor.h
  * @author  IMG SW Application Team
  * @brief   This header file contains the common defines and functions prototypes
  *          for the light sensor driver.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef LIGHT_SENSOR_H
#define LIGHT_SENSOR_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include <stdint.h>

/** @addtogroup BSP
  * @{
  */

/** @addtogroup Components
  * @{
  */

/** @addtogroup LIGHT_SENSOR
  * @{
  */

/** @defgroup LIGHT_SENSOR_Driver_structure  Ranging sensor Driver structure
  * @{
  */
typedef struct
{
  int32_t (*Init)(void *);
  int32_t (*DeInit)(void *);
  int32_t (*ReadID)(void *, uint32_t *);
  int32_t (*GetCapabilities)(void *, void *);
  int32_t (*SetExposureTime)(void *, uint32_t);
  int32_t (*GetExposureTime)(void *, uint32_t *);
  int32_t (*SetGain)(void *, uint8_t, uint32_t);
  int32_t (*GetGain)(void *, uint8_t, uint32_t *);
  int32_t (*SetInterMeasurementTime)(void *, uint32_t);
  int32_t (*GetInterMeasurementTime)(void *, uint32_t *);
  int32_t (*Start)(void *, uint32_t);
  int32_t (*Stop)(void *);
  int32_t (*StartFlicker)(void *, uint8_t, uint8_t);
  int32_t (*StopFlicker)(void *);
  int32_t (*GetValues)(void *, uint32_t *);
  int32_t (*SetControlMode)(void *, uint32_t, uint32_t);
} LIGHT_SENSOR_Drv_t;
/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */

/**
  * @}
  */

#ifdef __cplusplus
}
#endif

#endif /* LIGHT_SENSOR_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
