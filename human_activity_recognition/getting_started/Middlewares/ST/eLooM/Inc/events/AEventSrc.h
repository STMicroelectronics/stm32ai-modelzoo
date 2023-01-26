/**
 ******************************************************************************
 * @file    AEventSrc.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 3.0.0
 * @date    Jul 13, 2020
 *
 * @brief   Generic implementation of the ::IEventSrc interface.
 *
 * Generic abstract implementation of the ::IEventSrc interface.
 * The ::IEventListener objects are managed with an array of fixed size.
 * This class must be extended in order to define the
 * IEventSrcSendEvent() method.
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2020 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_EVENTS_AEVENTSRC_H_
#define INCLUDE_EVENTS_AEVENTSRC_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/IEventSrc.h"
#include "events/IEventSrc_vtbl.h"
#include "services/systp.h"


#ifndef AEVENT_SRC_CFG_MAX_LISTENERS
#define AEVENT_SRC_CFG_MAX_LISTENERS         2U
#endif


/**
 * Create  type name for _AEventSrc.
 */
typedef struct _AEventSrc AEventSrc;

/**
 * AEventSrc internal state.
 */
struct _AEventSrc {
  IEventSrc super;

  /**
   * Set of IEventListener object.
   */
  IEventListener *m_pxListeners[AEVENT_SRC_CFG_MAX_LISTENERS];

  /**
   * Specifies the owner of the object.
   */
  void *m_pxOwner;
};


// Public API declaration
//***********************

/**
 * Set the owner of the event source object.
 * @param _this [IN] specifies a pointer to an ::AEventSrc object.
 * @param pxOwner [IN] specifies a pointer to an application specific object that become the owner of the event source.
 *
 * @return SYS_NO_ERROR_CODE
 */
sys_error_code_t AEvtSrcSetOwner(IEventSrc *_this, void *pxOwner);

/**
 * Get the pointer to the owner of the event source.
 * @param _this [IN] specifies a pointer to an ::AEventSrc object.
 */
void *AEvtSrcGetOwner(IEventSrc *_this);

// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_AEVENTSRC_H_ */
