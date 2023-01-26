/**
  ******************************************************************************
  * @file    IProcessEventListener_vtbl.h
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
  
#ifndef INCLUDE_EVENTS_IPROCESSEVENTLISTENER_VTBL_H_
#define INCLUDE_EVENTS_IPROCESSEVENTLISTENER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/IEventListener_vtbl.h"


/**
 * Create  type name for _ISensorEventListener_vtbl.
 */
typedef struct _IProcessEventListener_vtbl IProcessEventListener_vtbl;


/**
 * Specifies the virtual table for the  class.
 */
struct _IProcessEventListener_vtbl {
  sys_error_code_t (*OnStatusChange)(IListener *this);                                   ///< @sa IListenerOnStatusChange
  void (*SetOwner)(IEventListener *this, void *pxOwner);                                 ///< @sa IEventListenerSetOwner
  void *(*GetOwner)(IEventListener *this);                                               ///< @sa IEventListenerGetOwner
  sys_error_code_t (*OnProcessedDataReady)(IEventListener *_this, const ProcessEvent *pxEvt);   ///< @sa ISensorEventListenerOnNewDataReady
};

/**
 * _ISensorEventListener interface internal state.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _IProcessEventListener {
  /**
   * Pointer to the virtual table for the class.
   */
  const IProcessEventListener_vtbl *vptr;
};


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IProcessEventListenerOnProcessedDataReady(IEventListener *_this, const ProcessEvent *pxEvt) {
  assert_param(_this);

  return ((IProcessEventListener*)_this)->vptr->OnProcessedDataReady(_this, pxEvt);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_IPROCESSEVENTLISTENER_VTBL_H_ */
