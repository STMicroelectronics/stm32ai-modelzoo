/**
  ******************************************************************************
  * @file    SQuery.h
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
#ifndef SENSORMANAGER_INC_SERVICES_SQUERY_H_
#define SENSORMANAGER_INC_SERVICES_SQUERY_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/SIterator.h"


/**
  * Create a type name for ::_SQuery_t
  */
typedef struct _SQuery_t SQuery_t;

/**
  * Sensor Query internal state.
  */
struct _SQuery_t
{
  /**
    * Specifies the iterator used to to iterate through a sensors.
    */
  SIterator_t iterator;
};

/**
  *  Initialize the query based on a sensor manager instance.
  *
  * @param _this [IN] specifies an ::SIterator_t object.
  * @param p_sm [IN] specifies a ::SensorManager_t instance.
  * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
  */
sys_error_code_t SQInit(SQuery_t *_this, SensorManager_t *p_sm);

/**
   * Return the sensor id of the next sensor in the iteration that match the given name.
   *
   * @param _this [IN] specifies an ::SIterator_t object.
   * @param sensor_name [IN] specify the name parameter for the query.
   * @return the sensor id of the next sensor in the iteration matching the query or SI_NULL_SENSOR_ID
   */
uint16_t SQNextByName(SQuery_t *_this, const char *sensor_name);

/**
   * Return the sensor id of the next sensor in the iteration that match the given type.
   *
   * @param _this [IN] specifies an ::SIterator_t object.
   * @param sensor_type [IN] specify the type parameter for the query. Valid values are:
   *        - COM_TYPE_ACC
   *        - COM_TYPE_MAG
   *        - COM_TYPE_GYRO
   *        - COM_TYPE_TEMP
   *        - COM_TYPE_PRESS
   *        - COM_TYPE_HUM
   *        - COM_TYPE_MIC
   *        - COM_TYPE_MLC
   * @return the sensor id of the next sensor in the iteration matching the query or SI_NULL_SENSOR_ID
   */
uint16_t SQNextByType(SQuery_t *_this, uint8_t sensor_type);

/**
  * Return the sensor id of the next sensor in the iteration that match the given name and type.
  *
  * @param _this [IN] specifies an ::SIterator_t object.
  * @param sensor_name [IN] specify the name parameter for the query.
  * @param sensor_type [IN] specify the type parameter for the query.
  * @return the sensor id of the next sensor in the iteration matching the query or SI_NULL_SENSOR
*/
uint16_t SQNextByNameAndType(SQuery_t *_this, const char *sensor_name, uint8_t sensor_type);

/**
  * Return the sensor id of the next sensor in the iteration that match the given name.
  *
  * @param _this [IN] specifies an ::SIterator_t object.
  * @param sensor_enable [IN] specify the enable status parameter for the query.
  * @return the sensor id of the next sensor in the iteration matching the query or SI_NULL_SENSOR_ID
  */
uint16_t SQNextByStatusEnable(SQuery_t *_this, bool sensor_enable);

#ifdef __cplusplus
}
#endif

#endif /* SENSORMANAGER_INC_SERVICES_SQUERY_H_ */
