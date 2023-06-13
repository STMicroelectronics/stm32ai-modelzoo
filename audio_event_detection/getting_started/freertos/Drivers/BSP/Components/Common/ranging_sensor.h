/**
  ******************************************************************************
  * @file    ranging_sensor.h
  * @author  IMG SW Application Team
  * @brief   This header file contains the common defines and functions prototypes
  *          for the ranging sensor driver.
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
#ifndef RANGING_SENSOR_H
#define RANGING_SENSOR_H

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

/** @addtogroup RANGING_SENSOR
  * @{
  */

/** @defgroup RANGING_SENSOR_Driver_structure  Ranging sensor Driver structure
  * @{
  */
typedef struct
{
  int32_t (*Init)(void *);
  int32_t (*DeInit)(void *);
  int32_t (*ReadID)(void *, uint32_t *);
  int32_t (*GetCapabilities)(void *, void *);
  int32_t (*ConfigProfile)(void *, void *);
  int32_t (*ConfigROI)(void *, void *);
  int32_t (*ConfigIT)(void *, void *);
  int32_t (*GetDistance)(void *, void *);
  int32_t (*Start)(void *, uint32_t);
  int32_t (*Stop)(void *);
  int32_t (*SetAddress)(void *, uint32_t);
  int32_t (*GetAddress)(void *, uint32_t *);
  int32_t (*SetPowerMode)(void *, uint32_t);
  int32_t (*GetPowerMode)(void *, uint32_t *);
} RANGING_SENSOR_Drv_t;
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

#endif /* RANGING_SENSOR_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
