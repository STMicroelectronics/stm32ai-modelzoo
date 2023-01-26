/**
 ******************************************************************************
 * @file    ISensorEventListener_vtbl.h
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
#ifndef INCLUDE_EVENTS_ISENSOREVENTLISTENER_VTBL_H_
#define INCLUDE_EVENTS_ISENSOREVENTLISTENER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/IEventListener_vtbl.h"


/**
 * Create  type name for _ISensorEventListener_vtbl.
 */
typedef struct _ISensorEventListener_vtbl ISensorEventListener_vtbl;


/**
 * Specifies the virtual table for the  class.
 */
struct _ISensorEventListener_vtbl {
  sys_error_code_t (*OnStatusChange)(IListener *this);                                   ///< @sa IListenerOnStatusChange
  void (*SetOwner)(IEventListener *this, void *pxOwner);                                 ///< @sa IEventListenerSetOwner
  void *(*GetOwner)(IEventListener *this);                                               ///< @sa IEventListenerGetOwner
  sys_error_code_t (*OnNewDataReady)(IEventListener *_this, const SensorEvent *pxEvt);   ///< @sa ISensorEventListenerOnNewDataReady
};

/**
 * _ISensorEventListener interface internal state.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _ISensorEventListener {
  /**
   * Pointer to the virtual table for the class.
   */
  const ISensorEventListener_vtbl *vptr;
};


// Inline functions definition
// ***************************

SYS_DEFINE_INLINE
sys_error_code_t ISensorEventListenerOnNewDataReady(IEventListener *_this, const SensorEvent *pxEvt) {
  assert_param(_this);

  return ((ISensorEventListener*)_this)->vptr->OnNewDataReady(_this, pxEvt);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_ISENSOREVENTLISTENER_VTBL_H_ */
