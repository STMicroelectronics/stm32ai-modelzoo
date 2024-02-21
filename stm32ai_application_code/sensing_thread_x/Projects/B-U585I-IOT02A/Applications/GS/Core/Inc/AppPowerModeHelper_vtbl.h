/**
 ******************************************************************************
 * @file    AppPowerModeHelper_vtbl.h
 * @author  STF12
 * @version 1.0.0
 * @date    Aug 10, 2020
 *
 * @brief
 *
 * <DESCRIPTIOM>
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
