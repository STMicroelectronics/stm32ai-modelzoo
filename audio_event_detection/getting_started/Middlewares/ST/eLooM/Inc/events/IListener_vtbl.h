/**
 ******************************************************************************
 * @file    IListener_vtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jan 6, 2017
 *
 * @brief   IListener virtual table definition.
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */

#ifndef INCLUDE_EVENTS_ILISTENERVTBL_H_
#define INCLUDE_EVENTS_ILISTENERVTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"

typedef struct _IListener_vtbl IListener_vtbl;


struct _IListener_vtbl {
	sys_error_code_t (*OnStatusChange)(IListener *this);
};

struct _IListener {
	const IListener_vtbl *vptr;
};

// Public API declaration
//***********************



// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IListenerOnStatusChange(IListener *this) {
	return this->vptr->OnStatusChange(this);
}

#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_EVENTS_ILISTENERVTBL_H_ */
