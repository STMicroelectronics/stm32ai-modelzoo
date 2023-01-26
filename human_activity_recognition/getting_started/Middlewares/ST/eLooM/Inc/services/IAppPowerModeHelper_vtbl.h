/**
 ******************************************************************************
 * @file    IAppPowerModeHelper_vtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Oct 30, 2018
 *
 * @brief
 *
 * <DESCRIPTIOM>
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
#ifndef INCLUDE_SERVICES_IAPPPOWERMODEHELPER_VTBL_H_
#define INCLUDE_SERVICES_IAPPPOWERMODEHELPER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "systp.h"
#include "systypes.h"
#include "syserror.h"


/**
 * Create  type name for _IAppPowerModeHelper_vtbl.
 */
typedef struct _IAppPowerModeHelper_vtbl IAppPowerModeHelper_vtbl;

/**
 * Specifies the virtual table for the  class.
 */
struct _IAppPowerModeHelper_vtbl {
  sys_error_code_t (*Init)(IAppPowerModeHelper *_this);
  EPowerMode (*ComputeNewPowerMode)(IAppPowerModeHelper *_this, const SysEvent xEvent);
  boolean_t (*CheckPowerModeTransaction)(IAppPowerModeHelper *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);
  sys_error_code_t (*DidEnterPowerMode)(IAppPowerModeHelper *_this, EPowerMode ePowerMode);
  EPowerMode (*GetActivePowerMode)(IAppPowerModeHelper *_this);
  SysPowerStatus (*GetPowerStatus)(IAppPowerModeHelper *_this);
  boolean_t (*IsLowPowerMode)(IAppPowerModeHelper *_this, const EPowerMode ePowerMode);
};

/**
 * IF_NAME interface internal state.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _IAppPowerModeHelper {
  /**
   * Pointer to the virtual table for the class.
   */
  const IAppPowerModeHelper_vtbl *vptr;
};


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IapmhInit(IAppPowerModeHelper *_this) {
  return _this->vptr->Init(_this);
}

SYS_DEFINE_STATIC_INLINE
EPowerMode IapmhComputeNewPowerMode(IAppPowerModeHelper *_this, const SysEvent xEvent) {
  return _this->vptr->ComputeNewPowerMode(_this, xEvent);
}

SYS_DEFINE_STATIC_INLINE
boolean_t IapmhCheckPowerModeTransaction(IAppPowerModeHelper *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode) {
  return _this->vptr->CheckPowerModeTransaction(_this, eActivePowerMode, eNewPowerMode);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IapmhDidEnterPowerMode(IAppPowerModeHelper *_this, EPowerMode ePowerMode) {
  return _this->vptr->DidEnterPowerMode(_this, ePowerMode);
}

SYS_DEFINE_STATIC_INLINE
EPowerMode IapmhGetActivePowerMode(IAppPowerModeHelper *_this) {
  return _this->vptr->GetActivePowerMode(_this);
}

SYS_DEFINE_STATIC_INLINE
SysPowerStatus IapmhGetPowerStatus(IAppPowerModeHelper *_this) {
  return _this->vptr->GetPowerStatus(_this);
}

SYS_DEFINE_STATIC_INLINE
boolean_t IapmhIsLowPowerMode(IAppPowerModeHelper *_this, const EPowerMode ePowerMode) {
  return _this->vptr->IsLowPowerMode(_this, ePowerMode);
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_IAPPPOWERMODEHELPER_VTBL_H_ */
