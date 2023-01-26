/**
  ******************************************************************************
  * @file    SensorEventSrc.c
  * @author  SRA - MCD
  * @brief
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


#include "events/ProcessEventSrc.h"
#include "events/ProcessEventSrc_vtbl.h"
#include "events/IProcessEventListener.h"
#include "events/IProcessEventListener_vtbl.h"
#include "FreeRTOS.h"


static const IEventSrc_vtbl s_xProcessEvent_vtbl = {
    AEventSrv_vtblInit,
    AEventSrv_vtblAddEventListener,
    AEventSrv_vtblRemoveEventListener,
    AEventSrv_vtblGetMaxListenerCount,
    ProcessEventSrc_vtblSendEvent
};

/**
 * SensorEventSrc internal state.
 */
struct _ProcessEventSrc {
  /**
   * Base class object.
   */
  AEventSrc super;
  uint32_t tag;
};


// Public functions definition
// ***************************

IEventSrc *ProcessEventSrcAlloc() {
  IEventSrc *pxObj = (IEventSrc*) pvPortMalloc(sizeof(ProcessEventSrc));

  if (pxObj != NULL) {
    pxObj->vptr = &s_xProcessEvent_vtbl;
  }

  return pxObj;
}

sys_error_code_t ProcessEventSrcSetTag(ProcessEventSrc *_this, uint32_t tag)
{
  assert_param(_this != NULL);
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;

  _this->tag = tag;
  return xRes;
}

uint32_t ProcessEventSrcGetTag(const ProcessEventSrc *_this)
{
  assert_param(_this != NULL);

  return _this->tag;
}




// IEventSoruce virtual functions definition.
// ******************************************

sys_error_code_t ProcessEventSrc_vtblSendEvent(const IEventSrc *_this, const IEvent *pxEvent, void *pvParams) {
  assert_param(_this != NULL);
  ProcessEventSrc *pObj = (ProcessEventSrc*)_this;
  sys_error_code_t xRes = SYS_NO_ERROR_CODE;
  UNUSED(pvParams);

  for (uint8_t i=0; i<AEVENT_SRC_CFG_MAX_LISTENERS; ++i) {
    if (pObj->super.m_pxListeners[i] != NULL) {
      IProcessEventListenerOnProcessedDataReady(pObj->super.m_pxListeners[i], (ProcessEvent*)pxEvent);
    }
  }

  return xRes;
}


