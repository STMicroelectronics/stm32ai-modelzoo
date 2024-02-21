/**
 ******************************************************************************
 * @file    IEventSrc_vtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Apr 6, 2017
 *
 * @brief   Definition of the IEventSrc virtual functions.
 *
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
#ifndef INCLUDE_EVENTS_IEVENTSRCVTBL_H_
#define INCLUDE_EVENTS_IEVENTSRCVTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"

typedef struct _IEventSrc_vtbl IEventSrc_vtbl;

/**
 * IEventSrc virtual table. This table define all the functions
 * that a subclass must overload.
 */
struct _IEventSrc_vtbl {
	sys_error_code_t (*Init)(IEventSrc *this);                                                      ///< @sa IEventSrcInit
	sys_error_code_t (*AddEventListener)(IEventSrc *this, IEventListener *pListener);               ///< @sa IEventSrcAddEventListener
	sys_error_code_t (*RemoveEventListener)(IEventSrc *this, IEventListener *pListener);            ///< @sa IEventSrcRemoveEventListener
	uint32_t (*GetMaxListenerCount)(const IEventSrc *this);                                         ///< @sa IEventSrcGetMaxListenerCount
	sys_error_code_t (*SendEvent)(const IEventSrc *this, const IEvent *pxEvent, void *pvParams);    ///< @sa IEventSrcSendEvent
};

/**
 * IEventSrc type definition.
 */
struct _IEventSrc {
	/**
	 * Pointer to the class virtual table.
	 */
	const IEventSrc_vtbl *vptr;
};


// Public API declaration
//***********************


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IEventSrcInit(IEventSrc *this) {
	return this->vptr->Init(this);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IEventSrcAddEventListener(IEventSrc *this, IEventListener *pListener) {
	return this->vptr->AddEventListener(this, pListener);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IEventSrcRemoveEventListener(IEventSrc *this, IEventListener *pListener) {
	return this->vptr->RemoveEventListener(this, pListener);
}

SYS_DEFINE_STATIC_INLINE
uint32_t IEventSrcGetMaxListenerCount(const IEventSrc *this) {
	return this->vptr->GetMaxListenerCount(this);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IEventSrcSendEvent(const IEventSrc *this, const IEvent *pxEvent, void *pvParams) {
	return this->vptr->SendEvent(this, pxEvent, pvParams);
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_IEVENTSRCVTBL_H_ */
