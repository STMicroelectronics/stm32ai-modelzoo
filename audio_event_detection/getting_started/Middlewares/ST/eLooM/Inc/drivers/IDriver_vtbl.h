/**
 ******************************************************************************
 * @file    IDriverVtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Sep 7, 2016
 * @brief   Private API for the Driver Interface
 *
 * This header file must be included included in all source files that use the
 * IDriver public API.
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

#ifndef INCLUDE_DRIVERS_IDRIVER_VTBL_H_
#define INCLUDE_DRIVERS_IDRIVER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"

typedef struct _IDriver_vtbl IDriver_vtbl;


struct _IDriver_vtbl {
  sys_error_code_t (*Init)(IDriver *_this, void *pParams);
  sys_error_code_t (*Start)(IDriver *_this);
  sys_error_code_t (*Stop)(IDriver *_this);
  sys_error_code_t (*DoEnterPowerMode)(IDriver *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);
  sys_error_code_t (*Reset)(IDriver *_this, void *pParams);
};

/**
 * IDriver interface internal state. This is the base interface for the the driver subsystem.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _IDriver {
  const IDriver_vtbl *vptr;
};

// Inline function definition.
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IDrvInit(IDriver *_this, void *pParams) {
  return _this->vptr->Init(_this, pParams);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IDrvStart(IDriver *_this) {
  return _this->vptr->Start(_this);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IDrvStop(IDriver *_this) {
  return _this->vptr->Stop(_this);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IDrvDoEnterPowerMode(IDriver *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode) {
  return _this->vptr->DoEnterPowerMode(_this, eActivePowerMode, eNewPowerMode);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IDrvReset(IDriver *_this, void *pParams) {
  return _this->vptr->Reset(_this, pParams);
}

#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_DRIVERS_IDRIVER_VTBL_H_ */
