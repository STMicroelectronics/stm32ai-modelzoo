/**
 ******************************************************************************
 * @file    ISensorEventListener.h
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *                             
 *
 ******************************************************************************
 */
#ifndef INCLUDE_EVENTS_ISENSOREVENTLISTENER_H_

#define INCLUDE_EVENTS_ISENSOREVENTLISTENER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/IEventListener.h"
#include "events/IEventListener_vtbl.h"
#include "events/SensorEvent.h"
#include "ai_sp_dataformat.h"


/**
 * Create  type name for _ISensorEventListener.
 */
typedef struct _ISensorEventListener ISensorEventListener;


// Public API declaration
//***********************

/**
 * Called by the a sensor ::IEventSrc when new data are ready.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
inline sys_error_code_t ISensorEventListenerOnNewDataReady(IEventListener *_this, const SensorEvent *pxEvt);


// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_ISENSOREVENTLISTENER_H_ */
