/**
  ******************************************************************************
  * @file    IBus_vtbl.h
  * @author  SRA - MCD
  * @brief
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file in
  * the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  *
  ******************************************************************************
  */
#ifndef IBUS_VTBL_H_
#define IBUS_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"

/**
  * Declare a type name for the struct _IBus_vtbl
  */
typedef struct _IBus_vtbl IBus_vtbl;

/**
  * Virtual table for the interface ::IBus
  */
struct _IBus_vtbl
{
  sys_error_code_t (*Ctrl)(IBus *_this, EBusCtrlCmd eCtrlCmd, uint32_t nParams);
  sys_error_code_t (*ConnectDevice)(IBus *_this, ABusIF *pxBusIF);
  sys_error_code_t (*DisconnectDevice)(IBus *_this, ABusIF *pxBusIF);
};

/**
  * IBus interface internal state. This is the base interface for the the Bus subsystem.
  * It declares only the virtual table used to implement the polymorphism.
  */
struct _IBus
{
  const IBus_vtbl *vptr;
};


// Inline function definition.
// ***************************

SYS_DEFINE_INLINE
sys_error_code_t IBusCtrl(IBus *_this, EBusCtrlCmd eCtrlCmd, uint32_t nParams)
{
  return _this->vptr->Ctrl(_this, eCtrlCmd, nParams);
}

SYS_DEFINE_INLINE
sys_error_code_t IBusConnectDevice(IBus *_this, ABusIF *pxBusIF)
{
  return _this->vptr->ConnectDevice(_this, pxBusIF);
}

SYS_DEFINE_INLINE
sys_error_code_t IBusDisconnectDevice(IBus *_this, ABusIF *pxBusIF)
{
  return _this->vptr->DisconnectDevice(_this, pxBusIF);
}


#ifdef __cplusplus
}
#endif

#endif /* IBUS_VTBL_H_ */
