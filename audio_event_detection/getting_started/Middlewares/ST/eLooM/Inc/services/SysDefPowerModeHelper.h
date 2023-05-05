/**
 ******************************************************************************
 * @file    SysDefPowerModeHelper.h
 * @author  STMicroelectronics - ST-Korea - MCD Team
 * @version 3.0.0
 * @date    Oct 31, 2018
 *
 * @brief
 *
 * <DESCRIPTIOM>
 *
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2017 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 ******************************************************************************
 */
#ifndef INCLUDE_SERVICES_SYSDEFPOWERMODEHELPER_H_
#define INCLUDE_SERVICES_SYSDEFPOWERMODEHELPER_H_

#ifdef __cplusplus
extern "C" {
#endif


#include "IAppPowerModeHelper.h"
#include "IAppPowerModeHelper_vtbl.h"


/**
 * Create  type name for _SysDefPowerModeHelper.
 */
typedef struct _SysDefPowerModeHelper SysDefPowerModeHelper;

/**
 * Internal state of the Default Power Mode Helper.
 */
struct _SysDefPowerModeHelper {

  /**
   * Base class object.
   */
  IAppPowerModeHelper *super;

  /**
   *
   */
  SysPowerStatus m_xStatus;
};

/* Public API declaration */
/**************************/

/**
 * Allocate an instance of SysDefPowerModeHelper. It is allocated in the FreeRTOS heap.
 *
 * @return a pointer to the generic interface ::IApplicationErrorDelegate if success,
 * or SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
IAppPowerModeHelper * SysDefPowerModeHelperAlloc(void);


/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_SYSDEFPOWERMODEHELPER_H_ */
