/**
 ******************************************************************************
 * @file    IListener.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Jan 6, 2017
 *
 * @brief   Generic Listener interface
 *
 * This interface is the base class for the Listener hierarchy. A Listener
 * is an object that can be notified about a status change.
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

#ifndef INCLUDE_EVENTS_ILISTENER_H_
#define INCLUDE_EVENTS_ILISTENER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "services/systypes.h"
#include "services/syserror.h"

typedef struct _IListener IListener;


// Public API declaration
//***********************


static inline sys_error_code_t IListenerOnStatusChange(IListener *this);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif


#endif /* INCLUDE_EVENTS_ILISTENER_H_ */
