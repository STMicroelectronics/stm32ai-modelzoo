/**
  ******************************************************************************
  * @file    IMP34DT05Task.h
  * @author  SRA - MCD
  *
  * @date    30-Jul-2021
  *
  * @brief
  *
  *
  *
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
#ifndef IMP34DT05TASK_H_
#define IMP34DT05TASK_H_

#ifdef __cplusplus
extern "C" {
#endif



#include "services/systp.h"
#include "services/syserror.h"
#include "services/AManagedTaskEx.h"
#include "services/AManagedTaskEx_vtbl.h"
#include "events/DataEventSrc.h"
#include "events/DataEventSrc_vtbl.h"
#include "ISensor.h"
#include "ISensor_vtbl.h"

/**
  * Create  type name for _IMP34DT05Task.
  */
typedef struct _IMP34DT05Task IMP34DT05Task;




// Public API declaration
//***********************

/**
  * Get the ISourceObservable interface for the analog microphone.
  * @param _this [IN] specifies a pointer to a task object.
  * @return a pointer to the generic object ::ISourceObservable if success,
  * or NULL if out of memory error occurs.
  */
ISourceObservable *IMP34DT05TaskGetMicSensorIF(IMP34DT05Task *_this);

/**
  * Allocate an instance of IMP34DT05Task.
  *
  * @param p_mx_dfsdm_cfg [IN] specifies a ::MX_DFSDMParams_t instance declared in the mx.h file.
  * @param p_mx_adc_cfg [IN] specifies a ::MX_ADCParams_t instance declared in the mx.h file.
  * @return a pointer to the generic object ::AManagedTaskEx if success,
  * or NULL if out of memory error occurs.
  */
AManagedTaskEx *IMP34DT05TaskAlloc(const void *p_mx_dfsdm_cfg);

IEventSrc *IMP34DT05TaskGetEventSrcIF(IMP34DT05Task *_this);

// Inline functions definition
// ***************************


#ifdef __cplusplus
}
#endif

#endif /* IMP34DT05TASK_H_ */
