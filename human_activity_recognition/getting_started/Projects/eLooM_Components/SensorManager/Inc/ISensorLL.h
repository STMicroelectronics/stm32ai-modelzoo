/**
  ******************************************************************************
  * @file    ISensorLL.h
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

#ifndef INCLUDE_ISENSORLL_H_
#define INCLUDE_ISENSORLL_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"
#include "SensorDef.h"

/**
  * Create  type name for ISensorLL.
  */
typedef struct _ISensorLL_t ISensorLL_t;

// Public API declaration
//***********************
/** Public interface **/
static inline sys_error_code_t ISensorReadReg(ISensorLL_t *_this, uint16_t reg, uint8_t *data, uint16_t len);
static inline sys_error_code_t ISensorWriteReg(ISensorLL_t *_this, uint16_t reg, const uint8_t *data, uint16_t len);
static inline sys_error_code_t ISensorSyncModel(ISensorLL_t *_this);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSORLL_H_ */
