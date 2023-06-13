/**
 ******************************************************************************
 * @file    IDataEventListener.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version M.m.b
 * @date    May 13, 2022
 *
 * @brief
 *
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2022 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef EMDATA_INC_EVENTS_IDATAEVENTLISTENER_H_
#define EMDATA_INC_EVENTS_IDATAEVENTLISTENER_H_

#include "events/IEventListener.h"
#include "events/IEventListener_vtbl.h"
#include "events/DataEvent.h"


/**
 * Create  type name for _IDataEventListener.
 */
typedef struct _IDataEventListener IDataEventListener_t;


/* Public API declaration */
/**************************/

/**
 * Called by the a sensor ::IEventSrc when new data are ready.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @param p_evt [IN] specifies a pointer to the event.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline
sys_error_code_t IDataEventListenerOnNewDataReady(IEventListener *_this, const DataEvent_t *p_evt);


/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif


#endif /* EMDATA_INC_EVENTS_IDATAEVENTLISTENER_H_ */
