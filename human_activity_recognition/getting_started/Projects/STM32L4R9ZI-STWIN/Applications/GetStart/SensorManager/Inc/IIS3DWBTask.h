/**
 ******************************************************************************
 * @file    IIS3DWBTask.h
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
#ifndef IIS3DWBTASK_H_
#define IIS3DWBTASK_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/AManagedTaskEx.h"
#include "services/AManagedTaskEx_vtbl.h"
#include "SPIBusIF.h"
#include "iis3dwb_reg.h"
#include "events/SensorEventSrc.h"
#include "events/SensorEventSrc_vtbl.h"
#include "ISensor.h"
#include "ISensor_vtbl.h"
#include "queue.h"

//TODO: STF.Begin - where should these be defined ?
#define IIS3DWB_MAX_DRDY_PERIOD           (1.0)
#ifndef IIS3DWB_MAX_WTM_LEVEL
#define IIS3DWB_MAX_WTM_LEVEL             (256)
#endif
#define IIS3DWB_MIN_WTM_LEVEL             (16)
#define IIS3DWB_MAX_SAMPLES_PER_IT        (IIS3DWB_MAX_WTM_LEVEL)
//STF.End

#define IIS3DWB_CFG_MAX_LISTENERS           2

/**
 * Create  type name for _IIS3DWBTask.
 */
typedef struct _IIS3DWBTask IIS3DWBTask;


// Public API declaration
//***********************

/**
 * Get the ISourceObservable interface for the accelerometer.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the generic object ::ISourceObservable if success,
 * or NULL if out of memory error occurs.
 */
ISourceObservable *IIS3DWBTaskGetAccSensorIF(IIS3DWBTask *_this);

/**
 * Allocate an instance of IIS3DWBTask.
 *
 * @return a pointer to the generic obejct ::AManagedTaskEx if success,
 * or NULL if out of memory error occurs.
 */
AManagedTaskEx *IIS3DWBTaskAlloc(void);

/**
 * Get the SPI interface for the sensor task.
 *
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the SPI interface of the sensor.
 */
SPIBusIF *IIS3DWBTaskGetSensorIF(IIS3DWBTask *_this);

/**
 * Get the ::IEventSrc interface for the sensor task.
 * @param _this [IN] specifies a pointer to a task object.
 * @return a pointer to the ::IEventSrc interface of the sensor.
 */
IEventSrc *IIS3DWBTaskGetEventSrcIF(IIS3DWBTask *_this);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* IIS3DWBTASK_H_ */
