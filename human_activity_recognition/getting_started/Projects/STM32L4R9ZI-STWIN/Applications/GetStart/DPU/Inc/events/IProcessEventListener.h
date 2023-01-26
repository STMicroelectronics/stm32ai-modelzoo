/**
  ******************************************************************************
  * @file    IProcessEventListener.h
  * @author  SRA - MCD
  * @brief
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
 
#ifndef INCLUDE_EVENTS_IPROCESSEVENTLISTENER_H_
#define INCLUDE_EVENTS_IPROCESSEVENTLISTENER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/IEventListener.h"
#include "events/IEventListener_vtbl.h"
#include "events/ProcessEvent.h"


/**
 * Create  type name for _ISensorEventListener.
 */
typedef struct _IProcessEventListener IProcessEventListener;


// Public API declaration
//***********************

/**
 * Called by the a sensor ::IEventSrc when new data are ready.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t IProcessEventListenerOnProcessedDataReady(IEventListener *_this, const ProcessEvent *pxEvt);
                        

// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_IPROCESSEVENTLISTENER_H_ */
