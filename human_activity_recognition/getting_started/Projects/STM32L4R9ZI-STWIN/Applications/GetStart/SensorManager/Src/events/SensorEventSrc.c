/**
 ******************************************************************************
 * @file    SensorEventSrc.c
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


#include "events/SensorEventSrc.h"
#include "events/SensorEventSrc_vtbl.h"
#include "events/ISensorEventListener.h"
#include "events/ISensorEventListener_vtbl.h"


static const IEventSrc_vtbl s_xSensorEvent_vtbl = {
    AEventSrv_vtblInit,
    AEventSrv_vtblAddEventListener,
    AEventSrv_vtblRemoveEventListener,
    AEventSrv_vtblGetMaxListenerCount,
    SensorEventSrc_vtblSendEvent
};

/**
 * SensorEventSrc internal state.
 */
struct _SensorEventSrc {
  /**
   * Base class object.
   */
  AEventSrc super;
};


// Public functions definition
// ***************************

IEventSrc *SensorEventSrcAlloc() {
  IEventSrc *pxObj = (IEventSrc*) pvPortMalloc(sizeof(SensorEventSrc));

  if (pxObj != NULL) {
    pxObj->vptr = &s_xSensorEvent_vtbl;
  }

  return pxObj;
}


// IEventSoruce virtual functions definition.
// ******************************************

sys_error_code_t SensorEventSrc_vtblSendEvent(const IEventSrc *_this, const IEvent *pxEvent, void *pvParams) {
  assert_param(_this);
  SensorEventSrc *pObj = (SensorEventSrc*)_this;
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  UNUSED(pvParams);

  for (uint8_t i=0; i<AEVENT_SRC_CFG_MAX_LISTENERS; ++i) {
    if (pObj->super.m_pxListeners[i] != NULL) {
      ISensorEventListenerOnNewDataReady(pObj->super.m_pxListeners[i], (SensorEvent*)pxEvent);
    }
  }

  return xRes;
}


