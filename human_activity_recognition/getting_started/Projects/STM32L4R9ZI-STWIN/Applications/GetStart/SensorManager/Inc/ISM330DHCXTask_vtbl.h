/**
 ******************************************************************************
 * @file    ISM330DHCXTask_vtbl.h
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
#ifndef ISM330DHCXTASK_VTBL_H_
#define ISM330DHCXTASK_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif




  /* AManagedTask virtual functions */

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
  sys_error_code_t ISM330DHCXTask_vtblHardwareInit(AManagedTask *_this, void *pParams);
  sys_error_code_t ISM330DHCXTask_vtblOnCreateTask(AManagedTask *_this, TaskFunction_t *pTaskCode, const char **pName, unsigned short *pStackDepth, void **pParams, UBaseType_t *pPriority); ///< @sa AMTOnCreateTask
  sys_error_code_t ISM330DHCXTask_vtblDoEnterPowerMode(AManagedTask *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTDoEnterPowerMode
  sys_error_code_t ISM330DHCXTask_vtblHandleError(AManagedTask *_this, SysEvent Error); ///< @sa AMTHandleError
  sys_error_code_t ISM330DHCXTask_vtblOnEnterTaskControlLoop(AManagedTask *this); ///< @sa AMTOnEnterTaskControlLoop

  /* AManagedTaskEx virtual functions */
  sys_error_code_t ISM330DHCXTask_vtblForceExecuteStep(AManagedTaskEx *_this, EPowerMode ActivePowerMode); ///< @sa AMTExForceExecuteStep
  sys_error_code_t ISM330DHCXTask_vtblOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode ActivePowerMode, const EPowerMode NewPowerMode); ///< @sa AMTExOnEnterPowerMode

  uint8_t ISM330DHCXTask_vtblAccGetId(ISourceObservable *_this);
  uint8_t ISM330DHCXTask_vtblGyroGetId(ISourceObservable *_this);
  IEventSrc *ISM330DHCXTask_vtblAccGetEventSourceIF(ISourceObservable *_this);
  IEventSrc *ISM330DHCXTask_vtblGyroGetEventSourceIF(ISourceObservable *_this);
  sys_error_code_t ISM330DHCXTask_vtblAccGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
  float ISM330DHCXTask_vtblAccGetFS(ISourceObservable *_this);
  float ISM330DHCXTask_vtblAccGetSensitivity(ISourceObservable *_this);
  sys_error_code_t ISM330DHCXTask_vtblGyroGetODR(ISourceObservable *_this, float *p_measured, float *p_nominal);
  float ISM330DHCXTask_vtblGyroGetFS(ISourceObservable *_this);
  float ISM330DHCXTask_vtblGyroGetSensitivity(ISourceObservable *_this);

  sys_error_code_t ISM330DHCXTask_vtblSensorStart(ISensor_t *_this);
  sys_error_code_t ISM330DHCXTask_vtblSensorStop(ISensor_t *_this);
  sys_error_code_t ISM330DHCXTask_vtblSensorSetODR(ISensor_t *_this, float ODR);
  sys_error_code_t ISM330DHCXTask_vtblSensorSetFS(ISensor_t *_this, float FS);
  sys_error_code_t ISM330DHCXTask_vtblSensorEnable(ISensor_t *_this);
  sys_error_code_t ISM330DHCXTask_vtblSensorDisable(ISensor_t *_this);
  boolean_t ISM330DHCXTask_vtblSensorIsEnabled(ISensor_t *_this);
  SensorDescriptor_t ISM330DHCXTask_vtblAccGetDescription(ISensor_t *_this);
  SensorDescriptor_t ISM330DHCXTask_vtblGyroGetDescription(ISensor_t *_this);
  SensorStatus_t ISM330DHCXTask_vtblAccGetStatus(ISensor_t *_this);
  SensorStatus_t ISM330DHCXTask_vtblGyroGetStatus(ISensor_t *_this);

#ifdef __cplusplus
}
#endif

#endif /* ISM330DHCXTASK_VTBL_H_ */
