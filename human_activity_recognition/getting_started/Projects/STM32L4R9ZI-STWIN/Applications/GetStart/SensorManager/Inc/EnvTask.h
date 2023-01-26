/**
 ******************************************************************************
 * @file    EnvTask.h
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
#ifndef HSDCORE_INC_ENVTASK_H_
#define HSDCORE_INC_ENVTASK_H_

#ifdef __cplusplus
extern "C" {
#endif



#include "services/systp.h"
#include "services/syserror.h"
#include "services/AManagedTaskEx.h"
#include "services/AManagedTaskEx_vtbl.h"
#include "events/SensorEventSrc.h"
#include "events/SensorEventSrc_vtbl.h"
#include "ISensor.h"
#include "ISensor_vtbl.h"
#include "queue.h"

#include "I2CBusIF.h"

#include "HTS221Class.h"
#include "LPS22HHClass.h"


/**
 * Create  type name for _EnvTask.
 */
typedef struct _EnvTask EnvTask;


/* Public API declaration */
/**************************/

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *EnvTaskGetHTS221TempSensorIF(EnvTask *_this);

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *EnvTaskGetHTS221HumSensorIF(EnvTask *_this);

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *EnvTaskGetLPS22HHTempSensorIF(EnvTask *_this);

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *EnvTaskGetLPS22HHPressSensorIF(EnvTask *_this);

/**
 * Allocate an instance of EnvTask.
 *
 * @return a pointer to the generic object ::AManagedTaskEx if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *EnvTaskAlloc(void);

/**
 * Get the SPI interface for the HTS221.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the SPI interface of the sensor.
 */
I2CBusIF *EnvTaskGetHTS221SensorIF(EnvTask *_this);

/**
 * Get the SPI interface for the LPS22HH.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the SPI interface of the sensor.
 */
I2CBusIF *EnvTaskGetLPS22HHSensorIF(EnvTask *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *EnvTaskGetHTS221TempEventSrcIF(EnvTask *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *EnvTaskGetHTS221HumEventSrcIF(EnvTask *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *EnvTaskGetLPS22HHTempEventSrcIF(EnvTask *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *EnvTaskGetLPS22HHPressEventSrcIF(EnvTask *_this);

/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* HSDCORE_INC_ENVTASK_H_ */
