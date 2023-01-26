/**
 ******************************************************************************
 * @file    ISensor.c
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
 
#include "ISensor.h"
#include "ISensor_vtbl.h"


// GCC requires one function forward declaration in only one .c source
// in order to manage the inline.
// See also http://stackoverflow.com/questions/26503235/c-inline-function-and-gcc
#if defined (__GNUC__)
extern sys_error_code_t ISensorStart(ISensor_t *_this);
extern sys_error_code_t ISensorStop(ISensor_t *_this);
extern sys_error_code_t ISensorSetODR(ISensor_t *_this, float ODR);
extern sys_error_code_t ISensorSetFS(ISensor_t *_this, float FS);
extern sys_error_code_t ISensorEnable(ISensor_t *_this);
extern sys_error_code_t ISensorDisable(ISensor_t *_this);
extern boolean_t ISensorIsEnabled(ISensor_t *_this);
extern SensorDescriptor_t ISensorGetDescription(ISensor_t *_this);
extern SensorStatus_t ISensorGetStatus(ISensor_t *_this);
#endif
