/**
 ******************************************************************************
 * @file    EnvTask_vtbl.h
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
#ifndef HSDCORE_INC_ENVTASK_VTBL_H_
#define HSDCORE_INC_ENVTASK_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif




/* AManagedTask virtual functions */
sys_error_code_t EnvTask_vtblHardwareInit(AManagedTask *_this, void *p_params); /*!< @sa AMTHardwareInit */
sys_error_code_t EnvTask_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *p_task_code, const char **p_name, unsigned short *p_stack_depth, void **p_params, UBaseType_t *p_priority); /*!< @sa AMTOnCreateTask */
sys_error_code_t EnvTask_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode); /*!< @sa AMTDoEnterPowerMode */
sys_error_code_t EnvTask_vtblHandleError(AManagedTask *_this, SysEvent error); /*!< @sa AMTHandleError */
sys_error_code_t EnvTask_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

/* AManagedTaskEx virtual functions */
sys_error_code_t EnvTask_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode active_power_mode); /*!< @sa AMTExForceExecuteStep */
sys_error_code_t EnvTask_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode active_power_mode, const EPowerMode new_power_mode); /*!< @sa AMTExOnEnterPowerMode */


uint8_t EnvTask_vtblHTS221TempGetId(ISourceObservable *_this);
IEventSrc *EnvTask_vtblHTS221TempGetEventSourceIF(ISourceObservable *_this);
uint8_t EnvTask_vtblHTS221HumGetId(ISourceObservable *_this);
IEventSrc *EnvTask_vtblHTS221HumGetEventSourceIF(ISourceObservable *_this);
sys_error_code_t EnvTask_vtblHTS221TempGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float EnvTask_vtblHTS221TempGetFS(ISourceObservable *_this);
float EnvTask_vtblHTS221TempGetSensitivity(ISourceObservable *_this);
sys_error_code_t EnvTask_vtblHTS221HumGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float EnvTask_vtblHTS221HumGetFS(ISourceObservable *_this);
float EnvTask_vtblHTS221HumGetSensitivity(ISourceObservable *_this);

uint8_t EnvTask_vtblLPS22HHTempGetId(ISourceObservable *_this);
IEventSrc *EnvTask_vtblLPS22HHTempGetEventSourceIF(ISourceObservable *_this);
uint8_t EnvTask_vtblLPS22HHPressGetId(ISourceObservable *_this);
IEventSrc *EnvTask_vtblLPS22HHPressGetEventSourceIF(ISourceObservable *_this);
sys_error_code_t EnvTask_vtblLPS22HHPressGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float EnvTask_vtblLPS22HHPressGetFS(ISourceObservable *_this);
float EnvTask_vtblLPS22HHPressGetSensitivity(ISourceObservable *_this);
sys_error_code_t EnvTask_vtblLPS22HHTempGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float EnvTask_vtblLPS22HHTempGetFS(ISourceObservable *_this);
float EnvTask_vtblLPS22HHTempGetSensitivity(ISourceObservable *_this);

sys_error_code_t EnvTask_vtblSensorStart(ISensor_t *_this);
sys_error_code_t EnvTask_vtblSensorStop(ISensor_t *_this);
sys_error_code_t EnvTask_vtblSensorSetODR(ISensor_t *_this, float ODR);
sys_error_code_t EnvTask_vtblSensorSetFS(ISensor_t *_this, float FS);
sys_error_code_t EnvTask_vtblSensorEnable(ISensor_t *_this);
sys_error_code_t EnvTask_vtblSensorDisable(ISensor_t *_this);
boolean_t EnvTask_vtblSensorIsEnabled(ISensor_t *_this);
SensorDescriptor_t EnvTask_vtblHTS221TempGetDescription(ISensor_t *_this);
SensorDescriptor_t EnvTask_vtblHTS221HumGetDescription(ISensor_t *_this);
SensorDescriptor_t EnvTask_vtblLPS22HHTempGetDescription(ISensor_t *_this);
SensorDescriptor_t EnvTask_vtblLPS22HHPressGetDescription(ISensor_t *_this);
SensorStatus_t EnvTask_vtblHTS221TempGetStatus(ISensor_t *_this);
SensorStatus_t EnvTask_vtblHTS221HumGetStatus(ISensor_t *_this);
SensorStatus_t EnvTask_vtblLPS22HHTempGetStatus(ISensor_t *_this);
SensorStatus_t EnvTask_vtblLPS22HHPressGetStatus(ISensor_t *_this);

#ifdef __cplusplus
}
#endif

#endif /* HSDCORE_INC_ENVTASK_VTBL_H_ */
