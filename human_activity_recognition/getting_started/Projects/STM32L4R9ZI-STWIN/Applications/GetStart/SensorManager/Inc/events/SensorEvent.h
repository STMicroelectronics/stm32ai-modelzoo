/**
 ******************************************************************************
 * @file    SensorEvent.h
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
#ifndef INCLUDE_EVENTS_SENSOREVENT_H_
#define INCLUDE_EVENTS_ISENSOREVENT_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "events/IEvent.h"
#include "features_extraction_if.h"


/**
 * Create  type name for _SensorEvent.
 */
typedef struct _SensorEvent SensorEvent;

/**
 * Specifies a generic Event. Each event has a pointer to the ::IEventSrc object
 * that has generated the event.
 */
struct _SensorEvent {
    /**
     * Specifies a pointer to the Event Source that generated the event.
     */
    IEvent super;
    
    /**
     * Specify the sensor data normalized according to the internal data format.
     * Size of the pData buffer.
     */
    const ai_logging_packet_t   *stream;

    /**
     * Timestamp
     */
    double fTimeStamp;

    /**
     * Specifies the sensor ID.
     */
    uint16_t nSensorID;
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
 * @param nSubSensorID [IN] specifies the ID of the subsensor.
 * @return SYS_NO_ERROR_CODE if success, an error code otherwise.
 */
static inline sys_error_code_t SensorEventInit(IEvent *_this, const IEventSrc *pSource, const ai_logging_packet_t   *stream, double fTimeStamp, uint16_t nSensorID);


// Inline functions definition
// ***************************

SYS_DEFINE_STATIC_INLINE
sys_error_code_t SensorEventInit(IEvent *_this, const IEventSrc *pSource, const ai_logging_packet_t   *stream, double fTimeStamp, uint16_t nSensorID) {
  assert_param(_this);
  SensorEvent *pObj = (SensorEvent*)_this;

  IEventInit(_this, pSource);
  pObj->stream = stream;
  pObj->fTimeStamp = fTimeStamp;
  pObj->nSensorID = nSensorID;

  return SYS_NO_ERROR_CODE;
}

#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_EVENTS_SENSOREVENT_H_ */
