/**
 ******************************************************************************
 * @file    AppPowerModeHelper.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 *
 * @brief Define the Power Mode State Machine.
 *
 * This object implements the ::IAppPowerModeHelper IF. The state machine has
 * four states as described in the section (TODO: PUT A REFERENCE)
 *
 *********************************************************************************
 * @attention
 *
 * Copyright (c) 2021 STMicroelectronics
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file in
 * the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *********************************************************************************
 */
#ifndef APPPOWERMODEHELPER_H_
#define APPPOWERMODEHELPER_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "services/IAppPowerModeHelper.h"
#include "services/IAppPowerModeHelper_vtbl.h"


/**
 * Create  type name for _AppPowermodeHelper.
 */
typedef struct _AppPowerModeHelper AppPowerModeHelper;


/* Public API declaration */
/***************************/

/**
 * Allocate an instance of AppPowerModeHelper. It is allocated in the FreeRTOS heap.
 *
 * @return a pointer to the generic interface ::IApplicationErrorDelegate if success,
 * or SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
IAppPowerModeHelper *AppPowerModeHelperAlloc(void);



/* Inline functions definition */
/*******************************/


#ifdef __cplusplus
}
#endif

#endif /* APPPOWERMODEHELPER_H_ */
