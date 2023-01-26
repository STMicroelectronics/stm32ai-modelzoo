/**
 ******************************************************************************
 * @file    SensorManager.c
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 * @brief   This file provides a set of functions to handle the COM structure
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

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "SensorManager.h"
#include "stdlib.h"
#include "string.h"

static SensorManager_t spSMObj = {0};


/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
/* Private function prototypes -----------------------------------------------*/
/* Private functions ---------------------------------------------------------*/

uint16_t SMGetNsensor(void)
{
  return spSMObj.n_sensors;
}

ISourceObservable * SMGetSensorObserver(uint8_t id)
{
  if (id < SMGetNsensor())
  {
    return (ISourceObservable *)(spSMObj.Sensors[id]);
  }
  else
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
    return 0;
  }
}

sys_error_code_t SMSensorStart(uint8_t id)
{
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    res = ISensorStart(p_obj);
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

sys_error_code_t SMSensorStop(uint8_t id)
{
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    res =  ISensorStop(p_obj);
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

sys_error_code_t SMSensorSetODR(uint8_t id, float ODR)
{
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    res =  ISensorSetODR(p_obj, ODR);
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

sys_error_code_t SMSensorSetFS(uint8_t id, float FS)
{
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    res =  ISensorSetFS(p_obj, FS);
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

sys_error_code_t SMSensorEnable(uint8_t id)
{
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    res =  ISensorEnable(p_obj);
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

sys_error_code_t SMSensorDisable(uint8_t id)
{
  sys_error_code_t res = SYS_NO_ERROR_CODE;

  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    res =  ISensorDisable(p_obj);
  }
  else
  {
    res = SYS_INVALID_PARAMETER_ERROR_CODE;
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
  }

  return res;
}

SensorDescriptor_t SMSensorGetDescription(uint8_t id)
{
  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    return ISensorGetDescription(p_obj);
  }
  else
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
    SensorDescriptor_t device_description;
    memset(&device_description, 0, sizeof(SensorDescriptor_t));
    return device_description;
  }
}

SensorStatus_t SMSensorGetStatus(uint8_t id)
{
  if (id < SMGetNsensor())
  {
    ISensor_t *p_obj = (ISensor_t *)(spSMObj.Sensors[id]);
    return ISensorGetStatus(p_obj);
  }
  else
  {
    SYS_SET_SERVICE_LEVEL_ERROR_CODE(SYS_INVALID_PARAMETER_ERROR_CODE);
    SensorStatus_t device_status;
    memset(&device_status, 0, sizeof(SensorStatus_t));
    return device_status;
  }
}

sys_error_code_t SMDeviceGetDescription(SensorDescriptor_t *device_description)
{
  uint16_t ii;
  uint16_t n_sensors = spSMObj.n_sensors;

  if (n_sensors != 0)
  {
    ISensor_t *p_obj;

    memset(device_description, 0, n_sensors*sizeof(SensorDescriptor_t));
    for (ii = 0; ii < n_sensors; ii++)
    {
      p_obj = (ISensor_t *)(spSMObj.Sensors[ii]);
      device_description[ii] = ISensorGetDescription(p_obj);
    }
    return SYS_NO_ERROR_CODE;
  }
  else
  {
    return SYS_OUT_OF_MEMORY_ERROR_CODE;
  }
}

SensorManager_t * SMGetSensorManager(void)
{
  return &spSMObj;
}

