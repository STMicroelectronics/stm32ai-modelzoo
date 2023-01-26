/**
 ******************************************************************************
 * @file    SensorEvent.c
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief  SensorEvent class definition.
 *
 * This file is needed only for GCC compiler in DEBUG configuration.
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

#include "events/SensorEvent.h"

// Public API implementation.
// **************************

// GCC requires one function forward declaration in only one .c source
// in order to manage the inline.
// See also http://stackoverflow.com/questions/26503235/c-inline-function-and-gcc
#if defined (__GNUC__) || defined (__ICCARM__)
extern sys_error_code_t SensorEventInit(IEvent *_this, const IEventSrc *pSource, const ai_logging_packet_t   *stream, double fTimeStamp, uint16_t nSensorID);
#endif
