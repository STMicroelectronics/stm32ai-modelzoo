/**
  ******************************************************************************
  * @file    SensorEventSrc.h
  * @author  SRA - MCD
  * @brief   Extend the abstract ::AEventSrc class.
  * ::IEventSrc class specialized for the ::SensorEvent.
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
  
#ifndef INCLUDE_EVENTS_SENSOREVENTSRC_H_
#define INCLUDE_EVENTS_SENSOREVENTSRC_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/AEventSrc.h"
#include "events/AEventSrc_vtbl.h"


/**
 * Create  type name for _SensorEventSrc.
 */
typedef struct _ProcessEventSrc ProcessEventSrc;


// Public API declaration
//***********************

/**
 * Allocate an instance of SensorEventSrc.
 *
 * @return a pointer to the generic object ::IEventSrc if success,
 * or NULL if out of memory error occurs.
 */
IEventSrc *ProcessEventSrcAlloc(void);
uint32_t ProcessEventSrcGetTag(const ProcessEventSrc *_this);
sys_error_code_t ProcessEventSrcSetTag(ProcessEventSrc *_this, uint32_t tag);

// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_SENSOREVENTSRC_H_ */
