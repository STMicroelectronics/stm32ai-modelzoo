/**
 ******************************************************************************
 * @file    SensorManager.h
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief   
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *                             
 *
 ******************************************************************************
 */
#ifndef HSDCORE_INC_SENSORMANAGER_H_
#define HSDCORE_INC_SENSORMANAGER_H_

#ifdef __cplusplus
extern "C" {
#endif




#include "ISensor.h"
#include "ISensor_vtbl.h"
#include "SensorDef.h"


  /**
   * Create  type name for _SensorManager_t.
   */
  typedef struct _SensorManager_t SensorManager_t;

  /**
   *  SensorManager_t internal structure.
   */
  struct _SensorManager_t {

    /**
     * Describes the sensor capabilities.
     */
    ISensor_t *Sensors[COM_MAX_SENSORS];

    /**
     * Indicates the number of sensors available.
     */
    uint16_t n_sensors;
  };


  /* Public API declaration */
  /**************************/
  ISourceObservable * SMGetSensorObserver(uint8_t id);
  uint16_t SMGetNsensor(void);
  sys_error_code_t SMSensorStart(uint8_t id);
  sys_error_code_t SMSensorStop(uint8_t id);
  sys_error_code_t SMSensorSetODR(uint8_t id, float ODR);
  sys_error_code_t SMSensorSetFS(uint8_t id, float FS);
  sys_error_code_t SMSensorEnable(uint8_t id);
  sys_error_code_t SMSensorDisable(uint8_t id);
  SensorDescriptor_t SMSensorGetDescription(uint8_t id);
  SensorStatus_t SMSensorGetStatus(uint8_t id);
  sys_error_code_t SMDeviceGetDescription(SensorDescriptor_t *device_description);
  SensorManager_t * SMGetSensorManager(void);

  /* Inline functions definition */
  /*******************************/


#ifdef __cplusplus
}
#endif

#endif /* HSDCORE_INC_SENSORMANAGER_H_ */
