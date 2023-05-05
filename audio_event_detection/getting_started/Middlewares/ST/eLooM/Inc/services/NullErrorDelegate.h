/**
 ******************************************************************************
 * @file    NullErrorDelegate.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Nov 14, 2017
 *
 * @brief   Empty implementation of the IApplicationErrorDelegate IF
 *
 * When installed this delegate disable the error managment subsystem.
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
#ifndef INCLUDE_SERVICES_NULLERRORDELEGATE_H_
#define INCLUDE_SERVICES_NULLERRORDELEGATE_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "IApplicationErrorDelegate.h"
#include "IApplicationErrorDelegateVtbl.h"

/**
 * Create a type name for _NuLLErrorDelegate
 */
typedef struct _NuLLErrorDelegate NullErrorDelegate;

/**
 * Define the NULL error manager delegate. It does not implement any error management.
 */
struct _NuLLErrorDelegate {
  /**
   * Base class object.
   */
  IApplicationErrorDelegate super;
};



// Public API declaration
//***********************

/**
 * Allocate an instance of ::NullErrorDelegate.
 * Initialize the object virtual table.
 *
 * @return
 */
IApplicationErrorDelegate *NullAEDAlloc(void);

static inline
void NullAEDResetCounter(IApplicationErrorDelegate *this);

static inline
uint8_t NullAEDGetMaxFirstResponderPriority(const IApplicationErrorDelegate *_this);

static inline
sys_error_code_t NullAEDRemoveFirstResponder(IApplicationErrorDelegate *_this, IErrFirstResponder *pFirstResponder);

static inline
sys_error_code_t NullAEDAddFirstResponder(IApplicationErrorDelegate *_this, IErrFirstResponder *pFirstResponder, uint8_t nPriority);

static inline
boolean_t NullAEDIsLastErrorPending(IApplicationErrorDelegate *_this);

static inline
sys_error_code_t NullAEDOnNewErrEvent(IApplicationErrorDelegate *_this, SysEvent xEvent);

static inline
sys_error_code_t NullAEDProcessEvent(IApplicationErrorDelegate *_this, ApplicationContext *pxContext, SysEvent xEvent);

static inline
sys_error_code_t NullAEDOnStartApplication(IApplicationErrorDelegate *_this, ApplicationContext *pxContext);

static inline
sys_error_code_t NullAEDInit(IApplicationErrorDelegate *_this, void *pParams);


/* Inline functions definition */
/*******************************/

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDInit
 */
static inline
sys_error_code_t NullAEDInit(IApplicationErrorDelegate *_this, void *pParams) {
  UNUSED(_this);
  UNUSED(pParams);
  return SYS_NO_ERROR_CODE;
}

/**
 * Default implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDOnStartApplication
 */
static inline
sys_error_code_t NullAEDOnStartApplication(IApplicationErrorDelegate *_this, ApplicationContext *pxContext) {
  UNUSED(_this);
  UNUSED(pxContext);
  return SYS_NO_ERROR_CODE;
}

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDProcessEvent
 */
static inline
sys_error_code_t NullAEDProcessEvent(IApplicationErrorDelegate *_this, ApplicationContext *pxContext, SysEvent xEvent) {
  UNUSED(_this);
  UNUSED(pxContext);
  UNUSED(xEvent);
  return SYS_NO_ERROR_CODE;
}

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDOnNewErrEvent
 */

static inline
sys_error_code_t NullAEDOnNewErrEvent(IApplicationErrorDelegate *_this, SysEvent xEvent) {
  UNUSED(_this);
  UNUSED(xEvent);
  return SYS_NO_ERROR_CODE;
}

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDIsLastErrorPending
 */
static inline
boolean_t NullAEDIsLastErrorPending(IApplicationErrorDelegate *_this) {
  UNUSED(_this);
  return FALSE;
}

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDAddFirstResponder
 */
static inline
sys_error_code_t NullAEDAddFirstResponder(IApplicationErrorDelegate *_this, IErrFirstResponder *pFirstResponder, uint8_t nPriority) {
  UNUSED(_this);
  UNUSED(pFirstResponder);
  UNUSED(nPriority);
  return SYS_NO_ERROR_CODE;
}

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDRemoveFirstResponder
 */
static inline
sys_error_code_t NullAEDRemoveFirstResponder(IApplicationErrorDelegate *_this, IErrFirstResponder *pFirstResponder) {
  UNUSED(_this);
  UNUSED(pFirstResponder);
  return SYS_NO_ERROR_CODE;
}

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDGetMaxFirstResponderPriority
 */
static inline
uint8_t NullAEDGetMaxFirstResponderPriority(const IApplicationErrorDelegate *_this) {
  UNUSED(_this);
  return 0;
}

/**
 * Null implementation of the IApplicationErrorDelegate. It does no error management.
 * @sa IAEDResetCounter
 */
static inline
void NullAEDResetCounter(IApplicationErrorDelegate *_this) {
  UNUSED(_this);
};


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_NULLERRORDELEGATE_H_ */
