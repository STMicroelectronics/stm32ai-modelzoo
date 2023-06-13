/**
 ******************************************************************************
 * @file    IEvent.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Apr 17, 2017
 *
 * @brief The root class from which all event state objects shall be derived.
 *
 * An event is an object that contains information about something that
 * happened in the system at a given moment. An event object is constructed
 * with a link to the EventSrc that has generated it.
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
#ifndef INCLUDE_EVENTS_IEVENT_H_
#define INCLUDE_EVENTS_IEVENT_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"

/**
 * Create  type name for _IEventSrc.
 */
typedef struct _IEventSrc IEventSrc;

/**
 * Create  type name for _IEvent.
 */
typedef struct _IEvent IEvent;

/**
 * Specifies a generic Event. Each event has a pointer to the ::IEventSrc object
 * that has generated the event.
 */
struct _IEvent {
	/**
	 * Specifies a pointer to the Event Source that generated the event.
	 */
	const IEventSrc *pSource;
};


// Public API declaration
//***********************

/**
 * Initialize an event. An is initialized when it is linked with the ::IEventSrc that has generated the event.
 *
 * @param this [IN] specifies an ::IEvent object
 * @param pSource [IN] specifies the ::IEventSrc object that has generated teh event.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IEventInit(IEvent *this, const IEventSrc *pSource);

// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IEventInit(IEvent *this, const IEventSrc *pSource) {
	this->pSource = pSource;

	return SYS_NO_ERROR_CODE;
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_IEVENT_H_ */
