/**
 ******************************************************************************
 * @file    HTS221Task_vtbl.h
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
#ifndef HTS221TASK_VTBL_H_
#define HTS221TASK_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif




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
sys_error_code_t HTS221Task_vtblHardwareInit(AManagedTask *_this, void *pParams);
sys_error_code_t HTS221Task_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *pTaskCode, const char **pName, unsigned short *pStackDepth, void **pParams, UBaseType_t *pPriority); ///< @sa AMTOnCreateTask
sys_error_code_t HTS221Task_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTDoEnterPowerMode
sys_error_code_t HTS221Task_vtblHandleError(AManagedTask *_this, SysEvent Error); ///< @sa AMTHandleError
sys_error_code_t HTS221Task_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

/* AManagedTaskEx virtual functions */
sys_error_code_t HTS221Task_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode ActivePowerMode); ///< @sa AMTExForceExecuteStep
sys_error_code_t HTS221Task_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTExOnEnterPowerMode


uint8_t HTS221Task_vtblTempGetId(ISourceObservable *_this);
uint8_t HTS221Task_vtblHumGetId(ISourceObservable *_this);
IEventSrc *HTS221Task_vtblTempGetEventSourceIF(ISourceObservable *_this);
IEventSrc *HTS221Task_vtblHumGetEventSourceIF(ISourceObservable *_this);
sys_error_code_t HTS221Task_vtblTempGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float HTS221Task_vtblTempGetFS(ISourceObservable *_this);
float HTS221Task_vtblTempGetSensitivity(ISourceObservable *_this);
sys_error_code_t HTS221Task_vtblHumGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float HTS221Task_vtblHumGetFS(ISourceObservable *_this);
float HTS221Task_vtblHumGetSensitivity(ISourceObservable *_this);

sys_error_code_t HTS221Task_vtblSensorStart(ISensor_t *_this);
sys_error_code_t HTS221Task_vtblSensorStop(ISensor_t *_this);
sys_error_code_t HTS221Task_vtblSensorSetODR(ISensor_t *_this, float ODR);
sys_error_code_t HTS221Task_vtblSensorSetFS(ISensor_t *_this, float FS);
sys_error_code_t HTS221Task_vtblSensorEnable(ISensor_t *_this);
sys_error_code_t HTS221Task_vtblSensorDisable(ISensor_t *_this);
boolean_t HTS221Task_vtblSensorIsEnabled(ISensor_t *_this);
SensorDescriptor_t HTS221Task_vtblTempGetDescription(ISensor_t *_this);
SensorDescriptor_t HTS221Task_vtblHumGetDescription(ISensor_t *_this);
SensorStatus_t HTS221Task_vtblTempGetStatus(ISensor_t *_this);
SensorStatus_t HTS221Task_vtblHumGetStatus(ISensor_t *_this);



#ifdef __cplusplus
}
#endif

#endif /* HTS221TASK_VTBL_H_ */
