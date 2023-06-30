/**
  ******************************************************************************
  * @file    ISensor_vtbl.h
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

#ifndef INCLUDE_ISENSOR_VTBL_H_
#define INCLUDE_ISENSOR_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/ISourceObservable.h"
#include "services/ISourceObservable_vtbl.h"

/**
  * Create a type name for ISensor_vtbl.
  */
typedef struct _ISensor_vtbl ISensor_vtbl;


struct _ISensor_vtbl
{
  uint8_t (*GetId)(ISourceObservable *_this);
  IEventSrc* (*GetEventSourceIF)(ISourceObservable *_this);
  EMData_t (*GetDataInfo)(ISourceObservable *_this);
  sys_error_code_t (*SensorGetODR)(ISourceObservable *_this, float *p_measured, float *p_nominal);
  float (*SensorGetFS)(ISourceObservable *_this);
  float (*SensorGetSensitivity)(ISourceObservable *_this);
  sys_error_code_t (*SensorSetODR)(ISensor_t *_this, float ODR);
  sys_error_code_t (*SensorSetFS)(ISensor_t *_this, float FS);
  sys_error_code_t (*SensorSetFifoWM)(ISensor_t *_this, uint16_t fifoWM);
  sys_error_code_t (*SensorEnable)(ISensor_t *_this);
  sys_error_code_t (*SensorDisable)(ISensor_t *_this);
  boolean_t (*SensorIsEnabled)(ISensor_t *_this);
  SensorDescriptor_t (*SensorGetDescription)(ISensor_t *_this);
  SensorStatus_t (*SensorGetStatus)(ISensor_t *_this);
};


struct _ISensor_t
{
  /**
    * Pointer to the virtual table for the class.
    */
  const ISensor_vtbl *vptr;
};


// Inline functions definition
// ***************************

static inline sys_error_code_t ISensorSetODR(ISensor_t *_this, float ODR)
{
  return _this->vptr->SensorSetODR(_this, ODR);
}

static inline sys_error_code_t ISensorSetFS(ISensor_t *_this, float FS)
{
  return _this->vptr->SensorSetFS(_this, FS);
}

static inline sys_error_code_t ISensorSetFifoWM(ISensor_t *_this, uint16_t fifoWM)
{
  if(_this->vptr->SensorSetFifoWM != NULL)
  {
    return  _this->vptr->SensorSetFifoWM(_this, fifoWM);
  }
  return SYS_INVALID_FUNC_CALL_ERROR_CODE;
}

static inline sys_error_code_t ISensorEnable(ISensor_t *_this)
{
  return _this->vptr->SensorEnable(_this);
}

static inline sys_error_code_t ISensorDisable(ISensor_t *_this)
{
  return _this->vptr->SensorDisable(_this);
}

static inline boolean_t ISensorIsEnabled(ISensor_t *_this)
{
  return _this->vptr->SensorIsEnabled(_this);
}

static inline SensorDescriptor_t ISensorGetDescription(ISensor_t *_this)
{
  return _this->vptr->SensorGetDescription(_this);
}

static inline SensorStatus_t ISensorGetStatus(ISensor_t *_this)
{
  return _this->vptr->SensorGetStatus(_this);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSOR_VTBL_H_ */
