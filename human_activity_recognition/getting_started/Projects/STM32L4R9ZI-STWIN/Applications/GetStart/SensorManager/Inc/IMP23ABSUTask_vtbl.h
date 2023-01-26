/**
 ******************************************************************************
 * @file    IMP23ABSUTask_vtbl.h
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
#ifndef IMP23ABSUTASK_VTBL_H_
#define IMP23ABSUTASK_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif



/* AManagedTask virtual functions */
sys_error_code_t IMP23ABSUTask_vtblHardwareInit(AManagedTask *_this, void *pParams); ///< @sa AMTHardwareInit
sys_error_code_t IMP23ABSUTask_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *pTaskCode, const char **pName, unsigned short *pStackDepth, void **pParams, UBaseType_t *pPriority); ///< @sa AMTOnCreateTask
sys_error_code_t IMP23ABSUTask_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTDoEnterPowerMode
sys_error_code_t IMP23ABSUTask_vtblHandleError(AManagedTask *_this, SysEvent Error); ///< @sa AMTHandleError
sys_error_code_t IMP23ABSUTask_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

/* AManagedTaskEx virtual functions */
sys_error_code_t IMP23ABSUTask_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode ActivePowerMode); ///< @sa AMTExForceExecuteStep
sys_error_code_t IMP23ABSUTask_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTExOnEnterPowerMode

uint8_t IMP23ABSUTask_vtblMicGetId(ISourceObservable *_this);
IEventSrc *IMP23ABSUTask_vtblGetEventSourceIF(ISourceObservable *_this);
sys_error_code_t IMP23ABSUTask_vtblMicGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
float IMP23ABSUTask_vtblMicGetFS(ISourceObservable *_this);
float IMP23ABSUTask_vtblMicGetSensitivity(ISourceObservable *_this);

sys_error_code_t IMP23ABSUTask_vtblSensorStart(ISensor_t *_this);
sys_error_code_t IMP23ABSUTask_vtblSensorStop(ISensor_t *_this);
sys_error_code_t IMP23ABSUTask_vtblSensorSetODR(ISensor_t *_this, float ODR);
sys_error_code_t IMP23ABSUTask_vtblSensorSetFS(ISensor_t *_this, float FS);
sys_error_code_t IMP23ABSUTask_vtblSensorEnable(ISensor_t *_this);
sys_error_code_t IMP23ABSUTask_vtblSensorDisable(ISensor_t *_this);
boolean_t IMP23ABSUTask_vtblSensorIsEnabled(ISensor_t *_this);
SensorDescriptor_t IMP23ABSUTask_vtblSensorGetDescription(ISensor_t *_this);
SensorStatus_t IMP23ABSUTask_vtblSensorGetStatus(ISensor_t *_this);

#ifdef __cplusplus
}
#endif

#endif /* IMP23ABSUTASK_VTBL_H_ */
