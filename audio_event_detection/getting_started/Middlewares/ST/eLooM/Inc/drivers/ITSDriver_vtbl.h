/**
 ******************************************************************************
 * @file    ITSDriver_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version 4.0.0
 * @date    Mar 15, 2022
 *
 * @brief   Private API for the Timestamp Driver Interface
 *
 * This header file must be included included in all source files that use the
 * ITSDriver public API.
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

#ifndef ELOOM_INC_DRIVERS_ITSDRIVER_VTBL_H_
#define ELOOM_INC_DRIVERS_ITSDRIVER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "IDriver_vtbl.h"

/**
 * Create  type name for _ITSDriver_vtbl.
 */
typedef struct _ITSDriver_vtbl ITSDriver_vtbl;

/**
 * Virtual table for the ITSDriver class.
 */
struct _ITSDriver_vtbl {
  sys_error_code_t (*Init)(IDriver *_this, void *pParams);
  sys_error_code_t (*Start)(IDriver *_this);
  sys_error_code_t (*Stop)(IDriver *_this);
  sys_error_code_t (*DoEnterPowerMode)(IDriver *_this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode);
  sys_error_code_t (*Reset)(IDriver *_this, void *pParams);
  uint64_t (*GetTimeStamp)(ITSDriver_t *_this);
};

/**
 *  ITSDriver_t interface internal state.
 */
struct _ITSDriver_t
{
  /**
   * Class virtual pointer.
   */
  const ITSDriver_vtbl *vptr;
};


/* Inline function definition. */
/*******************************/

SYS_DEFINE_STATIC_INLINE
uint64_t ITSDrvGetTimeStamp(ITSDriver_t *_this) {
  return _this->vptr->GetTimeStamp(_this);
}

#ifdef __cplusplus
}
#endif

#endif /* ELOOM_INC_DRIVERS_ITSDRIVER_VTBL_H_ */
