/**
 ******************************************************************************
 * @file    AppPowerModeHelper.h
 * @author  STF12
 * @version 1.0.0
 * @date    Aug 10, 2020
 *
 * @brief It implements the Power Mode State Machine.
 *
 * This object implements the IAppPowerModeHelper IF. The state machine has
 * two states as described in the section \ref tab_s4_power_management
 * "Power Management"
 *
 ******************************************************************************
 * @attention
 *
 * <h2><center>&copy; COPYRIGHT 2020 STF12 - Stefano Oliveri</center></h2>
 *
 * Licensed under MCD-ST Liberty SW License Agreement V2, (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at:
 *
 *        http://www.st.com/software_license_agreement_liberty_v2
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ******************************************************************************
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


// Public API declaration
//***********************

/**
 * Allocate an instance of AppPowerModeHelper. It is allocated in the FreeRTOS heap.
 *
 * @return a pointer to the generic interface ::IApplicationErrorDelegate if success,
 * or SYS_OUT_OF_MEMORY_ERROR_CODE otherwise.
 */
IAppPowerModeHelper *AppPowerModeHelperAlloc();


#ifdef __cplusplus
}
#endif

#endif /* APPPOWERMODEHELPER_H_ */
