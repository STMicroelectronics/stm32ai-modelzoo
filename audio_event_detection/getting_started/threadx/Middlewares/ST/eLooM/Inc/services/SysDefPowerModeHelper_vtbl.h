/**
 ******************************************************************************
 * @file    SysDefPowerModeHelper_vtbl.h
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
#ifndef INCLUDE_SERVICES_SYSDEFPOWERMODEHELPER_VTBL_H_
#define INCLUDE_SERVICES_SYSDEFPOWERMODEHELPER_VTBL_H_

#ifdef __cplusplus
extern "C" {
#endif


sys_error_code_t SysDefPowerModeHelper_vtblInit(IAppPowerModeHelper *this); ///< @sa IapmhInit
EPowerMode SysDefPowerModeHelper_vtblComputeNewPowerMode(IAppPowerModeHelper *this, const SysEvent xEvent); ///< @sa IapmhComputeNewPowerMode
boolean_t SysDefPowerModeHelper_vtblCheckPowerModeTransaction(IAppPowerModeHelper *this, const EPowerMode eActivePowerMode, const EPowerMode eNewPowerMode); ///< @sa IapmhCheckPowerModeTransaction
sys_error_code_t SysDefPowerModeHelper_vtblDidEnterPowerMode(IAppPowerModeHelper *this, EPowerMode ePowerMode); ///< @sa IapmhDidEnterPowerMode
EPowerMode SysDefPowerModeHelper_vtblGetActivePowerMode(IAppPowerModeHelper *this); ///< @sa IapmhGetActivePowerMode
SysPowerStatus SysDefPowerModeHelper_vtblGetPowerStatus(IAppPowerModeHelper *this); ///< @sa IapmhGetPowerStatus
boolean_t SysDefPowerModeHelper_vtblIsLowPowerMode(IAppPowerModeHelper *this, const EPowerMode ePowerMode); ///< @sa IapmhIsLowPowerMode


#ifdef __cplusplus
}
#endif

#endif /* INCLUDE_SERVICES_SYSDEFPOWERMODEHELPER_VTBL_H_ */
