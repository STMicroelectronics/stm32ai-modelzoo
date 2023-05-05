/**
 ******************************************************************************
 * @file    IEventListener.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Apr 6, 2017
 *
 * @brief   Event Listener Interface
 *
 * A tagging interface that all event listener interfaces must extend.
 * Each listener is could be linked to only one owner. The owner is an
 * application specific object.
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
#ifndef INCLUDE_EVENTS_IEVENTLISTENER_H_
#define INCLUDE_EVENTS_IEVENTLISTENER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "events/IListener.h"
#include "events/IListener_vtbl.h"

/**
 * Create  type name for _IEventListener.
 */
typedef struct _IEventListener IEventListener;


// Public API declaration
//***********************

/**
 * Set the owner of the listener.
 *
 * @param this [IN] specifies a pointer to an ::IEventListener object.
 * @param pxOwner [IN] specifies a pointer to an application specific object that become the owner of the listenr.
 */
static inline void IEventListenerSetOwner(IEventListener *this, void *pxOwner);

/**
 * Get the pointer to the listener's owner.
 *
 * @param this [IN] specifies a pointer to an ::IEventListener object.
 */
static inline void *IEventListenerGetOwner(IEventListener *this);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_IEVENTLISTENER_H_ */
