/**
 ******************************************************************************
 * @file    IErrorFirstResponderVtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Aug 11, 2017
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
#ifndef INCLUDE_SERVICES_IERRORFIRSTRESPONDERVTBL_H_
#define INCLUDE_SERVICES_IERRORFIRSTRESPONDERVTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "IErrorFirstResponder.h"
#include "systp.h"

/**
 * Create  type name for _IErrFirstResponder.
 */
typedef struct _IErrFirstResponder_vtbl IErrFirstResponder_vtbl;

/**
 * IErrFirstResponder virtual table. This table define all the functions
 * that a subclass must overload.
 */
struct _IErrFirstResponder_vtbl {
	void (*SetOwner)(IErrFirstResponder *_this, void *pxOwner);  ///< @sa IErrFirstResponderSetOwner
	void *(*GetOwner)(IErrFirstResponder *_this);  ///< @sa IErrFirstResponderGetOwner
	sys_error_code_t (*NewError)(IErrFirstResponder *_this, SysEvent xError, boolean_t bIsCalledFromISR);  ///< @sa IErrFirstResponderNewError
};

/**
 * IErrFirstResponder interface definition.
 */
struct _IErrFirstResponder {
	/**
	 * Pointer to the class virtual table.
	 */
	const IErrFirstResponder_vtbl *vptr;
};


// Public API declaration
//***********************


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
void IErrFirstResponderSetOwner(IErrFirstResponder *_this, void *pxOwner) {
	_this->vptr->SetOwner(_this, pxOwner);
}

SYS_DEFINE_STATIC_INLINE
void *IErrFirstResponderGetOwner(IErrFirstResponder *_this) {
	return _this->vptr->GetOwner(_this);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IErrorFirstResponderNewError(IErrFirstResponder *_this, SysEvent xError, boolean_t bIsCalledFromISR) {
	return _this->vptr->NewError(_this, xError, bIsCalledFromISR);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_IERRORFIRSTRESPONDERVTBL_H_ */
