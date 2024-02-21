/**
 ******************************************************************************
 * @file    IIODriver_vtbl.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Aug 6, 2019
 *
 * @brief   Private API for the I/O Driver Interface
 *
 * This header file must be included included in all source files that use the
 * IIODriver public API.
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2017 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_DRIVERS_IIODRIVER_VTBL_H_
#define INCLUDE_DRIVERS_IIODRIVER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "IDriver_vtbl.h"

typedef struct _IIODriver_vtbl IIODriver_vtbl;

struct _IIODriver_vtbl {
  sys_error_code_t (*Init)(IDriver *_this, void *pParams);
  sys_error_code_t (*Start)(IDriver *_this);
  sys_error_code_t (*Stop)(IDriver *_this);
  sys_error_code_t (*DoEnterPowerMode)(IDriver *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);
  sys_error_code_t (*Reset)(IDriver *_this, void *pParams);
  sys_error_code_t (*Write)(IIODriver *_this, uint8_t *pDataBuffer, uint16_t nDataSize, uint16_t nChannel);
  sys_error_code_t (*Read)(IIODriver *_this, uint8_t *pDataBuffer, uint16_t nDataSize, uint16_t nChannel);
};

/**
 * IDriver interface internal state. This is the base interface for the the driver subsystem.
 * It declares only the virtual table used to implement the inheritance.
 */
struct _IIODriver {
  const IIODriver_vtbl *vptr;
};


// Inline function definition.
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IIODrvWrite(IIODriver *_this, uint8_t *pDataBuffer, uint16_t nDataSize, uint16_t nChannel) {
  return _this->vptr->Write(_this, pDataBuffer, nDataSize, nChannel);
}

SYS_DEFINE_STATIC_INLINE
sys_error_code_t IIODrvRead(IIODriver *_this, uint8_t *pDataBuffer, uint16_t nDataSize, uint16_t nChannel) {
  return _this->vptr->Read(_this, pDataBuffer, nDataSize, nChannel);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_DRIVERS_IIODRIVER_VTBL_H_ */
