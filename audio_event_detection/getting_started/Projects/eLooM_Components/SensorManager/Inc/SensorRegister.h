/**
  ******************************************************************************
  * @file    SensorRegister.h
  * @author  SRA - MCD
  * @brief
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  *
  ******************************************************************************
  */
#ifndef SENSORREGISTER_H_
#define SENSORREGISTER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "ISensor.h"
#include "ISensor_vtbl.h"

#define SM_INVALID_SENSOR_ID (0xFF) /**< Specifies the invalid sensor ID.  */

/* Public API declaration */
/**************************/

/**
  * Register a sensor with the SensorManager. During the registration the SensorManager assigns an ID to the sensor.
  * This ID is unique during the application lifecycle, and it can be used with the other public API of the
  * SensorManager to operate the sensor.
  *
  * @param pSensor [IN] specifies a sensor interface to be registered with the SensorManager.
  * @return the sensor ID if success, SM_INVALID_SENSOR_ID otherwise.
  */
uint8_t SMAddSensor(ISensor_t *pSensor);

/**
  * Remove a sensor from the SensorManager.
  * @param id [IN] specifies the Sensor ID to be removed.
  * @return the sensor ID if success, SM_INVALID_SENSOR_ID otherwise.
  */
sys_error_code_t SMRemoveSensor(ISensor_t *pSensor);


/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* SENSORREGISTER_H_ */
