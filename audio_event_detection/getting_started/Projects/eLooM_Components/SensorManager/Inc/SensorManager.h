/**
  ******************************************************************************
  * @file    SensorManager.h
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
#ifndef SENSORMANAGER_H_
#define SENSORMANAGER_H_

#ifdef __cplusplus
extern "C" {
#endif



#include "SensorManager_conf.h"
#include "ISensor.h"
#include "ISensor_vtbl.h"
#include "SensorDef.h"


/* sensor error code */
/*********************/

#ifndef SYS_NO_ERROR_CODE
#define SYS_NO_ERROR_CODE                                   0
#endif
#ifndef SYS_SENSOR_TASK_BASE_ERROR_CODE
#define SYS_SENSOR_TASK_BASE_ERROR_CODE                     1
#endif
#define SYS_SENSOR_TASK_OP_ERROR_CODE                       SYS_SENSOR_TASK_BASE_ERROR_CODE + 1
#define SYS_SENSOR_TASK_UNKNOWN_MSG_ERROR_CODE              SYS_SENSOR_TASK_BASE_ERROR_CODE + 2
#define SYS_SENSOR_TASK_MSG_LOST_ERROR_CODE                 SYS_SENSOR_TASK_BASE_ERROR_CODE + 3


#ifndef HSD_USE_DUMMY_DATA
#define HSD_USE_DUMMY_DATA 0
#endif

#ifndef SM_MAX_SENSORS
#define SM_MAX_SENSORS               16
#endif

/**
  * Create  type name for _SensorManager_t.
  */
typedef struct _SensorManager_t SensorManager_t;

/**
  *  SensorManager_t internal structure.
  */
struct _SensorManager_t
{

  /**
    * Describes the sensor capabilities.
    */
  ISensor_t *Sensors[SM_MAX_SENSORS];

  /**
    * Indicates the number of sensors available.
    */
  uint16_t n_sensors;
};


/* Public API declaration */
/**************************/
ISourceObservable *SMGetSensorObserver(uint8_t id);
uint16_t SMGetNsensor(void);
sys_error_code_t SMSensorSetODR(uint8_t id, float ODR);
sys_error_code_t SMSensorSetFS(uint8_t id, float FS);
sys_error_code_t SMSensorSetFifoWM(uint8_t id, uint16_t fifoWM);
sys_error_code_t SMSensorEnable(uint8_t id);
sys_error_code_t SMSensorDisable(uint8_t id);
SensorDescriptor_t SMSensorGetDescription(uint8_t id);
SensorStatus_t SMSensorGetStatus(uint8_t id);
sys_error_code_t SMDeviceGetDescription(SensorDescriptor_t *device_description);
SensorManager_t *SMGetSensorManager(void);
uint32_t SMGetnBytesPerSample(uint8_t id);


/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* SENSORMANAGER_H_ */
