/**
 ******************************************************************************
 * @file    LPS22HHTask_vtbl.h
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
#ifndef LPS22HHTASK_VTBL_H_
#define LPS22HHTASK_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


//#include "ISensor.h"


// AManagedTaskEx virtual functions

/**
 * Initialize the hardware resource for the task.
 * This task doesn't need a driver extending the ::IDriver interface because:
 * - it manages two GPIO pins, that are the CS connected to the sensor SPI IF and the EXTI line.
 * - it uses the common sensor driver provided by the ST Sensor Solutions Software Team .
 *
 * @param _this [IN] specifies a task object.
 * @param pParams [IN] specifies task specific parameters. Not used
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 * @sa AMTHardwareInit
 */
sys_error_code_t LPS22HHTask_vtblHardwareInit(AManagedTask *_this, void *pParams);
sys_error_code_t LPS22HHTask_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *pTaskCode, const char **pName, unsigned short *pStackDepth, void **pParams, UBaseType_t *pPriority); ///< @sa AMTOnCreateTask
sys_error_code_t LPS22HHTask_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTDoEnterPowerMode
sys_error_code_t LPS22HHTask_vtblHandleError(AManagedTask *_this, SysEvent Error); ///< @sa AMTHandleError
sys_error_code_t LPS22HHTask_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

/* AManagedTaskEx virtual functions */
sys_error_code_t LPS22HHTask_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode ActivePowerMode); ///< @sa AMTExForceExecuteStep
sys_error_code_t LPS22HHTask_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTExOnEnterPowerMode


uint8_t LPS22HHTask_vtblTempGetId(ISourceObservable *_this);
uint8_t LPS22HHTask_vtblPressGetId(ISourceObservable *_this);
IEventSrc *LPS22HHTask_vtblTempGetEventSourceIF(ISourceObservable *_this);
IEventSrc *LPS22HHTask_vtblPressGetEventSourceIF(ISourceObservable *_this);
sys_error_code_t LPS22HHTask_vtblPressGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float LPS22HHTask_vtblPressGetFS(ISourceObservable *_this);
float LPS22HHTask_vtblPressGetSensitivity(ISourceObservable *_this);
sys_error_code_t LPS22HHTask_vtblTempGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float LPS22HHTask_vtblTempGetFS(ISourceObservable *_this);
float LPS22HHTask_vtblTempGetSensitivity(ISourceObservable *_this);

sys_error_code_t LPS22HHTask_vtblSensorStart(ISensor_t *_this);
sys_error_code_t LPS22HHTask_vtblSensorStop(ISensor_t *_this);
sys_error_code_t LPS22HHTask_vtblSensorSetODR(ISensor_t *_this, float ODR);
sys_error_code_t LPS22HHTask_vtblSensorSetFS(ISensor_t *_this, float FS);
sys_error_code_t LPS22HHTask_vtblSensorEnable(ISensor_t *_this);
sys_error_code_t LPS22HHTask_vtblSensorDisable(ISensor_t *_this);
boolean_t LPS22HHTask_vtblSensorIsEnabled(ISensor_t *_this);
SensorDescriptor_t LPS22HHTask_vtblTempGetDescription(ISensor_t *_this);
SensorDescriptor_t LPS22HHTask_vtblPressGetDescription(ISensor_t *_this);
SensorStatus_t LPS22HHTask_vtblTempGetStatus(ISensor_t *_this);
SensorStatus_t LPS22HHTask_vtblPressGetStatus(ISensor_t *_this);

#ifdef __cplusplus
}
#endif

#endif /* LPS22HHTASK_VTBL_H_ */
