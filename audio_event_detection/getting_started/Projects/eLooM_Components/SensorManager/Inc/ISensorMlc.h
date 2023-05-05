/**
  ******************************************************************************
  * @file    ISensorMlc.h
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

#ifndef INCLUDE_ISENSORMLC_H_
#define INCLUDE_ISENSORMLC_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/systypes.h"
#include "services/syserror.h"
#include "services/systp.h"
#include "SensorDef.h"

/**
  * Create  type name for ISensorMlc.
  */
typedef struct _ISensorMlc_t ISensorMlc_t;

// Public API declaration
//***********************
/** Public interface **/
static inline sys_error_code_t ISensorMlcLoadUcf(ISensorMlc_t *_this, uint32_t size, const char *ucf);
static inline boolean_t ISensorMlcIsEnabled(ISensorMlc_t *_this);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_ISENSORMLC_H_ */
