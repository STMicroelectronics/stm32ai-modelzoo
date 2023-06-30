/**
  ******************************************************************************
  * @file    ISensor.h
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

#ifndef INCLUDE_ISENSOR_H_
#define INCLUDE_ISENSOR_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"
#include "SensorDef.h"
#include "services/ISourceObservable.h"


/**
  * Create  type name for ISensor.
  */
typedef struct _ISensor_t ISensor_t;


// Public API declaration
//***********************
/** Public interface **/
static inline sys_error_code_t ISensorSetODR(ISensor_t *_this, float ODR);
static inline sys_error_code_t ISensorSetFS(ISensor_t *_this, float FS);
static inline sys_error_code_t ISensorSetFifoWM(ISensor_t *_this, uint16_t fifoWM);
static inline sys_error_code_t ISensorEnable(ISensor_t *_this);
static inline sys_error_code_t ISensorDisable(ISensor_t *_this);
static inline boolean_t ISensorIsEnabled(ISensor_t *_this);
static inline SensorDescriptor_t ISensorGetDescription(ISensor_t *_this);
static inline SensorStatus_t ISensorGetStatus(ISensor_t *_this);


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSOR_H_ */
