/**
 ******************************************************************************
 * @file    ProcessEvent.h
 * @author  SRA - MCD
 * @version 1.0.0
 * @date    6-Sep-2021
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
 * All rights reserved.</center></h2>
 *
 * This software component is licensed by ST under ODE SOFTWARE LICENSE AGREEMENT
 * SLA0094, the "License"; You may not use this file except in compliance with
 * the License. You may obtain a copy of the License at:
 *                             www.st.com/SLA0094
 *
 ******************************************************************************
 */
 
#ifndef INCLUDE_EVENTS_IPROCESSEVENT_H_
#define INCLUDE_EVENTS_IPROCESSEVENT_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/IEvent.h"
#include "features_extraction_if.h"


/**
 * Create  type name for _ProcessEvent.
 */
typedef struct _ProcessEvent ProcessEvent;

/**
 * Specifies a generic Event. Each event has a pointer to the ::IEventSrc object
 * that has generated the event.
 */
struct _ProcessEvent {
    /**
     * Specifies a pointer to the Event Source that generated the event.
     */
    IEvent super;

    ai_logging_packet_t   *stream;

    uint32_t tag;
};


// Public API declaration
//***********************

/**
 * Initialize the interface ISensorEvent. It should be called after the object allocation and before using the object.
 *
 * @param _this [IN] specifies a pointer to the object.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */

/**
 *
 * @param _this [IN] Initialize the interface ISensorEvent. It should be called after the object allocation and before using the object.
 * @param pSource [IN] specifies the source of the event.
 * @param pData [IN] specifies the buffer containing the raw data form the sensor.
 * @param nDataSize [IN] specifies the size in byt of the data coming from the sensor.
 * @param fTimeStamp [IN] specifies the timestamp of the data.
 * @param nSensorID [IN] specifies the ID of the sensor in the sensor DB.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t ProcessEventInit(IEvent *_this, const IEventSrc *pSource,  ai_logging_packet_t   *stream, uint32_t tag);



// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t ProcessEventInit(IEvent *_this, const IEventSrc *pSource,  ai_logging_packet_t   *stream, uint32_t tag) {
  assert_param(_this);
  ProcessEvent *pObj = (ProcessEvent*)_this;

  IEventInit(_this, pSource);
  pObj->stream = stream;
  pObj->tag = tag;

  return SYS_NO_ERROR_CODE;
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_IPROCESSEVENT_H_ */
