/**
 ******************************************************************************
 * @file    IDataEventListener_vtbl.h
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
#ifndef EMDATA_INC_EVENTS_IDATAEVENTLISTENER_VTBL_H_
#define EMDATA_INC_EVENTS_IDATAEVENTLISTENER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/IEventListener_vtbl.h"


/**
 * Create  type name for _IDataEventListener_vtbl.
 */
typedef struct _IDataEventListener_vtbl IDataEventListener_vtbl;


/**
 * Specifies the virtual table for the  class.
 */
struct _IDataEventListener_vtbl {
  sys_error_code_t (*OnStatusChange)(IListener *_this);                                   ///< @sa IListenerOnStatusChange
  void (*SetOwner)(IEventListener *_this, void *p_owner);                                 ///< @sa IEventListenerSetOwner
  void *(*GetOwner)(IEventListener *_this);                                               ///< @sa IEventListenerGetOwner
  sys_error_code_t (*OnNewDataReady)(IEventListener *_this, const DataEvent_t *p_evt);      ///< @sa IDataEventListenerOnNewDataReady
};

/**
 * _IDataEventListener interface internal state.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _IDataEventListener {
  /**
   * Pointer to the virtual table for the class.
   */
  const IDataEventListener_vtbl *vptr;
};


/* Inline functions definition */
/*******************************/

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IDataEventListenerOnNewDataReady(IEventListener *_this, const DataEvent_t *p_evt) {
  assert_param(_this != NULL);

  return ((IDataEventListener_t*)_this)->vptr->OnNewDataReady(_this, p_evt);
}


#ifdef __cplusplus
}
#endif

#endif /* EMDATA_INC_EVENTS_IDATAEVENTLISTENER_VTBL_H_ */
