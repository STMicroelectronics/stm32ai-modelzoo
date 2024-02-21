/**
 ******************************************************************************
 * @file    IBootVtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Nov 22, 2017
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2017 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_SERVICES_IBOOTVTBL_H_
#define INCLUDE_SERVICES_IBOOTVTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "systp.h"
#include "systypes.h"
#include "syserror.h"

/**
 * Create a type name for _IBoot_vtbl.
 */
typedef struct _IBoot_vtbl IBoot_vtbl;

/**
 * Specifies the virtual table for the ::IBoot class.
 */
struct _IBoot_vtbl {
  sys_error_code_t (*Init)(IBoot *_this);
  boolean_t (*CheckDFUTrigger)(IBoot *_this);
  uint32_t (*GetAppAdderss)(IBoot *_this);
  sys_error_code_t (*OnJampToApp)(IBoot *_this, uint32_t nAppDress);
};

/**
 * IBoot interface internal state.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _IBoot {
  /**
   * Pointer to the virtual table for the class.
   */
  const IBoot_vtbl *vptr;
};


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IBootInit(IBoot *_this) {
  return _this->vptr->Init(_this);
}

SYS_DEFINE_STATIC_INLINE
boolean_t IBootCheckDFUTrigger(IBoot *_this) {
  return _this->vptr->CheckDFUTrigger(_this);
}

SYS_DEFINE_STATIC_INLINE
uint32_t IBootGetAppAdderss(IBoot *_this) {
  return _this->vptr->GetAppAdderss(_this);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IBootOnJampToApp(IBoot *_this, uint32_t nAppDress) {
  return _this->vptr->OnJampToApp(_this, nAppDress);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_IBOOTVTBL_H_ */
