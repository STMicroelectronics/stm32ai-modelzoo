/**
  ******************************************************************************
  * @file    IDPU_vtbl.h
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
  
#ifndef INCLUDE_IDPUVTBL_H_
#define INCLUDE_IDPUVTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "events/ProcessEvent.h"

/**
 * Create a type name for IDPU_vtbl.
 */
typedef struct _IDPU_vtbl IDPU_vtbl;


/**
 * Specifies the virtual table for the  class.
 */
struct _IDPU_vtbl {
  sys_error_code_t (*Init)(IDPU *_this);
  sys_error_code_t (*AttachToSensor)(IDPU *_this, ISourceObservable *s, void *buffer );
  sys_error_code_t (*DetachFromSensor)(IDPU *_this, ISourceObservable *s);
  sys_error_code_t (*AttachInputDPU)(IDPU *_this, IDPU *in_adpu, void *buffer );
  sys_error_code_t (*DetachFromDPU)(IDPU *_this);
  sys_error_code_t (*DispatchEvents)(IDPU *_this,  ProcessEvent *pxEvt);
  sys_error_code_t (*RegisterNotifyCallback)(IDPU *_this, DPU_ReadyToProcessCallback_t callback, void *p_param);
  sys_error_code_t (*Process)(IDPU *_this);
};

struct _IDPU{
  /**
   * Pointer to the virtual table for the class.
   */
  const IDPU_vtbl *vptr;
};


// Inline functions definition
// ***************************
inline sys_error_code_t IDPU_Init(IDPU *_this) {
  return _this->vptr->Init(_this );
}

inline sys_error_code_t IDPU_AttachToSensor(IDPU *_this, ISourceObservable *s, void *buffer) {
  return _this->vptr->AttachToSensor(_this, s, buffer );
}

inline sys_error_code_t IDPU_DetachFromSensor(IDPU *_this, ISourceObservable *s)  {
  return _this->vptr->DetachFromSensor(_this, s );
}

inline sys_error_code_t IDPU_AttachInputDPU(IDPU *_this, IDPU *in_adpu, void *buffer) {
  return _this->vptr->AttachInputDPU(_this, in_adpu, buffer );
}

inline sys_error_code_t IDPU_DetachFromDPU(IDPU *_this) {
  return _this->vptr->DetachFromDPU(_this);
}

inline sys_error_code_t IDPU_DispatchEvents(IDPU *_this,  ProcessEvent *pxEvt) {
  return _this->vptr->DispatchEvents(_this, pxEvt );
}

inline sys_error_code_t IDPU_RegisterNotifyCallback(IDPU *_this, DPU_ReadyToProcessCallback_t callback, void *p_param) {
  return _this->vptr->RegisterNotifyCallback(_this, callback, p_param);
}

inline sys_error_code_t IDPU_Process(IDPU *_this) {
  return _this->vptr->Process(_this );
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_IDPUVTBL_H_ */
