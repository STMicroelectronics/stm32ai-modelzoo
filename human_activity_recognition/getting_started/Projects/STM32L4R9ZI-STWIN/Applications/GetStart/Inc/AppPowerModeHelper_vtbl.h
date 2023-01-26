/**
 ******************************************************************************
 * @file    AppPowerModeHelper_vtbl.h
 * @author  STMicroelectronics - AIS - MCD Team
 * @version V0.9.0
 * @date    21-Oct-2022
 * @brief
 *
 * <DESCRIPTIOM>
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
#ifndef APPPOWERMODEHELPER_VTBL_H_
#define APPPOWERMODEHELPER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


sys_error_code_t AppPowerModeHelper_vtblInit(IAppPowerModeHelper *this); ///< @sa IapmhInit
EPowerMode AppPowerModeHelper_vtblComputeNewPowerMode(IAppPowerModeHelper *this, const SysEvent xEvent); ///< @sa IapmhComputeNewPowerMode
boolean_t AppPowerModeHelper_vtblCheckPowerModeTransaction(IAppPowerModeHelper *this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode); ///< @sa IapmhCheckPowerModeTransaction
sys_error_code_t AppPowerModeHelper_vtblDidEnterPowerMode(IAppPowerModeHelper *this, EPowerMode ePowerMode); ///< @sa IapmhDidEnterPowerMode
EPowerMode AppPowerModeHelper_vtblGetActivePowerMode(IAppPowerModeHelper *this); ///< @sa IapmhGetActivePowerMode
SysPowerStatus AppPowerModeHelper_vtblGetPowerStatus(IAppPowerModeHelper *this); ///< @sa IapmhGetPowerStatus
boolean_t AppPowerModeHelper_vtblIsLowPowerMode(IAppPowerModeHelper *this, const EPowerMode ePowerMode); ///< @sa IapmhIsLowPowerMode


#ifdef __cplusplus
}
#endif

#endif /* APPPOWERMODEHELPER_VTBL_H_ */
