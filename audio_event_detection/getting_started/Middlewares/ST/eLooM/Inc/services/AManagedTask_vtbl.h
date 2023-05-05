/**
 ******************************************************************************
 * @file    AManagedTask_vtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jan 13, 2017
 * @brief
 *
 * TODO - insert here the file description
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2016 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#ifndef INCLUDE_SERVICES_AMANAGEDTASKVTBL_H_
#define INCLUDE_SERVICES_AMANAGEDTASKVTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "systypes.h"
#include "syserror.h"
#include "systp.h"
/* MISRA messages linked to FreeRTOS include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
/*cstat +MISRAC2012-* */

/**
 * Create  type name for _IManagedTask_vtb.
 */
typedef struct _AManagedTask_vtbl AManagedTask_vtbl;

struct _AManagedTask_vtbl {
  sys_error_code_t (*HardwareInit)(AManagedTask *_this, void *pParams);
  sys_error_code_t (*OnCreateTask)(AManagedTask *_this, tx_entry_function_t *pvTaskCode, CHAR **pcName, VOID **pvStackStart, ULONG *pnStackSize, UINT *pnPriority, UINT *pnPreemptThreshold, ULONG *pnTimeSlice, ULONG *pnAutoStart, ULONG *pnParams);
  sys_error_code_t (*DoEnterPowerMode)(AManagedTask *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);
  sys_error_code_t (*HandleError)(AManagedTask *_this, SysEvent xError);
  sys_error_code_t (*OnEnterTaskControlLoop)(AManagedTask *_this);
};

/**
 * Managed Task status field. This data is used to coordinate the power mode switch between the INIT task
 * and the application managed tasks.
 */
typedef struct _AMTStatus {
  /**
   * Set by task to delay a power mode switch. This allow a task to complete a step in its control loop
   * and put the task in a safe state before the power mode transaction.
   */
  uint8_t nDelayPowerModeSwitch: 1;

  /**
   * Set by INIT to signal a task about a pending power mode switch.
   */
  uint8_t nPowerModeSwitchPending: 1;

  /**
   * SET by INIT to mark a task ready for the power mode switch.
   * RESET by INIT at the end of teh power mode switch sequence.
   */
  uint8_t nPowerModeSwitchDone: 1;

  /**
   * Set by a managed task to notify the system that it is working fine. It is reset by the application error delegate.
   */
  uint8_t nIsTaskStillRunning: 1;

  /**
   * Count the error occurred during the task execution.
   */
  uint8_t nErrorCount: 2;

  /**
   * Specify if the task has been created suspended. It depends on the pnAutoStart parameter passed
   * during the task creation.
   */
  uint8_t nAutoStart: 1;

  uint8_t nReserved : 1;
} AMTStatus;

/**
 * A Managed Task a task integrated in the system. It defines a common interface for all application tasks.
 * All Managed Tasks belong to a linked list that is the ::_ApplicationContext.
 */
struct _AManagedTask {
  /**
   * Specifies  a pointer to the class virtual table.
   */
  const AManagedTask_vtbl *vptr;

  /**
   * Specifies the native ThreadX task handle.
   */
  TX_THREAD m_xTaskHandle;

  /**
   *Specifies a pointer to the next managed task in the _ApplicationContext.
   */
  struct _AManagedTask *m_pNext;

  /**
   * Specifies a map (PM_STATE, ExecuteStepFunc) between each application PM state and the associated step function.
   * If the pointer
   */
  const pExecuteStepFunc_t *m_pfPMState2FuncMap;

  /**
   * Specifies a map (PM_STATE, PM_STATE). It is used by the application to re-map the behavior of an ::AManagedTask
   * during a power mode switch. Image a developer that want to use an existing managed task (MyManagedTask1) in a new application. Probably
   * the new application has a different PM (PM_SM_2) state machine than the one used to design and implement the managed task
   * MyManagedTask1 (PM_SM_1). In this scenario it is possible to reuse the managed task as it is if exist a subjective function
   * f(x) -> (PM_SM_2, PM_SM_1), that map all states of PM_SM_1 in one or more states of PM_SM_2.
   * It is possible to set this member to NULL, and, in this case no remapping is done.
   */
  const EPowerMode *m_pPMState2PMStateMap;

  /**
   * Status flags.
   */
  AMTStatus m_xStatus;
};

