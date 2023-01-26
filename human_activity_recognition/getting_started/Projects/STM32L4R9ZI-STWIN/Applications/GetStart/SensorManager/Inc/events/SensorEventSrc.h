/**
 ******************************************************************************
 * @file    SensorEventSrc.h
 * @author  SRA - MCD
 * @version 1.1.0
 * @date    10-Dec-2021
 *
 * @brief   Extend the abstract ::AEventSrc class.
 *
 * ::IEventSrc class specialized for the ::SensorEvent.
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
#ifndef INCLUDE_EVENTS_SENSOREVENTSRC_H_
#define INCLUDE_EVENTS_SENSOREVENTSRC_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/AEventSrc.h"
#include "events/AEventSrc_vtbl.h"
#include "FreeRTOS.h"


/**
 * Create  type name for _SensorEventSrc.
 */
typedef struct _SensorEventSrc SensorEventSrc;


// Public API declaration
//***********************

/**
 * Allocate an instance of SensorEventSrc.
 *
 * @return a pointer to the generic object ::IEventSrc if success,
 * or NULL if out of memory error occurs.
 */
IEventSrc *SensorEventSrcAlloc(void);

/**
 * Deallocate an instance of SensorEventSrc.
 *
 */
static inline void SensorEventSrcFree(IEventSrc *pxObj);

// Inline functions definition
// ***************************

static inline
void SensorEventSrcFree(IEventSrc *pxObj) {

  /* kernel deallocator already check for a NULL pointer. */
  vPortFree(pxObj);
}


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_SENSOREVENTSRC_H_ */
