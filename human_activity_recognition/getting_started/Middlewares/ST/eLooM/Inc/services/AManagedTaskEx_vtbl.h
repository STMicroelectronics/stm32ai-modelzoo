/**
 ******************************************************************************
 * @file    AManagedTaskEx_vtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jul 30, 2018
 *
 * @brief
 *
 * TODO - insert here the file description
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2018 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_SERVICES_AMANAGEDTASKEX_VTBL_H_
#define INCLUDE_SERVICES_AMANAGEDTASKEX_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "systypes.h"
#include "syserror.h"
#include "systp.h"
/* MISRA messages linked to FreeRTOS include are ignored */
/*cstat -MISRAC2012-* */
#include "tx_api.h"
/*cstat -MISRAC2012-* */
#include "AManagedTask_vtbl.h"

/**
 * Create  type name for _IManagedTask_vtb.
 */
typedef struct _AManagedTaskEx_vtbl AManagedTaskEx_vtbl;

struct _AManagedTaskEx_vtbl {
  sys_error_code_t (*HardwareInit)(AManagedTask *_this, void *pParams);
  sys_error_code_t (*OnCreateTask)(AManagedTask *_this, tx_entry_function_t *pvTaskCode, CHAR **pcName, VOID **pvStackStart, ULONG *pnStackSize, UINT *pnPriority, UINT *pnPreemptThreshold, ULONG *pnTimeSlice, ULONG *pnAutoStart, ULONG *pnParams);
  sys_error_code_t (*DoEnterPowerMode)(AManagedTask *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);
  sys_error_code_t (*HandleError)(AManagedTask *_this, SysEvent xError);
  sys_error_code_t (*OnEnterTaskControlLoop)(AManagedTask *_this);
  sys_error_code_t (*ForceExecuteStep)(AManagedTaskEx *_this, EPowerMode eActivePowerMode);
  sys_error_code_t (*OnEnterPowerMode)(AManagedTaskEx *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);
};

/**
 * Managed Task extended status field. This data is used to coordinate the power mode switch between the INIT task
 * and the application managed tasks.
 */
typedef struct _AMTStatusEx {
  uint8_t nIsWaitingNoTimeout : 1;
  uint8_t nPowerModeClass: 2;

  uint8_t nUnused: 4;
  uint8_t nReserved : 1;
} AMTStatusEx;

/**
 * A Managed Task a task integrated in the system. It defines a common interface for all application tasks.
 * All Managed Tasks belong to a linked list that is the ::_ApplicationContext.
 */
struct _AManagedTaskEx {
  /**
   * Specifies  a pointer to the class virtual table.
   */
  const AManagedTaskEx_vtbl *vptr;

  /**
   * Specifies the native ThreadX task handle.
   */
  TX_THREAD m_xTaskHandle;

  /**
   *Specifies a pointer to the next managed task in the _ApplicationContext.
   */
  struct _AManagedTaskEx *m_pNext;

  /**
   * Specifies a map (PM_STATE, ExecuteStepFunc) between each application PM state and the associated step function.
   * If the pointer
   */
  const pExecuteStepFunc_t *m_pfPMState2FuncMap;

  /**
   * @see ::AMAnagedTask::m_pPMState2PMStateMap
   */
  const EPowerMode *m_pPMState2PMStateMap;

  /**
   * Status flags.
   */
  AMTStatus m_xStatus;

  /**
   * Extended status flags.
   */
  AMTStatusEx m_xStatusEx;
};

extern EPowerMode SysGetPowerMode(void);

// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTExForceExecuteStep(AManagedTaskEx *_this, EPowerMode eActivePowerMode) {
  assert_param(_this != NULL);
    EPowerMode eObjeActivePowerMode = eActivePowerMode;

    if (_this->m_pPMState2PMStateMap != NULL) {
      /* remap the PM states. */
      eObjeActivePowerMode = _this->m_pPMState2PMStateMap[(uint8_t)eActivePowerMode];
    }

  return _this->vptr->ForceExecuteStep(_this, eObjeActivePowerMode);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTExOnEnterPowerMode(AManagedTaskEx *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode) {
  assert_param(_this != NULL);
  EPowerMode eObjeActivePowerMode = eActivePowerMode;
  EPowerMode eObjNewPowerMode = eNewPowerMode;

  if (_this->m_pPMState2PMStateMap != NULL) {
    /* remap the PM states. */
    eObjeActivePowerMode = _this->m_pPMState2PMStateMap[(uint8_t)eActivePowerMode];
    eObjNewPowerMode = _this->m_pPMState2PMStateMap[(uint8_t)eNewPowerMode];
  }

  return _this->vptr->OnEnterPowerMode(_this, eObjeActivePowerMode, eObjNewPowerMode);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTInitEx(AManagedTaskEx *_this) {

  _this->m_pNext = NULL;
  _this->m_pfPMState2FuncMap = NULL;
  _this->m_pPMState2PMStateMap = NULL;
  _this->m_pfPMState2FuncMap = NULL;
  _this->m_pPMState2PMStateMap = NULL;
  _this->m_xStatus.nDelayPowerModeSwitch = 1;
  _this->m_xStatus.nPowerModeSwitchPending = 0;
  _this->m_xStatus.nPowerModeSwitchDone = 0;
  _this->m_xStatus.nIsTaskStillRunning = 0;
  _this->m_xStatus.nErrorCount = 0;
  _this->m_xStatus.nAutoStart = 0;
  _this->m_xStatus.nReserved = 1; // this identifies the task as an AManagedTaskEx.
  _this->m_xStatusEx.nIsWaitingNoTimeout = 0;
  _this->m_xStatusEx.nPowerModeClass = E_PM_CLASS_0;
  _this->m_xStatusEx.nUnused = 0;
  _this->m_xStatusEx.nReserved = 0;

  return SYS_NO_ERROR_CODE;
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTExSetInactiveState(AManagedTaskEx *_this, boolean_t bBlockedSuspended) {
  assert_param(_this);

  _this->m_xStatusEx.nIsWaitingNoTimeout = (uint8_t)bBlockedSuspended;

  return SYS_NO_ERROR_CODE;
}

SYS_DEFINE_STATIC_INLINE
boolean_t AMTExIsTaskInactive(AManagedTaskEx *_this){
  assert_param(_this);

  return (boolean_t)_this->m_xStatusEx.nIsWaitingNoTimeout;
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t AMTExSetPMClass(AManagedTaskEx *_this, EPMClass eNewPMClass) {
  assert_param(_this);

  _this->m_xStatusEx.nPowerModeClass = (uint8_t)eNewPMClass;

  return SYS_NO_ERROR_CODE;
}

SYS_DEFINE_STATIC_INLINE
EPMClass AMTExGetPMClass(AManagedTaskEx *_this) {
  assert_param(_this);

  return (EPMClass)_this->m_xStatusEx.nPowerModeClass;
}


#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_SERVICES_AMANAGEDTASKEX_VTBL_H_ */