extern EPowerMode SysGetPowerMode(void);


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTHardwareInit(AManagedTask *_this, void *pParams) {
  return _this->vptr->HardwareInit(_this, pParams);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTOnCreateTask(AManagedTask *_this, tx_entry_function_t *pvTaskCode, CHAR **pcName,
    VOID **pvStackStart, ULONG *pnStackSize,
    UINT *pnPriority, UINT *pnPreemptThreshold,
    ULONG *pnTimeSlice, ULONG *pnAutoStart,
    ULONG *pnParams) {
  return _this->vptr->OnCreateTask(_this, pvTaskCode, pcName, pvStackStart, pnStackSize, pnPriority, pnPreemptThreshold, pnTimeSlice, pnAutoStart, pnParams);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTDoEnterPowerMode(AManagedTask *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode) {
  assert_param(_this != NULL);
  EPowerMode eObjeActivePowerMode = eActivePowerMode;
  EPowerMode eObjNewPowerMode = eNewPowerMode;

  if (_this->m_pPMState2PMStateMap != NULL) {
    /* remap the PM states. */
    eObjeActivePowerMode = _this->m_pPMState2PMStateMap[(uint8_t)eActivePowerMode];
    eObjNewPowerMode = _this->m_pPMState2PMStateMap[(uint8_t)eNewPowerMode];
  }

  return _this->vptr->DoEnterPowerMode(_this, eObjeActivePowerMode, eObjNewPowerMode);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTHandleError(AManagedTask *_this, SysEvent xError) {
  return _this->vptr->HandleError(_this, xError);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTOnEnterTaskControlLoop(AManagedTask *_this) {
  return _this->vptr->OnEnterTaskControlLoop(_this);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTInit(AManagedTask *_this) {
  _this->m_pNext = NULL;
  _this->m_pfPMState2FuncMap = NULL;
  _this->m_pPMState2PMStateMap = NULL;
  _this->m_xStatus.nDelayPowerModeSwitch = 1;
  _this->m_xStatus.nPowerModeSwitchPending = 0;
  _this->m_xStatus.nPowerModeSwitchDone = 0;
  _this->m_xStatus.nIsTaskStillRunning = 0;
  _this->m_xStatus.nErrorCount = 0;
  _this->m_xStatus.nAutoStart = 0;
  _this->m_xStatus.nReserved = 0;

  return SYS_NO_ERROR_CODE;
}

SYS_DEFINE_STATIC_INLINE
EPowerMode AMTGetSystemPowerMode() {
  return SysGetPowerMode();
}

SYS_DEFINE_STATIC_INLINE
EPowerMode AMTGetTaskPowerMode(AManagedTask *_this) {
  assert_param(_this != NULL);

  EPowerMode eTaskPowrMode = (_this->m_pPMState2PMStateMap != NULL) ?
      _this->m_pPMState2PMStateMap[(uint8_t)SysGetPowerMode()] :
      SysGetPowerMode();

  return eTaskPowrMode;
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTNotifyIsStillRunning(AManagedTask *_this, sys_error_code_t nStepError) {

  if (SYS_IS_ERROR_CODE(nStepError) && (_this->m_xStatus.nErrorCount < MT_MAX_ERROR_COUNT)) {
    _this->m_xStatus.nErrorCount++;
  }
  if (_this->m_xStatus.nErrorCount < MT_ALLOWED_ERROR_COUNT) {
    _this->m_xStatus.nIsTaskStillRunning = 1;
  }

  return SYS_NO_ERROR_CODE;
}

SYS_DEFINE_STATIC_INLINE
void AMTResetAEDCounter(AManagedTask *_this) {
  UNUSED(_this);
  SysResetAEDCounter();
}

SYS_DEFINE_STATIC_INLINE
boolean_t AMTIsPowerModeSwitchPending(AManagedTask *_this) {
  assert_param(_this != NULL);

  return (boolean_t)_this->m_xStatus.nPowerModeSwitchPending;
}

SYS_DEFINE_STATIC_INLINE
void AMTReportErrOnStepExecution(AManagedTask *_this, sys_error_code_t nStepError) {
  UNUSED(nStepError);

  if (_this->m_xStatus.nErrorCount < MT_ALLOWED_ERROR_COUNT) {
    _this->m_xStatus.nErrorCount++;
  }
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTSetPMStateRemapFunc(AManagedTask *_this, const EPowerMode *pPMState2PMStateMap) {
	assert_param(_this != NULL);

	_this->m_pPMState2PMStateMap = pPMState2PMStateMap;

	return SYS_NO_ERROR_CODE;
}

#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_SERVICES_AMANAGEDTASKVTBL_H_ */
